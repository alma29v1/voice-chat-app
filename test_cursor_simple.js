const WebSocket = require('ws');

console.log('🧪 Testing cursor with NON-programming message...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');
const cursorWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/cursor');

let phoneConnected = false;
let cursorConnected = false;

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    phoneConnected = true;
    startTest();
});

cursorWs.on('open', function open() {
    console.log('💻 Cursor connected');
    cursorConnected = true;
    startTest();
});

function startTest() {
    if (phoneConnected && cursorConnected) {
        console.log('\n🎯 Testing cursor → phone with simple message...\n');
        
        setTimeout(() => {
            console.log('💻➡️ Cursor: "The weather is nice today"');
            cursorWs.send(JSON.stringify({
                content: "The weather is nice today",
                type: "text",
                sender: "cursor"
            }));
        }, 1000);
        
        setTimeout(() => {
            console.log('\n🔌 Test complete');
            phoneWs.close();
            cursorWs.close();
            process.exit(0);
        }, 5000);
    }
}

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    if (parsed.sender === 'cursor') {
        console.log('🎉 📱 Phone RECEIVED Cursor message:', parsed.content);
    } else {
        console.log(`📱 Phone received [${parsed.type}] ${parsed.sender || 'system'}: "${parsed.content}"`);
    }
});

cursorWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    console.log(`💻 Cursor received [${parsed.type}] ${parsed.sender || 'system'}: "${parsed.content}"`);
});

phoneWs.on('error', (err) => console.log('❌ Phone error:', err.message));
cursorWs.on('error', (err) => console.log('❌ Cursor error:', err.message));
