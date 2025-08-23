#!/usr/bin/env python3
"""
Test WebSocket connection and message flow
"""

import asyncio
import websockets
import json
import time

async def test_websocket():
    uri = "wss://347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev:5000/ws/phone"
    
    print("🔗 Testing WebSocket connection...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            print(f"📨 Connection response: {response}")
            
            # Send a test message
            test_message = {
                "content": "Hello Grok, can you help me with a programming question?",
                "type": "text"
            }
            
            print(f"🎤 Sending message: {test_message['content']}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for responses
            print("⏳ Waiting for responses...")
            
            response_count = 0
            while response_count < 3:  # Wait for up to 3 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    response_data = json.loads(response)
                    response_count += 1
                    
                    print(f"📨 Response {response_count}:")
                    print(f"   Type: {response_data.get('type', 'unknown')}")
                    print(f"   Sender: {response_data.get('sender', 'unknown')}")
                    print(f"   Content: {response_data.get('content', '')[:100]}...")
                    print()
                    
                    if response_data.get("sender") == "grok":
                        print("✅ Grok AI responded successfully!")
                        break
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break
            
            print("✅ Test completed!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
