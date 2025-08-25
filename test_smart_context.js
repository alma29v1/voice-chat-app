const WebSocket = require('ws');

console.log('🧠 Testing SMART CONTEXT system...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');

phoneWs.on('open', function open() {
    console.log('📱 Phone connected for smart context test');
    
    // Test 1: Debugging question (should set context type to "debugging")
    setTimeout(() => {
        console.log('\n📱➡️ Phone: "I have a JavaScript error - my function returns undefined. Can you help me debug this?"');
        phoneWs.send(JSON.stringify({
            content: "I have a JavaScript error - my function returns undefined. Can you help me debug this?",
            type: "text",
            sender: "phone"
        }));
    }, 3000);
    
    // Test 2: Follow-up question (should reference previous context)
    setTimeout(() => {
        console.log('\n📱➡️ Phone: "What else should I check?"');
        phoneWs.send(JSON.stringify({
            content: "What else should I check?",
            type: "text",
            sender: "phone"
        }));
    }, 12000);
    
    // Keep connection open longer to see responses
    setTimeout(() => {
        console.log('\n🎯 Smart context test completed!');
        phoneWs.close();
        process.exit(0);
    }, 20000);
});

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    const timestamp = new Date().toLocaleTimeString();
    
    if (parsed.sender === 'cursor') {
        console.log(`\n💻 [${timestamp}] CURSOR RESPONSE:`);
        console.log(`   "${parsed.content.substring(0, 150)}..."`);
    } else if (parsed.sender === 'grok') {
        console.log(`\n🧠 [${timestamp}] GROK WITH SMART CONTEXT:`);
        console.log(`   "${parsed.content}"`);
        
        // Check if response shows context awareness
        if (parsed.content.includes('debug') || parsed.content.includes('Cursor') || parsed.content.includes('three-way')) {
            console.log(`   ✅ SMART CONTEXT WORKING! Grok shows awareness of situation.`);
        }
    } else {
        console.log(`[${timestamp}] 📱 ${parsed.type}: "${parsed.content}"`);
    }
});

phoneWs.on('error', (err) => console.log('❌ Phone error:', err.message));
phoneWs.on('close', () => console.log('📱 Phone disconnected'));
