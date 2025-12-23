

#####################################
#Leaflet web search - version 1.0.1
# Initiated by: Rajesh Bisht
# using : sillenium 
#####################################

from selenium import webdriver
import requests
import time
import json
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class LeafletWebSearch:
    def __init__(self, logger, login_url, module_name, folder_name, documentname, user_name, password):
        self.login_url = login_url
        self.folder_name = folder_name
        self.module_name = module_name
        self.user_name = user_name
        self.password = password
        self.document_name = documentname
        self.logger = logger

    def get_driver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
        })
        chrome_options.add_argument("--disable-password-manager-dorsal")
        chrome_options.add_argument("--disable-save-password-bubble")
        chrome_options.add_argument("--start-maximized") 
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions") 
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def signup_process(self, driver):
        logger = self.logger
        try:            
            logger.debug(f"signup_process:login_url-1: {self.login_url}")    
            driver.get(self.login_url)
            time.sleep(2)
            logger.debug("fill user name...")
            driver.find_element(By.ID, "mat-input-0").send_keys(self.user_name)
            time.sleep(2)
            pass_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "button-signup"))
            )
            pass_button.click()
            time.sleep(3)
            logger.debug("button click...")
            driver.find_element(By.ID, "mat-input-2").send_keys(self.password)
            logger.debug("Fill password...")
            time.sleep(3)
            sign_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Sign In"))
            )
            sign_button.click()
            logger.debug(f"signup_process completed...")
        except Exception as e:
            logger.debug(f"Exp: signup_process: {str(e)}")
            

    def traverse_folder(self, driver):
        logger = self.logger
        logger.debug("traverse_folder start...")
        document_names = []
       
        try:
            element = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[@title='{self.folder_name}']"))
            )
            element.click()
            time.sleep(5)
            logger.debug(f"Folder name :{self.folder_name} clicked.")
            document_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[@id='title-name']"))
            )   
            logger.debug(f"document_elements11 : {len(document_elements)}")
            doc_name = ''
            i = -1
            for element in document_elements:
                i = i+1
                try:
                    doc_name = element.text.strip()
                except Exception as e:
                    pass
                if doc_name:
                    if i % 4 == 0:
                        document_names.append(doc_name)
   
        except Exception as e:
            logger.debug(f"Exp:traverse_folder : {str(e)}")
               
        return document_names


    def main_process(self):
        logger = self.logger
        driver = self.get_driver()
        logger.debug("main_process start...")
        self.signup_process(driver)        
        time.sleep(6)
        documents_list = self.traverse_folder(driver)
        logger.debug(f"documents_list completed counts {len(documents_list)}")
        top10 = documents_list[:10]
        comma_separated = ', '.join(map(str, top10))
        logger.debug(f"Top-10: {comma_separated}")
        #print(f"Found {len(document_names)} documents:")
        #for i, name in enumerate(document_names, 1):
            #print(f"{i}. {name}")
    
        doc_name = self.document_name
        logger.debug(f"doc name: {doc_name}")
        document_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//span[@id='title-name' and normalize-space(text())='{doc_name}']"))
            )
        
        context_menu_button = document_element.find_element(By.XPATH, ".//ancestor::*[contains(@class, 'row') or contains(@class, 'item')]//button[last()]")
        context_menu_button.click()
        logger.debug("context menu clicked...")
        export_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Export to Local')]"))
        )
        export_option.click()
        logger.debug("Export to Local clicked...")
        time.sleep(4)        

        ok_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button/span[contains(text(), 'OK')]"))
        )
                
        ok_button.click()
        logger.debug("OK button clicked...")
        logger.debug(f"Successfully exported: {doc_name}")


if __name__ == "__main__":
    json_path = "docsearch.json"
    logging.basicConfig(filename="debuglog.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
                    
    logger = logging.getLogger('testlogs')
    logger.setLevel(logging.DEBUG)
    data = {}
    with open(json_path, 'r') as f:
        data = json.load(f)
   # login_url, module_name, folder_name, user_name, password):
    url = f"https://uat.leafletcorp.com:2508/llc/auth/email?module=DraftLive"
    folder_name = "Meenu"
    clobj = LeafletWebSearch(logger, data['url'], data['module'], data['folder'], data['document'], data['username'], data['password'])
    clobj.main_process()
    
