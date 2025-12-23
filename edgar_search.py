
"""
# Last updated: 17 JUL 2025
# Leaflet - Crawling , Scraping
# Initiated by: Bisht Rajesh
# Edgar Search document : American securit exchange : eFiling data.
# Library : BeautifullSoup , sellenium , requests
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
import sys
import requests
import json
import logging
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class LeafletEdgarApp:
    def __init__(self, logger, login_url, company, cik, form_type):
        self.logger = logger
        self.login_url = login_url
        self.company = company
        self.cik = cik
        self.form_type = form_type
        self.TARGET_EXTENSIONS = ('.pdf', '.htm', '.html', '.docx')
        self.collected_file_links = []
        self.session = None
        self.driver = None
        self.popindex=0
    
    def get_driver(self):
        user_data_dir = tempfile.mkdtemp()
        download_dir = os.path.abspath("downloads")
        os.makedirs(download_dir, exist_ok=True)
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.notifications": 2
        })

        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-password-manager-dorsal")
        chrome_options.add_argument("--disable-save-password-bubble")
        chrome_options.add_argument("--start-maximized") 
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions") 
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)
        service = Service()
        driver = webdriver.Chrome(service=service)
        return driver
            
    def links_checks(self, url, download_folder="web_downloads"): 
        driver = self.driver
        logger = self.logger
        logger.debug("links_checks start...")
        os.makedirs(download_folder, exist_ok=True) 
        encoded_name = quote(self.company)
        final_url = url # f"{url}?company={encoded_name}"
        # Setup session with proper headers
        session = requests.Session()
        
        # session.headers.update({
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        # }) 
        session.headers.update =({
            'User-Agent': 'Leafletcorp rbisht@leafletcorp.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        })
       
        self.session = session 
        headers = {
            'User-Agent': 'Leafletcorp rbisht@leafletcorp.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
         }

        logger.debug(f"Fetching URL with GET request: {final_url}")
        all_links = set()
        rendered_html = driver.page_source

        try:
            # GET request to fetch the webpage
            response = session.get(final_url, headers=headers, timeout=30)
            response.raise_for_status()
            logger.debug(f"Successfully fetched page (Status: {response.status_code})") 
            # Parse HTML
            #soup = BeautifulSoup(response.content, 'html.parser')
            soup = BeautifulSoup(rendered_html, 'html.parser')            
            # Find all links 
            logger.debug("********** First Level Links **************")
            
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                full_url = urljoin(url, href)
                full_url = urljoin(url, href)
                logger.debug(f"url111 => {full_url}")
                if(not full_url.lower().startswith("http")):
                    continue 
                # if not any(pattern in full_url.lower() for pattern in [
                #     #'/archives/',
                #     '.htm',
                #     '.html',
                #     '.pdf',
                #     '.txt',
                #     '.xml'
                # ]):
                
                if(re.search(r'&CIK=\d+$', full_url)):
                    all_links.add(full_url)             
                    text = a.get_text(strip=True)
                    return all_links                    
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"Error fetching webpage: {e}")
        return all_links

    def signup_process(self):
        logger = self.logger  
        driver = self.driver        
        loginurl = self.login_url
        try:            
            logger.debug(f"signup_process:login_url: {loginurl}")    
            driver.get(loginurl)
            time.sleep(2)
            logger.debug(f"fill company : {self.company}")
            driver.find_element(By.ID, "company").send_keys(self.company)
            time.sleep(2)
            # logger.debug(f"fill CIK : {self.cik}")
            # driver.find_element(By.ID, "CIK").send_keys(self.cik)
            # time.sleep(1)
            # logger.debug(f"fill form type : {self.form_type}")
            # driver.find_element(By.ID, "form_type").send_keys(self.form_type)
            # time.sleep(1)
            #retrieve_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Retrieve Filings']")))

            # retrieve_button = WebDriverWait(driver, 5).until(
            #     EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Retrieve Filings']"))
            # )
            retrieve_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and text()='Search']"))
            )

            retrieve_button.click()
            time.sleep(3)
            logger.debug("retrieve_button click...")
            
        except Exception as e:
            logger.debug(f"Exp: signup_process: {str(e)}")
    
    def is_target_file(self, url):
        return url.lower().endswith(self.TARGET_EXTENSIONS)

    def crawl_until_file(self, url, visited, depth=0, max_depth=2):
        logger = self.logger
        driver = self.driver
        #logger.debug(f"Inside: crawl_until_file start: URL: {url}")
        if(self.count_threshold_check() == True):
           return
        session = self.session
        logger = self.logger       
        if url in visited or depth > max_depth:            
            return
        
        visited.add(url)        
        driver.get(url)
        time.sleep(4)
        rendered_html = driver.page_source        
        soup = BeautifulSoup(rendered_html, 'html.parser')
        found_links = soup.find_all('a', href=True)
        logger.debug(f"Total found_links founds: {len(found_links)}")
        keywords = ["annual", "report", "of year", "for year", "quarterly", "ending"]
        pattern = re.compile(r"(annual|report|of year|for year|quarterly|ending|)", re.IGNORECASE)

        for a_tag in found_links:
            if(self.count_threshold_check() == True):
               break 
            href = a_tag['href'].strip()
            full_url = urljoin(url, href)
            href_text_val = a_tag.get_text(strip=True)
            #logger.debug(f"href_val111: {href.lower()} and==> {full_url}")            
            if(not href_text_val.strip()):
                continue
            matched = False
            if full_url in self.collected_file_links:
                continue

            if not full_url.startswith('http'):
                continue
            for stext in keywords:
                if stext in href_text_val.lower():
                   matched = True
                   break
            
            if(matched == False):
                continue
            else:
                pass
                
            
            if full_url.lower().endswith(('.htm', '.html', '.xml', '.txt', '.pdf', '.doc', '.docx')):                
                    #logger.debug(f" File found: {full_url}  => {href_text_val}")
                    self.collected_file_links.append(full_url)
                    continue  #  Stop further on this branch
            #if not full_url.lower().endswith(('.htm', '.html')):
                #return
            if(self.count_threshold_check() == True):
               break 

        url_url = None
        if(len(self.collected_file_links) > self.popindex):
           url_url = self.collected_file_links[self.popindex] 
        else:
            return 
        self.popindex = self.popindex + 1
        self.crawl_until_file(url_url, visited, depth+1, max_depth)  ### recursive
    
        
    def start_crawl(self, base_links):
        logger = self.logger        
        logger.debug("Start Crawling Level Depths...")    
        visited = set()
        for link in base_links:
            self.crawl_until_file(link, visited)
        
        logger.debug(f"collected_file_links Results : {self.collected_file_links}")
        logger.debug("Ends Crawling Level Depths...")
    
    def count_threshold_check(self, cnt=5):
        logger = self.logger
        try:
            if(len(self.collected_file_links) > cnt):
               logger.debug("Total count completed")
               return True
        except Exception as e:
            logger.debug(f"Exp: count_threshold_check {str(e)}")
            return False
    
   ######## Download urls ########
    def download_files_and_return_json(self, url_list, download_directory="edgar_downloads"):
        logger = self.logger
        logger.debug("download files and return json start...")
        #logger.debug(f"url_list: {url_list}")
        os.makedirs(download_directory, exist_ok=True)
        downloaded_files_info = {}
    
        headers = {
            "User-Agent": "Rajesh Bisht (rbisht@leafletcorp.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }

        request_delay = 1.5
        suffix_txt = ".txt"
        for url in url_list:
            try:
                logger.debug(f"Attempting to download: {url}")                
                #original_filename = os.path.basename(a.path)
                original_filename = os.path.basename(url)
                #filename_to_save = original_filename
                root_name, extension = os.path.splitext(original_filename)
                if extension == None:
                   extension = ".txt"
                
                local_filepath = os.path.join(download_directory, root_name)
                local_filepath += extension
                logger.debug(f"local_filepath => {local_filepath}")                
                
                response = requests.get(url, stream=True, headers=headers)
                response.raise_for_status() 

                os.makedirs(os.path.dirname(local_filepath), exist_ok=True)

                with open(local_filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                downloaded_files_info[url] = os.path.abspath(local_filepath)
                logger.debug(f"Successfully downloaded: {local_filepath}")

            except requests.exceptions.HTTPError as e:
                logger.debug(f"Error downloading {url}: {e}")
                downloaded_files_info[url] = f"Error: {e.response.status_code} {e.response.reason}"
            except requests.exceptions.RequestException as e:
                logger.debug(f"Network error or other request issue for {url}: {e}")
                downloaded_files_info[url] = f"Network Error: {e}"
            except Exception as e:
                logger.debug(f"An unexpected error occurred for {url}: {e}")
                downloaded_files_info[url] = f"Unexpected Error: {e}"
            finally:                
                time.sleep(request_delay)

        return json.dumps(downloaded_files_info, indent=4)


    def main_process(self):
        logger = self.logger
        driver = None
        logger.debug("**************** EDGAR Process Start ***************")
        try:
            driver = self.get_driver()
            self.driver = driver          
            self.signup_process()
            currenturl = driver.current_url        
            logger.debug(f"Current URL after fill values : {currenturl}")
            link_list = self.links_checks(currenturl)  
            logger.debug(f"Total first level links : {len(link_list)}")
            first_url = list(link_list)[0]
            logger.debug(f"link_list first link: {first_url}")            
            link_list = []
            link_list.append(first_url)     
            self.start_crawl(link_list)           
            logger.debug("After start_crawl...")
            if(self.collected_file_links == None):
                return {}
            if(len(self.collected_file_links) == 0):
                return {}
            logger.debug(f"Total collected_file_links links : {len(self.collected_file_links)}") 
            results = self.download_files_and_return_json(self.collected_file_links)
            return results
        except Exception as e:
            logger.debug(f"Error webpage: {e}")
            return {}
        finally:
            logger.debug("**************** EDGAR Process END ***************")
            driver.quit()
        

if __name__ == "__main__":  
    #argumens = sys.argv 
    logging.basicConfig(filename="debuglog.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
                    
    logger = logging.getLogger('testlogs')
    logger.setLevel(logging.DEBUG)
    json_path = "edgar_search.json"
    data = {}
    with open(json_path, 'r') as f:
        data = json.load(f)

    target_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000904155&owner=include&count=40"
    objLedgar = LeafletEdgarApp(logger, data['url'], data['company'], data['cik'], data['form_type'])
    objLedgar.main_process()
    
