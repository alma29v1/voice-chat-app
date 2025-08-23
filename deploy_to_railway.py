#!/usr/bin/env python3
"""
Railway Deployment Helper
Helps you deploy ThreeWayChat to Railway
"""

import os
import subprocess
import json
from pathlib import Path

def check_git_repo():
    """Check if this is a git repository"""
    if not Path(".git").exists():
        print("❌ This is not a git repository")
        print("Please run: git init && git add . && git commit -m 'Initial commit'")
        return False
    return True

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Railway CLI not found")
    print("Install it with: npm install -g @railway/cli")
    return False

def create_railway_config():
    """Create Railway configuration"""
    config = {
        "build": {
            "builder": "nixpacks"
        },
        "deploy": {
            "startCommand": "uvicorn cloud_server:app --host 0.0.0.0 --port $PORT",
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created railway.json configuration")

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    try:
        # Login to Railway
        print("🔐 Logging into Railway...")
        subprocess.run(["railway", "login"], check=True)
        
        # Initialize Railway project
        print("📦 Initializing Railway project...")
        subprocess.run(["railway", "init"], check=True)
        
        # Set environment variables
        grok_key = input("Enter your Grok API key: ").strip()
        if grok_key:
            print("🔑 Setting environment variables...")
            subprocess.run(["railway", "variables", "set", f"GROK_API_KEY={grok_key}"], check=True)
        
        # Deploy
        print("🚀 Deploying...")
        subprocess.run(["railway", "deploy"], check=True)
        
        # Get the URL
        print("🔗 Getting deployment URL...")
        result = subprocess.run(["railway", "domain"], capture_output=True, text=True, check=True)
        domain = result.stdout.strip()
        
        print(f"\n🎉 Deployment successful!")
        print(f"🌐 Your app is live at: https://{domain}")
        print(f"📱 Phone WebSocket: wss://{domain}/ws/phone")
        print(f"💻 Cursor WebSocket: wss://{domain}/ws/cursor")
        
        return domain
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return None
    except KeyboardInterrupt:
        print("\n🛑 Deployment cancelled")
        return None

def update_app_configs(domain):
    """Update app configurations with the new domain"""
    print(f"\n🔧 Updating app configurations...")
    
    # Update voice control app
    swift_file = Path("ThreeWayChat/Voice control/Voice control/ContentView.swift")
    if swift_file.exists():
        with open(swift_file, "r") as f:
            content = f.read()
        
        # Replace the server IP with the domain
        content = content.replace(
            '@State private var serverIP = "192.168.84.130"',
            f'@State private var serverIP = "{domain}"'
        )
        
        with open(swift_file, "w") as f:
            f.write(content)
        
        print("✅ Updated voice control app configuration")
    
    # Update cursor extension
    js_file = Path("cursor_extension.js")
    if js_file.exists():
        with open(js_file, "r") as f:
            content = f.read()
        
        # Replace the server IP with the domain
        content = content.replace(
            'this.serverIP = "192.168.84.130";',
            f'this.serverIP = "{domain}";'
        )
        
        with open(js_file, "w") as f:
            f.write(content)
        
        print("✅ Updated cursor extension configuration")
    
    # Create updated config file
    config = {
        "server_domain": domain,
        "phone_websocket": f"wss://{domain}/ws/phone",
        "cursor_websocket": f"wss://{domain}/ws/cursor",
        "api_endpoint": f"https://{domain}"
    }
    
    with open("threewaychat_cloud_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created cloud configuration file")

def main():
    print("🚀 Railway Deployment Helper")
    print("="*40)
    
    # Check prerequisites
    if not check_git_repo():
        return
    
    if not check_railway_cli():
        return
    
    # Create Railway config
    create_railway_config()
    
    # Deploy
    domain = deploy_to_railway()
    
    if domain:
        # Update configurations
        update_app_configs(domain)
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Build and run your voice control app in Xcode")
        print(f"2. Run the cursor extension: node cursor_extension.js")
        print(f"3. Start chatting! 🎉")
        
        print(f"\n📋 CONNECTION DETAILS:")
        print(f"Domain: {domain}")
        print(f"Phone: wss://{domain}/ws/phone")
        print(f"Cursor: wss://{domain}/ws/cursor")
        print(f"API: https://{domain}")

if __name__ == "__main__":
    main()
