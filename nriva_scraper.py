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


if __name__ == "__main__":
    scraper = NRIVAScraper()
    print("NRIVA Scraper created successfully!") 