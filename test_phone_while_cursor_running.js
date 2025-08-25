const WebSocket = require('ws');

console.log('🧪 Testing phone connection while real cursor is running...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    
    // Send a test message that should reach cursor
    setTimeout(() => {
        console.log('📱➡️ Phone: "Hello, is anyone there?"');
        phoneWs.send(JSON.stringify({
            content: "Hello, is anyone there?",
            type: "text",
            sender: "phone"
        }));
    }, 2000);
    
    // Keep connection open to listen for responses
    setTimeout(() => {
        console.log('\n🔌 Closing phone connection');
        phoneWs.close();
        process.exit(0);
    }, 10000);
});

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    if (parsed.sender === 'cursor') {
        console.log('✅ 📱 Phone RECEIVED Cursor message:', parsed.content);
    } else {
        console.log(`📱 Phone received [${parsed.type}] ${parsed.sender || 'system'}: "${parsed.content}"`);
    }
});

phoneWs.on('error', (err) => console.log('❌ Phone error:', err.message));
phoneWs.on('close', () => console.log('📱 Phone connection closed'));
