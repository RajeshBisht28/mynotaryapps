
"""
Leaflet Technology - 2025
Initiate by: Rajesh Bisht
SEQ Legal Document List Scraper
This script scrapes and displays all available free legal documents from seqlegal.com
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from urllib.parse import urljoin, urlparse
import time
import re
from typing import List, Dict, Optional

class SEQLegalScraper:
    def __init__(self):
        self.base_url = "https://seqlegal.com"
        self.free_docs_url = f"{self.base_url}/free-legal-documents"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.documents = []
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            #print(f"Error fetching {url}: {e}")
            return None
            
    def extract_document_info(self, doc_element) -> Dict:
        """Extract document information from HTML element"""
        doc_info = {
            'title': '',
            'url': '',
            'description': '',
            'category': '',
            'image_url': ''
        }
        
        # Extract title and URL
        title_link = doc_element.find('a')
        if title_link:
            doc_info['title'] = title_link.get_text(strip=True)
            doc_info['url'] = urljoin(self.base_url, title_link.get('href', ''))
            
        # Extract description
        desc_elem = doc_element.find('p') or doc_element.find('div', class_='description')
        if desc_elem:
            doc_info['description'] = desc_elem.get_text(strip=True)
            
        # Extract image URL
        img_elem = doc_element.find('img')
        if img_elem:
            doc_info['image_url'] = urljoin(self.base_url, img_elem.get('src', ''))
            
        return doc_info
        
    def scrape_main_documents_page(self):
        """Scrape the main free documents page"""
        #print("Scraping main documents page...")
        soup = self.get_page(self.free_docs_url)
        
        if not soup:
            #print("Failed to load main documents page")
            return
            
        # Find document containers - these may vary based on site structure
        doc_containers = (
            soup.find_all('div', class_=['document-item', 'doc-item', 'legal-doc']) or
            soup.find_all('article') or
            soup.find_all('div', class_=re.compile(r'.*doc.*|.*item.*|.*card.*'))
        )
        
        # If no specific containers found, look for links in the content area
        if not doc_containers:
            content_area = soup.find('div', class_=['content', 'main-content', 'entry-content']) or soup.find('main')
            if content_area:
                doc_links = content_area.find_all('a', href=re.compile(r'/free-legal-documents/'))
                for link in doc_links:
                    if link.get_text(strip=True):
                        doc_info = {
                            'title': link.get_text(strip=True),
                            'url': urljoin(self.base_url, link.get('href', '')),
                            'description': '',
                            'category': self.categorize_document(link.get_text(strip=True)),
                            'image_url': ''
                        }
                        self.documents.append(doc_info)
        
        for container in doc_containers:
            doc_info = self.extract_document_info(container)
            if doc_info['title'] and doc_info['url']:
                doc_info['category'] = self.categorize_document(doc_info['title'])
                self.documents.append(doc_info)
                
        #print(f"Found {len(self.documents)} documents on main page")
        
    def categorize_document(self, title: str) -> str:
        """Categorize document based on title"""
        title_lower = title.lower()
        
        categories = {
            'Website & Privacy': ['privacy', 'cookie', 'terms', 'website', 'disclaimer', 'gdpr'],
            'Business Agreements': ['agreement', 'contract', 'consultancy', 'service', 'partnership'],
            'Employment': ['employment', 'employee', 'job', 'work', 'hr'],
            'Property & Real Estate': ['property', 'lease', 'rent', 'real estate', 'land'],
            'Medical & Health': ['medical', 'health', 'patient', 'healthcare'],
            'Legal Notices': ['notice', 'legal', 'warning', 'liability'],
            'General': []
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
                
        return 'General'
        
    def get_detailed_document_info(self, doc_url: str) -> Dict:
        """Get detailed information about a specific document"""
        soup = self.get_page(doc_url)
        if not soup:
            return {}
            
        detail_info = {}
        
        # Extract description
        desc_elem = (soup.find('div', class_=['description', 'content', 'entry-content']) or 
                    soup.find('p'))
        if desc_elem:
            detail_info['detailed_description'] = desc_elem.get_text(strip=True)[:500]
            
        # Look for download links
        download_links = soup.find_all('a', href=re.compile(r'\.(pdf|doc|docx)$'))
        detail_info['download_links'] = [urljoin(self.base_url, link.get('href')) 
                                       for link in download_links]
        
        return detail_info
        
    def scrape_all_documents(self):
        """Main method to scrape all documents"""
        #print("Starting SEQ Legal document scraping...")
        
        # First, get documents from main page
        self.scrape_main_documents_page()
        
        # Add known documents based on search results
        known_documents = [
            {
                'title': 'Privacy Policy',
                'url': f"{self.base_url}/free-legal-documents/privacy-policy",
                'category': 'Website & Privacy',
                'description': 'Privacy policy template for websites'
            },
            {
                'title': 'Legal Disclaimer',
                'url': f"{self.base_url}/free-legal-documents/legal-disclaimer",
                'category': 'Legal Notices',
                'description': 'Legal disclaimer template'
            },
            {
                'title': 'Website Terms and Conditions',
                'url': f"{self.base_url}/free-legal-documents/website-terms-and-conditions",
                'category': 'Website & Privacy',
                'description': 'Website terms and conditions template'
            },
            {
                'title': 'Medical Disclaimer',
                'url': f"{self.base_url}/free-legal-documents/medical-disclaimer",
                'category': 'Medical & Health',
                'description': 'Medical disclaimer for websites with health information'
            },
            {
                'title': 'Consultancy Agreement',
                'url': f"{self.base_url}/free-legal-documents/consultancy-agreement",
                'category': 'Business Agreements',
                'description': 'Consultancy agreement template'
            }
        ]
        
        # Add known documents if not already found
        existing_urls = {doc['url'] for doc in self.documents}
        for known_doc in known_documents:
            if known_doc['url'] not in existing_urls:
                self.documents.append(known_doc)
        
        #print(f"Total documents found: {len(self.documents)}")
        
        # Get detailed info for each document (with rate limiting)
        #print("Getting detailed information for each document...")
        for i, doc in enumerate(self.documents):
            #print(f"Processing {i+1}/{len(self.documents)}: {doc['title']}")
            detailed_info = self.get_detailed_document_info(doc['url'])
            doc.update(detailed_info)
            time.sleep(1)  # Rate limiting
     
    def get_json_data(self):
        return json.dumps(self.documents, indent=2)
    
    def get_download_urls(self) -> List[str]:
        """Get all direct download URLs"""
        download_urls = []
        for doc in self.documents:
            if doc.get('download_links'):
                download_urls.extend(doc['download_links'])
        return download_urls
    
    def get_docs_info(self):
        try:
            self.scrape_all_documents()
            return self.get_json_data()
        except Exception as e:
            return str(e)

def main():
    """Main function to run the scraper"""
    scraper = SEQLegalScraper()
    
    try:
        # Scrape all documents
        scraper.scrape_all_documents()
        return self.get_json_data()
        # Display results
       # scraper.display_documents()   
    except KeyboardInterrupt:
        pass
        #print("\nScraping interrupted by user.")
    except Exception as e:
        return str(e)
       # print(f"Error during scraping: {e}")

if __name__ == "__main__":
    main()