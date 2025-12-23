
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
from typing import List, Tuple

class LeafletImageEnhancementV1:
    def __init__(self):
        pass

    def pil_to_cv(self, pil_image: Image.Image) -> np.ndarray:
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def cv_to_pil(self, cv_image: np.ndarray) -> Image.Image:
        return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

    # 1. RESOLUTION ENHANCEMENT
    def enhance_resolution(self, pil_image: Image.Image, improvements: List[str]) -> Tuple[Image.Image, List[str]]:
        width, height = pil_image.size
        min_width, min_height = 800, 600
        
        if width < min_width or height < min_height:
            scale_x = max(1.0, min_width / width)
            scale_y = max(1.0, min_height / height)
            scale_factor = max(scale_x, scale_y)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
            improvements.append(f"Upscaled resolution from {width}x{height} to {new_width}x{new_height}")
            
        return pil_image, improvements

    # 2. BRIGHTNESS CORRECTION
    def adjust_brightness(self, cv_image: np.ndarray, improvements: List[str]) -> Tuple[np.ndarray, List[str]]:
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        print(f"brightness: {brightness}")
        if brightness < 50 or brightness > 200:
            target_brightness = 120
            brightness_factor = target_brightness / brightness
            
            cv_image = cv2.convertScaleAbs(cv_image, alpha=brightness_factor, beta=0)
            improvements.append(f"Adjusted brightness from {brightness:.1f} to ~{target_brightness}")
            
        return cv_image, improvements

    # 3. CONTRAST ENHANCEMENT
    def enhance_contrast(self, cv_image: np.ndarray, improvements: List[str]) -> Tuple[np.ndarray, List[str]]:
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray)
        
        if contrast < 40:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            cv_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            improvements.append(f"Enhanced contrast from {contrast:.1f} using CLAHE")
            
        return cv_image, improvements

    # 4. BLUR REDUCTION (SHARPENING)
    def reduce_blur(self, cv_image: np.ndarray, improvements: List[str]) -> Tuple[np.ndarray, List[str]]:
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        min_blur_score = 150
        
        if blur_score < min_blur_score:
            gaussian = cv2.GaussianBlur(cv_image, (0, 0), 2.0)
            cv_image = cv2.addWeighted(cv_image, 1.5, gaussian, -0.5, 0)
            
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            cv_image = cv2.filter2D(cv_image, -1, kernel * 0.1)
            
            improvements.append(f"Applied sharpening to improve blur score from {blur_score:.1f}")
            
        return cv_image, improvements

    # 5. NOISE REDUCTION
    def reduce_noise(self, cv_image: np.ndarray, improvements: List[str]) -> Tuple[np.ndarray, List[str]]:
        cv_image = cv2.bilateralFilter(cv_image, 9, 75, 75)
        improvements.append("Applied noise reduction")
        return cv_image, improvements

    # 6. DOCUMENT STRAIGHTENING
    def straighten_document(self, cv_image: np.ndarray, improvements: List[str]) -> Tuple[np.ndarray, List[str]]:
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
        
        if lines is not None and len(lines) > 0:
            angles = [np.degrees(theta) - 90 for rho, theta in lines[0:10] if abs(np.degrees(theta) - 90) < 45]
            
            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:
                    height, width = cv_image.shape[:2]
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    cv_image = cv2.warpAffine(cv_image, rotation_matrix, (width, height),
                                            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    improvements.append(f"Corrected rotation by {median_angle:.1f} degrees")
                    
        return cv_image, improvements

    def enhance_sharpness_and_dpi(self, pil_image: Image.Image, improvements: List[str]) -> Tuple[Image.Image, Tuple[int, int], List[str]]:
        # Set DPI
        current_dpi = pil_image.info.get('dpi', (72, 72))
        min_dpi = 150
        actual_dpi = min(current_dpi) if isinstance(current_dpi, tuple) else current_dpi
        new_dpi = (300, 300) if actual_dpi < min_dpi else current_dpi
        
        if actual_dpi < min_dpi:
            improvements.append(f"Enhanced DPI from {actual_dpi} to 300")
        
        # Slight sharpness enhancement
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(1.1)
        
        return pil_image, new_dpi, improvements
    
    def create_out_filepath(self, file_path):
        #file_path = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\id_identification\img_files\dl3.png"
        new_file_path = None
        try:
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            new_base_name = f"enhance_{base_name}" 
            new_file_path = os.path.join(dir_name, new_base_name)
        except:
            pass 
        return new_file_path


    def enhance_image_pipeline(self, input_path: str, output_path: str = None, enhancements_to_apply: List[str] = None) -> dict:
        if output_path is None:
           output_path = self.create_out_filepath(input_path)
        
        improvements = []
        
        try:
            pil_image = Image.open(input_path)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
                improvements.append("Converted to RGB color mode")

            # Create a dictionary to map enhancement names to functions
            enhancements = {
                "resolution": self.enhance_resolution,
                #"brightness": adjust_brightness,
                "contrast": self.enhance_contrast,
                "blur_reduction": self.reduce_blur,
                "noise_reduction": self.reduce_noise,
                "straighten": self.straighten_document,
            }
            #enhancements_to_apply = ["brightness", "contrast", "blur_reduction", "noise_reduction", "straighten"]
            enhancements_to_apply = ["brightness", "contrast", "blur_reduction", "noise_reduction"] # blur_reduction brightness  contrast noise_reduction
            # Handle resolution and DPI first, as they affect the whole image
            pil_image, improvements = enhancements["resolution"](pil_image, improvements)
            pil_image, new_dpi, improvements = self.enhance_sharpness_and_dpi(pil_image, improvements)

            # Convert to OpenCV for subsequent operations
            cv_image = self.pil_to_cv(pil_image)

            # Apply other enhancements as per user requirement
            if enhancements_to_apply is None:
                enhancements_to_apply = ["brightness", "contrast", "blur_reduction", "noise_reduction", "straighten"]

            for enhancement in enhancements_to_apply:
                if enhancement in enhancements:
                    # Some functions work on PIL, others on OpenCV. Check type.
                    if enhancement in ["brightness", "contrast", "blur_reduction", "noise_reduction", "straighten"]:
                        cv_image, improvements = enhancements[enhancement](cv_image, improvements)
                    
            # Final conversion back to PIL for saving
            pil_final = self.cv_to_pil(cv_image)
            #print(f"output_path: {output_path}")
            # Save with high quality and correct DPI
            pil_final.save(output_path, 'JPEG', quality=95, dpi=new_dpi, optimize=True)
            
            return {
                "success": True,
                "message": f"Image enhanced successfully. Applied {len(improvements)} improvements.",
                "enhanced_path": output_path,
                "improvements": improvements
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error enhancing image: {str(e)}",
                "enhanced_path": "",
                "improvements": []
            }


if __name__ == "__main__":
    file_path = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\testfiles\us_passports_img\uspass200.png"
    update_path = None # r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\id_identification\img_files\enhance_dl3.png"
    enhancements_to_apply= None  #["contrast", "blur_reduction"]
    objEnh = LeafletImageEnhancementV1()
    print("=== Custom Enhancement ===")
    result = objEnh.enhance_image_pipeline(file_path, update_path, enhancements_to_apply=enhancements_to_apply)
    print("*********************************")
    print(result)
    print("*********************************")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['improvements']:
        print("Improvements applied:")
        for improvement in result['improvements']:
            print(f"  • {improvement}")