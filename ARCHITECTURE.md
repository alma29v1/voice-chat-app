# 🏗️ ThreeWayChat Technical Architecture

## 📋 **System Overview**

ThreeWayChat implements a sophisticated voice-controlled AI system with three main components working in harmony:

1. **iOS Voice Interface** - Natural language input/output
2. **Cloud Server** - WebSocket orchestration and AI routing  
3. **AI Integration Layer** - Multi-model AI coordination

## 🔧 **Component Architecture**

### **1. iOS Frontend (`ContentView.swift`)**

#### **Speech Recognition Pipeline**
```swift
SFSpeechRecognizer → AVAudioEngine → Voice Activity Detection → WebSocket
```

#### **Key Classes & Methods**
- `startContinuousListening()` - Maintains always-on voice detection
- `resetSilenceTimer()` - 5-second timeout for natural speech
- `shouldStartRecording()` - Smart trigger for voice capture
- `speakGrokResponse()` - Text-to-speech with anti-feedback

#### **Voice Activity Detection (VAD)**
```swift
// Custom VAD with amplitude analysis
private func detectVoiceActivity(in buffer: AVAudioPCMBuffer) {
    let averageAmplitude = calculateAmplitude(buffer)
    if averageAmplitude > voiceThreshold {
        lastSpeechTime = Date()
    }
}
```

#### **Anti-Feedback System**
- Stops listening during TTS output
- 2-second delay before restart after AI speech
- "Headset Mode" toggle for self-listening prevention

### **2. Cloud Server (`cloud_server.py`)**

#### **FastAPI WebSocket Architecture**
```python
/ws/phone   → iOS app connection
/ws/cursor  → Cursor AI integration
/api/health → Health monitoring
```

#### **Connection Manager**
```python
class ConnectionManager:
    - phone_connection: WebSocket
    - cursor_connection: WebSocket  
    - knowledge_base: List[Message]
    - conversation_context: Dict
    - extended_memory: Dict
```

#### **Smart Context System**
```python
def get_smart_context_for_grok(self) -> str:
    """Generates comprehensive context for Grok with:
    - Complete project ecosystem knowledge
    - Extended memory (errors, solutions, interactions)
    - Conversation type awareness
    - Token-efficient context building
    """
```

#### **Extended Memory Implementation**
```python
extended_memory = {
    "project_states": {
        "threeway_chat": {...},
        "big_beautiful": {...}, 
        "companion_app": {...}
    },
    "conversation_history": [...],
    "technical_context": {
        "recent_errors": [...],
        "solved_problems": [...],
        "active_debugging": None
    }
}
```

### **3. Cursor Integration (`real_cursor_integration.js`)**

#### **Multi-Project Management**
```javascript
projects = {
    'threeway-chat': { name, path, description },
    'big-beautiful': { name, path, apiUrl, description },
    'companion-app': { name, path, apiUrl, endpoints }
}
```

#### **Voice Command Processing**
```javascript
handleIncomingMessage(data) {
    // Project switching: "Switch to [project]"
    // API commands: "Get contacts", "Check health" 
    // Programming help: Auto-detect technical questions
}
```

#### **API Integration Example**
```javascript
async callCompanionAPI(endpoint, parameters) {
    // Smart endpoint routing
    // Authentication handling
    // Formatted response processing
}
```

## 🔄 **Data Flow Architecture**

### **Voice Input Flow**
```
1. User speaks → iOS captures audio
2. SFSpeechRecognizer → transcribes text
3. WebSocket → sends to cloud server
4. Smart routing → determines AI target (Grok/Cursor)
5. Context building → adds conversation history
6. AI processing → generates response
7. WebSocket → returns to iOS
8. AVSpeechSynthesizer → speaks response
```

### **Project Switching Flow**
```
1. Voice: "Switch to Companion App"
2. Cursor integration detects command
3. Updates current project context
4. Sends confirmation to server
5. Server updates conversation context
6. Response sent to iOS with new project info
```

### **API Execution Flow**
```
1. Voice: "Get contacts"
2. Cursor integration parses command
3. Identifies target API endpoint
4. Makes authenticated HTTP request
5. Formats response data
6. Sends formatted result to iOS
7. iOS speaks the results
```

## 🧠 **AI Integration Architecture**

### **Grok Integration**
```python
# Smart context-aware API calls
async def call_grok_api(message: str, context: str) -> str:
    history_messages = [
        {"role": "system", "content": context},
        *[conversation_history],
        {"role": "user", "content": message}
    ]
    
    response = await client.post(
        "https://api.x.ai/v1/chat/completions",
        json={
            "model": "grok-4",
            "messages": history_messages,
            "max_tokens": 1000
        }
    )
```

### **Cursor Integration Pattern**
```javascript
// Real-time WebSocket client simulation
class RealCursorIntegration {
    - Connects to cloud server WebSocket
    - Monitors for programming questions
    - Provides contextual development assistance
    - Handles project switching commands
    - Executes API calls on behalf of user
}
```

## 🔐 **Security & Authentication**

### **API Key Management**
```python
# Environment-based configuration
GROK_API_KEY = os.getenv("GROK_API_KEY")
X_API_KEY = "xai-wQ6qJGFoJT8GSwJ7Uht3vYzVzDWNw1i7EewqHkVNRpJcgNkcGDZYQa8w9OjhMPJMaZZEg9Cqm4IqF3mJQ"
```

### **WebSocket Security**
- WSS encryption for production
- Connection validation and cleanup
- Rate limiting on message processing
- Graceful error handling and recovery

## 📊 **Performance Optimizations**

### **Speech Recognition**
- Continuous listening with smart triggers
- 5-second silence timeout (optimized for natural speech)
- Buffer size optimization (1024 samples)
- Audio session configuration for background operation

### **Context Management**
- Token-efficient context building
- Sliding window for conversation history (50 messages)
- Smart keyword extraction and topic tracking
- Extended memory with automatic cleanup

### **WebSocket Optimization**
- Automatic reconnection on disconnects
- Message queuing during reconnection
- Heartbeat monitoring for connection health
- Background operation support

## 🚀 **Scalability Considerations**

### **Current Architecture Limits**
- Single server instance (Render deployment)
- In-memory conversation storage
- Direct WebSocket connections only

### **Commercial Scaling Path**
- Horizontal server scaling with load balancing
- Database persistence for conversation history
- Redis for real-time message brokering
- CDN for WebSocket connection distribution

## 🔮 **Extension Points**

### **AI Model Integration**
```python
# Pluggable AI provider system
class AIProvider:
    async def generate_response(context, message) -> str
    
class GrokProvider(AIProvider): ...
class OpenAIProvider(AIProvider): ...
class ClaudeProvider(AIProvider): ...
```

### **Project Plugin System**
```javascript
// Extensible project definitions
const projectPlugins = {
    'custom-project': {
        detector: (message) => boolean,
        handler: (command) => Promise<result>,
        apiIntegration: CustomAPIClient
    }
}
```

### **Voice Processing Pipeline**
```swift
// Modular voice processing
protocol VoiceProcessor {
    func processAudio(buffer: AVAudioPCMBuffer) -> ProcessingResult
}

class NoiseReductionProcessor: VoiceProcessor { ... }
class SpeechEnhancementProcessor: VoiceProcessor { ... }
class CustomVADProcessor: VoiceProcessor { ... }
```

## 🎯 **Commercial Architecture Recommendations**

### **Microservices Breakdown**
1. **Voice Service** - Speech processing and WebSocket management
2. **AI Orchestration Service** - Multi-AI routing and context management  
3. **Project Management Service** - Workspace and API integrations
4. **User Management Service** - Authentication and preferences
5. **Analytics Service** - Usage tracking and insights

### **Data Architecture**
- **PostgreSQL** - User data, conversation history, project configs
- **Redis** - Real-time session state, WebSocket connections
- **S3** - Voice recordings, model training data
- **ElasticSearch** - Conversation search and analytics

### **Infrastructure**
- **Kubernetes** - Container orchestration and scaling
- **NGINX** - Load balancing and WebSocket proxy
- **CloudFlare** - CDN and DDoS protection
- **Monitoring** - Prometheus, Grafana, Sentry

---

This architecture demonstrates a production-ready foundation for voice-controlled AI systems with proven scalability patterns and commercial viability.
