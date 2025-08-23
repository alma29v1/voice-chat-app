import SwiftUI

struct ContentView: View {
    @StateObject private var chatManager = ChatManager()
    @State private var messageText = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header with connection status
                VStack(spacing: 8) {
                    HStack {
                        Text("ThreeWayChat")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Spacer()
                        
                        Circle()
                            .fill(chatManager.isConnected ? Color.green : Color.red)
                            .frame(width: 8, height: 8)
                    }
                    
                    HStack {
                        Text(chatManager.connectionStatus)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        Text("Server: \(chatManager.serverIP)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal)
                .padding(.vertical, 8)
                .background(Color(.systemBackground))
                .shadow(color: .black.opacity(0.1), radius: 1, x: 0, y: 1)
                
                // Messages list
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(chatManager.messages) { message in
                            MessageBubble(message: message)
                        }
                    }
                    .padding(.horizontal)
                    .padding(.top, 8)
                }
                .background(Color(.systemGroupedBackground))
                
                // Input area
                VStack(spacing: 0) {
                    Divider()
                    
                    HStack(spacing: 12) {
                        TextField("Type a message...", text: $messageText, axis: .vertical)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .lineLimit(1...4)
                        
                        Button(action: sendMessage) {
                            Image(systemName: "paperplane.fill")
                                .foregroundColor(.white)
                                .padding(8)
                                .background(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? Color.gray : Color.blue)
                                .clipShape(Circle())
                        }
                        .disabled(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || !chatManager.isConnected)
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 12)
                    .background(Color(.systemBackground))
                }
            }
            .navigationTitle("ThreeWayChat")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    HStack(spacing: 4) {
                        Circle()
                            .fill(chatManager.isConnected ? Color.green : Color.red)
                            .frame(width: 6, height: 6)
                        
                        Text(chatManager.isConnected ? "Connected" : "Disconnected")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(chatManager.isConnected ? "Disconnect" : "Connect") {
                        if chatManager.isConnected {
                            chatManager.disconnect()
                        } else {
                            chatManager.connect()
                        }
                    }
                    .foregroundColor(chatManager.isConnected ? .red : .green)
                }
            }
        }
        .onAppear {
            // Auto-connect when app appears
            if !chatManager.isConnected {
                chatManager.connect()
            }
        }
    }
    
    private func sendMessage() {
        let trimmedMessage = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedMessage.isEmpty else { return }
        
        chatManager.sendMessage(trimmedMessage)
        messageText = ""
    }
}

struct MessageBubble: View {
    let message: ChatManager.ChatMessage
    
    private var isFromPhone: Bool {
        message.sender == "phone"
    }
    
    private var bubbleColor: Color {
        switch message.sender {
        case "phone":
            return .blue
        case "cursor":
            return .green
        case "grok":
            return .purple
        default:
            return .gray
        }
    }
    
    private var senderName: String {
        switch message.sender {
        case "phone":
            return "You"
        case "cursor":
            return "Cursor"
        case "grok":
            return "Grok AI"
        default:
            return message.sender.capitalized
        }
    }
    
    var body: some View {
        HStack {
            if isFromPhone {
                Spacer(minLength: 60)
            }
            
            VStack(alignment: isFromPhone ? .trailing : .leading, spacing: 4) {
                HStack {
                    if !isFromPhone {
                        Text(senderName)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    if isFromPhone {
                        Text(senderName)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Text(message.content)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(bubbleColor.opacity(isFromPhone ? 1.0 : 0.1))
                    .foregroundColor(isFromPhone ? .white : .primary)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    .textSelection(.enabled)
            }
            
            if !isFromPhone {
                Spacer(minLength: 60)
            }
        }
    }
}

#Preview {
    ContentView()
}
