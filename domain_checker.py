#!/usr/bin/env python3
"""
Domain Checker for ThreeWayChat
Automatically finds and updates the current Replit server domain
"""

import requests
import json
import time
import subprocess
import os

class DomainChecker:
    def __init__(self):
        self.base_domain = "riker.replit.dev"
        self.known_prefixes = [
            "347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz",
            # Add more known prefixes here as they change
        ]
        
    def check_domain(self, domain):
        """Check if a domain is responding"""
        try:
            url = f"https://{domain}:5000/"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "ThreeWayChat Cloud Server":
                    return True, data
        except Exception as e:
            pass
        return False, None
    
    def find_current_domain(self):
        """Find the current working domain"""
        print("🔍 Searching for current server domain...")
        
        # First, try known domains
        for prefix in self.known_prefixes:
            domain = f"{prefix}.{self.base_domain}"
            print(f"  Trying: {domain}")
            is_working, data = self.check_domain(domain)
            if is_working:
                print(f"✅ Found working domain: {domain}")
                return domain, data
        
        print("❌ No known domains working. You may need to restart the Replit server.")
        return None, None
    
    def update_ios_app(self, domain):
        """Update the iOS app with the new domain"""
        if not domain:
            print("❌ No domain provided for update")
            return False
            
        print(f"📱 Updating iOS app with domain: {domain}")
        
        # Path to the iOS app file
        ios_file = "ThreeWayChat/Voice control/Voice control/ContentView.swift"
        
        if not os.path.exists(ios_file):
            print(f"❌ iOS file not found: {ios_file}")
            return False
        
        try:
            # Read the current file
            with open(ios_file, 'r') as f:
                content = f.read()
            
            # Update the server IP
            import re
            pattern = r'@State private var serverIP = "[^"]*"'
            replacement = f'@State private var serverIP = "{domain}"'
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                
                # Write the updated content
                with open(ios_file, 'w') as f:
                    f.write(new_content)
                
                print(f"✅ iOS app updated with new domain: {domain}")
                return True
            else:
                print("❌ Could not find serverIP line in iOS file")
                return False
                
        except Exception as e:
            print(f"❌ Error updating iOS app: {e}")
            return False
    
    def create_domain_file(self, domain):
        """Create a file with the current domain for easy access"""
        try:
            with open("current_domain.txt", 'w') as f:
                f.write(domain)
            print(f"📄 Current domain saved to: current_domain.txt")
        except Exception as e:
            print(f"❌ Error saving domain file: {e}")
    
    def run(self):
        """Main function to find and update domain"""
        print("🚀 ThreeWayChat Domain Checker")
        print("=" * 40)
        
        # Find current domain
        domain, data = self.find_current_domain()
        
        if domain:
            print(f"\n📊 Server Status:")
            print(f"   Domain: {domain}")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Connections: {data.get('connections', {})}")
            
            # Update iOS app
            if self.update_ios_app(domain):
                print(f"\n✅ SUCCESS: iOS app updated!")
                print(f"   Rebuild your iOS app to use the new domain")
            else:
                print(f"\n⚠️  WARNING: Could not update iOS app automatically")
                print(f"   Manual update required: {domain}")
            
            # Save domain to file
            self.create_domain_file(domain)
            
        else:
            print(f"\n❌ No working domain found!")
            print(f"   Please restart your Replit server")
            print(f"   Then run this script again")

if __name__ == "__main__":
    checker = DomainChecker()
    checker.run()
