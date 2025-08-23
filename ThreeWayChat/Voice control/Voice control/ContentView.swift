//
//  ContentView.swift
//  Voice control
//
//  Created by Matthew Caison on 8/22/25.
//

import SwiftUI
import Speech
import AVFoundation
import AVFAudio

extension Date {
    var iso8601: String {
        let formatter = ISO8601DateFormatter()
        return formatter.string(from: self)
    }
}

class SpeechDelegate: NSObject, AVSpeechSynthesizerDelegate {
    @Binding var isGrokSpeaking: Bool
    
    init(isGrokSpeaking: Binding<Bool>) {
        self._isGrokSpeaking = isGrokSpeaking
    }
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            self.isGrokSpeaking = false
        }
    }
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            self.isGrokSpeaking = false
        }
    }
}

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
    @State private var serverIP = "347be302-059c-492a-90fa-6d7560469c87-00-2sc0ut3ttu7zz.riker.replit.dev:5000" // Your cloud server
    @State private var showingServerConfig = false
    @State private var connectionStatus = "Disconnected"
    
    // Speech recognition state
    @State private var speechRecognizer: SFSpeechRecognizer?
    @State private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    @State private var audioEngine: AVAudioEngine?
    
    // Text-to-speech state
    @State private var speechSynthesizer = AVSpeechSynthesizer()
    @State private var isGrokSpeaking = false
    @State private var grokResponse = ""
    @State private var speechDelegate: SpeechDelegate?
    
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
                    VStack(spacing: 15) {
                        HStack {
                            Button(action: { showingServerConfig = true }) {
                                Image(systemName: "gear")
                                    .foregroundColor(.blue)
                                    .font(.title2)
                            }
                            Spacer()
                            Text("Three-Way Chat")
                                .font(.title)
                                .fontWeight(.bold)
                                .foregroundColor(.primary)
                            Spacer()
                            Button(action: { }) {
                                Image(systemName: "info.circle")
                                    .foregroundColor(.blue)
                                    .font(.title2)
                            }
                        }
                        .padding(.horizontal)
                        
                        // Three-Way Connection Status
                        HStack(spacing: 20) {
                            // Phone/User Status
                            VStack(spacing: 8) {
                                ZStack {
                                    Circle()
                                        .fill(isConnected ? Color.blue : Color.gray)
                                        .frame(width: 50, height: 50)
                                    
                                    Image(systemName: "person.fill")
                                        .font(.title2)
                                        .foregroundColor(.white)
                                }
                                
                                Text("You")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                
                                Text(isConnected ? "Connected" : "Disconnected")
                                    .font(.caption2)
                                    .foregroundColor(isConnected ? .green : .red)
                            }
                            
                            // Connection Lines
                            VStack(spacing: 15) {
                                Rectangle()
                                    .fill(isConnected ? Color.green : Color.gray)
                                    .frame(width: 2, height: 20)
                                
                                Rectangle()
                                    .fill(isConnected ? Color.green : Color.gray)
                                    .frame(width: 2, height: 20)
                            }
                            
                            // Grok AI Status
                            VStack(spacing: 8) {
                                ZStack {
                                    Circle()
                                        .fill(isConnected ? Color.purple : Color.gray)
                                        .frame(width: 50, height: 50)
                                    
                                    Image(systemName: "brain.head.profile")
                                        .font(.title2)
                                        .foregroundColor(.white)
                                }
                                
                                Text("Grok AI")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                
                                Text(isConnected ? "Ready" : "Offline")
                                    .font(.caption2)
                                    .foregroundColor(isConnected ? .green : .red)
                            }
                            
                            // Connection Lines
                            VStack(spacing: 15) {
                                Rectangle()
                                    .fill(isConnected ? Color.green : Color.gray)
                                    .frame(width: 2, height: 20)
                                
                                Rectangle()
                                    .fill(isConnected ? Color.green : Color.gray)
                                    .frame(width: 2, height: 20)
                            }
                            
                            // Cursor AI Status
                            VStack(spacing: 8) {
                                ZStack {
                                    Circle()
                                        .fill(isConnected ? Color.green : Color.gray)
                                        .frame(width: 50, height: 50)
                                    
                                    Image(systemName: "cursorarrow.rays")
                                        .font(.title2)
                                        .foregroundColor(.white)
                                }
                                
                                Text("Cursor AI")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                
                                Text(isConnected ? "Ready" : "Offline")
                                    .font(.caption2)
                                    .foregroundColor(isConnected ? .green : .red)
                            }
                        }
                        .padding(.horizontal)
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
                        .onChange(of: messages.count) { _, _ in
                            if let lastMessage = messages.last {
                                withAnimation(.easeInOut(duration: 0.3)) {
                                    proxy.scrollTo(lastMessage.id, anchor: .bottom)
                                }
                            }
                        }
                    }
                    
                    // Recording area
                    VStack(spacing: 20) {
                        // Conversation Status
                        if isRecording {
                            VStack(spacing: 8) {
                                HStack {
                                    Image(systemName: "mic.fill")
                                        .foregroundColor(.red)
                                        .font(.title2)
                                    
                                    Text("Recording...")
                                        .font(.headline)
                                        .foregroundColor(.red)
                                        .fontWeight(.semibold)
                                }
                                
                                Text(timeString(from: recordingTime))
                                    .font(.title3)
                                    .fontWeight(.medium)
                                    .foregroundColor(.red)
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 15)
                            .background(Color.red.opacity(0.1))
                            .cornerRadius(20)
                        } else if isGrokSpeaking {
                            VStack(spacing: 8) {
                                HStack {
                                    Image(systemName: "brain.head.profile")
                                        .foregroundColor(.purple)
                                        .font(.title2)
                                    
                                    Text("Grok AI is responding...")
                                        .font(.headline)
                                        .foregroundColor(.purple)
                                        .fontWeight(.semibold)
                                }
                                
                                Text("Listening to Grok's response")
                                    .font(.caption)
                                    .foregroundColor(.purple)
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 15)
                            .background(Color.purple.opacity(0.1))
                            .cornerRadius(20)
                        } else {
                            VStack(spacing: 8) {
                                HStack {
                                    Image(systemName: "message.circle.fill")
                                        .foregroundColor(.blue)
                                        .font(.title2)
                                    
                                    Text("Ready for conversation")
                                        .font(.headline)
                                        .foregroundColor(.blue)
                                        .fontWeight(.semibold)
                                }
                                
                                Text("Tap to start talking")
                                    .font(.caption)
                                    .foregroundColor(.blue)
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 15)
                            .background(Color.blue.opacity(0.1))
                            .cornerRadius(20)
                        }
                        
                        // Main recording button
                        Button(action: toggleRecording) {
                            ZStack {
                                Circle()
                                    .fill(isRecording ? Color.red : (isGrokSpeaking ? Color.gray : Color.blue))
                                    .frame(width: 100, height: 100)
                                    .shadow(color: isRecording ? .red.opacity(0.4) : .blue.opacity(0.4), radius: 15, x: 0, y: 8)
                                
                                Image(systemName: isRecording ? "stop.fill" : "mic.fill")
                                    .font(.system(size: 40, weight: .medium))
                                    .foregroundColor(.white)
                            }
                        }
                        .scaleEffect(isRecording ? 1.2 : 1.0)
                        .animation(.easeInOut(duration: 0.3), value: isRecording)
                        .disabled(!isConnected || isGrokSpeaking)
                        
                        // Show transcribed text while recording
                        if isRecording && !transcribedText.isEmpty {
                            VStack(spacing: 8) {
                                Text("You're saying:")
                                    .font(.caption)
                                    .foregroundColor(.blue)
                                    .fontWeight(.medium)
                                
                                Text(transcribedText)
                                    .font(.body)
                                    .foregroundColor(.primary)
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 12)
                                    .background(Color.blue.opacity(0.1))
                                    .cornerRadius(12)
                                    .multilineTextAlignment(.center)
                            }
                            .padding(.horizontal)
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
            print("Sending message to server: \(transcribedText)")
            sendMessageToServer(transcribedText)
            
            // Add user message to the conversation
            let userMessage = Message(
                sender: "phone",
                content: transcribedText,
                messageType: "text",
                timestamp: Date().iso8601
            )
            messages.append(userMessage)
            
            // Clear transcribed text
            transcribedText = ""
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
        
        // Store the recognizer for stopping later
        self.speechRecognizer = speechRecognizer
        self.recognitionRequest = request
    }
    
    private func stopSpeechRecognition() {
        // Stop speech recognition
        recognitionRequest?.endAudio()
        audioEngine?.stop()
        speechRecognizer = nil
    }
    
    private func speakGrokResponse(_ text: String) {
        // Stop any current speech
        if speechSynthesizer.isSpeaking {
            speechSynthesizer.stopSpeaking(at: .immediate)
        }
        
        // Create speech utterance
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = 0.5
        utterance.pitchMultiplier = 1.0
        utterance.volume = 0.8
        
        // Create and store delegate
        speechDelegate = SpeechDelegate(isGrokSpeaking: $isGrokSpeaking)
        speechSynthesizer.delegate = speechDelegate
        
        // Start speaking
        isGrokSpeaking = true
        speechSynthesizer.speak(utterance)
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
        let url = URL(string: "wss://\(serverIP)/ws/phone")!
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
                                
                                // If it's from Grok, speak the response
                                if sender == "grok" {
                                    self.speakGrokResponse(content)
                                }
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
                        HStack(spacing: 6) {
                            Image(systemName: senderIcon)
                                .font(.caption)
                                .foregroundColor(senderColor)
                            
                            Text(senderName)
                                .font(.caption)
                                .foregroundColor(senderColor)
                                .fontWeight(.semibold)
                        }
                    }
                    Spacer()
                    if message.sender == "phone" {
                        HStack(spacing: 6) {
                            Text(senderName)
                                .font(.caption)
                                .foregroundColor(senderColor)
                                .fontWeight(.semibold)
                            
                            Image(systemName: senderIcon)
                                .font(.caption)
                                .foregroundColor(senderColor)
                        }
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
    
    private var senderName: String {
        switch message.sender {
        case "phone": return "You"
        case "grok": return "Grok AI"
        case "cursor": return "Cursor AI"
        default: return message.sender.capitalized
        }
    }
    
    private var senderIcon: String {
        switch message.sender {
        case "phone": return "person.fill"
        case "grok": return "brain.head.profile"
        case "cursor": return "cursorarrow.rays"
        default: return "person"
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
