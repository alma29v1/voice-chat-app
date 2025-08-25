const WebSocket = require('ws');

console.log('🧪 Testing simple message routing...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');
const cursorWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/cursor');

let phoneConnected = false;
let cursorConnected = false;

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    phoneConnected = true;
    runTest();
});

cursorWs.on('open', function open() {
    console.log('💻 Cursor connected');
    cursorConnected = true;
    runTest();
});

function runTest() {
    if (phoneConnected && cursorConnected) {
        console.log('\n🎯 Testing simple non-programming messages...\n');
        
        setTimeout(() => {
            console.log('💻➡️ Cursor: "Good morning! How are you?"');
            cursorWs.send(JSON.stringify({
                content: "Good morning! How are you?",
                type: "text",
                sender: "cursor"
            }));
        }, 1000);
        
        setTimeout(() => {
            console.log('📱➡️ Phone: "I am doing well, thanks!"');
            phoneWs.send(JSON.stringify({
                content: "I am doing well, thanks!",
                type: "text",
                sender: "phone"
            }));
        }, 3000);
        
        setTimeout(() => {
            console.log('\n🔌 Test complete');
            phoneWs.close();
            cursorWs.close();
            process.exit(0);
        }, 7000);
    }
}

phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    if (parsed.sender === 'cursor') {
        console.log('✅ 📱 Phone RECEIVED Cursor message:', parsed.content);
    } else if (parsed.sender === 'phone') {
        console.log('📱 Phone received own message (echo):', parsed.content);
    } else {
        console.log('📱 Phone received:', parsed.type, parsed.content);
    }
});

cursorWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    if (parsed.sender === 'phone') {
        console.log('✅ 💻 Cursor RECEIVED Phone message:', parsed.content);
    } else if (parsed.sender === 'cursor') {
        console.log('💻 Cursor received own message (echo):', parsed.content);
    } else {
        console.log('💻 Cursor received:', parsed.type, parsed.content);
    }
});

phoneWs.on('error', (err) => console.log('❌ Phone error:', err.message));
cursorWs.on('error', (err) => console.log('❌ Cursor error:', err.message));
