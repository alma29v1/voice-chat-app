# ThreeWayChat Setup Guide

## Setting Up Grok API Key

### Option 1: Using config.py (Recommended for Private Replit)

1. **Get your Grok API Key**:
   - Go to https://console.x.ai/
   - Sign up or log in
   - Create a new API key

2. **Edit the config.py file**:
   - Open `config.py` in your Replit project
   - Replace the empty string with your API key:
   ```python
   GROK_API_KEY = "your-actual-api-key-here"
   ```

3. **Restart the server**:
   - The server will automatically use your API key

### Option 2: Using Replit Secrets (For Public Replit)

1. **Make your Replit project public**:
   - Go to your Replit project settings
   - Change visibility to "Public"

2. **Add the secret**:
   - Go to "Tools" → "Secrets"
   - Add: `GROK_API_KEY` = `your-api-key-here`

### Testing the Setup

1. **Start the server** (if not already running)
2. **Open your iOS app**
3. **Try talking to it** - you should get intelligent responses from Grok AI

### Troubleshooting

- **"API key not configured"**: Make sure you've added your API key to `config.py`
- **"Connection failed"**: Check that the cloud server is running
- **"No response"**: The server might be restarting, wait a moment and try again

## Current Status

- ✅ Cloud server is running
- ✅ iOS app is connected
- ✅ Voice recording works
- ✅ Message flow works
- ⚠️ Need to add Grok API key for full functionality
