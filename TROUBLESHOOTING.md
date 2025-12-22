# 🔧 Troubleshooting Guide - "Failed to Fetch" Error

## ❌ Error: "Failed to fetch"

### What This Means:
Your **frontend** (Next.js) is trying to connect to your **backend** (FastAPI), but the backend is not running or not reachable.

### Visual Explanation:
```
Frontend (Port 3000) ──[HTTP Request]──> Backend (Port 8000)
       ✅ Running                              ❌ NOT Running

Result: "Failed to fetch" error
```

---

## 🎯 SOLUTION: Start Both Servers

You need **TWO terminals running at the same time**:

### Terminal 1: Backend Server

**Option 1: Double-click the script**
```
START_BACKEND.bat
```

**Option 2: Manual command**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
Created default user: admin@example.com
Created default user: demo@example.com
Created default user: test@example.com
```

---

### Terminal 2: Frontend Server

**Option 1: Double-click the script**
```
START_FRONTEND.bat
```

**Option 2: Manual command**
```bash
cd frontend
npm run dev
```

**You should see:**
```
✓ Ready in 2.5s
○ Local:   http://localhost:3000
```

---

## ✅ How to Verify Everything is Working

### Step 1: Check Backend is Running

Open browser or run in terminal:
```bash
curl http://127.0.0.1:8000/health
```

**Expected Response:**
```json
{"status":"healthy","message":"Todo API is running!"}
```

**If you get an error:** Backend is NOT running. Start it!

---

### Step 2: Check Frontend is Running

Open browser: http://localhost:3000

**Expected:** You should see the Todo app login/chat page

**If page doesn't load:** Frontend is NOT running. Start it!

---

### Step 3: Test the Connection

1. Open http://localhost:3000 in your browser
2. Login with: `demo@example.com` / `demo123`
3. Type in chat: `help`
4. **If you see a response:** ✅ Everything is working!
5. **If you see "Failed to fetch":** ❌ Backend is not running

---

## 🔍 Why "Failed to Fetch" Happens

### Cause 1: Backend Not Running (Most Common)

**Symptoms:**
- Frontend loads fine
- Can type messages
- Get "Failed to fetch" error when sending messages

**Solution:**
Start the backend server!

---

### Cause 2: Wrong Backend URL

**Check your frontend configuration:**

File: `frontend/hooks/useChat.js` (Line 39)
```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
```

**Make sure:**
- Backend is running on port **8000**
- URL is `http://127.0.0.1:8000` (not localhost, not https)

---

### Cause 3: Port Already in Use

**Symptoms:**
```
ERROR: [Errno 10048] Only one usage of each socket address
```

**Solution (Windows):**
```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number from above)
taskkill /PID <PID> /F
```

**Solution (Git Bash/Linux/Mac):**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

---

### Cause 4: Firewall Blocking Connection

**Solution (Windows):**
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Click "Change settings"
4. Find "Python" and check both Private and Public
5. Click OK

---

### Cause 5: CORS Issues

**Symptoms:**
- Backend is running
- Frontend is running
- Still get "Failed to fetch"
- Browser console shows CORS error

**Solution:**
The backend already has CORS configured in `main.py` (lines 25-31). If you still have issues, check:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚨 Common Mistakes

### Mistake 1: Only Starting Frontend

```
❌ Frontend running on :3000
❌ Backend NOT running
Result: "Failed to fetch"
```

**Fix:** Start BOTH servers!

---

### Mistake 2: Wrong Directory

```bash
# ❌ WRONG - Running from root directory
uvicorn main:app --reload

# ✅ CORRECT - Running from backend directory
cd backend
uvicorn main:app --reload
```

---

### Mistake 3: Using Python 3.12 Instead of 3.11

**Check which Python uvicorn uses:**
```bash
which uvicorn
uvicorn --version
```

**Should show:** Python 3.11.9

**If wrong version:** Install dependencies for the correct Python:
```bash
# Use the Python that uvicorn uses
"C:\Users\Kazuma Satou\AppData\Local\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt
```

---

## 📊 Quick Diagnostic Checklist

Run through this checklist:

- [ ] Backend is running: `curl http://127.0.0.1:8000/health`
- [ ] Frontend is running: Open http://localhost:3000
- [ ] Can see login page
- [ ] Can login with demo@example.com / demo123
- [ ] Backend shows no errors in terminal
- [ ] Frontend shows no red errors in browser console (F12)
- [ ] Port 8000 is not blocked by firewall
- [ ] Port 3000 is not blocked by firewall

---

## 🎯 Still Not Working?

### Debug Step 1: Check Backend Logs

When backend starts, you should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**If you see errors:** Share the error message!

---

### Debug Step 2: Check Frontend Console

1. Open http://localhost:3000
2. Press F12 (Developer Tools)
3. Go to "Console" tab
4. Try sending a message
5. Look for errors (red text)

**Common errors:**
- `Failed to fetch` = Backend not running
- `CORS error` = CORS configuration issue
- `401 Unauthorized` = Not logged in / Invalid token

---

### Debug Step 3: Test Backend Directly

```bash
# Test health endpoint
curl http://127.0.0.1:8000/health

# Test chat endpoint (need auth token)
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "help"}'
```

---

## 💡 Pro Tips

### Tip 1: Keep Both Terminals Open

- Terminal 1: Backend (black screen with logs)
- Terminal 2: Frontend (colorful Next.js output)

**Don't close these terminals while using the app!**

---

### Tip 2: Check Logs When Issues Happen

When you get "Failed to fetch":
1. Look at backend terminal - any errors?
2. Look at frontend terminal - any errors?
3. Look at browser console (F12) - any errors?

---

### Tip 3: Restart Backend if Needed

If backend is acting weird:
1. Press `Ctrl+C` in backend terminal
2. Wait for it to stop
3. Run `uvicorn main:app --reload --port 8000` again

---

## 📞 Quick Reference Commands

### Start Backend:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend:
```bash
cd frontend
npm run dev
```

### Test Backend:
```bash
curl http://127.0.0.1:8000/health
```

### Check What's Running:
```bash
# Windows
netstat -ano | findstr ":8000"
netstat -ano | findstr ":3000"

# Linux/Mac
lsof -i :8000
lsof -i :3000
```

### Kill Process:
```bash
# Windows (replace PID)
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>
```

---

## 🎉 Success!

When everything works, you should:
- ✅ See backend running in terminal 1
- ✅ See frontend running in terminal 2
- ✅ Open http://localhost:3000 in browser
- ✅ Login successfully
- ✅ Send messages and get responses
- ✅ No "Failed to fetch" errors!

---

## 📚 Related Files

- **START_BACKEND.bat** - Quick script to start backend (Windows)
- **START_FRONTEND.bat** - Quick script to start frontend (Windows)
- **QUICK_START.md** - Complete startup guide
- **BUGS_FIXED.md** - All bugs and solutions
- **PHASE5_DEPLOYMENT_GUIDE.md** - Full deployment guide
