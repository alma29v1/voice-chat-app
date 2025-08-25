#!/usr/bin/env python3
"""
Cloud-Based ThreeWayChat Server
Deploy this to your website or cloud service (Heroku, Railway, Render, etc.)
"""

import asyncio
import json
import logging
import os
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Grok AI Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY", "")  # Set via Render environment
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Available Grok models with pricing info (updated with Grok 4)
GROK_MODELS = {
    "grok-2-mini": {"name": "Grok 2 Mini", "cost": "Cheapest", "speed": "Fastest"},
    "grok-2": {"name": "Grok 2", "cost": "Medium", "speed": "Fast"},  
    "grok-2-1212": {"name": "Grok 2 (Dec 2024)", "cost": "Medium", "speed": "Fast"},
    "grok-beta": {"name": "Grok Beta", "cost": "Higher", "speed": "Medium"},
    "grok-vision-beta": {"name": "Grok Vision", "cost": "Highest", "speed": "Slower"},
    "grok-4": {"name": "Grok 4", "cost": "Premium", "speed": "Advanced"},
    "grok-4-heavy": {"name": "Grok 4 Heavy (Multi-Agent)", "cost": "Enterprise", "speed": "Advanced+"}
}

# Current model (can be changed via API)  
CURRENT_GROK_MODEL = "grok-4"  # Upgraded to Grok 4 for better performance

# Debug: Log API key status (without revealing the key)
if GROK_API_KEY:
    logger.info(f"✅ GROK_API_KEY loaded successfully (length: {len(GROK_API_KEY)})")
    logger.info(f"🤖 Using Grok model: {CURRENT_GROK_MODEL}")
else:
    logger.error("❌ GROK_API_KEY not found in environment variables")


class Message(BaseModel):
    sender: str
    content: str
    message_type: str = "text"
    timestamp: Optional[str] = None


class ConnectionManager:
    def __init__(self):
        self.phone_connection: Optional[WebSocket] = None
        self.cursor_connection: Optional[WebSocket] = None
        self.knowledge_base: List[Message] = []
        self.conversation_context = {
            "topic": None,
            "cursor_last_response": None,
            "user_question": None,
            "key_points": [],
            "conversation_type": "general"  # general, debugging, coding, explanation
        }
        
        # Extended memory for comprehensive project knowledge
        self.extended_memory = {
            "project_states": {
                "threeway_chat": {
                    "current_issues": [],
                    "recent_changes": [],
                    "active_features": ["voice_control", "websocket_communication", "grok_integration"]
                },
                "big_beautiful": {
                    "api_status": "configured",
                    "available_functions": [],
                    "last_interaction": None
                },
                "companion_app": {
                    "api_status": "ready",
                    "endpoints_used": [],
                    "last_data_sync": None
                }
            },
            "conversation_history": [],  # Long-term conversation memory
            "technical_context": {
                "recent_errors": [],
                "solved_problems": [],
                "active_debugging": None
            }
        }

    async def connect_phone(self, websocket: WebSocket):
        await websocket.accept()
        self.phone_connection = websocket
        logger.info("📱 Phone connected")

        # Send connection confirmation
        await self.send_to_phone({
            "type": "system",
            "content": "Connected to ThreeWayChat cloud server",
            "timestamp": self.get_timestamp()
        })

    async def connect_cursor(self, websocket: WebSocket):
        await websocket.accept()
        self.cursor_connection = websocket
        logger.info("💻 Cursor connected")

        # Send connection confirmation
        await self.send_to_cursor({
            "type": "system",
            "content": "Connected to ThreeWayChat cloud server",
            "timestamp": self.get_timestamp()
        })

    async def disconnect_phone(self):
        self.phone_connection = None
        logger.info("📱 Phone disconnected")

    async def disconnect_cursor(self):
        self.cursor_connection = None
        logger.info("💻 Cursor disconnected")

    async def send_to_phone(self, message: dict):
        if self.phone_connection:
            try:
                await self.phone_connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to phone: {e}")
                await self.disconnect_phone()

    async def send_to_cursor(self, message: dict):
        if self.cursor_connection:
            try:
                await self.cursor_connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to cursor: {e}")
                await self.disconnect_cursor()

    async def broadcast(self, message: dict, exclude_sender: str = None):
        """Broadcast message to all connected clients"""
        if exclude_sender != "phone" and self.phone_connection:
            await self.send_to_phone(message)
        if exclude_sender != "cursor" and self.cursor_connection:
            await self.send_to_cursor(message)

    def get_timestamp(self):
        return datetime.now().isoformat()

    def add_to_knowledge_base(self, message: Message):
        """Store message in knowledge base and update context"""
        self.knowledge_base.append(message)
        self.update_conversation_context(message)
        self.update_extended_memory(message)  # Enhanced memory tracking
        logger.info(
            f"Added to knowledge base: {message.sender}: {message.content[:50]}...")
    
    def update_conversation_context(self, message: Message):
        """Smart context management to reduce token usage"""
        content_lower = message.content.lower()
        
        # Update conversation type
        if any(word in content_lower for word in ['debug', 'error', 'undefined', 'bug', 'fix']):
            self.conversation_context["conversation_type"] = "debugging"
        elif any(word in content_lower for word in ['code', 'function', 'javascript', 'python', 'programming']):
            self.conversation_context["conversation_type"] = "coding"
        elif any(word in content_lower for word in ['how', 'what', 'why', 'explain']):
            self.conversation_context["conversation_type"] = "explanation"
        
        # Track user questions
        if message.sender == "phone" and any(char in message.content for char in ['?', 'help', 'can you']):
            self.conversation_context["user_question"] = message.content[:100]
        
        # Track cursor responses
        if message.sender == "cursor":
            self.conversation_context["cursor_last_response"] = message.content[:200]
        
        # Extract key points (simple keyword extraction)
        keywords = []
        for word in message.content.split():
            if len(word) > 4 and word.lower() not in ['this', 'that', 'with', 'have', 'will', 'from', 'they']:
                keywords.append(word.lower())
        
        # Keep only recent key points to limit memory
        self.conversation_context["key_points"].extend(keywords[:3])
        self.conversation_context["key_points"] = self.conversation_context["key_points"][-10:]  # Last 10 keywords
    
    def get_smart_context_for_grok(self) -> str:
        """Generate comprehensive context for Grok with full project knowledge"""
        ctx = self.conversation_context
        
        context_parts = [
            "You are Grok in a three-way conversation with a user (phone) and Cursor AI (coding assistant).",
            "\n=== COMPLETE PROJECT ECOSYSTEM ===",
            
            "🎯 **ThreeWayChat App** (Current App):",
            "- Voice-controlled iOS app with Swift/SwiftUI",
            "- Real-time WebSocket communication via FastAPI server on Render",
            "- Speech-to-text (SFSpeechRecognizer) and text-to-speech (AVSpeechSynthesizer)",
            "- Voice Activity Detection (VAD) with automatic restart after responses",
            "- Anti-feedback loop protection (headset mode)",
            "- Smart context system for efficient conversation history",
            "- Project switching capabilities between multiple programs",
            "- Files: ContentView.swift, cloud_server.py, real_cursor_integration.js",
            "- Server: voice-chat-app-cc40.onrender.com (FastAPI + WebSockets)",
            
            "🏢 **Big Beautiful Program** (Main Application):",
            "- Primary business application with its own API server",
            "- Has dedicated API endpoints and authentication system",
            "- Integrated via voice commands through ThreeWayChat",
            "- Can execute functions remotely via API calls",
            "- Currently configurable in cursor integration",
            
            "📱 **Companion App** (Business Tool):",
            "- Business management application on localhost:5001",
            "- API Key: X authentication (xai-wQ6qJGFoJT8GSwJ7Uht3vYzVzDWNw1i7EewqHkVNRpJcgNkcGDZYQa8w9OjhMPJMaZZEg9Cqm4IqF3mJQ)",
            "- Endpoints: /api/health, /api/contacts, /api/analytics",
            "- Sales tracking: /api/rolling-sales, /api/rolling-sales/export",
            "- Location services: /api/geocode, /api/att-fiber-check",
            "- Data management: /api/sync, POST /api/contacts",
            "- Full voice control via 'Switch to Companion App' command",
            
            "🔧 **Technical Architecture**:",
            "- Cursor AI Integration: real_cursor_integration.js (Node.js WebSocket client)",
            "- AI Models: Grok-4 (1000 tokens), Cursor AI (programming help)",
            "- Voice Flow: Phone → Server → Grok/Cursor → Phone",
            "- Project Management: Voice switching between all three programs",
            "- API Integration: RESTful calls with formatted responses",
            "- Smart Context: Conversation-aware, token-efficient system"
        ]
        
        # Add conversation type context
        if ctx["conversation_type"] == "debugging":
            context_parts.append("\n🐛 **Current Session**: Debugging - Help solve code issues across any project.")
        elif ctx["conversation_type"] == "coding":
            context_parts.append("\n💻 **Current Session**: Coding - Provide programming guidance for any project.")
        elif ctx["conversation_type"] == "explanation":
            context_parts.append("\n📚 **Current Session**: Explanation - Help clarify concepts across the ecosystem.")
        
        # Add user's current question if available
        if ctx["user_question"]:
            context_parts.append(f"\n❓ **User Question**: {ctx['user_question']}")
        
        # Add what Cursor already said to avoid repetition
        if ctx["cursor_last_response"]:
            context_parts.append(f"\n🤖 **Cursor Response**: {ctx['cursor_last_response'][:300]}...")
            context_parts.append("Build on or complement Cursor's response, don't repeat it.")
        
        # Add key topics
        if ctx["key_points"]:
            recent_topics = list(set(ctx["key_points"][-5:]))  # Last 5 unique keywords
            context_parts.append(f"\n🔑 **Key Points**: {', '.join(recent_topics)}")
        
        context_parts.append("\n\n🎯 **Your Role**: Provide contextual help understanding the full ecosystem. Reference specific projects, APIs, and technical details when relevant.")
        
        # Add extended memory context
        if self.extended_memory["technical_context"]["active_debugging"]:
            context_parts.append(f"\n🔧 **Active Debug**: {self.extended_memory['technical_context']['active_debugging']}")
        
        if self.extended_memory["technical_context"]["recent_errors"]:
            recent_errors = self.extended_memory["technical_context"]["recent_errors"][-2:]  # Last 2 errors
            context_parts.append(f"\n⚠️ **Recent Issues**: {'; '.join(recent_errors)}")
        
        if self.extended_memory["technical_context"]["solved_problems"]:
            solved = self.extended_memory["technical_context"]["solved_problems"][-2:]  # Last 2 solutions
            context_parts.append(f"\n✅ **Recently Solved**: {'; '.join(solved)}")
        
        return " ".join(context_parts)
    
    def update_extended_memory(self, message: Message):
        """Update extended memory with conversation insights"""
        content_lower = message.content.lower()
        
        # Track errors and problems
        if any(word in content_lower for word in ['error', 'bug', 'issue', 'problem', 'broken']):
            error_summary = message.content[:100] + "..." if len(message.content) > 100 else message.content
            self.extended_memory["technical_context"]["recent_errors"].append(error_summary)
            self.extended_memory["technical_context"]["recent_errors"] = self.extended_memory["technical_context"]["recent_errors"][-5:]  # Keep last 5
            
            # Set active debugging if not already set
            if not self.extended_memory["technical_context"]["active_debugging"]:
                self.extended_memory["technical_context"]["active_debugging"] = error_summary
        
        # Track solutions
        if any(word in content_lower for word in ['fixed', 'solved', 'working', 'resolved', 'success']):
            if self.extended_memory["technical_context"]["active_debugging"]:
                solution = f"Resolved: {self.extended_memory['technical_context']['active_debugging']}"
                self.extended_memory["technical_context"]["solved_problems"].append(solution)
                self.extended_memory["technical_context"]["solved_problems"] = self.extended_memory["technical_context"]["solved_problems"][-5:]  # Keep last 5
                self.extended_memory["technical_context"]["active_debugging"] = None
        
        # Track project interactions
        if 'companion app' in content_lower:
            if 'api' in content_lower or any(endpoint in content_lower for endpoint in ['health', 'contacts', 'analytics', 'sales']):
                import datetime
                self.extended_memory["project_states"]["companion_app"]["last_interaction"] = datetime.datetime.now().isoformat()
        
        # Store in long-term conversation history (keep last 50 messages)
        self.extended_memory["conversation_history"].append({
            "sender": message.sender,
            "content": message.content[:200],  # Truncate for memory efficiency
            "timestamp": message.timestamp,
            "type": getattr(message, 'message_type', 'text')
        })
        self.extended_memory["conversation_history"] = self.extended_memory["conversation_history"][-50:]


# Initialize FastAPI app and connection manager
app = FastAPI(title="ThreeWayChat Cloud Server")
manager = ConnectionManager()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def call_grok_api(message: str, context: str = "") -> str:
    """Call Grok AI API with the given message"""

    if not GROK_API_KEY:
        logger.error("GROK_API_KEY not set - using smart fallback response")
        # Smart fallback based on context
        if "debug" in message.lower() or "error" in message.lower():
            return "I can see you're debugging something! Once my API key is configured, I'll be able to provide detailed assistance. For now, Cursor is helping with the technical details."
        elif "?" in message:
            return "I hear your question! I'm Grok AI and I'm ready to help in this three-way conversation with you and Cursor. Just need my API key to be set up properly."
        else:
            return "Hello! I'm Grok AI in this three-way chat with you and Cursor. I can see the conversation but need my API key configured to provide full responses."

    # Build messages with history and system prompt
    history_messages = [
        {"role": "system", "content": context},
    ] + [
        {"role": "user" if msg.sender ==
            "phone" else "assistant", "content": msg.content}
        for msg in manager.knowledge_base[-10:]  # Last 10 messages for context
    ] + [
        {"role": "user", "content": message}
    ]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GROK_API_URL,
                headers={
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": CURRENT_GROK_MODEL,
                    "messages": history_messages,
                    "temperature": 0.7,
                    "max_tokens": 1000  # Increased for better responses
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Grok API error: {response.status} - {error_text}")
                    logger.error(f"Using model: {CURRENT_GROK_MODEL}")
                    logger.error(f"API Key length: {len(GROK_API_KEY) if GROK_API_KEY else 0}")
                    return "Sorry, there was an error processing your request."

                data = await response.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    logger.error("Invalid API response")
                    return "Sorry, I couldn't generate a response."
    except Exception as e:
        logger.error(f"Exception calling Grok API: {e}")
        logger.error(f"Model: {CURRENT_GROK_MODEL}, API Key length: {len(GROK_API_KEY) if GROK_API_KEY else 0}")
        return "Sorry, there was an error processing your request."


def is_programming_question(content: str) -> bool:
    """Detect if a message is a programming question"""
    programming_keywords = [
        "code", "program", "function", "class", "bug", "error", "debug",
        "python", "javascript", "swift", "java", "c++", "sql", "api",
        "algorithm", "data structure", "framework", "library", "git",
        "deploy", "server", "database", "frontend", "backend", "fullstack"
    ]

    content_lower = content.lower()
    return any(keyword in content_lower for keyword in programming_keywords)


@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "message": "ThreeWayChat Cloud Server",
        "status": "running",
        "connections": {
            "phone": manager.phone_connection is not None,
            "cursor": manager.cursor_connection is not None
        },
        "deployment": "cloud"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for cloud deployment"""
    return {
        "status": "healthy",
        "timestamp": manager.get_timestamp(),
        "connections": {
            "phone": manager.phone_connection is not None,
            "cursor": manager.cursor_connection is not None
        }
    }


@app.websocket("/ws/phone")
async def websocket_phone(websocket: WebSocket):
    """WebSocket endpoint for phone connection"""
    await manager.connect_phone(websocket)
    try:
        while True:
            logger.info("Phone WebSocket: Waiting for message...")
            data = await websocket.receive_text()
            logger.info(
                f"Phone WebSocket: Received data: "
                f"{data}"
            )
            message_data = json.loads(data)
            logger.info(f"Phone WebSocket: Parsed message: {message_data}")

            # Create message object
            message = Message(
                sender="phone",
                content=message_data.get("content", ""),
                message_type=message_data.get("type", "text"),
                timestamp=manager.get_timestamp()
            )

            # Add to knowledge base
            manager.add_to_knowledge_base(message)

            # Broadcast to cursor
            logger.info("Broadcasting to cursor")
            try:
                await manager.send_to_cursor({
                    "type": "message",
                    "sender": "phone",
                    "content": message.content,
                    "message_type": message.message_type,
                    "timestamp": message.timestamp
                })
                logger.info("Cursor broadcast sent successfully")
            except Exception as e:
                logger.error(f"Error broadcasting to cursor: {e}")

            # Send processing indicator to phone
            await manager.send_to_phone({
                "type": "system",
                "content": "Grok is thinking...",
                "timestamp": manager.get_timestamp()
            })

            # Call Grok API with smart context
            smart_context = manager.get_smart_context_for_grok()
            grok_response = await call_grok_api(message.content, smart_context)

            # Check for Cursor query tag
            import re
            cursor_query_match = re.search(
                r'\[CURSOR_QUERY\](.*?)\[/CURSOR_QUERY\]',
                grok_response,
                re.DOTALL
            )
            if cursor_query_match:
                cursor_query = cursor_query_match.group(1).strip()

                # Send status to phone
                await manager.send_to_phone({
                    "type": "system",
                    "content": "Grok is consulting Cursor AI...",
                    "timestamp": manager.get_timestamp()
                })

                # Send query to cursor
                await manager.send_to_cursor({
                    "type": "query",
                    "sender": "grok",
                    "content": cursor_query,
                    "timestamp": manager.get_timestamp()
                })

                # Wait for cursor response (simple timeout-based wait for demo;
                # improve later)
                cursor_response = None
                start_time = datetime.now()
                while (
                        datetime.now() -
                        start_time).seconds < 30:  # 30s timeout
                    # Check knowledge base for recent cursor message
                    recent_messages = [
                        m for m in manager.knowledge_base[-5:] if m.sender == "cursor"]
                    if recent_messages:
                        cursor_response = recent_messages[-1].content
                        break
                    await asyncio.sleep(1)

                if cursor_response:
                    # Call Grok again to summarize
                    summary_prompt = (
                        f"Summarize this Cursor AI response in simple, "
                        f"natural language: {cursor_response}. "
                        "Keep it jargon-free for voice relay."
                    )
                    grok_summary = await call_grok_api(summary_prompt, "Summarize for user")
                    final_response = grok_summary
                else:
                    final_response = "Cursor AI didn't respond in time. Here's my direct response: " + grok_response
            else:
                final_response = grok_response

            # Create final message
            final_message = Message(
                sender="grok",
                content=final_response,
                message_type="text",
                timestamp=manager.get_timestamp()
            )

            # Add to knowledge base
            manager.add_to_knowledge_base(final_message)

            # Send to phone
            await manager.send_to_phone({
                "type": "message",
                "sender": "grok",
                "content": final_response,
                "message_type": "text",
                "timestamp": final_message.timestamp
            })

    except WebSocketDisconnect:
        await manager.disconnect_phone()
    except Exception as e:
        logger.error(f"Phone WebSocket error: {e}")
        await manager.disconnect_phone()


@app.websocket("/ws/cursor")
async def websocket_cursor(websocket: WebSocket):
    """WebSocket endpoint for cursor connection"""
    await manager.connect_cursor(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Create message object
            message = Message(
                sender="cursor",
                content=message_data.get("content", ""),
                message_type=message_data.get("type", "text"),
                timestamp=manager.get_timestamp()
            )

            # Add to knowledge base
            manager.add_to_knowledge_base(message)

            # Send cursor message to phone (enabling three-way conversation)
            await manager.send_to_phone({
                "type": "message",
                "sender": "cursor",
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.timestamp
            })

            # Check if it's a programming question and route to Grok
            if is_programming_question(message.content):
                logger.info("Programming question detected, routing to Grok")

                # Send processing indicator
                await manager.send_to_cursor({
                    "type": "system",
                    "content": "Processing with Grok AI...",
                    "timestamp": manager.get_timestamp()
                })

                # Get Grok response with smart context
                smart_context = manager.get_smart_context_for_grok()
                grok_response = await call_grok_api(message.content, smart_context)

                # Create Grok response message
                grok_message = Message(
                    sender="grok",
                    content=grok_response,
                    message_type="text",
                    timestamp=manager.get_timestamp()
                )

                # Add to knowledge base
                manager.add_to_knowledge_base(grok_message)

                # Send Grok response to cursor
                await manager.send_to_cursor({
                    "type": "message",
                    "sender": "grok",
                    "content": grok_response,
                    "message_type": "text",
                    "timestamp": grok_message.timestamp
                })

    except WebSocketDisconnect:
        await manager.disconnect_cursor()
    except Exception as e:
        logger.error(f"Cursor WebSocket error: {e}")
        await manager.disconnect_cursor()


@app.get("/history")
async def get_conversation_history():
    """Get conversation history from knowledge base"""
    return {
        "messages": [
            {
                "sender": msg.sender,
                "content": msg.content,
                "message_type": msg.message_type,
                "timestamp": msg.timestamp
            }
            for msg in manager.knowledge_base
        ]
    }


@app.get("/models")
async def get_available_models():
    """Get available Grok models"""
    return {
        "models": GROK_MODELS,
        "current": CURRENT_GROK_MODEL
    }


@app.post("/model")
async def change_model(request: dict):
    """Change the current Grok model"""
    global CURRENT_GROK_MODEL
    
    new_model = request.get("model")
    if new_model not in GROK_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Available: {list(GROK_MODELS.keys())}")
    
    CURRENT_GROK_MODEL = new_model
    logger.info(f"🔄 Model changed to: {new_model}")
    
    # Broadcast model change to all connected clients
    await manager.broadcast({
        "type": "system",
        "content": f"Grok model changed to {GROK_MODELS[new_model]['name']}",
        "timestamp": manager.get_timestamp()
    })
    
    return {
        "success": True,
        "model": new_model,
        "info": GROK_MODELS[new_model]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
