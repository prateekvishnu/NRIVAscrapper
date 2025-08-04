#!/usr/bin/env python3
"""
NRIVA Profile Scraper
Scrapes female profiles with max age 31 and USA citizenship from nriva.org
"""

import requests
import re
import json
import logging
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pandas as pd


class NRIVAScraper:
    """Main scraper class for NRIVA profiles"""
    
    def __init__(self):
        """Initialize the scraper with session and configuration"""
        self.session = requests.Session()
        self.base_url = "https://www.nriva.org"
        self.search_url = f"{self.base_url}/eedu-jodu/search-profiles"
        self.login_url = f"{self.base_url}/login"
        self.search_endpoint = f"{self.base_url}/eedu-jodu/search-eedujodu-profiles"
        
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
        
        # Setup output directory
        self.output_dir = Path("nriva_profiles")
        self.output_dir.mkdir(exist_ok=True)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.logger.info("NRIVA Scraper initialized")
    
    def solve_math_captcha(self, captcha_text):
        """Solve simple math captcha like '5 + 9 = '"""
        try:
            # Extract numbers and operator using regex
            match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)\s*=', captcha_text)
            if match:
                num1 = int(match.group(1))
                operator = match.group(2)
                num2 = int(match.group(3))
                
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '*':
                    result = num1 * num2
                elif operator == '/':
                    result = num1 / num2
                else:
                    return None
                
                self.logger.info(f"Solved captcha: {num1} {operator} {num2} = {result}")
                return str(result)
            else:
                self.logger.warning(f"Could not parse captcha: {captcha_text}")
                return None
        except Exception as e:
            self.logger.error(f"Error solving captcha: {e}")
            return None
    
    def get_captcha_from_login_page(self):
        """Get captcha from login page"""
        try:
            response = self.session.get(self.login_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for captcha text in various possible locations
            captcha_selectors = [
                'label:contains("captcha")',
                '.captcha',
                '#captcha',
                'input[name="captcha"]',
                'label[for*="captcha"]'
            ]
            
            # Try to find captcha text in the page
            captcha_text = None
            for selector in captcha_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if re.search(r'\d+\s*[+\-*/]\s*\d+\s*=', text):
                        captcha_text = text
                        break
                if captcha_text:
                    break
            
            # If not found in specific elements, search in all text
            if not captcha_text:
                page_text = soup.get_text()
                captcha_match = re.search(r'(\d+\s*[+\-*/]\s*\d+\s*=)', page_text)
                if captcha_match:
                    captcha_text = captcha_match.group(1)
            
            if captcha_text:
                self.logger.info(f"Found captcha: {captcha_text}")
                return captcha_text
            else:
                self.logger.warning("No captcha found on login page")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting captcha: {e}")
            return None
    
    def get_csrf_token(self, soup):
        """Extract CSRF token from BeautifulSoup object"""
        try:
            # Look for CSRF token in meta tag
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                return csrf_meta.get('content')
            
            # Look for CSRF token in input field
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                return csrf_input.get('value')
            
            # Look for CSRF token in any input with csrf in name
            csrf_input = soup.find('input', {'name': re.compile(r'csrf|token', re.I)})
            if csrf_input:
                return csrf_input.get('value')
            
            self.logger.warning("No CSRF token found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting CSRF token: {e}")
            return None
    
    def login(self, username, password):
        """Login to NRIVA with captcha solving"""
        try:
            self.logger.info("Attempting to login...")
            
            # Get login page and extract CSRF token
            response = self.session.get(self.login_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get CSRF token
            csrf_token = self.get_csrf_token(soup)
            if not csrf_token:
                self.logger.error("Could not get CSRF token")
                return False
            
            # Get captcha from login page
            captcha_text = self.get_captcha_from_login_page()
            if not captcha_text:
                self.logger.error("Could not get captcha from login page")
                return False
            
            # Solve captcha
            captcha_solution = self.solve_math_captcha(captcha_text)
            if not captcha_solution:
                self.logger.error("Could not solve captcha")
                return False
            
            # Prepare login data
            login_data = {
                '_token': csrf_token,
                'email': username,
                'password': password,
                'captcha': captcha_solution
            }
            
            # Submit login form
            response = self.session.post(self.login_url, data=login_data)
            
            # Check if login was successful
            if response.status_code == 200:
                # Check if we're redirected to dashboard or still on login page
                if 'dashboard' in response.url or 'login' not in response.url:
                    self.logger.info("Login successful!")
                    return True
                else:
                    # Check for error messages in response
                    soup = BeautifulSoup(response.content, 'html.parser')
                    error_messages = soup.find_all(class_=re.compile(r'error|alert|danger', re.I))
                    if error_messages:
                        error_text = ' '.join([msg.get_text().strip() for msg in error_messages])
                        self.logger.error(f"Login failed: {error_text}")
                    else:
                        self.logger.error("Login failed: Unknown error")
                    return False
            else:
                self.logger.error(f"Login failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            return False
    
    def search_profiles(self, gender="Female", max_age=31, citizenship="USA"):
        """Search for profiles with specified criteria"""
        try:
            self.logger.info(f"Searching for profiles: Gender={gender}, Max Age={max_age}, Citizenship={citizenship}")
            
            # First get the search page to extract CSRF token
            response = self.session.get(self.search_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get CSRF token
            csrf_token = self.get_csrf_token(soup)
            if not csrf_token:
                self.logger.error("Could not get CSRF token from search page")
                return []
            
            # Prepare search data
            search_data = {
                '_token': csrf_token,
                'gender': gender,
                'max_age': max_age,
                'citizenship': citizenship
            }
            
            # Submit search request
            response = self.session.post(self.search_endpoint, data=search_data)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if 'data' in data:
                profiles = data['data']
                total_records = data.get('recordsTotal', len(profiles))
                self.logger.info(f"Found {total_records} profiles matching criteria")
                return profiles
            else:
                self.logger.error("No data found in search response")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching profiles: {e}")
            return []


if __name__ == "__main__":
    scraper = NRIVAScraper()
    print("NRIVA Scraper created successfully!")
    
    # Test login
    success = scraper.login("prateekvishnu04@gmail.com", "bHZV2btjn6FK@2")
    if success:
        print("Login test successful!")
        
        # Test search
        profiles = scraper.search_profiles()
        print(f"Found {len(profiles)} profiles")
    else:
        print("Login test failed!") 