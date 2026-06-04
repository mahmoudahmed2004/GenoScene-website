#!/usr/bin/env python3
"""
GenoScene - Face Image Generator
===============================

This script generates realistic face images for all possible phenotype combinations
used in the GenoScene phenotype prediction system.
"""

import os
from PIL import Image, ImageDraw
import math

def create_face_image(hair_color, eye_color, skin_color, size=(200, 200)):
    """
    Create a realistic face image with specified colors
    
    Args:
        hair_color (str): Hair color ('brown', 'blonde', 'black')
        eye_color (str): Eye color ('brown', 'blue', 'green')
        skin_color (str): Skin color ('light', 'medium', 'dark')
        size (tuple): Image size (width, height)
    
    Returns:
        PIL.Image: Generated face image
    """
    
    # Color mappings
    colors = {
        'hair': {
            'brown': (139, 69, 19),
            'blonde': (218, 165, 32),
            'black': (47, 47, 47)
        },
        'eye': {
            'brown': (139, 69, 19),
            'blue': (65, 105, 225),
            'green': (34, 139, 34)
        },
        'skin': {
            'light': (244, 209, 182),
            'medium': (209, 166, 121),
            'dark': (141, 85, 36)
        }
    }
    
    # Create image with transparent background
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Draw hair (behind face)
    hair_points = []
    for angle in range(0, 180, 5):
        x = center_x + int(60 * math.cos(math.radians(angle)))
        y = center_y - 40 + int(30 * math.sin(math.radians(angle)))
        hair_points.append((x, y))
    
    if hair_points:
        draw.polygon(hair_points, fill=colors['hair'][hair_color])
    
    # Draw face (ellipse)
    face_bbox = (center_x - 60, center_y - 30, center_x + 60, center_y + 80)
    draw.ellipse(face_bbox, fill=colors['skin'][skin_color], outline=(0, 0, 0, 255), width=2)
    
    # Draw eyes
    left_eye_bbox = (center_x - 35, center_y - 10, center_x - 15, center_y + 10)
    right_eye_bbox = (center_x + 15, center_y - 10, center_x + 35, center_y + 10)
    
    draw.ellipse(left_eye_bbox, fill=colors['eye'][eye_color], outline=(0, 0, 0, 255), width=1)
    draw.ellipse(right_eye_bbox, fill=colors['eye'][eye_color], outline=(0, 0, 0, 255), width=1)
    
    # Draw pupils
    left_pupil_bbox = (center_x - 30, center_y - 5, center_x - 20, center_y + 5)
    right_pupil_bbox = (center_x + 20, center_y - 5, center_x + 30, center_y + 5)
    
    draw.ellipse(left_pupil_bbox, fill=(0, 0, 0, 255))
    draw.ellipse(right_pupil_bbox, fill=(0, 0, 0, 255))
    
    # Draw nose
    nose_points = [
        (center_x, center_y + 10),
        (center_x - 8, center_y + 25),
        (center_x + 8, center_y + 25)
    ]
    draw.polygon(nose_points, fill=colors['skin'][skin_color], outline=(0, 0, 0, 255), width=1)
    
    # Draw mouth
    mouth_bbox = (center_x - 15, center_y + 40, center_x + 15, center_y + 50)
    draw.arc(mouth_bbox, 0, 180, fill=(139, 0, 0, 255), width=2)
    
    return img

def generate_all_faces():
    """Generate all possible face combinations"""
    
    hair_colors = ['brown', 'blonde', 'black']
    eye_colors = ['brown', 'blue', 'green']
    skin_colors = ['light', 'medium', 'dark']
    
    total_combinations = len(hair_colors) * len(eye_colors) * len(skin_colors)
    current = 0
    
    print(f"Generating {total_combinations} face images...")
    
    for hair in hair_colors:
        for eye in eye_colors:
            for skin in skin_colors:
                current += 1
                filename = f"face_{hair}_{eye}_{skin}.png"
                filepath = os.path.join(os.path.dirname(__file__), filename)
                
                print(f"[{current}/{total_combinations}] Generating {filename}...")
                
                try:
                    img = create_face_image(hair, eye, skin)
                    img.save(filepath, 'PNG')
                    print(f"✅ Saved {filename}")
                except Exception as e:
                    print(f"❌ Error generating {filename}: {e}")
    
    print(f"\n🎉 Generated {current} face images successfully!")

if __name__ == "__main__":
    generate_all_faces()
