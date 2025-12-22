# Event-Driven Architecture with Dapr

## Goal
Implement an event-driven architecture using Dapr (Distributed Application Runtime) for pub/sub messaging to handle asynchronous task operations, particularly for recurring task management.

## Architecture Overview

### Dapr Pub/Sub Pattern
- Use **dapr-python-sdk** for event publishing and subscription
- Stateless backend: No in-memory event queues or Kafka clients
- All event handling through Dapr sidecars via HTTP/gRPC

### Event Flow
1. Task status changes trigger events (e.g., task completed)
2. Events are published to Dapr pub/sub component
3. Dapr routes events to subscribed endpoints
4. Endpoints process events and update database

## Pub/Sub Configuration

### Topic: `task-events`
- **Publisher:** FastAPI backend (when tasks are updated/completed)
- **Subscribers:** FastAPI backend endpoints for event processing

### Event Types

1. **task.completed**
   - Triggered when a task status changes to "completed"
   - Payload:
     ```json
     {
       "event_type": "task.completed",
       "task_id": 123,
       "user_id": 1,
       "title": "Daily exercise",
       "recurrence": "daily",
       "priority": "medium",
       "tags": ["health", "routine"],
       "due_date": "2025-12-20T10:00:00Z",
       "completed_at": "2025-12-19T14:30:00Z"
     }
     ```

2. **task.reminder**
   - Triggered by cron scheduler for tasks due within 10 minutes
   - Published to `reminders` topic
   - Payload:
     ```json
     {
       "event_type": "task.reminder",
       "task_id": 123,
       "user_id": 1,
       "title": "Team meeting",
       "description": "Quarterly review",
       "priority": "high",
       "tags": ["work", "meeting"],
       "due_date": "2025-12-19T15:05:00Z",
       "minutes_until_due": 8
     }
     ```

## API Endpoints

### Event Subscription Endpoints

#### POST /api/events/task-completed
- **Purpose:** Dapr subscription endpoint for task completion events
- **Triggered by:** Dapr when task.completed events are published
- **Dapr Subscription:** Subscribes to `task-events` topic with route `/api/events/task-completed`
- **Logic:**
  - Receives task completion event
  - Checks if task has recurrence field set
  - If recurring, creates a new task with:
    - Same title, description, priority, tags, recurrence
    - New due_date calculated based on recurrence pattern
    - Status reset to "pending"
- **Returns:** HTTP 200 for successful processing

#### POST /api/events/task-reminder
- **Purpose:** Dapr subscription endpoint for task reminder events
- **Triggered by:** Dapr when reminder events are published to `reminders` topic
- **Dapr Subscription:** Subscribes to `reminders` topic with route `/api/events/task-reminder`
- **Logic:**
  1. Logs notification to console: "🔔 Sending reminder for Task ID {task_id}"
  2. Gets or creates the user's most recent conversation
  3. Creates reminder message: "⏰ REMINDER: Your task '{title}' is due in X minutes!"
  4. Stores message in `messages` table with `role='assistant'`
  5. Updates conversation `updated_at` timestamp
- **Returns:** HTTP 200 with conversation_id and reminder_sent status
- **Result:** Reminder appears in chat history for the user

#### POST /reminder-cron
- **Purpose:** Dapr cron binding handler for task reminders
- **Triggered by:** Dapr cron binding (every 5 minutes)
- **Logic:**
  - Queries database for pending tasks with `due_date` within next 10 minutes and `reminder_sent=False`
  - For each upcoming task, publishes `task.reminder` event to `reminders` topic
  - Marks `reminder_sent=True` to prevent duplicate reminders
- **Returns:** HTTP 200 with count of reminders sent

#### GET /dapr/subscribe
- **Purpose:** Dapr subscription discovery endpoint
- **Returns:** Array of subscription definitions for Dapr to configure
- **Example Response:**
  ```json
  [
    {
      "pubsubname": "todo-pubsub",
      "topic": "task-events",
      "route": "/api/events/task-completed"
    },
    {
      "pubsubname": "todo-pubsub",
      "topic": "reminders",
      "route": "/api/events/task-reminder"
    }
  ]
  ```

## Implementation Requirements

### 1. Dapr SDK Integration
- Install `dapr-python-sdk` package
- Use `DaprClient` for publishing events
- Use FastAPI endpoints for receiving events (Dapr push model)

### 2. Event Publishing
- Publish events when:
  - Task status changes to "completed"
- Use Dapr HTTP API endpoint: `http://localhost:3500/v1.0/publish/{pubsubname}/{topic}`
- Publish via `DaprClient.publish_event()` method

### 3. Event Subscription
- Implement `/dapr/subscribe` endpoint for Dapr discovery
- Implement handler endpoints for each event type
- Handle idempotency (events may be delivered multiple times)

### 4. Recurring Task Logic
When a task with recurrence is completed:
- Calculate next due date:
  - `daily`: +1 day from completion time
  - `weekly`: +7 days from completion time
  - `monthly`: +1 month from completion time
  - `yearly`: +1 year from completion time
- Create new task with calculated due_date
- Preserve all other task attributes

### 5. Cron Binding for Reminders
- Dapr cron binding triggers `/reminder-cron` every 5 minutes
- Query database for tasks where:
  - `status = "pending"`
  - `due_date` is NOT NULL
  - `due_date` is between NOW and NOW + 10 minutes
  - `reminder_sent = False` (prevent duplicate reminders)
- Publish reminder event for each task found
- Mark `reminder_sent = True` after publishing to prevent spam
- Cron schedule: `*/5 * * * *` (every 5 minutes)

## Dapr Component Configuration

### Pub/Sub Component (pubsub.yaml)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

### Alternative: In-Memory (Development)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.in-memory
  version: v1
```

## Testing

### Manual Testing with Dapr CLI
```bash
# Start Dapr sidecar
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --components-path ./dapr/components

# Start FastAPI backend
uvicorn main:app --reload --port 8000

# Publish test event via Dapr HTTP
curl -X POST http://localhost:3500/v1.0/publish/todo-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.completed",
    "task_id": 1,
    "user_id": 1,
    "title": "Daily standup",
    "recurrence": "daily"
  }'
```

## Benefits of Dapr Approach

1. **No Direct Dependencies:** No Kafka, RabbitMQ, or other message broker libraries
2. **Pluggable:** Switch pub/sub backends (Redis, Kafka, Azure Service Bus) via config
3. **Stateless:** Backend remains stateless, Dapr handles delivery
4. **Cloud-Ready:** Works with Kubernetes and cloud services
5. **Simplified Code:** No connection pooling, retry logic, or broker-specific code

## User Stories

- "I complete a daily task" → System automatically creates the same task for tomorrow
- "I finish my weekly review meeting task" → System creates next week's task
- "I complete a one-time task" → No new task is created (no recurrence)
- "System fails to create recurring task" → Event is retried by Dapr automatically
