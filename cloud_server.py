#!/usr/bin/env python3
"""
Cloud-Based ThreeWayChat Server
Deploy this to your website or cloud service (Heroku, Railway, Render, etc.)
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import aiohttp
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Grok AI Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY", "")  # Set via Replit secrets
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-4-latest"

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
        logger.info(f"Added to knowledge base: {message.sender}: {message.content[:50]}...")

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
    
    logger.info(f"call_grok_api called with message: {message[:50]}...")
    
    # For now, return a simple response to test the flow
    responses = [
        "Hello! I'm Grok AI. I'm here to help you with any questions or conversations. What would you like to talk about?",
        "Hi there! I'm Grok AI, ready to assist you with programming, general questions, or just chat. What's on your mind?",
        "Greetings! I'm Grok AI. I can help with coding, problem-solving, or casual conversation. How can I assist you today?",
        "Hello! I'm Grok AI. I'm excited to help you with any questions or topics you'd like to discuss. What would you like to explore?"
    ]
    
    import random
    response = random.choice(responses)
    logger.info(f"Returning response: {response[:50]}...")
    return response

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
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
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
            await manager.send_to_cursor({
                "type": "message",
                "sender": "phone",
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.timestamp
            })
            
            # Send immediate response for testing
            logger.info("Sending immediate response")
            
            # Send processing indicator
            await manager.send_to_phone({
                "type": "system",
                "content": "Processing with Grok AI...",
                "timestamp": manager.get_timestamp()
            })
            
            # Send Grok response immediately
            await manager.send_to_phone({
                "type": "message",
                "sender": "grok",
                "content": "Hello! I'm Grok AI. I can hear you! This is a test response to make sure the conversation is working.",
                "message_type": "text",
                "timestamp": manager.get_timestamp()
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
            
            # Broadcast to phone
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

if __name__ == "__main__":
    # Get port from environment (for cloud deployment)
    port = int(os.getenv("PORT", 5000))
    
    print(f"🚀 ThreeWayChat Cloud Server starting...")
    print(f"📱 Phone should connect to: ws://your-domain.com/ws/phone")
    print(f"💻 Cursor should connect to: ws://your-domain.com/ws/cursor")
    print(f"🌐 Server running on port: {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
