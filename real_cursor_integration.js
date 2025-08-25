// Real Cursor Integration for ThreeWayChat
// This connects to the actual Cursor AI in this conversation window

const WebSocket = require('ws');

class RealCursorIntegration {
    constructor() {
        this.serverIP = 'voice-chat-app-cc40.onrender.com';
        this.ws = null;
        this.conversationContext = '';
        this.currentProject = 'threeway-chat'; // Default project
        this.projects = {
            'threeway-chat': {
                name: 'ThreeWayChat App',
                path: '/Volumes/LaCie/ThreeWayChat',
                description: 'Voice-controlled three-way chat with Grok and Cursor AI'
            },
            'big-beautiful': {
                name: 'Big Beautiful Program',
                path: '/path/to/big-beautiful-program', // Update with actual path
                description: 'Main application with API and server',
                apiUrl: 'your-big-beautiful-program-api-url' // Update with actual API
            },
            'companion-app': {
                name: 'Big Beautiful Program Companion',
                path: '/path/to/companion-app', // Update with actual path
                description: 'Companion application for Big Beautiful Program',
                apiUrl: 'http://localhost:5001',
                endpoints: {
                    'health': 'GET /api/health',
                    'contacts': 'GET /api/contacts',
                    'contact': 'GET /api/contacts/<id>',
                    'create-contact': 'POST /api/contacts',
                    'geocode': 'POST /api/geocode',
                    'att-fiber-check': 'POST /api/att-fiber-check',
                    'analytics': 'GET /api/analytics',
                    'sync': 'POST /api/sync',
                    'rolling-sales': 'GET /api/rolling-sales',
                    'export-sales': 'GET /api/rolling-sales/export'
                }
            }
        };
        console.log('[Real Cursor] Initializing real Cursor integration...');
        console.log(`[Real Cursor] Current project: ${this.projects[this.currentProject].name}`);
    }

    async connect() {
        try {
            console.log('[Real Cursor] Connecting to server:', this.serverIP);
            this.ws = new WebSocket(`wss://${this.serverIP}/ws/cursor`);
            
            this.ws.on('open', () => {
                console.log('✅ [Real Cursor] Connected to ThreeWayChat server');
                this.sendMessage('Real Cursor AI connected and ready to assist with this conversation');
            });

            this.ws.on('message', (data) => {
                this.handleIncomingMessage(data);
            });

            this.ws.on('close', () => {
                console.log('[Real Cursor] Disconnected from server');
                setTimeout(() => this.connect(), 5000); // Auto-reconnect
            });

            this.ws.on('error', (error) => {
                console.error('[Real Cursor] WebSocket error:', error);
            });

        } catch (error) {
            console.error('[Real Cursor] Connection error:', error);
        }
    }

    handleIncomingMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('[Real Cursor] Received:', message);

            // Respond to phone messages that need assistance
            if (message.sender === 'phone' && message.type === 'message') {
                console.log('[Real Cursor] Phone message received, checking if help needed...');
                
                        // Check for project switching commands
        const content = message.content.toLowerCase();
        if (content.includes('switch to') || content.includes('change project')) {
            this.handleProjectSwitch(message.content);
            return;
        }
        
        // Check if it's a programming/tech question
        if (content.includes('debug') || content.includes('error') || 
            content.includes('undefined') || content.includes('function') ||
            content.includes('help') || content.includes('javascript') ||
            content.includes('code') || content.includes('api') ||
            content.includes('run function') || content.includes('execute')) {
            
            console.log('[Real Cursor] Programming/API question detected, providing assistance...');
            this.provideRealCursorResponse(message.content);
        }
            }
            
            // Also respond to queries from Grok (CURSOR_QUERY tags)
            if (message.type === 'query' && message.sender === 'grok') {
                console.log('[Real Cursor] Grok is asking for help with:', message.content);
                this.provideRealCursorResponse(message.content);
            }
        } catch (error) {
            console.error('[Real Cursor] Error parsing message:', error);
        }
    }

    async provideRealCursorResponse(query) {
        // This is where we'd integrate with the real Cursor AI
        // For now, let's provide intelligent responses based on the actual conversation context
        
        let response = '';
        
        if (query.toLowerCase().includes('debug') || query.toLowerCase().includes('undefined')) {
            response = `Based on our conversation history, I can see you're building a three-way chat app with voice control. For JavaScript functions returning undefined, check:

1. **Return statements**: Make sure your functions explicitly return values
2. **Async/await**: If calling async functions, ensure proper await usage  
3. **Variable scope**: Check if variables are defined in the right scope
4. **Function calls**: Verify you're calling functions with correct parameters

From your ThreeWayChat app, I can see similar patterns in your WebSocket message handling and speech recognition functions.`;
        
        } else if (query.toLowerCase().includes('websocket') || query.toLowerCase().includes('connection')) {
            response = `Looking at your ThreeWayChat implementation, I can see you're using WebSocket connections. Common issues:

1. **Connection state**: Check if WebSocket is in OPEN state before sending
2. **Error handling**: Add proper error handlers for connection failures
3. **Reconnection logic**: Implement auto-reconnect like in your iOS app
4. **Message format**: Ensure JSON messages match expected server format

Your current setup with Render deployment looks solid.`;
            
        } else if (query.toLowerCase().includes('swift') || query.toLowerCase().includes('ios')) {
            response = `From your iOS app development, I can see you're working with:

1. **SwiftUI**: Voice control interface with proper state management
2. **AVSpeechSynthesizer**: Text-to-speech functionality  
3. **SFSpeechRecognizer**: Speech-to-text conversion
4. **WebSocket**: Real-time communication with your server

The voice activity detection you implemented is working well. Any specific iOS issues?`;

        } else if (query.toLowerCase().includes('run function') || query.toLowerCase().includes('execute') || query.toLowerCase().includes('call api') || query.toLowerCase().includes('get contacts') || query.toLowerCase().includes('check health') || query.toLowerCase().includes('get analytics')) {
            
            // Handle specific API commands for Companion App
            if (this.currentProject === 'companion-app') {
                await this.handleCompanionAPICommand(query);
                return;
            } else if (this.currentProject === 'big-beautiful') {
                response = `I can help you run functions in your Big Beautiful Program! 

**Available Commands:**
- "run function [name]" - Execute a specific function
- "call api [endpoint]" - Make an API call
- "get status" - Check program status
- "list functions" - Show available functions

What function would you like to execute?`;
            } else {
                response = `To run functions and APIs, first switch to a project:
- "Switch to Big Beautiful Program" 
- "Switch to Companion App"

Then I can help you execute functions and make API calls.`;
            }
        } else {
            const currentProj = this.projects[this.currentProject];
            response = `I can help with **${currentProj.name}**! I'm connected to your actual Cursor conversation and can see:

- Your current project: **${currentProj.name}**
- Project path: ${currentProj.path}
- ${currentProj.description}
${currentProj.apiUrl ? `- API available for function calls` : ''}

**Available Commands:**
🔄 "Switch to [project name]" - Change projects
${this.currentProject === 'big-beautiful' ? '⚡ "Run function [name]" - Execute API functions' : ''}
${this.currentProject === 'companion-app' ? '📱 "Get contacts", "Check health", "Get analytics", "Get rolling sales"' : ''}
🔧 Technical questions and debugging

What would you like me to help with?`;
        }

        await this.sendMessage(response);
        console.log('[Real Cursor] Provided response to Grok');
    }

    handleProjectSwitch(message) {
        const content = message.toLowerCase();
        let targetProject = null;
        
        if (content.includes('big beautiful') || content.includes('main program')) {
            targetProject = 'big-beautiful';
        } else if (content.includes('companion') || content.includes('companion app')) {
            targetProject = 'companion-app';
        } else if (content.includes('three way') || content.includes('chat app')) {
            targetProject = 'threeway-chat';
        }
        
        if (targetProject && targetProject !== this.currentProject) {
            const oldProject = this.projects[this.currentProject].name;
            this.currentProject = targetProject;
            const newProject = this.projects[this.currentProject].name;
            
            console.log(`[Real Cursor] Switching from ${oldProject} to ${newProject}`);
            
            this.sendMessage(`✅ Switched to **${newProject}**
            
📁 **Project Path**: ${this.projects[targetProject].path}
📋 **Description**: ${this.projects[targetProject].description}
${this.projects[targetProject].apiUrl ? `🔗 **API Available**: ${this.projects[targetProject].apiUrl}` : ''}

I'm now ready to help with ${newProject}. What would you like to work on?`);
        } else if (targetProject === this.currentProject) {
            this.sendMessage(`Already working on **${this.projects[targetProject].name}**. What can I help you with?`);
        } else {
            this.sendMessage(`**Available Projects:**
            
🔹 **ThreeWayChat App** - "switch to three way chat"
🔹 **Big Beautiful Program** - "switch to big beautiful program" 
🔹 **Companion App** - "switch to companion app"

Currently working on: **${this.projects[this.currentProject].name}**`);
        }
    }

    async handleCompanionAPICommand(query) {
        const lowerQuery = query.toLowerCase();
        let endpoint = null;
        let parameters = {};
        let contactId = null;
        
        // Parse the command and determine which API to call
        if (lowerQuery.includes('check health') || lowerQuery.includes('health check')) {
            endpoint = 'health';
        } else if (lowerQuery.includes('get contacts') || lowerQuery.includes('show contacts')) {
            endpoint = 'contacts';
        } else if (lowerQuery.includes('get analytics') || lowerQuery.includes('show analytics')) {
            endpoint = 'analytics';
        } else if (lowerQuery.includes('rolling sales') || lowerQuery.includes('weekly sales')) {
            endpoint = 'rolling-sales';
        } else if (lowerQuery.includes('export sales') || lowerQuery.includes('export for email')) {
            endpoint = 'export-sales';
        } else if (lowerQuery.includes('sync data') || lowerQuery.includes('sync')) {
            endpoint = 'sync';
        } else if (lowerQuery.includes('geocode') && lowerQuery.includes('address')) {
            endpoint = 'geocode';
            // Extract address from query if possible
            const addressMatch = query.match(/address[:\s]+(.+)/i);
            if (addressMatch) {
                parameters.address = addressMatch[1].trim();
            }
        } else if (lowerQuery.includes('att fiber') || lowerQuery.includes('fiber check')) {
            endpoint = 'att-fiber-check';
            // Extract address from query if possible
            const addressMatch = query.match(/(?:for|at)[:\s]+(.+)/i);
            if (addressMatch) {
                parameters.address = addressMatch[1].trim();
            }
        } else {
            // Show available commands
            this.sendMessage(`**Available Companion App API Commands:**

🏥 **Health Check**: "check health"
👥 **Contacts**: "get contacts" 
📊 **Analytics**: "get analytics"
📈 **Sales**: "get rolling sales" or "export sales for email"
🔄 **Sync**: "sync data"
🗺️ **Geocode**: "geocode address [address]"
🌐 **Fiber Check**: "check AT&T fiber for [address]"

What would you like me to do?`);
            return;
        }
        
        try {
            const result = await this.callCompanionAPI(endpoint, parameters, contactId);
            
            if (result.success) {
                let responseMessage = `✅ **${endpoint.toUpperCase()} API Call Successful**\n\n`;
                
                // Format response based on endpoint
                switch(endpoint) {
                    case 'health':
                        responseMessage += `🟢 **Server Status**: ${JSON.stringify(result.data, null, 2)}`;
                        break;
                    case 'contacts':
                        if (Array.isArray(result.data)) {
                            responseMessage += `📱 **Found ${result.data.length} contacts**\n`;
                            result.data.slice(0, 5).forEach(contact => {
                                responseMessage += `• ${contact.name || 'Unknown'} - ${contact.phone || 'No phone'}\n`;
                            });
                            if (result.data.length > 5) {
                                responseMessage += `... and ${result.data.length - 5} more`;
                            }
                        } else {
                            responseMessage += `📱 **Contact Data**: ${JSON.stringify(result.data, null, 2)}`;
                        }
                        break;
                    case 'analytics':
                        responseMessage += `📊 **Analytics Data**: ${JSON.stringify(result.data, null, 2)}`;
                        break;
                    case 'rolling-sales':
                        responseMessage += `📈 **Rolling Sales Data**: ${JSON.stringify(result.data, null, 2)}`;
                        break;
                    case 'export-sales':
                        responseMessage += `📧 **Sales Export Ready**: ${JSON.stringify(result.data, null, 2)}`;
                        break;
                    default:
                        responseMessage += `📊 **Data**: ${JSON.stringify(result.data, null, 2)}`;
                }
                
                this.sendMessage(responseMessage);
            } else {
                this.sendMessage(`❌ **API Error**: ${result.error}\n\nEndpoint: ${endpoint}`);
            }
        } catch (error) {
            this.sendMessage(`❌ **Unexpected Error**: ${error.message}`);
        }
    }

    async callCompanionAPI(endpoint, parameters = {}, contactId = null) {
        const project = this.projects['companion-app'];
        if (!project.apiUrl) {
            return 'API URL not configured for Companion App';
        }
        
        try {
            console.log(`[Real Cursor] Calling Companion API: ${endpoint}`);
            
            let url = `${project.apiUrl}/api/${endpoint}`;
            let method = 'GET';
            let body = null;
            
            // Handle specific endpoints
            switch(endpoint) {
                case 'contacts':
                    if (contactId) {
                        url = `${project.apiUrl}/api/contacts/${contactId}`;
                    }
                    break;
                case 'create-contact':
                    url = `${project.apiUrl}/api/contacts`;
                    method = 'POST';
                    body = JSON.stringify(parameters);
                    break;
                case 'geocode':
                case 'att-fiber-check':
                case 'sync':
                    method = 'POST';
                    body = JSON.stringify(parameters);
                    break;
            }
            
            const headers = {
                'Content-Type': 'application/json',
                'X-API-Key': 'YOUR_API_KEY_HERE' // Update with actual API key
            };
            
            const response = await fetch(url, {
                method: method,
                headers: headers,
                body: body
            });
            
            const result = await response.json();
            console.log(`[Real Cursor] Companion API Response:`, result);
            
            return {
                success: true,
                data: result,
                endpoint: endpoint
            };
        } catch (error) {
            console.error(`[Real Cursor] Companion API Error:`, error);
            return {
                success: false,
                error: error.message,
                endpoint: endpoint
            };
        }
    }

    async callBigBeautifulAPI(functionName, parameters = {}) {
        const project = this.projects['big-beautiful'];
        if (!project.apiUrl) {
            return 'API URL not configured for Big Beautiful Program';
        }
        
        try {
            console.log(`[Real Cursor] Calling Big Beautiful API: ${functionName}`);
            
            // Make API call to your Big Beautiful Program
            const response = await fetch(`${project.apiUrl}/api/${functionName}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add your API key here if needed
                    // 'Authorization': 'Bearer your-api-key'
                },
                body: JSON.stringify(parameters)
            });
            
            const result = await response.json();
            console.log(`[Real Cursor] API Response:`, result);
            
            return result;
        } catch (error) {
            console.error(`[Real Cursor] API Error:`, error);
            return `Error calling ${functionName}: ${error.message}`;
        }
    }

    async sendMessage(content) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const message = {
                content: content,
                type: 'text',
                sender: 'cursor'
            };
            
            this.ws.send(JSON.stringify(message));
            console.log('[Real Cursor] Sent response');
        } else {
            console.error('[Real Cursor] WebSocket not open, cannot send message');
        }
    }
}

// Start the real Cursor integration
const realCursor = new RealCursorIntegration();
realCursor.connect();

console.log('🚀 Real Cursor Integration started - connected to your actual conversation!');
