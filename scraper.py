#!/usr/bin/env python3
import csv
import sys
import time
import datetime
import argparse
import os
from google_play_scraper import app as app_details
from google_play_scraper import Sort, reviews_all, reviews

# Country codes mapping for user reference with their primary language codes
COUNTRY_CODES = {
    'United States': 'us',
    'United Kingdom': 'gb',
    'Canada': 'ca',
    'Australia': 'au',
    'India': 'in',
    'Germany': 'de',
    'France': 'fr',
    'Japan': 'jp',
    'Brazil': 'br',
    'Mexico': 'mx',
    'Spain': 'es',
    'Italy': 'it',
    'Russia': 'ru',
    'South Korea': 'kr',
    'Turkey': 'tr',
    'China': 'cn',
    'Indonesia': 'id',
    'Malaysia': 'my',
    'Philippines': 'ph',
    'Singapore': 'sg',
    'Thailand': 'th',
    'Vietnam': 'vn',
    'Egypt': 'eg',
    'South Africa': 'za',
    'United Arab Emirates': 'ae',
    'Saudi Arabia': 'sa',
    'Israel': 'il',
    'Argentina': 'ar',
    'Chile': 'cl',
    'Colombia': 'co',
    'Peru': 'pe',
    'Venezuela': 've',
    'Belgium': 'be',
    'Netherlands': 'nl',
    'Poland': 'pl',
    'Sweden': 'se',
    'Switzerland': 'ch',
    'Austria': 'at',
    'Denmark': 'dk',
    'Finland': 'fi',
    'Norway': 'no',
    'Greece': 'gr',
    'Hungary': 'hu',
    'Czech Republic': 'cz',
    'Portugal': 'pt',
    'Romania': 'ro',
    'Ukraine': 'ua',
    'New Zealand': 'nz',
    'Ireland': 'ie',
}

def get_app_id_from_url(url):
    """Extract app ID from Google Play Store URL."""
    if 'id=' in url:
        return url.split('id=')[1].split('&')[0]
    elif '/apps/details/' in url:
        return url.split('/apps/details/')[1].split('?')[0]
    else:
        return url  # Assume the input is already an app ID

# Language code mapping for countries
LANGUAGE_CODES = {
    'us': 'en', # United States - English
    'gb': 'en', # United Kingdom - English
    'ca': 'en', # Canada - English (could also be 'fr' for French Canada)
    'au': 'en', # Australia - English
    'in': 'en', # India - English (multiple languages, but English is common)
    'de': 'de', # Germany - German
    'fr': 'fr', # France - French
    'jp': 'ja', # Japan - Japanese
    'br': 'pt', # Brazil - Portuguese
    'mx': 'es', # Mexico - Spanish
    'es': 'es', # Spain - Spanish
    'it': 'it', # Italy - Italian
    'ru': 'ru', # Russia - Russian
    'kr': 'ko', # South Korea - Korean
    'tr': 'tr', # Turkey - Turkish
    'cn': 'zh', # China - Chinese
    'id': 'id', # Indonesia - Indonesian
    'my': 'ms', # Malaysia - Malay
    'ph': 'en', # Philippines - English (Filipino/Tagalog also used)
    'sg': 'en', # Singapore - English
    'th': 'th', # Thailand - Thai
    'vn': 'vi', # Vietnam - Vietnamese
    'eg': 'ar', # Egypt - Arabic
    'za': 'en', # South Africa - English
    'ae': 'ar', # UAE - Arabic
    'sa': 'ar', # Saudi Arabia - Arabic
    'il': 'he', # Israel - Hebrew
    'ar': 'es', # Argentina - Spanish
    'cl': 'es', # Chile - Spanish
    'co': 'es', # Colombia - Spanish
    'pe': 'es', # Peru - Spanish
    've': 'es', # Venezuela - Spanish
    'be': 'nl', # Belgium - Dutch/French
    'nl': 'nl', # Netherlands - Dutch
    'pl': 'pl', # Poland - Polish
    'se': 'sv', # Sweden - Swedish
    'ch': 'de', # Switzerland - German/French/Italian
    'at': 'de', # Austria - German
    'dk': 'da', # Denmark - Danish
    'fi': 'fi', # Finland - Finnish
    'no': 'no', # Norway - Norwegian
    'gr': 'el', # Greece - Greek
    'hu': 'hu', # Hungary - Hungarian
    'cz': 'cs', # Czech Republic - Czech
    'pt': 'pt', # Portugal - Portuguese
    'ro': 'ro', # Romania - Romanian
    'ua': 'uk', # Ukraine - Ukrainian
    'nz': 'en', # New Zealand - English
    'ie': 'en', # Ireland - English
}

def get_language_for_country(country_code):
    """Get the appropriate language code for a country code."""
    return LANGUAGE_CODES.get(country_code.lower(), 'en')  # Default to English if country not found

def get_app_details(app_id, country_code):
    """Get app details using google-play-scraper."""
    try:
        # Get the appropriate language for the country
        lang = get_language_for_country(country_code)
        
        result = app_details(
            app_id,
            lang=lang,  # Language appropriate for the country
            country=country_code  # Country for the app details
        )
        return result
    except Exception as e:
        print(f"Error getting app details: {e}")
        return None

def fetch_reviews(app_id, country_code, count=100):
    """Fetch reviews for the given app ID from Google Play Store."""
    print(f"Fetching reviews for {app_id} from country: {country_code}")
    
    # Get the appropriate language for the country
    lang = get_language_for_country(country_code)
    print(f"Using language code: {lang} for country: {country_code}")
    
    try:
        # For unlimited reviews or large counts, use reviews_all
        if count > 1000 or count == 0:  # 0 means fetch all available reviews
            print("Fetching all available reviews (this might take a while)...")
            result = reviews_all(
                app_id,
                lang=lang,  # Language appropriate for the country
                country=country_code,  # Country for the reviews
                sort=Sort.NEWEST,  # Sort by newest reviews first
            )
            print(f"Found {len(result)} total reviews")
            
            # If count is 0, get all reviews, otherwise limit to the specified count
            if count > 0 and len(result) > count:
                result = result[:count]
                print(f"Limiting to {count} reviews as requested")
        else:
            # For smaller counts, use the regular reviews function
            print(f"Fetching up to {count} reviews...")
            result, continuation_token = reviews(
                app_id,
                lang=lang,  # Language appropriate for the country
                country=country_code,
                sort=Sort.NEWEST,
                count=count
            )
        
        # Process the reviews
        processed_reviews = []
        for review in result:
            processed_review = {
                'username': review.get('userName', ''),
                'rating': review.get('score', 0),
                'comment': review.get('content', ''),
                'date': review.get('at', ''),
                'developer_response': ''
            }
            
            # Check if there's a developer reply
            if 'replyContent' in review and review['replyContent']:
                processed_review['developer_response'] = review['replyContent']
            
            processed_reviews.append(processed_review)
        
        print(f"Successfully fetched {len(processed_reviews)} reviews")
        return processed_reviews
    
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return []

def save_to_csv(reviews, app_name, output_dir='output'):
    """Save reviews to a CSV file."""
    # Clean app name for filename
    safe_app_name = ''.join(c if c.isalnum() or c == ' ' else '_' for c in app_name)
    safe_app_name = safe_app_name.replace(' ', '_')
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_app_name}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'rating', 'comment', 'date', 'developer_response']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for review in reviews:
                writer.writerow(review)
        
        print(f"Reviews saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return None

def display_country_codes():
    """Display available country codes for reference."""
    print("\nAvailable country codes:")
    print("=" * 50)
    print(f"{'Country':<25} {'Code':<5}")
    print("-" * 50)
    
    # Display country codes in columns
    countries = sorted(COUNTRY_CODES.items())
    for i in range(0, len(countries), 2):
        if i + 1 < len(countries):
            print(f"{countries[i][0]:<25} {countries[i][1]:<5}   {countries[i+1][0]:<25} {countries[i+1][1]:<5}")
        else:
            print(f"{countries[i][0]:<25} {countries[i][1]:<5}")
    
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description='Scrape reviews from Google Play Store')
    parser.add_argument('--app', help='App ID or Google Play Store URL')
    parser.add_argument('--country', help='Country code (e.g., us, gb, ca)')
    parser.add_argument('--count', type=int, default=100, help='Number of reviews to fetch (default: 100, use 0 for all available reviews)')
    parser.add_argument('--output', default='output', help='Output directory for CSV file (default: output)')
    parser.add_argument('--list-countries', action='store_true', help='List available country codes')
    
    args = parser.parse_args()
    
    if args.list_countries:
        display_country_codes()
        return
    
    # Interactive mode if no app ID is provided
    app_id = args.app
    count = args.count
    
    if not app_id:
        app_input = input("Enter Google Play Store app URL or app ID: ")
        app_id = get_app_id_from_url(app_input.strip())
        
        # Interactive mode if no country code is provided
        display_country_codes()
        country_code = input("\nEnter country code (e.g., us, gb, ca): ").strip().lower()
        
        # Ask user how many reviews they want to fetch
        print("\nHow many reviews would you like to fetch?")
        print("1. Default (100 reviews)")
        print("2. Custom number")
        print("3. All available reviews (may take longer)")
        review_choice = input("Enter your choice (1-3): ")
        
        if review_choice == "1":
            count = 100
        elif review_choice == "2":
            try:
                count = int(input("Enter number of reviews to fetch: "))
            except ValueError:
                print("Invalid number. Using default (100 reviews).")
                count = 100
        elif review_choice == "3":
            count = 0  # 0 means fetch all available reviews
            print("Fetching all available reviews. This may take some time...")
        else:
            print("Invalid choice. Using default (100 reviews).")
            count = 100
    else:
        app_id = get_app_id_from_url(app_id)
        
        # Interactive mode if no country code is provided
        country_code = args.country
        if not country_code:
            display_country_codes()
            country_code = input("\nEnter country code (e.g., us, gb, ca): ").strip().lower()
    
    print(f"Fetching details for app ID: {app_id} from country: {country_code}")
    
    # Get app details
    details = get_app_details(app_id, country_code)
    
    if details:
        app_name = details.get('title', app_id)
        print(f"App name: {app_name}")
        print(f"Developer: {details.get('developer', 'Unknown')}")
        print(f"Rating: {details.get('score', 'N/A')} ({details.get('ratings', 0)} ratings)")
        
        # Fetch reviews
        reviews_data = fetch_reviews(app_id, country_code, count)
        
        if reviews_data:
            # Save to CSV
            save_to_csv(reviews_data, app_name, args.output)
        else:
            print("No reviews found or error occurred.")
    else:
        print(f"Could not fetch app details for {app_id}. Using app ID as name.")
        # Try to fetch reviews anyway
        reviews_data = fetch_reviews(app_id, country_code, count)
        
        if reviews_data:
            # Save to CSV
            save_to_csv(reviews_data, app_id, args.output)
        else:
            print("No reviews found or error occurred.")

if __name__ == "__main__":
    main()
