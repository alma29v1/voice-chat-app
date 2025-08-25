const vscode = require('vscode');
const WebSocket = require('ws');

class ThreeWayChatExtension {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.statusBarItem = null;
        this.currentModel = 'grok-2-mini'; // Default model
        this.serverURL = 'voice-chat-app-cc40.onrender.com';
        
        // Available Grok models with descriptions
        this.grokModels = {
            'grok-2-mini': 'Grok 2 Mini - Fast, efficient (cheapest)',
            'grok-2': 'Grok 2 - Balanced performance and cost',
            'grok-2-1212': 'Grok 2 (Dec 2024) - Latest stable version',
            'grok-beta': 'Grok Beta - Experimental features',
            'grok-vision-beta': 'Grok Vision Beta - With image understanding'
        };
    }

    activate(context) {
        console.log('ThreeWay Chat extension activated');

        // Create status bar item
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.text = '$(radio-tower) ThreeWay: Disconnected';
        this.statusBarItem.tooltip = 'Click to connect to ThreeWay Chat';
        this.statusBarItem.command = 'threeway.connect';
        this.statusBarItem.show();

        // Register commands
        const connectCommand = vscode.commands.registerCommand('threeway.connect', () => {
            if (!this.isConnected) {
                this.connect();
            } else {
                this.disconnect();
            }
        });

        const disconnectCommand = vscode.commands.registerCommand('threeway.disconnect', () => {
            this.disconnect();
        });

        const selectModelCommand = vscode.commands.registerCommand('threeway.selectModel', () => {
            this.selectModel();
        });

        // Watch for active editor changes
        const editorChangeListener = vscode.window.onDidChangeActiveTextEditor(() => {
            if (this.isConnected) {
                this.sendCurrentContext();
            }
        });

        // Watch for text changes
        const textChangeListener = vscode.workspace.onDidChangeTextDocument(() => {
            if (this.isConnected) {
                // Debounce text changes to avoid spam
                clearTimeout(this.textChangeTimeout);
                this.textChangeTimeout = setTimeout(() => {
                    this.sendCurrentContext();
                }, 2000);
            }
        });

        context.subscriptions.push(
            connectCommand,
            disconnectCommand, 
            selectModelCommand,
            editorChangeListener,
            textChangeListener,
            this.statusBarItem
        );
    }

    async connect() {
        try {
            console.log('Connecting to ThreeWay Chat server...');
            this.statusBarItem.text = '$(sync~spin) ThreeWay: Connecting...';
            
            this.ws = new WebSocket(`wss://${this.serverURL}/ws/cursor`);
            
            this.ws.on('open', () => {
                this.isConnected = true;
                this.statusBarItem.text = `$(radio-tower) ThreeWay: Connected (${this.currentModel})`;
                this.statusBarItem.command = 'threeway.disconnect';
                this.statusBarItem.tooltip = 'Connected to ThreeWay Chat - Click to disconnect';
                
                vscode.window.showInformationMessage('Connected to ThreeWay Chat! Your voice conversation can now access this Cursor window.');
                
                // Send initial context
                this.sendCurrentContext();
                
                // Send connection message
                this.sendMessage('Real Cursor connected from VS Code extension - can now read active window content');
            });

            this.ws.on('message', (data) => {
                this.handleMessage(data);
            });

            this.ws.on('close', () => {
                this.isConnected = false;
                this.statusBarItem.text = '$(radio-tower) ThreeWay: Disconnected';
                this.statusBarItem.command = 'threeway.connect';
                this.statusBarItem.tooltip = 'Click to connect to ThreeWay Chat';
                console.log('Disconnected from ThreeWay Chat');
            });

            this.ws.on('error', (error) => {
                console.error('WebSocket error:', error);
                vscode.window.showErrorMessage(`ThreeWay Chat connection error: ${error.message}`);
                this.disconnect();
            });

        } catch (error) {
            console.error('Connection failed:', error);
            vscode.window.showErrorMessage(`Failed to connect to ThreeWay Chat: ${error.message}`);
            this.statusBarItem.text = '$(radio-tower) ThreeWay: Connection Failed';
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.statusBarItem.text = '$(radio-tower) ThreeWay: Disconnected';
        this.statusBarItem.command = 'threeway.connect';
        this.statusBarItem.tooltip = 'Click to connect to ThreeWay Chat';
        vscode.window.showInformationMessage('Disconnected from ThreeWay Chat');
    }

    async selectModel() {
        const modelOptions = Object.keys(this.grokModels).map(key => ({
            label: key,
            description: this.grokModels[key],
            picked: key === this.currentModel
        }));

        const selected = await vscode.window.showQuickPick(modelOptions, {
            placeHolder: 'Select Grok AI model for voice conversation',
            canPickMany: false
        });

        if (selected) {
            this.currentModel = selected.label;
            if (this.isConnected) {
                this.statusBarItem.text = `$(radio-tower) ThreeWay: Connected (${this.currentModel})`;
                
                // Send model change to server
                this.sendMessage(`Model changed to ${this.currentModel}`);
                
                vscode.window.showInformationMessage(`Switched to ${selected.label}: ${selected.description}`);
            } else {
                vscode.window.showInformationMessage(`Selected ${selected.label}. Connect to ThreeWay Chat to use it.`);
            }
        }
    }

    sendCurrentContext() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }

        const document = editor.document;
        const selection = editor.selection;
        
        // Get current file info
        const fileName = document.fileName;
        const language = document.languageId;
        const lineCount = document.lineCount;
        
        // Get selected text or current line
        let contextText = '';
        if (!selection.isEmpty) {
            contextText = document.getText(selection);
        } else {
            // Get current line and surrounding context
            const currentLine = selection.active.line;
            const startLine = Math.max(0, currentLine - 5);
            const endLine = Math.min(lineCount - 1, currentLine + 5);
            const range = new vscode.Range(startLine, 0, endLine, 0);
            contextText = document.getText(range);
        }

        // Create context message
        const contextMessage = {
            type: 'context',
            fileName: fileName.split('/').pop(), // Just the filename
            language: language,
            lineCount: lineCount,
            currentLine: selection.active.line + 1,
            selectedText: !selection.isEmpty ? document.getText(selection) : null,
            contextText: contextText,
            model: this.currentModel
        };

        this.sendMessage(`Current context: Working in ${contextMessage.fileName} (${language}), line ${contextMessage.currentLine}/${lineCount}\n\nCurrent code:\n\`\`\`${language}\n${contextText}\n\`\`\``);
    }

    handleMessage(data) {
        try {
            const message = JSON.parse(data.toString());
            console.log('Received message:', message);

            // Handle query messages from Grok
            if (message.type === 'query' && message.sender === 'grok') {
                this.handleGrokQuery(message.content);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    }

    async handleGrokQuery(query) {
        console.log('Handling Grok query:', query);
        
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            this.sendMessage('No active editor open in Cursor');
            return;
        }

        const document = editor.document;
        const fullText = document.getText();
        const fileName = document.fileName.split('/').pop();
        const language = document.languageId;

        // Analyze the query and provide contextual response
        let response = `Looking at your ${fileName} file (${language}):\n\n`;

        if (query.toLowerCase().includes('debug') || query.toLowerCase().includes('undefined')) {
            response += `**Debug Analysis:**\n`;
            response += `- File: ${fileName} (${document.lineCount} lines)\n`;
            response += `- Language: ${language}\n`;
            
            if (fullText.includes('function')) {
                response += `- Functions detected in this file\n`;
            }
            if (fullText.includes('undefined')) {
                response += `- ⚠️ "undefined" found in code - check variable declarations and return statements\n`;
            }
            if (fullText.includes('async') && !fullText.includes('await')) {
                response += `- ⚠️ Async functions detected but no await - possible missing await\n`;
            }
            
            response += `\n**Current Context:**\n\`\`\`${language}\n${fullText.substring(0, 500)}${fullText.length > 500 ? '...' : ''}\n\`\`\``;
            
        } else if (query.toLowerCase().includes('explain') || query.toLowerCase().includes('what')) {
            response += `**Code Explanation:**\n`;
            response += `This ${language} file appears to be `;
            
            if (fileName.includes('test')) response += 'a test file';
            else if (fileName.includes('config')) response += 'a configuration file';
            else if (fileName.includes('index')) response += 'a main entry point';
            else if (language === 'javascript') response += 'a JavaScript module';
            else if (language === 'python') response += 'a Python script';
            else response += `a ${language} source file`;
            
            response += `.\n\n**Key elements:**\n`;
            if (fullText.includes('import') || fullText.includes('require')) response += `- Has imports/dependencies\n`;
            if (fullText.includes('export') || fullText.includes('module.exports')) response += `- Exports functionality\n`;
            if (fullText.includes('class ')) response += `- Contains class definitions\n`;
            if (fullText.includes('function ')) response += `- Contains functions\n`;
            
        } else {
            response += `**General Analysis:**\n`;
            response += `Currently working on ${fileName} with ${document.lineCount} lines of ${language} code.\n\n`;
            response += `Query: "${query}"\n\n`;
            response += `I can see your current code and help with specific questions about this file.`;
        }

        this.sendMessage(response);
    }

    sendMessage(content) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const message = {
                content: content,
                type: 'text',
                sender: 'cursor',
                model: this.currentModel
            };
            
            this.ws.send(JSON.stringify(message));
            console.log('Sent message to ThreeWay Chat');
        }
    }

    deactivate() {
        this.disconnect();
    }
}

let extension;

function activate(context) {
    extension = new ThreeWayChatExtension();
    extension.activate(context);
}

function deactivate() {
    if (extension) {
        extension.deactivate();
    }
}

module.exports = {
    activate,
    deactivate
};
