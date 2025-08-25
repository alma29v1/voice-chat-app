const WebSocket = require('ws');

console.log('🧪 Testing cursor message sending...');

const cursorWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/cursor');

cursorWs.on('open', function open() {
    console.log('💻 Cursor connected');
    
    // Send a simple test message
    setTimeout(() => {
        console.log('💻➡️ Cursor: "Hello from cursor integration!"');
        
        const message = {
            content: "Hello from cursor integration!",
            type: "text",
            sender: "cursor"
        };
        
        try {
            cursorWs.send(JSON.stringify(message));
            console.log('✅ Message sent successfully');
        } catch (error) {
            console.log('❌ Error sending message:', error.message);
        }
    }, 2000);
    
    // Send a programming response
    setTimeout(() => {
        console.log('💻➡️ Cursor: Programming help response');
        
        const response = {
            content: "I can help you debug JavaScript functions! Common causes of undefined returns are missing return statements or incorrect async/await usage.",
            type: "text",
            sender: "cursor"
        };
        
        try {
            cursorWs.send(JSON.stringify(response));
            console.log('✅ Programming response sent');
        } catch (error) {
            console.log('❌ Error sending response:', error.message);
        }
    }, 5000);
    
    // Keep alive for a bit
    setTimeout(() => {
        console.log('💻 Closing cursor connection');
        cursorWs.close();
        process.exit(0);
    }, 10000);
});

cursorWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    console.log('💻 Cursor received:', parsed);
});

cursorWs.on('error', function error(err) {
    console.log('❌ Cursor WebSocket error:', err.message);
});

cursorWs.on('close', function close() {
    console.log('💻 Cursor connection closed');
});
