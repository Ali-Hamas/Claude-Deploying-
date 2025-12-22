# Quick Start Guide - Dapr Backend

## ✅ Issue Fixed!

**Problem:** Duplicate component name `todo-pubsub` (both Redis and In-Memory versions)

**Solution:** Renamed files:
- `pubsub-inmemory.yaml` → `pubsub.yaml` (ACTIVE)
- `pubsub.yaml` → `pubsub-redis.yaml.disabled` (DISABLED)

Now only ONE `todo-pubsub` component is loaded (in-memory version for development).

---

## 🚀 CORRECT COMMAND TO RUN

Use `--resources-path` instead of the deprecated `--components-path`:

```bash
cd backend
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --resources-path ../dapr/components -- uvicorn main:app --reload --port 8000
```

---

## 📋 WHAT THIS DOES

- Starts **Dapr sidecar** on port 3500
- Starts **FastAPI backend** on port 8000
- Loads Dapr components from `../dapr/components/`:
  - `pubsub.yaml` (in-memory pub/sub) ✅
  - `reminder-cron.yaml` (cron every 5 minutes) ✅
- Enables event-driven features:
  - Recurring tasks
  - Task reminders
  - Event publishing/subscription

---

## ✅ VERIFY IT'S WORKING

After starting, you should see:

```
ℹ️  Starting Dapr with id todo-backend. HTTP Port: 3500. gRPC Port: [random]
✅  You're up and running! Both Dapr and your app logs will appear here.
```

Then test:

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Dapr Subscriptions:**
   ```bash
   curl http://localhost:8000/dapr/subscribe
   ```

3. **Dapr Dashboard:**
   ```bash
   dapr dashboard
   ```
   Open http://localhost:8080

---

## 🔄 TO SWITCH TO REDIS (PRODUCTION)

If you want to use Redis instead of in-memory:

1. **Start Redis:**
   ```bash
   docker run -d --name redis -p 6379:6379 redis:latest
   ```

2. **Enable Redis component:**
   ```bash
   cd dapr/components
   mv pubsub.yaml pubsub-inmemory.yaml.disabled
   mv pubsub-redis.yaml.disabled pubsub-redis.yaml
   ```

3. **Restart Dapr** with the same command

---

## 🛑 TO STOP

Press `Ctrl+C` in the terminal

Dapr will automatically clean up the sidecar.

---

## 📚 NEXT STEPS

Follow **PHASE5_DEPLOYMENT_GUIDE.md** for:
- Testing recurring tasks
- Testing reminders
- Complete verification checklist

---

## 🐛 TROUBLESHOOTING

**Error: "duplicate definition of Component name"**
- Fixed! Only one `pubsub.yaml` file is active now

**Error: "port 8000 already in use"**
- Stop any running uvicorn/backend processes
- Use: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Mac/Linux)

**Error: "dapr: command not found"**
- Install Dapr CLI: `powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"`
- Then run: `dapr init`
