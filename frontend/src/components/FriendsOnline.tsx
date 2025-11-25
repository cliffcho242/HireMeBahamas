import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { VideoCameraIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

interface Friend {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  avatar_url?: string;
  is_available_for_hire: boolean;
}

interface FriendSuggestion {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  avatar_url?: string;
  bio?: string;
  location?: string;
}

const FriendsOnline: React.FC = () => {
  const { user } = useAuth();
  const [friends, setFriends] = useState<Friend[]>([]);
  const [suggestions, setSuggestions] = useState<FriendSuggestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadFriendsData();
    }
  }, [user]);

  const loadFriendsData = async () => {
    try {
      const [friendsRes, suggestionsRes] = await Promise.all([
        api.get('/api/friends/list'),
        api.get('/api/friends/suggestions')
      ]);

      if (friendsRes.data.success) {
        setFriends(friendsRes.data.friends);
      }
      if (suggestionsRes.data.success) {
        setSuggestions(suggestionsRes.data.suggestions.slice(0, 3)); // Limit to 3 suggestions
      }
    } catch (error) {
      console.error('Error loading friends data:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendFriendRequest = async (userId: number) => {
    try {
      await api.post(`/api/friends/send-request/${userId}`);
      // Refresh suggestions
      const response = await api.get('/api/friends/suggestions');
      if (response.data.success) {
        setSuggestions(response.data.suggestions.slice(0, 3));
      }
    } catch (error: unknown) {
      console.error('Error sending friend request:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Contacts</h3>
        <div className="flex items-center space-x-2">
          <button className="p-1 rounded-full hover:bg-gray-100 transition-colors">
            <VideoCameraIcon className="w-5 h-5 text-gray-600" />
          </button>
          <button className="p-1 rounded-full hover:bg-gray-100 transition-colors">
            <MagnifyingGlassIcon className="w-5 h-5 text-gray-600" />
          </button>
          <button className="p-1 rounded-full hover:bg-gray-100 transition-colors">
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
            </svg>
          </button>
        </div>
      </div>

      {/* Online Friends */}
      <div className="space-y-3 mb-6">
        {friends.slice(0, 5).map((friend) => (
          <div key={friend.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors group">
            <div className="relative">
              <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold text-sm">
                  {(friend.first_name[0] + friend.last_name[0]).toUpperCase()}
                </span>
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {friend.first_name} {friend.last_name}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {friend.is_available_for_hire ? 'Available for Hire' : 'Online'}
              </p>
            </div>
            <div className="opacity-0 group-hover:opacity-100 transition-opacity">
              <button className="p-1 rounded-full hover:bg-gray-200 transition-colors">
                <VideoCameraIcon className="w-4 h-4 text-gray-600" />
              </button>
            </div>
          </div>
        ))}
        {friends.length === 0 && (
          <div className="text-center py-4">
            <p className="text-sm text-gray-500">No friends online</p>
          </div>
        )}
      </div>

      {/* Suggested Friends */}
      <div className="border-t border-gray-200 pt-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">People you may know</h4>
        <div className="space-y-3">
          {suggestions.map((suggestion) => (
            <div key={suggestion.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold text-sm">
                  {(suggestion.first_name[0] + suggestion.last_name[0]).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {suggestion.first_name} {suggestion.last_name}
                </p>
                <p className="text-xs text-gray-500 truncate">{suggestion.location || 'No location'}</p>
                {suggestion.bio && (
                  <p className="text-xs text-gray-500 truncate">{suggestion.bio}</p>
                )}
              </div>
              <button
                onClick={() => sendFriendRequest(suggestion.id)}
                className="px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors"
              >
                Add Friend
              </button>
            </div>
          ))}
          {suggestions.length === 0 && (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500">No suggestions available</p>
            </div>
          )}
        </div>
      </div>

      {/* See All Link */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <Link to="/friends" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
          See all contacts
        </Link>
      </div>
    </div>
  );
};

export default FriendsOnline;