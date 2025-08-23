# ThreeWayChat System

A real-time three-way conversation system connecting Phone (iOS), Cursor AI, and Grok AI with automatic programming question routing.

## 🚀 Features

- **Real-time WebSocket communication** between phone and computer
- **Automatic Grok AI integration** for programming questions
- **Beautiful iOS SwiftUI interface** with modern design
- **Knowledge base** for conversation history
- **Network hotspot support** for mobile connectivity
- **Auto IP detection** and configuration

## 📁 Project Structure

```
/Volumes/LaCie/ThreeWayChat/
├── backend/
│   └── server.py          # FastAPI WebSocket server
├── ThreeWayChat/          # iOS app files
│   ├── ThreeWayChatApp.swift
│   ├── ContentView.swift
│   └── ChatManager.swift
├── requirements.txt       # Python dependencies
└── README.md
```

## 🛠️ Setup Instructions

### 1. Backend Server Setup

1. **Navigate to project directory:**
   ```bash
   cd /Volumes/LaCie/ThreeWayChat
   ```

2. **Create Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server:**
   ```bash
   cd backend
   python server.py
   ```

The server will display connection information including the IP address for the iOS app.

### 2. iOS App Setup

1. **Open Xcode** and create a new iOS project
2. **Replace the default files** with the provided Swift files:
   - `ThreeWayChatApp.swift`
   - `ContentView.swift` 
   - `ChatManager.swift`

3. **Configure the app** to connect to your server IP address
4. **Build and run** on your iOS device

## 🔧 Configuration

### Server IP Configuration

The iOS app needs to know your computer's IP address. The server will display this when started:

```
🚀 ThreeWayChat Server starting...
📱 Phone should connect to: ws://192.168.1.100:8000/ws/phone
💻 Cursor should connect to: ws://192.168.1.100:8000/ws/cursor
🌐 Server IP: 192.168.1.100
🔗 API endpoint: http://192.168.1.100:8000
```

### iOS App Configuration

1. **Open the app** and tap the network icon in the header
2. **Enter your computer's IP address** (e.g., `192.168.1.100`)
3. **Tap Save** to update the connection
4. **Tap Connect** in Settings to establish connection

## 🌐 Network Requirements

### For Hotspot Connection

1. **Enable hotspot** on your computer
2. **Connect your phone** to the computer's hotspot
3. **Use the computer's IP address** in the iOS app
4. **Ensure port 8000** is accessible

### For Local Network

1. **Connect both devices** to the same WiFi network
2. **Use the computer's local IP** (usually `192.168.1.x` or `192.168.0.x`)
3. **Check firewall settings** to allow port 8000

## 🤖 Grok AI Integration

The system automatically detects programming questions and routes them to Grok AI:

### Programming Keywords Detected:
- code, program, function, class, bug, error, debug
- python, javascript, swift, java, c++, sql, api
- algorithm, data structure, framework, library, git
- deploy, server, database, frontend, backend, fullstack

### API Configuration:
- **API Key**: Configured in `server.py`
- **Model**: `grok-4-latest`
- **Endpoint**: `https://api.x.ai/v1/chat/completions`

## 📱 iOS App Features

### Main Interface
- **Real-time chat** with message bubbles
- **Connection status** indicator
- **Server IP configuration**
- **Settings panel** for connection management

### Message Types
- **Phone messages**: Blue bubbles (right-aligned)
- **Cursor messages**: Green bubbles (left-aligned)  
- **Grok AI responses**: Purple bubbles (left-aligned)

### Settings
- **Connection status** monitoring
- **Server IP** configuration
- **Message history** management
- **Quick IP presets** for common configurations

## 🔌 WebSocket Endpoints

### Phone Connection
```
ws://[SERVER_IP]:8000/ws/phone
```

### Cursor Connection  
```
ws://[SERVER_IP]:8000/ws/cursor
```

### HTTP Endpoints
- `GET /` - Server status
- `GET /ip` - Server IP information
- `GET /history` - Conversation history

## 📊 Message Format

### Outgoing Messages
```json
{
  "type": "message",
  "sender": "phone",
  "content": "Hello, world!",
  "message_type": "text",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Incoming Messages
```json
{
  "type": "message",
  "sender": "grok",
  "content": "Hello! I'm here to help with programming questions.",
  "message_type": "text", 
  "timestamp": "2024-01-01T12:00:01Z"
}
```

## 🚨 Troubleshooting

### Connection Issues
1. **Check IP address** - Ensure you're using the correct computer IP
2. **Verify network** - Both devices must be on same network
3. **Check firewall** - Port 8000 must be open
4. **Restart server** - Stop and restart the Python server

### Grok API Issues
1. **Check API key** - Verify the key is valid and active
2. **Network connectivity** - Ensure server can reach api.x.ai
3. **Rate limits** - Check if API quota is exceeded

### iOS App Issues
1. **Reconnect** - Disconnect and reconnect in Settings
2. **Clear messages** - Use Settings to clear message history
3. **Update IP** - Reconfigure server IP if network changes

## 🔒 Security Notes

- **API Key**: The Grok API key is embedded in the server code
- **Network**: Messages are sent over WebSocket (not encrypted by default)
- **Local Network**: System designed for local network use
- **Firewall**: Ensure proper firewall configuration for production use

## 📈 Future Enhancements

- **Message encryption** for secure communication
- **File sharing** capabilities
- **Voice messages** support
- **Push notifications** for iOS
- **User authentication** system
- **Persistent storage** for conversation history
- **Multi-room** chat support

## 🤝 Contributing

This is a personal project for three-way communication between phone, Cursor AI, and Grok AI. Feel free to fork and modify for your own needs.

## 📄 License

This project is for personal use. The Grok API integration requires a valid X API key.
