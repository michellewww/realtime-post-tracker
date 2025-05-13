import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [email, setEmail] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [articles, setArticles] = useState([]);
  const [fetchingArticles, setFetchingArticles] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    setArticles([]); // Clear previous articles
    
    if (!searchQuery.trim()) {
      setError('Please enter a search term');
      setLoading(false);
      return;
    }
    
    try {
      console.log("Searching for:", searchQuery);
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      console.log("Received keywords:", data.keywords);
      
      // If no keywords were extracted, use the original search query as a keyword
      if (!data.keywords || data.keywords.length === 0) {
        console.log("No keywords extracted, using search query as keyword");
        setKeywords([searchQuery.trim()]);
      } else {
        setKeywords(data.keywords);
      }
      
    } catch (err) {
      setError('Failed to search. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    if (!email || !searchQuery) {
      setError('Please enter both email and a topic');
      setLoading(false);
      return;
    }

    try {
      console.log('Subscribing with:', { email, topic: searchQuery });

      const formData = new FormData();
      formData.append('email', email);
      formData.append('topic', searchQuery);

      const response = await fetch('/api/subscribe', {
        method: 'POST',
        body: formData,
      });

      console.log('Status:', response.status);

      if (!response.ok) {
        const rawText = await response.text();
        console.error('Raw backend response:', rawText);
        throw new Error('Subscription failed');
      }

      const data = await response.json();
      setMessage(`${data.message} - A confirmation email has been sent to your inbox.`);
      setEmail('');
    } catch (err) {
      setError('Failed to subscribe. Please try again.');
      console.error('[Subscribe error]', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (keywords.length > 0) {
      fetchNews();
    }
  }, [keywords]);

  const fetchNews = async () => {
    try {
      setFetchingArticles(true);
      console.log("Fetching news for keywords:", keywords);
      
      const response = await fetch('/api/news', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keywords }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch news');
      }

      const data = await response.json();
      console.log("News API response:", data);
      console.log("Number of articles received:", data.articles ? data.articles.length : 0);
      
      if (data.articles && data.articles.length > 0) {
        setArticles(data.articles);
        console.log("Articles state updated");
      } else {
        console.log("No articles found or empty articles array");
        setArticles([]);
      }
    } catch (err) {
      console.error('Error fetching news:', err);
      setArticles([]);
    } finally {
      setFetchingArticles(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Get Immediate Updates With Things You Follow</h1>
        <div className="email-input-container">
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="email-input"
          />
        </div>
        <div className="search-container">
          <input
            type="text"
            placeholder="What topics do you care about most?"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <div className="button-container">
            <button onClick={handleSearch} disabled={loading} className="search-button">
              {loading ? 'Searching...' : 'Search'}
            </button>
            <button onClick={handleSubscribe} disabled={loading} className="subscribe-button">
              {loading ? 'Processing...' : 'Subscribe'}
            </button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}
        {message && <div className="success-message">{message}</div>}


        {fetchingArticles ? (
          <div className="loading-container">
            <h2>Searching for news articles...</h2>
            <div className="loading-spinner"></div>
          </div>
        ) : (
          articles && articles.length > 0 ? (
            <div className="news-container">
              <h2>Recent News Articles</h2>
              <div className="news-list">
                {articles.map((article, index) => (
                  <div key={index} className="news-card">
                    <div className="news-source">{article.source}</div>
                    <a 
                      href={article.url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="news-title"
                    >
                      {article.title}
                    </a>
                    <p className="news-description">{article.description}</p>
                    <span className="news-time">
                      {new Date(article.publishedAt).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            keywords.length > 0 && !loading && (
              <div className="news-container">
                <h2>No recent news found for these keywords</h2>
                <p>Try different keywords or check back later.</p>
              </div>
            )
          )
        )}
      </header>
    </div>
  );
}

export default App;
