
###########################################
"""
@Leaflet version 1.0.1
@Date : 30 JUN 2025
@Initiated: Bisht Rajesh
@Notary Services API
"""
#############################################

#### Comman imports
from flask import Flask, request, Response, jsonify, send_file, abort, render_template
from datetime import datetime
import logging
import os
import subprocess
import datetime
import json
import threading
import random
import string
import qrcode
import base64
import uuid
import io

os.environ['HF_HOME'] = "f:/python_model_cache/huggingface"
os.environ['TORCH_HOME'] = "f:/python_model_cache/torch"
os.environ['TFHUB_CACHE_DIR'] = "f:/python_model_cache/tensorflow"
os.environ['NLTK_DATA'] = "f:/python_model_cache/nltk_data"

#### logging implementation 
current_filedir = os.path.dirname(__file__)
log_folder_name = "notary_logs"
log_directory_path = os.path.join(current_filedir, log_folder_name)
if not os.path.exists(log_directory_path):
    os.makedirs(log_directory_path, exist_ok=True)
    
FACE_IDENTITY = 'FACE_IDENTITY'
if not os.path.exists(FACE_IDENTITY):
    os.makedirs(FACE_IDENTITY)
    
current_date = datetime.datetime.now()
date_str = current_date.strftime("%d%b%Y")
log_file_base_name = f"notary_log_{date_str}.log"
log_file_full_path = os.path.join(log_directory_path, log_file_base_name)

logging.basicConfig(filename=log_file_full_path,
                    format='%(asctime)s %(message)s',
                    filemode='a')
                    
logger = logging.getLogger('notaryapplicationLog')
logger.setLevel(logging.DEBUG)

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DRIVE_FOLDER = 'DriveLicenses'
if not os.path.exists(DRIVE_FOLDER):
    os.makedirs(DRIVE_FOLDER)
    
@app.route('/')
def endpoint_check():
    logger.debug("End point check") 
    return "<h1>Welcome ! Leaflet Notary ver-4.2.2</h1>"

@app.route('/api/', methods=['GET'])
def home():
    logger.debug("API  point check")
    return "<h1>Leaflet Notary API. ver-102</h1>"


@app.route('/api/test', methods=['GET'])
def test():
    return "<h1> Notary testing tags...ver-101 </h1>"

##################### Openvidu Requests / Response ################
import requests
from openvidu_apps import OpenviduRequestApps

@app.route('/api/openvidu/api/sessions', methods=['POST'])
def initializeSession():
    try:
        data = request.get_json()
        sessionId = data.get('customSessionId')
        openvidObj = OpenviduRequestApps("","", logger)
        response = openvidObj.initializeSession(sessionId)
        result = {
            'session': response
        }
        return result
    except Exception as e:
        logger.error('Initialized  session:', exc_info=e)
        return jsonify({"error": str(e)})
        
@app.route('/api/openvidu/api/sessions/<sessionId>/connection', methods=['POST'])
def createToken(sessionId):
    try:
        openvidObj = OpenviduRequestApps("","", logger)
        response = openvidObj.createToken(sessionId)
        result = {
            'token': response
        }
        return result
    except Exception as e:
        logger.error('Create Token:', exc_info=e)
        return jsonify({"error": str(e)})


@app.route('/api/openvidu/api/recordings/start', methods=['POST'])
def openvidu_start_recording():
    logger.info("[START] : openvidu_start_recording")
           
    try:
        data = request.get_json()
        sessionId = data.get('sessionId')
        openvidObj = OpenviduRequestApps("","", logger)
        response = openvidObj.recordingStart(sessionId)
        logger.info("[END] : openvidu_start_recording")
        return response
        
    except Exception as e:
        logger.error('openvidu_start_recording:', exc_info=e)
        return jsonify({"error": str(e)})


@app.route('/api/openvidu/api/recordings/<recordingId>')
def openvidu_get_recording_info(recordingId):
    logger.info(f"Get recording info recordingId: {recordingId}")
    try:     
        openvidObj = OpenviduRequestApps("","", logger)
        response = openvidObj.getRecordingInfo(recordingId)
        try:
            rec_url = response.get('url')
            logger.info(f"Response recodring url: {rec_url}") 
        except Exception as ex:
            logger.error('exception recording url:', exc_info=ex)
            
        return response
        
    except Exception as e:
        logger.error('openvidu_get_recording_info:', exc_info=e)
        return jsonify({"error": str(e)})

@app.route('/api/openvidu/api/recordings/stop/<recordingId>', methods=['POST'])
def openvidu_stop_recording(recordingId):
    logger.info(f"Stop recording  recordingId: {recordingId}")
    try:        
        openvidObj = OpenviduRequestApps("","", logger)
        response = openvidObj.recordingStop(recordingId)
        return response
        
    except Exception as e:
        logger.error('openvidu_stop_recording:', exc_info=e)
        return jsonify({"error": str(e)})
        
@app.route('/api/openvidu/api/sessions/<session_id>', methods=['POST'])
def openvidu_delete_session():
    try:        
        openvidObj = OpenviduRequestApps("","", logger)
        response = openvidObj.deleteSession(session_id)
        return response
        
    except Exception as e:
        logger.error('openvidu_delete_session:', exc_info=e)
        return jsonify({"error": str(e)}) 

############## End: OpenVidu API #############

############ Face detection no need : import anything in this file #####
import random
import time
from face_detect_yolo import LeafletFaceDetectImage

## @Virtual environment python executable path 
ENOTARY_ENV_EXE_PATH = r"F:\IISsites\notary_vir_env\Scripts\python.exe"
## @python script file path
FACE_DETECT_SCRIPTS_PATH = "face_detect_yolo.py"

@app.route('/api/notary/blob/face-detect', methods=['POST'])
def face_crop_blob():
    logger.error("face crop blob: api called")
    try:
        imageBase64Content = data.get('imageBase64Content')
        image_path1 = create_image_path_from_base4Str(FACE_IDENTITY, imageBase64Content, "detect")
        timestamp_part = str(int(time.time()))[-4:]
        random_part = str(random.randint(10, 99))
        random_folder = timestamp_part + random_part
        saved_path = os.path.join(FACE_IDENTITY, random_folder, "face_detect.png")
        model_path = r"yolo_models/arnabdharYOLOv8-Face-Detection.pt"
        ov = LeafletFaceDetectImage(model_path=model_path, logger=logger)
        imagename =  ov.get_face_image_path(image_path, saved_path)
        blob_64encode = get_base64_file(output_filename)
        if os.path.exists(saved_path):
           return jsonify({
                'status': True,
                'imagepath': blob_64encode
            })
        else:
            return jsonify({
                'status': False,
                'imagepath': "not detected."
            })    
    except:
        logger.error(f"face crop blob exp: {str(e)}")
        return jsonify({'status': 'error', 'imagepath': str(e)}), 500
    

@app.route('/api/notary/face-detect', methods=['POST'])
def face_crop_from_image():    
    logger.error("face_crop_from_image: api called")
    try:
        data = request.get_json()
        image_path = data.get('imagepath')
        save_dir = data.get('savedir')        
        timestamp_part = str(int(time.time()))[-4:]
        random_part = str(random.randint(10, 99))
        random_folder = timestamp_part + random_part
        saved_path = os.path.join(save_dir, random_folder, "face_detect.png")
        model_path = r"yolo_models/arnabdharYOLOv8-Face-Detection.pt"
        ov = LeafletFaceDetectImage(model_path=model_path)
        imagename =  ov.get_face_image_path(image_path, saved_path)
        if os.path.exists(saved_path):
            return jsonify({
                'status': "true",
                'imagepath': saved_path
            })
        else:
            return jsonify({
                'status': "false",
                'imagepath': saved_path
            }), 500
            
    except Exception as e:
        logger.error(f"exp: {str(e)}")
        return jsonify({'status': 'error', 'imagepath': str(e)}), 500


@app.route('/api/notary/face-identity', methods=['POST'])
def face_identity_check():
    logger.error("face_identity_check: api called") 
    status = False     
    try:
        data = request.get_json()
        image_path1 = data.get('imagepath_1')
        image_path2 = data.get('imagepath_2')
        save_dir = os.path.dirname(image_path2)
        timestamp_part = str(int(time.time()))[-4:]
        random_part = str(random.randint(10, 99))
        random_folder = timestamp_part + random_part
        saved_path = os.path.join(save_dir, random_folder, "faceIdentity.txt")
        model_path = r"yolo_models/arnabdharYOLOv8-Face-Detection.pt"
        ov = LeafletFaceDetectImage(model_path=model_path)     
        result_status = ov.face_identity(image_path1, image_path2)
        logger.error(f"result_status => face_identity_check: {result_status}")           
        return result_status
            
    except Exception as e:
        logger.error(f"Exception => face_identity_check : {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/notary/blob/face-identity', methods=['POST'])
def identity_check_face_blob():
    logger.info("START API CALL]: identity check face blob") 
    status = False 
    image_path1 = 'img-1'
    image_path2 = 'img-2'
    try:
        data = request.get_json()
        idBase64Content = data.get('idBase64Content')
        faceBase64Content = data.get('faceBase64Content')
        image_path1 = create_image_path_from_base4Str(FACE_IDENTITY, idBase64Content, "base")
        logger.debug(f"face identity blob: image path-1: {image_path1}")
        image_path2 = create_image_path_from_base4Str(FACE_IDENTITY, faceBase64Content, "face")
        logger.debug(f"face identity blob: image_path2: {image_path2}")
        save_dir = os.path.dirname(image_path2)
        timestamp_part = str(int(time.time()))[-4:]
        random_part = str(random.randint(10, 99))
        random_folder = timestamp_part + random_part
        saved_path = os.path.join(save_dir, random_folder, "faceIdentity.txt")
        model_path = r"yolo_models/arnabdharYOLOv8-Face-Detection.pt"
        ov = LeafletFaceDetectImage(model_path=model_path, logger=logger)     
        status = ov.face_detect_and_identity(image_path1, image_path2)
        logger.debug(f"Status => identity check face blob: {status}")
        return status
        
    except Exception as e:
        logger.error(f"Exception =>identity check face blob: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
  
######################## END Face detection #####################
################### BEGIN: Enotary Seal #####################

import json
import random
import os 
import time
import logging
from notary_seal_circle import LeafletNotarySeal
from notary_seal_rect import LeafletNotaryStampGeneratorCairo


@app.route('/api/notary/seal-create', methods=['POST'])
def enotary_seal_creation():
    logger.info("Start enotary_seal_creation")
    #outdir = Path("seal_output")
    outdir = "seal_output"
    os.makedirs(outdir, exist_ok=True)
    #outdir.mkdir(parents=True, exist_ok=True)
    request_json = {}
    
    try:
        data = request.get_json()
        data['outDir'] = outdir
        sealStyle = data.get('sealStyle')
        logger.info(f"enotary_seal_creation sealStyle : {sealStyle}")
        data['outDir'] = outdir
        if(sealStyle.lower()== "circle"):
            return circle_enotary_seal_creation(data)
        elif(sealStyle.lower()=="rectangle"):
            return rectangle_notary_seal_creation(data)
        else:
            return jsonify({'status': 'Invalid style of seal.', 'outpath': ' '})

    except Exception as e:
        return jsonify({'status': 'error', 'outpath': str(e)}), 500


############# NOTARY SEAL CREATION -- HELPER FUNCTION ##################
def circle_enotary_seal_creation(data):    
    random_part = str(random.randint(100000, 900000))
    create_status = False 
    blob_64encode = None   
    try:        
        outDir = data.get('outDir')
        output_filename = os.path.join(outDir, f"notarySeal_{random_part}.png")
        data['upperCircleText'] = data['sealUpperText']
        data['lowerCircleText'] = data['sealLowerText']
        upper_circle_text = data.get('sealUpperText')
        lower_circle_text = data.get('sealLowerText')
        notaryId = data.get('notaryId')
        expireOn = data.get('expireOn')        
        data['outFile'] = output_filename         
        json_str = json.dumps(data)
        clobj = LeafletNotarySeal()
        response = clobj.mainprocess(logger, json_str)
        resp_Str = json.dumps(response)
        logger.debug(f"Circle Seal response=> {resp_Str}")
        
        if os.path.exists(output_filename):
            blob_64encode = get_base64_file(output_filename)
            create_status = True
            return jsonify({
                'status': str(create_status),
                'outpath': blob_64encode
            })
        else:
            return jsonify({
                'status': str(create_status),
                'outpath': ' '
            }), 500
            
    except Exception as e:
        return jsonify({
                'status': str(e),
                'outpath': blob_64encode
            })


def rectangle_notary_seal_creation(data):
    logger.debug(f"Request notary_seal_rect_creation")
    random_part = str(random.randint(100000, 900000))
    create_status = False
    blob_64encode = None   
    
    try:
        data['topCurevedText'] = data['sealUpperText'] 
        data['bottomCurvedText'] = data['sealLowerText'] 
        data['notaryName'] = data['sealName']
        outDir = data.get('outDir')
        output_filename = os.path.join(outDir, f"notarySealRect_{random_part}.png")                
        data['outFile'] = output_filename 
        json_str = json.dumps(data)
        logger.debug(f"notary_seal_rect_creation : json_str=> {json_str}")
        logger.debug(f"Rectangle Seal json_str => {json_str}")
        objNotaryClass = LeafletNotaryStampGeneratorCairo(width=600, height=250)
        resp = objNotaryClass.main_process(logger, json_str)
       
        if os.path.exists(output_filename):
            blob_64encode = get_base64_file(output_filename)
            create_status = True
            return jsonify({
                'status': str(create_status),
                'outpath': blob_64encode
            })
        else:
            return jsonify({
                'status': str(create_status),
                'outpath': blob_64encode
            }), 500
            
    except Exception as e:
        return jsonify({
                'status': str(e),
                'outpath': blob_64encode
            })
 
##################### End ENOTARY SEAL -- HELPER FUNCTIONS  #############################


@app.route('/api/notary/seal-create/circle', methods=['POST'])
def notary_seal_creation():    
    random_part = str(random.randint(100000, 900000))
    create_status = False    
    try:
        data = request.get_json()
        outDir = data.get('outDir')
        output_filename = os.path.join(outDir, f"notarySeal_{random_part}.png")
        upper_circle_text = data.get('upperCircleText')
        lower_circle_text = data.get('lowerCircleText')
        notaryId = data.get('notaryId')
        expireOn = data.get('expireOn')        
        data['outFile'] = output_filename         
        json_str = json.dumps(data)
        clobj = LeafletNotarySeal()
        response = clobj.mainprocess(logger, json_str)
        resp_Str = json.dumps(response)
        logger.debug(f"Circle Seal response=> {resp_Str}")
        if os.path.exists(output_filename):
            create_status = True
            return jsonify({
                'status': str(create_status),
                'outpath': output_filename
            })
        else:
            return jsonify({
                'status': str(create_status),
                'outpath': ' '
            }), 500
            
    except Exception as e:
        logger.debug(f"Circle Seal Exception=> {str(e)}")
        return jsonify({'status': 'error', 'outpath': str(e)}), 500

###### Rectangle Seal Creations 
from notary_seal_rect import LeafletNotaryStampGeneratorCairo
import random
import time
import os 

@app.route('/api/notary/seal-create/rectangle', methods=['POST'])
def notary_seal_rect_creation():
    logger.debug(f"Request notary_seal_rect_creation")
    random_part = str(random.randint(100000, 900000))
    create_status = False
        
    try:
        data = request.get_json()
        outDir = data.get('outDir')
        output_filename = os.path.join(outDir, f"notarySealRect_{random_part}.png")                
        data['outFile'] = output_filename 
        json_str = json.dumps(data)
        logger.debug(f"notary_seal_rect_creation : json_str=> {json_str}")
        logger.debug(f"Rectangle Seal json_str => {json_str}")
        objNotaryClass = LeafletNotaryStampGeneratorCairo(width=600, height=250)
        resp = objNotaryClass.main_process(logger, json_str)
       
        if os.path.exists(output_filename):
            create_status = True
            return jsonify({
                'status': str(create_status),
                'outpath': output_filename
            })
        else:
            return jsonify({
                'status': str(create_status),
                'outpath': ' '
            }), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'outpath': str(e)}), 500
 
################### END: Enotary Seal #######################        
############ Start: Certificate Validity ###########
from revocation_cert import LeafletCertVarification
import json

@app.route('/api/notary/certificate/revocation', methods=['POST'])
def certificate_revocation_check():
    logger.debug("Request: certificate_revocation_check")
    try:
        data = request.get_json()
        cert_path = data['certpath']
        objC = LeafletCertVarification(cert_path)
        json_obj = objC.check_certificate_revocation()
        json_str = json.dumps(json_obj)        
        logger.debug(f"Response: certificate_revocation_check=> Seal json_str => {json_str}")
        return json_obj  #jsonify(json_str)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

### certificate Validations 
from cert_validation import LeafletCertValidation
import json
@app.route('/api/notary/certificate/validation', methods=['POST'])
def certificate_validation_check():
    logger.debug("Request: certificate_validation_check")
    try:
        data = request.get_json()
        certpath = data['certpath']
        password = data['password']
        cvalid = LeafletCertValidation()
        resp_obj = cvalid.check_certificate_validation(certpath, password)        
        json_str = json.dumps(resp_obj)        
        logger.debug(f"Response: certificate_validation_check=> Seal json_str => {json_str}")
        return resp_obj
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
############ End: Certificate Validity ###########
########################## Web Search #####################
from web_search import LeafletWebSearch
@app.route('/api/websearch/download', methods=['POST'])
def websearch_download():
    try:
        logger.debug("\n **************Request websearch_download**************")
        data = request.get_json()
        url = data.get('url')
        module = data.get('module')
        folder = data.get('folder')
        logger.debug(f" {url} - {module} - {folder}")
        clobj = LeafletWebSearch(logger, url, module, folder, data['document'], data['username'], data['password'])
        outfile_path = clobj.main_process()
        logger.debug("websearch_download has been completed")
        logger.debug("*******************************************************")
        return jsonify({'status': 'OK', 'message': "file downloded", 'filepath': outfile_path})
        
    except Exception as e:
        logger.debug(f"exp websearch_download: {str(e)}") 
        logger.debug("*******************************************************")
        return jsonify({'status': 'error', 'message': str(e)}), 500        


from seqlegal import SEQLegalScraper
@app.route('/api/seqlegal/info', methods=['GET'])
def seqlegal_information():
    try:
        logger.debug("\n **************Request seqlegal_information**************")
        seqobj = SEQLegalScraper()
        json_resp = seqobj.get_docs_info()
        logger.debug("websearch_download has been completed")
        logger.debug("*******************************************************")
        return json_resp        
    except Exception as e:
        logger.debug(f"exp seqlegal_information: {str(e)}") 
        logger.debug("*******************************************************")
        return jsonify({'status': 'error', 'message': str(e)}), 500 
        
from edgar_search import LeafletEdgarApp
@app.route('/api/edgar/info', methods=['POST'])
def edgar_information():
    try:
        logger.debug("\n **************Request edgar_information**************")
        data = request.get_json()
        url = data.get('url')
        seqobj = LeafletEdgarApp(logger, data.get('url'), data.get('company'), data.get('cik'), data.get('form_type'))
        json_resp = seqobj.main_process()
        logger.debug("websearch_download has been completed")
        logger.debug("*******************************************************")
        return json_resp        
    except Exception as e:
        logger.debug(f"exp edgar_information: {str(e)}") 
        logger.debug("*******************************************************")
        return jsonify({'status': 'error', 'message': str(e)}), 500 
        
######################################### EDAR Info End ##################################################

####### Gennerate MD5 Hashcode #################
import hashlib
def get_md5_hash(file_path):
    try:
        md5_hash = hashlib.md5()    
        with open(file_path, 'rb') as f:        
            while chunk := f.read(8192):
                md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    except Exception as e:
        return str(e)

@app.route('/api/md5hash', methods=['POST'])
def get_file_md5hash():
    try:
        data = request.get_json()
        file_path = data.get('filepath')
        hash_code = get_md5_hash(file_path)
        logger.debug(f"File: {file_path} => MD5 Hash Code: {hash_code}")
        return jsonify({"hashvalue": hash_code})
    except Exception as e:
        logger.error('Exception get_md5_hash:', exc_info=e)
        return jsonify({"error": str(e)})
        

################ Extraction via LLM ############### 
from  llm_process import LeafletLLM_Ver10
from canmon_temp_prompt import LeafletCanmonTemplatePrompt
@app.route('/api/llm/extract', methods=['POST'])
def entity_extraction_llm():
    template_json = None
    entity_json_str = None    
    data = {}
    #document_type = ' Master Service Agreement ' 
    try:
        data = request.get_json()
        entity_json = data.get("entities")
        document_type = data.get("document_type")        
        objconmonTemp = LeafletCanmonTemplatePrompt(document_type = document_type, prompt_template_path ='canmon_prompt_template.md', document_content=' ', request_json=entity_json)
        template_json, entity_json_str = objconmonTemp.get_formatted_prompt_template()
    except Exception as e: 
        logger.error('Exception get_formatted_prompt_template:', exc_info=e)
        return jsonify({"error get_formatted_prompt_template": str(e)})

    try:
        caller = "api/llm/extract"        
        file_path = data.get('filepath')              
        objcls = LeafletLLM_Ver10(logger, file_path, template_json, entity_json_str, caller)
        logger.debug("===>LeafletLLM_Ver10")
        extracted_data = objcls.request_entity()
        resp_data = convert_json_keyvalue(extracted_data)
        #json_string = json.dumps(resp_data, indent=2, ensure_ascii=False)
        return resp_data
    except Exception as e:
        logger.error('Exception entity_extraction_llm:', exc_info=e)
        return jsonify({"error": str(e)})

def convert_json_keyvalue(extracted_data):
    data = json.loads(extracted_data)
    return {item['conceptName']: item['conceptValue'] for item in data}
    
    
def transform_list_to_dict(extracted_data):
    json_string = json.dumps(extracted_data)
    logger.debug(f"Length of Text: {len(json_string)}")
    try:
        data_list = json.loads(json_string)
        logger.debug(f"Length of data_list: {len(data_list)}")
        transformed_dict = {
            item["conceptName"]: item["conceptValue"]
            for item in data_list
            if "conceptName" in item and "conceptValue" in item
        }
        logger.debug(f"Length of transformed_dict: {len(transformed_dict)}")
        return transformed_dict
    except Exception as e:
        logger.error('Exception transform_list_to_dict:', exc_info=e)
    return {'error': str(e)}


###### Classify Document based on content: not custom Label #####
#### Temporary comment....
# from zero_shot_classify import LeafletZeroShotClassifyNoLabel

# @app.route('/api/classify/document', methods=['POST'])
# def zero_shot_classify():
#     try:
#         data = request.get_json()
#         file_path = data.get('filepath')
#         clf_object = LeafletZeroShotClassifyNoLabel(top_k_keywords=3)
#         response = clf_object.process_classify(file_path)
#         logger.debug(f"File: {file_path} => Classify completed")
#         return response
#     except Exception as e:
#         logger.error('Exception Zero shot Classify:', exc_info=e)
#         return jsonify({"error": str(e)})
        
 ################### PDF file Signed ######################
from pdf_file_sign import LeafletPDFDigitalSigner
@app.route('/api/pdf/appysign', methods=['POST'])
def pdf_file_applysign():
    try:
        data = request.get_json()
        pfx_path = data.get('pfx_path')        
        pfx_password = data.get('pfx_password')
        field_name = data.get('field_name')
        signer_name = data.get('signer_name')
        reason = data.get('reason')
        location = data.get('location')
        contact_info = data.get('contact_info')
        input_pdf_file = data.get('input_pdf_file')
        output_signed_pdf_file = data.get('output_signed_pdf_file')
        object_pdf_signer = LeafletPDFDigitalSigner(
            pfx_path=pfx_path,
            pfx_password=pfx_password.encode('utf-8'),            
            field_name=field_name,
            signer_name=signer_name,
            reason=reason,
            location=location,
            contact_info=contact_info
        )
        resp_status = object_pdf_signer.sign_process(input_pdf_file)
        logger.debug(f"status: PDF file sign completed")
        return resp_status ###jsonify({"out_file": resp_status})
    except Exception as e:
        logger.error('Exception PDF file sign:', exc_info=e)
        return jsonify({"error": str(e)})
          
################### PDF file Signed ######################
from pdf_file_metadata import LeafletPDFSignAnalyzer
@app.route('/api/pdf/sign-metadata', methods=['POST'])
def pdf_file_sign_metadata():
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        obj_pdf = LeafletPDFSignAnalyzer(log_prefix="sign_metadata")
        signatures_json = obj_pdf.check_digital_signatures(file_path)
        logger.debug(f"status: {signatures_json} => pdf_file_sign_metadata completed")
        return signatures_json
    except Exception as e:
        logger.error('Exception pdf_file_sign_metadata:', exc_info=e)
        return jsonify({"error": str(e)})
        
################### Sales Force ######################
PYTHON_ENV_EXE = r"F:\IISsites\notary_vir_env\Scripts\python.exe"  # Path to virtual env's python.exe
SCRIPT_PATH = r"F:\IISsites\PythonSP\notary_source\salforce.py"
out_json_path = r"F:\IISsites\PythonSP\notary_source\TextData\link_map.json"
PARAMS = []
from salforce import LeafletSalesForceVer100
@app.route('/api/crawl/salesforce', methods=['GET'])
def salesforce_crawler():
    try:
        process = subprocess.Popen(
            [PYTHON_ENV_EXE, SCRIPT_PATH] + (PARAMS or []),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if os.path.exists(out_json_path):
           os.remove(out_json_path)
           
        start_time = time.time()
        timeout = 1000
        while not os.path.exists(out_json_path):
            if time.time() - start_time > timeout:
                logger.error(f"Timeout: Output file not found within {timeout} minutes.")
                return jsonify({"error": "Timeout waiting for output file"}), 504
            time.sleep(10)
            logger.debug(f"time span : {time.time() - start_time}")
         
        time.sleep(2)

        logger.debug("Output file found, reading result...")
        response = read_result_json_file(out_json_path)
        logger.debug("Crawler finished.")
        return response #jsonify({"status": response})
    
    except Exception as e:
        logger.error(f"Crawler failed: {e}", exc_info=True)
        return jsonify({"error": str(e)})


    

@app.route('/api/crawl/salesforceold', methods=['GET'])
def salesforce_crawler_old():
    try:
        #data = request.get_json()
        #file_path = data.get('file_path')
        result = subprocess.run(
            [PYTHON_ENV_EXE, SCRIPT_PATH] + (PARAMS or []),
            capture_output=True,  # Captures stdout & stderr
            text=True             # Decodes output to str
           )
        response = read_result_json_file(out_json_path)
        logger.debug("salesforce_crawler started")
        #lf_salf = LeafletSalesForceVer100()
        #response = lf_salf.scrape_salesforce_1_level()
        logger.debug(f"status: {response}.")
        #st = "completed: check Summary file"
        return response #jsonify({"status": response}) 
    except Exception as e:
        logger.error('Exception salesforce_crawler:', exc_info=e)
        return jsonify({"error": str(e)})      


###### QR Code Generate #################

@app.route('/api/notary/qrcode', methods=['POST'])
def create_url_qr():
    DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'QR_FILES')
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    random_name = ''.join(random.choices(string.ascii_lowercase, k=5))
    random_filename = f"{random_name}_QrCode.png"
    try:
        data = request.get_json()
        url_name = data.get('url')
        logger.debug(f"QR code for url_name: {url_name}")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(url_name)
        qr.make(fit=True)    
        img = qr.make_image(fill_color="black", back_color="white")
        save_path = os.path.join(DOWNLOAD_FOLDER, random_filename)
        img.save(save_path)
        logger.debug(f"QR code save path: {save_path}")
        download_path = f"https://uat.leafletcorp.com:8961/api/notary/{random_filename}"
        blob_64encode = get_base64_file(save_path)
        response_data = {
            "download_qrcode": download_path,
            "blob": blob_64encode
        }
        return jsonify(response_data)
    except Exception as e:
        logger.error('Exception create_url_qr:', exc_info=e)
        return jsonify({"error": str(e)})


@app.route("/api/notary/identity/qrcode", methods=['GET'])
def display_generate_qrcode():
    # Get the 'url' parameter from query string
    data = request.args.get("url")
    if not data:
        return {"error": "Please provide ?url= parameter"}, 400

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # Return QR code image as response
    return Response(buf, mimetype="image/png")

@app.route('/api/notary/<filename>', methods=['GET'])
def download_file(filename):
    DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'QR_FILES')
    
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    safe_path = os.path.abspath(file_path)
    if not safe_path.startswith(os.path.abspath(DOWNLOAD_FOLDER)):        
        abort(404)
		
    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        try:
            # Serve the file for download.
            return send_file(safe_path, as_attachment=True, download_name=filename)
        except Exception as e:
            # Handle any potential errors during file sending
            return str(e), 500
    else:
        # If the file doesn't exist, return a 404 Not Found error
        abort(404)

############# DRIVING LICENSE INFORMATION EXTRACTION #################
from drive_license import LeafletDriverLicenseExtractor
@app.route('/api/driveid/info', methods=['POST'])
def drive_license_extraction():
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        logger.info(f"drive_license_extraction image_path: {image_path}")
        info = call_usa_drive_license_model(image_path) ###LeafletDriverLicenseExtractor(image_path)
        ###info = extractor.info
        logger.debug(f"status: {info} => drive_license_extraction completed")
        return info
    except Exception as e:
        logger.error('Exception drive_license_extraction:', exc_info=e)
        return jsonify({"error": str(e)})

def read_result_json_file(json_path):
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:               
            return "Json file code error"
        except Exception as e:                
            return "File path issue"
    else:            
        return "File does not exist" 


@app.route('/api/extraction/id-info', methods=['POST'])
def id_extraction_process():
    logger.info("--- Start : id_extraction_process --- ")
    try:
        data = request.get_json()
        id_type = request.json.get('id_type')
        base64_string = request.json.get('documentBase64Content')
        pre_fix = "na"
        file_path = ""
        if(id_type.strip() == "drivers_license"):
            file_path = create_image_path_from_base4Str(DRIVE_FOLDER, base64_string, id_type)         
            logger.info("drive license file path after write:", file_path)
            info = call_usa_drive_license_model(file_path)
            logger.debug(f"status: {info} => id_extraction_process completed")
            return info
        elif(id_type.strip() == 'passport'):
            logger.info("usa_passport_info_extraction request")
            img_name = create_image_path_from_base4Str(DRIVE_FOLDER, base64_string, id_type)
            country_codes_file = 'country_codes.json'
            #img_name = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\testfiles\us_passports_img\enhance_uspass200.png"
            extractor = LleafletUSAPassportDataExtractor()
            data = extractor.extract_us_passport_data(img_name)
            return jsonify(data)
        else:      
            return jsonify({"error": 'Not implemented yet.'})
        
    except Exception as e:
        logger.error('Exception usa_drive_license_extraction:', exc_info=e)
        return jsonify({"error": str(e)})

@app.route('/api/driveid/usa-info', methods=['POST'])
def usa_drive_license_extraction():
    logger.info("--- Start : usa_drive_license_extraction --- ")
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        info = call_usa_drive_license_model(image_path)
        logger.debug(f"status: {info} => usa_drive_license_extraction completed")
        return info
    except Exception as e:
        logger.error('Exception usa_drive_license_extraction:', exc_info=e)
        return jsonify({"error": str(e)})

@app.route('/api/driveid/blob/usa-info', methods=['POST'])
def usa_drive_license_extraction_fromBlob():
    logger.info("--- Start : usa_drive_license_extraction_fromBlob --- ")
    try:
        data = request.get_json()
        ###image_path = data.get('image_path')
        base64_string = request.json.get('image_blob')
        # Generate unique image_path
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        image_path = f"id_card_{timestamp}_{unique_id}"
        update_path = None
        clean_base64 = base64_string
        if base64_string.startswith('data:'):
            clean_base64 = base64_string.split(',')[1]
        image_format = detect_image_format(base64_string)
        image_data = base64.b64decode(clean_base64)
        file_path = os.path.join(DRIVE_FOLDER, image_path) + "." + image_format
        logger.info("drive license file path:", file_path)
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(image_data)
        logger.info("drive license file path after write:", file_path)
        info = call_usa_drive_license_model(file_path)
        logger.debug(f"status: {info} => usa_drive_license_extraction_fromBlob completed")
        return info
    except Exception as e:
        logger.error('Exception usa_drive_license_extraction_fromBlob:', exc_info=e)
        return jsonify({"error": str(e)})

def create_image_path_from_base4Str(dir_name, base64_string, pre_fix):
    #base64_string = request.json.get('image_blob')
    # Generate unique image_path
    try:
        logger.debug("Start create image path from_base4Str")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        image_path = f"{pre_fix}_{timestamp}_{unique_id}"
        clean_base64 = base64_string
        if base64_string.startswith('data:'):
           clean_base64 = base64_string.split(',')[1]
        image_format = detect_image_format(base64_string)
        image_data = base64.b64decode(clean_base64)
        file_path = os.path.join(dir_name, image_path) + "." + image_format
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(image_data)
        logger.debug('Return create image path from_base4Str.')
        return file_path
    except Exception as e:
        logger.error("Exception create image path from_base4Str", exc_info=e)
        return ""
 
    
    
    
######################## BEGIN:: USA DRIVING LICENSE #############################
import os
import sys
import uuid
import json
import subprocess 

def run_python_venv(venv_path, script_path, *args):
    # Determine the Python executable path based on OS
    python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
    result = subprocess.run(
        [python_exe, script_path] + list(args),
        capture_output=True,
        text=True
    )
    return result.returncode


def read_config_file(config_file_name):
    ###dir_name = os.path.dirname(os.path.abspath(__file__))
    dir_name = os.path.dirname(__file__)

    config_file_path = os.path.join(dir_name, config_file_name)
    full_path = os.path.abspath(config_file_path)
    logger.info(f"read_config_file-full_path : {full_path}")
    config = None
    with open(full_path, 'r') as f:
            config = json.load(f)
    
    return config

def call_usa_drive_license_model(id_file_path):
    logger.info("---- Start : call_usa_drive_license_model...")
    file_path = enhance_by_magick_tool(id_file_path)
    logger.info(f"Return from magick tool: ", file_path)
    if not file_path.strip():
       file_path = id_file_path
        
    conf_path = "usa_drive_license_paths_config.json"
    config = read_config_file(conf_path)
    dir_name = os.path.dirname(file_path)
    random_id = str(uuid.uuid4())[:6]
    random_name = f"ext_{random_id}.json"
    result_file = os.path.join(dir_name, random_name)
    logger.info(f"result_file: {result_file}")
    script_path = config['script_path']
    logger.info(f"script_path: {script_path}")
    env_path = config['env_path']
    logger.info(f"env_path: {env_path}")
    ext_code = run_python_venv(env_path, script_path, file_path, result_file)
    logger.info(f"ext_code : {ext_code}")
    if not os.path.exists(result_file):
        return {
                "status": "fail",
                "message": "Unable extract information."                
            }
    
    if os.path.getsize(result_file) == 0:
        return {
                "status": "fail",
                "message": "Unable extract information."                
            }
    
    with open(result_file, 'r', encoding='latin-1') as f:
        data = json.load(f)
    return data


def enhance_by_magick_tool(original_path):
    try:
        directory, filename = os.path.split(original_path)
        stem, suffix = os.path.splitext(filename)
        new_filename = f"{stem}_mgc{suffix}"
        new_path = os.path.join(directory, new_filename)
        magick_exe_path = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
        magick_command = f"{magick_exe_path} {original_path} -colorspace Gray -contrast-stretch 1%x1% -sharpen 0x2 {new_path}"
        #output_filepath = r'C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\pythonTesting\doc_scantest\111\enhanced123.png'
        #output_filepath = r'C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\pythonTesting\doc_scantest\111\enhanced123.png'
        try:
            subprocess.run(magick_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"Magrick Command outcome: ", new_path)
            return new_path
        except subprocess.CalledProcessError:
            return original_path
        except FileNotFoundError:
            return original_path
    except:
        return original_path
        
 
######################## ENDS:: USA DRIVING LICENSE ############################# 
@app.route('/face/livedetect', methods=['GET'])
def liveness_face_process():
    logger.info("Render-1 face/livedetect")
    return render_template('liveface.html') 

@app.route('/face/livescore', methods=['POST'])
def get_set_liveness_score():
    data = request.get_json()
    score = data.get('score')
    status = data.get('status')
    return {'message': f'liveness_score: {score}, Status: {status}'}, 200

##### Capture Client ID-proof #########
@app.route('/id/capture')
def id_captre_show():
    logger.info("rendering Id/capture")
    return render_template('Idcapture.html')


@app.route('/capture_id', methods=['POST'])
def capture_id():
    try:
        logger.info("Get the image data from the request")
        image_data = request.json.get('image_data')
        
        if not image_data:
            logger.info("No image data received for image...")
            return jsonify({'success': False, 'error': 'No image data received'})
        
        # Remove the data URL prefix (data:image/jpeg;base64,)
        image_data = image_data.split(',')[1]        
        image_binary = base64.b64decode(image_data)
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"id_card_{timestamp}_{unique_id}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        logger.info(f"Upload file path: {filepath}")
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(image_binary)
                
        return jsonify({
            'success': True, 
            'message': 'ID card captured successfully!',
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Upload error : {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

from image_quality_enhance import LeafletImageEnhancementV1 
@app.route('/validate/passport/quality-enhance', methods=['POST'])
def passport_image_quality_enhance():
    try:
        logger.info("passport_image_quality_enhance request")
        file_path = request.json.get('image_path')
        update_path = None # r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\id_identification\img_files\enhance_dl3.png"
        enhancements_to_apply= None  #["contrast", "blur_reduction"]
        objEnh = LeafletImageEnhancementV1()        
        result = objEnh.enhance_image_pipeline(file_path, update_path, enhancements_to_apply=enhancements_to_apply)
        return result        
    except Exception as e:
        logger.error(f"passport_image_quality_enhance error : {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


from idcard_upload_validation import LeafletImageUploadTest 
@app.route('/validate/passport/quality-check', methods=['POST'])
def passport_image_quality_check():
    try:
        logger.info("passport_image_quality_check request")
        file_path = request.json.get('image_path')
        imgObj = LeafletImageUploadTest()
        result = imgObj.validate_id_upload(file_path)
        return result        
    except Exception as e:
        logger.error(f"passport_image_quality_check: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

######## Leaflet document scanning #########
from cv2_document_scanner import LeafletDocumentScanner
@app.route('/api/idcard/preprocess', methods=['POST'])
def detect_idcard_scanning():
    try:
        logger.info("detect_idcard_scanning")
        base64_string = request.json.get('image_blob')
        # Generate unique filename
        
        unique_id = str(uuid.uuid4())[:8]
        filename = f"card_{unique_id}"
        outfile = f"cropped_{unique_id}"
        update_path = None
        clean_base64 = base64_string
        if base64_string.startswith('data:'):
            clean_base64 = base64_string.split(',')[1]
        image_format = detect_image_format(base64_string)
        image_data = base64.b64decode(clean_base64)
        file_path = os.path.join(UPLOAD_FOLDER, filename) + "." + image_format
        out_file = os.path.join(UPLOAD_FOLDER, outfile) + "." + image_format
        
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"detect_idcard_scanning::Upload file path: {file_path}")
        logger.info(f"detect_idcard_scanning::result file path: {out_file}")
        
        objEnh = LeafletDocumentScanner(file_path, out_file)  ### objEnh = LeafletImageEnhancementV1()      
        result = objEnh.processing()
        if(result['status']==True):
            blob_64encode = get_base64_file(result['image_path'])
            resp = {
             'image_blob': blob_64encode,
             'status': True
            }
        else:
            resp = {
             'image_blob': None,
             'status': False
            }
            
        return resp       
    except Exception as e:
        logger.error(f"detect_idcard_scanning: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})



from image_quality_enhance import LeafletImageEnhancementV1  
@app.route('/api/idcard/preprocessV10', methods=['POST'])
def passport_image_preprocess():
    try:
        logger.info("passport_image_preprocess request")
        base64_string = request.json.get('image_blob')
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"id_card_{timestamp}_{unique_id}"
        update_path = None
        clean_base64 = base64_string
        if base64_string.startswith('data:'):
            clean_base64 = base64_string.split(',')[1]
        image_format = detect_image_format(base64_string)
        image_data = base64.b64decode(clean_base64)
        file_path = os.path.join(UPLOAD_FOLDER, filename) + "." + image_format
        
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Upload file path: {file_path}")
        enhancements_to_apply= None  ###["contrast", "blur_reduction"]
        objEnh = LeafletImageEnhancementV1()  ### objEnh = LeafletImageEnhancementV1()      
        result = objEnh.enhance_image_pipeline(file_path, update_path, enhancements_to_apply=enhancements_to_apply)
        blob_64encode = get_base64_file(result['enhanced_path'])
        resp = {
         'image_blob': blob_64encode,
         'status': True
        }
        return resp       
    except Exception as e:
        logger.error(f"passport_image_preprocess: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


def detect_image_format(base64_string):
    try:
        
        if base64_string.startswith('data:'):
            if 'image/' in base64_string:
                format_part = base64_string.split('image/')[1].split(';')[0]
                if format_part in ['jpeg', 'jpg']:
                    return 'jpg'
                elif format_part in ['png', 'gif', 'webp', 'bmp', 'tiff']:
                    return format_part
            base64_string = base64_string.split(',')[1]
        
        # Decode first few bytes to check magic numbers
        header_bytes = base64.b64decode(base64_string[:50])  # First ~37 bytes should be enough
        
        # Check magic numbers for different image formats
        if header_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        elif header_bytes.startswith(b'\xff\xd8\xff'):
            return 'jpg'
        elif header_bytes.startswith(b'GIF87a') or header_bytes.startswith(b'GIF89a'):
            return 'gif'
        elif header_bytes.startswith(b'RIFF') and b'WEBP' in header_bytes[:12]:
            return 'webp'
        elif header_bytes.startswith(b'BM'):
            return 'bmp'
        elif header_bytes.startswith(b'II*\x00') or header_bytes.startswith(b'MM\x00*'):
            return 'tiff'
        elif header_bytes.startswith(b'\x00\x00\x01\x00') or header_bytes.startswith(b'\x00\x00\x02\x00'):
            return 'ico'
        else:
            # Default to png if format cannot be determined
            print("Warning: Could not detect image format, defaulting to PNG")
            return 'png'
            
    except Exception as e:
        print(f"Error detecting format: {e}")
        return 'png'

from usa_passport_extraction import LleafletUSAPassportDataExtractor 
@app.route('/passport/usa/info', methods=['POST'])
def usa_passport_info_extraction():
    try:
        logger.info("usa_passport_info_extraction request")
        img_name = request.json.get('image_path')
        country_codes_file = 'country_codes.json'
        #img_name = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\testfiles\us_passports_img\enhance_uspass200.png"
        extractor = LleafletUSAPassportDataExtractor()
        data = extractor.extract_us_passport_data(img_name)
        return jsonify(data)
    except Exception as e:
        logger.error(f"usa_passport_info_extraction: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


from usa_passport_extraction import LleafletUSAPassportDataExtractor 
@app.route('/passport/usa/info-extract', methods=['POST'])
def usa_passport_info_extraction_fromBase64():
    try:
        logger.info("usa_passport_info_extraction_fromBase64 request")
        base64_string = request.json.get('image_blob')
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"passport_{timestamp}_{unique_id}"
        update_path = None
        clean_base64 = base64_string
        if base64_string.startswith('data:'):
            clean_base64 = base64_string.split(',')[1]
        image_format = detect_image_format(base64_string)
        image_data = base64.b64decode(clean_base64)
        file_path = os.path.join(UPLOAD_FOLDER, filename) + "." + image_format
        
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"passport ile path: {file_path}")
        country_codes_file = 'country_codes.json'
        #img_name = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\testfiles\us_passports_img\enhance_uspass200.png"
        extractor = LleafletUSAPassportDataExtractor()
        data = extractor.extract_us_passport_data(file_path)
        return jsonify(data)
    except Exception as e:
        logger.error(f"usa_passport_info_extraction: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


from ssn_info_experian import LeafletExperianVerify 
@app.route('/ssn/info', methods=['POST'])
def ssn_info_verify_experian():
    try:
        logger.info("ssn_info_verify_experian request")
        data = request.json
        objssn = LeafletExperianVerify()
        result = objssn.info_by_ssn(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"ssn_info_verify_experian: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

#kba_api_testing

from ssn_info_experian import LeafletExperianVerify 
@app.route('/ssn/exp-kba', methods=['POST'])
def kba_question_experian():
    try:
        logger.info("kba_question_experian request")
        data = request.json
        objssn = LeafletExperianVerify()
        result = objssn.kba_api_testing(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"kba_question_experian: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


from ssn_info_experian import LeafletExperianVerify 
@app.route('/ssn/kba-verify', methods=['POST'])
def ssn_kba_verification():
    try:
        logger.info("ssn_kba_verification request")
        kba_question_answer = request.json
        objssn = LeafletExperianVerify()
        repo = objssn.load_repo()
        ans = objssn.verify_ssn_kba(kba_question_answer, repo)
        return jsonify(ans)
    except Exception as e:
        logger.error(f"ssn_kba_verification: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

###### FOLDER RECOMMENDATION ######
from folder_recommend import LeafletFolderRecommendaion
@app.route('/api/folder-recom', methods=['POST'])
def folder_recommendation_process():
    try:
        logger.info("start folder_recommendation_process request")
        data = request.get_json()
        emails=data["emails"]
        folders=data["folders"]
        objFr = LeafletFolderRecommendaion(logger)
        ans =  objFr.process_it(emails, folders)
        logger.info("completed success, folder_recommendation_process request")
        ###logger.info(f"ans=> {ans}")
        return jsonify(ans)
    except Exception as e:
        logger.error(f"folder_recommendation_process: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

"""
############################################## KBA Process ##########################################
from kba_pro import LeafletKBAProcess 
@app.route('/kba/store-info', methods=['POST'])
def kba_info_stored():
    try:
        logger.info("kba_info_stored request")
        data = request.json
        kba = LeafletKBAProcess()
        result=kba.store_kba(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"kba_info_stored: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

from kba_pro import LeafletKBAProcess 
@app.route('/kba/fetch-info', methods=['POST'])
def kba_info_fetch():
    try:
        logger.info("kba_info_fetch request")
        data = request.json
        userid = data.get('userid')
        kba = LeafletKBAProcess()
        result=kba.verify_kba(userid, data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"kba_info_fetch: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


 
"""
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'ID Card Capture Service is running'})

def get_base64_file(file_path):
    encoded = None
    with open(file_path, "rb") as f:
      encoded = base64.b64encode(f.read()).decode()
    return encoded


####### *******************************************************

# OpenVidu Server Configuration
OPENVIDU_URL = "https://dev.leafletcorp.com" 
OPENVIDU_SECRET = "vdconf_leaflet_2025"

# Create session with basic auth
def get_auth():
    return ('OPENVIDUAPP', OPENVIDU_SECRET)

@app.route('/api/testing/sharetesting')
def testingsharing():
    return render_template('record.html')

@app.route('/api/testing/get-token', methods=['POST'])
def get_openvidu_token():
    """Create session and return token"""
    try:
        data = request.json
        session_id = data.get('sessionId', 'TestSession')
        
        # Step 1: Create or get session
        session_response = requests.post(
            f"{OPENVIDU_URL}/openvidu/api/sessions",
            json={"customSessionId": session_id},
            auth=get_auth(),
            verify=False  # Only for testing with self-signed certificates
        )
        
        if session_response.status_code == 409:
            # Session already exists
            print(f"Session {session_id} already exists")
        elif session_response.status_code == 200:
            print(f"Session {session_id} created")
        else:
            return jsonify({"error": "Failed to create session"}), 500
        
        # Step 2: Create token (connection)
        token_response = requests.post(
            f"{OPENVIDU_URL}/openvidu/api/sessions/{session_id}/connection",
            json={},
            auth=get_auth(),
            verify=False
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            return jsonify({
                "token": token_data['token'],
                "sessionId": session_id
            })
        else:
            return jsonify({"error": "Failed to create token"}), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/testing/start-recording', methods=['POST'])
def start_openvidu_recording():
    """Start recording the session"""
    try:
        data = request.json
        session_id = data.get('sessionId')
        
        recording_response = requests.post(
            f"{OPENVIDU_URL}/openvidu/api/recordings/start",
            json={
                "session": session_id,
                "outputMode": "COMPOSED",
                "recordingLayout": "BEST_FIT",
                "resolution": "1920x1080",
                "hasAudio": True,
                "hasVideo": True
            },
            auth=get_auth(),
            verify=False
        )
        
        if recording_response.status_code == 200:
            return jsonify(recording_response.json())
        else:
            return jsonify({"error": "Failed to start recording"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/testing/stop-recording', methods=['POST'])
def stop_openvidu_recording():
    """Stop recording"""
    try:
        data = request.json
        recording_id = data.get('recordingId')
        
        stop_response = requests.post(
            f"{OPENVIDU_URL}/openvidu/api/recordings/stop/{recording_id}",
            auth=get_auth(),
            verify=False
        )
        
        if stop_response.status_code == 200:
            return jsonify(stop_response.json())
        else:
            return jsonify({"error": "Failed to stop recording"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500




##### *****************************************************
if __name__ == "__main__":
    logger.error("REQUEST: LOCAL Via shell command-1")
    app.run(debug=True, host='0.0.0.0', port=5000)
    print("Server is ready...")
else:
    logger.error("REQUEST: API Via IIS")


