/* eslint-disable @typescript-eslint/no-explicit-any */
// Social feed component with dynamic API responses
import { useState, useEffect, useCallback } from 'react';
import './SocialFeed.css';

// 🔍 TEMP DEBUG: Check if API URL is properly configured (development only)
if (import.meta.env.DEV) {
  console.log("API URL:", import.meta.env.VITE_API_URL);
}

// ✅ Correct API URL pattern: Use environment variable or same-origin
const API = import.meta.env.VITE_API_URL || window.location.origin;

// Enhanced API service with AI features
const socialAPI = {
  baseURL: API,
  
  async request(endpoint: string, options: any = {}) {
    const token = localStorage.getItem('auth_token');
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  },

  // User authentication
  async login(email: string, password: string) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  // Posts API
  async getPosts() {
    return this.request('/posts');
  },

  async createPost(content: string, imageUrl: string = '', postType: string = 'text') {
    return this.request('/posts', {
      method: 'POST',
      body: JSON.stringify({
        content,
        image_url: imageUrl,
        post_type: postType,
      }),
    });
  },

  async likePost(postId: string | number) {
    return this.request(`/posts/${postId}/like`, {
      method: 'POST',
    });
  },

  // AI Analytics
  async getUserAnalytics() {
    return this.request('/user/analytics');
  },
};

// Post Component
const Post = ({ post, onLike }: { post: any, onLike: any }) => {
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(post.likes_count);

  const handleLike = async () => {
    try {
      const result = await onLike(post.id);
      setIsLiked(result.action === 'like');
      setLikesCount((prev: number) => result.action === 'like' ? prev + 1 : prev - 1);
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const formatTime = (timestamp: string | number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((Number(now) - Number(date)) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h`;
    return `${Math.floor(diffInMinutes / 1440)}d`;
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <div className="user-info">
          <div className="avatar">
            {post.author.avatar_url ? (
              <img src={post.author.avatar_url} alt={post.author.full_name} />
            ) : (
              <div className="avatar-placeholder">
                {post.author.full_name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div className="user-details">
            <h4 className="user-name">{post.author.full_name}</h4>
            <span className="username">@{post.author.username}</span>
            <span className="post-time">{formatTime(post.created_at)}</span>
          </div>
        </div>
        <div className="post-menu">
          <button className="menu-btn">⋯</button>
        </div>
      </div>

      <div className="post-content">
        <p>{post.content}</p>
        {post.image_url && (
          <div className="post-image">
            <img src={post.image_url} alt="Post content" />
          </div>
        )}
      </div>

      <div className="post-stats">
        <span className="likes-count">{likesCount} likes</span>
        <span className="comments-count">{post.comments_count} comments</span>
        <span className="shares-count">{post.shares_count} shares</span>
      </div>

      <div className="post-actions">
        <button 
          className={`action-btn like-btn ${isLiked ? 'liked' : ''}`}
          onClick={handleLike}
        >
          <span className="icon">👍</span>
          <span>Like</span>
        </button>
        <button className="action-btn comment-btn">
          <span className="icon">💬</span>
          <span>Comment</span>
        </button>
        <button className="action-btn share-btn">
          <span className="icon">🔄</span>
          <span>Share</span>
        </button>
      </div>
    </div>
  );
};

// Create Post Component
const CreatePost = ({ onPostCreated, currentUser }: { onPostCreated: any, currentUser: any }) => {
  const [content, setContent] = useState('');
  const [isPosting, setIsPosting] = useState(false);
  const [showImageUpload, setShowImageUpload] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsPosting(true);
    try {
      await socialAPI.createPost(content);
      setContent('');
      onPostCreated();
    } catch (error) {
      console.error('Error creating post:', error);
      alert('Failed to create post. Please try again.');
    } finally {
      setIsPosting(false);
    }
  };

  return (
    <div className="create-post-card">
      <div className="create-post-header">
        <div className="avatar">
          {currentUser?.avatar_url ? (
            <img src={currentUser.avatar_url} alt={currentUser.full_name} />
          ) : (
            <div className="avatar-placeholder">
              {currentUser?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
          )}
        </div>
        <form onSubmit={handleSubmit} className="post-form">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What's on your mind?"
            className="post-input"
            rows={3}
          />
          <div className="post-actions">
            <div className="post-options">
              <button 
                type="button" 
                className="option-btn"
                onClick={() => setShowImageUpload(!showImageUpload)}
              >
                📷 Photo
              </button>
              <button type="button" className="option-btn">
                🎥 Video
              </button>
              <button type="button" className="option-btn">
                😊 Feeling
              </button>
              <button type="button" className="option-btn">
                📍 Location
              </button>
            </div>
            <button 
              type="submit" 
              className="post-btn"
              disabled={!content.trim() || isPosting}
            >
              {isPosting ? 'Posting...' : 'Post'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// AI Recommendations Component
const AIRecommendations = ({ recommendations, userPatterns }: { recommendations: any[], userPatterns: any }) => {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <div className="ai-recommendations">
      <div className="recommendations-header">
        <h3>🤖 AI Recommendations</h3>
        <span className="ai-badge">Powered by AI</span>
      </div>
      
      {userPatterns && (
        <div className="user-insights">
          <h4>Your Activity Insights</h4>
          <div className="insights-grid">
            <div className="insight-item">
              <span className="insight-label">User Type</span>
              <span className="insight-value">{userPatterns.user_type || 'New User'}</span>
            </div>
            <div className="insight-item">
              <span className="insight-label">Engagement Score</span>
              <span className="insight-value">{userPatterns.engagement_score || 0}/100</span>
            </div>
            <div className="insight-item">
              <span className="insight-label">Activity Trend</span>
              <span className="insight-value">{userPatterns.activity_trend || 'Stable'}</span>
            </div>
          </div>
        </div>
      )}

      <div className="recommendations-list">
        {recommendations.map((rec: any, index: number) => (
          <div key={index} className="recommendation-item">
            <div className="rec-icon">
              {rec.type === 'trending' && '🔥'}
              {rec.type === 'creator_tool' && '🛠️'}
              {rec.type === 'discussion' && '💬'}
              {rec.type === 'social' && '👥'}
              {rec.type === 'event' && '📅'}
            </div>
            <div className="rec-content">
              <h4>{rec.title}</h4>
              <p>{rec.description}</p>
              {rec.engagement_score && (
                <span className="engagement-score">
                  🔥 {rec.engagement_score}% engagement
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main Social Feed Component
const SocialFeed = () => {
  const [posts, setPosts] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState([]);
  const [userPatterns, setUserPatterns] = useState(null);
  
  // Use lazy initialization to avoid cascading renders
  const [currentUser, setCurrentUser] = useState<any>(() => {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  });
  
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return !!localStorage.getItem('auth_token');
  });

  // Login state
  const [loginForm, setLoginForm] = useState({
    email: 'admin@hiremebahamas.com',
    password: 'AdminPass123!'
  });

  const loadPosts = useCallback(async () => {
    try {
      const data = await socialAPI.getPosts();
      setPosts(data.posts || []);
      setRecommendations(data.recommendations || []);
      if (data.ai_insights) {
        setUserPatterns(data.ai_insights);
      }
    } catch (error) {
      console.error('Error loading posts:', error);
    }
  }, []);

  const loadAnalytics = useCallback(async () => {
    if (!isLoggedIn) return;
    
    try {
      const analytics = await socialAPI.getUserAnalytics();
      setUserPatterns(analytics.user_patterns);
      setRecommendations(analytics.recommendations);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  }, [isLoggedIn]);

  // Load posts and analytics on mount and when login state changes
  useEffect(() => {
    // These are intentional data fetching operations on mount/login
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadPosts();
    if (isLoggedIn) {
      loadAnalytics();
    }
  }, [loadPosts, loadAnalytics, isLoggedIn]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await socialAPI.login(loginForm.email, loginForm.password);
      localStorage.setItem('auth_token', result.token);
      localStorage.setItem('user_data', JSON.stringify(result.user));
      setCurrentUser(result.user);
      setIsLoggedIn(true);
      await loadPosts();
      await loadAnalytics();
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please check your credentials.');
    }
  };

  const handleLike = async (postId: string | number) => {
    return await socialAPI.likePost(postId);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    setCurrentUser(null);
    setIsLoggedIn(false);
    setUserPatterns(null);
    setRecommendations([]);
  };

  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h1>🚀 HireMeBahamas</h1>
            <p>AI-Powered Social Platform</p>
          </div>
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <input
                type="email"
                placeholder="Email"
                value={loginForm.email}
                onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                placeholder="Password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                required
              />
            </div>
            <button type="submit" className="login-btn">
              Sign In
            </button>
          </form>
          <div className="demo-info">
            <p>Demo Account:</p>
            <p><strong>Email:</strong> admin@hiremebahamas.com</p>
            <p><strong>Password:</strong> AdminPass123!</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="social-feed">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <h1>🚀 HireMeBahamas</h1>
            <span className="ai-badge">AI-Powered</span>
          </div>
          <div className="user-menu">
            <span>Welcome, {currentUser?.full_name}</span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="main-content">
        <div className="feed-container">
          <div className="left-sidebar">
            <div className="user-profile-card">
              <div className="avatar">
                {currentUser?.avatar_url ? (
                  <img src={currentUser.avatar_url} alt={currentUser.full_name} />
                ) : (
                  <div className="avatar-placeholder">
                    {currentUser?.full_name?.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              <h3>{currentUser?.full_name}</h3>
              <p>@{currentUser?.username}</p>
            </div>

            <AIRecommendations 
              recommendations={recommendations} 
              userPatterns={userPatterns}
            />
          </div>

          <div className="main-feed">
            <CreatePost 
              onPostCreated={loadPosts} 
              currentUser={currentUser}
            />
            
            <div className="posts-list">
              {posts.length === 0 ? (
                <div className="empty-feed">
                  <h3>No posts yet!</h3>
                  <p>Be the first to share something amazing.</p>
                </div>
              ) : (
                posts.map((post) => (
                  <Post
                    key={post.id}
                    post={post}
                    onLike={handleLike}
                  />
                ))
              )}
            </div>
          </div>

          <div className="right-sidebar">
            <div className="trending-topics">
              <h3>🔥 Trending</h3>
              <div className="trending-list">
                <div className="trending-item">#AIJobs</div>
                <div className="trending-item">#RemoteWork</div>
                <div className="trending-item">#TechCareers</div>
                <div className="trending-item">#Networking</div>
              </div>
            </div>

            <div className="suggested-connections">
              <h3>👥 People to Follow</h3>
              <div className="suggestions-list">
                <div className="suggestion-item">
                  <div className="avatar-small">JS</div>
                  <div className="suggestion-info">
                    <span className="name">John Smith</span>
                    <span className="title">Software Engineer</span>
                  </div>
                  <button className="follow-btn">Follow</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocialFeed;