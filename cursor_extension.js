// ThreeWayChat Cursor Extension
// This extension allows Cursor AI to participate in the three-way conversation

class ThreeWayChatExtension {
    constructor() {
        console.log("[ThreeWayChat] Initializing extension...");
        this.websocket = null;
        this.serverIP = "voice-chat-app-cc40.onrender.com"; // Render cloud server
        this.isConnected = false;
        this.messageHistory = [];
        this.autoRespond = true;
        console.log("[ThreeWayChat] Extension initialized with server:", this.serverIP);
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
        console.log("[ThreeWayChat] Attempting to connect to server:", this.serverIP);
        try {
            const WebSocket = require('ws');
            const url = `wss://${this.serverIP}/ws/cursor`;
            
            this.websocket = new WebSocket(url);
            
            this.websocket.on('open', () => {
                console.log("[ThreeWayChat] Connected to server");
                this.isConnected = true;
                this.sendSystemMessage("Cursor AI connected and ready to participate in the conversation");
            });
            
            this.websocket.on('message', (data) => {
                console.log("[ThreeWayChat] Received raw message:", data);
                this.handleIncomingMessage(data);
            });
            
            this.websocket.on('close', () => {
                console.log("[ThreeWayChat] Disconnected from server");
                this.isConnected = false;
            });
            
            this.websocket.on('error', (error) => {
                console.error("[ThreeWayChat] WebSocket error:", error);
                this.isConnected = false;
            });
            
        } catch (error) {
            console.error("[ThreeWayChat] Failed to connect to server:", error);
            this.isConnected = false;
        }
    }

    // Handle incoming messages from the server
    handleIncomingMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log("[ThreeWayChat] Parsed incoming message:", message);
            
            // Store message in history
            this.messageHistory.push(message);
            
            // Keep only last 50 messages
            if (this.messageHistory.length > 50) {
                this.messageHistory = this.messageHistory.slice(-50);
            }
            
            // Handle query messages from Grok (when Grok consults Cursor)
            if (message.type === "query" && message.sender === "grok") {
                console.log("[ThreeWayChat] Query from Grok - generating coding response");
                this.generateCodingResponse(message);
                return;
            }

            // If auto-respond is enabled and it's a message from phone or grok
            if (this.autoRespond && message.type === "message" && 
                (message.sender === "phone" || message.sender === "grok")) {
                
                // Generate a response based on the message
                this.generateResponse(message);
            }
            
        } catch (error) {
            console.error("[ThreeWayChat] Error parsing message:", error);
        }
    }

    // Generate a response to incoming messages
    async generateResponse(message) {
        console.log("[ThreeWayChat] Generating response for message:", message.content);
        try {
            // Simple response without API calls
            let response = "I'm Cursor AI, ready to help with coding tasks.";
            
            const content = message.content.toLowerCase();
            
            if (content.includes('code') || content.includes('program') || content.includes('function')) {
                response = "I can help with coding! What specific programming task would you like assistance with?";
            } else if (content.includes('error') || content.includes('bug') || content.includes('debug')) {
                response = "I'd be happy to help debug that issue. Can you share more details about the error you're seeing?";
            } else if (content.includes('hello') || content.includes('hi') || content.includes('working')) {
                response = "Hello! I'm Cursor AI, your coding assistant. I'm connected and ready to help!";
            } else if (content.includes('can')) {
                response = "Yes, I can help! What would you like me to assist you with?";
            }
            
            // Send the response
            await this.sendMessage(response);
            console.log("[ThreeWayChat] Response generated and sent");
            
        } catch (error) {
            console.error("[ThreeWayChat] Error generating response:", error);
        }
    }

    // Generate response specifically for coding queries from Grok
    async generateCodingResponse(message) {
        console.log("[ThreeWayChat] Generating coding response for:", message.content);
        try {
            let response = "I can help with that coding task.";
            
            const content = message.content.toLowerCase();
            
            if (content.includes('debug') || content.includes('error') || content.includes('fix')) {
                response = "To debug this issue, I'd recommend: 1) Check the console for error messages, 2) Verify variable types and values, 3) Add logging to trace the execution flow.";
            } else if (content.includes('function') || content.includes('method')) {
                response = "For creating functions, consider: 1) Clear naming conventions, 2) Single responsibility principle, 3) Proper parameter validation, 4) Return value documentation.";
            } else if (content.includes('performance') || content.includes('optimize')) {
                response = "For performance optimization: 1) Profile the code to identify bottlenecks, 2) Minimize DOM manipulations, 3) Use efficient algorithms, 4) Consider caching strategies.";
            } else if (content.includes('database') || content.includes('sql')) {
                response = "For database queries: 1) Use proper indexing, 2) Avoid N+1 queries, 3) Validate input parameters, 4) Consider using prepared statements for security.";
            } else if (content.includes('api') || content.includes('endpoint')) {
                response = "For API development: 1) Follow RESTful conventions, 2) Implement proper error handling, 3) Add input validation, 4) Include comprehensive documentation.";
            } else if (content.includes('test') || content.includes('testing')) {
                response = "For testing: 1) Write unit tests for individual functions, 2) Add integration tests for workflows, 3) Mock external dependencies, 4) Aim for good test coverage.";
            }
            
            // Send the response
            await this.sendMessage(response);
            console.log("[ThreeWayChat] Coding response generated and sent");
            
        } catch (error) {
            console.error("[ThreeWayChat] Error generating coding response:", error);
        }
    }

    // New method to call Grok API
    async callGrokAPI(message, systemPrompt) {
        console.log("[ThreeWayChat] Calling Grok API with prompt:", systemPrompt);
        const fetch = require('node-fetch');
        
        const API_KEY = process.env.GROK_API_KEY;  // Set this env var
        if (!API_KEY) {
            console.error("[ThreeWayChat] GROK_API_KEY not set");
            throw new Error("GROK_API_KEY not set");
        }
        
        const response = await fetch('https://api.x.ai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify({
                model: 'grok-4-latest',
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: message }
                ],
                temperature: 0.7,
                max_tokens: 500
            })
        });
        
        const data = await response.json();
        if (data.choices && data.choices[0]) {
            console.log("[ThreeWayChat] Grok API response received");
            return data.choices[0].message.content.trim();
        } else {
            console.error("[ThreeWayChat] Invalid API response");
            throw new Error("Invalid API response");
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
        console.log("[ThreeWayChat] Sending message:", content);
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
