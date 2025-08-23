#!/usr/bin/env python3
"""
Simple test server to verify WebSocket functionality
"""

import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Simple test server running"}

@app.websocket("/ws/phone")
async def websocket_phone(websocket: WebSocket):
    await websocket.accept()
    print("📱 Phone connected")
    
    # Send connection confirmation
    await websocket.send_text(json.dumps({
        "type": "system",
        "content": "Connected to test server",
        "timestamp": "2025-08-23T14:00:00.000000"
    }))
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            print(f"📨 Received: {message_data}")
            
            # Send processing message
            await websocket.send_text(json.dumps({
                "type": "system",
                "content": "Processing with Grok AI...",
                "timestamp": "2025-08-23T14:00:00.000000"
            }))
            
            # Send Grok response
            await websocket.send_text(json.dumps({
                "type": "message",
                "sender": "grok",
                "content": "Hello! I'm Grok AI. This is a test response from the simple server. The WebSocket connection is working!",
                "message_type": "text",
                "timestamp": "2025-08-23T14:00:00.000000"
            }))
            
            print("✅ Sent response")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting simple test server...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
