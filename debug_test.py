import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_websocket():
    uri = "wss://347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev:5000/ws/phone"
    
    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Wait for initial message
            initial_msg = await websocket.recv()
            print(f"📨 Initial: {initial_msg}")
            
            # Send a test message
            test_message = {
                "type": "text",
                "content": "Hello from test script"
            }
            
            print(f"📤 Sending: {json.dumps(test_message)}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            print("⏳ Waiting for response...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📨 Response: {response}")
            except asyncio.TimeoutError:
                print("❌ Timeout - no response received")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
