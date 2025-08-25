const WebSocket = require('ws');

console.log('🔍 Debugging cursor message sending...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');
const cursorWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/cursor');

let phoneConnected = false;
let cursorConnected = false;

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    phoneConnected = true;
    sendTestMessage();
});

cursorWs.on('open', function open() {
    console.log('💻 Cursor connected');
    cursorConnected = true;
    sendTestMessage();
});

function sendTestMessage() {
    if (phoneConnected && cursorConnected) {
        console.log('\n🧪 Sending NON-programming message from Cursor...\n');
        
        setTimeout(() => {
            console.log('💻➡️ Cursor sending: "The weather is nice today"');
            cursorWs.send(JSON.stringify({
                content: "The weather is nice today",
                type: "text",
                sender: "cursor"
            }));
        }, 1000);
        
        setTimeout(() => {
            console.log('\n📊 Test Results:');
            console.log('- Phone should have received cursor message about weather');
            console.log('- No Grok processing should occur (non-programming message)');
            phoneWs.close();
            cursorWs.close();
            process.exit(0);
        }, 5000);
    }
}

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    console.log(`📱 Phone RX [${parsed.type}] ${parsed.sender || 'system'}: "${parsed.content}"`);
});

cursorWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    console.log(`💻 Cursor RX [${parsed.type}] ${parsed.sender || 'system'}: "${parsed.content}"`);
});

phoneWs.on('error', (err) => console.log('❌ Phone error:', err.message));
cursorWs.on('error', (err) => console.log('❌ Cursor error:', err.message));
