# NRIVA Eedu-Jodu Profile Scraper

A Python scraper for extracting matrimonial profiles from the NRIVA (NRI Vasavi Association) Eedu-Jodu platform. This scraper is designed to search for specific profiles based on criteria like gender, age, and citizenship, then extract and store profile data, images, and horoscope documents.

## Features

- **Advanced Search**: Search profiles by gender, age range, citizenship, education, and more
- **Data Extraction**: Extract comprehensive profile information including personal details, contact info, and preferences
- **Media Download**: Download profile images and horoscope PDFs
- **Multiple Output Formats**: Save data in JSON, CSV, and HTML formats
- **Session Management**: Handle authentication and maintain session cookies
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Rate Limiting**: Respectful scraping with configurable delays

## Requirements

- Python 3.7+
- Chrome browser (for Selenium functionality)
- ChromeDriver (automatically managed if using webdriver-manager)

## Installation

1. **Clone or download the scraper files**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome browser** (if not already installed)

4. **Configure the scraper**:
   - Edit `config.py` to customize search criteria and settings
   - Set login credentials if required

## Usage

### Basic Usage

```python
from nriva_scraper_enhanced import NRIVAScraperEnhanced

# Initialize scraper
scraper = NRIVAScraperEnhanced()

# Run the scraper
scraper.scrape_all_profiles()
```

### With Login Credentials

```python
from nriva_scraper_enhanced import NRIVAScraperEnhanced

# Initialize scraper
scraper = NRIVAScraperEnhanced()

# Run with login credentials
scraper.scrape_all_profiles(
    username="your_email@example.com",
    password="your_password"
)
```

### Custom Search Criteria

```python
from nriva_scraper_enhanced import NRIVAScraperEnhanced

scraper = NRIVAScraperEnhanced()

# Search with custom criteria
profiles = scraper.search_profiles(
    gender="Female",
    max_age=31,
    citizenship="USA",
    min_age=25,
    education_level="Masters Degree"
)

# Process profiles
for profile in profiles:
    scraper.process_profile(profile)
```

## Configuration

Edit `config.py` to customize the scraper behavior:

### Search Criteria
```python
SEARCH_CRITERIA = {
    "gender": "Female",
    "max_age": 31,
    "citizenship": "USA",
    "min_age": None,
    "education_level": None,
    "marital_status": None,
}
```

### Scraping Settings
```python
SCRAPING_SETTINGS = {
    "use_selenium": True,
    "delay_between_requests": 2,
    "max_retries": 3,
    "timeout": 30,
}
```

## Output Structure

The scraper creates the following directory structure:

```
nriva_profiles/
├── profiles/
│   ├── [profile_id_1]/
│   │   ├── profile.html
│   │   ├── profile_data.json
│   │   ├── images/
│   │   │   ├── image_0.jpg
│   │   │   └── image_1.png
│   │   └── horoscope.pdf
│   └── [profile_id_2]/
│       └── ...
├── data/
│   ├── all_profiles.json
│   ├── all_profiles.csv
│   └── scraping_report.txt
├── cookies/
│   └── session_cookies.pkl
└── logs/
    └── nriva_scraper.log
```

## Data Extracted

For each profile, the scraper extracts:

### Basic Information
- Profile ID
- Name
- Age
- Gender
- Marital Status
- Location/Citizenship

### Contact Information
- Email (if available)
- Phone (if available)

### Professional Details
- Education Level
- Profession
- Current Company/Work Location

### Personal Details
- Height
- Zodiac Sign/Rashi
- Horoscope availability

### Media Files
- Profile Images
- Horoscope PDFs (if available)

## Important Notes

### Legal and Ethical Considerations
- **Respect Terms of Service**: Ensure you comply with NRIVA's terms of service
- **Rate Limiting**: The scraper includes delays to avoid overwhelming the server
- **Data Privacy**: Handle scraped data responsibly and in accordance with privacy laws
- **Personal Use**: This tool is intended for personal research purposes only

### Technical Limitations
- The scraper may need adjustments if the website structure changes
- Some profiles may require authentication to access
- Horoscope files may not be available for all profiles
- Image quality and availability may vary

### Troubleshooting

#### Common Issues

1. **CSRF Token Error**
   - The website may have changed its security measures
   - Try refreshing the session or updating the token extraction logic

2. **Login Issues**
   - Verify credentials are correct
   - Check if the website requires additional authentication steps
   - Some profiles may be accessible without login

3. **Selenium Issues**
   - Ensure Chrome browser is installed
   - Update ChromeDriver if needed
   - Try running without Selenium by setting `use_selenium=False`

4. **No Profiles Found**
   - Verify search criteria are correct
   - Check if the website structure has changed
   - Try different search parameters

#### Debug Mode

Enable debug logging by modifying `config.py`:
```python
LOGGING_SETTINGS = {
    "level": "DEBUG",
    # ... other settings
}
```

## Logs

The scraper generates detailed logs in `nriva_scraper.log` including:
- Search progress
- Profile processing status
- Download success/failure
- Error messages and debugging information

## Contributing

To improve the scraper:

1. Test with different search criteria
2. Report any issues with specific error messages
3. Suggest improvements for data extraction
4. Update selectors if the website structure changes

## Disclaimer

This scraper is provided for educational and research purposes. Users are responsible for:
- Complying with the target website's terms of service
- Respecting privacy and data protection laws
- Using scraped data responsibly and ethically
- Not overwhelming the target server with requests

The authors are not responsible for any misuse of this tool or any legal consequences arising from its use. 