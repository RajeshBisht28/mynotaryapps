"""
# Initiated by @Rajesh Bisht
# Leaflet Technology - 2025 
# Required:  Enable CORS support
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
# Example:  CORS(app, origins=[openvidu_server_url])
 openvidu_server_url : dev.leafletcorp.com
"""
#OpenVidu Response Error Codes:
#409 - Conflict, session already exist
#401 - Unauthorized , key issue 
#400 - Bad Request, payoad issue
#403 - Forbidden, insufficient permissions
#404 - Not Found, Session, connection, or resource doesn't exist

import requests
import random
import json
import os
from requests.auth import HTTPBasicAuth

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "openvidu_config.json")

class OpenviduRequestApps:    
    def __init__(self, openvidu_secret, openvidu_server, logger, config_path=CONFIG_PATH):
        self.logger = logger
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            self.openvidu_server = config.get("url")
            self.openvidu_secret = config.get("key")
            self.recording_output = config.get("recording_output")
            self.recording_layout = config.get("recording_layout")
        except Exception as ex:
            logger.info(f"exception : initialize Openvidu class=> {ex}")
            
    
    def initializeSession(self, sessionId):        
        try:
            body = {
                'customSessionId': sessionId
            }
            response = requests.post(
                self.openvidu_server + "/openvidu/api/sessions",
                verify=False,
                auth=("OPENVIDUAPP", self.openvidu_secret),
                headers={'Content-type': 'application/json'},
                json=body
            )
            response.raise_for_status()
            return response.json()["sessionId"]
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 409:                
                try:
                    return err.response.json()["customSessionId"]
                except ValueError:                    
                    return sessionId
            else:
                return f"error: HTTP {err.response.status_code}:{err.response.text}"
            
    def createToken(self, sessionId):
        try:
            body = {}
            response = requests.post(
                self.openvidu_server + "/openvidu/api/sessions/" + sessionId + "/connection",
                verify=False,
                auth=("OPENVIDUAPP", self.openvidu_secret),
                headers={'Content-type': 'application/json'},
                json=body
            )
            response.raise_for_status()
            return response.json()["token"]
        except requests.exceptions.RequestException as err:
            return f"error: {str(err)}"
    
    def recordingStart(self, sessionId):
        try:
            random_part = str(random.randint(10000, 99000))
            recording_name = f"{sessionId}_{random_part}"
            body = {'session': sessionId, 
                    'name': recording_name, 
                    'hasAudio': True, 
                    'hasVideo': True, 
                    'frameRate': 25, 
                    'outputMode': self.recording_output, 
                    'recordingLayout': self.recording_layout,
                    'customLayout': "mylayouts"
                    }
            
            response = requests.post(
                self.openvidu_server + "/openvidu/api/recordings/start",
                verify=False,
                auth=("OPENVIDUAPP", self.openvidu_secret),
                headers={'Content-type': 'application/json'},
                json=body
            )
            
            if response.status_code == 400:
               return {'sessionId': sessionId, 'status': True, 'message': 'Problem with some body parameter.' }
            elif response.status_code == 409:
               return {'sessionId': sessionId, 'status': True, 'message': 'The session is not configured for using MediaMode ROUTED or it is already being recorded.' }
            elif response.status_code == 501:
               return {'sessionId': sessionId, 'status': True, 'message': 'Recording module is disabled.' }
            elif response.status_code == 404:
               return {'sessionId': sessionId, 'status': False, 'message': 'Session not found.' }
            elif response.status_code == 406:
               return {'sessionId': sessionId, 'status': False, 'message': 'Session has no connected participants.' }
            elif response.status_code == 422:
               return {'sessionId': sessionId, 'status': False, 'message': 'Invalid recording properties.' }
            else:
               message = f"{response.status_code}, Response: {response.text}"
               return {'sessionId': sessionId, 'status': False, 'message': message }
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return f"error: {str(err)}"
    
    def recordingStop(self, recording_id):
        try:            
            body = {}            
            response = requests.post(
                self.openvidu_server + f"/openvidu/api/recordings/stop/{recording_id}",
                verify=False,
                auth=("OPENVIDUAPP", self.openvidu_secret),
                headers={'Content-type': 'application/json'},
                json=body
            )
            
            if response.status_code == 200:
               return {'recordId': recording_id, 'status': False, 'message': 'The session has successfully stopped from being recorded.' }
            elif response.status_code == 406:
               return {'recordId': recording_id, 'status': False, 'message': 'Recording has starting status. Wait until started status before stopping the recording.' }
            elif response.status_code == 404:
               return {'recordId': recording_id, 'status': False, 'message': 'No recording exists for the passed Recording Id.' }
            elif response.status_code == 501:
               return {'recordId': recording_id, 'status': False, 'message': 'OpenVidu Server recording module is disabled: OPENVIDU_RECORDING configuration property is set to false.' }
            else:
               message = f"{response.status_code}, Response: {response.text}"
               return {'recordId': recording_id, 'status': False, 'message': message }
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return f"error: {str(err)}"
    
    def deleteSession(self, sessionId):
        try:
            url = self.openvidu_server + f"/openvidu/api/sessions/{sessionId}"
            response = requests.delete(url, auth=HTTPBasicAuth('OPENVIDUAPP', self.openvidu_secret), verify=False)
            
            if response.status_code == 204:
               return {'sessionId': sessionId, 'status': True, 'message': 'deleted' }
            elif response.status_code == 404:
               return {'sessionId': sessionId, 'status': False, 'message': 'Session not found' }
            else:
               message = f"{response.status_code}, Response: {response.text}"
               return {'sessionId': sessionId, 'status': False, 'message': message }

        except requests.exceptions.RequestException as err:
            return f"error: {str(err)}"
 
    
    def getRecordingInfo(self, recordingId):
        logger = self.logger
        try:
            logger.info(f"Openvidu-getRecordingInfo recordingId: {recordingId}")
            url = self.openvidu_server + f"/openvidu/api/recordings/{recordingId}"
            logger.info(f"Openvidu-recording request url: {url}") 
            ###response = requests.delete(url, auth=HTTPBasicAuth('OPENVIDUAPP', self.openvidu_secret), verify=False)
            response = requests.get(
                url, 
                auth=HTTPBasicAuth('OPENVIDUAPP', self.openvidu_secret), 
                verify=False
            )
            
            if response.status_code == 200:
               return response.json()
            else:
               message = f"{response.status_code}, Response: {response.text}"
               return {'recordingId': recordingId, 'status': False, 'message': message }

        except requests.exceptions.RequestException as err:
            return f"error: {str(err)}"    
        
    def debugTest(self, msg):
        print(f"msg : {msg}")
    

if __name__ == '__main__':
    openvidObj = OpenviduRequestApps("", "")
    sessionid = openvidObj.initializeSession("poc-demo-test")
    print(f"create session : {sessionid}")
    token = openvidObj.createToken(sessionid)
    print(f"createToken : {token}")