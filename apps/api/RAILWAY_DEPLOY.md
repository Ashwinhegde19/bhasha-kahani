# Railway Deployment Guide

## 🚀 Deploy to Railway (FREE $5 Credit)

### Step 1: Sign Up
1. Go to: https://railway.app
2. Sign up with GitHub
3. Verify with credit card (for $5 free credit)
4. No charges unless you exceed $5

### Step 2: Create Project
1. Railway Dashboard → "New Project"
2. Select "Deploy from GitHub repo"
3. Choose: `Ashwinhegde19/bhasha-kahani`
4. Select branch: `feature/backend-sprint`

### Step 3: Configure Service
```
Name: bhasha-kahani-api
Root Directory: apps/api
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

### Step 4: Add Environment Variables
In Railway Dashboard → Your Service → Variables:

```env
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres
SUPABASE_SERVICE_KEY=your_key_here
SARVAM_API_KEY=your_key_here
SECRET_KEY=random_secret_here
REDIS_URL=redis://localhost:6379
```

### Step 5: Deploy!
Click "Deploy" and wait 2-3 minutes.

Your API will be live at:
```
https://bhasha-kahani-api.up.railway.app
```

### Step 6: Test
```bash
curl https://bhasha-kahani-api.up.railway.app/health
curl https://bhasha-kahani-api.up.railway.app/stories
```

## 💰 Cost
- FREE for 2-3 months with $5 credit
- After that: ~$5/month for light usage
- Can upgrade or move to other platform later

## 🎯 Why Railway?
✅ Works with Supabase (unlike Vercel)
✅ Your code runs as-is
✅ No build issues
✅ Easy deployment
✅ Good for hackathons
