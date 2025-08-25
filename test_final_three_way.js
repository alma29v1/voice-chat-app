const WebSocket = require('ws');

console.log('🎯 FINAL three-way connection test...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');

phoneWs.on('open', function open() {
    console.log('📱 Phone connected to three-way chat');
    
    // Test programming question that should trigger cursor response
    setTimeout(() => {
        console.log('\n📱➡️ Phone: "I have a JavaScript error - my function returns undefined. Can someone help me debug this?"');
        phoneWs.send(JSON.stringify({
            content: "I have a JavaScript error - my function returns undefined. Can someone help me debug this?",
            type: "text",
            sender: "phone"
        }));
    }, 3000);
    
    // Keep connection open longer to see all responses
    setTimeout(() => {
        console.log('\n🔍 Checking final server status...');
        fetch('https://voice-chat-app-cc40.onrender.com/')
            .then(r => r.json())
            .then(data => {
                console.log('📊 Final server status:', data);
                console.log('\n✅ Three-way chat test completed!');
                phoneWs.close();
                process.exit(0);
            })
            .catch(e => {
                console.log('❌ Status check failed:', e.message);
                phoneWs.close();
                process.exit(0);
            });
    }, 15000);
});

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    const timestamp = new Date().toLocaleTimeString();
    
    if (parsed.sender === 'cursor') {
        console.log(`\n🎉 [${timestamp}] 📱 PHONE RECEIVED CURSOR RESPONSE:`);
        console.log(`   📝 "${parsed.content}"`);
        console.log(`   🔥 THREE-WAY CHAT IS WORKING! 🔥`);
    } else if (parsed.sender === 'grok') {
        console.log(`🤖 [${timestamp}] 📱 Phone received Grok: "${parsed.content}"`);
    } else {
        console.log(`[${timestamp}] 📱 Phone received [${parsed.type}] ${parsed.sender || 'system'}: "${parsed.content}"`);
    }
});

phoneWs.on('error', (err) => {
    console.log('❌ Phone connection error:', err.message);
});

phoneWs.on('close', () => {
    console.log('📱 Phone connection closed');
});
