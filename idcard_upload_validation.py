############################################################################################################################
## image brightness, dpi, blur checking with specify range
## Date 11 SEP 2025
############################################################################################################################

import os
import mimetypes
from PIL import Image
import cv2
import numpy as np
from typing import Dict


try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

class LeafletImageUploadTest:
    def __init__(self):
        pass

    def validate_id_upload(self, file_path: str, max_size_mb: int = 10, min_size_kb: int = 50) -> Dict:
        errors = []
        try:
            # 1. FILE EXISTENCE CHECK
            if not os.path.exists(file_path):
                return {"valid": False, "message": "File does not exist"}
            
            # 2. FILE SIZE VALIDATION
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            min_size_bytes = min_size_kb * 1024
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size < min_size_bytes:
                errors.append(f"File too small ({file_size_mb}MB), minimum required: {min_size_kb}KB")
            
            if file_size > max_size_bytes:
                errors.append(f"File too large ({file_size_mb}MB), maximum allowed: {max_size_mb}MB")
            
            # 3. FILE FORMAT VALIDATION
            mime_type = None
            try:
                if HAS_MAGIC:
                    mime_type = magic.from_file(file_path, mime=True)
                else:
                    mime_type, _ = mimetypes.guess_type(file_path)
                
                allowed_mime_types = [
                    'image/jpeg',
                    'image/jpg', 
                    'image/png',
                    'image/tiff',
                    'image/tif'
                ]
                
                if mime_type and mime_type not in allowed_mime_types:
                    errors.append(f"Unsupported file format: {mime_type}, allowed formats: JPEG, PNG, TIFF")
                    
            except Exception:
                # Fallback to extension check
                pass
            
            # 4. FILE EXTENSION VALIDATION
            file_extension = os.path.splitext(file_path)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif']
            if file_extension not in allowed_extensions:
                errors.append(f"Invalid file extension: {file_extension}, allowed: JPG, JPEG, PNG, TIFF")
            
            # 5. IMAGE-SPECIFIC VALIDATIONS
            if mime_type and mime_type.startswith('image/'):
                try:
                    # Open image with PIL
                    with Image.open(file_path) as img:
                        width, height = img.size
                        
                        # Resolution validation
                        min_width, min_height = 800, 600
                        if width < min_width or height < min_height:
                            errors.append(f"Image resolution too low ({width}x{height}), minimum required: {min_width}x{min_height}")
                        
                        # STRICT DPI CHECK - Must be 150+ DPI
                        dpi = img.info.get('dpi')
                        if dpi:
                            min_dpi = 150
                            actual_dpi = min(dpi) if isinstance(dpi, tuple) else dpi
                            if actual_dpi < min_dpi:
                                errors.append(f"Image DPI too low ({actual_dpi}), minimum required: {min_dpi} DPI")
                        else:
                            errors.append("Image DPI information not found, minimum required: 150 DPI")
                        
                        # Color mode validation
                        if img.mode not in ['RGB', 'RGBA', 'L']:
                            errors.append(f"Unsupported color mode: {img.mode}, required: RGB, RGBA, or Grayscale")
                    
                    # 6. STRICT BLUR CHECK using OpenCV
                    cv_image = cv2.imread(file_path)
                    if cv_image is not None:
                        # Blur detection using Laplacian variance
                        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                        
                        # STRICT BLUR THRESHOLD - Must have good focus
                        min_blur_score = 150  # Higher threshold for strict validation
                        if blur_score < min_blur_score:
                            errors.append(f"Image is too blurry (score: {blur_score:.1f}), minimum sharpness required: {min_blur_score}")
                        
                        # Brightness check
                        brightness = np.mean(gray)
                        if brightness < 50:
                            errors.append(f"Image too dark (brightness: {brightness:.1f}), minimum required: 50")
                        elif brightness > 200:
                            errors.append(f"Image too bright (brightness: {brightness:.1f}), maximum allowed: 200")
                        
                        # Contrast check
                        contrast = np.std(gray)
                        if contrast < 40:  # Stricter contrast requirement
                            errors.append(f"Image contrast too low ({contrast:.1f}), minimum required: 40")
                            
                except Exception as e:
                    errors.append(f"Error processing image: {str(e)}")
            
            # 7. FILE CORRUPTION CHECK
            try:
                if mime_type and mime_type.startswith('image/'):
                    with Image.open(file_path) as img:
                        img.verify()  # Verify image integrity
            except Exception:
                errors.append("File appears to be corrupted or invalid image format")
            
            # 8. SECURITY CHECK
            try:
                with open(file_path, 'rb') as f:
                    file_content = f.read(1024)  # Read first 1KB
                    suspicious_patterns = [b'MZ', b'PK', b'<?php', b'<script']
                    for pattern in suspicious_patterns:
                        if pattern in file_content:
                            errors.append("File contains suspicious or executable content")
                            break
            except Exception:
                pass
            
        except Exception as e:
            errors.append(f"Unexpected validation error: {str(e)}")
        
        # Return result
        if errors:
            return {
                "valid": False,
                "message": "; ".join(errors)
            }
        else:
            return {
                "valid": True,
                "message": "Image validation successful"
            }

    

def test_validation(self):
        """Test function to demonstrate usage"""
        test_files = [
            "sample_license_good.jpg",      # Should pass
            "sample_license_blurry.jpg",    # Should fail - blur
            "sample_license_low_dpi.jpg",   # Should fail - DPI
            "sample_document.pdf"           # Should fail - format
        ]
        
        for file_path in test_files:
            print(f"\nTesting: {file_path}")
            result = validate_id_upload(file_path)
            print(f"Valid: {result['valid']}")
            print(f"Message: {result['message']}")
            print("-" * 50)

# Usage example:
if __name__ == "__main__":    
    file_path =  r"F:\face_detect_images\indopass6.jpg"
    # r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\id_identification\img_files\dl3.png"
    imgObj = LeafletImageUploadTest()
    result = imgObj.validate_id_upload(file_path)
    
    print("Validation Result:")
    print(f"Valid: {result['valid']}")
    print(f"Message: {result['message']}")
    
    # For API integration
    if result['valid']:
        print("\n Proceed with OCR processing")
    else:
        print(f"\n Validation failed: {result['message']}")