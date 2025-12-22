# Feature: Advanced Todo Logic (Phase V)

## Recurring Tasks
- **Requirement:** When a task marked as "recurring" is completed, the system must automatically create the next occurrence.
- **Architecture:** 1. Backend publishes a `task-completed` event to the `task-events` Kafka topic via Dapr.
  2. A Dapr subscriber listens to this topic.
  3. If the task has a recurrence rule, the subscriber calculates the next date and creates a new task in the DB.

## Reminders
- **Requirement:** Users receive notifications for tasks with due dates.
- **Architecture:**
  1. Use Dapr Bindings (Cron) to trigger a backend endpoint `/api/cron/reminders` every 5 minutes.
  2. The endpoint queries the DB for tasks due in the next 10 minutes.
  3. If found, publish a `send-notification` event to the `reminders` topic via Dapr.