#!/bin/bash

echo "========================================"
echo " Deploying Hackathon Todo to Vercel"
echo "========================================"
echo ""

echo "Step 1: Installing Vercel CLI (if not installed)..."
npm install -g vercel

echo ""
echo "Step 2: Logging into Vercel..."
echo "Please follow the browser login prompt..."
vercel login

echo ""
echo "Step 3: Deploying frontend to production..."
vercel --prod --name hackathon-todo

echo ""
echo "========================================"
echo " Deployment Complete!"
echo "========================================"
echo ""
echo "IMPORTANT: Configure environment variables:"
echo "1. Go to your Vercel dashboard"
echo "2. Navigate to Settings -> Environment Variables"
echo "3. Add: NEXT_PUBLIC_API_URL"
echo "4. Value: Your backend URL (Railway/Render)"
echo ""
echo "For local testing, use: http://YOUR_IP:8000"
echo ""
echo "Then redeploy: vercel --prod"
echo ""
