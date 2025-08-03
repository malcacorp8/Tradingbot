"""
Real-time News Analysis and Sentiment Processing
Integrates with NewsAPI and Polygon for comprehensive market sentiment
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
from polygon import RESTClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """
    Real-time news analysis with sentiment scoring
    Integrates NewsAPI and Polygon for comprehensive market intelligence
    """
    
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        
        # Initialize sentiment analysis model
        try:
            # Try to load FinBERT with compatibility fixes
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            
            # Use CPU for compatibility
            self.sentiment_pipeline = pipeline("sentiment-analysis", 
                                              model=self.sentiment_model, 
                                              tokenizer=self.sentiment_tokenizer,
                                              device=-1)  # Force CPU
            logger.info("✅ FinBERT sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load FinBERT model: {e}")
            self.sentiment_pipeline = None
        
        # Initialize Polygon client
        if self.polygon_api_key:
            self.polygon_client = RESTClient(self.polygon_api_key)
        else:
            self.polygon_client = None
            logger.warning("⚠️ Polygon API key not configured")
    
    def get_news_sentiment(self, symbol: str, hours_back: int = 24) -> Dict:
        """
        Get comprehensive news sentiment for a symbol
        Returns sentiment score, news count, and key headlines
        """
        try:
            # Fetch news from NewsAPI
            news_data = self._fetch_news_api(symbol, hours_back)
            
            # Fetch news from Polygon (if available)
            polygon_news = self._fetch_polygon_news(symbol, hours_back)
            
            # Combine and analyze
            all_news = news_data + polygon_news
            
            if not all_news:
                return {
                    'sentiment_score': 0.5,
                    'news_count': 0,
                    'headlines': [],
                    'confidence': 0.0
                }
            
            # Analyze sentiment for each headline
            sentiments = []
            headlines = []
            
            for news_item in all_news[:10]:  # Limit to 10 most recent
                headline = news_item.get('title', '')
                if headline:
                    sentiment = self._analyze_sentiment(headline)
                    sentiments.append(sentiment['score'])
                    headlines.append({
                        'title': headline,
                        'sentiment': sentiment['score'],
                        'source': news_item.get('source', 'Unknown'),
                        'published': news_item.get('publishedAt', '')
                    })
            
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                confidence = len(sentiments) / 10.0  # More news = higher confidence
            else:
                avg_sentiment = 0.5
                confidence = 0.0
            
            return {
                'sentiment_score': avg_sentiment,
                'news_count': len(all_news),
                'headlines': headlines[:5],  # Top 5 headlines
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting news sentiment for {symbol}: {e}")
            return {
                'sentiment_score': 0.5,
                'news_count': 0,
                'headlines': [],
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _fetch_news_api(self, symbol: str, hours_back: int) -> List[Dict]:
        """Fetch news from NewsAPI"""
        if not self.news_api_key:
            return []
        
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Search for company news
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'"{symbol}" OR "{self._get_company_name(symbol)}"',
                'from': start_time.strftime('%Y-%m-%d'),
                'to': end_time.strftime('%Y-%m-%d'),
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('articles', [])
            
        except Exception as e:
            logger.error(f"Error fetching NewsAPI data: {e}")
            return []
    
    def _fetch_polygon_news(self, symbol: str, hours_back: int) -> List[Dict]:
        """Fetch news from Polygon API"""
        if not self.polygon_client:
            return []
        
        try:
            # Get news from Polygon
            news = self.polygon_client.get_news(symbol, limit=20)
            
            return [
                {
                    'title': article.title,
                    'source': article.publisher.name,
                    'publishedAt': article.published_utc,
                    'url': article.article_url
                }
                for article in news
            ]
            
        except Exception as e:
            logger.error(f"Error fetching Polygon news: {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text using FinBERT"""
        if not self.sentiment_pipeline:
            return {'score': 0.5, 'label': 'neutral'}
        
        try:
            result = self.sentiment_pipeline(text)[0]
            
            # Convert to numerical score
            if result['label'] == 'positive':
                score = min(result['score'], 1.0)
            elif result['label'] == 'negative':
                score = max(1 - result['score'], 0.0)
            else:
                score = 0.5
            
            return {
                'score': score,
                'label': result['label'],
                'confidence': result['score']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'score': 0.5, 'label': 'neutral'}
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol"""
        company_names = {
            'AAPL': 'Apple Inc',
            'TSLA': 'Tesla Inc',
            'GOOGL': 'Alphabet Inc',
            'MSFT': 'Microsoft Corporation',
            'NVDA': 'NVIDIA Corporation',
            'AMZN': 'Amazon.com Inc',
            'META': 'Meta Platforms Inc',
            'NFLX': 'Netflix Inc',
            'AMD': 'Advanced Micro Devices Inc',
            'INTC': 'Intel Corporation'
        }
        return company_names.get(symbol, symbol)
    
    def get_market_sentiment_summary(self, symbols: List[str]) -> Dict:
        """Get overall market sentiment across multiple symbols"""
        sentiments = {}
        total_sentiment = 0
        total_confidence = 0
        
        for symbol in symbols:
            sentiment_data = self.get_news_sentiment(symbol)
            sentiments[symbol] = sentiment_data
            total_sentiment += sentiment_data['sentiment_score'] * sentiment_data['confidence']
            total_confidence += sentiment_data['confidence']
        
        if total_confidence > 0:
            market_sentiment = total_sentiment / total_confidence
        else:
            market_sentiment = 0.5
        
        return {
            'market_sentiment': market_sentiment,
            'symbol_sentiments': sentiments,
            'timestamp': datetime.now().isoformat()
        } 