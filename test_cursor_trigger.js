const WebSocket = require('ws');

console.log('🧪 Testing cursor response trigger...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    
    // Send a message that should definitely trigger cursor response
    setTimeout(() => {
        console.log('📱➡️ Phone: "I need help debugging my JavaScript code"');
        phoneWs.send(JSON.stringify({
            content: "I need help debugging my JavaScript code",
            type: "text",
            sender: "phone"
        }));
    }, 2000);
    
    // Send another trigger message
    setTimeout(() => {
        console.log('📱➡️ Phone: "My function returns undefined, can you help?"');
        phoneWs.send(JSON.stringify({
            content: "My function returns undefined, can you help?",
            type: "text",
            sender: "phone"
        }));
    }, 8000);
    
    // Check connections
    setTimeout(() => {
        console.log('\n🔍 Final connection check...');
        fetch('https://voice-chat-app-cc40.onrender.com/')
            .then(r => r.json())
            .then(data => {
                console.log('📊 Final status:', data);
            })
            .catch(e => console.log('❌ Status check failed'));
    }, 15000);
    
    // Close after test
    setTimeout(() => {
        console.log('\n✅ Cursor trigger test complete!');
        phoneWs.close();
        process.exit(0);
    }, 18000);
});

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    const timestamp = new Date().toLocaleTimeString();
    
    if (parsed.sender === 'cursor') {
        console.log(`🎉 [${timestamp}] 📱 Phone RECEIVED Cursor response:`);
        console.log(`   "${parsed.content.substring(0, 100)}..."`);
    } else {
        console.log(`[${timestamp}] 📱 Phone received [${parsed.type}] ${parsed.sender || 'system'}: "${parsed.content}"`);
    }
});

phoneWs.on('error', (err) => console.log('❌ Phone error:', err.message));
phoneWs.on('close', () => console.log('📱 Phone connection closed'));
