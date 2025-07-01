# 🌍 Trending Hashtags App

A modern Flask web application that displays trending hashtags from Twitter with multiple data sources and fallback methods.

## ✨ Features

- **Multiple Data Sources**: Uses Twitter API v2 via Tweepy, web scraping, and mock data as fallbacks
- **Modern UI**: Beautiful, responsive design with hover effects and animations
- **Real-time Updates**: Auto-refreshes data every 5 minutes
- **API Endpoint**: JSON API endpoint for programmatic access
- **Error Handling**: Graceful fallbacks when APIs are unavailable

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Twitter API v2 Credentials (Optional - for real Twitter data)
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Legacy Twitter API v1.1 (Optional - for additional features)
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### 3. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## 🔧 How It Works

### Data Sources (in order of preference):

1. **Twitter API v2 (Tweepy)**: Uses Bearer token to search for popular hashtags
2. **Web Scraping**: Falls back to scraping Twitter's trending page
3. **Mock Data**: Provides sample data when APIs are unavailable

### API Endpoints:

- `GET /` - Main web interface
- `GET /api/trends` - JSON API endpoint

## 📱 Twitter API Setup (Optional)

To get real Twitter data, you'll need to:

1. **Create a Twitter Developer Account**:
   - Go to [Twitter Developer Portal](https://developer.twitter.com/)
   - Apply for a developer account
   - Create a new app

2. **Get Your Credentials**:
   - Bearer Token (for API v2)
   - API Key and Secret (for API v1.1)
   - Access Token and Secret (for API v1.1)

3. **Add to .env file**:
   ```env
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

## 🎨 Customization

### Styling
The app uses modern CSS with:
- Gradient backgrounds
- Hover animations
- Responsive design
- Twitter-inspired color scheme

### Data Format
Each hashtag object contains:
```json
{
  "name": "#hashtag",
  "tweet_volume": 15000,
  "url": "https://twitter.com/search?q=%23hashtag"
}
```

## 🔍 Troubleshooting

### Common Issues:

1. **"No API access available"**: 
   - The app will use mock data if no Twitter credentials are provided
   - This is normal and expected behavior

2. **Rate Limiting**:
   - Twitter API has rate limits
   - The app includes fallback methods to handle this

3. **Web Scraping Blocked**:
   - Some networks may block web scraping
   - The app will fall back to mock data

### Debug Mode:
The app runs in debug mode by default. Check the console for detailed error messages.

## 📊 API Response Format

```json
{
  "hashtags": [
    {
      "name": "#trending",
      "tweet_volume": 15000,
      "url": "https://twitter.com/search?q=%23trending"
    }
  ],
  "count": 1
}
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This application is for educational purposes. Please respect Twitter's Terms of Service and API usage guidelines. The web scraping method is provided as a fallback and should be used responsibly. 