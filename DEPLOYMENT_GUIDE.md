# 🚀 GitHub & Render Deployment Guide

This guide gives you step-by-step instructions to:
1. Push your project code to **GitHub** safely (without exposing your API key).
2. Deploy the web application for free on **Render**.

---

## 🔒 Part 1: Push to GitHub (Safely)

### Step 1: Open Terminal and Navigate to Project
```bash
cd /Users/shriyasanjayyerane/.gemini/antigravity/scratch/livestock-health-monitoring-assistant
```

### Step 2: Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: Livestock Health Monitoring Assistant with Multi-Agent System"
```

> **Security Note:** Your secret `.env` file is already listed in `.gitignore`, so your API key will **NEVER** be committed or uploaded to GitHub.

### Step 3: Create a New GitHub Repository
1. Go to [https://github.com/new](https://github.com/new).
2. Set the repository name (e.g. `livestock-health-monitoring-assistant`).
3. Set visibility to **Public** or **Private** (both work fine).
4. Do **NOT** initialize with a README (we already have one).
5. Click **Create repository**.

### Step 4: Link Local Repo and Push
Copy the commands shown on GitHub, which look like:
```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/livestock-health-monitoring-assistant.git
git push -u origin main
```

---

## ☁️ Part 2: Deploy on Render (Free)

### Step 1: Create a Render Account
1. Go to [https://render.com](https://render.com) and sign up / log in with your GitHub account.

### Step 2: Create a New Web Service
1. In your Render Dashboard, click **New +** > **Web Service**.
2. Select **"Build and deploy from a Git repository"**.
3. Choose your `livestock-health-monitoring-assistant` repository from the list and click **Connect**.

### Step 3: Configure Settings
Fill in these standard settings:
- **Name:** `livestock-health-assistant` (or any name you like)
- **Language / Runtime:** `Python 3`
- **Branch:** `main`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`
- **Instance Type:** `Free`

### Step 4: Add Environment Variable (Your API Key)
Scroll down to the **Environment Variables** section:
1. Click **Add Environment Variable**.
2. **Key:** `OPENAI_API_KEY`
3. **Value:** Paste your OpenAI API key (`sk-proj-...`).

### Step 5: Deploy
1. Click **Create Web Service**.
2. Render will automatically build and launch the app in 2–3 minutes.
3. Once finished, you will receive a public live URL (e.g. `https://livestock-health-assistant.onrender.com`).

---

## 🔄 Updating Your Live App Later
Whenever you make changes to your local code, simply run:
```bash
git add .
git commit -m "Update application"
git push
```
Render will automatically detect the changes on GitHub and redeploy your live web application!
