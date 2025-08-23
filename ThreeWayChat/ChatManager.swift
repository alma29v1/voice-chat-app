import Foundation
import Combine

class ChatManager: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isConnected = false
    @Published var connectionStatus = "Disconnected"
    @Published var serverIP = "192.168.1.100" // Default IP, will be configurable
    
    private var webSocket: URLSessionWebSocketTask?
    private var timer: Timer?
    
    struct ChatMessage: Identifiable, Codable {
        let id = UUID()
        let sender: String
        let content: String
        let messageType: String
        let timestamp: String
        
        enum CodingKeys: String, CodingKey {
            case sender, content, messageType = "message_type", timestamp
        }
    }
    
    struct WebSocketMessage: Codable {
        let type: String
        let sender: String?
        let content: String
        let messageType: String?
        let timestamp: String?
    }
    
    func connect() {
        guard let url = URL(string: "ws://\(serverIP):8000/ws/phone") else {
            connectionStatus = "Invalid URL"
            return
        }
        
        let session = URLSession(configuration: .default)
        webSocket = session.webSocketTask(with: url)
        webSocket?.resume()
        
        connectionStatus = "Connecting..."
        receiveMessage()
        
        // Start heartbeat timer
        timer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { _ in
            self.sendHeartbeat()
        }
    }
    
    func disconnect() {
        webSocket?.cancel()
        webSocket = nil
        timer?.invalidate()
        timer = nil
        isConnected = false
        connectionStatus = "Disconnected"
    }
    
    func sendMessage(_ content: String) {
        let message = WebSocketMessage(
            type: "message",
            sender: "phone",
            content: content,
            messageType: "text",
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        sendWebSocketMessage(message)
        
        // Add message to local array immediately
        let chatMessage = ChatMessage(
            sender: "phone",
            content: content,
            messageType: "text",
            timestamp: message.timestamp ?? ""
        )
        
        DispatchQueue.main.async {
            self.messages.append(chatMessage)
        }
    }
    
    private func sendWebSocketMessage(_ message: WebSocketMessage) {
        guard let webSocket = webSocket else { return }
        
        do {
            let data = try JSONEncoder().encode(message)
            let string = String(data: data, encoding: .utf8) ?? ""
            let wsMessage = URLSessionWebSocketTask.Message.string(string)
            
            webSocket.send(wsMessage) { error in
                if let error = error {
                    print("WebSocket send error: \(error)")
                    DispatchQueue.main.async {
                        self.connectionStatus = "Send error: \(error.localizedDescription)"
                    }
                }
            }
        } catch {
            print("JSON encoding error: \(error)")
        }
    }
    
    private func sendHeartbeat() {
        let heartbeat = WebSocketMessage(
            type: "heartbeat",
            sender: "phone",
            content: "ping",
            messageType: "system",
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        sendWebSocketMessage(heartbeat)
    }
    
    private func receiveMessage() {
        guard let webSocket = webSocket else { return }
        
        webSocket.receive { [weak self] result in
            guard let self = self else { return }
            
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    self.handleReceivedMessage(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        self.handleReceivedMessage(text)
                    }
                @unknown default:
                    break
                }
                
                // Continue receiving messages
                self.receiveMessage()
                
            case .failure(let error):
                print("WebSocket receive error: \(error)")
                DispatchQueue.main.async {
                    self.connectionStatus = "Receive error: \(error.localizedDescription)"
                    self.isConnected = false
                }
            }
        }
    }
    
    private func handleReceivedMessage(_ text: String) {
        do {
            let data = text.data(using: .utf8) ?? Data()
            let message = try JSONDecoder().decode(WebSocketMessage.self, from: data)
            
            DispatchQueue.main.async {
                switch message.type {
                case "system":
                    self.connectionStatus = message.content
                    if message.content.contains("Connected") {
                        self.isConnected = true
                    }
                    
                case "message":
                    let chatMessage = ChatMessage(
                        sender: message.sender ?? "unknown",
                        content: message.content,
                        messageType: message.messageType ?? "text",
                        timestamp: message.timestamp ?? ""
                    )
                    self.messages.append(chatMessage)
                    
                default:
                    break
                }
            }
        } catch {
            print("JSON decoding error: \(error)")
            print("Received text: \(text)")
        }
    }
    
    func updateServerIP(_ newIP: String) {
        serverIP = newIP
        if isConnected {
            disconnect()
            connect()
        }
    }
    
    func clearMessages() {
        messages.removeAll()
    }
}
