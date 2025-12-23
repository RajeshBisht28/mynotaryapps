
# This code is part of a web scraping project using Playwright and BeautifulSoup to extract content from Salesforce pages.
# It logs in to a Salesforce instance, navigates through content links, and saves the text content to files.
# The code also collects links and saves them in a JSON file for further reference.
#date initiated: 12-AUG-2025
#last edited: 21-AUG-2025
#Lead By: Rajesh Bisht

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import time
import json
import sys
import traceback

class LeafletSalesForceVer100:
    def __init__(self):
        self.file_path = r"F:\IISsites\PythonSP\notary_source\TextData\summary.txt"
        self.rootdir = r"F:\IISsites\PythonSP\notary_source\TextData"
        self.file_name_list = []
        self.urls_list = []
        self.ignore_href = []
        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir)
    
    def extract_page_main_class_content_only(self, class_name, html_content):
        """Extract text only from <div class="main"> element"""
        soup = BeautifulSoup(html_content, 'lxml')  # 'html.parser')
        # Find the div with class="page"
        main_div = soup.find('div', class_= 'main')
        if main_div:
            # Extract text while preserving some structure
            text_content = main_div.get_text(separator='\n', strip=True)
            return text_content
        else:
            return "Page div not found"
    
    def write_text(self, content):
        with open(self.file_path, "a", encoding='utf-8') as file:
            file.write(content)

    def write_links_first_level_text(self, page, all_links):
        i = 0
        json_data = []
        try:
            for link in all_links:
                url = link['href']
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
               # page.goto(url, wait_until="load")
                page.wait_for_selector('div.main', timeout=10000)  #state='visible')  # Wait until .main is visible
                page.wait_for_timeout(3*1000)  # Wait for 3 seconds to ensure the page is fully loaded
                
                full_html = page.content()
                body_text = self.extract_page_main_class_content_only('main', full_html)
                soup = BeautifulSoup(full_html, 'html.parser')
                complete_text = soup.get_text(separator='\n', strip=True)
                content = f"\n{url}\n\n{body_text}"
                complete_text = f"\n{url}\n\n{complete_text}"
                filename = self.file_name_list[i]
                filepath = os.path.join(self.rootdir, filename)
                extrra_filepath = os.path.join(self.rootdir, f"FullText_{filename}")
                
                try:
                    with open(filepath, "w", encoding='utf-8') as file:
                        file.write(content)
                except Exception as e:
                    pass

                try:
                    with open(extrra_filepath, "w", encoding='utf-8') as file:
                        file.write(complete_text)
                except Exception as e:
                    pass
                    #print(f"Error writing to file {filepath}: {e}")

                link_info = {
                "filepath": filepath,
                "fullTextPath": extrra_filepath,
                "url": url
                }
                json_data.append(link_info)
                i += 1

        except Exception as exp:
            pass
            #print(f"Exp: write_links_first_level_text: {exp}")
        return json_data
    
    def get_content_links_from_page(self, page):
        soup = BeautifulSoup(page.content(), 'html.parser')
        links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)

            if href.startswith('/'):
                current_url = page.url
                base_url = f"{current_url.split('/')[0]}//{current_url.split('/')[2]}"
                href = base_url + href
            elif not href.startswith('http') and not href.startswith('javascript'):
                current_url = page.url
                base_url = '/'.join(current_url.split('/')[:-1])
                href = base_url + '/' + href
            
            if(self.exist_inlist(text, href, links)):
                continue

            if (
                href
                and not href.startswith('javascript')
                and href.startswith('https')
                and '=site_content_tab&' in href
                and text
            ):
                links.append({'href': href, 'text': text})

        return links
    
    def get_inside_links_from_page(self, page):

        soup = BeautifulSoup(page.content(), 'lxml') ### 'html.parser')
       # links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)

            if href.startswith('/'):
                current_url = page.url
                base_url = f"{current_url.split('/')[0]}//{current_url.split('/')[2]}"
                href = base_url + href
            elif not href.startswith('http') and not href.startswith('javascript') and not href.startswith('mail'):
                current_url = page.url
                base_url = '/'.join(current_url.split('/')[:-1])
                href = base_url + '/' + href
            
            if(self.exist_inlist(text, href, self.urls_list)):
                continue

            if(href in self.ignore_href):
               continue

            if (
                href
                and not href.startswith('javascript')
                and href.startswith('https')
                and '--sandbox--simpplr.sandbox.' in href
                and text
            ):
                self.urls_list.append({'href': href, 'text': text})
                #print(f"self.href_list : {len(self.urls_list)}")

        
        return True
    
    def exist_inlist(self, text, url, list_data):
        for link in list_data:
            if(text.lower().strip()==link['text'].lower().strip() or url.lower().strip() == link['href'].lower().strip()):
                return True
        return False
        
    def traverse_inner_level(self, page, all_links):
        for link in all_links:
            if(self.exist_inlist(link['text'], link['href'], self.urls_list)):
                continue
            
            self.urls_list.append(link)
        
        
        lookup = []
        lookup.append("dummy...")
        
        prev_counts = 0
        prev_match = 0
        for link in self.urls_list:
            url = link['href']
                        
            if(url in lookup or url in self.ignore_href):
                continue
                        
            lookup.append(url)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            page.wait_for_selector('div.main', timeout=10000)
            page.wait_for_timeout(3*1000) 
            self.get_inside_links_from_page(page)
            if(prev_counts == len(self.urls_list)):
                prev_match = prev_match + 1
            else:
                prev_match = 0
            
            if prev_match > 3:                
                break
            prev_counts = len(self.urls_list)
            #print(f"iteration: {i} ==> total self.urls_list: {len(self.urls_list)}")
        
        ###self.write_text(f"{self.urls_list}")

    def scrape_salesforce_1_level(self):
        self.ignore_href.append("https://veracity--sandbox--simpplr.sandbox.vf.force.com/apex/simpplr__app?u=/")
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        trc_msg = "Starting Salesforce scraping...\n"
        self.write_text(trc_msg)
        """
        if not sys.stdout:
           sys.stdout = open(os.devnull, "w")
        if not sys.stderr:
           sys.stderr = open(os.devnull, "w")
        if not sys.stdin:
           sys.stdin = open(os.devnull, "r")
        """
        try:
            with sync_playwright() as p:
                self.write_text("\n Launching browser...\n")
                #browser = p.chromium.launch(headless=False)
                browser = p.chromium.launch(
                    headless=False,
                    args=["--disable-gpu", "--disable-software-rasterizer"],
                    executable_path=chrome_path
                )

                forced_user_agent = (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/128.0.0.0 Safari/537.36"
                )

                context = browser.new_context(
                    user_agent=forced_user_agent,
                    locale="en-US",
                    timezone_id="Asia/Kolkata"
                )

                context.add_init_script("localStorage.clear(); sessionStorage.clear();")

                page = context.new_page()
                #page.goto(url, wait_until="domcontentloaded")  # or "networkidle" if it works for your site

                self.write_text("Starting Salesforce scraping...\n")
                login_url = "https://veracity--sandbox--simpplr.sandbox.vf.force.com/apex/simpplr__app?u=/site/a14WE00000nwz8XYAQ/content"

                # Go to login page
                page.goto(login_url)
                page.wait_for_load_state("networkidle")

                # Login
                page.fill('input[name="username"]', "ksbisht@leafletcorp.com.sandbox")
                page.fill('input[name="pw"]', "Leafwel@31")
                page.click('input[name="Login"]')
                wait_time = 10  # seconds
                # Wait for login redirect
                page.wait_for_load_state("networkidle")
                # Open target page again after login
                page.goto(login_url)
                page.wait_for_timeout(wait_time*1500)
                # Get links
                level0_links = self.get_content_links_from_page(page)
                all_links = []
                all_links.extend(level0_links)
                self.traverse_inner_level(page, all_links)
                
                self.write_text(f"\nUnique links collected: {len(self.urls_list)}\n")

                i = 1               
                for link in self.urls_list:
                    onlyname = link['text'].replace('/', '_').replace('\\', '_')
                    filename = f"{onlyname}.txt"
                    self.write_text(f"\nFile path: {os.path.join(self.rootdir, filename)}\n")
                    self.write_text(f"\nVisiting level-1 link: {link['href']}\n")
                    if filename in self.file_name_list:
                        filename = f"{onlyname}_{i}.txt"

                    self.file_name_list.append(filename)
                    i += 1
                # Remove duplicates
                unique_links = {link['href']: link for link in self.urls_list}.values()

                json_data = self.write_links_first_level_text(page, list(self.urls_list)) 
                json_filepath = os.path.join(self.rootdir, 'link_map.json')
                with open(json_filepath, 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
                #print("Links written to files successfully.")
                browser.close()
                return json_data
        except Exception as e:
            self.write_text(f"Error in scrape_salesforce_1_level: {traceback.format_exc()}\n")
            return {"error": str(e)}


if __name__ == "__main__":
    clobj = LeafletSalesForceVer100()
    clobj.scrape_salesforce_1_level()
    #print("Salesforce scraping completed.")
    clobj.write_text("Salesforce scraping completed.\n")
