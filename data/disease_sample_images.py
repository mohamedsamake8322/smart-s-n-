
import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
from typing import List, Dict

def create_sample_disease_images():
    """
    CrÃ©e des images d'exemple pour tester la dÃ©tection de maladies
    """
    
    # Create directories
    base_dir = "data/disease_images"
    os.makedirs(base_dir, exist_ok=True)
    
    # Disease categories with characteristics
    disease_samples = {
        "healthy": {
            "color": (34, 139, 34),  # Forest green
            "pattern": "uniform",
            "description": "Healthy plant leaf"
        },
        "late_blight": {
            "color": (139, 69, 19),  # Saddle brown
            "pattern": "irregular_spots",
            "description": "Late blight symptoms"
        },
        "early_blight": {
            "color": (160, 82, 45),  # Saddle brown
            "pattern": "concentric_rings",
            "description": "Early blight with target spots"
        },
        "bacterial_spot": {
            "color": (105, 105, 105),  # Dim gray
            "pattern": "small_spots",
            "description": "Bacterial spot symptoms"
        },
        "rust": {
            "color": (255, 140, 0),  # Dark orange
            "pattern": "rust_pustules",
            "description": "Rust disease pustules"
        },
        "powdery_mildew": {
            "color": (255, 255, 255),  # White
            "pattern": "powdery_coating",
            "description": "Powdery mildew coating"
        }
    }
    
    created_images = []
    
    for disease_type, characteristics in disease_samples.items():
        for i in range(5):  # Create 5 samples per disease
            # Create base image
            img = Image.new('RGB', (224, 224), (34, 139, 34))  # Green background
            draw = ImageDraw.Draw(img)
            
            # Add disease patterns
            if characteristics['pattern'] == 'uniform':
                # Healthy leaf - just green with some variation
                _add_leaf_texture(draw, img.size)
            
            elif characteristics['pattern'] == 'irregular_spots':
                # Late blight - irregular brown spots
                _add_irregular_spots(draw, img.size, characteristics['color'])
            
            elif characteristics['pattern'] == 'concentric_rings':
                # Early blight - target spots
                _add_target_spots(draw, img.size, characteristics['color'])
            
            elif characteristics['pattern'] == 'small_spots':
                # Bacterial spot - small dark spots
                _add_small_spots(draw, img.size, characteristics['color'])
            
            elif characteristics['pattern'] == 'rust_pustules':
                # Rust - orange pustules
                _add_rust_pustules(draw, img.size, characteristics['color'])
            
            elif characteristics['pattern'] == 'powdery_coating':
                # Powdery mildew - white coating
                _add_powdery_coating(draw, img.size, characteristics['color'])
            
            # Add some natural variation
            _add_natural_variation(img)
            
            # Save image
            filename = f"{disease_type}_sample_{i+1}.jpg"
            filepath = os.path.join(base_dir, filename)
            img.save(filepath, 'JPEG', quality=85)
            
            created_images.append({
                'filename': filename,
                'filepath': filepath,
                'disease_type': disease_type,
                'description': characteristics['description'],
                'created_date': datetime.now().isoformat()
            })
    
    # Save image metadata
    metadata_path = os.path.join(base_dir, 'image_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(created_images, f, ensure_ascii=False, indent=2)
    
    print(f"Created {len(created_images)} sample images in {base_dir}")
    return created_images

def _add_leaf_texture(draw, size):
    """Add natural leaf texture"""
    width, height = size
    
    # Add some vein-like lines
    for i in range(3):
        start_x = width // 4 + np.random.randint(-20, 20)
        start_y = np.random.randint(height // 4, 3 * height // 4)
        end_x = 3 * width // 4 + np.random.randint(-20, 20)
        end_y = start_y + np.random.randint(-30, 30)
        
        draw.line([(start_x, start_y), (end_x, end_y)], 
                 fill=(0, 100, 0), width=2)

def _add_irregular_spots(draw, size, color):
    """Add irregular spots for late blight"""
    width, height = size
    
    for _ in range(np.random.randint(3, 8)):
        center_x = np.random.randint(width // 4, 3 * width // 4)
        center_y = np.random.randint(height // 4, 3 * height // 4)
        
        # Create irregular shape
        points = []
        for angle in range(0, 360, 30):
            radius = np.random.randint(15, 35)
            x = center_x + radius * np.cos(np.radians(angle))
            y = center_y + radius * np.sin(np.radians(angle))
            points.append((x, y))
        
        draw.polygon(points, fill=color)

def _add_target_spots(draw, size, color):
    """Add concentric ring spots for early blight"""
    width, height = size
    
    for _ in range(np.random.randint(2, 5)):
        center_x = np.random.randint(width // 4, 3 * width // 4)
        center_y = np.random.randint(height // 4, 3 * height // 4)
        
        # Draw concentric circles
        for ring in range(3):
            radius = 15 + ring * 8
            bbox = [center_x - radius, center_y - radius,
                   center_x + radius, center_y + radius]
            
            ring_color = tuple(max(0, c - ring * 30) for c in color)
            draw.ellipse(bbox, outline=ring_color, width=2)

def _add_small_spots(draw, size, color):
    """Add small spots for bacterial diseases"""
    width, height = size
    
    for _ in range(np.random.randint(10, 20)):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        radius = np.random.randint(2, 6)
        
        bbox = [x - radius, y - radius, x + radius, y + radius]
        draw.ellipse(bbox, fill=color)

def _add_rust_pustules(draw, size, color):
    """Add rust pustules"""
    width, height = size
    
    for _ in range(np.random.randint(15, 30)):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        radius = np.random.randint(1, 4)
        
        bbox = [x - radius, y - radius, x + radius, y + radius]
        draw.ellipse(bbox, fill=color)

def _add_powdery_coating(draw, size, color):
    """Add powdery mildew coating"""
    width, height = size
    
    # Create patches of white coating
    for _ in range(np.random.randint(3, 6)):
        x = np.random.randint(0, width // 2)
        y = np.random.randint(0, height // 2)
        w = np.random.randint(30, 80)
        h = np.random.randint(30, 80)
        
        # Semi-transparent white overlay
        overlay_color = (*color, 128)  # Semi-transparent
        draw.rectangle([x, y, x + w, y + h], fill=color)

def _add_natural_variation(img):
    """Add natural color variation to the image"""
    img_array = np.array(img)
    
    # Add slight noise
    noise = np.random.normal(0, 5, img_array.shape)
    img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    # Create new image from modified array
    modified_img = Image.fromarray(img_array)
    img.paste(modified_img)

def create_disease_training_dataset():
    """
    CrÃ©e un dataset d'entraÃ®nement plus large pour les modÃ¨les
    """
    print("CrÃ©ation du dataset d'entraÃ®nement...")
    
    # Create sample images
    sample_images = create_sample_disease_images()
    
    # Create training/validation split info
    training_info = {
        'dataset_size': len(sample_images),
        'classes': list(set([img['disease_type'] for img in sample_images])),
        'samples_per_class': 5,
        'image_format': 'JPEG',
        'image_size': '224x224',
        'created_date': datetime.now().isoformat(),
        'notes': 'Sample dataset for demonstration purposes'
    }
    
    # Save training info
    with open('data/disease_images/training_info.json', 'w', encoding='utf-8') as f:
        json.dump(training_info, f, ensure_ascii=False, indent=2)
    
    print(f"Dataset crÃ©Ã© avec {len(sample_images)} images")
    print(f"Classes: {training_info['classes']}")
    
    return sample_images, training_info

if __name__ == "__main__":
    create_disease_training_dataset()





