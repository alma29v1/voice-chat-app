const WebSocket = require('ws');

console.log('🧪 Testing three-way connection...');

// Simulate phone connection
const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');
// Simulate cursor connection  
const cursorWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/cursor');

let phoneConnected = false;
let cursorConnected = false;

phoneWs.on('open', function open() {
    console.log('📱 Phone connected');
    phoneConnected = true;
    checkAndStartTest();
});

cursorWs.on('open', function open() {
    console.log('💻 Cursor connected');
    cursorConnected = true;
    checkAndStartTest();
});

function checkAndStartTest() {
    if (phoneConnected && cursorConnected) {
        console.log('\n🎯 Both connections established - starting three-way test...\n');
        
        // Test 1: Phone sends message
        setTimeout(() => {
            console.log('📱➡️ Phone: Sending message to conversation');
            phoneWs.send(JSON.stringify({
                content: "Hello everyone, can we debug my JavaScript function?",
                type: "text",
                sender: "phone"
            }));
        }, 1000);
        
        // Test 2: Cursor responds
        setTimeout(() => {
            console.log('💻➡️ Cursor: Sending response');
            cursorWs.send(JSON.stringify({
                content: "Sure! Can you share the function code?",
                type: "text", 
                sender: "cursor"
            }));
        }, 3000);
        
        // Test 3: Phone responds with code
        setTimeout(() => {
            console.log('📱➡️ Phone: Sending code example');
            phoneWs.send(JSON.stringify({
                content: "function test() { return value; } // value is undefined",
                type: "text",
                sender: "phone"
            }));
        }, 5000);
        
        // Close connections after test
        setTimeout(() => {
            console.log('\n🔌 Closing connections...');
            phoneWs.close();
            cursorWs.close();
            process.exit(0);
        }, 15000);
    }
}

// Phone message handlers
phoneWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    console.log('📱⬅️ Phone received:', parsed);
});

phoneWs.on('error', function error(err) {
    console.log('❌ Phone WebSocket error:', err.message);
});

// Cursor message handlers  
cursorWs.on('message', function message(data) {
    const parsed = JSON.parse(data.toString());
    console.log('💻⬅️ Cursor received:', parsed);
});

cursorWs.on('error', function error(err) {
    console.log('❌ Cursor WebSocket error:', err.message);
});

// Connection close handlers
phoneWs.on('close', function close() {
    console.log('📱 Phone connection closed');
});

cursorWs.on('close', function close() {
    console.log('💻 Cursor connection closed');
});
