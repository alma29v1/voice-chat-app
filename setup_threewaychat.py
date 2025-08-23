#!/usr/bin/env python3
"""
ThreeWayChat Setup Script
Helps configure and start the three-way conversation system
"""

import socket
import subprocess
import sys
import os
import json
from pathlib import Path

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Could not determine IP address: {e}")
        return "localhost"

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "websockets",
        "requests",
        "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def start_backend_server():
    """Start the backend server"""
    print("🚀 Starting ThreeWayChat backend server...")
    
    server_path = Path("backend/server.py")
    if not server_path.exists():
        print("❌ Backend server not found at backend/server.py")
        return False
    
    try:
        # Start the server in the background
        process = subprocess.Popen([
            sys.executable, str(server_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Backend server started successfully")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return False

def create_config_file(server_ip):
    """Create a configuration file with server details"""
    config = {
        "server_ip": server_ip,
        "server_port": 8000,
        "phone_websocket": f"ws://{server_ip}:8000/ws/phone",
        "cursor_websocket": f"ws://{server_ip}:8000/ws/cursor",
        "api_endpoint": f"http://{server_ip}:8000"
    }
    
    with open("threewaychat_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration file created: threewaychat_config.json")

def print_connection_instructions(server_ip):
    """Print connection instructions"""
    print("\n" + "="*60)
    print("🎯 THREE-WAY CHAT SETUP COMPLETE!")
    print("="*60)
    
    print(f"\n📱 VOICE CONTROL APP:")
    print(f"   1. Open your voice control app in Xcode")
    print(f"   2. Tap the gear icon to configure server")
    print(f"   3. Enter server IP: {server_ip}")
    print(f"   4. Build and run the app")
    
    print(f"\n💻 CURSOR AI:")
    print(f"   1. Install the cursor extension:")
    print(f"      npm install ws")
    print(f"   2. Set environment variable:")
    print(f"      export THREEWAYCHAT_SERVER_IP={server_ip}")
    print(f"   3. Run the extension:")
    print(f"      node cursor_extension.js")
    
    print(f"\n🤖 GROK AI:")
    print(f"   - Already configured in backend/server.py")
    print(f"   - Will automatically respond to programming questions")
    
    print(f"\n🔗 CONNECTION DETAILS:")
    print(f"   Server IP: {server_ip}")
    print(f"   Phone WebSocket: ws://{server_ip}:8000/ws/phone")
    print(f"   Cursor WebSocket: ws://{server_ip}:8000/ws/cursor")
    print(f"   API Endpoint: http://{server_ip}:8000")
    
    print(f"\n🎉 HOW TO USE:")
    print(f"   1. Start the backend server: python backend/server.py")
    print(f"   2. Run the voice control app on your phone")
    print(f"   3. Start the cursor extension")
    print(f"   4. Speak into your phone - it will be transcribed and sent to Grok")
    print(f"   5. Grok will respond, and Cursor AI can participate too!")
    
    print("\n" + "="*60)

def main():
    print("🎤 ThreeWayChat Setup")
    print("="*40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Get server IP
    server_ip = get_local_ip()
    print(f"📍 Server IP: {server_ip}")
    
    # Create config file
    create_config_file(server_ip)
    
    # Print instructions
    print_connection_instructions(server_ip)
    
    # Ask if user wants to start the server
    response = input("\n🤔 Would you like to start the backend server now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        server_process = start_backend_server()
        if server_process:
            print("\n✅ Server is running! Press Ctrl+C to stop.")
            try:
                server_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                server_process.terminate()

if __name__ == "__main__":
    main()
