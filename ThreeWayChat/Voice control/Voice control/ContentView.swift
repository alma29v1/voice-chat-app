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

// Full replacement for ContentView to fix braces and structure

struct ContentView: View {
    @State private var isRecording = false
    @State private var transcribedText = ""
    @State private var isListening = false
    @State private var recordingTime: TimeInterval = 0
    @State private var timer: Timer?
    @State private var showingPermissionAlert = false
    @State private var permissionAlertMessage = ""
    
    @State private var webSocket: URLSessionWebSocketTask?
    @State private var isConnected = false
    @State private var messages: [Message] = []
    @State private var serverIP = "voice-chat-app-cc40.onrender.com"
    @State private var showingServerConfig = false
    @State private var connectionStatus = "Disconnected"
    @State private var isWakingUp = false
    @State private var retryCount = 0
    @State private var isGrokThinking = false
    @State private var isCursorThinking = false
    @State private var isVoiceActivated = true // Auto voice detection
    @State private var silenceTimer: Timer?
    @State private var lastSpeechTime = Date()
    @State private var voiceThreshold: Float = 0.1 // Voice detection sensitivity
    
    @State private var speechRecognizer: SFSpeechRecognizer?
    @State private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    @State private var audioEngine: AVAudioEngine?
    
    @State private var speechSynthesizer = AVSpeechSynthesizer()
    @State private var isGrokSpeaking = false
    @State private var grokResponse = ""
    @State private var speechDelegate: SpeechDelegate?
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient(
                    gradient: Gradient(colors: [Color.blue.opacity(0.1), Color.purple.opacity(0.1)]),
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    VStack(spacing: 10) {
                        HStack {
                            Button(action: { showingServerConfig = true }) {
                                Image(systemName: "gear")
                                    .foregroundColor(.blue)
                                    .font(.title2)
                            }
                            Spacer()
                            Text("Three-Way Chat")
                                .font(.title2)
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
                        
                        HStack {
                            Image(systemName: "speaker.wave.3.fill")
                                .foregroundColor(.green)
                                .font(.caption)
                            Text("Background Audio Enabled")
                                .font(.caption)
                                .foregroundColor(.green)
                                .fontWeight(.medium)
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.green.opacity(0.1))
                        .cornerRadius(8)
                        
                        HStack(spacing: 15) {
                            VStack(spacing: 8) {
                                ZStack {
                                    Circle()
                                        .fill(isConnected ? Color.blue : Color.gray)
                                        .frame(width: 40, height: 40)
                                    Image(systemName: "person.fill")
                                        .font(.title3)
                                        .foregroundColor(.white)
                                }
                                Text("You")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                Text(isConnected ? "Connected" : "Disconnected")
                                    .font(.caption2)
                                    .foregroundColor(isConnected ? .green : .red)
                            }
                            
                            VStack(spacing: 15) {
                                Rectangle()
                                    .fill(isConnected ? Color.green : Color.gray)
                                    .frame(width: 2, height: 20)
                                Rectangle()
                                    .fill(isConnected ? Color.green : Color.gray)
                                    .frame(width: 2, height: 20)
                            }
                            
                            VStack(spacing: 8) {
                                ZStack {
                                    Circle()
                                        .fill(isGrokThinking ? Color.blue : (isConnected ? Color.purple : Color.gray))
                                        .frame(width: 40, height: 40)
                                    Image(systemName: isGrokThinking ? "brain.head.profile.fill" : "brain.head.profile")
                                        .font(.title3)
                                        .foregroundColor(.white)
                                        .opacity(isGrokThinking ? 0.6 : 1.0)
                                        .animation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true), value: isGrokThinking)
                                }
                                Text("Grok AI")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                Text(isGrokThinking ? "Thinking..." : 
                                     (isConnected ? "Ready" : (isWakingUp ? "Waking up..." : "Offline")))
                                    .font(.caption2)
                                    .foregroundColor(isGrokThinking ? .blue : 
                                                   (isConnected ? .green : (isWakingUp ? .orange : .red)))
                            }
                            
                            VStack(spacing: 15) {
                                Rectangle()
                                    .fill(isConnected ? Color.green : Color.gray)
                                    .frame(width: 2, height: 20)
                                Rectangle()
                                    .fill(isConnected ? Color.green : Color.gray)
                                    .frame(width: 2, height: 20)
                            }
                            
                            VStack(spacing: 8) {
                                ZStack {
                                    Circle()
                                        .fill(isCursorThinking ? Color.blue : (isConnected ? Color.green : Color.gray))
                                        .frame(width: 40, height: 40)
                                    Image(systemName: isCursorThinking ? "cursorarrow.rays.fill" : "cursorarrow.rays")
                                        .font(.title3)
                                        .foregroundColor(.white)
                                        .opacity(isCursorThinking ? 0.6 : 1.0)
                                        .animation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true), value: isCursorThinking)
                                }
                                Text("Cursor AI")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                Text(isCursorThinking ? "Thinking..." : 
                                     (isConnected ? "Ready" : (isWakingUp ? "Waking up..." : "Offline")))
                                    .font(.caption2)
                                    .foregroundColor(isCursorThinking ? .blue : 
                                                   (isConnected ? .green : (isWakingUp ? .orange : .red)))
                            }
                        }
                        .padding(.horizontal)
                    }
                    .padding(.top)
                    
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
                    
                    VStack(spacing: 20) {
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
                        
                        VStack(spacing: 15) {
                            Button(action: toggleVoiceActivation) {
                                ZStack {
                                    Circle()
                                        .fill(isVoiceActivated ? (isRecording ? Color.red : Color.green) : Color.gray)
                                        .frame(width: 100, height: 100)
                                        .shadow(color: isVoiceActivated ? .green.opacity(0.4) : .gray.opacity(0.4), radius: 15, x: 0, y: 8)
                                    
                                    Image(systemName: isVoiceActivated ? (isRecording ? "waveform" : "ear") : "mic.slash")
                                        .font(.system(size: 40, weight: .medium))
                                        .foregroundColor(.white)
                                        .opacity(isRecording ? 0.7 : 1.0)
                                        .animation(.easeInOut(duration: 0.5).repeatForever(autoreverses: true), value: isRecording)
                                }
                            }
                            .scaleEffect(isRecording ? 1.2 : 1.0)
                            .animation(.easeInOut(duration: 0.3), value: isRecording)
                            .disabled(!isConnected || isGrokSpeaking)
                            
                            Text(isVoiceActivated ? (isRecording ? "Listening..." : "Say something") : "Voice Detection Off")
                                .font(.caption)
                                .foregroundColor(isVoiceActivated ? .green : .gray)
                                .multilineTextAlignment(.center)
                        }
                        
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
            .alert("Permission Required", isPresented: $showingPermissionAlert) {
                Button("OK") { }
            } message: {
                Text(permissionAlertMessage)
            }
            .sheet(isPresented: $showingServerConfig) {
                ServerConfigView(serverIP: $serverIP, isConnected: $isConnected, connectionStatus: $connectionStatus)
            }
            .onAppear {
                setupAudioSession()
                connectToServer()
                // Auto-start voice detection
                if isVoiceActivated {
                    startVoiceActivityDetection()
                }
            }
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
    
    private func setupAudioSession() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            
            try audioSession.setCategory(.playAndRecord, mode: .default, options: [
                .allowBluetooth,
                .allowBluetoothA2DP,
                .defaultToSpeaker,
                .mixWithOthers,
                .allowAirPlay
            ])
            
            try audioSession.setActive(true)
            
            print("✅ Audio session configured for background playback")
            
        } catch {
            print("❌ Failed to configure audio session: \(error)")
        }
    }
    
    private func toggleVoiceActivation() {
        isVoiceActivated.toggle()
        
        if isVoiceActivated {
            startVoiceActivityDetection()
        } else {
            stopVoiceActivityDetection()
        }
    }
    
    private func startVoiceActivityDetection() {
        print("🎤 Starting voice activity detection")
        setupAudioSession()
        startContinuousListening()
    }
    
    private func stopVoiceActivityDetection() {
        print("🛑 Stopping voice activity detection")
        stopContinuousListening()
        if isRecording {
            stopRecording()
        }
    }
    
    private func startRecording() {
        isRecording = true
        isListening = true
        recordingTime = 0
        transcribedText = ""
        
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
            recordingTime += 0.1
        }
        
        startSpeechRecognition()
    }
    
    private func stopRecording() {
        isRecording = false
        isListening = false
        timer?.invalidate()
        timer = nil
        
        stopSpeechRecognition()
        
        print("🔍 Final transcribed text: '\(transcribedText)'")
        
        if !transcribedText.isEmpty {
            print("📤 Sending message to server: \(transcribedText)")
            
            // Show that Grok is thinking
            isGrokThinking = true
            
            sendMessageToServer(transcribedText)
            
            let userMessage = Message(
                sender: "phone",
                content: transcribedText,
                messageType: "text",
                timestamp: Date().iso8601
            )
            messages.append(userMessage)
            
            transcribedText = ""
        }
    }
    
    private func startSpeechRecognition() {
        let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
        let request = SFSpeechAudioBufferRecognitionRequest()
        let audioEngine = AVAudioEngine()
        
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("❌ Audio session error: \(error)")
            return
        }
        
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            request.append(buffer)
        }
        
        request.shouldReportPartialResults = true
        
        speechRecognizer?.recognitionTask(with: request) { result, error in
            if let result = result {
                DispatchQueue.main.async {
                    self.transcribedText = result.bestTranscription.formattedString
                    print("🎤 Transcribed: \(self.transcribedText)")
                }
            }
            
            if let error = error {
                print("❌ Speech recognition error: \(error)")
            }
        }
        
        audioEngine.prepare()
        
        do {
            try audioEngine.start()
            print("✅ Speech recognition started")
        } catch {
            print("❌ Audio engine start error: \(error)")
        }
        
        self.speechRecognizer = speechRecognizer
        self.recognitionRequest = request
        self.audioEngine = audioEngine
    }
    
    private func stopSpeechRecognition() {
        print("🛑 Stopping speech recognition")
        
        recognitionRequest?.endAudio()
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        
        speechRecognizer = nil
        recognitionRequest = nil
        audioEngine = nil
        
        print("✅ Speech recognition stopped")
    }
    
    private func startContinuousListening() {
        guard !isRecording else { return }
        
        let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
        let request = SFSpeechAudioBufferRecognitionRequest()
        let audioEngine = AVAudioEngine()
        
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("❌ Audio session error: \(error)")
            return
        }
        
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            request.append(buffer)
            
            // Voice activity detection
            self.detectVoiceActivity(in: buffer)
        }
        
        request.shouldReportPartialResults = true
        
        speechRecognizer?.recognitionTask(with: request) { result, error in
            if let result = result {
                let newText = result.bestTranscription.formattedString
                DispatchQueue.main.async {
                    if !self.isRecording && self.shouldStartRecording(for: newText) {
                        self.startRecording()
                    }
                    
                    if self.isRecording {
                        self.transcribedText = newText
                        self.lastSpeechTime = Date()
                        self.resetSilenceTimer()
                        print("🎤 Continuous: \(newText)")
                    }
                }
            }
            
            if let error = error {
                print("❌ Continuous speech error: \(error)")
            }
        }
        
        audioEngine.prepare()
        
        do {
            try audioEngine.start()
            print("✅ Continuous listening started")
        } catch {
            print("❌ Continuous audio engine error: \(error)")
        }
        
        self.speechRecognizer = speechRecognizer
        self.recognitionRequest = request
        self.audioEngine = audioEngine
    }
    
    private func stopContinuousListening() {
        print("🛑 Stopping continuous listening")
        
        recognitionRequest?.endAudio()
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        
        speechRecognizer = nil
        recognitionRequest = nil
        audioEngine = nil
        
        silenceTimer?.invalidate()
        silenceTimer = nil
    }
    
    private func detectVoiceActivity(in buffer: AVAudioPCMBuffer) {
        guard let channelData = buffer.floatChannelData?[0] else { return }
        
        let frameLength = Int(buffer.frameLength)
        var sum: Float = 0
        
        for i in 0..<frameLength {
            sum += abs(channelData[i])
        }
        
        let averageAmplitude = sum / Float(frameLength)
        
        // If amplitude exceeds threshold, consider it voice activity
        if averageAmplitude > voiceThreshold {
            DispatchQueue.main.async {
                self.lastSpeechTime = Date()
            }
        }
    }
    
    private func shouldStartRecording(for text: String) -> Bool {
        // Start recording if we detect meaningful speech (more than just noise)
        return text.count > 2 && !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
    
    private func resetSilenceTimer() {
        silenceTimer?.invalidate()
        silenceTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: false) { _ in
            DispatchQueue.main.async {
                if self.isRecording && Date().timeIntervalSince(self.lastSpeechTime) > 1.5 {
                    print("🔇 Silence detected, stopping recording")
                    self.stopRecording()
                }
            }
        }
    }
    
    private func speakGrokResponse(_ text: String) {
        if speechSynthesizer.isSpeaking {
            speechSynthesizer.stopSpeaking(at: .immediate)
        }
        
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = 0.5
        utterance.pitchMultiplier = 1.0
        utterance.volume = 0.8
        
        speechDelegate = SpeechDelegate(isGrokSpeaking: $isGrokSpeaking)
        speechSynthesizer.delegate = speechDelegate
        
        isGrokSpeaking = true
        speechSynthesizer.speak(utterance)
    }
    
    private func sendMessageToServer(_ content: String) {
        guard isConnected else {
            print("❌ Cannot send message: Not connected to server")
            return
        }
        
        let message = [
            "content": content,
            "type": "text",
            "sender": "phone"
        ]
        
        print("📦 Preparing message: \(message)")
        
        if let data = try? JSONSerialization.data(withJSONObject: message),
           let jsonString = String(data: data, encoding: .utf8) {
            print("📡 Sending JSON: \(jsonString)")
            webSocket?.send(.string(jsonString)) { error in
                if let error = error {
                    print("❌ Error sending message: \(error)")
                } else {
                    print("✅ Message sent successfully")
                }
            }
        } else {
            print("❌ Failed to serialize message to JSON")
        }
    }
    
    private func connectToServer() {
        retryCount += 1
        
        // Determine status message based on retry attempts
        if retryCount == 1 {
            connectionStatus = "Connecting..."
        } else if retryCount <= 10 {
            connectionStatus = "Server waking up... (\(retryCount)/10)"
            isWakingUp = true
        } else {
            connectionStatus = "Retrying connection..."
        }
        
        let url = URL(string: "wss://\(serverIP)/ws/phone")!
        let session = URLSession(configuration: .default)
        webSocket = session.webSocketTask(with: url)
        
        print("🔗 Attempting WebSocket connection to: wss://\(serverIP)/ws/phone")
        
        // Start receiving before resuming
        receiveMessage()
        
        // Add connection state tracking
        webSocket?.resume()
        
        print("🚀 WebSocket task resumed")
        
        // Check connection status with smart retry
        DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
            if self.isConnected {
                self.connectionStatus = "Connected"
                self.isWakingUp = false
                self.retryCount = 0
                print("✅ WebSocket connection successful")
            } else {
                print("❌ WebSocket connection failed after 5 seconds")
                // Retry with exponential backoff for hibernating servers
                let delay = self.retryCount <= 10 ? 5.0 : 10.0 // 5s for wakeup, 10s for connection issues
                
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                    self.connectToServer() // Retry automatically
                }
            }
        }
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
                                // Handle status messages
                                if let content = messageData["content"] as? String {
                                    if content.contains("Connected to ThreeWayChat") {
                                        // Only set connected on the specific connection message
                                        self.connectionStatus = "Connected"
                                        self.isConnected = true
                                        print("✅ Confirmed connection to server")
                                    } else if content.contains("Grok thinking") {
                                        self.isGrokThinking = true
                                    } else if content.contains("Consulting Cursor") {
                                        self.isCursorThinking = true
                                    }
                                }
                                
                            } else if let sender = messageData["sender"] as? String,
                                      let content = messageData["content"] as? String {
                                
                                // Reset thinking states when we get actual responses
                                if sender == "grok" {
                                    self.isGrokThinking = false
                                }
                                if sender == "cursor" {
                                    self.isCursorThinking = false
                                }
                                
                                let message = Message(
                                    sender: sender,
                                    content: content,
                                    messageType: messageData["message_type"] as? String ?? "text",
                                    timestamp: messageData["timestamp"] as? String ?? ""
                                )
                                self.messages.append(message)
                                
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
                
                self.receiveMessage()
                
            case .failure(let error):
                DispatchQueue.main.async {
                    self.connectionStatus = "Connection failed"
                    self.isConnected = false
                }
                print("❌ WebSocket error: \(error)")
                
                // Trigger reconnection on error
                DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                    self.connectToServer()
                }
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
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                DispatchQueue.main.async {
                    if !granted {
                        permissionAlertMessage = "Microphone access is required for voice control."
                        showingPermissionAlert = true
                    }
                }
            }
        }
        
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
                            .foregroundColor(isConnected ? .green : (connectionStatus.contains("waking") ? .orange : .red))
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
