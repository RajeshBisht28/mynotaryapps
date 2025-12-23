##################################333
####### USA Pasport extractor using "MRZ READER" ##################3
#########################################################################3

from passporteye import read_mrz
import pytesseract
from PIL import Image
import cv2
import re
import json
from dateutil import parser
import warnings
from datetime import datetime


warnings.filterwarnings('ignore')

class LleafletUSAPassportDataExtractor:
    def __init__(self):
        pass

    def extract_us_passport_data(self, img_path):
        data = self.extract_mrz_fields(img_path)
        if data:
            data['method'] = 'MRZ'
            return data
        return None
    
    def extract_mrz_fields(self, img_path):
        try:
            mrz = read_mrz(img_path)
            if not mrz:
                return None
            data = mrz.to_dict()
            nat = data.get('nationality','').strip().upper()
            rowtext = data.get('raw_text', '')
            lines = rowtext.split("\n")
            upper_textlength = len(lines[0])
            lower_textlength = len(lines[1])
        
            if nat in ('USA', 'US ', 'UNITED STATES', 'UNITED STATES OF AMERICA'):
                # Standardize field names
                res = {
                    'Nationality': data.get('nationality', ''),
                    'Surname': data.get('surname', ''),
                    'Name': data.get('names', ''),
                    'Passport Number': data.get('number', ''),
                    'Date of Birth': self.parse_mrz_date(data.get('date_of_birth', ''), 'birth'),
                    'Gender': data.get('sex', ''),
                    'Expiration Date': self.parse_mrz_date(data.get('expiration_date', ''), 'expiry'),
                    'valid_number': data.get('valid_number'),
                    'valid_expiration_date': data.get('valid_expiration_date', ''),
                    'valid_score': data.get('valid_score', ''),
                    'check_composite': data.get('check_composite', ''),
                    'valid_composite': data.get('valid_composite'),
                    'raw_text': rowtext,
                    'upper_textlength': upper_textlength,
                    'lower_textlength': lower_textlength,
                }
                return res
            else:
                return None
        except Exception as e:
            return str(e)
    
    def parse_birth_date(self, date_string):
        try:
            # Parse the date assuming the year is in the range 1900-2099
            date = parser.parse(date_string, yearfirst=True).date()
            # Adjust the year if it falls outside the expected range
            if date.year >= 2000:
                date = date.replace(year=date.year - 100)
            return date.strftime('%d/%m/%Y')
        except ValueError:
            return None
    
    def parse_mrz_date(self, date_str, date_type):
        """Parse MRZ YYMMDD into full date with century correction."""
        yy = int(date_str[0:2])
        mm = int(date_str[2:4])
        dd = int(date_str[4:6])

        # Start with 1900-based year
        year = 1900 + yy
        parsed = datetime(year, mm, dd)

        now = datetime.now()

        if date_type == "birth":
            # Birthdate must not be in future → if > now, subtract 100 years
            if parsed > now:
                parsed = datetime(year - 100, mm, dd)

        elif date_type == "expiry":
            # Expiry date usually within next 20 years
            if parsed < now.replace(year=now.year - 20):  
                parsed = datetime(year + 100, mm, dd)

        return parsed.strftime("%d/%m/%Y")


if __name__ == '__main__':
    img = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\testfiles\us_passports_img\enhance passport photo page ID.png" #enhance_uspass200.png"
    uspass_obj = LleafletUSAPassportDataExtractor()
    res = uspass_obj.extract_us_passport_data(img)
    print(json.dumps(res, indent=2))
