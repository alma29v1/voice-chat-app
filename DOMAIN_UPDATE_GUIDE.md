# 🔄 ThreeWayChat Domain Update Guide

## 🚨 **The Problem**
Replit servers change their domain names when restarted, which breaks the iOS app connection.

## ✅ **The Solution**
We've created an automatic domain updater that finds the current server domain and updates your iOS app automatically.

## 📋 **How to Use**

### **Option 1: Simple Script (Recommended)**
```bash
./update_domain.sh
```

### **Option 2: Direct Python Script**
```bash
python3 domain_checker.py
```

## 🔧 **What It Does**

1. **🔍 Searches** for the current working server domain
2. **📱 Updates** your iOS app automatically with the new domain
3. **💾 Saves** the current domain to `current_domain.txt`
4. **✅ Confirms** the update was successful

## 📱 **After Running the Script**

1. **Rebuild your iOS app** in Xcode
2. **Install the updated app** on your device
3. **Test the connection** - it should work immediately!

## 🚀 **When to Use This**

- ✅ **After restarting the Replit server**
- ✅ **When the app shows "Connection failed"**
- ✅ **When you get a new domain from Replit**
- ✅ **Before testing the app after server changes**

## 📊 **Example Output**
```
🚀 ThreeWayChat Domain Checker
========================================
🔍 Searching for current server domain...
  Trying: 347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev
✅ Found working domain: 347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev

📊 Server Status:
   Domain: 347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev
   Status: running
   Connections: {'phone': False, 'cursor': False}
📱 Updating iOS app with domain: 347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev
✅ iOS app updated with new domain: 347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev

✅ SUCCESS: iOS app updated!
   Rebuild your iOS app to use the new domain
📄 Current domain saved to: current_domain.txt
```

## 🔄 **Workflow**

1. **Server restarts** → Domain changes
2. **Run update script** → Finds new domain
3. **Script updates iOS app** → New domain installed
4. **Rebuild iOS app** → Ready to use
5. **Test connection** → Should work!

## 🛠 **Troubleshooting**

### **Script says "No known domains working"**
- Restart your Replit server
- Run the script again

### **iOS app not updating**
- Check that `ContentView.swift` exists
- Make sure you have write permissions
- Try running the Python script directly

### **Still can't connect**
- Check the `current_domain.txt` file for the domain
- Manually update the domain in Xcode
- Verify the server is running

## 📞 **Support**
If you need help, check:
1. The `current_domain.txt` file for the current domain
2. The server status at the domain URL
3. The iOS app connection status
