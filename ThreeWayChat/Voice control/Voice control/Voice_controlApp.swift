//
//  Voice_controlApp.swift
//  Voice control
//
//  Created by Matthew Caison on 8/22/25.
//

import SwiftUI
import AVFoundation

@main
struct Voice_controlApp: App {
    init() {
        // Configure audio session for background playback
        setupAudioSession()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onAppear {
                    // Set supported orientations to landscape
                    UIDevice.current.setValue(UIInterfaceOrientation.landscapeRight.rawValue, forKey: "orientation")
                }
        }
    }
    
    private func setupAudioSession() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.playAndRecord, mode: .default, options: [.allowBluetooth, .allowBluetoothA2DP, .defaultToSpeaker])
            try audioSession.setActive(true)
        } catch {
            print("Failed to configure audio session: \(error)")
        }
    }
}
