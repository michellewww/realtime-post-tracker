import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

class NewsCrawler:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        # Use "top-headlines" instead of "everything" for faster response and more relevant news
        self.base_url = 'https://newsapi.org/v2/top-headlines'
        
        # List of sources for top headlines - we'll use country instead
        self.countries = ['us']

    def search_news(self, keywords, max_results=5):
        try:
            start_time = time.time()
            print(f"DEBUG - Starting news search for: {keywords}")
            
            # For popular topics like "Trump", we can directly use the query
            combined_query = ' OR '.join(keywords)
            
            params = {
                'q': combined_query,
                'language': 'en',
                'country': 'us',  # Focus on US news for faster results
                'pageSize': max_results,
                'apiKey': self.api_key
            }
            
            print(f"DEBUG - Requesting with params: {params}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"DEBUG - API response status: {data.get('status')}")
            print(f"DEBUG - Total results: {data.get('totalResults', 0)}")
            
            # If no results with top-headlines, fall back to "everything" endpoint
            if data.get('status') != 'ok' or data.get('totalResults', 0) == 0:
                print("DEBUG - No results from top-headlines, trying 'everything' endpoint")
                everything_url = 'https://newsapi.org/v2/everything'
                
                # Calculate date for last 24 hours
                from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                
                params = {
                    'q': combined_query,
                    'from': from_date,
                    'language': 'en',
                    'sortBy': 'relevancy',  # Sort by relevancy instead of publishedAt
                    'apiKey': self.api_key,
                    'pageSize': max_results
                }
                
                response = requests.get(everything_url, params=params)
                response.raise_for_status()
                data = response.json()
                print(f"DEBUG - 'everything' API response status: {data.get('status')}")
                print(f"DEBUG - 'everything' total results: {data.get('totalResults', 0)}")
            
            if data.get('status') != 'ok' or not data.get('articles'):
                print("DEBUG - No articles found in the response")
                return []
            
            # Format the results
            results = []
            for article in data.get('articles', []):
                results.append({
                    'title': article.get('title', 'No title'),
                    'url': article.get('url', '#'),
                    'source': article.get('source', {}).get('name', 'Unknown source'),
                    'publishedAt': article.get('publishedAt', datetime.now().isoformat()),
                    'description': article.get('description', 'No description available')
                })
            
            end_time = time.time()
            print(f"DEBUG - Found {len(results)} articles in {end_time - start_time:.2f} seconds")
            
            return results

        except Exception as e:
            print(f"ERROR searching news: {str(e)}")
            return [] 