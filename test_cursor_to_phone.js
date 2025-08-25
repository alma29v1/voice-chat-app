const WebSocket = require('ws');

console.log('🧪 Testing Cursor → Phone routing...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');
const cursorWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/cursor');

let phoneConnected = false;
let cursorConnected = false;

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    phoneConnected = true;
    testCursorToPhone();
});

cursorWs.on('open', function open() {
    console.log('💻 Cursor connected');
    cursorConnected = true;
    testCursorToPhone();
});

function testCursorToPhone() {
    if (phoneConnected && cursorConnected) {
        console.log('\n🎯 Testing Cursor → Phone routing...\n');
        
        setTimeout(() => {
            console.log('💻➡️ Cursor sending: "Hello from Cursor!"');
            cursorWs.send(JSON.stringify({
                content: "Hello from Cursor!",
                type: "text",
                sender: "cursor"
            }));
        }, 1000);
        
        setTimeout(() => {
            console.log('\n🔌 Test complete - closing connections');
            phoneWs.close();
            cursorWs.close();
            process.exit(0);
        }, 5000);
    }
}

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    if (parsed.sender === 'cursor') {
        console.log('✅ 📱 Phone RECEIVED Cursor message:', parsed.content);
    } else {
        console.log('📱 Phone received (other):', parsed.content);
    }
});

cursorWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    console.log('💻 Cursor received:', parsed.content);
});

phoneWs.on('error', (err) => console.log('❌ Phone error:', err.message));
cursorWs.on('error', (err) => console.log('❌ Cursor error:', err.message));
