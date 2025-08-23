#!/usr/bin/env python3
"""
Voice Control App Icon Generator
Creates a modern microphone-based app icon with voice waves
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

def create_voice_control_icon():
    # Create a 1024x1024 image with a gradient background
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(size):
        # Blue to purple gradient
        r = int(59 + (y / size) * 20)  # 59-79
        g = int(130 + (y / size) * 40)  # 130-170
        b = int(246 + (y / size) * 20)  # 246-266 (capped at 255)
        b = min(b, 255)
        
        color = (r, g, b, 255)
        draw.line([(0, y), (size, y)], fill=color)
    
    # Add a subtle radial gradient overlay
    center_x, center_y = size // 2, size // 2
    max_radius = size // 2
    
    for radius in range(max_radius, 0, -1):
        alpha = int(255 * (1 - radius / max_radius) * 0.3)
        if alpha > 0:
            # Create a circle with decreasing opacity
            bbox = (center_x - radius, center_y - radius, 
                   center_x + radius, center_y + radius)
            overlay = Image.new('RGBA', (size, size), (255, 255, 255, alpha))
            mask = Image.new('L', (size, size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse(bbox, fill=255)
            img = Image.alpha_composite(img, overlay)
            draw = ImageDraw.Draw(img)
    
    # Draw the main microphone body
    mic_center_x, mic_center_y = size // 2, size // 2 - 50
    mic_width, mic_height = 200, 300
    
    # Microphone body (rounded rectangle)
    mic_rect = [
        mic_center_x - mic_width // 2,
        mic_center_y - mic_height // 2,
        mic_center_x + mic_width // 2,
        mic_center_y + mic_height // 2
    ]
    
    # Draw microphone body with gradient
    for i in range(mic_height // 2):
        y_offset = i
        alpha = int(255 * (1 - i / (mic_height // 2)) * 0.8)
        color = (255, 255, 255, alpha)
        
        # Top part of microphone
        draw.ellipse([
            mic_rect[0], mic_center_y - mic_height // 2 + y_offset,
            mic_rect[2], mic_center_y - mic_height // 2 + y_offset + 2
        ], fill=color)
        
        # Bottom part of microphone
        draw.ellipse([
            mic_rect[0], mic_center_y + mic_height // 2 - y_offset - 2,
            mic_rect[2], mic_center_y + mic_height // 2 - y_offset
        ], fill=color)
    
    # Draw microphone grill (dots)
    grill_radius = 60
    for angle in range(0, 360, 15):
        x = mic_center_x + grill_radius * math.cos(math.radians(angle))
        y = mic_center_y + grill_radius * math.sin(math.radians(angle))
        draw.ellipse([x-8, y-8, x+8, y+8], fill=(100, 100, 100, 200))
    
    # Draw voice waves
    wave_center_x, wave_center_y = size // 2, size // 2 + 200
    wave_colors = [(255, 255, 255, 180), (255, 255, 255, 140), (255, 255, 255, 100)]
    
    for wave_idx, wave_color in enumerate(wave_colors):
        wave_amplitude = 30 + wave_idx * 20
        wave_frequency = 0.02 + wave_idx * 0.005
        
        points = []
        for x in range(0, size, 2):
            y = wave_center_y + wave_amplitude * math.sin(wave_frequency * x + wave_idx * 0.5)
            points.append((x, y))
        
        if len(points) > 1:
            draw.line(points, fill=wave_color, width=4)
    
    # Add a subtle glow effect around the microphone
    glow_radius = mic_width // 2 + 30
    for i in range(20):
        alpha = int(255 * (1 - i / 20) * 0.1)
        color = (255, 255, 255, alpha)
        bbox = (mic_center_x - glow_radius - i, mic_center_y - glow_radius - i,
               mic_center_x + glow_radius + i, mic_center_y + glow_radius + i)
        draw.ellipse(bbox, outline=color, width=2)
    
    return img

def main():
    print("Generating Voice Control app icon...")
    
    # Create the icon
    icon = create_voice_control_icon()
    
    # Save the icon
    output_path = "Voice control/Voice control/AppIcon.png"
    icon.save(output_path, "PNG")
    
    print(f"✅ App icon generated successfully: {output_path}")
    print("📱 The icon is ready to be used in your Xcode project!")
    print("\nTo use this icon:")
    print("1. Open your Xcode project")
    print("2. Go to Assets.xcassets > AppIcon")
    print("3. Drag and drop the generated AppIcon.png file")
    print("4. Xcode will automatically create all required sizes")

if __name__ == "__main__":
    main()
