# 🌐 ThreeWayChat Cloud Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Free & Easy)
1. **Go to [Railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select your ThreeWayChat repository**
5. **Add environment variable:**
   - `GROK_API_KEY` = your Grok API key
6. **Deploy!** Railway will give you a URL like `https://your-app.railway.app`

### Option 2: Render (Free Tier Available)
1. **Go to [Render.com](https://render.com)**
2. **Sign up and create new Web Service**
3. **Connect your GitHub repository**
4. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn cloud_server:app --host 0.0.0.0 --port $PORT`
5. **Add environment variable:**
   - `GROK_API_KEY` = your Grok API key
6. **Deploy!**

### Option 3: Heroku (Paid)
1. **Install Heroku CLI**
2. **Run commands:**
   ```bash
   heroku create your-threewaychat-app
   heroku config:set GROK_API_KEY=your_grok_api_key
   git push heroku main
   ```

### Option 4: Your Own Website/Domain
1. **Upload `cloud_server.py` to your web server**
2. **Install Python dependencies**
3. **Set up environment variable:**
   ```bash
   export GROK_API_KEY=your_grok_api_key
   ```
4. **Run the server:**
   ```bash
   python3 cloud_server.py
   ```

## 🔧 Configuration

### Environment Variables
- `GROK_API_KEY`: Your XAI Grok API key
- `PORT`: Port number (usually set automatically by cloud platform)

### Update Your Apps

#### 📱 Voice Control App
Update the server URL in `ContentView.swift`:
```swift
@State private var serverIP = "your-deployed-domain.com" // No http:// or ws://
```

#### 💻 Cursor Extension
Update the server URL in `cursor_extension.js`:
```javascript
this.serverIP = "your-deployed-domain.com"; // No http:// or ws://
```

## 🌍 WebSocket URLs
After deployment, your WebSocket URLs will be:
- **Phone:** `wss://your-domain.com/ws/phone`
- **Cursor:** `wss://your-domain.com/ws/cursor`

## ✅ Testing Your Deployment
1. **Visit your domain** (e.g., `https://your-app.railway.app`)
2. **You should see:** `{"message": "ThreeWayChat Cloud Server", "status": "running"}`
3. **Test health endpoint:** `https://your-domain.com/health`

## 🔒 Security Notes
- **HTTPS/WSS required** for production
- **CORS enabled** for cross-origin requests
- **Environment variables** keep your API key secure

## 🆘 Troubleshooting
- **Connection failed:** Check if your domain supports WebSockets
- **API errors:** Verify your Grok API key is correct
- **Deployment fails:** Check the logs in your cloud platform dashboard

## 📞 Support
- **Railway:** Excellent free tier, great for testing
- **Render:** Good free tier, reliable
- **Heroku:** More expensive but very reliable
- **Your domain:** Full control but requires server management
