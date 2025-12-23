#######################
## Leaflet technology
## initiate by: raesh bisht
## Date: 10-AUG-2025
########################
#from huggingface_hub import hf_hub_download
from ultralytics import YOLO
from supervision import Detections
from deepface import DeepFace
import logging
from PIL import Image
import os
import sys
import json
import random

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class LeafletFaceDetectImage:    
    def __init__(self, model_path: str, logger):
        self.model_path = model_path
        self.logger = logger
    
    def logs(self, msg):
        logger = self.logger
        if(logger):
          logger.debug(msg)
          
          
    def get_face_image_path(self, image_path, save_path):
            
        ### ==> model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")         
        #r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\pythonTesting\yolomodel/arnabdharYOLOv8-Face-Detection.pt"
        face_imagepath = save_path
        if(self.model_path is None or self.model_path == ""):
           self.model_path = r"yolo_models/arnabdharYOLOv8-Face-Detection.pt"
        #print(f"model pat before loading: {self.model_path}")
        model = YOLO(self.model_path)
        model.save()
        image = Image.open(image_path) 
        name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        #saved_image_name = name_without_ext + "_faceDetect.png"
        output = model(image)
        results = Detections.from_ultralytics(output[0])
        dir_names = None
        if os.path.isdir(face_imagepath):
            dir_names = face_imagepath
        else:
            dir_names = os.path.dirname(face_imagepath)
            
        os.makedirs(dir_names, exist_ok=True)
        ###save_path = "detected_faces"
        #face_imagepath = os.path.join(save_path, f"{saved_image_name}")
        #
        for i, (x1, y1, x2, y2) in enumerate(results.xyxy):        
            face = image.crop((x1, y1, x2, y2))        
            face.save(face_imagepath)

        return face_imagepath
    

    def face_identity(self, img1_path, img2_path): 
        self.logs("inside face_identity class")    
        status = False
        summary_result = {
                "status": status,
                "message": ""
            }
        try:
            result = DeepFace.verify(img1_path, img2_path, model_name="ArcFace")
            self.logs("After verified.") 
            ##print(f"result: {result}")
            status = result["verified"]
            if(result["distance"] < 65/100):  ###65/100 As threshold...
               status = True
             
            confidence = max(0, min(1, 1 - result["distance"]))
            summary_result = {
                "score": result["distance"],
                "confidence": round(confidence, 3),
                "confidence_percent": f"{confidence * 100:.2f}%",
                "verified": result["verified"],
                "threshold": result["threshold"],
                "status": status,
            }
                 
        except Exception as e:
            summary_result = {
                "status": status,
                "message": str(e)
            }
        finally: 
            self.logs("finally face identity.")        
            summary_json = json.dumps(summary_result, indent=4)
            return summary_json           
          
    def face_detect_and_identity(self, img1_path, img2_path):
        self.logs("[START]: Face detect and identity.")
        random_part = str(random.randint(10, 999999))
        
        dir_name = os.path.dirname(img1_path)
        saved_path = os.path.join(dir_name, random_part, "face_detect.png")
        try:
            face_image1 = self.get_face_image_path(img1_path, saved_path)
            self.logs(f"[IMAGE-1]: {face_image1}")
            ##print(f"[IMAGE-1]: {face_image1}")
            random_part = str(random.randint(10, 999999))
            
            dir_name = os.path.dirname(img2_path)
            saved_path = os.path.join(dir_name, random_part, "face_detect.png")
            face_image2 = self.get_face_image_path(img2_path, saved_path)
            self.logs(f"[IMAGE-2]: {face_image2}")
            ##print(f"[IMAGE-2]: {face_image2}")
            result = self.face_identity(face_image1, face_image2)
            self.logs("[END]: Face detect and identity.")
            return result
        except Exception as e:
            self.logs(f"[EXP]: Face detect and identity. {e}")
            return {
                "status": False,
                "message": str(e)
            }


    def write_text_file(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as file:
             file.write(str(content))    


def debugWrite(file_path, content):
        with open(file_path, 'w', encoding='utf-8') as file:
             file.write(str(content))
             
if __name__ == "__main__":        
    arguments = sys.argv
    model_path = r"yolo_models/arnabdharYOLOv8-Face-Detection.pt"
    image1_path = r"F:\IISsites\PythonSP\FACE_IDENTITY\base.png"
    image2_path = r"F:\IISsites\PythonSP\FACE_IDENTITY\face.png"
    result_path = "F:\IISsites\PythonSP\FACE_IDENTITY"
    print(f"model_path: {model_path}")
    if os.path.exists(model_path):
       print("model path exist")
    else:
       print("model path doesnot exist")
       
    ov = LeafletFaceDetectImage(model_path=model_path, logger=None)
    #st = ov.face_identity(image1_path, image2_path)
    st = ov.face_detect_and_identity(image1_path, image2_path)
    print(f"Final result: {st}")
