const WebSocket = require('ws');

console.log('🔍 Testing connection stability...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    
    // Send initial test message
    setTimeout(() => {
        console.log('📱➡️ Phone: "Hello, testing connection stability"');
        phoneWs.send(JSON.stringify({
            content: "Hello, testing connection stability",
            type: "text",
            sender: "phone"
        }));
    }, 2000);
    
    // Wait 10 seconds, then check if cursor is still connected
    setTimeout(() => {
        console.log('📱➡️ Phone: "Is cursor still there?"');
        phoneWs.send(JSON.stringify({
            content: "Is cursor still there?",
            type: "text", 
            sender: "phone"
        }));
    }, 10000);
    
    // Test with a programming question that should trigger cursor response
    setTimeout(() => {
        console.log('📱➡️ Phone: "I have a JavaScript error, can you help debug it?"');
        phoneWs.send(JSON.stringify({
            content: "I have a JavaScript error, can you help debug it?",
            type: "text",
            sender: "phone"
        }));
    }, 15000);
    
    // Close after test
    setTimeout(() => {
        console.log('\n✅ Connection stability test complete');
        phoneWs.close();
        process.exit(0);
    }, 25000);
});

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    const timestamp = new Date().toLocaleTimeString();
    
    if (parsed.sender === 'cursor') {
        console.log(`✅ [${timestamp}] 📱 Phone RECEIVED Cursor response: "${parsed.content.substring(0, 100)}..."`);
    } else {
        console.log(`[${timestamp}] 📱 Phone received [${parsed.type}] ${parsed.sender || 'system'}: "${parsed.content}"`);
    }
});

phoneWs.on('error', (err) => {
    console.log('❌ Phone error:', err.message);
});

phoneWs.on('close', () => {
    console.log('📱 Phone connection closed');
});
