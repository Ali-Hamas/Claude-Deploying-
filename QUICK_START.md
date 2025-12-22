# 🚀 Quick Start Guide - Todo Chat Bot

## ✅ ISSUES FIXED

### 1. Hydration Mismatch Error (Frontend)
**Fixed!** Added `suppressHydrationWarning` to prevent browser extension conflicts.

### 2. "Failed to fetch" Errors
**Cause:** Backend is not running.
**Solution:** Start the backend (see below).

---

## 📋 STEP-BY-STEP STARTUP

### Step 1: Start Backend

**Option A: With Dapr (Full Features)**
```bash
cd backend
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --resources-path ../dapr/components -- uvicorn main:app --reload --port 8000
```

**Option B: Without Dapr (Simple Testing)**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Success Indicators:**
```
✓ Component loaded: todo-pubsub (pubsub.in-memory/v1)
✓ Component loaded: reminder-cron (bindings.cron/v1)
✓ Uvicorn running on http://127.0.0.1:8000
✓ Created default user: admin@example.com
✓ Application startup complete.
```

**Ignore These Warnings:**
- ⚠️ Scheduler connection errors (non-critical)
- ⚠️ Zipkin tracing errors (non-critical)

---

### Step 2: Start Frontend

**In a NEW terminal:**
```bash
cd frontend
npm run dev
```

**Success:**
```
✓ Ready in 2.5s
○ Local:        http://localhost:3000
```

---

### Step 3: Test the System

#### Test Backend API:
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{"status":"healthy","message":"Todo API is running!"}
```

#### Test Frontend:
Open browser: http://localhost:3000

---

## 🔐 DEFAULT LOGIN CREDENTIALS

The backend creates 3 default users:

| Email | Password | Purpose |
|-------|----------|---------|
| admin@example.com | admin123 | Admin user |
| demo@example.com | demo123 | Demo user |
| test@example.com | test123 | Test user |

---

## 🐛 TROUBLESHOOTING

### Issue: "Failed to fetch"

**Symptoms:**
- Chat shows "Failed to fetch"
- Can't create tasks
- Login doesn't work

**Cause:** Backend is not running

**Solution:**
1. Check if backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. If you get an error, start the backend:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

---

### Issue: Port 8000 Already in Use

**Symptoms:**
```
ERROR: [Errno 10048] error while attempting to bind on address
```

**Solution:**

**Windows:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

---

### Issue: Hydration Mismatch Warning (Fixed)

**Symptoms:**
```
Error: A tree hydrated but some attributes of the server rendered HTML didn't match
```

**Cause:** Browser extensions modifying HTML

**Status:** ✅ FIXED - Added `suppressHydrationWarning` to layout.js

---

### Issue: ModuleNotFoundError

**Symptoms:**
```
ModuleNotFoundError: No module named 'jose'
```

**Cause:** Dependencies not installed for the correct Python

**Solution:**
```bash
cd backend

# Windows
install_dependencies.bat

# Linux/Mac
chmod +x install_dependencies.sh
./install_dependencies.sh
```

---

## 📊 SYSTEM ARCHITECTURE

```
┌─────────────────┐
│   Frontend      │  Next.js 16 on :3000
│   (React UI)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Backend       │  FastAPI on :8000
│   (API Server)  │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌───────┐ ┌──────┐  ┌──────────┐
│ SQLite│ │ Dapr │  │  OpenAI  │
│  DB   │ │Sidecar│ │  Agents  │
└───────┘ └──────┘  └──────────┘
```

---

## 🎯 TESTING CHECKLIST

### Backend Tests:
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] Register user: POST `/auth/register`
- [ ] Login: POST `/auth/login`
- [ ] Create task: POST `/api/tasks`
- [ ] List tasks: GET `/api/tasks`

### Frontend Tests:
- [ ] Page loads at http://localhost:3000
- [ ] No hydration errors in console
- [ ] Login page works
- [ ] Can register new user
- [ ] Chat interface loads

### Integration Tests:
- [ ] Login from frontend works
- [ ] Create task from chat works
- [ ] Task list displays correctly
- [ ] Task completion works

---

## 🔥 COMMON COMMANDS

### Backend:

```bash
# Start with Dapr
cd backend
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --resources-path ../dapr/components -- uvicorn main:app --reload --port 8000

# Start without Dapr
cd backend
uvicorn main:app --reload --port 8000

# Install dependencies
cd backend
pip install -r requirements.txt

# Check if backend is running
curl http://localhost:8000/health
```

### Frontend:

```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev

# Build for production
npm run build
npm start
```

### Dapr:

```bash
# Check Dapr status
dapr list

# Open Dapr dashboard
dapr dashboard

# Stop Dapr app
# Press Ctrl+C in the terminal
```

---

## 📚 RELATED DOCUMENTATION

- **BUGS_FIXED.md** - All bugs and solutions
- **PHASE5_DEPLOYMENT_GUIDE.md** - Complete Phase 5 guide
- **START_DAPR.md** - Dapr-specific instructions
- **backend/install_dependencies.bat** - Windows dependency installer
- **backend/install_dependencies.sh** - Linux/Mac dependency installer

---

## 🆘 STILL STUCK?

### Check These:

1. **Both servers running?**
   - Backend: http://localhost:8000/health
   - Frontend: http://localhost:3000

2. **Dependencies installed?**
   - Backend: `pip list | grep jose`
   - Frontend: `npm list next`

3. **Ports available?**
   - Backend needs port 8000
   - Frontend needs port 3000
   - Dapr needs port 3500

4. **Environment variables set?**
   - Check `backend/.env` exists
   - `DATABASE_URL` is set
   - `BETTER_AUTH_SECRET` is set

---

## ✅ SUCCESS CHECKLIST

Mark these when complete:

- [ ] Dependencies installed (backend)
- [ ] Dependencies installed (frontend)
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:8000/health
- [ ] Can access http://localhost:3000
- [ ] No hydration errors in browser console
- [ ] Can register a user
- [ ] Can login
- [ ] Can create a task
- [ ] Can list tasks
- [ ] Dapr components load (if using Dapr)

---

## 🎉 YOU'RE READY!

Once all checks pass:
1. Backend running on http://localhost:8000
2. Frontend running on http://localhost:3000
3. Login with `demo@example.com` / `demo123`
4. Start creating tasks!

**Phase 5 is complete! Your event-driven todo app with AI integration is live!** 🚀
