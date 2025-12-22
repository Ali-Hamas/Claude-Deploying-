"""
Personal Task Assistant Agent

This module implements the AI agent using the OpenAI Agents SDK.
The agent manages a user's todo list using natural language and
utilizes MCP tools from the todo_mcp skill.

Spec Reference: specs/subagents/todo_agent.md
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

from agents import Agent, Runner, function_tool
from sqlmodel import Session, select

from database.connection import engine
from models.todo_models import Task, TaskStatus, Message, MessageRole, Conversation


# =============================================================================
# Tool Definitions (wrapping todo_mcp functions for OpenAI Agents SDK)
# =============================================================================

@function_tool
def add_task(user_id: str, title: str, description: str = "", due_date: str = None) -> dict:
    """
    Create a new task for the user's todo list.

    Args:
        user_id: The ID of the user (required)
        title: The title of the task (required)
        description: Optional description of the task
        due_date: Optional due date/time in ISO 8601 format (e.g., "2025-12-25T15:00:00")

    Returns:
        JSON object containing task_id, status, title, and due_date
    """
    with Session(engine) as session:
        try:
            user_id_int = int(user_id)
        except ValueError:
            return {"error": f"Invalid user_id: {user_id}", "status": "error"}

        try:
            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    return {
                        "error": f"Invalid due_date format: {due_date}. Use ISO 8601 format (e.g., 2025-12-25T15:00:00)",
                        "status": "error"
                    }

            task = Task(
                title=title,
                description=description if description else None,
                user_id=user_id_int,
                status=TaskStatus.pending,
                due_date=parsed_due_date
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": task.id,
                "status": task.status.value,
                "title": task.title,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
        except Exception as e:
            session.rollback()
            return {"error": str(e), "status": "error"}


@function_tool
def list_tasks(user_id: str, status: str = "all") -> dict:
    """
    Retrieve tasks from the user's todo list.

    Args:
        user_id: The ID of the user (required)
        status: Filter by status - "all", "pending", or "completed" (optional, defaults to "all")

    Returns:
        Array of task objects
    """
    with Session(engine) as session:
        try:
            user_id_int = int(user_id)
        except ValueError:
            return {"error": f"Invalid user_id: {user_id}", "tasks": []}

        try:
            query = select(Task).where(Task.user_id == user_id_int)

            if status != "all":
                try:
                    status_enum = TaskStatus(status)
                    query = query.where(Task.status == status_enum)
                except ValueError:
                    return {
                        "error": f"Invalid status: {status}. Use 'all', 'pending', or 'completed'",
                        "tasks": []
                    }

            tasks = session.exec(query).all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                })

            return {"tasks": task_list}

        except Exception as e:
            return {"error": str(e), "tasks": []}


@function_tool
def complete_task(user_id: str, task_id: int) -> dict:
    """
    Mark a task as complete.

    Args:
        user_id: The ID of the user (required)
        task_id: The ID of the task to complete (required)

    Returns:
        JSON object with status: "completed"
    """
    with Session(engine) as session:
        try:
            user_id_int = int(user_id)
        except ValueError:
            return {"status": "error", "error": f"Invalid user_id: {user_id}"}

        task = session.get(Task, task_id)
        if not task or task.user_id != user_id_int:
            return {
                "status": "error",
                "error": f"Task with ID {task_id} not found for user {user_id}"
            }

        try:
            task.status = TaskStatus.completed
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            # Publish task-completed event for recurring task processing
            # Run async event publishing in the background
            import asyncio
            from services.event_service import publish_task_completed_event

            try:
                # Try to get the running event loop
                loop = asyncio.get_running_loop()
                loop.create_task(publish_task_completed_event(task))
            except RuntimeError:
                # No event loop running, create a new one
                asyncio.run(publish_task_completed_event(task))

            return {"status": "completed", "task_id": task.id}
        except Exception as e:
            session.rollback()
            return {"status": "error", "error": str(e)}


@function_tool
def delete_task(user_id: str, task_id: int) -> dict:
    """
    Remove a task from the todo list.

    Args:
        user_id: The ID of the user (required)
        task_id: The ID of the task to delete (required)

    Returns:
        JSON object with status: "deleted"
    """
    with Session(engine) as session:
        try:
            user_id_int = int(user_id)
        except ValueError:
            return {"status": "error", "error": f"Invalid user_id: {user_id}"}

        task = session.get(Task, task_id)
        if not task or task.user_id != user_id_int:
            return {
                "status": "error",
                "error": f"Task with ID {task_id} not found for user {user_id}"
            }

        try:
            session.delete(task)
            session.commit()
            return {"status": "deleted", "task_id": task_id}
        except Exception as e:
            session.rollback()
            return {"status": "error", "error": str(e)}


@function_tool
def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """
    Update a task's title or description.

    Args:
        user_id: The ID of the user (required)
        task_id: The ID of the task to update (required)
        title: New title for the task (optional)
        description: New description for the task (optional)

    Returns:
        JSON object with status: "updated"
    """
    with Session(engine) as session:
        try:
            user_id_int = int(user_id)
        except ValueError:
            return {"status": "error", "error": f"Invalid user_id: {user_id}"}

        task = session.get(Task, task_id)
        if not task or task.user_id != user_id_int:
            return {
                "status": "error",
                "error": f"Task with ID {task_id} not found for user {user_id}"
            }

        try:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description

            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "updated",
                "task_id": task.id,
                "title": task.title,
                "description": task.description
            }
        except Exception as e:
            session.rollback()
            return {"status": "error", "error": str(e)}


# =============================================================================
# Agent System Instructions (per spec behavior rules)
# =============================================================================

AGENT_INSTRUCTIONS = """You are a Personal Task Assistant, an AI capable of managing a user's todo list using natural language.

## Behavior Rules:

1. **Task Creation:** When a user mentions adding, creating, or remembering something, call `add_task` with an appropriate title and description.
   - Example: "Add a task to buy milk" -> call add_task with title "Buy milk"
   - Example: "Remind me to call mom tomorrow" -> call add_task with title "Call mom tomorrow"

   **Due Date Extraction:**
   - **ALWAYS extract and set due_date when the user says "remind me"**
   - Extract due dates from natural language and convert to ISO 8601 format
   - Current date/time context: {current_datetime}
   - Examples:
     * "Remind me to buy groceries tomorrow at 3pm" -> due_date: tomorrow at 15:00:00
     * "Add task: meeting on Friday at 2:30pm" -> due_date: next Friday at 14:30:00
     * "Remind me in 2 hours to call John" -> due_date: current time + 2 hours
     * "Schedule dentist appointment for December 25th at 10am" -> due_date: 2025-12-25T10:00:00
   - If time is not specified but date is, default to 9:00 AM
   - If only relative time is given (e.g., "in 30 minutes"), calculate from current time
   - If "remind me" is used without time/date, ask the user for clarification

2. **Task Listing:** When asked to show, list, or display tasks, call `list_tasks` with the appropriate status filter.
   - Example: "What do I have to do?" -> call list_tasks with status "pending"
   - Example: "Show all my tasks" -> call list_tasks with status "all"
   - Example: "What have I completed?" -> call list_tasks with status "completed"

3. **Task Completion:** When a user says "done", "finished", "completed", or marks a task as done, call `complete_task`.
   - Example: "I finished task 3" -> call complete_task with task_id 3
   - Example: "Mark task 1 as done" -> call complete_task with task_id 1

4. **Task Deletion:** When a user wants to remove or delete a task, call `delete_task`.
   - Always confirm the deletion with a friendly response.

5. **Task Updates:** When a user wants to change or update a task's title or description, call `update_task`.

## Date/Time Processing:
- Parse natural language dates and times intelligently
- Support formats: "tomorrow", "next Monday", "in 2 hours", "at 3pm", "on Dec 25"
- Always output dates in ISO 8601 format: YYYY-MM-DDTHH:MM:SS
- Use 24-hour time format
- If ambiguous, ask for clarification

## Response Style:
- Be friendly and conversational
- Always confirm actions with clear responses, including due dates when set
- Summarize task lists in a readable format
- If an error occurs, explain it clearly and suggest alternatives
- When a reminder is set, confirm the date/time in human-readable format

## Important:
- The user_id will be provided in the context. Always use it for all tool calls.
- Never expose internal error details to users - keep responses friendly.
- **CRITICAL: When "remind me" is used, ALWAYS set a due_date parameter in add_task.**
"""


# =============================================================================
# Agent Factory and Runner
# =============================================================================

def create_todo_agent() -> Agent:
    """
    Create and configure the Personal Task Assistant agent.

    Returns:
        Agent: Configured OpenAI Agent with todo management tools
    """
    return Agent(
        name="Personal Task Assistant",
        instructions=AGENT_INSTRUCTIONS,
        tools=[add_task, list_tasks, complete_task, delete_task, update_task],
        model="gpt-4-turbo"
    )


class TodoAgentRunner:
    """
    Runner class for executing the Todo Agent with conversation persistence.

    This class handles:
    - Loading conversation history from the database
    - Running the agent with user input
    - Saving messages to the database
    - Maintaining stateless operation per spec
    """

    def __init__(self, user_id: int):
        """
        Initialize the TodoAgentRunner.

        Args:
            user_id: The ID of the user this agent is serving
        """
        self.user_id = user_id
        self.agent = create_todo_agent()

    def load_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Load conversation history from the database.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            List of message dicts formatted for the agent
        """
        with Session(engine) as session:
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at)
            messages = session.exec(statement).all()

            formatted_messages = []
            for msg in messages:
                role = "assistant" if msg.role == MessageRole.assistant else "user"
                formatted_messages.append({
                    "role": role,
                    "content": msg.content
                })

            return formatted_messages

    def save_message(self, conversation_id: int, role: str, content: str):
        """
        Save a message to the conversation in the database.

        Args:
            conversation_id: The ID of the conversation
            role: The role of the message sender ('user' or 'assistant')
            content: The message content
        """
        with Session(engine) as session:
            message_role = MessageRole.assistant if role == "assistant" else MessageRole.user
            message = Message(
                conversation_id=conversation_id,
                role=message_role,
                content=content
            )
            session.add(message)
            session.commit()

    async def run(self, user_input: str, conversation_id: int) -> Dict[str, Any]:
        """
        Run the agent with user input.

        Args:
            user_input: The user's message
            conversation_id: The ID of the conversation

        Returns:
            Dict containing response and conversation_id
        """
        try:
            # Load conversation history
            history = self.load_conversation_history(conversation_id)

            # Get current datetime for the agent context
            current_dt = datetime.utcnow()
            current_datetime_str = current_dt.strftime("%Y-%m-%d %H:%M:%S UTC (Day: %A)")

            # Update agent instructions with current datetime
            instructions_with_time = self.agent.instructions.replace(
                "{current_datetime}",
                current_datetime_str
            )
            self.agent.instructions = instructions_with_time

            # Prepare input with user context
            context_input = f"[User ID: {self.user_id}]\n{user_input}"

            # Run the agent
            result = await Runner.run(
                self.agent,
                input=context_input,
                context={"user_id": str(self.user_id), "conversation_history": history}
            )

            # Extract the response
            response_text = result.final_output if hasattr(result, 'final_output') else str(result)

            # Save messages to database
            self.save_message(conversation_id, "user", user_input)
            self.save_message(conversation_id, "assistant", response_text)

            return {
                "response": response_text,
                "conversation_id": conversation_id
            }

        except Exception as e:
            error_msg = f"I encountered an issue processing your request. Please try again."
            self.save_message(conversation_id, "assistant", error_msg)
            return {
                "response": error_msg,
                "conversation_id": conversation_id,
                "error": True,
                "error_detail": str(e)
            }

    def run_sync(self, user_input: str, conversation_id: int) -> Dict[str, Any]:
        """
        Synchronous wrapper for running the agent.

        Args:
            user_input: The user's message
            conversation_id: The ID of the conversation

        Returns:
            Dict containing response and conversation_id
        """
        return asyncio.run(self.run(user_input, conversation_id))


# =============================================================================
# Convenience Functions
# =============================================================================

def get_agent_runner(user_id: int) -> TodoAgentRunner:
    """
    Factory function to create a TodoAgentRunner instance.

    Args:
        user_id: The ID of the user

    Returns:
        TodoAgentRunner instance configured for the user
    """
    return TodoAgentRunner(user_id=user_id)


async def run_agent(user_id: int, user_input: str, conversation_id: int) -> Dict[str, Any]:
    """
    Convenience function to run the agent for a user.

    Args:
        user_id: The ID of the user
        user_input: The user's message
        conversation_id: The ID of the conversation

    Returns:
        Dict containing response and conversation_id
    """
    runner = TodoAgentRunner(user_id=user_id)
    return await runner.run(user_input, conversation_id)
