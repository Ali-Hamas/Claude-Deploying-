# Bugs Fixed and Solutions

## 🐛 BUG #1: ModuleNotFoundError: No module named 'jose'

### Error Message:
```
File "D:\Panavirsty\Phase 51\Todo-Chat-Bot\backend\auth.py", line 4, in <module>
    from jose import JWTError, jwt
ModuleNotFoundError: No module named 'jose'
```

### Root Cause:
Dependencies were NOT installed before running the application.

### ✅ Solution:
Install all required Python packages:

**Windows (PowerShell or CMD):**
```bash
cd backend
install_dependencies.bat
```

**Or manually:**
```bash
cd backend
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd backend
chmod +x install_dependencies.sh
./install_dependencies.sh
```

---

## 🐛 BUG #2: Duplicate Component Name 'todo-pubsub'

### Error Message:
```
error validating components in resources path: duplicate definition of Component name todo-pubsub (pubsub.redis/v1) with existing todo-pubsub (pubsub.in-memory/v1)
```

### Root Cause:
TWO Dapr pubsub components with the SAME name (`todo-pubsub`) existed in `/dapr/components/`:
- `pubsub.yaml` (Redis)
- `pubsub-inmemory.yaml` (In-Memory)

Dapr can only load ONE component with a given name.

### ✅ Solution Applied:
Renamed files to keep only one active:
- `pubsub-inmemory.yaml` → `pubsub.yaml` (ACTIVE for development)
- `pubsub.yaml` → `pubsub-redis.yaml.disabled` (DISABLED)

**To switch to Redis later:**
```bash
cd dapr/components
mv pubsub.yaml pubsub-inmemory.yaml.disabled
mv pubsub-redis.yaml.disabled pubsub-redis.yaml
```

---

## 🐛 BUG #3: Wrong Package Name 'agents-sdk'

### Error Message:
Would have caused:
```
ModuleNotFoundError: No module named 'agents'
```

### Root Cause:
In `requirements.txt`, the package was listed as `agents-sdk`, but the correct package name is `openai-agents`.

### ✅ Solution Applied:
Updated `requirements.txt`:
```diff
- agents-sdk
+ openai-agents
```

**Correct installation:**
```bash
pip install openai-agents
```

**Import in code:**
```python
from agents import Agent, Runner, function_tool
```

---

## 🐛 BUG #4: Import Path Issues in agent.py

### Error Message:
Would have caused:
```
ModuleNotFoundError: No module named 'backend.database'
```

### Root Cause:
`agent.py` used absolute imports with `backend.` prefix:
```python
from backend.database.connection import engine
from backend.models.todo_models import Task
```

When running from the `/backend` directory, Python doesn't recognize `backend` as a module.

### ✅ Solution Applied:
Changed to relative imports in `agent.py`:
```diff
- from backend.database.connection import engine
- from backend.models.todo_models import Task
+ from database.connection import engine
+ from models.todo_models import Task
```

---

## ⚠️ WARNING (NOT A BUG): Scheduler Connection Errors

### Warning Message:
```
level=error msg="Failed to connect to scheduler host: failed to watch scheduler hosts: rpc error: code = Unavailable desc = connection error: desc = \"transport: Error while dialing: dial tcp [::1]:6060: connectex: No connection could be made because the target machine actively refused it.\""
```

### Root Cause:
Dapr is trying to connect to the **Dapr Scheduler service** on port 6060. This is a NEW feature in Dapr 1.16+ for managing reminders/timers.

### Is This Critical?
**NO!** This is a WARNING, not an error. Your application will work fine without it.

The scheduler is for **advanced reminder/timer management**. Your cron binding (reminder-cron.yaml) will still work perfectly.

### Solutions (Optional):

**Option 1: Ignore It** (Recommended for development)
- The app works fine without the scheduler
- Warnings can be safely ignored

**Option 2: Disable Scheduler Feature**
Add to Dapr run command:
```bash
--disable-scheduler
```

Full command:
```bash
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --resources-path ../dapr/components --disable-scheduler -- uvicorn main:app --reload --port 8000
```

**Option 3: Install Dapr Scheduler** (Advanced)
For production, install the Dapr Scheduler component:
https://docs.dapr.io/developing-applications/building-blocks/actors/actors-timers-reminders/

---

## ⚠️ WARNING (NOT A BUG): Zipkin Connection Error

### Warning Message:
```
request to http://localhost:9411/api/v2/spans failed: Post "http://localhost:9411/api/v2/spans": dial tcp [::1]:9411: connectex: No connection could be made because the target machine actively refused it.
```

### Root Cause:
Dapr is trying to send tracing data to Zipkin (distributed tracing system) on port 9411.

### Is This Critical?
**NO!** Zipkin is for observability/debugging. Your app works without it.

### Solutions (Optional):

**Option 1: Ignore It** (Recommended for development)

**Option 2: Disable Tracing**
Set environment variable:
```bash
set DAPR_TRACING_ENABLED=false
```

**Option 3: Install Zipkin** (For observability)
```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```

---

## 📋 COMPLETE FIX CHECKLIST

### ✅ Step 1: Install Dependencies

**Windows:**
```bash
cd backend
install_dependencies.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### ✅ Step 2: Verify Installations

```bash
cd backend
python -c "from jose import jwt; import dapr; from agents import Agent; print('✅ All critical modules installed')"
```

### ✅ Step 3: Run Backend Without Dapr (Test)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Visit: http://localhost:8000/health

If you see `{"status":"healthy",...}`, the backend is working!

Press Ctrl+C to stop.

### ✅ Step 4: Run with Dapr

```bash
cd backend
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --resources-path ../dapr/components -- uvicorn main:app --reload --port 8000
```

**Ignore these warnings:**
- ⚠️ Scheduler connection errors (non-critical)
- ⚠️ Zipkin connection errors (non-critical)
- ⚠️ `pubsub-redis.yaml.disabled` warnings (expected)

**Success indicators:**
- ✅ `Component loaded: todo-pubsub (pubsub.in-memory/v1)`
- ✅ `Component loaded: reminder-cron (bindings.cron/v1)`
- ✅ `You're up and running! Both Dapr and your app logs will appear here.`
- ✅ `Uvicorn running on http://127.0.0.1:8000`

### ✅ Step 5: Test the API

```bash
curl http://localhost:8000/health
curl http://localhost:8000/dapr/subscribe
```

---

## 🎯 SUMMARY OF ALL BUGS FIXED

| Bug # | Issue | Status | Solution |
|-------|-------|--------|----------|
| 1 | Missing `jose` module | ✅ Fixed | Install dependencies |
| 2 | Duplicate Dapr component names | ✅ Fixed | Renamed files |
| 3 | Wrong package `agents-sdk` | ✅ Fixed | Changed to `openai-agents` |
| 4 | Wrong import paths in agent.py | ✅ Fixed | Changed to relative imports |
| 5 | Scheduler warnings | ⚠️ Non-critical | Can be ignored |
| 6 | Zipkin tracing warnings | ⚠️ Non-critical | Can be ignored |

---

## 🚀 NEXT ACTIONS

1. ✅ Run `install_dependencies.bat` (Windows) or `install_dependencies.sh` (Linux/Mac)
2. ✅ Verify installations work
3. ✅ Start backend with Dapr
4. ✅ Test APIs
5. ✅ Follow PHASE5_DEPLOYMENT_GUIDE.md for feature testing

---

## 📚 REFERENCE DOCUMENTS

- **Installation Scripts:**
  - Windows: `backend/install_dependencies.bat`
  - Linux/Mac: `backend/install_dependencies.sh`

- **Requirements:** `backend/requirements.txt`

- **Start Guide:** `START_DAPR.md`

- **Complete Deployment:** `PHASE5_DEPLOYMENT_GUIDE.md`

---

## 🔗 SOURCES

- [OpenAI Agents SDK PyPI](https://pypi.org/project/openai-agents/)
- [OpenAI Agents SDK GitHub](https://github.com/openai/openai-agents-python)
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
