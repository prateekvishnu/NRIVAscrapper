# NRIVA Scraper - Memory Bank

## Custom Rules
1. **Git Version Control**: Every significant change must be committed to Git
2. **Test Before Commit**: Run the scraper and verify it works before each commit
3. **Incremental Development**: Build features one at a time, test, then commit
4. **Documentation**: Update this memory bank with lessons learned

## Project Knowledge

### Website Structure
- **Base URL**: https://www.nriva.org/eedu-jodu/search-profiles
- **Login Required**: Yes, with math captcha
- **Search Endpoint**: POST to /eedu-jodu/search-eedujodu-profiles
- **Profile Format**: Individual profile pages (URL pattern TBD)

### Working Solutions
- **Login**: Math captcha solving with regex parsing
- **Search**: Form-encoded POST with gender=female, max_age=31, citizenship=USA
- **Session Management**: Maintains cookies across requests

### Known Issues
- **Profile Access**: Current profile URL construction fails (404 errors)
- **URL Pattern**: Need to discover correct profile page URL format

### Credentials
- Username: prateekvishnu04@gmail.com
- Password: bHZV2btjn6FK@2

### Dependencies
- requests
- beautifulsoup4
- pandas
- lxml
- urllib3

## Development History
- Started with multiple scraper versions
- Discovered working login and search methods
- Current challenge: Profile page access
- Clean slate approach with Git version control

## Next Steps
1. Create basic scraper structure
2. Implement working login with captcha
3. Implement working search functionality
4. Fix profile page access
5. Add data extraction and storage 