
### Leaflet technology


import datetime
import hashlib
import os
import requests
import logging
from typing import Optional
from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.timestamps import HTTPTimeStamper
from urllib.parse import urlparse, urlunparse
import base64
import urllib.parse
import hashlib
import json


class LeafletPDFDigitalSigner:
    """
    A class for digitally signing PDF documents with timestamps.
    """
    
    def __init__(
        self,
        pfx_path: str,
        pfx_password: bytes,
        tsa_url: str = "http://timestamp.identrust.com",  ##"http://timestamp.digicert.com",
        field_name: str = "Leaflet_DOCID_1090000000",
        signer_name: str = "Leaflet-eSign",
        reason: str = "Digitally verifiable PDF sign approval",
        location: str = "New DELHI, India",
        contact_info: str = "support@leafletcorp.com",
        md_algorithm: str = "sha256",
        embed_validation_info: bool = False
    ):
        """
        Initialize the PDF Digital Signer.
        
        Args:
            pfx_path (str): Path to the .pfx certificate file
            pfx_password (bytes): Password for the certificate as bytes
            tsa_url (str): Timestamp Authority URL
            field_name (str): Name of the signature field
            signer_name (str): Name of the signer
            reason (str): Reason for signing
            location (str): Location of signing
            contact_info (str): Contact information
            md_algorithm (str): Message digest algorithm
            embed_validation_info (bool): Whether to embed validation info
        """
        self.pfx_path = pfx_path
        self.pfx_password = pfx_password
        self.tsa_url = tsa_url
        self.field_name = field_name
        self.signer_name = signer_name
        self.reason = reason
        self.location = location
        self.contact_info = contact_info
        self.md_algorithm = md_algorithm
        self.embed_validation_info = embed_validation_info
        
        # Initialize logger with date-based file logging
        self.logger = self._setup_logger()
        
        # Initialize signer and timestamper
        self.signer = None
        self.timestamper = None
        
        try:
            self._initialize_components()
        except Exception as e:
            self.logger.error(f"Failed to initialize PDF signer: {str(e)}")
            raise
    
    def _setup_logger(self):
        """Setup logger with date-based file logging in sign_logs folder."""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Create sign_logs directory at the same level as the script
            log_dir = os.path.join(script_dir, 'sign_logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # Create date-based log filename (e.g., 31Jul25_sign.log)
            current_date = datetime.datetime.now()
            log_filename = f"{current_date.strftime('%d%b%y')}_sign.log"
            log_filepath = os.path.join(log_dir, log_filename)
            
            # Create logger
            logger = logging.getLogger(f"{__name__}_{id(self)}")  # Unique logger per instance
            logger.setLevel(logging.INFO)
            
            # Remove existing handlers to avoid duplicates
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # Create file handler
            file_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            logger.info(f"Logger initialized. Log file: {log_filepath}")
            return logger
            
        except Exception as e:
            # Fallback to basic logger if file logging fails
            fallback_logger = logging.getLogger(__name__)
            fallback_logger.error(f"Failed to setup file logging: {str(e)}")
            return fallback_logger
    
    def _initialize_components(self):
        """Initialize the signer and timestamper components."""
        try:
            # Validate certificate file exists
            if not os.path.exists(self.pfx_path):
                raise FileNotFoundError(f"Certificate file not found: {self.pfx_path}")
            
            # Load the certificate
            self.signer = signers.SimpleSigner.load_pkcs12(
                self.pfx_path,
                passphrase=self.pfx_password
            )
            self.logger.info("Certificate loaded successfully")
            
            # Initialize timestamper
            self.timestamper = HTTPTimeStamper(self.tsa_url)
            self.logger.info(f"Timestamper initialized with URL: {self.tsa_url}")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {str(e)}")
            raise
    
    def _create_signature_metadata(self) -> signers.PdfSignatureMetadata:
        """Create and return PDF signature metadata."""
        try:
            return signers.PdfSignatureMetadata(
                field_name=self.field_name,
                name=self.signer_name,
                reason=self.reason,
                location=self.location,
                contact_info=self.contact_info,
                md_algorithm=self.md_algorithm,
                embed_validation_info=self.embed_validation_info
            )
        except Exception as e:
            self.logger.error(f"Error creating signature metadata: {str(e)}")
            raise
    
    def upload_file(self, url:str, file_for_upload:str, file_name:str):
       
        try:
                with open(file_for_upload, "rb") as f:
                    files = {"file": (file_name, f, "application/pdf")}
                    response = requests.post(url, files=files)
                
                if response.status_code == 200 or response.status_code == 201:
                    upload_at = os.path.join(url, file_name)
                    self.logger.info(f"File uploaded successfully uploaded: {upload_at}")
                    return upload_at
                else:
                    self.logger.error(f"Upload failed with status code {response.status_code}")
                    self.logger.error(f"Response: {response}")
        except Exception as e:
                self.logger.error(f"Exception: upload_file {str(e)}")
        return response.text

    def fetch_root_url(self, url):
        try:
            normalized_url = url.replace("\\", "/")
            parsed = urlparse(normalized_url)
            path_without_file = os.path.dirname(parsed.path)
            base_url = urlunparse((parsed.scheme, parsed.netloc, path_without_file + '/', '', '', ''))
            return base_url
        except Exception as e:
            pass
        return None
    
    def get_base64_file(self, file_path):
        encoded = None
        with open(file_path, "rb") as f:
          encoded = base64.b64encode(f.read()).decode()
        return encoded


    def download_file(self, file_url:str) -> str:
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)

        folder_name = os.path.join(script_dir,"download_signpdf")
        url = file_url
        # Create folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        # Extract file name from URL or choose one explicitly
        file_name = url.split("/")[-1] 
        # Full path to save the file
        file_path = os.path.join(folder_name, file_name)
        
        # Download file
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)

            self.logger.info(f"File downloaded successfully to: {file_path}")
            return file_path
        else:
            self.logger.error(f"Failed to download file, status code: {response.status_code}")
        return None 
    
    def url_fix(self, input_file_url):
        url_raw = input_file_url
        url_fixed = url_raw.replace("\\", "/")
        base_url = url_fixed.rsplit("/", 1)[0]
        filename = url_fixed.rsplit("/", 1)[1]
        encoded_filename = urllib.parse.quote(filename)
        final_url = f"{base_url}/{encoded_filename}"
        self.logger.info(f"Fixed File Url : {final_url}")
        return final_url
        

    def sign_process(self, input_pdf_path: str):
        input_pdf_path = self.url_fix(input_pdf_path)
        try:
            in_file = self.download_file(input_pdf_path)
            if os.path.exists(in_file)==False:
               self.logger.error(f"in-file does not exist {in_file}")
               return ""

            original_path = in_file
            directory = os.path.dirname(original_path)
            original_filename = os.path.basename(original_path)
            base_name, ext = os.path.splitext(original_filename)
            new_filename = f"digital_sign_{base_name}{ext}"
            out_path = os.path.join(directory, new_filename)
            resp = self.sign_pdf(in_file, out_path)
            if(resp == False):
                return "Unable sign"
            url_upload = self.fetch_root_url(input_pdf_path)
            blob_64encode = self.get_base64_file(out_path) #self.upload_file(url_upload, out_path, new_filename)
            hashvalue = self.get_md5_hash(out_path)
            return json.dumps({"blob_64encode": blob_64encode, "hashvalue": hashvalue})

        except Exception as e:
            self.logger.error(f"Error during PDF sign-process: {str(e)}")
            return jsonify({"error": str(e)})


    def sign_pdf(self, input_pdf_path: str, output_pdf_path: str) -> bool:
        """
        Sign a PDF document.
        
        Args:
            input_pdf_path (str): Path to the input PDF file
            output_pdf_path (str): Path where the signed PDF will be saved
            
        Returns:
            bool: True if signing was successful, False otherwise
        """

        try:
            # Validate input file
            if not os.path.exists(input_pdf_path):
                raise FileNotFoundError(f"Input PDF file not found: {input_pdf_path}")
            
            # Validate output directory exists
            output_dir = os.path.dirname(output_pdf_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.logger.info(f"Created output directory: {output_dir}")
            
            # Check if components are initialized
            if not self.signer or not self.timestamper:
                raise RuntimeError("Signer components not properly initialized")
            
            # Create signature metadata
            metadata = self._create_signature_metadata()
            
            # Sign the PDF
            with open(input_pdf_path, "rb") as input_file:
                try:
                    writer = IncrementalPdfFileWriter(input_file)
                    pdf_signer = signers.PdfSigner(
                        metadata, 
                        signer=self.signer, 
                        timestamper=self.timestamper
                    )
                    
                    with open(output_pdf_path, "wb") as output_file:
                        pdf_signer.sign_pdf(writer, output=output_file)
                    
                    self.logger.info(f"PDF signed successfully: {output_pdf_path}")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Error during PDF signing process: {str(e)}")
                    # Clean up partial output file if it exists
                    if os.path.exists(output_pdf_path):
                        try:
                            os.remove(output_pdf_path)
                            self.logger.info("Cleaned up partial output file")
                        except:
                            pass
                    raise
                    
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {str(e)}")
            return False
        except PermissionError as e:
            self.logger.error(f"Permission denied: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during PDF signing: {str(e)}")
            return False
    
    def update_certificate(self, new_pfx_path: str, new_pfx_password: bytes):
        """
        Update the certificate used for signing.
        
        Args:
            new_pfx_path (str): Path to the new certificate file
            new_pfx_password (bytes): Password for the new certificate
        """
        try:
            if not os.path.exists(new_pfx_path):
                raise FileNotFoundError(f"New certificate file not found: {new_pfx_path}")
            
            # Test loading the new certificate
            test_signer = signers.SimpleSigner.load_pkcs12(
                new_pfx_path,
                passphrase=new_pfx_password
            )
            
            # If successful, update the instance variables
            self.pfx_path = new_pfx_path
            self.pfx_password = new_pfx_password
            self.signer = test_signer
            
            self.logger.info("Certificate updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating certificate: {str(e)}")
            raise
    
    def update_timestamp_url(self, new_tsa_url: str):
        """
        Update the timestamp authority URL.
        
        Args:
            new_tsa_url (str): New timestamp authority URL
        """
        try:
            # Test the new URL
            test_timestamper = HTTPTimeStamper(new_tsa_url)
            
            # If successful, update the instance variables
            self.tsa_url = new_tsa_url
            self.timestamper = test_timestamper
            
            self.logger.info(f"Timestamp URL updated to: {new_tsa_url}")
            
        except Exception as e:
            self.logger.error(f"Error updating timestamp URL: {str(e)}")
            raise
    
    def get_md5_hash(self, file_path):
        try:
            md5_hash = hashlib.md5()    
            with open(file_path, 'rb') as f:        
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
            
            return md5_hash.hexdigest()
        except Exception as e:
            return str(e)

def from_shellcommand():
    """Example usage of the PDFDigitalSigner class."""
    try:
        # Configuration parameters
        input_pdf_file = "https://uat.leafletcorp.com:2508/leafSign//temp//1753953907086/test.pdf"
        #r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\pythonTesting\tamper_test\ls100.pdf"
        pfx_certificate_file = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\certificateTesting\scripts\sample_certificate\IdenTrustEncryptionCert.pfx"
        pfx_password = b"Backup251330@IdenTrust"
        output_signed_pdf_file = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\pythonTesting\tamper_test\cls1_signed_ls100.pdf"
        
        # Create signer instance (logging is automatically configured)
        pdf_signer = LeafletPDFDigitalSigner(
            pfx_path=pfx_certificate_file,
            pfx_password=pfx_password,
            # You can customize other parameters here
            field_name="Leaflet_DOCID_1090000000",
            signer_name="Leaflet-eSign",
            reason="Digitally verifiable PDF sign approval",
            location="New DELHI, India",
            contact_info="support@leafletcorp.com"
        )
        
        # Sign the PDF
        success = pdf_signer.sign_process(input_pdf_file)
        print(f"response: {success}")

        if success:
            print("PDF signed successfully!")
        else:
            print("Failed to sign PDF. Check logs for details.")
            
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    from_shellcommand()