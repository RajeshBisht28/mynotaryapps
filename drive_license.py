import cv2
import pytesseract
import re
import json

class LeafletDriverLicenseExtractor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.extracted_text = self.extract_text_with_tabs(image_path)
        self.info = self.extract_field_text(self.extracted_text)

    def extract_text_with_tabs(self, image_path):
        #pytesseract.pytesseract.tesseract_cmd = r'C:\Users\hp\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            custom_config = r'--psm 6 -c preserve_interword_spaces=1'
            text = pytesseract.image_to_string(gray, config=custom_config)
            return text
        except pytesseract.TesseractNotFoundError:
            return "Tesseract executable not found. Please install the Tesseract OCR engine."
        except Exception as e:
            return f"An error occurred: {e}"

    def extract_field_text(self, extracted_text):
        info = {}
        # Extract DL Number
        try:
            dl_number_match = re.search(r'DL No\s*([\w\s]+)', extracted_text, re.IGNORECASE)
            dl_number = dl_number_match.group(1).strip() if dl_number_match else "Not Found"

            # Extract Date of Issue (DOI)
            # The pattern looks for 'DOI' or 'DO!', followed by a date in DD-MM-YYYY format
            doi_match = re.search(r'DO[I!]\s*(\d{2}-\d{2}-\d{4})', extracted_text, re.IGNORECASE)
            doi = doi_match.group(1) if doi_match else "Not Found"

            # Extract 'Valid Till' date
            valid_till_match = re.search(r'Valid Till\s*(\d{2}-\d{2}-\d{4})', extracted_text, re.IGNORECASE)
            valid_till = valid_till_match.group(1) if valid_till_match else "Not Found"

            # Extract Date of Birth (DOB)
            dob_match = re.search(r'DOB:\s*(\d{2}-\d{2}-\d{4})', extracted_text)
            dob = dob_match.group(1) if dob_match else "Not Found"
            info["DL_Number"] = dl_number
            info["Date_of_Issue"] = doi 
            info["Valid_Till"] = valid_till
            info["Date_of_Birth"] = dob
        
        except Exception as e:
            info["Error"] = str(e)

        return info
        
    def exteacted_lines(self, extracted_text):
        lines = extracted_text.split('\n')
        processed_lines = []
        for line in lines:
            if line.strip():  # Only process non-empty lines
                words = line.split()
                processed_line = '\t'.join(words)
                processed_lines.append(processed_line)
        return '\n'.join(processed_lines)


if __name__ == "__main__":
    image_path = r"f:\LicenseTestFiles\id100.jpg" 
    extractor = LeafletDriverLicenseExtractor(image_path)
    info = extractor.info
    #extracted_text = extract_text_with_tabs(image_path)
    #info = extract_field_text(extracted_text)
    print(json.dumps(info, indent=2))
    #print("Extracted Text:\n", extracted_text)