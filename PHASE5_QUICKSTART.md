# Phase V Quick Start Guide

## Prerequisites Checklist
- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed (for frontend)
- [ ] Dapr CLI installed (`dapr --version`)
- [ ] Docker Desktop running (for Kafka)
- [ ] Backend dependencies installed (`pip install -r backend/requirements.txt`)

## 🚀 Start the System (5 Steps)

### Step 1: Start Kafka
```bash
# Using Docker Compose (if you have docker-compose.yml)
docker-compose up -d kafka zookeeper

# OR use Dapr's built-in Redis pub/sub (for testing)
# Edit dapr/components/pubsub.yaml to use Redis instead of Kafka
```

### Step 2: Verify Dapr Components
```bash
cd "D:\Panavirsty\Phase 51\Todo-Chat-Bot"
dapr components list --components-path ./dapr/components
```

Expected output:
```
NAME             TYPE             VERSION  SCOPES
reminder-cron    bindings.cron    v1
todo-pubsub      pubsub.kafka     v1
```

### Step 3: Start Backend with Dapr
```bash
cd backend

# Windows
dapr run --app-id todo-api --app-port 8000 --dapr-http-port 3500 --components-path ../dapr/components -- python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Linux/Mac
dapr run --app-id todo-api --app-port 8000 --dapr-http-port 3500 --components-path ../dapr/components -- uvicorn main:app --host 0.0.0.0 --port 8000
```

### Step 4: Start Frontend (Optional)
```bash
cd frontend
npm install
npm run dev
```

### Step 5: Run Verification Tests
```bash
cd backend
python verify_phase5_complete.py
```

## 🧪 Quick Test

### Test Event Publishing
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "demo123"}'

# Copy the access_token from response

# Create a task (publishes task.created event)
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "priority": "high"}'

# Check backend logs for: "Published task.created event for task_id=X"
```

### Test Recurring Tasks
```bash
# Create a recurring task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "recurrence": "daily",
    "due_date": "2025-12-21T09:00:00Z"
  }'

# Complete it (this will trigger creation of next instance)
curl -X PUT http://localhost:8000/api/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Wait 3 seconds and list tasks - you should see the new instance
curl http://localhost:8000/api/tasks -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Reminder System
```bash
# Create an overdue task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Overdue Task",
    "due_date": "2025-12-20T08:00:00Z"
  }'

# Manually trigger the cron (or wait for it to run every minute)
curl -X POST http://localhost:8000/reminder-cron

# Check logs for: "🔔 Sending Reminder for Task ID X"
```

## 📊 Monitor Logs

### Backend Logs
Look for these messages:
- ✅ `Published task.created event for task_id=X`
- ✅ `Published task.updated event for task_id=X`
- ✅ `Published task.completed event for task_id=X`
- ✅ `Reminder cron triggered`
- ✅ `🔔 Sending Reminder for Task ID X`
- ✅ `Created recurring task X (from task Y)`

### Dapr Logs
Look for:
- Subscription discovery on startup
- Event publishing confirmations
- Cron binding triggers every minute

## 🔧 Common Issues

### Kafka Not Running
**Symptom:** `Failed to publish task event: connection refused`
**Solution:** Start Kafka or switch to Redis pub/sub for testing

### Dapr Components Not Found
**Symptom:** `component not found: todo-pubsub`
**Solution:** Verify `--components-path` points to `../dapr/components`

### Recurring Tasks Not Created
**Symptom:** Completing a recurring task doesn't create next instance
**Solution:**
1. Check Dapr subscription discovery: `curl http://localhost:3500/dapr/subscribe`
2. Verify backend logs show "Received task.completed event"

### Reminders Not Working
**Symptom:** No reminders for overdue tasks
**Solution:**
1. Manually trigger: `curl -X POST http://localhost:8000/reminder-cron`
2. Check if task has `due_date` in the past and `reminder_sent=False`

## 🎯 Success Criteria

After running the verification script, you should see:
- ✅ All tests pass
- ✅ Events are published to Kafka
- ✅ Recurring tasks are automatically created
- ✅ Reminders are logged for overdue tasks

## 📚 Additional Resources

- **Implementation Details:** See `PHASE5_IMPLEMENTATION_SUMMARY.md`
- **Troubleshooting:** See `TROUBLESHOOTING.md`
- **API Documentation:** Visit http://localhost:8000/docs after starting the backend
- **Dapr Documentation:** https://docs.dapr.io/

## 🆘 Need Help?

If you encounter issues:
1. Check the backend logs for error messages
2. Verify all prerequisites are installed
3. Review the troubleshooting section in `PHASE5_IMPLEMENTATION_SUMMARY.md`
4. Check Dapr status: `dapr list`
