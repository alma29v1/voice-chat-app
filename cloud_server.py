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

# Available Grok models with pricing info (hypothetical costs for reference)
GROK_MODELS = {
    "grok-2-mini": {"name": "Grok 2 Mini", "cost": "Cheapest", "speed": "Fastest"},
    "grok-2": {"name": "Grok 2", "cost": "Medium", "speed": "Fast"},  
    "grok-2-1212": {"name": "Grok 2 (Dec 2024)", "cost": "Medium", "speed": "Fast"},
    "grok-beta": {"name": "Grok Beta", "cost": "Higher", "speed": "Medium"},
    "grok-vision-beta": {"name": "Grok Vision", "cost": "Highest", "speed": "Slower"}
}

# Current model (can be changed via API)  
CURRENT_GROK_MODEL = "grok-2"

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
        """Store message in knowledge base"""
        self.knowledge_base.append(message)
        logger.info(
            f"Added to knowledge base: {message.sender}: {message.content[:50]}...")


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
        logger.error("GROK_API_KEY not set - using fallback response")
        return "Hello! I'm Grok AI. I can hear you! This is a test response to make sure the conversation is working."

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
                    "max_tokens": 500
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

            # Call Grok API
            grok_response = await call_grok_api(
                message.content,
                (
                    "You are Grok in a three-way conversation with the user and Cursor AI. "
                    "Respond naturally. If the query needs coding help, wrap the specific "
                    "task in [CURSOR_QUERY]task here[/CURSOR_QUERY]. Summarize any Cursor "
                    "responses in plain English."
                )
            )

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

                # Get Grok response
                grok_response = await call_grok_api(message.content, "Programming question from cursor")

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
