
import requests
import json
import os
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

class LeafletExperianVerify:
    def __init__(self, repo_file="ssn_question_repo.json"):
        self.repo_file = repo_file
        if not os.path.exists(self.repo_file):
            with open(self.repo_file, "w") as f:
                json.dump({}, f)
    
    def load_repo(self):
        with open(self.repo_file, "r") as f:
            return json.load(f)

    def store_info(self, user_data: dict):
        
        if "ssn_value" not in user_data:
            raise ValueError("user_data must include 'ssn_value'")

        ssn_value = str(user_data["ssn_value"])
        repo = self.load_repo()
        repo[ssn_value] = user_data
        self._save_repo(repo)

    def _save_repo(self, repo):
        with open(self.repo_file, "w") as f:
            json.dump(repo, f, indent=4)
    
    def verify_ssn_kba(self, input_data, repo_data):
        try:
            results = {}
            correct_count = 0
            ssnid = str(input_data["ssn_id"])

            if ssnid not in repo_data:
                return {"status": False, "msg": f"No pre-KBA process for user: {ssnid}"}

            repo = repo_data[ssnid]
            # Q1: Name check
            ans = input_data.get("Answer-1", "").strip().upper()
            name_match = ans in [n.upper() for n in repo["names"]]
            results["Q1_NameMatch"] = name_match
            if name_match: correct_count += 1
            
            # Q2: DOB (DD-MM)
            ans = input_data.get("Answer-2", "").strip()
            expected = f'{repo["dob"]["day"]}-{repo["dob"]["month"]}'
            dob_match = ans == expected
            results["Q2_DOBMatch"] = dob_match
            if dob_match: correct_count += 1
            # Q3: Street name
            ans = input_data.get("Answer-3", "").strip().upper()
            streets = [addr["street"].upper() for addr in repo["addresses"]]
            street_match = ans in streets
            results["Q3_StreetMatch"] = street_match
            if street_match: correct_count += 1

            # Q4: Last 4 digits of phone
            ans = input_data.get("Answer-4", "").strip()
            phones = [ph[-4:] for ph in repo["phones"]]
            phone_match = ans in phones
            results["Q4_PhoneMatch"] = phone_match
            if phone_match: correct_count += 1

            # Q5: First 4 digits of zipcode
            ans = input_data.get("Answer-5", "").strip()
            zips = [addr["zipCode"][:4] for addr in repo["addresses"]]
            zipcode_match = ans in zips
            results["Q5_ZipcodeMatch"] = zipcode_match
            if zipcode_match: correct_count += 1

            # Final summary
            results["TotalCorrect"] = correct_count
            results["VerificationStatus"] = "Success" if correct_count == 5 else "Failure"
            return results
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_access_token(self):
        try:
            token_url = "https://sandbox-us-api.experian.com/oauth2/v1/token"

            token_payload = {
                "username": "rbisht@leafletcorp.com",
                "password": "Leaflet@2025",
                "client_id": "4CGes7GK3dcpATiE7LzpKkjk2nhx9gek",
                "client_secret": "lsvOWaPUOV4yY5pu",
                "grant_type": "password"
            }

            token_headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            token_response = requests.post(token_url, data=token_payload, headers=token_headers)

            if token_response.status_code != 200:
                res = {
                    "access_token": token_response.status_code,
                    "message": token_response.text,
                    "status": False
                }
                return res
                
            token_data = token_response.json()
            access_token = token_data.get("access_token") 
            res = {
                    "access_token": access_token,
                    "message": token_response.text,
                    "status": True
                }
            return res
        except:
            pass
    
    ##### KBA testing ...
    def kba_api_testing(self, payload):
        try:
            resp_data = self.get_access_token()
            access_token = resp_data.get("access_token")
            social_url =  "https://api.experian.com.br/openapi/quiz/v1/quizzes" #  "https://api.experian.com.br/quiz/v1/quizzes"
            #payload['requestor'] = requestor
            #payload['addOns'] = addOns
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "companyId": "SBMYSQL",
                "clientReferenceId": "SBMYSQL"
            }
            response = requests.post(social_url, json=payload, headers=headers)
            return response
        except Exception as e:
            return {
                    "status": "error",
                    "message": str(e)
                } 
    
    def info_by_ssn(self, payload):
        try:
            
            resp_data = self.get_access_token()
            access_token = resp_data.get("access_token")
            # Step 2: Call Social Search API
            social_url = "https://sandbox-us-api.experian.com/consumerservices/social-search/v1/social-search"
        
            requestor = {
                    "subscriberCode": "2222222"
                }
            
            addOns = {
                        "directCheck": "Y",
                        "demographics": "Geocode and Phone",
                        "fraudShield": "Y"
                    }

            # payload = {
            #     "ssn": [
            #             {
            #             "ssn": "111111111"
            #             }
            #         ]
            #     }

            payload['requestor'] = requestor
            payload['addOns'] = addOns
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "companyId": "SBMYSQL",
                "clientReferenceId": "SBMYSQL"
            }

            response = requests.post(social_url, json=payload, headers=headers)
            ssn_value = payload["ssn"][0]["ssn"]

            resp = self.filter_club_response(response.text)
            resp['ssn_value'] = ssn_value
            self.store_info(resp)
            return resp
        except Exception as e:
            return {
                    "status": "error",
                    "message": str(e)
                }

    def filter_club_response(self, text):
        json_resp = {}
        data = json.loads(text)
        social_search = data.get("socialSearch", [])[0]
        names = []
        for n in social_search.get("consumerIdentity", {}).get("name", []):
            full_name = " ".join([n.get("firstName", ""), n.get("middleName", ""), n.get("surname", "")]).strip()
            names.append(full_name)

        # DOB
        dob_data = social_search.get("consumerIdentity", {}).get("dob", {})
        dob = {
            "day": dob_data.get("day"),
            "month": dob_data.get("month"),
            "year": dob_data.get("year")
        } if dob_data else None

        # Addresses
        addresses = []
        for a in social_search.get("addressInformation", []):
            addresses.append({
                "street": f"{a.get('streetPrefix', '')} {a.get('streetName', '')} {a.get('streetSuffix', '')}".strip(),
                "city": a.get("city"),
                "state": a.get("state"),
                "zipCode": a.get("zipCode")
            })

        # Phones
        phones = [p.get("number") for p in social_search.get("consumerIdentity", {}).get("phone", [])]

        # Fraud Flags
        fraud_flags = []
        for f in social_search.get("fraudShield", []):
            fraud_flags.extend(f.get("fraudShieldIndicators", {}).get("indicator", []))
        
        spouse = social_search.get("consumerIdentity", {}).get("spouseName")

        # Build extracted JSON
        extracted_info = {
            "names": names,
            "dob": dob,
            "addresses": addresses,
            "phones": phones,
            "spouse": spouse,
            "fraudFlags": fraud_flags
        }
        return extracted_info
        

if __name__ == "__main__":
    payload = {
                "ssn": [
                        {
                        "ssn": "111111111"
                        }
                    ]
                }

    kba_question_answer = {
        "ssn_id": "111111111",
        "Question-1": "What is your name?",
        "Answer-1": "WEI  BESSER",
        "Question-2": "your birth day and month (DD-MM)?",
        "Answer-2": "xxxxxxx",
        "Question-3": "Please write your street name?",
        "Answer-3": "xxxxxxx",
        "Question-4": "Mention last 4 digit of your phone number?",
        "Answer-4": "xxxxxxx",
        "Question-5": "What are first 4 digit of your zipcode?",
        "Answer-5": "xxxxxxx",
    }
    
    objssn = LeafletExperianVerify()
    repo = objssn.load_repo()
    ans = objssn.info_by_ssn(payload)
    #ans = objssn.verify_ssn_kba(kba_question_answer, repo)
    print(ans)
    #testing()
