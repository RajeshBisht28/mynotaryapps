###################################################
### @Leaflet-2025 
### @version: 1.0.1
### @Check certificate revocation status
### #Initiated : Rajesh Bisht
###################################################
"""
# Class Name: LeafletCertVarification
# Constructor : LeafletCertVarification(certificate_file_path)
# return type json Object: {"message": "unable load certificate.", "revocation": "NA", "status": false}
# Main mthod : check_certificate_revocation

"""

import subprocess
import tempfile
import requests
import os
import sys
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.ocsp import OCSPRequestBuilder
from cryptography.hazmat.primitives import serialization
from pathlib import Path
import json


class LeafletCertVarification:
    def  __init__(self, file_path=None):
        self.file_path = file_path
        self.info = {}
    
    def get_extention(self, file_path):
        extension = Path(filename).suffix

    def check_certificate_revocation(self):
        self.info['message'] = ''
        self.info['revocation'] = 'NA'
        ca_cet_path = self.file_path
        try:            
            cert = self.load_certificate(ca_cet_path)
            if(cert == None):           
               self.info['status'] = False
               self.info['message'] = "unable load certificate."
               return self.info
            
            ocsp_url = self.get_ocsp_url(cert)
            if(ocsp_url == None):          
              return self.info

            issuer_url = self.get_issuer_url(cert)
            if(issuer_url == None):
              self.info['status'] = False          
              return self.info
            
            issuer_info = self.download_binary_certificate(issuer_url)
            
            ocsp_resp = self.ocsp_check_revocation(cert, issuer_info, ocsp_url)
            status = ocsp_resp.certificate_status
            self.info['status'] = True        
            if status == x509.ocsp.OCSPCertStatus.GOOD:
                self.info['revocation'] = 'VALID'
            elif status == x509.ocsp.OCSPCertStatus.REVOKED:
                self.info['revocation'] = 'REVOKED'
            else:
                self.info['revocation'] = 'UNKNOWN'
        except Exception as ex:
               self.info['message'] = str(ex)
        return self.info

    def load_certificate(self, ca_cet_path):
        try:
            with open(ca_cet_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read(), default_backend())
                return cert
        except Exception as e:
            self.info['message'] = str(e)
        return None

    def get_ocsp_url(self, cert):
        ocsp_url = None
        try:
            for ext in cert.extensions:
                if isinstance(ext.value, x509.AuthorityInformationAccess):
                    for access in ext.value:
                        if access.access_method == x509.AuthorityInformationAccessOID.OCSP:
                            ocsp_url = access.access_location.value
        except Exception as e:
            self.info['message'] = str(e)        
        return ocsp_url

    def get_issuer_url(self, cert):
        issuer_url = None
        try:            
            for ext in cert.extensions:
                if isinstance(ext.value, x509.AuthorityInformationAccess):
                    for access in ext.value:
                        if access.access_method == x509.AuthorityInformationAccessOID.CA_ISSUERS:
                            issuer_url = access.access_location.value
        except Exception as e:
            self.info['message'] = str(e)

        return issuer_url

    def  ocsp_url_check(self, url):
         resp = requests.get(issuer_url)
         if resp.status_code != 200:
            return False

         return True
    
    def download_binary_certificate(self, issuer_url):
        resp = requests.get(issuer_url)
        issuer_path = None
        issuer_info = None
        try:
            if resp.status_code != 200:
                self.info['message'] = "Failed to download issuer certificate"           
                return issuer_info

            with tempfile.NamedTemporaryFile(delete=False, suffix=".p7c") as f:
                f.write(resp.content)
                issuer_path = f.name
            
            pem_path = issuer_path + ".pem"
            subprocess.run([
                "openssl", "pkcs7",
                "-print_certs",
                "-inform", "DER",
                "-in", issuer_path,
                "-out", pem_path
            ], check=True)
            
            with open(pem_path, "rb") as f:
                issuer_info = x509.load_pem_x509_certificate(f.read(), default_backend())
            
            os.remove(issuer_path)
            os.remove(pem_path)
        except Exception as e:
            sef.info['message'] = str(e)
        return issuer_info

    def  ocsp_check_revocation(self, cert, issuer, ocsp_url):
        ocsp_resp = None 
        try:
            builder = OCSPRequestBuilder()
            builder = builder.add_certificate(cert, issuer, cert.signature_hash_algorithm)
            ocsp_req = builder.build()

            headers = {
                "Content-Type": "application/ocsp-request",
                "Accept": "application/ocsp-response"
            }
            resp = requests.post(
                ocsp_url,
                data=ocsp_req.public_bytes(encoding=serialization.Encoding.DER),
                headers=headers
            )
            ocsp_resp = x509.ocsp.load_der_ocsp_response(resp.content)
            return ocsp_resp
        except Exception as e:
            self.info['message'] = str(e)
            return ocsp_resp


########### Testing usage #################
def write_result(file_path, content):
    result_path = os.path.join(os.path.dirname(file_path), "result.txt")
    with open(result_path, 'w') as f:
        f.write(content)

#### For run as command ######
if __name__ == "__main__":
    arguments = sys.argv
    #cert_path = 'cert.pem' 
    cert_path = arguments[1]       
    objC = LeafletCertVarification(cert_path)
    json_obj = objC.check_certificate_revocation()
    json_string = json.dumps(json_obj)
    write_result(cert_path, json_string)
    #print(json_string)
