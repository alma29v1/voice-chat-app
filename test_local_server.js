const WebSocket = require('ws');

console.log('🧪 Testing local server with debug logging...');

// Connect to local server
const phoneWs = new WebSocket('ws://localhost:8001/ws/phone');
const cursorWs = new WebSocket('ws://localhost:8001/ws/cursor');

let phoneConnected = false;
let cursorConnected = false;

phoneWs.on('open', function open() {
    console.log('📱 Phone connected to LOCAL server');
    phoneConnected = true;
    runTest();
});

cursorWs.on('open', function open() {
    console.log('💻 Cursor connected to LOCAL server');
    cursorConnected = true;
    runTest();
});

function runTest() {
    if (phoneConnected && cursorConnected) {
        console.log('\n🎯 Testing cursor → phone routing on local server...\n');
        
        setTimeout(() => {
            console.log('💻➡️ Cursor: "Testing local message routing"');
            cursorWs.send(JSON.stringify({
                content: "Testing local message routing",
                type: "text",
                sender: "cursor"
            }));
        }, 1000);
        
        setTimeout(() => {
            console.log('\n🔌 Closing connections');
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
        console.log('📱 Phone received:', parsed.type, '-', parsed.content);
    }
});

cursorWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    console.log('💻 Cursor received:', parsed.type, '-', parsed.content);
});

phoneWs.on('error', (err) => console.log('❌ Phone error:', err.message));
cursorWs.on('error', (err) => console.log('❌ Cursor error:', err.message));
