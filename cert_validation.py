###################################################
### @Leaflet-2025 
### @version: 1.0.1
### @Check certificate Validity status
### #Initiated : Rajesh Bisht
###################################################

import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import ExtensionOID
import base64

class LeafletCertValidation:
    def  __init__(self):
        pass

    def load_pfx_certificate(self, pfx_path, password):
        certificate = None
        try:
            with open(pfx_path, 'rb') as f:
                pfx_data = f.read()
            
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                pfx_data, password.encode()
            )
        except Exception as ex:
            print(f"ex: {ex}")
        return certificate


    def check_certificate_validation(self, cert_path, password=None):
        info = {}
        try:
            certificate = self.load_pfx_certificate(cert_path, password)
            if(certificate == None):
                info['status'] = True
                info['message'] = 'unable load certificate.'
                return info

            info['subject'] = str(certificate.subject)
            info['serial_number'] = str(certificate.serial_number)
            info['not_valid_before'] = certificate.not_valid_before_utc.strftime('%B %d, %Y at %I:%M:%S %p UTC')
            info['not_valid_after'] = certificate.not_valid_after_utc.strftime('%B %d, %Y at %I:%M:%S %p UTC')
            info['status'] = True
            info['message'] = 'successfull'
        except Exception as ex:
            info['status'] = False
            info['message'] = str(ex)
        return info


if __name__ == "__main__":
    certpath = "IdenTrustSignCert.pfx"
    password = "Backup251330@IdenTrust"
    cvalid = LeafletCertValidation()
    resp = cvalid.check_certificate_validation(certpath, password)
   # jsonstr = json.dumps(resp)
    
    
