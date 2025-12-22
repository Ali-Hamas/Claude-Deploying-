# Running Todo-Chat-Bot with Dapr

This directory contains Dapr component configurations for the Todo-Chat-Bot application.

## Prerequisites

1. Install Dapr CLI: https://docs.dapr.io/getting-started/install-dapr-cli/
2. Initialize Dapr: `dapr init`
3. Install Redis (for production pub/sub) or use in-memory (for development)

## Components

### Cron Binding (reminder-cron.yaml)
The cron binding triggers the `/reminder-cron` endpoint every 5 minutes to check for tasks due soon.

- **Schedule:** `*/5 * * * *` (every 5 minutes)
- **Endpoint:** POST `/reminder-cron`
- **Action:** Queries for tasks due within next 10 minutes and publishes reminders

## Pub/Sub Components

### In-Memory (Development)
Use `pubsub-inmemory.yaml` for local development without Redis:

```bash
cd backend
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --components-path ../dapr/components --resources-path ../dapr/components -- uvicorn main:app --reload --port 8000
```

**Note:** Use `pubsub-inmemory.yaml` by renaming it to `pubsub.yaml` or adjust the component name in the code.

### Redis (Production)
Use `pubsub.yaml` for production with Redis:

1. Ensure Redis is running:
   ```bash
   redis-server
   ```

2. Start the backend with Dapr:
   ```bash
   cd backend
   dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --components-path ../dapr/components -- uvicorn main:app --reload --port 8000
   ```

## Testing Event Publishing

### Test via Dapr HTTP API
Publish a test event directly to Dapr:

```bash
curl -X POST http://localhost:3500/v1.0/publish/todo-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.completed",
    "task_id": 1,
    "user_id": 1,
    "title": "Daily standup",
    "description": "Morning team sync",
    "priority": "medium",
    "due_date": "2025-12-20T10:00:00Z",
    "tags": ["work", "daily"],
    "recurrence": "daily",
    "completed_at": "2025-12-19T14:30:00Z"
  }'
```

### Test via Application API
Complete a task through the API and watch for automatic event publishing:

```bash
# Create a recurring task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily exercise",
    "description": "30 minutes cardio",
    "priority": "high",
    "tags": ["health", "daily"],
    "recurrence": "daily"
  }'

# Complete the task (this will trigger event publishing)
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

The event will be published to Dapr, which will deliver it to `/api/events/task-completed`,
and a new recurring task will be automatically created.

### Test Cron Binding
Test the reminder cron manually:

```bash
# Trigger the cron endpoint directly
curl -X POST http://localhost:8000/reminder-cron

# Or wait for Dapr cron to trigger it automatically (every 5 minutes)
```

To test reminders, create a task with a due date in the near future:

```bash
# Create a task due in 8 minutes
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important meeting",
    "description": "Quarterly review",
    "priority": "urgent",
    "due_date": "2025-12-19T15:08:00Z",
    "tags": ["work", "meeting"]
  }'

# Wait for the cron to trigger (within 5 minutes)
# Check logs for reminder events
```

## Verifying Dapr Setup

### Check Dapr Dashboard
```bash
dapr dashboard
```
Open http://localhost:8080 to see applications, components, and pub/sub topics.

### View Dapr Logs
```bash
# View sidecar logs
dapr logs --app-id todo-backend
```

### Check Subscriptions
```bash
curl http://localhost:8000/dapr/subscribe
```

Expected response:
```json
[
  {
    "pubsubname": "todo-pubsub",
    "topic": "task-events",
    "route": "/api/events/task-completed"
  }
]
```

## Troubleshooting

### Events not being delivered
1. Check Dapr sidecar is running: `dapr list`
2. Verify subscription endpoint: `curl http://localhost:8000/dapr/subscribe`
3. Check Redis is running (if using Redis component): `redis-cli ping`
4. View Dapr logs: `dapr logs --app-id todo-backend`

### Redis connection errors
- Ensure Redis is running on port 6379
- Check Redis host in `pubsub.yaml`
- Test Redis connection: `redis-cli ping`

### In-Memory alternative
For development without Redis, use the in-memory pub/sub:
1. Rename `pubsub-inmemory.yaml` to `pubsub.yaml`
2. Restart the Dapr application

## Architecture Notes

- The backend is **stateless** - no in-memory queues or Kafka clients
- Event publishing is handled by Dapr sidecar via HTTP
- Event delivery is managed by Dapr with automatic retries
- The application can be easily deployed to Kubernetes with Dapr
