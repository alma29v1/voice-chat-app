#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_response():
    uri = "wss://347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev:5000/ws/phone"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to server")
            
            # Get connection response
            response = await websocket.recv()
            print(f"📨 Connection: {response}")
            
            # Send a test message
            test_msg = {"content": "Hello, can you hear me?", "type": "text"}
            await websocket.send(json.dumps(test_msg))
            print("📤 Sent: Hello, can you hear me?")
            
            # Wait for processing message
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📨 Processing: {response}")
            
            # Wait for Grok response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"📨 Grok response: {response}")
            
            print("✅ Test completed successfully!")
            
    except asyncio.TimeoutError:
        print("⏰ Timeout - server not responding")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test_response())
