from sqlmodel import Session, select
from typing import List, Optional
from models.todo_models import Task, TaskCreate, TaskUpdate, TaskRead, TaskStatus, TaskPriority, TaskRecurrence, Message, MessageRole
from datetime import datetime
import json

def get_user_tasks(db: Session, user_id: str, status_filter: str = "all") -> List[TaskRead]:
    """
    Get all tasks for a user, optionally filtered by status
    """
    query = select(Task).where(Task.user_id == user_id)

    if status_filter != "all":
        try:
            status_enum = TaskStatus(status_filter)
            query = query.where(Task.status == status_enum)
        except ValueError:
            # Invalid status, return empty list or all tasks
            pass

    tasks = db.exec(query).all()
    return [TaskRead.from_orm(task) if hasattr(TaskRead, 'from_orm') else
            TaskRead(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date,
                tags=json.loads(task.tags) if task.tags else [],
                recurrence=task.recurrence,
                reminder_sent=task.reminder_sent,
                user_id=task.user_id,
                created_at=task.created_at,
                updated_at=task.updated_at
            ) for task in tasks]

def get_task_by_id(db: Session, task_id: int, user_id: str) -> Optional[Task]:
    """
    Get a specific task by ID for a user
    """
    query = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
    return db.exec(query).first()

def create_task_for_user(db: Session, task_data: TaskCreate, user_id: str) -> TaskRead:
    """
    Create a new task for a user and publish task.created event
    """
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status if task_data.status else TaskStatus.pending,
        priority=task_data.priority if task_data.priority else TaskPriority.medium,
        due_date=task_data.due_date,
        tags=json.dumps(task_data.tags) if task_data.tags else "[]",
        recurrence=task_data.recurrence,
        user_id=user_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Publish task.created event to Dapr pub/sub
    try:
        from services.event_service import publish_task_event
        import asyncio
        # Run the async function in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(publish_task_event("task.created", task))
    except Exception as e:
        # Log error but don't fail the creation
        import logging
        logging.error(f"Failed to publish task.created event: {str(e)}")

    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        tags=json.loads(task.tags) if task.tags else [],
        recurrence=task.recurrence,
        reminder_sent=task.reminder_sent,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

def update_task(db: Session, task_id: int, user_id: str, task_update: TaskUpdate) -> Optional[TaskRead]:
    """
    Update a task for a user and publish task.updated or task.completed event
    """
    task = get_task_by_id(db, task_id, user_id)
    if not task:
        return None

    # Track if status changed to completed
    was_completed = False
    if task_update.status is not None and task_update.status == TaskStatus.completed:
        if task.status != TaskStatus.completed:
            was_completed = True

    # Update only the fields that are provided
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.tags is not None:
        task.tags = json.dumps(task_update.tags)
    if task_update.recurrence is not None:
        task.recurrence = task_update.recurrence

    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)

    # Publish events to Dapr pub/sub
    try:
        from services.event_service import publish_task_event
        import asyncio
        # Run the async function in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Publish task.completed event if status changed to completed
        if was_completed:
            loop.run_until_complete(publish_task_event("task.completed", task))
        else:
            # Publish task.updated event for all other updates
            loop.run_until_complete(publish_task_event("task.updated", task))
    except Exception as e:
        # Log error but don't fail the update
        import logging
        logging.error(f"Failed to publish task event: {str(e)}")

    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        tags=json.loads(task.tags) if task.tags else [],
        recurrence=task.recurrence,
        reminder_sent=task.reminder_sent,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

def delete_task(db: Session, task_id: int, user_id: str) -> bool:
    """
    Delete a task for a user
    """
    task = get_task_by_id(db, task_id, user_id)
    if not task:
        return False

    db.delete(task)
    db.commit()
    return True