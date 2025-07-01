from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv
import tweepy
from bs4 import BeautifulSoup
import json
import time

# Load .env variables
load_dotenv()

app = Flask(__name__)

# Twitter API credentials from environment variables
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def get_trending_hashtags_tweepy():
    """Get trending hashtags using Tweepy library"""
    try:
        # Initialize Tweepy client with Bearer token (v2 API)
        client = tweepy.Client(bearer_token=BEARER_TOKEN)
        
        # Get trending topics for worldwide (WOEID: 1)
        # Note: Twitter API v2 doesn't have direct trends endpoint like v1.1
        # We'll use search to find popular hashtags instead
        
        # Search for popular tweets with hashtags
        query = "#trending OR #viral OR #popular -is:retweet"
        tweets = client.search_recent_tweets(
            query=query,
            max_results=100,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        hashtags = []
        if tweets.data:
            for tweet in tweets.data:
                # Extract hashtags from tweet text
                words = tweet.text.split()
                for word in words:
                    if word.startswith('#') and len(word) > 1:
                        hashtag = word.lower()
                        # Check if hashtag already exists
                        existing = next((h for h in hashtags if h['name'] == hashtag), None)
                        if existing:
                            existing['tweet_volume'] = existing.get('tweet_volume', 0) + 1
                        else:
                            hashtags.append({
                                'name': hashtag,
                                'tweet_volume': 1,
                                'url': f"https://twitter.com/search?q={hashtag}"
                            })
        
        # Sort by tweet volume and return top 20
        hashtags.sort(key=lambda x: x.get('tweet_volume', 0), reverse=True)
        return hashtags[:20]
        
    except Exception as e:
        print(f"Tweepy API Error: {e}")
        return []

def get_trending_hashtags_scraping():
    """Fallback method: Scrape trending hashtags from Twitter web"""
    try:
        # Use a more reliable approach - scrape from Twitter's trending page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Try to get trending topics from Twitter's web interface
        url = "https://twitter.com/explore/tabs/trending"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            hashtags = []
            
            # Look for trending hashtags in the page
            # This is a simplified approach - Twitter's structure may change
            trend_elements = soup.find_all(['div', 'span'], class_=lambda x: x and 'trend' in x.lower())
            
            for element in trend_elements[:20]:
                text = element.get_text().strip()
                if text.startswith('#') and len(text) > 1:
                    hashtags.append({
                        'name': text.lower(),
                        'tweet_volume': 'Unknown',
                        'url': f"https://twitter.com/search?q={text}"
                    })
            
            return hashtags
        else:
            print(f"Scraping failed with status code: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Scraping Error: {e}")
        return []

def get_trending_hashtags_mock():
    """Mock data for testing when APIs are not available"""
    return [
        {'name': '#trending', 'tweet_volume': 15000, 'url': 'https://twitter.com/search?q=%23trending'},
        {'name': '#viral', 'tweet_volume': 12000, 'url': 'https://twitter.com/search?q=%23viral'},
        {'name': '#news', 'tweet_volume': 10000, 'url': 'https://twitter.com/search?q=%23news'},
        {'name': '#technology', 'tweet_volume': 8000, 'url': 'https://twitter.com/search?q=%23technology'},
        {'name': '#sports', 'tweet_volume': 7500, 'url': 'https://twitter.com/search?q=%23sports'},
        {'name': '#entertainment', 'tweet_volume': 7000, 'url': 'https://twitter.com/search?q=%23entertainment'},
        {'name': '#politics', 'tweet_volume': 6500, 'url': 'https://twitter.com/search?q=%23politics'},
        {'name': '#business', 'tweet_volume': 6000, 'url': 'https://twitter.com/search?q=%23business'},
        {'name': '#health', 'tweet_volume': 5500, 'url': 'https://twitter.com/search?q=%23health'},
        {'name': '#education', 'tweet_volume': 5000, 'url': 'https://twitter.com/search?q=%23education'}
    ]

def get_trending_hashtags():
    """Main function to get trending hashtags with multiple fallback methods"""
    
    # Try Tweepy first (if credentials are available)
    if BEARER_TOKEN:
        hashtags = get_trending_hashtags_tweepy()
        if hashtags:
            return hashtags
    
    # Try web scraping as fallback
    hashtags = get_trending_hashtags_scraping()
    if hashtags:
        return hashtags
    
    # Return mock data if all else fails
    print("Using mock data - no API access available")
    return get_trending_hashtags_mock()

@app.route('/')
def index():
    hashtags = get_trending_hashtags()
    return render_template("index.html", hashtags=hashtags)

@app.route('/api/trends')
def api_trends():
    """API endpoint to get trending hashtags as JSON"""
    hashtags = get_trending_hashtags()
    return {'hashtags': hashtags, 'count': len(hashtags)}

def get_instagram_trending_hashtags_scraping():
    """Scrape popular Instagram hashtags from a public aggregator site as Instagram itself is hard to scrape directly."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Use a public aggregator site for trending Instagram hashtags
        url = "https://www.all-hashtag.com/library/contents/ajax/popular-hashtags.php?type=top&lang=english"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            hashtags = []
            # The hashtags are in <div class="tag-box tag-box-v3 margin-bottom-40">, each hashtag in <a>
            tag_box = soup.find('div', class_='tag-box')
            if tag_box:
                for a in tag_box.find_all('a'):
                    text = a.get_text().strip()
                    if text.startswith('#') and len(text) > 1:
                        hashtags.append({
                            'name': text.lower(),
                            'url': f"https://www.instagram.com/explore/tags/{text[1:]}/"
                        })
            return hashtags[:20]
        else:
            print(f"Instagram scraping failed with status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Instagram Scraping Error: {e}")
        return []

def get_instagram_trending_hashtags_mock():
    """Mock data for Instagram trending hashtags."""
    return [
        {'name': '#love', 'url': 'https://www.instagram.com/explore/tags/love/'},
        {'name': '#instagood', 'url': 'https://www.instagram.com/explore/tags/instagood/'},
        {'name': '#fashion', 'url': 'https://www.instagram.com/explore/tags/fashion/'},
        {'name': '#photooftheday', 'url': 'https://www.instagram.com/explore/tags/photooftheday/'},
        {'name': '#beautiful', 'url': 'https://www.instagram.com/explore/tags/beautiful/'},
        {'name': '#art', 'url': 'https://www.instagram.com/explore/tags/art/'},
        {'name': '#photography', 'url': 'https://www.instagram.com/explore/tags/photography/'},
        {'name': '#happy', 'url': 'https://www.instagram.com/explore/tags/happy/'},
        {'name': '#picoftheday', 'url': 'https://www.instagram.com/explore/tags/picoftheday/'},
        {'name': '#cute', 'url': 'https://www.instagram.com/explore/tags/cute/'},
    ]

def get_instagram_trending_hashtags():
    """Main function to get Instagram trending hashtags with fallback."""
    hashtags = get_instagram_trending_hashtags_scraping()
    if hashtags:
        return hashtags
    print("Using Instagram mock data - scraping failed or blocked")
    return get_instagram_trending_hashtags_mock()

@app.route('/instagram')
def instagram():
    hashtags = get_instagram_trending_hashtags()
    return render_template("index.html", hashtags=hashtags, platform='Instagram')

@app.route('/api/instagram_trends')
def api_instagram_trends():
    hashtags = get_instagram_trending_hashtags()
    return {'hashtags': hashtags, 'count': len(hashtags)}

def get_tiktok_trending_hashtags_scraping():
    """Scrape trending TikTok hashtags from a public aggregator site."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Use a public aggregator site for trending TikTok hashtags
        url = "https://www.all-hashtag.com/library/contents/ajax/popular-hashtags.php?type=top-tiktok&lang=english"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            hashtags = []
            tag_box = soup.find('div', class_='tag-box')
            if tag_box:
                for a in tag_box.find_all('a'):
                    text = a.get_text().strip()
                    if text.startswith('#') and len(text) > 1:
                        hashtags.append({
                            'name': text.lower(),
                            'url': f"https://www.tiktok.com/tag/{text[1:]}"
                        })
            return hashtags[:20]
        else:
            print(f"TikTok scraping failed with status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"TikTok Scraping Error: {e}")
        return []

def get_tiktok_trending_hashtags_mock():
    """Mock data for TikTok trending hashtags."""
    return [
        {'name': '#foryou', 'url': 'https://www.tiktok.com/tag/foryou'},
        {'name': '#foryoupage', 'url': 'https://www.tiktok.com/tag/foryoupage'},
        {'name': '#viral', 'url': 'https://www.tiktok.com/tag/viral'},
        {'name': '#trending', 'url': 'https://www.tiktok.com/tag/trending'},
        {'name': '#tiktok', 'url': 'https://www.tiktok.com/tag/tiktok'},
        {'name': '#funny', 'url': 'https://www.tiktok.com/tag/funny'},
        {'name': '#duet', 'url': 'https://www.tiktok.com/tag/duet'},
        {'name': '#love', 'url': 'https://www.tiktok.com/tag/love'},
        {'name': '#music', 'url': 'https://www.tiktok.com/tag/music'},
        {'name': '#dance', 'url': 'https://www.tiktok.com/tag/dance'},
    ]

def get_tiktok_trending_hashtags():
    """Main function to get TikTok trending hashtags with fallback."""
    hashtags = get_tiktok_trending_hashtags_scraping()
    if hashtags:
        return hashtags
    print("Using TikTok mock data - scraping failed or blocked")
    return get_tiktok_trending_hashtags_mock()

@app.route('/tiktok')
def tiktok():
    hashtags = get_tiktok_trending_hashtags()
    return render_template("index.html", hashtags=hashtags, platform='TikTok')

@app.route('/api/tiktok_trends')
def api_tiktok_trends():
    hashtags = get_tiktok_trending_hashtags()
    return {'hashtags': hashtags, 'count': len(hashtags)}

# Facebook Ad Library Trending Ads

def get_facebook_ad_library_trending_ads(country='US', ad_type='POLITICAL_AND_ISSUE_ADS'):
    """Fetch trending ads from the Facebook Ad Library API (public endpoint)."""
    try:
        # Facebook Ad Library API endpoint (public, no auth required for basic queries)
        url = f"https://www.facebook.com/ads/library/api"  # This is a placeholder; see below
        # The real API is not fully public, but we can scrape the Ad Library search page for public data
        search_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type={ad_type}&country={country}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            ads = []
            # Facebook Ad Library is heavily JS-based, so scraping is limited
            # We'll look for ad titles and links in the static HTML as a fallback
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/ads/library/?id=' in href:
                    ad_id = href.split('id=')[-1]
                    ad_url = f"https://www.facebook.com{href}" if href.startswith('/') else href
                    ad_title = a.get_text().strip() or f"Ad {ad_id}"
                    ads.append({
                        'name': ad_title,
                        'url': ad_url
                    })
            return ads[:20]
        else:
            print(f"Facebook Ad Library scraping failed with status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Facebook Ad Library Scraping Error: {e}")
        return []

def get_facebook_ad_library_trending_ads_mock():
    """Mock data for Facebook Ad Library trending ads."""
    return [
        {'name': 'Sample Ad 1', 'url': 'https://www.facebook.com/ads/library/?id=123456'},
        {'name': 'Sample Ad 2', 'url': 'https://www.facebook.com/ads/library/?id=654321'},
    ]

def get_facebook_trending_ads():
    ads = get_facebook_ad_library_trending_ads()
    if ads:
        return ads
    print("Using Facebook Ad Library mock data - scraping failed or blocked")
    return get_facebook_ad_library_trending_ads_mock()

# Facebook Public Page/Reel Scraping

def get_facebook_page_trending_posts(page_url="https://www.facebook.com/facebook"):
    """Scrape trending posts from a public Facebook Page (limited, may break)."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(page_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            posts = []
            # Facebook's structure is dynamic; look for post containers
            for div in soup.find_all('div'):
                text = div.get_text().strip()
                if text and len(text) > 50:  # crude filter for post content
                    posts.append({
                        'name': text[:60] + '...' if len(text) > 60 else text,
                        'url': page_url
                    })
                if len(posts) >= 10:
                    break
            return posts
        else:
            print(f"Facebook Page scraping failed with status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Facebook Page Scraping Error: {e}")
        return []

def get_facebook_page_trending_posts_mock():
    """Mock data for Facebook Page trending posts."""
    return [
        {'name': 'Sample Facebook Post 1...', 'url': 'https://www.facebook.com/facebook'},
        {'name': 'Sample Facebook Post 2...', 'url': 'https://www.facebook.com/facebook'},
    ]

def get_facebook_trending_posts():
    posts = get_facebook_page_trending_posts()
    if posts:
        return posts
    print("Using Facebook Page mock data - scraping failed or blocked")
    return get_facebook_page_trending_posts_mock()

@app.route('/facebook')
def facebook():
    ads = get_facebook_trending_ads()
    posts = get_facebook_trending_posts()
    # Combine ads and posts for display
    hashtags = ads + posts
    return render_template("index.html", hashtags=hashtags, platform='Facebook')

@app.route('/api/facebook_trends')
def api_facebook_trends():
    ads = get_facebook_trending_ads()
    posts = get_facebook_trending_posts()
    hashtags = ads + posts
    return {'hashtags': hashtags, 'count': len(hashtags)}

if __name__ == '__main__':
    app.run(debug=True)
