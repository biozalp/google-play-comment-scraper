# Google Play Store Comment Scraper

A Python tool to scrape comments and reviews from Google Play Store app pages.

## Features

- Scrapes user reviews from Google Play Store app pages
- Captures ratings, comments, and developer responses
- Supports different country stores via country codes
- Outputs data to CSV files with app name and timestamp
- Interactive command-line interface

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the script with:

```
python scraper.py
```

This will start in interactive mode, prompting you for:
- App URL or ID
- Country code

### Command Line Arguments

```
python scraper.py --app [APP_ID_OR_URL] --country [COUNTRY_CODE] --count [NUMBER_OF_REVIEWS] --output [OUTPUT_DIRECTORY]
```

Parameters:
- `--app`: App ID or Google Play Store URL (optional, will prompt if not provided)
- `--country`: Country code e.g., 'us', 'gb', 'ca' (optional, will prompt if not provided)
- `--count`: Number of reviews to fetch (default: 100)
- `--output`: Directory to save the CSV file (default: current directory)
- `--list-countries`: Display available country codes

### Examples

```
# Interactive mode
python scraper.py

# Specify app and country
python scraper.py --app com.example.app --country us

# Specify app URL and country
python scraper.py --app "https://play.google.com/store/apps/details?id=com.example.app" --country de

# List available country codes
python scraper.py --list-countries
```

## Output

The script generates a CSV file with the following format:
- Filename: `AppName_YYYYMMDD_HHMMSS.csv`
- Contents: username, rating, comment, date, developer_response

## Limitations

- The scraper uses a simplified approach to extract data from Google Play Store pages
- Google may change their page structure, which could break the scraper
- The number of reviews that can be fetched may be limited by Google's API
