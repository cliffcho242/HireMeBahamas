import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { UserGroupIcon, UserPlusIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { UserGroupIcon as UserGroupSolidIcon } from '@heroicons/react/24/solid';

interface Friend {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  avatar_url?: string;
  is_available_for_hire: boolean;
}

interface FriendRequest {
  id: number;
  sender_id: number;
  created_at: string;
  sender: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    avatar_url?: string;
  };
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

const Friends: React.FC = () => {
  const { user } = useAuth();
  const [friends, setFriends] = useState<Friend[]>([]);
  const [friendRequests, setFriendRequests] = useState<FriendRequest[]>([]);
  const [suggestions, setSuggestions] = useState<FriendSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'friends' | 'requests' | 'suggestions'>('friends');

  useEffect(() => {
    if (user) {
      loadFriendsData();
    }
  }, [user]);

  const loadFriendsData = async () => {
    setLoading(true);
    try {
      const [friendsRes, requestsRes, suggestionsRes] = await Promise.all([
        api.get('/api/friends/list'),
        api.get('/api/friends/requests'),
        api.get('/api/friends/suggestions')
      ]);

      if (friendsRes.data.success) {
        setFriends(friendsRes.data.friends);
      }
      if (requestsRes.data.success) {
        setFriendRequests(requestsRes.data.requests);
      }
      if (suggestionsRes.data.success) {
        setSuggestions(suggestionsRes.data.suggestions);
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
        setSuggestions(response.data.suggestions);
      }
      alert('Friend request sent!');
    } catch (error: any) {
      console.error('Error sending friend request:', error);
      alert(error.response?.data?.message || 'Failed to send friend request');
    }
  };

  const respondToRequest = async (requestId: number, action: 'accept' | 'decline') => {
    try {
      await api.post(`/api/friends/respond/${requestId}`, { action });
      // Refresh data
      await loadFriendsData();
      alert(`Friend request ${action}ed!`);
    } catch (error: any) {
      console.error('Error responding to friend request:', error);
      alert(error.response?.data?.message || 'Failed to respond to friend request');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Friends</h1>
          <p className="text-gray-600">Connect with other professionals in your network</p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('friends')}
              className={`flex items-center px-6 py-4 text-sm font-medium ${
                activeTab === 'friends'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <UserGroupSolidIcon className="h-5 w-5 mr-2" />
              My Friends ({friends.length})
            </button>
            <button
              onClick={() => setActiveTab('requests')}
              className={`flex items-center px-6 py-4 text-sm font-medium ${
                activeTab === 'requests'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <UserPlusIcon className="h-5 w-5 mr-2" />
              Friend Requests ({friendRequests.length})
            </button>
            <button
              onClick={() => setActiveTab('suggestions')}
              className={`flex items-center px-6 py-4 text-sm font-medium ${
                activeTab === 'suggestions'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <UserGroupIcon className="h-5 w-5 mr-2" />
              Suggestions
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {activeTab === 'friends' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">My Friends</h2>
              {friends.length === 0 ? (
                <div className="text-center py-12">
                  <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No friends yet</h3>
                  <p className="text-gray-500 mb-4">Start connecting with other professionals!</p>
                  <button
                    onClick={() => setActiveTab('suggestions')}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Find Friends
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {friends.map((friend) => (
                    <div key={friend.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                          {(friend.first_name[0] + friend.last_name[0]).toUpperCase()}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">
                            {friend.first_name} {friend.last_name}
                          </h3>
                          <p className="text-sm text-gray-500">{friend.email}</p>
                          {friend.is_available_for_hire && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                              Available for Hire
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'requests' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Friend Requests</h2>
              {friendRequests.length === 0 ? (
                <div className="text-center py-12">
                  <UserPlusIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No friend requests</h3>
                  <p className="text-gray-500">When someone sends you a friend request, it will appear here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {friendRequests.map((request) => (
                    <div key={request.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                            {(request.sender.first_name[0] + request.sender.last_name[0]).toUpperCase()}
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900">
                              {request.sender.first_name} {request.sender.last_name}
                            </h3>
                            <p className="text-sm text-gray-500">{request.sender.email}</p>
                            <p className="text-xs text-gray-400">
                              Sent {new Date(request.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => respondToRequest(request.id, 'accept')}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center"
                          >
                            <CheckIcon className="h-4 w-4 mr-1" />
                            Accept
                          </button>
                          <button
                            onClick={() => respondToRequest(request.id, 'decline')}
                            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex items-center"
                          >
                            <XMarkIcon className="h-4 w-4 mr-1" />
                            Decline
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'suggestions' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Friend Suggestions</h2>
              {suggestions.length === 0 ? (
                <div className="text-center py-12">
                  <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No suggestions available</h3>
                  <p className="text-gray-500">Check back later for new friend suggestions!</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {suggestions.map((suggestion) => (
                    <div key={suggestion.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                            {(suggestion.first_name[0] + suggestion.last_name[0]).toUpperCase()}
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900">
                              {suggestion.first_name} {suggestion.last_name}
                            </h3>
                            <p className="text-sm text-gray-500">{suggestion.location || 'No location'}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => sendFriendRequest(suggestion.id)}
                          className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 flex items-center text-sm"
                        >
                          <UserPlusIcon className="h-4 w-4 mr-1" />
                          Add Friend
                        </button>
                      </div>
                      {suggestion.bio && (
                        <p className="text-sm text-gray-600 mt-2">{suggestion.bio}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Friends;