import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import json
from pathlib import Path

load_dotenv()

class NewsCrawler:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        # Use "top-headlines" instead of "everything" for faster response and more relevant news
        self.base_url = 'https://newsapi.org/v2/top-headlines'
        
        # List of sources for top headlines - we'll use country instead
        self.countries = ['us']
        
        # Load feedback data if available
        # Use absolute path to ensure file is created in the correct location
        self.feedback_file = Path(os.path.dirname(os.path.abspath(__file__))) / "feedback_data.json"
        print(f"DEBUG - Feedback data file path: {self.feedback_file}")
        self.load_feedback_data()
    
    def load_feedback_data(self):
        """Load previously saved feedback data"""
        self.blocklist = set()  # URLs that users marked as irrelevant
        self.relevant_sources = {}  # Sources that users found relevant, with counts
        
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    data = json.load(f)
                    self.blocklist = set(data.get('blocklist', []))
                    self.relevant_sources = data.get('relevant_sources', {})
                print(f"DEBUG - Loaded feedback data: {len(self.blocklist)} blocked URLs, {len(self.relevant_sources)} relevant sources")
            except Exception as e:
                print(f"ERROR - Failed to load feedback data: {str(e)}")
    
    def save_feedback(self, article_id, is_relevant, keywords):
        """Save user feedback for future searches"""
        try:
            data = {}
            
            if self.feedback_file.exists():
                with open(self.feedback_file, 'r') as f:
                    data = json.load(f)
            
            # Initialize data structure if needed
            if 'blocklist' not in data:
                data['blocklist'] = []
            if 'relevant_sources' not in data:
                data['relevant_sources'] = {}
            
            # Extract domain from URL
            domain = article_id.split('//')[1].split('/')[0] if '//' in article_id else None
            
            if is_relevant and domain:
                # Increment count for this source
                data['relevant_sources'][domain] = data['relevant_sources'].get(domain, 0) + 1
                print(f"DEBUG - Marked {domain} as relevant source")
            elif not is_relevant:
                # Add to blocklist
                if article_id not in data['blocklist']:
                    data['blocklist'].append(article_id)
                    print(f"DEBUG - Added {article_id} to blocklist")
            
            # Save the updated data
            with open(self.feedback_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Update in-memory data
            self.blocklist = set(data['blocklist'])
            self.relevant_sources = data['relevant_sources']
            
            return True
        except Exception as e:
            print(f"ERROR - Failed to save feedback: {str(e)}")
            return False

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
                'pageSize': max_results * 2,  # Get more results to account for filtering
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
                    'pageSize': max_results * 2  # Get more results to account for filtering
                }
                
                response = requests.get(everything_url, params=params)
                response.raise_for_status()
                data = response.json()
                print(f"DEBUG - 'everything' API response status: {data.get('status')}")
                print(f"DEBUG - 'everything' total results: {data.get('totalResults', 0)}")
            
            if data.get('status') != 'ok' or not data.get('articles'):
                print("DEBUG - No articles found in the response")
                return []
            
            # Format and filter the results
            results = []
            for article in data.get('articles', []):
                url = article.get('url', '')
                
                # Skip articles that are in the blocklist
                if url in self.blocklist:
                    print(f"DEBUG - Skipping blocked article: {url}")
                    continue
                
                # Extract domain to check if it's a relevant source
                domain = url.split('//')[1].split('/')[0] if '//' in url else None
                
                article_data = {
                    'title': article.get('title', 'No title'),
                    'url': url,
                    'source': article.get('source', {}).get('name', 'Unknown source'),
                    'publishedAt': article.get('publishedAt', datetime.now().isoformat()),
                    'description': article.get('description', 'No description available')
                }
                
                # Prioritize articles from sources users have marked as relevant
                if domain and domain in self.relevant_sources:
                    # Add to the beginning of the list
                    results.insert(0, article_data)
                    print(f"DEBUG - Prioritizing article from relevant source: {domain}")
                else:
                    # Add to the end of the list
                    results.append(article_data)
            
            # Limit to the requested number of results
            results = results[:max_results]
            
            end_time = time.time()
            print(f"DEBUG - Found {len(results)} articles in {end_time - start_time:.2f} seconds")
            
            return results

        except Exception as e:
            print(f"ERROR searching news: {str(e)}")
            return [] 