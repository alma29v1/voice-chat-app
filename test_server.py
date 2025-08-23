#!/usr/bin/env python3
"""
Test script for ThreeWayChat server
Tests WebSocket connections and Grok API integration
"""

import asyncio
import websockets
import json
import requests
import time

# Server configuration
SERVER_IP = "localhost"  # Change to your server IP
SERVER_PORT = 8000
PHONE_WS_URL = f"ws://{SERVER_IP}:{SERVER_PORT}/ws/phone"
CURSOR_WS_URL = f"ws://{SERVER_IP}:{SERVER_PORT}/ws/cursor"

async def test_phone_connection():
    """Test phone WebSocket connection"""
    print("📱 Testing phone connection...")
    
    try:
        async with websockets.connect(PHONE_WS_URL) as websocket:
            print("✅ Phone WebSocket connected successfully")
            
            # Send a test message
            test_message = {
                "type": "message",
                "sender": "phone",
                "content": "Hello from phone test!",
                "message_type": "text",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message from phone")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
                
    except Exception as e:
        print(f"❌ Phone connection failed: {e}")

async def test_cursor_connection():
    """Test cursor WebSocket connection"""
    print("💻 Testing cursor connection...")
    
    try:
        async with websockets.connect(CURSOR_WS_URL) as websocket:
            print("✅ Cursor WebSocket connected successfully")
            
            # Send a programming question to test Grok integration
            test_message = {
                "type": "message",
                "sender": "cursor",
                "content": "How do I create a Python function?",
                "message_type": "text",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Sent programming question from cursor")
            
            # Wait for Grok response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📥 Received Grok response: {response[:200]}...")
            except asyncio.TimeoutError:
                print("⏰ No Grok response received within 10 seconds")
                
    except Exception as e:
        print(f"❌ Cursor connection failed: {e}")

def test_http_endpoints():
    """Test HTTP endpoints"""
    print("🌐 Testing HTTP endpoints...")
    
    base_url = f"http://{SERVER_IP}:{SERVER_PORT}"
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ HTTP test failed: {e}")
    
    try:
        # Test IP endpoint
        response = requests.get(f"{base_url}/ip")
        if response.status_code == 200:
            print("✅ IP endpoint working")
            print(f"   Server IP: {response.json()}")
        else:
            print(f"❌ IP endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ IP endpoint test failed: {e}")

async def main():
    """Run all tests"""
    print("🧪 ThreeWayChat Server Test Suite")
    print("=" * 40)
    
    # Test HTTP endpoints first
    test_http_endpoints()
    print()
    
    # Test WebSocket connections
    await test_phone_connection()
    print()
    
    await test_cursor_connection()
    print()
    
    print("🏁 Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main())
