//
//  ContentView.swift
//  Voice control
//
//  Created by Matthew Caison on 8/22/25.
//

import SwiftUI
import Speech
import AVFoundation

struct Message: Identifiable, Codable {
    let id = UUID()
    let sender: String
    let content: String
    let messageType: String
    let timestamp: String
    
    enum CodingKeys: String, CodingKey {
        case sender, content, messageType = "message_type", timestamp
    }
}

struct ContentView: View {
    @State private var isRecording = false
    @State private var transcribedText = ""
    @State private var isListening = false
    @State private var recordingTime: TimeInterval = 0
    @State private var timer: Timer?
    @State private var showingPermissionAlert = false
    @State private var permissionAlertMessage = ""
    
    // WebSocket and conversation state
    @State private var webSocket: URLSessionWebSocketTask?
    @State private var isConnected = false
    @State private var messages: [Message] = []
    @State private var serverIP = "192.168.84.130" // Your server IP
    @State private var showingServerConfig = false
    @State private var connectionStatus = "Disconnected"
    
    var body: some View {
        NavigationView {
            ZStack {
                // Background gradient
                LinearGradient(
                    gradient: Gradient(colors: [Color.blue.opacity(0.1), Color.purple.opacity(0.1)]),
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Header with connection status
                    VStack(spacing: 10) {
                        HStack {
                            Image(systemName: isConnected ? "wifi" : "wifi.slash")
                                .foregroundColor(isConnected ? .green : .red)
                            Text(connectionStatus)
                                .font(.caption)
                                .foregroundColor(isConnected ? .green : .red)
                            Spacer()
                            Button(action: { showingServerConfig = true }) {
                                Image(systemName: "gear")
                                    .foregroundColor(.blue)
                            }
                        }
                        .padding(.horizontal)
                        
                        Text("Three-Way Chat")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.primary)
                        
                        Text("Voice • Grok AI • Cursor AI")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding(.top)
                    
                    // Messages area
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 12) {
                                ForEach(messages) { message in
                                    MessageBubble(message: message)
                                        .id(message.id)
                                }
                            }
                            .padding()
                        }
                        .onChange(of: messages.count) { _ in
                            if let lastMessage = messages.last {
                                withAnimation(.easeInOut(duration: 0.3)) {
                                    proxy.scrollTo(lastMessage.id, anchor: .bottom)
                                }
                            }
                        }
                    }
                    
                    // Recording area
                    VStack(spacing: 15) {
                        // Recording timer
                        if isRecording {
                            Text(timeString(from: recordingTime))
                                .font(.title2)
                                .fontWeight(.medium)
                                .foregroundColor(.red)
                                .padding(.horizontal, 20)
                                .padding(.vertical, 10)
                                .background(Color.red.opacity(0.1))
                                .cornerRadius(15)
                        }
                        
                        // Main recording button
                        Button(action: toggleRecording) {
                            ZStack {
                                Circle()
                                    .fill(isRecording ? Color.red : Color.blue)
                                    .frame(width: 80, height: 80)
                                    .shadow(color: isRecording ? .red.opacity(0.3) : .blue.opacity(0.3), radius: 10, x: 0, y: 5)
                                
                                Image(systemName: isRecording ? "stop.fill" : "mic.fill")
                                    .font(.system(size: 30, weight: .medium))
                                    .foregroundColor(.white)
                            }
                        }
                        .scaleEffect(isRecording ? 1.1 : 1.0)
                        .animation(.easeInOut(duration: 0.2), value: isRecording)
                        .disabled(!isConnected)
                        
                        // Status indicators
                        HStack(spacing: 20) {
                            StatusIndicator(
                                title: "Connection",
                                isActive: isConnected,
                                icon: "wifi"
                            )
                            
                            StatusIndicator(
                                title: "Recording",
                                isActive: isRecording,
                                icon: "mic.fill"
                            )
                        }
                    }
                    .padding()
                }
            }
        }
        .alert("Permission Required", isPresented: $showingPermissionAlert) {
            Button("OK") { }
        } message: {
            Text(permissionAlertMessage)
        }
        .sheet(isPresented: $showingServerConfig) {
            ServerConfigView(serverIP: $serverIP, isConnected: $isConnected, connectionStatus: $connectionStatus)
        }
        .onAppear {
            requestPermissions()
            connectToServer()
        }
    }
    
    private func toggleRecording() {
        if isRecording {
            stopRecording()
        } else {
            startRecording()
        }
    }
    
    private func startRecording() {
        isRecording = true
        isListening = true
        recordingTime = 0
        transcribedText = ""
        
        // Start timer
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
            recordingTime += 0.1
        }
        
        // Start speech recognition
        startSpeechRecognition()
    }
    
    private func stopRecording() {
        isRecording = false
        isListening = false
        timer?.invalidate()
        timer = nil
        
        // Stop speech recognition
        stopSpeechRecognition()
        
        // Send transcribed text to server
        if !transcribedText.isEmpty {
            sendMessageToServer(transcribedText)
        }
    }
    
    private func startSpeechRecognition() {
        // Initialize speech recognition
        let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
        let request = SFSpeechAudioBufferRecognitionRequest()
        
        // Configure audio session
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("Audio session error: \(error)")
        }
        
        // Start recognition
        speechRecognizer?.recognitionTask(with: request) { result, error in
            if let result = result {
                DispatchQueue.main.async {
                    self.transcribedText = result.bestTranscription.formattedString
                }
            }
        }
    }
    
    private func stopSpeechRecognition() {
        // Stop speech recognition
    }
    
    private func sendMessageToServer(_ content: String) {
        let message = [
            "content": content,
            "type": "text"
        ]
        
        if let data = try? JSONSerialization.data(withJSONObject: message),
           let jsonString = String(data: data, encoding: .utf8) {
            webSocket?.send(.string(jsonString)) { error in
                if let error = error {
                    print("Error sending message: \(error)")
                }
            }
        }
    }
    
    private func connectToServer() {
        let url = URL(string: "ws://\(serverIP):8000/ws/phone")!
        let session = URLSession(configuration: .default)
        webSocket = session.webSocketTask(with: url)
        
        webSocket?.resume()
        connectionStatus = "Connecting..."
        
        // Start receiving messages
        receiveMessage()
    }
    
    private func receiveMessage() {
        webSocket?.receive { result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    if let data = text.data(using: .utf8),
                       let messageData = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                        
                        DispatchQueue.main.async {
                            if messageData["type"] as? String == "system" {
                                self.connectionStatus = "Connected"
                                self.isConnected = true
                            } else if let sender = messageData["sender"] as? String,
                                      let content = messageData["content"] as? String {
                                
                                let message = Message(
                                    sender: sender,
                                    content: content,
                                    messageType: messageData["message_type"] as? String ?? "text",
                                    timestamp: messageData["timestamp"] as? String ?? ""
                                )
                                self.messages.append(message)
                            }
                        }
                    }
                case .data(let data):
                    print("Received data: \(data)")
                @unknown default:
                    break
                }
                
                // Continue receiving messages
                self.receiveMessage()
                
            case .failure(let error):
                DispatchQueue.main.async {
                    self.connectionStatus = "Connection failed"
                    self.isConnected = false
                }
                print("WebSocket error: \(error)")
            }
        }
    }
    
    private func timeString(from timeInterval: TimeInterval) -> String {
        let minutes = Int(timeInterval) / 60
        let seconds = Int(timeInterval) % 60
        let tenths = Int((timeInterval * 10).truncatingRemainder(dividingBy: 10))
        return String(format: "%02d:%02d.%01d", minutes, seconds, tenths)
    }
    
    private func requestPermissions() {
        // Request microphone permission using the new API
        if #available(iOS 17.0, *) {
            AVAudioApplication.requestRecordPermission { granted in
                DispatchQueue.main.async {
                    if !granted {
                        permissionAlertMessage = "Microphone access is required for voice control."
                        showingPermissionAlert = true
                    }
                }
            }
        } else {
            // Fallback for older iOS versions
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                DispatchQueue.main.async {
                    if !granted {
                        permissionAlertMessage = "Microphone access is required for voice control."
                        showingPermissionAlert = true
                    }
                }
            }
        }
        
        // Request speech recognition permission
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                if status != .authorized {
                    permissionAlertMessage = "Speech recognition access is required for voice control."
                    showingPermissionAlert = true
                }
            }
        }
    }
}

struct MessageBubble: View {
    let message: Message
    
    var body: some View {
        HStack {
            if message.sender == "phone" {
                Spacer()
            }
            
            VStack(alignment: message.sender == "phone" ? .trailing : .leading, spacing: 4) {
                HStack {
                    if message.sender != "phone" {
                        Text(message.sender.capitalized)
                            .font(.caption)
                            .foregroundColor(senderColor)
                            .fontWeight(.semibold)
                    }
                    Spacer()
                    if message.sender == "phone" {
                        Text(message.sender.capitalized)
                            .font(.caption)
                            .foregroundColor(senderColor)
                            .fontWeight(.semibold)
                    }
                }
                
                Text(message.content)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(bubbleColor)
                    .foregroundColor(textColor)
                    .cornerRadius(16)
                    .frame(maxWidth: .infinity * 0.8, alignment: message.sender == "phone" ? .trailing : .leading)
            }
            
            if message.sender != "phone" {
                Spacer()
            }
        }
    }
    
    private var senderColor: Color {
        switch message.sender {
        case "phone": return .blue
        case "grok": return .purple
        case "cursor": return .green
        default: return .gray
        }
    }
    
    private var bubbleColor: Color {
        switch message.sender {
        case "phone": return .blue
        case "grok": return .purple.opacity(0.2)
        case "cursor": return .green.opacity(0.2)
        default: return .gray.opacity(0.2)
        }
    }
    
    private var textColor: Color {
        switch message.sender {
        case "phone": return .white
        default: return .primary
        }
    }
}

struct ServerConfigView: View {
    @Binding var serverIP: String
    @Binding var isConnected: Bool
    @Binding var connectionStatus: String
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Server Configuration")
                    .font(.title2)
                    .fontWeight(.bold)
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("Server IP Address")
                        .font(.headline)
                    
                    TextField("Enter server IP", text: $serverIP)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.numbersAndPunctuation)
                }
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("Connection Status")
                        .font(.headline)
                    
                    HStack {
                        Image(systemName: isConnected ? "wifi" : "wifi.slash")
                            .foregroundColor(isConnected ? .green : .red)
                        Text(connectionStatus)
                            .foregroundColor(isConnected ? .green : .red)
                    }
                }
                
                Button("Test Connection") {
                    // Test connection logic
                }
                .buttonStyle(.borderedProminent)
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(trailing: Button("Done") { dismiss() })
        }
    }
}

struct StatusIndicator: View {
    let title: String
    let isActive: Bool
    let icon: String
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(isActive ? .green : .gray)
            
            Text(title)
                .font(.caption)
                .foregroundColor(isActive ? .green : .gray)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(isActive ? Color.green.opacity(0.1) : Color.gray.opacity(0.1))
        )
    }
}

#Preview {
    ContentView()
}
