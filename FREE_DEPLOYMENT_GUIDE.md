# 🆓 Free ThreeWayChat Deployment Guide

## 🎯 Completely Free Options (No Credit Card Required)

### **Option 1: Replit (100% Free - Recommended)**

**Step 1: Create Replit Account**
1. Go to [replit.com](https://replit.com)
2. Sign up with GitHub (free)
3. Click "Create Repl"

**Step 2: Import Your Code**
1. Choose "Import from GitHub"
2. Enter your ThreeWayChat repository URL
3. Select "Python" as language

**Step 3: Configure Environment**
1. In the Repl, go to "Tools" → "Secrets"
2. Add secret: `GROK_API_KEY` = your Grok API key
3. Click "Run" to start the server

**Step 4: Get Your URL**
- Your app will be available at: `https://your-repl-name.your-username.repl.co`
- WebSocket URLs:
  - Phone: `wss://your-repl-name.your-username.repl.co/ws/phone`
  - Cursor: `wss://your-repl-name.your-username.repl.co/ws/cursor`

**✅ Benefits:**
- 100% free forever
- No credit card required
- Automatic HTTPS
- Always online
- Easy to use

---

### **Option 2: Render (Free Tier)**

**Step 1: Create Account**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (free)
3. No credit card required for free tier

**Step 2: Deploy**
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** threewaychat
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn cloud_server:app --host 0.0.0.0 --port $PORT`
4. Add environment variable: `GROK_API_KEY`
5. Click "Create Web Service"

**✅ Benefits:**
- 750 free hours/month (enough for 24/7)
- Automatic deployments
- Custom domains
- No credit card required

---

### **Option 3: Railway (Free Credit)**

**Step 1: Create Account**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Get $5 free credit monthly

**Step 2: Deploy**
1. Click "New Project" → "Deploy from GitHub repo"
2. Select your repository
3. Add environment variable: `GROK_API_KEY`
4. Deploy!

**✅ Benefits:**
- $5 free credit monthly (enough for small apps)
- Very easy deployment
- Great performance

---

### **Option 4: Fly.io (Free Tier)**

**Step 1: Install Fly CLI**
```bash
curl -L https://fly.io/install.sh | sh
```

**Step 2: Deploy**
```bash
fly auth signup
fly launch
fly secrets set GROK_API_KEY=your_key
fly deploy
```

**✅ Benefits:**
- 3 free VMs
- Global deployment
- No credit card required

---

## 🔧 Update Your Apps After Deployment

### **📱 Voice Control App**
Update `ContentView.swift`:
```swift
@State private var serverIP = "your-app-name.your-username.repl.co" // For Replit
// OR
@State private var serverIP = "your-app.onrender.com" // For Render
```

### **💻 Cursor Extension**
Update `cursor_extension.js`:
```javascript
this.serverIP = "your-app-name.your-username.repl.co"; // For Replit
// OR
this.serverIP = "your-app.onrender.com"; // For Render
```

---

## 🎯 **Recommended: Replit (100% Free)**

**Why Replit is best:**
- ✅ **Completely free forever**
- ✅ **No credit card required**
- ✅ **Automatic HTTPS/WSS**
- ✅ **Always online**
- ✅ **Easy to use**
- ✅ **Instant deployment**

**Quick Replit Setup:**
1. Go to [replit.com](https://replit.com)
2. Sign up with GitHub
3. Create new Repl → Import from GitHub
4. Add your Grok API key as a secret
5. Click Run
6. Copy the URL and update your apps

---

## 🆘 Troubleshooting

**Connection Issues:**
- Make sure you're using `wss://` (secure WebSocket)
- Check that your domain supports WebSockets
- Verify your Grok API key is correct

**Deployment Issues:**
- Check the logs in your cloud platform
- Make sure all files are committed to GitHub
- Verify environment variables are set correctly

---

## 💡 Pro Tips

1. **Use Replit** for the easiest free deployment
2. **Keep your API keys secure** using environment variables
3. **Test your deployment** by visiting the URL in a browser
4. **Monitor your usage** to stay within free limits
5. **Backup your configuration** after successful deployment

**🎉 You can have a professional three-way chat system completely free!**
