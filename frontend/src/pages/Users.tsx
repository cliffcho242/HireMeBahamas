import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import axios from 'axios';
import { UserGroupIcon, UserPlusIcon, CheckIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { UserGroupIcon as UserGroupSolidIcon } from '@heroicons/react/24/solid';

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  username?: string;
  avatar_url?: string;
  bio?: string;
  occupation?: string;
  location?: string;
  is_following?: boolean;  // Make optional for defensive programming
  followers_count?: number;  // Make optional for defensive programming
  following_count?: number;  // Make optional for defensive programming
}

const Users: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [following, setFollowing] = useState<User[]>([]);
  const [followers, setFollowers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'discover' | 'following' | 'followers'>('discover');

  const getUserInitials = (userData: User): string => {
    const firstInitial = userData.first_name?.[0] || '';
    const lastInitial = userData.last_name?.[0] || '';
    const initials = (firstInitial + lastInitial).toUpperCase();
    return initials || '?';
  };

  // Helper function to validate and filter user data
  const validateUsers = (userArray: (User | null | undefined)[]): User[] => {
    return userArray.filter((u: User | null | undefined): u is User => {
      return u != null && typeof u === 'object' && 'id' in u;
    });
  };

  // Helper function to extract error message from API errors
  const getErrorMessage = (error: unknown, defaultMessage: string): string => {
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      return error.response.data.detail;
    }
    return defaultMessage;
  };

  const loadUsersData = useCallback(async () => {
    setLoading(true);
    try {
      const [usersRes, followingRes, followersRes] = await Promise.all([
        api.get('/api/users/list'),
        api.get('/api/users/following/list'),
        api.get('/api/users/followers/list')
      ]);

      if (usersRes.data.success && Array.isArray(usersRes.data.users)) {
        setUsers(validateUsers(usersRes.data.users));
      }
      if (followingRes.data.success && Array.isArray(followingRes.data.following)) {
        setFollowing(validateUsers(followingRes.data.following));
      }
      if (followersRes.data.success && Array.isArray(followersRes.data.followers)) {
        setFollowers(validateUsers(followersRes.data.followers));
      }
    } catch (error) {
      console.error('Error loading users data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      loadUsersData();
    }
  }, [user, loadUsersData]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      loadUsersData();
      return;
    }

    try {
      const response = await api.get(`/api/users/list?search=${searchTerm}`);
      if (response.data.success) {
        setUsers(validateUsers(response.data.users));
      }
    } catch (error) {
      console.error('Error searching users:', error);
    }
  };

  const handleFollow = async (userId: number) => {
    try {
      await api.post(`/api/users/follow/${userId}`);
      // Refresh data
      await loadUsersData();
    } catch (error) {
      console.error('Error following user:', error);
      alert(getErrorMessage(error, 'Failed to follow user'));
    }
  };

  const handleUnfollow = async (userId: number) => {
    try {
      await api.post(`/api/users/unfollow/${userId}`);
      // Refresh data
      await loadUsersData();
    } catch (error) {
      console.error('Error unfollowing user:', error);
      alert(getErrorMessage(error, 'Failed to unfollow user'));
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Discover Users</h1>
          <p className="text-gray-600">Connect with other professionals in your network</p>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 p-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search users by name, occupation, location..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleSearch}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Search
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('discover')}
              className={`flex items-center px-6 py-4 text-sm font-medium ${
                activeTab === 'discover'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <UserGroupIcon className="h-5 w-5 mr-2" />
              Discover Users
            </button>
            <button
              onClick={() => setActiveTab('following')}
              className={`flex items-center px-6 py-4 text-sm font-medium ${
                activeTab === 'following'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <UserPlusIcon className="h-5 w-5 mr-2" />
              Following ({following.length})
            </button>
            <button
              onClick={() => setActiveTab('followers')}
              className={`flex items-center px-6 py-4 text-sm font-medium ${
                activeTab === 'followers'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <UserGroupSolidIcon className="h-5 w-5 mr-2" />
              Followers ({followers.length})
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {activeTab === 'discover' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Discover Users</h2>
              {users.length === 0 ? (
                <div className="text-center py-12">
                  <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
                  <p className="text-gray-500">Try adjusting your search criteria</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {users.map((userData) => (
                    <div key={userData.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                            {getUserInitials(userData)}
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900">
                              {userData.first_name || ''} {userData.last_name || ''}
                            </h3>
                            {userData.occupation && (
                              <p className="text-sm text-gray-500">{userData.occupation}</p>
                            )}
                            {userData.location && (
                              <p className="text-xs text-gray-400">{userData.location}</p>
                            )}
                          </div>
                        </div>
                      </div>
                      {userData.bio && (
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{userData.bio}</p>
                      )}
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                        <span>{userData.followers_count ?? 0} followers</span>
                        <span>{userData.following_count ?? 0} following</span>
                      </div>
                      {(userData.is_following ?? false) ? (
                        <button
                          onClick={() => handleUnfollow(userData.id)}
                          className="w-full bg-gray-200 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-300 flex items-center justify-center text-sm"
                        >
                          <CheckIcon className="h-4 w-4 mr-1" />
                          Following
                        </button>
                      ) : (
                        <button
                          onClick={() => handleFollow(userData.id)}
                          className="w-full bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center text-sm"
                        >
                          <UserPlusIcon className="h-4 w-4 mr-1" />
                          Follow
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'following' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Following</h2>
              {following.length === 0 ? (
                <div className="text-center py-12">
                  <UserPlusIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Not following anyone yet</h3>
                  <p className="text-gray-500">Start following other professionals!</p>
                  <button
                    onClick={() => setActiveTab('discover')}
                    className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Discover Users
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {following.map((userData) => (
                    <div key={userData.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                          {getUserInitials(userData)}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">
                            {userData.first_name || ''} {userData.last_name || ''}
                          </h3>
                          {userData.occupation && (
                            <p className="text-sm text-gray-500">{userData.occupation}</p>
                          )}
                        </div>
                      </div>
                      {userData.bio && (
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{userData.bio}</p>
                      )}
                      <button
                        onClick={() => handleUnfollow(userData.id)}
                        className="w-full bg-gray-200 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-300 text-sm"
                      >
                        Unfollow
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'followers' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Followers</h2>
              {followers.length === 0 ? (
                <div className="text-center py-12">
                  <UserGroupSolidIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No followers yet</h3>
                  <p className="text-gray-500">When others follow you, they will appear here</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {followers.map((userData) => (
                    <div key={userData.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                          {getUserInitials(userData)}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">
                            {userData.first_name || ''} {userData.last_name || ''}
                          </h3>
                          {userData.occupation && (
                            <p className="text-sm text-gray-500">{userData.occupation}</p>
                          )}
                        </div>
                      </div>
                      {userData.bio && (
                        <p className="text-sm text-gray-600 mt-2 line-clamp-2">{userData.bio}</p>
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

export default Users;