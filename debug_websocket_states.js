const WebSocket = require('ws');

console.log('🔍 Debugging WebSocket states and message sending...');

const phoneWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/phone');
const cursorWs = new WebSocket('wss://voice-chat-app-cc40.onrender.com/ws/cursor');

phoneWs.on('open', function open() {
    console.log(`📱 Phone connected - ReadyState: ${phoneWs.readyState}`);
    testAfterConnections();
});

cursorWs.on('open', function open() {
    console.log(`💻 Cursor connected - ReadyState: ${cursorWs.readyState}`);
    testAfterConnections();
});

let connectionsReady = 0;

function testAfterConnections() {
    connectionsReady++;
    if (connectionsReady === 2) {
        console.log('\n🧪 Both connections ready - testing message sending...\n');
        
        setTimeout(() => {
            console.log(`💻 Cursor ReadyState before send: ${cursorWs.readyState} (1=OPEN)`);
            
            const message = {
                content: "Test message from cursor",
                type: "text",
                sender: "cursor"
            };
            
            console.log('💻➡️ Cursor sending:', JSON.stringify(message));
            
            try {
                cursorWs.send(JSON.stringify(message));
                console.log('✅ Message sent successfully');
            } catch (error) {
                console.log('❌ Error sending message:', error.message);
            }
            
            console.log(`💻 Cursor ReadyState after send: ${cursorWs.readyState}`);
        }, 1000);
        
        setTimeout(() => {
            console.log('\n📊 Final WebSocket states:');
            console.log(`📱 Phone: ${phoneWs.readyState}`);
            console.log(`💻 Cursor: ${cursorWs.readyState}`);
            
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

phoneWs.on('close', () => console.log('📱 Phone connection closed'));
cursorWs.on('close', () => console.log('💻 Cursor connection closed'));
