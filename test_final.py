#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test():
    uri = "wss://347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev:5000/ws/phone"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Get connection response
            response = await websocket.recv()
            print(f"📨 {response}")
            
            # Send message
            await websocket.send(json.dumps({"content": "Hello Grok!", "type": "text"}))
            print("📤 Sent: Hello Grok!")
            
            # Wait for processing
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📨 Processing: {response}")
            
            # Wait for Grok response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📨 Grok: {response}")
            
            print("✅ SUCCESS! Server is responding!")
            
    except Exception as e:
        print(f"❌ {e}")

asyncio.run(test())
