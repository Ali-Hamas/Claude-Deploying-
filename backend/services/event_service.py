"""
Event Service for Dapr Pub/Sub Integration

This module provides stateless event publishing and handling
using the Dapr SDK for distributed pub/sub messaging.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dapr.clients import DaprClient
from sqlmodel import Session
import logging

from models.todo_models import Task, TaskRecurrence, TaskPriority, TaskStatus
import json

logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_PUBSUB_NAME = "todo-pubsub"
TASK_EVENTS_TOPIC = "task-events"
REMINDERS_TOPIC = "reminders"


async def publish_task_event(
    event_type: str,
    task: Task,
    dapr_client: Optional[DaprClient] = None
) -> bool:
    """
    Publish a task event to Dapr pub/sub.

    Args:
        event_type: The type of event (task.created, task.updated, task.completed)
        task: The task object
        dapr_client: Optional DaprClient instance (for testing)

    Returns:
        bool: True if published successfully, False otherwise
    """
    try:
        # Prepare event payload
        event_data = {
            "event_type": event_type,
            "task_id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value if task.status else "pending",
            "priority": task.priority.value if task.priority else "medium",
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": json.loads(task.tags) if task.tags else [],
            "recurrence": task.recurrence.value if task.recurrence else None,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add completed_at for completed events
        if event_type == "task.completed":
            event_data["completed_at"] = event_data["timestamp"]

        # Use provided client or create a new one
        client = dapr_client or DaprClient()

        # Publish event to Dapr
        client.publish_event(
            pubsub_name=DAPR_PUBSUB_NAME,
            topic_name=TASK_EVENTS_TOPIC,
            data=json.dumps(event_data),
            data_content_type="application/json"
        )

        logger.info(f"Published {event_type} event for task_id={task.id}")

        # Close client if we created it
        if not dapr_client:
            client.close()

        return True

    except Exception as e:
        logger.error(f"Failed to publish {event_type} event: {str(e)}")
        # Don't fail the request if event publishing fails
        return False


async def publish_task_completed_event(
    task: Task,
    dapr_client: Optional[DaprClient] = None
) -> bool:
    """
    Publish a task.completed event to Dapr pub/sub.

    Args:
        task: The completed task
        dapr_client: Optional DaprClient instance (for testing)

    Returns:
        bool: True if published successfully, False otherwise
    """
    return await publish_task_event("task.completed", task, dapr_client)


async def publish_task_reminder_event(
    task: Task,
    minutes_until_due: int,
    dapr_client: Optional[DaprClient] = None
) -> bool:
    """
    Publish a task.reminder event to Dapr pub/sub.

    Args:
        task: The task with an upcoming due date
        minutes_until_due: Minutes until the task is due
        dapr_client: Optional DaprClient instance (for testing)

    Returns:
        bool: True if published successfully, False otherwise
    """
    try:
        # Prepare event payload
        event_data = {
            "event_type": "task.reminder",
            "task_id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value if task.priority else "medium",
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": json.loads(task.tags) if task.tags else [],
            "minutes_until_due": minutes_until_due
        }

        # Use provided client or create a new one
        client = dapr_client or DaprClient()

        # Publish event to Dapr
        client.publish_event(
            pubsub_name=DAPR_PUBSUB_NAME,
            topic_name=REMINDERS_TOPIC,
            data=json.dumps(event_data),
            data_content_type="application/json"
        )

        logger.info(f"Published task.reminder event for task_id={task.id}, due in {minutes_until_due} minutes")

        # Close client if we created it
        if not dapr_client:
            client.close()

        return True

    except Exception as e:
        logger.error(f"Failed to publish task.reminder event: {str(e)}")
        return False


def calculate_next_due_date(
    recurrence: TaskRecurrence,
    base_date: Optional[datetime] = None
) -> datetime:
    """
    Calculate the next due date based on recurrence pattern.

    Args:
        recurrence: The recurrence pattern (daily, weekly, monthly, yearly)
        base_date: The base date to calculate from (defaults to now)

    Returns:
        datetime: The calculated next due date
    """
    if base_date is None:
        base_date = datetime.utcnow()

    if recurrence == TaskRecurrence.daily:
        return base_date + timedelta(days=1)
    elif recurrence == TaskRecurrence.weekly:
        return base_date + timedelta(weeks=1)
    elif recurrence == TaskRecurrence.monthly:
        # Add approximately 1 month (30 days)
        # For more precise month calculation, use dateutil.relativedelta
        return base_date + timedelta(days=30)
    elif recurrence == TaskRecurrence.yearly:
        return base_date + timedelta(days=365)
    else:
        return base_date


def handle_recurring_task(event_data: Dict[str, Any], db: Session) -> Optional[Task]:
    """
    Handle recurring task logic when a task is completed.

    Creates a new task with the same properties but updated due date
    if the task has a recurrence pattern.

    Args:
        event_data: The task completion event data
        db: Database session

    Returns:
        Optional[Task]: The newly created recurring task, or None if not recurring
    """
    try:
        recurrence_str = event_data.get("recurrence")

        # Only create new task if recurrence is set
        if not recurrence_str:
            logger.info(f"Task {event_data.get('task_id')} has no recurrence, skipping")
            return None

        # Parse recurrence
        try:
            recurrence = TaskRecurrence(recurrence_str)
        except ValueError:
            logger.warning(f"Invalid recurrence value: {recurrence_str}")
            return None

        # Calculate next due date
        completed_at = event_data.get("completed_at")
        base_date = datetime.fromisoformat(completed_at) if completed_at else None
        next_due_date = calculate_next_due_date(recurrence, base_date)

        # Create new task with same properties
        new_task = Task(
            title=event_data.get("title"),
            description=event_data.get("description"),
            status=TaskStatus.pending,
            priority=TaskPriority(event_data.get("priority", "medium")),
            due_date=next_due_date,
            tags=json.dumps(event_data.get("tags", [])),
            recurrence=recurrence,
            user_id=event_data.get("user_id")
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        logger.info(
            f"Created recurring task {new_task.id} "
            f"(from task {event_data.get('task_id')}) "
            f"with due_date={next_due_date.isoformat()}"
        )

        return new_task

    except Exception as e:
        logger.error(f"Failed to handle recurring task: {str(e)}")
        db.rollback()
        return None
