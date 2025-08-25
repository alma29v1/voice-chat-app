const WebSocket = require('ws');

console.log('🎯 Testing FULL three-way connection...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    
    // Test 1: Simple message
    setTimeout(() => {
        console.log('\n📱➡️ Phone: "Hello everyone!"');
        phoneWs.send(JSON.stringify({
            content: "Hello everyone!",
            type: "text",
            sender: "phone"
        }));
    }, 2000);
    
    // Test 2: Programming question for cursor
    setTimeout(() => {
        console.log('\n📱➡️ Phone: "I have a JavaScript function returning undefined, can you help debug it?"');
        phoneWs.send(JSON.stringify({
            content: "I have a JavaScript function returning undefined, can you help debug it?",
            type: "text",
            sender: "phone"
        }));
    }, 8000);
    
    // Test 3: Check connection status
    setTimeout(() => {
        console.log('\n🔍 Checking server connection status...');
        fetch('https://voice-chat-app-cc40.onrender.com/')
            .then(r => r.json())
            .then(data => {
                console.log('📊 Server status:', data);
            })
            .catch(e => console.log('❌ Status check failed:', e.message));
    }, 15000);
    
    // Close after test
    setTimeout(() => {
        console.log('\n✅ Three-way connection test complete!');
        phoneWs.close();
        process.exit(0);
    }, 20000);
});

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    const timestamp = new Date().toLocaleTimeString();
    
    if (parsed.sender === 'cursor') {
        console.log(`🎉 [${timestamp}] 📱 Phone RECEIVED Cursor response:`);
        console.log(`   "${parsed.content.substring(0, 120)}..."`);
    } else if (parsed.sender === 'grok') {
        console.log(`🤖 [${timestamp}] 📱 Phone RECEIVED Grok response: "${parsed.content}"`);
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
