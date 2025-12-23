###########################################################
# Leaflet Corporation - Version:1.1.0
# Recommendations - Pre-trained media - Hugging Face.

###########################################################
 
import json
import numpy as np
import os
import logging
import warnings
from sentence_transformers import SentenceTransformer, util
from flask import Flask, jsonify, request
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0=all, 1=filter INFO, 2=filter WARNING, 3=filter ERROR

warnings.filterwarnings('ignore')
#app = Flask(__name__)

#@app.route('/', methods=['GET'])
def test():
    return jsonify({'message': 'Folder Recommendation from HTTP API'}), 200

class LeafletFolderRecommendaion:
    def __init__(self, logger):
        self.logger = logger
    
    def request_folder_recommendation(self):
        logger = self.logger
        logger.info("start : request_folder_recommendation")
        data = None
        
        if request.is_json:
           data = request.get_json()
        else:
            return jsonify({"error": "Request must be JSON"}), 400

        try:          
            emails=data["emails"]
            folders=data["folders"]
            resp =  process_it(emails, folders)
            return resp
            
        except Exception as ex:
            return jsonify({'status': False,
            'folder': f"{str(ex)}"
        }), 500

    
    def get_metadata(self, fine_name):
        data = None
        try:
            with open(fine_name, "r") as f:
                data = json.load(f)
        except Exception as ex:
            return jsonify({"error": f""}), 400
        
        return data
		

    def process_it(self, email_embedding, folders_metadata):
        logger = self.logger
        logger.info("start : process_it...process")
        try:
            threshold = 0.1
            model_name="all-mpnet-base-v2"
            #folder_texts=["very Good"]
            email_text="this tool is awesome"
            model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2') 	
            #folders_metadata = get_metadata("folder_meta_data.json")    
            folder_texts = [f"{folder['folderName']} {folder['matterName']}" for folder in folders_metadata]
            # Batch compute folder embeddings
            #print(f"folder Text: {folder_texts}")
            folder_embeddings = model.encode(folder_texts, convert_to_tensor=True)    
            email_text = f"{email_embedding['Subject']} {email_embedding['Content']}"
            email_embedding = model.encode(email_text, convert_to_tensor=True)    
            # Compute similarities
            similarities = util.cos_sim(email_embedding, folder_embeddings)[0] 
            #print(f"similarities: {similarities}")  
            # Get all matches with their indices and scores
            all_matches = [(idx, float(score)) for idx, score in enumerate(similarities)] 
            #print(f"all_matches: {all_matches}")
            filtered_matches = [(idx, score) for idx, score in all_matches if score >= threshold]     
            # Sort matches by descending similarity
            filtered_matches = sorted(filtered_matches, key=lambda x: x[1], reverse=True) 
            #print(f"filtered_matches: {filtered_matches}")

            # Pick top 5 matches
            top_matches = filtered_matches[:5]  
            rec_folder = []
            for idx, score in top_matches:
                rec_folder.append(folders_metadata[idx]) 

            distinct_list = [dict(t) for t in {tuple(d.items()) for d in rec_folder}]  
            #resp_data=[]
            
            rest_data={
                "status":True,
                "folders": distinct_list
            } 
            logger.info("completed : process_it...process")            
            return rest_data
        except Exception as e:
            return jsonify({
                'status': str(e)
            })


if __name__ == "__main__":
    print("Running... Port 5210")
    #app.run(debug=True, host='0.0.0.0', port=5210)
    #process_it()



