import React, { useState } from 'react';
import './App.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [email, setEmail] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    
    try {
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
      setKeywords(data.keywords);
      if (data.keywords.length === 0) {
        setMessage('No relevant keywords found. Try a different search term.');
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
    
    if (!email) {
      setError('Please enter your email address');
      setLoading(false);
      return;
    }
    
    try {
      const formData = new FormData();
      formData.append('email', email);
      formData.append('topic', searchQuery);
      
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Subscription failed');
      }
      
      const data = await response.json();
      setMessage(data.message);
      setEmail('');
    } catch (err) {
      setError('Failed to subscribe. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
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
        
        {keywords.length > 0 && (
          <div className="keywords-container">
            <h2>Keywords from your search:</h2>
            <ul className="keywords-list">
              {keywords.map((keyword, index) => (
                <li key={index} className="keyword-item">{keyword}</li>
              ))}
            </ul>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
