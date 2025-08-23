# ThreeWayChat Setup Guide

## Setting Up Grok API Key

### Using Replit Secrets (Recommended)

1. **Get your Grok API Key**:
   - Go to https://console.x.ai/
   - Sign up or log in
   - Create a new API key

2. **Add the secret to Replit**:
   - In your Replit project, go to "Tools" → "Secrets"
   - Click "New Secret"
   - Key: `GROK_API_KEY`
   - Value: `your-actual-api-key-here`

3. **Restart the server**:
   - The server will automatically use your API key from secrets

### Important Security Notes

- ✅ **API key is stored securely** in Replit secrets
- ✅ **No sensitive data in code** - safe for GitHub
- ✅ **Works with private Replit** - no need to make public
- ✅ **Automatically protected** by .gitignore

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
