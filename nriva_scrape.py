import requests
import json
import os
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path

class NRIVAScraperSimple:
    def __init__(self, base_url="https://www.nriva.org", output_dir="nriva_profiles"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.session = requests.Session()
        self.csrf_token = None
        self.profiles_data = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('nriva_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directories
        self.setup_directories()
        
        # Setup session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def setup_directories(self):
        """Create necessary directories for storing scraped data"""
        directories = [
            self.output_dir,
            f"{self.output_dir}/profiles",
            f"{self.output_dir}/images",
            f"{self.output_dir}/horoscopes",
            f"{self.output_dir}/data"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def login(self, username, password):
        """Login to NRIVA website"""
        try:
            self.logger.info("Attempting to login...")
            
            # First get the login page to extract CSRF token
            login_page_url = f"{self.base_url}/login"
            response = self.session.get(login_page_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            
            if csrf_meta:
                self.csrf_token = csrf_meta.get('content')
                self.logger.info(f"CSRF Token extracted: {self.csrf_token[:10]}...")
            
            # Prepare login data
            login_data = {
                "_token": self.csrf_token,
                "email": username,
                "password": password,
                "captcha": "14"  # This might need to be dynamic
            }
            
            # Perform login
            response = self.session.post(login_page_url, data=login_data)
            response.raise_for_status()
            
            # Check if login was successful
            if response.status_code == 200:
                self.logger.info("Login request sent successfully")
                
                # Check if we're redirected to a dashboard or account page
                if "dashboard" in response.url or "account" in response.url:
                    self.logger.info("Login successful - redirected to dashboard")
                    return True
                else:
                    # Check response content for login success indicators
                    if "logout" in response.text.lower() or "dashboard" in response.text.lower():
                        self.logger.info("Login appears successful")
                        return True
                    else:
                        self.logger.warning("Login may have failed - check response")
                        return False
            else:
                self.logger.error(f"Login failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def get_csrf_token(self):
        """Extract CSRF token from the search page"""
        try:
            search_url = f"{self.base_url}/eedu-jodu/search-profiles"
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            
            if csrf_meta:
                self.csrf_token = csrf_meta.get('content')
                self.logger.info(f"CSRF Token extracted: {self.csrf_token[:10]}...")
                return True
            else:
                self.logger.error("CSRF token not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error getting CSRF token: {e}")
            return False
    
    def search_profiles(self, gender="Female", max_age=31, citizenship="USA"):
        """Search for profiles with specified criteria"""
        if not self.csrf_token:
            if not self.get_csrf_token():
                return []
        
        search_url = f"{self.base_url}/eedu-jodu/search-eedujodu-profiles"
        
        # Prepare search parameters based on the JavaScript code from the HTML
        search_data = {
            "_token": self.csrf_token,
            "gender": gender,
            "max_age": max_age,
            "citizenship": citizenship,
            "draw": 1,
            "start": 0,
            "length": 100,
            "search": {"value": "", "regex": False},
            "order": [{"column": 1, "dir": "asc"}]
        }
        
        try:
            self.logger.info(f"Searching for profiles: Gender={gender}, Max Age={max_age}, Citizenship={citizenship}")
            
            # Set content type for JSON
            headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.post(search_url, json=search_data, headers=headers)
            response.raise_for_status()
            
            self.logger.info(f"Search response status: {response.status_code}")
            self.logger.info(f"Search response headers: {dict(response.headers)}")
            
            try:
                data = response.json()
                self.logger.info(f"Search response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                self.logger.info(f"Response content: {response.text[:500]}...")
                return []
            
            if 'data' in data:
                total_records = data.get('recordsTotal', 0)
                self.logger.info(f"Found {total_records} profiles matching criteria")
                
                # Process all pages
                all_profiles = []
                page = 0
                
                while True:
                    search_data['start'] = page * search_data['length']
                    search_data['draw'] = page + 1
                    
                    response = self.session.post(search_url, json=search_data, headers=headers)
                    response.raise_for_status()
                    
                    page_data = response.json()
                    
                    if not page_data.get('data'):
                        break
                    
                    all_profiles.extend(page_data['data'])
                    self.logger.info(f"Processed page {page + 1}, got {len(page_data['data'])} profiles")
                    
                    if len(page_data['data']) < search_data['length']:
                        break
                    
                    page += 1
                    time.sleep(1)  # Be respectful to the server
                
                return all_profiles
            else:
                self.logger.error("No data found in response")
                self.logger.info(f"Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching profiles: {e}")
            return []
    
    def extract_profile_details(self, profile_html):
        """Extract detailed information from profile HTML"""
        soup = BeautifulSoup(profile_html, 'html.parser')
        
        profile_data = {}
        
        try:
            # Extract basic information
            # Profile ID
            profile_id_elem = soup.find('td', string=re.compile(r'Profile ID', re.I))
            if profile_id_elem:
                profile_data['profile_id'] = profile_id_elem.find_next('td').get_text(strip=True)
            
            # Name
            name_elem = soup.find('h4', class_='OpenSans-Semibold')
            if name_elem:
                profile_data['name'] = name_elem.get_text(strip=True)
            
            # User ID
            user_id_elem = soup.find('h5', string=re.compile(r'User ID', re.I))
            if user_id_elem:
                user_id_text = user_id_elem.get_text()
                user_id_match = re.search(r'(\d+)', user_id_text)
                if user_id_match:
                    profile_data['user_id'] = user_id_match.group(1)
            
            # Profile image
            img_elem = soup.find('img', class_='userprofileimage')
            if img_elem and img_elem.get('src'):
                profile_data['profile_image_url'] = img_elem['src']
            
        except Exception as e:
            self.logger.error(f"Error extracting profile details: {e}")
        
        return profile_data
    
    def download_file(self, url, filepath):
        """Download a file from URL to specified filepath"""
        try:
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Downloaded: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {e}")
            return False
    
    def get_profile_page(self, profile_id):
        """Get the detailed profile page for a specific profile ID"""
        try:
            # Try different URL patterns for profile pages
            possible_urls = [
                f"{self.base_url}/eedu-jodu/profile/{profile_id}",
                f"{self.base_url}/eedu-jodu/view-profile/{profile_id}",
                f"{self.base_url}/eedu-jodu/profile-details/{profile_id}",
                f"{self.base_url}/account/profile/{profile_id}"
            ]
            
            for url in possible_urls:
                try:
                    response = self.session.get(url)
                    if response.status_code == 200:
                        return response.text
                except:
                    continue
            
            self.logger.warning(f"Could not find profile page for ID {profile_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting profile page for ID {profile_id}: {e}")
            return None
    
    def process_profile(self, profile_data):
        """Process individual profile and extract all data"""
        profile_id = profile_data.get('member_id') or profile_data.get('profile_id')
        
        if not profile_id:
            self.logger.warning("No profile ID found, skipping profile")
            return None
        
        self.logger.info(f"Processing profile ID: {profile_id}")
        
        # Create profile directory
        profile_dir = Path(f"{self.output_dir}/profiles/{profile_id}")
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        # Get detailed profile page
        profile_html = self.get_profile_page(profile_id)
        
        if profile_html:
            # Extract detailed information
            detailed_data = self.extract_profile_details(profile_html)
            profile_data.update(detailed_data)
            
            # Save profile HTML
            html_file = profile_dir / "profile.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(profile_html)
            
            # Extract and download images
            self.extract_images(profile_html, profile_dir)
            
            # Extract and download horoscope
            self.extract_horoscope(profile_html, profile_dir)
        
        # Save profile data as JSON
        json_file = profile_dir / "profile_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        return profile_data
    
    def extract_images(self, html_content, profile_dir):
        """Extract and download images from profile HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        images_dir = profile_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Find all images
        img_tags = soup.find_all('img')
        
        for i, img in enumerate(img_tags):
            src = img.get('src')
            if src:
                try:
                    # Generate filename
                    ext = Path(urlparse(src).path).suffix or '.jpg'
                    filename = f"image_{i}{ext}"
                    filepath = images_dir / filename
                    
                    # Download image
                    if self.download_file(src, filepath):
                        self.logger.info(f"Downloaded image: {filename}")
                        
                except Exception as e:
                    self.logger.error(f"Error downloading image {src}: {e}")
    
    def extract_horoscope(self, html_content, profile_dir):
        """Extract and download horoscope PDF if available"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for horoscope links
        horoscope_links = soup.find_all('a', href=re.compile(r'horoscope|kundali|pdf', re.I))
        
        for link in horoscope_links:
            href = link.get('href')
            if href:
                try:
                    filename = f"horoscope_{Path(urlparse(href).path).name}"
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'
                    
                    filepath = profile_dir / filename
                    
                    if self.download_file(href, filepath):
                        self.logger.info(f"Downloaded horoscope: {filename}")
                        
                except Exception as e:
                    self.logger.error(f"Error downloading horoscope {href}: {e}")
    
    def scrape_all_profiles(self, username="prateekvishnu04@gmail.com", password="bHZV2btjn6FK@2"):
        """Main method to scrape all profiles"""
        self.logger.info("Starting NRIVA profile scraping...")
        
        # Try to login first
        if username and password:
            if not self.login(username, password):
                self.logger.warning("Login failed, but continuing with public access...")
        
        # Search for profiles
        profiles = self.search_profiles(gender="Female", max_age=31, citizenship="USA")
        
        if not profiles:
            self.logger.error("No profiles found")
            return
        
        self.logger.info(f"Found {len(profiles)} profiles to process")
        
        # Process each profile
        for i, profile in enumerate(profiles, 1):
            self.logger.info(f"Processing profile {i}/{len(profiles)}")
            
            processed_profile = self.process_profile(profile)
            if processed_profile:
                self.profiles_data.append(processed_profile)
            
            # Be respectful to the server
            time.sleep(2)
        
        # Save summary data
        self.save_summary()
        
        self.logger.info("Scraping completed!")
    
    def save_summary(self):
        """Save summary of all scraped profiles"""
        # Save as JSON
        summary_file = Path(f"{self.output_dir}/data/all_profiles.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.profiles_data, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        if self.profiles_data:
            df = pd.json_normalize(self.profiles_data)
            csv_file = Path(f"{self.output_dir}/data/all_profiles.csv")
            df.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Save summary report
        report_file = Path(f"{self.output_dir}/data/scraping_report.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"NRIVA Profile Scraping Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total profiles scraped: {len(self.profiles_data)}\n")
            f.write(f"Search criteria: Female, Max Age 31, USA Citizenship\n")
            f.write(f"\nProfile IDs:\n")
            for profile in self.profiles_data:
                f.write(f"- {profile.get('member_id', 'N/A')}: {profile.get('name', 'N/A')}\n")
        
        self.logger.info(f"Summary saved to {self.output_dir}/data/")

def main():
    """Main function to run the scraper"""
    scraper = NRIVAScraperSimple()
    scraper.scrape_all_profiles()

if __name__ == "__main__":
    main() 