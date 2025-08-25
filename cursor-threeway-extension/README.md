# ThreeWay Chat - Cursor Extension

This extension connects your Cursor windows to your ThreeWay Chat voice conversation system.

## Features

- 🎤 **Voice Control**: Talk to Grok AI about your current code
- 👀 **Context Awareness**: Extension reads your active Cursor window
- 🔄 **Model Selection**: Choose between different Grok models (Mini, Standard, Beta, Vision)
- 📝 **Real-time Updates**: Automatically shares context when you switch files
- 💬 **Smart Responses**: Grok can see your actual code and provide specific help

## Installation

### Option 1: Local Development Install

1. **Copy Extension Folder**:
   ```bash
   cp -r /Volumes/LaCie/ThreeWayChat/cursor-threeway-extension ~/.cursor/extensions/threeway-chat-cursor
   ```

2. **Install Dependencies**:
   ```bash
   cd ~/.cursor/extensions/threeway-chat-cursor
   npm install
   ```

3. **Restart Cursor**

4. **Activate Extension**:
   - Open Command Palette (`Cmd+Shift+P`)
   - Type "ThreeWay Chat: Connect"
   - Click to connect

### Option 2: VSCode/Cursor Extension Development

1. **Open in Cursor**:
   ```bash
   cursor /Volumes/LaCie/ThreeWayChat/cursor-threeway-extension
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Test Extension**:
   - Press `F5` to open Extension Development Host
   - The extension will load in the new window

## Usage

### Connecting
1. Look for "ThreeWay: Disconnected" in the status bar (bottom right)
2. Click it to connect to your voice chat server
3. Status will change to "ThreeWay: Connected (model-name)"

### Model Selection
1. Open Command Palette (`Cmd+Shift+P`)
2. Type "ThreeWay Chat: Select Grok Model"
3. Choose from available models:
   - **Grok 2 Mini**: Fast, efficient, cheapest
   - **Grok 2**: Balanced performance and cost
   - **Grok 2 (Dec 2024)**: Latest stable version
   - **Grok Beta**: Experimental features
   - **Grok Vision Beta**: With image understanding

### Voice Conversation
1. **Connect** the extension
2. **Open your iOS ThreeWay Chat app**
3. **Start talking**: "Hey Grok, can you help me debug this function?"
4. **Grok can now see** your current file and provide specific help!

## How It Works

1. **Context Sharing**: Extension automatically shares your current file, line number, and selected code
2. **Voice Query**: You ask Grok a question via voice
3. **Smart Response**: Grok sees your actual code and provides specific advice
4. **Real-time Updates**: As you switch files, Grok stays aware of your context

## Example Conversations

**You**: "This function is returning undefined, can you help?"

**Grok** (can now see your code): "Looking at your `calculateTotal.js` file, I can see on line 15 you're missing a return statement in your if block. Here's the fix..."

**You**: "Explain what this code does"

**Grok**: "This React component in `UserProfile.tsx` appears to be handling user authentication. I can see you're using hooks for state management..."

## Troubleshooting

### Extension Not Connecting
- Check that your ThreeWay Chat server is running
- Verify the server URL in extension settings
- Look for errors in Cursor's Developer Console

### No Context Being Shared
- Make sure you have a file open in Cursor
- Check that the extension status shows "Connected"
- Try switching between files to trigger context update

### Voice App Not Receiving Responses
- Ensure both iOS app and Cursor extension are connected
- Check server health at: https://voice-chat-app-cc40.onrender.com/health
- Verify API key is set in Render environment

## Status Bar Indicators

- `$(radio-tower) ThreeWay: Disconnected` - Click to connect
- `$(sync~spin) ThreeWay: Connecting...` - Connection in progress  
- `$(radio-tower) ThreeWay: Connected (grok-2-mini)` - Connected and ready
- `$(radio-tower) ThreeWay: Connection Failed` - Check server status

## Commands

- `ThreeWay Chat: Connect` - Connect to voice chat server
- `ThreeWay Chat: Disconnect` - Disconnect from server
- `ThreeWay Chat: Select Grok Model` - Choose AI model

This extension makes your voice conversation with Grok AI truly context-aware of your actual code!
