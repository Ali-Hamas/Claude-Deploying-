# Skill: Todo List Management (MCP Server)

## Purpose
[cite_start]This skill provides Model Context Protocol (MCP) tools that allow an AI agent to perform CRUD operations on the user's todo list[cite: 414].

## Tool Definitions
[cite_start]The following tools must be implemented using the Official MCP SDK and SQLModel[cite: 421, 422].

### 1. add_task
- **Purpose:** Create a new task.
- **Parameters:**
  - `user_id` (string, required)
  - `title` (string, required)
  - `description` (string, optional)
  - `priority` (string, optional: "low", "medium", "high", "urgent", default: "medium")
  - `due_date` (string ISO 8601, optional)
  - `tags` (array of strings, optional)
  - `recurrence` (string, optional: "daily", "weekly", "monthly", "yearly")
- [cite_start]**Returns:** JSON object containing `task_id`, `status`, `title`, and other task fields [cite: 450-451].
- **Note:** If `recurrence` is set, completing this task will automatically create a new instance with the next due date.

### 2. list_tasks
- **Purpose:** Retrieve tasks from the list.
- **Parameters:**
  - `user_id` (string, required)
  - `status` (string, optional: "all", "pending", "completed")
- [cite_start]**Returns:** Array of task objects [cite: 455-456].

### 3. update_task
- **Purpose:** Modify task properties.
- **Parameters:**
  - `user_id` (string, required)
  - `task_id` (integer, required)
  - `title` (string, optional)
  - `description` (string, optional)
  - `priority` (string, optional)
  - `due_date` (string ISO 8601, optional)
  - `tags` (array of strings, optional)
  - `recurrence` (string, optional)
  - `status` (string, optional: "pending", "completed")
- [cite_start]**Returns:** JSON object with `status: "updated"` [cite: 461-462].
- **Note:** Changing status to "completed" triggers an event that may create a recurring task instance.

### 4. complete_task
- **Purpose:** Mark a task as complete.
- **Parameters:** `user_id`, `task_id`
- [cite_start]**Returns:** JSON object with `status: "completed"` [cite: 457-458].
- **Note:** Completing a task with recurrence triggers an async event that creates the next instance.

### 5. delete_task
- **Purpose:** Remove a task.
- **Parameters:** `user_id`, `task_id`
- [cite_start]**Returns:** JSON object with `status: "deleted"` [cite: 459-460].

## Agent Behavior with Reminders

### "Remind Me" Pattern
When a user says "remind me", the agent MUST:
1. Extract the task description from the user's message
2. Parse any date/time information using natural language understanding
3. Convert the date/time to ISO 8601 format
4. Call `add_task` with the `due_date` parameter set

### Date/Time Extraction Examples
- "Remind me to buy groceries tomorrow at 3pm" → `due_date: "2025-12-20T15:00:00"`
- "Remind me in 2 hours to call John" → `due_date: "2025-12-19T16:30:00"` (calculated from current time)
- "Remind me on Friday at 10am about the meeting" → `due_date: "2025-12-22T10:00:00"`
- "Remind me next Monday" → `due_date: "2025-12-23T09:00:00"` (default to 9am if no time specified)

### Agent System Prompt Requirements
The agent system prompt must:
- Be aware of the current date and time for relative date calculations
- Parse natural language date/time expressions (tomorrow, next week, in X hours, etc.)
- Default to 9:00 AM when only a date is specified (no time)
- Ask for clarification if "remind me" is used without any time/date context
- Confirm the reminder time in human-readable format after creation

### Integration with Cron Reminder System
- Tasks with `due_date` set will trigger reminder events via the Dapr cron binding
- Reminders are sent 0-10 minutes before the due date
- The agent doesn't need to manage reminders; the backend handles this automatically