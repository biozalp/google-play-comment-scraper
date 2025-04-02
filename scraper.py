#!/usr/bin/env python3
import csv
import sys
import time
import datetime
import argparse
import os
from google_play_scraper import app as app_details
from google_play_scraper import Sort, reviews_all, reviews

# Country codes mapping for user reference
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

def get_app_details(app_id, country_code):
    """Get app details using google-play-scraper."""
    try:
        result = app_details(
            app_id,
            lang='en',  # Language for the app details
            country=country_code  # Country for the app details
        )
        return result
    except Exception as e:
        print(f"Error getting app details: {e}")
        return None

def fetch_reviews(app_id, country_code, count=100):
    """Fetch reviews for the given app ID from Google Play Store."""
    print(f"Fetching up to {count} reviews for {app_id} from country: {country_code}")
    
    try:
        # If count is large, use reviews_all (might take longer)
        if count > 100:
            print("This might take a while for a large number of reviews...")
            result, continuation_token = reviews(
                app_id,
                lang='en',  # Language for the reviews
                country=country_code,  # Country for the reviews
                sort=Sort.NEWEST,  # Sort by newest reviews first
                count=count  # Number of reviews to fetch
            )
        else:
            # For smaller counts, use the regular reviews function
            result, continuation_token = reviews(
                app_id,
                lang='en',
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

def save_to_csv(reviews, app_name, output_dir='.'):
    """Save reviews to a CSV file."""
    # Clean app name for filename
    safe_app_name = ''.join(c if c.isalnum() or c == ' ' else '_' for c in app_name)
    safe_app_name = safe_app_name.replace(' ', '_')
    
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
    parser.add_argument('--count', type=int, default=100, help='Number of reviews to fetch (default: 100)')
    parser.add_argument('--output', default='.', help='Output directory for CSV file')
    parser.add_argument('--list-countries', action='store_true', help='List available country codes')
    
    args = parser.parse_args()
    
    if args.list_countries:
        display_country_codes()
        return
    
    # Interactive mode if no app ID is provided
    app_id = args.app
    if not app_id:
        app_input = input("Enter Google Play Store app URL or app ID: ")
        app_id = get_app_id_from_url(app_input.strip())
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
        reviews_data = fetch_reviews(app_id, country_code, args.count)
        
        if reviews_data:
            # Save to CSV
            save_to_csv(reviews_data, app_name, args.output)
        else:
            print("No reviews found or error occurred.")
    else:
        print(f"Could not fetch app details for {app_id}. Using app ID as name.")
        # Try to fetch reviews anyway
        reviews_data = fetch_reviews(app_id, country_code, args.count)
        
        if reviews_data:
            # Save to CSV
            save_to_csv(reviews_data, app_id, args.output)
        else:
            print("No reviews found or error occurred.")

if __name__ == "__main__":
    main()
