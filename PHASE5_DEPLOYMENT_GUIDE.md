# Phase 5 Deployment Guide - Event-Driven Architecture with Dapr

## 🎯 Phase 5 Completion Status

### ✅ COMPLETED ITEMS

#### Backend Implementation
- ✅ Event service implemented (backend/services/event_service.py)
- ✅ Dapr pub/sub integration with DaprClient
- ✅ Task completion event publishing
- ✅ Task reminder event publishing
- ✅ Recurring task logic (daily, weekly, monthly, yearly)
- ✅ Cron handler for reminders (/reminder-cron endpoint)
- ✅ Dapr subscription endpoints implemented
  - ✅ POST /api/events/task-completed
  - ✅ POST /api/events/task-reminder
  - ✅ GET /dapr/subscribe
- ✅ Event handlers store reminders in conversation history
- ✅ reminder_sent field in Task model to prevent spam

#### Dapr Configuration
- ✅ Local Dapr components (dapr/components/)
  - ✅ pubsub.yaml (Redis)
  - ✅ pubsub-inmemory.yaml (Development)
  - ✅ reminder-cron.yaml (Every 5 minutes)
- ✅ Kubernetes Dapr components (k8s/components/)
  - ✅ pubsub.yaml (Kafka/In-Memory)
  - ✅ statestore.yaml (PostgreSQL)
  - ✅ saas.yaml

#### Database Schema
- ✅ Task model with all Phase 5 fields:
  - ✅ priority (low, medium, high, urgent)
  - ✅ due_date (datetime, nullable)
  - ✅ tags (JSON array)
  - ✅ recurrence (daily, weekly, monthly, yearly)
  - ✅ reminder_sent (boolean)
- ✅ Conversation and Message models for chat history
- ✅ User model with authentication

#### Dependencies
- ✅ requirements.txt updated with all dependencies:
  - ✅ fastapi, uvicorn
  - ✅ sqlmodel, psycopg2-binary
  - ✅ openai, mcp, agents-sdk
  - ✅ python-jose[cryptography]
  - ✅ passlib[argon2], argon2-cffi
  - ✅ python-dotenv
  - ✅ dapr, dapr-ext-fastapi
  - ✅ python-multipart

#### Bug Fixes Applied
- ✅ Fixed agent.py imports (backend.database.connection → database.connection)
- ✅ Added missing python-dotenv dependency
- ✅ Added missing agents-sdk dependency

---

## 📋 DEPLOYMENT CHECKLIST

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Expected output:** All packages install successfully without errors.

**Verify:**
```bash
python -c "import jose; import passlib; import dapr; import agents; print('All imports successful!')"
```

---

### Step 2: Configure Environment Variables

Edit `backend/.env`:

```bash
# For local development (SQLite)
DATABASE_URL=sqlite:///./todo.db

# For production (Neon PostgreSQL)
# DATABASE_URL=postgresql://username:password@ep-xxxxx.aws.neon.tech/neondb?sslmode=require

BETTER_AUTH_SECRET=your-super-secret-key-change-in-production
```

**For production:** Get your Neon PostgreSQL connection string from https://neon.tech

---

### Step 3: Install Dapr CLI (if not already installed)

**Windows:**
```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**macOS/Linux:**
```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

**Verify:**
```bash
dapr --version
```

---

### Step 4: Initialize Dapr

```bash
dapr init
```

This installs:
- Dapr runtime
- Redis (for state store and pub/sub)
- Zipkin (for distributed tracing)

**Verify:**
```bash
dapr list
```

---

### Step 5: Choose Pub/Sub Component

#### Option A: In-Memory (Recommended for Development)

No additional setup needed! Uses `pubsub-inmemory.yaml`

#### Option B: Redis (Recommended for Production)

Ensure Redis is running:

**Windows (WSL2 or Docker):**
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

**macOS/Linux:**
```bash
redis-server
```

**Verify Redis:**
```bash
redis-cli ping
# Should return: PONG
```

---

### Step 6: Test Backend Without Dapr

First, verify the backend works standalone:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Dapr subscribe endpoint
curl http://localhost:8000/dapr/subscribe
```

**Expected response from /dapr/subscribe:**
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

Stop the server (Ctrl+C) before proceeding.

---

### Step 7: Run Backend with Dapr

#### Development Mode (In-Memory Pub/Sub)

```bash
cd backend
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../dapr/components \
  -- uvicorn main:app --reload --port 8000
```

**What this does:**
- Starts Dapr sidecar on port 3500
- Starts FastAPI backend on port 8000
- Loads Dapr components from ../dapr/components/
- Enables pub/sub, cron bindings, and event delivery

#### Production Mode (Redis Pub/Sub)

Same command as above - Dapr will use `pubsub.yaml` (Redis) automatically if Redis is running.

---

### Step 8: Verify Dapr Integration

#### Check Dapr Dashboard

```bash
dapr dashboard
```

Open http://localhost:8080 and verify:
- Application "todo-backend" is listed
- Components are loaded (todo-pubsub, reminder-cron)
- Topics are visible (task-events, reminders)

#### Check Dapr Subscriptions

```bash
curl http://localhost:8000/dapr/subscribe
```

Should return the subscription configuration.

#### Check Running Dapr Apps

```bash
dapr list
```

Should show "todo-backend" with APP PORT 8000 and DAPR HTTP PORT 3500.

---

### Step 9: Test Event-Driven Features

#### Test 1: Create and Complete a Recurring Task

1. **Register a user:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "name": "Test User"
  }'
```

Save the `access_token` from the response.

2. **Create a recurring task:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Exercise",
    "description": "30 minutes cardio",
    "priority": "high",
    "tags": ["health", "daily"],
    "recurrence": "daily"
  }'
```

Save the task `id` from the response.

3. **Complete the task (triggers event):**
```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

4. **Verify new recurring task was created:**
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected:** You should see TWO tasks:
- Original task (completed)
- New task (pending) with due_date = tomorrow

#### Test 2: Task Reminders

1. **Create a task due in 8 minutes:**

Calculate the time 8 minutes from now and format as ISO 8601:
```bash
# Example: 2025-12-19T15:08:00Z
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important Meeting",
    "description": "Quarterly review",
    "priority": "urgent",
    "due_date": "2025-12-19T15:08:00Z",
    "tags": ["work", "meeting"]
  }'
```

2. **Wait up to 5 minutes** (cron runs every 5 minutes)

3. **Watch backend logs** for reminder events:
```
🔔 Sending reminder for Task ID 2
REMINDER: User 1 has task 'Important Meeting' due in 8 minutes
✓ Reminder stored in conversation 1 for user 1
```

4. **Verify reminder in conversation history:**
```bash
# Use the chat endpoint to see history (if implemented)
# Or check database directly
```

#### Test 3: Direct Event Publishing via Dapr

```bash
curl -X POST http://localhost:3500/v1.0/publish/todo-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.completed",
    "task_id": 999,
    "user_id": 1,
    "title": "Test Recurring Task",
    "description": "Testing Dapr",
    "priority": "medium",
    "due_date": "2025-12-20T10:00:00Z",
    "tags": ["test"],
    "recurrence": "weekly",
    "completed_at": "2025-12-19T14:30:00Z"
  }'
```

**Expected:** Check logs - a new task should be created automatically.

---

### Step 10: Frontend Setup (Optional for Phase 5)

The frontend is Next.js-based but Phase 5 focuses on backend event-driven architecture.

If you want to test the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## 🐛 TROUBLESHOOTING

### Issue: ModuleNotFoundError: No module named 'jose'

**Solution:**
```bash
cd backend
pip install python-jose[cryptography]
```

### Issue: ModuleNotFoundError: No module named 'agents'

**Solution:**
```bash
pip install agents-sdk
```

### Issue: Events not being delivered

**Diagnosis:**
1. Check Dapr is running: `dapr list`
2. Check subscriptions: `curl http://localhost:8000/dapr/subscribe`
3. Check Dapr logs: `dapr logs --app-id todo-backend`
4. Check if Redis is running (if using Redis): `redis-cli ping`

**Solution:**
- Restart Dapr: Stop the app (Ctrl+C) and restart with `dapr run...`
- Use in-memory pub/sub for development (no Redis needed)

### Issue: Cron not triggering

**Diagnosis:**
Check if reminder-cron component is loaded:
```bash
curl http://localhost:8000/dapr/subscribe
```

**Solution:**
- Verify `reminder-cron.yaml` is in `dapr/components/`
- Restart Dapr application
- Check Dapr logs for cron binding errors

### Issue: Redis connection refused

**Solution:**
Option 1: Install and start Redis
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

Option 2: Use in-memory pub/sub (development)
- Ensure `pubsub-inmemory.yaml` is in `dapr/components/`
- Restart Dapr

---

## 📊 PHASE 5 VERIFICATION CHECKLIST

Mark these off as you verify:

- [ ] All Python dependencies installed successfully
- [ ] Backend starts without import errors
- [ ] Dapr CLI installed and initialized
- [ ] Dapr sidecar starts with backend
- [ ] /dapr/subscribe endpoint returns subscriptions
- [ ] Creating and completing a recurring task creates a new task
- [ ] Tasks due within 10 minutes trigger reminders
- [ ] Reminders appear in conversation history
- [ ] Events publish to Dapr topics successfully
- [ ] Dapr dashboard shows app and components
- [ ] No errors in backend or Dapr logs

---

## 🚀 NEXT STEPS AFTER PHASE 5

### Production Deployment

1. **Database:** Switch to Neon PostgreSQL
   - Update `DATABASE_URL` in `.env`
   - Run migrations if needed

2. **Kubernetes Deployment:**
   - Use components in `k8s/components/`
   - Deploy with Dapr sidecar injection
   - Configure ingress for backend API

3. **Monitoring:**
   - Enable Dapr tracing (Zipkin/Jaeger)
   - Set up logging aggregation
   - Monitor pub/sub message delivery

### Frontend Integration

- Implement chat interface with OpenAI ChatKit
- Connect to backend API endpoints
- Display task reminders in chat UI
- Add authentication flow

### Additional Features

- Add user notifications (email/SMS)
- Implement task sharing between users
- Add task analytics and insights
- Implement search and filtering

---

## 📚 REFERENCE DOCUMENTS

- **Event-Driven Spec:** specs/architecture/event_driven.md
- **Dapr Infrastructure:** specs/deployment/dapr_infra.md
- **Advanced Features:** specs/features/advanced_features.md
- **Database Schema:** specs/database/schema.md
- **Dapr Components README:** dapr/README.md

---

## 🎉 PHASE 5 COMPLETE!

Once all verification items are checked, Phase 5 (Event-Driven Architecture with Dapr) is complete!

**Key Achievements:**
- Stateless, event-driven backend
- Automatic recurring task creation
- Proactive task reminders
- Scalable pub/sub architecture
- Production-ready Dapr integration
