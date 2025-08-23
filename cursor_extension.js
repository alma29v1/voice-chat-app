// ThreeWayChat Cursor Extension
// This extension allows Cursor AI to participate in the three-way conversation

class ThreeWayChatExtension {
    constructor() {
        this.websocket = null;
        this.serverIP = "347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev"; // Your cloud server
        this.isConnected = false;
        this.messageHistory = [];
        this.autoRespond = true;
    }

    // Initialize the extension
    async initialize() {
        console.log("🚀 ThreeWayChat Cursor Extension initializing...");
        
        // Try to get server IP from environment or config
        this.serverIP = process.env.THREEWAYCHAT_SERVER_IP || this.serverIP;
        
        // Connect to the server
        await this.connectToServer();
        
        // Set up periodic connection check
        setInterval(() => {
            if (!this.isConnected) {
                this.connectToServer();
            }
        }, 5000);
        
        console.log("✅ ThreeWayChat Cursor Extension ready!");
    }

    // Connect to the ThreeWayChat server
    async connectToServer() {
        try {
            const WebSocket = require('ws');
            const url = `wss://${this.serverIP}/ws/cursor`;
            
            this.websocket = new WebSocket(url);
            
            this.websocket.on('open', () => {
                console.log("🔗 Connected to ThreeWayChat server");
                this.isConnected = true;
                this.sendSystemMessage("Cursor AI connected and ready to participate in the conversation");
            });
            
            this.websocket.on('message', (data) => {
                this.handleIncomingMessage(data);
            });
            
            this.websocket.on('close', () => {
                console.log("❌ Disconnected from ThreeWayChat server");
                this.isConnected = false;
            });
            
            this.websocket.on('error', (error) => {
                console.error("WebSocket error:", error);
                this.isConnected = false;
            });
            
        } catch (error) {
            console.error("Failed to connect to server:", error);
            this.isConnected = false;
        }
    }

    // Handle incoming messages from the server
    handleIncomingMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log("📨 Received message:", message);
            
            // Store message in history
            this.messageHistory.push(message);
            
            // Keep only last 50 messages
            if (this.messageHistory.length > 50) {
                this.messageHistory = this.messageHistory.slice(-50);
            }
            
            // If auto-respond is enabled and it's a message from phone or grok
            if (this.autoRespond && message.type === "message" && 
                (message.sender === "phone" || message.sender === "grok")) {
                
                // Generate a response based on the message
                this.generateResponse(message);
            }
            
        } catch (error) {
            console.error("Error parsing message:", error);
        }
    }

    // Generate a response to incoming messages
    async generateResponse(message) {
        try {
            // Create a context-aware response
            const response = this.createContextualResponse(message);
            
            // Send the response
            await this.sendMessage(response);
            
        } catch (error) {
            console.error("Error generating response:", error);
        }
    }

    // Create a contextual response based on the message
    createContextualResponse(message) {
        const content = message.content.toLowerCase();
        
        // Programming-related responses
        if (content.includes("code") || content.includes("programming") || content.includes("bug")) {
            return "I can help with programming questions! I have access to your codebase and can provide specific assistance with your project.";
        }
        
        if (content.includes("python") || content.includes("javascript") || content.includes("swift")) {
            return "I'm familiar with multiple programming languages and can help you with code examples, debugging, and best practices.";
        }
        
        // Project-related responses
        if (content.includes("project") || content.includes("feature") || content.includes("implement")) {
            return "I can help you implement new features, refactor code, or work on your project. What would you like to work on?";
        }
        
        // General conversation
        if (content.includes("hello") || content.includes("hi")) {
            return "Hello! I'm the Cursor AI assistant. I'm here to help with your coding tasks and participate in our three-way conversation.";
        }
        
        // Default response
        return "I'm listening and ready to help with any programming or development tasks you have!";
    }

    // Send a message to the server
    async sendMessage(content) {
        if (!this.isConnected || !this.websocket) {
            console.log("❌ Not connected to server, cannot send message");
            return;
        }
        
        try {
            const message = {
                content: content,
                type: "text"
            };
            
            this.websocket.send(JSON.stringify(message));
            console.log("📤 Sent message:", content);
            
        } catch (error) {
            console.error("Error sending message:", error);
        }
    }

    // Send a system message
    async sendSystemMessage(content) {
        if (!this.isConnected || !this.websocket) {
            return;
        }
        
        try {
            const message = {
                content: content,
                type: "system"
            };
            
            this.websocket.send(JSON.stringify(message));
            
        } catch (error) {
            console.error("Error sending system message:", error);
        }
    }

    // Get conversation history
    getConversationHistory() {
        return this.messageHistory;
    }

    // Toggle auto-response
    toggleAutoRespond() {
        this.autoRespond = !this.autoRespond;
        console.log(`Auto-respond ${this.autoRespond ? 'enabled' : 'disabled'}`);
        return this.autoRespond;
    }

    // Set server IP
    setServerIP(ip) {
        this.serverIP = ip;
        console.log(`Server IP set to: ${ip}`);
        
        // Reconnect with new IP
        if (this.websocket) {
            this.websocket.close();
        }
        this.connectToServer();
    }

    // Get connection status
    getStatus() {
        return {
            connected: this.isConnected,
            serverIP: this.serverIP,
            autoRespond: this.autoRespond,
            messageCount: this.messageHistory.length
        };
    }
}

// Export the extension
module.exports = ThreeWayChatExtension;

// If running directly, initialize the extension
if (require.main === module) {
    const extension = new ThreeWayChatExtension();
    extension.initialize().catch(console.error);
}
