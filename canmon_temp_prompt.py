import json
import os

class LeafletCanmonTemplatePrompt:
    def __init__(self, document_type, prompt_template_path, document_content, request_json):
        self.template_path = prompt_template_path
        self.document_content = document_content
        self.document_type = document_type
        self.extract_fields_tag, self.response_field_tag = self._get_required_fields(request_json)
        
    def _create_filepath(self, file_name):
        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)
        full_path = os.path.join(current_directory, file_name)
        return full_path

    def _get_template_text(self):
        #prompt_template_path = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\scraping_test\canmon_prompt_template.md"
        prompt_template_path = self._create_filepath(self.template_path)
        content = ""
        try:
            with open(prompt_template_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            pass #print(f"Error: The file '{prompt_template_path}' was not found.")
        except Exception as e:
            pass #print(f"An error occurred: {e}")
        return content

    def _set_template_tags(self):
        #### simple stringg template : No tags values replace or assign.
        extract_tag_json = self.extract_fields_tag
        #response_field_tag_value = self.response_field_tag
        document_content_value = self.document_content
        template_content = self._get_template_text()
        template_content = template_content.replace("{document_type}", self.document_type)
        prompt_template_json = template_content.format(
        extract_field_tag='{extract_field_tag}',
        document_content='{document_content}'
        )
        json_str = json.dumps(extract_tag_json, indent=2)
        return prompt_template_json, json_str
        #print(prompt_template_json)
        
    def get_formatted_prompt_template(self):
       return self._set_template_tags()

    def _read_json(self, json_path):
        data = {}
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            pass
        return data

    def _get_required_fields(self, data):
        extract_fields_tag = []
        response_field_tag = []
        #concept_names = []
        for item in data:
                #concept_names.append(item.get("synonyms", ""))
                extract_items = {
                    "conceptName": item.get("synonyms", ""),
                    "description": item.get("description", "")
                }
                response_field_items = {
                    "conceptName": item.get("conceptName", ""),
                    "conceptValue": item.get("conceptValue", None)
                }
                extract_fields_tag.append(extract_items)
                response_field_tag.append(response_field_items)
        
        #result = ','.join(concept_names)
        return extract_fields_tag, response_field_tag

    # def collect_conceptname(file_path, document_content_value):
    #     extract_fields_tag_value, response_field_tag_value = get_required_fields(file_path)    
    #     set_template_tags(extract_fields_tag_value, response_field_tag_value, document_content_value)


if __name__ == "__main__":
    file_path = r"C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\testfiles\test.json"
    cls_obj = LeafletCanmonTemplatePrompt(" Master Service Agreement ", "canmon_prompt_template.md", "document text sample", "test.json")
    #(self, document_type, prompt_template_path, document_content, request_json)
    
    ###collect_conceptname(file_path) 
