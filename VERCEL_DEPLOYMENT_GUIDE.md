# 🚀 Vercel Deployment Guide for Hackathon Todo App

## 📋 Overview

This guide explains how to deploy your Todo application with:
- **Frontend**: Next.js → Vercel
- **Backend**: Python FastAPI → Railway/Render (Not Vercel compatible)

## ⚠️ Important: Why We Can't Deploy Everything to Vercel

Vercel is designed for:
- ✅ Frontend frameworks (Next.js, React, Vue)
- ✅ Serverless functions (short-lived, stateless)
- ❌ **NOT for**: Long-running Python backends with Dapr, Redis, and PostgreSQL

Your backend requires:
- Persistent database connections
- Dapr sidecar processes
- Redis pub/sub
- Long-running Uvicorn server

**Solution**: Deploy frontend to Vercel, backend elsewhere.

---

## 🎯 Deployment Strategy

### Option A: Quick Deploy (Frontend Only)

Deploy just the frontend to Vercel for demo purposes, keep backend running locally.

### Option B: Full Production Deploy (Recommended)

1. **Frontend** → Vercel
2. **Backend** → Railway.app or Render.com
3. **Database** → Neon.tech (PostgreSQL)
4. **Redis** → Upstash.com

---

## 📦 Option A: Deploy Frontend Only to Vercel

### Prerequisites

- Vercel account (free): https://vercel.com/signup
- Git repository (GitHub, GitLab, or Bitbucket)

### Step 1: Prepare Your Repository

1. **Ensure your code is in a Git repository:**

```bash
cd "d:\Panavirsty\Phase 51\Todo-Chat-Bot"
git init
git add .
git commit -m "Prepare for deployment"
```

2. **Create GitHub repository** (optional but recommended):
   - Go to https://github.com/new
   - Create a new repository named `hackathon-todo`
   - Push your code:

```bash
git remote add origin https://github.com/YOUR_USERNAME/hackathon-todo.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Vercel via CLI

```bash
cd frontend

# Login to Vercel
vercel login

# Deploy (production)
vercel --prod

# When prompted:
# - Project name: hackathon-todo
# - Directory: ./ (current directory)
# - Build settings: auto-detected (Next.js)
```

### Step 3: Configure Environment Variables

After deployment, add the backend URL:

```bash
# For local backend testing
vercel env add NEXT_PUBLIC_API_URL production
# Enter: http://YOUR_LOCAL_IP:8000
# Example: http://192.168.100.27:8000

# Or use ngrok to expose local backend
ngrok http 8000
# Then set: https://YOUR_NGROK_URL.ngrok.io
```

### Step 4: Redeploy with Environment Variables

```bash
vercel --prod
```

Your frontend is now live at: `https://hackathon-todo.vercel.app`

---

## 🌐 Option B: Full Production Deployment

### Part 1: Deploy Backend to Railway

Railway.app supports Python backends with Dapr.

#### Step 1: Sign Up

- Go to https://railway.app/
- Sign up with GitHub

#### Step 2: Create New Project

```bash
cd backend

# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

#### Step 3: Configure Environment Variables in Railway Dashboard

Add these in Railway dashboard:

```env
DATABASE_URL=postgresql://user:password@host/db
BETTER_AUTH_SECRET=your-super-secret-key-here
OPENAI_API_KEY=sk-...your-key-here
```

#### Step 4: Get Backend URL

Railway will give you a URL like: `https://your-app.railway.app`

### Part 2: Deploy Frontend to Vercel

```bash
cd frontend

# Deploy to Vercel
vercel --prod

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-app.railway.app

# Redeploy
vercel --prod
```

---

## 🗄️ Database Setup (Production)

### Using Neon.tech (Recommended)

1. **Sign up**: https://neon.tech/
2. **Create new project**: hackathon-todo
3. **Copy connection string**:
   ```
   postgresql://user:pass@ep-xxx.aws.neon.tech/neondb?sslmode=require
   ```
4. **Add to Railway environment variables**:
   ```
   DATABASE_URL=postgresql://user:pass@ep-xxx.aws.neon.tech/neondb?sslmode=require
   ```

### Using Supabase (Alternative)

1. **Sign up**: https://supabase.com/
2. **Create project**
3. **Get connection string** from Settings → Database
4. **Add to Railway**

---

## 🔴 Redis Setup (Production)

### Using Upstash

1. **Sign up**: https://upstash.com/
2. **Create Redis database**
3. **Copy Redis URL**: `redis://default:password@host:port`
4. **Update Dapr component** in backend:

```yaml
# dapr/components/pubsub-redis-prod.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: "your-upstash-host:port"
  - name: redisPassword
    value: "your-upstash-password"
```

---

## 🧪 Testing Your Deployment

### Test Frontend

1. Visit: `https://hackathon-todo.vercel.app`
2. Create account
3. Try creating a task

### Test Backend API

```bash
curl https://your-backend.railway.app/health
```

### Test Full Integration

1. Register user in frontend
2. Create task
3. Complete task
4. Verify recurring task appears

---

## 🐛 Troubleshooting

### ERROR: "Failed to fetch" in Production

**Cause**: Backend URL not configured or CORS issue

**Solution**:
1. Verify `NEXT_PUBLIC_API_URL` is set in Vercel:
   ```bash
   vercel env ls
   ```
2. Check CORS in backend `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://hackathon-todo.vercel.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### ERROR: Dapr Not Working on Railway

**Solution**: Railway doesn't support Dapr sidecars in free tier.

**Workaround**: Remove Dapr dependency for simple deployment:
- Disable event publishing features
- Use simple CRUD operations
- Or upgrade to containerized deployment (Docker)

### ERROR: Database Connection Failed

**Check**:
```bash
# In Railway logs
# Verify DATABASE_URL is set correctly
```

---

## 📊 Deployment Checklist

### Frontend (Vercel)
- [ ] Code pushed to Git
- [ ] Vercel CLI installed
- [ ] Deployed with `vercel --prod`
- [ ] Environment variable `NEXT_PUBLIC_API_URL` set
- [ ] Frontend accessible at `https://hackathon-todo.vercel.app`

### Backend (Railway)
- [ ] Railway CLI installed
- [ ] Backend deployed
- [ ] Environment variables configured:
  - [ ] `DATABASE_URL`
  - [ ] `BETTER_AUTH_SECRET`
  - [ ] `OPENAI_API_KEY`
- [ ] Backend accessible at `https://your-app.railway.app`
- [ ] Health check endpoint responds: `/health`

### Database
- [ ] PostgreSQL database created (Neon/Supabase)
- [ ] Connection string added to backend
- [ ] Tables created (auto-created on first run)

### Integration
- [ ] Frontend can reach backend
- [ ] CORS configured correctly
- [ ] Authentication working
- [ ] Tasks can be created and completed

---

## 🎉 Success Criteria

Your deployment is successful when:

1. ✅ Frontend loads at `https://hackathon-todo.vercel.app`
2. ✅ You can create an account
3. ✅ You can create, view, and complete tasks
4. ✅ No console errors in browser
5. ✅ Backend health check returns 200 OK

---

## 🔗 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Railway Dashboard**: https://railway.app/dashboard
- **Neon Dashboard**: https://console.neon.tech/
- **Upstash Dashboard**: https://console.upstash.com/

---

## 💡 Alternative: Deploy Both via Docker (Advanced)

If you want to deploy the entire stack together:

### Use DigitalOcean App Platform or AWS ECS

1. **Dockerize your application**
2. **Create docker-compose.yml**:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - redis
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

3. **Deploy to DigitalOcean**:
   - Use App Platform
   - Or use Kubernetes with Helm

---

## 📝 Notes

- **Free Tier Limitations**: Vercel free tier is generous but has limits
- **Backend Hosting**: Railway free tier gives you $5/month credit
- **Database**: Neon.tech free tier is perfect for small projects
- **Redis**: Upstash free tier has usage limits

---

## ✅ Next Steps After Deployment

1. **Monitor performance** in Vercel Analytics
2. **Set up error tracking** (Sentry)
3. **Configure custom domain** (if desired)
4. **Set up CI/CD** with GitHub Actions
5. **Add monitoring** for backend (Railway logs)

---

**Need Help?**

- Vercel Support: https://vercel.com/support
- Railway Docs: https://docs.railway.app/
- Community Discord: https://discord.gg/vercel

Good luck with your deployment! 🚀
