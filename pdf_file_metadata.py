

import fitz
import datetime
import os
import logging
import json
from typing import Dict, List, Optional, Any
from pypdf import PdfReader


class LeafletPDFSignAnalyzer:
    """
    A class for analyzing PDF digital signatures with JSON output and comprehensive logging.
    """
    
    def __init__(self, log_prefix: str = "pdf_analysis"):
        """
        Initialize the PDF Analyzer with logging configuration.
        
        Args:
            log_prefix (str): Prefix for log filenames (default: "pdf_analysis")
        """
        self.log_prefix = log_prefix
        self.logger = self._setup_logger()
        
        self.logger.info("LeafletPDFSignAnalyzer initialized successfully")
    
    def _setup_logger(self):
        """Setup logger with date-based file logging in sign_logs folder."""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Create sign_logs directory at the same level as the script
            log_dir = os.path.join(script_dir, 'sign_logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # Create date-based log filename (e.g., 31Jul25_pdf_analysis.log)
            current_date = datetime.datetime.now()
            log_filename = f"{current_date.strftime('%d%b%y')}_{self.log_prefix}.log"
            log_filepath = os.path.join(log_dir, log_filename)
            
            # Create logger
            logger = logging.getLogger(f"{__name__}_{self.log_prefix}_{id(self)}")
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
    
    def _validate_file_path(self, file_path: str) -> bool:
        """
        Validate if the file path exists and is a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File does not exist: {file_path}")
                return False
            
            if not os.path.isfile(file_path):
                self.logger.error(f"Path is not a file: {file_path}")
                return False
            
            # Check file extension
            if not file_path.lower().endswith('.pdf'):
                self.logger.warning(f"File does not have .pdf extension: {file_path}")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                self.logger.error(f"File is empty: {file_path}")
                return False
            
            self.logger.info(f"File validation successful: {file_path} (Size: {file_size} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating file path {file_path}: {str(e)}")
            return False
    
    def extract_metadata(self, file_path: str) -> Optional[str]:
        """
        Extract metadata from a PDF file using PyMuPDF (fitz).
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Optional[str]: JSON string containing metadata or None if failed
        """
        try:
            self.logger.info(f"Starting metadata extraction for: {file_path}")
            
            # Validate file path
            if not self._validate_file_path(file_path):
                return json.dumps({
                    "status": "error",
                    "message": "File validation failed",
                    "file_path": file_path,
                    "metadata": {}
                }, indent=2)
            
            # Open PDF document
            doc = fitz.open(file_path)
            metadata = doc.metadata
            
            if not metadata:
                self.logger.warning(f"No metadata found in PDF: {file_path}")
                doc.close()
                return json.dumps({
                    "status": "success",
                    "message": "No metadata found in PDF",
                    "file_path": file_path,
                    "analysis_timestamp": datetime.datetime.now().isoformat(),
                    "metadata": {}
                }, indent=2)
            
            # Convert metadata to serializable format
            serializable_metadata = {}
            for key, value in metadata.items():
                if value is not None:
                    serializable_metadata[key] = str(value)
            
            self.logger.info(f"Successfully extracted metadata from: {file_path}")
            self.logger.info("=== PDF Metadata ===")
            
            for key, value in serializable_metadata.items():
                self.logger.info(f"{key}: {value}")
            
            doc.close()
            
            result = {
                "status": "success",
                "message": f"Successfully extracted {len(serializable_metadata)} metadata field(s)",
                "file_path": file_path,
                "analysis_timestamp": datetime.datetime.now().isoformat(),
                "metadata": serializable_metadata
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {file_path}: {str(e)}")
            try:
                if 'doc' in locals():
                    doc.close()
            except:
                pass
            
            error_result = {
                "status": "error",
                "message": f"Error extracting metadata: {str(e)}",
                "file_path": file_path,
                "analysis_timestamp": datetime.datetime.now().isoformat(),
                "metadata": {}
            }
            return json.dumps(error_result, indent=2)
    
    def check_digital_signatures(self, file_path: str) -> Optional[str]:
        """
        Check for digital signatures in a PDF file using pypdf.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Optional[str]: JSON string containing signature information or None if failed
        """
        try:
            self.logger.info(f"Starting digital signature check for: {file_path}")
            
            # Validate file path
            if not self._validate_file_path(file_path):
                return json.dumps({
                    "status": "error",
                    "message": "File validation failed",
                    "file_path": file_path,
                    "signatures": []
                }, indent=2)
            
            # Open PDF with pypdf
            reader = PdfReader(file_path)
            signatures = []
            
            # Check if AcroForm exists
            if "/Root" not in reader.trailer:
                self.logger.warning(f"No /Root found in PDF trailer: {file_path}")
                return json.dumps({
                    "status": "success",
                    "message": "No /Root found in PDF trailer",
                    "file_path": file_path,
                    "signatures": []
                }, indent=2)
            
            root = reader.trailer["/Root"]
            if "/AcroForm" not in root:
                self.logger.info(f"No AcroForm found in PDF: {file_path}")
                return json.dumps({
                    "status": "success",
                    "message": "No AcroForm found in PDF",
                    "file_path": file_path,
                    "signatures": []
                }, indent=2)
            
            acroform = root["/AcroForm"]
            fields = acroform.get("/Fields", [])
            
            if not fields:
                self.logger.info(f"No form fields found in PDF: {file_path}")
                return json.dumps({
                    "status": "success",
                    "message": "No form fields found in PDF",
                    "file_path": file_path,
                    "signatures": []
                }, indent=2)
            
            # Check each field for digital signatures
            for i, field in enumerate(fields):
                try:
                    field_obj = field.get_object()
                    field_type = field_obj.get("/FT")
                    
                    if field_type == "/Sig":
                        self.logger.info(f"Digital signature field found at index {i}")
                        
                        signature_info = {
                            "field_index": i,
                            "field_name": str(field_obj.get("/T", "Unknown")) if field_obj.get("/T") else None,
                            "field_type": str(field_type),
                            "name": None,
                            "location": None,
                            "reason": None,
                            "contact_info": None,
                            "signing_date": None,
                            "byte_range": None,
                            "signature_present": False,
                            "error": None
                        }
                        
                        # Get signature dictionary
                        sig_dict = field_obj.get("/V")
                        if sig_dict:
                            try:
                                sig_obj = sig_dict.get_object()
                                signature_info.update({
                                    "name": str(sig_obj.get("/Name")) if sig_obj.get("/Name") else None,
                                    "location": str(sig_obj.get("/Location")) if sig_obj.get("/Location") else None,
                                    "reason": str(sig_obj.get("/Reason")) if sig_obj.get("/Reason") else None,
                                    "contact_info": str(sig_obj.get("/ContactInfo")) if sig_obj.get("/ContactInfo") else None,
                                    "signing_date": str(sig_obj.get("/M")) if sig_obj.get("/M") else None,
                                    "byte_range": list(sig_obj.get("/ByteRange")) if sig_obj.get("/ByteRange") else None,
                                    "signature_present": True
                                })
                                
                                self.logger.info(f"Digital signature found: {signature_info.get('name', 'Unknown')}")
                                        
                            except Exception as e:
                                self.logger.error(f"Error reading signature object: {str(e)}")
                                signature_info["error"] = f"Could not read signature object: {str(e)}"
                        else:
                            self.logger.warning("Signature field found but no signature value present")
                            signature_info["error"] = "No signature value present"
                        
                        signatures.append(signature_info)
                    
                except Exception as e:
                    self.logger.error(f"Error processing field at index {i}: {str(e)}")
                    continue
            
            # Create final JSON response
            result = {
                "status": "success",
                "message": f"Found {len(signatures)} digital signature field(s)" if signatures else "No digital signature fields found",
                "file_path": file_path,
                "analysis_timestamp": datetime.datetime.now().isoformat(),
                "total_signatures": len(signatures),
                "signatures": signatures
            }
            
            self.logger.info(f"Analysis complete: {len(signatures)} signature(s) found")
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Error checking digital signatures in {file_path}: {str(e)}")
            error_result = {
                "status": "error",
                "message": f"Error checking digital signatures: {str(e)}",
                "file_path": file_path,
                "analysis_timestamp": datetime.datetime.now().isoformat(),
                "signatures": []
            }
            return json.dumps(error_result, indent=2)
    
    def analyze_pdf(self, file_path: str) -> str:
        """
        Perform complete PDF analysis including metadata and digital signatures.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: JSON string containing complete analysis results
        """
        try:
            self.logger.info(f"Starting complete PDF analysis for: {file_path}")
            
            analysis_result = {
                "status": "success",
                "message": "PDF analysis completed",
                "file_path": file_path,
                "analysis_timestamp": datetime.datetime.now().isoformat(),
                "metadata_result": None,
                "signatures_result": None,
                "errors": []
            }
            
            # Extract metadata
            try:
                metadata_json = self.extract_metadata(file_path)
                if metadata_json:
                    analysis_result["metadata_result"] = json.loads(metadata_json)
            except Exception as e:
                error_msg = f"Failed to extract metadata: {str(e)}"
                self.logger.error(error_msg)
                analysis_result["errors"].append(error_msg)
            
            # Check digital signatures
            try:
                signatures_json = self.check_digital_signatures(file_path)
                if signatures_json:
                    analysis_result["signatures_result"] = json.loads(signatures_json)
            except Exception as e:
                error_msg = f"Failed to check digital signatures: {str(e)}"
                self.logger.error(error_msg)
                analysis_result["errors"].append(error_msg)
            
            # Update status if there were errors
            if analysis_result["errors"]:
                analysis_result["status"] = "partial_success" if (analysis_result["metadata_result"] or analysis_result["signatures_result"]) else "error"
                analysis_result["message"] = f"Analysis completed with {len(analysis_result['errors'])} error(s)"
            
            self.logger.info(f"PDF analysis completed for: {file_path}")
            return json.dumps(analysis_result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Error during complete PDF analysis: {str(e)}")
            error_result = {
                "status": "error",
                "message": f"Analysis failed: {str(e)}",
                "file_path": file_path,
                "analysis_timestamp": datetime.datetime.now().isoformat(),
                "metadata_result": None,
                "signatures_result": None,
                "errors": [f"Analysis failed: {str(e)}"]
            }
            return json.dumps(error_result, indent=2)
    
    def print_analysis_summary(self, analysis_json: str):
        """
        Print a formatted summary of the analysis results from JSON.
        
        Args:
            analysis_json (str): JSON string from analyze_pdf method
        """
        try:
            analysis_result = json.loads(analysis_json)
            
            print(f"\n{'='*50}")
            print(f"PDF ANALYSIS SUMMARY")
            print(f"{'='*50}")
            print(f"File: {analysis_result.get('file_path', 'Unknown')}")
            print(f"Analysis Time: {analysis_result.get('analysis_timestamp', 'Unknown')}")
            print(f"Status: {analysis_result.get('status', 'Unknown')}")
            print(f"Message: {analysis_result.get('message', 'No message')}")
            
            # Print metadata summary
            metadata_result = analysis_result.get('metadata_result')
            if metadata_result and metadata_result.get('status') == 'success':
                metadata = metadata_result.get('metadata', {})
                print(f"\nMetadata Fields Found: {len(metadata)}")
                for key, value in metadata.items():
                    print(f"  {key}: {value}")
            else:
                print("\nNo metadata found or extraction failed")
            
            # Print signature summary
            signatures_result = analysis_result.get('signatures_result')
            if signatures_result and signatures_result.get('status') == 'success':
                signatures = signatures_result.get('signatures', [])
                print(f"\nDigital Signatures Found: {len(signatures)}")
                for i, sig in enumerate(signatures, 1):
                    print(f"\n  Signature {i}:")
                    print(f"    Field Name: {sig.get('field_name', 'N/A')}")
                    print(f"    Name: {sig.get('name', 'N/A')}")
                    print(f"    Location: {sig.get('location', 'N/A')}")
                    print(f"    Reason: {sig.get('reason', 'N/A')}")
                    print(f"    Contact: {sig.get('contact_info', 'N/A')}")
                    print(f"    Date: {sig.get('signing_date', 'N/A')}")
                    print(f"    Signature Present: {sig.get('signature_present', False)}")
                    if sig.get('error'):
                        print(f"    Error: {sig.get('error')}")
            else:
                print("\nNo digital signatures found")
            
            # Print errors if any
            if analysis_result.get('errors'):
                print(f"\nErrors encountered:")
                for error in analysis_result['errors']:
                    print(f"  - {error}")
            
            print(f"{'='*50}\n")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON for summary: {str(e)}")
            print(f"Error parsing analysis results: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error printing analysis summary: {str(e)}")
            print(f"Error displaying analysis summary: {str(e)}")
    
    def get_signatures_only_json(self, file_path: str) -> str:
        """
        Get only digital signature information in JSON format (simplified method).
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: JSON string containing only signature information
        """
        return self.check_digital_signatures(file_path)
    
    def get_metadata_only_json(self, file_path: str) -> str:
        """
        Get only metadata information in JSON format (simplified method).
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: JSON string containing only metadata information
        """
        return self.extract_metadata(file_path)


def main():
    """Example usage focusing only on digital signatures JSON output."""
    try:
        # Create analyzer instance
        analyzer = PDFAnalyzer(log_prefix="pdf_analysis")
        
        # File to analyze
        file_path = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\pythonTesting\tamper_test\cls1_signed_ls100.pdf"
        
        # Get digital signatures as JSON (main focus)
        signatures_json = analyzer.check_digital_signatures(file_path)
        print("================================================")
        # Output only the JSON result
        print(signatures_json)
        print("================================================")
    except Exception as e:
        # Return error as JSON format
        error_result = {
            "status": "error",
            "message": f"Error in main execution: {str(e)}",
            "file_path": "",
            "analysis_timestamp": datetime.datetime.now().isoformat(),
            "signatures": []
        }
        print(json.dumps(error_result, indent=2))


if __name__ == "__main__":
    main()