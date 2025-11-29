import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  UserCircleIcon,
  MapPinIcon,
  BriefcaseIcon,
  BuildingOfficeIcon,
  EnvelopeIcon,
  PhoneIcon,
  CalendarIcon,
  ChatBubbleLeftIcon,
  ArrowLeftIcon,
  UserPlusIcon,
  UserMinusIcon,
} from '@heroicons/react/24/outline';
import { authAPI, postsAPI, usersAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { ApiError } from '../types';

interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  username?: string;
  user_type: string;
  location?: string;
  phone?: string;
  bio?: string;
  avatar_url?: string;
  occupation?: string;
  company_name?: string;
  created_at: string;
  is_available_for_hire: boolean;
  posts_count: number;
  is_following: boolean; // Changed from optional to required since we always set defaults
  followers_count: number; // Changed from optional to required since we always set defaults
  following_count: number; // Changed from optional to required since we always set defaults
}

interface Post {
  id: number;
  content: string;
  image_url?: string;
  video_url?: string;
  created_at: string;
  likes_count: number;
  comments_count: number;
}

interface FollowUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  username?: string;
  avatar_url?: string;
  bio?: string;
  occupation?: string;
  location?: string;
  is_following?: boolean;
  followers_count?: number;
  following_count?: number;
}

// Constants
const USERS_LIST_ROUTE = '/friends';
const REDIRECT_DELAY_SECONDS = 3;

const UserProfile: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [userPosts, setUserPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'posts' | 'about' | 'photos' | 'videos' | 'followers' | 'following'>('posts');
  const [isFollowing, setIsFollowing] = useState(false);
  const [followersCount, setFollowersCount] = useState(0);
  const [followingCount, setFollowingCount] = useState(0);
  const [isFollowLoading, setIsFollowLoading] = useState(false);
  const [redirectCountdown, setRedirectCountdown] = useState<number | null>(null);
  const [followersList, setFollowersList] = useState<FollowUser[]>([]);
  const [followingList, setFollowingList] = useState<FollowUser[]>([]);
  const [isLoadingFollowers, setIsLoadingFollowers] = useState(false);
  const [isLoadingFollowing, setIsLoadingFollowing] = useState(false);
  const [followersLoaded, setFollowersLoaded] = useState(false);
  const [followingLoaded, setFollowingLoaded] = useState(false);
  
  // Use ref to store interval ID for proper cleanup
  // In browsers, setInterval returns number; in Node.js it returns NodeJS.Timeout
  const countdownIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchUserProfile = useCallback(async () => {
    if (!userId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await authAPI.getUserProfile(userId);
      const userData = response.user as unknown as Record<string, unknown>; // API response may have additional fields
      
      // Normalize user data with safe defaults
      const normalizedProfile: UserProfile = {
        id: userData.id as number,
        email: (userData.email as string) || '',
        first_name: (userData.first_name as string) || '',
        last_name: (userData.last_name as string) || '',
        username: userData.username as string | undefined,
        user_type: (userData.user_type as string) || 'freelancer',
        location: userData.location as string | undefined,
        phone: userData.phone as string | undefined,
        bio: userData.bio as string | undefined,
        avatar_url: userData.avatar_url as string | undefined,
        occupation: userData.occupation as string | undefined,
        company_name: userData.company_name as string | undefined,
        created_at: (userData.created_at as string) || new Date().toISOString(),
        is_available_for_hire: (userData.is_available_for_hire as boolean) ?? false,
        posts_count: (userData.posts_count as number) ?? 0,
        is_following: (userData.is_following as boolean) ?? false,
        followers_count: (userData.followers_count as number) ?? 0,
        following_count: (userData.following_count as number) ?? 0,
      };
      
      setProfile(normalizedProfile);
      
      // Set follow state - these are now guaranteed to be defined
      setIsFollowing(normalizedProfile.is_following);
      setFollowersCount(normalizedProfile.followers_count);
      setFollowingCount(normalizedProfile.following_count);

      // Fetch user's posts
      const allPosts = await postsAPI.getPosts();
      const filteredPosts = allPosts.filter((post: { user_id?: number }) => post.user_id === parseInt(userId));
      setUserPosts(filteredPosts);
    } catch (error: unknown) {
      console.error('Failed to fetch user profile:', error);
      
      // Extract error message with more detail
      let errorMessage = 'Failed to load user profile';
      const errorObj = error as { response?: { data?: { detail?: string; message?: string }; status?: number }; message?: string };
      if (errorObj.response?.data?.detail) {
        errorMessage = errorObj.response.data.detail;
      } else if (errorObj.response?.data?.message) {
        errorMessage = errorObj.response.data.message;
      } else if (errorObj.response?.status === 404) {
        errorMessage = `User with ID "${userId}" not found`;
      } else if (errorObj.message) {
        errorMessage = errorObj.message;
      }
      
      setError(errorMessage);
      toast.error(errorMessage);
      
      // Auto-redirect to users page after 3 seconds for 404 errors
      if (errorObj.response?.status === 404) {
        console.log(`User not found. Auto-redirecting to users page in ${REDIRECT_DELAY_SECONDS} seconds...`);
        setRedirectCountdown(REDIRECT_DELAY_SECONDS);
        
        // Clear any existing interval
        if (countdownIntervalRef.current) {
          clearInterval(countdownIntervalRef.current);
        }
        
        // Countdown timer
        countdownIntervalRef.current = setInterval(() => {
          setRedirectCountdown((prev) => {
            if (prev === null || prev <= 1) {
              if (countdownIntervalRef.current) {
                clearInterval(countdownIntervalRef.current);
                countdownIntervalRef.current = null;
              }
              navigate(USERS_LIST_ROUTE);
              return null;
            }
            return prev - 1;
          });
        }, 1000);
      }
    } finally {
      setIsLoading(false);
    }
  }, [userId, navigate]);

  useEffect(() => {
    if (userId) {
      // Reset loaded states when userId changes
      setFollowersLoaded(false);
      setFollowingLoaded(false);
      setFollowersList([]);
      setFollowingList([]);
      setActiveTab('posts');
      fetchUserProfile();
    }
    
    // Cleanup countdown interval on unmount or userId change
    return () => {
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
        countdownIntervalRef.current = null;
      }
    };
  }, [userId, fetchUserProfile]);

  const handleMessageUser = () => {
    // Navigate to messages with this user
    navigate(`/messages?user=${userId}`);
    toast.success('Opening chat...');
  };

  const handleFollowToggle = async () => {
    if (!userId) return;
    
    setIsFollowLoading(true);
    try {
      if (isFollowing) {
        await usersAPI.unfollowUser(parseInt(userId));
        setIsFollowing(false);
        setFollowersCount(prev => Math.max(0, prev - 1));
        toast.success('User unfollowed');
      } else {
        await usersAPI.followUser(parseInt(userId));
        setIsFollowing(true);
        setFollowersCount(prev => prev + 1);
        toast.success('User followed');
      }
    } catch (error: unknown) {
      const apiError = error as ApiError;
      console.error('Failed to toggle follow:', error);
      toast.error(apiError.response?.data?.message || 'Failed to update follow status');
    } finally {
      setIsFollowLoading(false);
    }
  };

  const fetchFollowers = async (forceRefresh = false) => {
    if (!userId) return;
    
    // Don't refetch if already loaded successfully (unless force refresh)
    if (followersLoaded && !forceRefresh) return;
    
    setIsLoadingFollowers(true);
    try {
      const response = await usersAPI.getUserFollowers(parseInt(userId));
      // Ensure we always get an array, even if API response is malformed
      const followers = Array.isArray(response?.followers) ? response.followers : [];
      setFollowersList(followers);
      setFollowersLoaded(true);
    } catch (error: unknown) {
      console.error('Failed to fetch followers:', error);
      // Provide more helpful error message based on error type
      const apiError = error as { response?: { status?: number }; message?: string };
      if (apiError.response?.status === 401) {
        toast.error('Please log in to view followers');
      } else if (apiError.response?.status === 404) {
        toast.error('User not found');
      } else {
        toast.error('Failed to load followers. Click again to retry.');
      }
      setFollowersLoaded(false);
    } finally {
      setIsLoadingFollowers(false);
    }
  };

  const fetchFollowing = async (forceRefresh = false) => {
    if (!userId) return;
    
    // Don't refetch if already loaded successfully (unless force refresh)
    if (followingLoaded && !forceRefresh) return;
    
    setIsLoadingFollowing(true);
    try {
      const response = await usersAPI.getUserFollowing(parseInt(userId));
      // Ensure we always get an array, even if API response is malformed
      const following = Array.isArray(response?.following) ? response.following : [];
      setFollowingList(following);
      setFollowingLoaded(true);
    } catch (error: unknown) {
      console.error('Failed to fetch following:', error);
      // Provide more helpful error message based on error type
      const apiError = error as { response?: { status?: number }; message?: string };
      if (apiError.response?.status === 401) {
        toast.error('Please log in to view following');
      } else if (apiError.response?.status === 404) {
        toast.error('User not found');
      } else {
        toast.error('Failed to load following. Click again to retry.');
      }
      setFollowingLoaded(false);
    } finally {
      setIsLoadingFollowing(false);
    }
  };

  const handleTabChange = (tab: 'posts' | 'about' | 'photos' | 'videos' | 'followers' | 'following') => {
    setActiveTab(tab);
    // Fetch data if not loaded yet (allows retry on failure since followersLoaded/followingLoaded will be false)
    if (tab === 'followers' && !followersLoaded && !isLoadingFollowers) {
      fetchFollowers();
    } else if (tab === 'following' && !followingLoaded && !isLoadingFollowing) {
      fetchFollowing();
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-md mx-auto px-4"
        >
          <div className="bg-white rounded-lg shadow-md p-8">
            <UserCircleIcon className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">User Not Found</h2>
            <p className="text-gray-600 mb-6">
              {error || "The user you're looking for doesn't exist or may have been removed."}
            </p>
            {redirectCountdown !== null && (
              <div className="mb-6">
                <div className="inline-flex items-center justify-center px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg text-blue-700">
                  <span className="font-medium">
                    Auto-redirecting in {redirectCountdown} second{redirectCountdown !== 1 ? 's' : ''}...
                  </span>
                </div>
              </div>
            )}
            <div className="space-y-3">
              <button
                onClick={() => navigate(-1)}
                className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <ArrowLeftIcon className="w-5 h-5 mr-2" />
                Go Back
              </button>
              <button
                onClick={() => navigate(USERS_LIST_ROUTE)}
                className="w-full flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <UserCircleIcon className="w-5 h-5 mr-2" />
                Browse All Users
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                Return to Dashboard
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  const isOwnProfile = currentUser?.id === profile.id;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          Back
        </button>

        {/* Profile Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-md overflow-hidden mb-6"
        >
          {/* Cover Image */}
          <div className="h-48 bg-gradient-to-r from-blue-500 to-purple-600"></div>

          <div className="relative px-6 pb-6">
            {/* Avatar */}
            <div className="absolute -top-16 left-6">
              <div className="w-32 h-32 rounded-full border-4 border-white bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                {profile.avatar_url ? (
                  <img
                    src={profile.avatar_url}
                    alt={`${profile.first_name} ${profile.last_name}`}
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <span className="text-white text-4xl font-bold">
                    {profile.first_name?.[0]}{profile.last_name?.[0]}
                  </span>
                )}
              </div>
            </div>

            {/* Profile Info */}
            <div className="pt-20">
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">
                    {profile.first_name} {profile.last_name}
                  </h1>
                  {profile.username && (
                    <p className="text-blue-600 font-medium mt-1">@{profile.username}</p>
                  )}
                  {profile.occupation && (
                    <p className="text-gray-600 mt-2 flex items-center">
                      <BriefcaseIcon className="w-5 h-5 mr-2" />
                      {profile.occupation}
                    </p>
                  )}
                  {profile.company_name && (
                    <p className="text-gray-600 mt-1 flex items-center">
                      <BuildingOfficeIcon className="w-5 h-5 mr-2" />
                      {profile.company_name}
                    </p>
                  )}
                  {profile.location && (
                    <p className="text-gray-600 mt-1 flex items-center">
                      <MapPinIcon className="w-5 h-5 mr-2" />
                      {profile.location}
                    </p>
                  )}
                </div>

                {/* Action Buttons */}
                {!isOwnProfile && (
                  <div className="flex space-x-3">
                    <button
                      onClick={handleFollowToggle}
                      disabled={isFollowLoading}
                      className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                        isFollowing
                          ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      {isFollowLoading ? (
                        <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
                      ) : isFollowing ? (
                        <UserMinusIcon className="w-5 h-5 mr-2" />
                      ) : (
                        <UserPlusIcon className="w-5 h-5 mr-2" />
                      )}
                      {isFollowing ? 'Unfollow' : 'Follow'}
                    </button>
                    <button
                      onClick={handleMessageUser}
                      className="flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <ChatBubbleLeftIcon className="w-5 h-5 mr-2" />
                      Message
                    </button>
                  </div>
                )}

                {isOwnProfile && (
                  <button
                    onClick={() => navigate('/profile')}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Edit Profile
                  </button>
                )}
              </div>

              {/* Stats */}
              <div className="flex space-x-8 mt-6 pt-6 border-t border-gray-200">
                <button
                  onClick={() => handleTabChange('posts')}
                  className="text-center hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors"
                >
                  <p className="text-2xl font-bold text-gray-900">{profile.posts_count}</p>
                  <p className="text-sm text-gray-600">Posts</p>
                </button>
                <button
                  onClick={() => handleTabChange('followers')}
                  className="text-center hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors"
                >
                  <p className="text-2xl font-bold text-gray-900">{followersCount}</p>
                  <p className="text-sm text-gray-600">Followers</p>
                </button>
                <button
                  onClick={() => handleTabChange('following')}
                  className="text-center hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors"
                >
                  <p className="text-2xl font-bold text-gray-900">{followingCount}</p>
                  <p className="text-sm text-gray-600">Following</p>
                </button>
                {profile.is_available_for_hire && (
                  <div className="flex items-center">
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                      Available for Hire
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex flex-wrap">
              <button
                onClick={() => handleTabChange('posts')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'posts'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Posts ({profile.posts_count})
              </button>
              <button
                onClick={() => handleTabChange('about')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'about'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                About
              </button>
              <button
                onClick={() => handleTabChange('followers')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'followers'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Followers ({followersCount})
              </button>
              <button
                onClick={() => handleTabChange('following')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'following'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Following ({followingCount})
              </button>
              <button
                onClick={() => handleTabChange('photos')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'photos'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Photos ({userPosts.filter(p => p.image_url).length})
              </button>
              <button
                onClick={() => handleTabChange('videos')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'videos'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Videos ({userPosts.filter(p => p.video_url).length})
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'posts' && (
              <div className="space-y-4">
                {userPosts.length === 0 ? (
                  <div className="text-center py-12">
                    <UserCircleIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No posts yet</p>
                  </div>
                ) : (
                  userPosts.map((post) => (
                    <motion.div
                      key={post.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-gray-50 rounded-lg p-6"
                    >
                      <p className="text-gray-900 mb-4">{post.content}</p>
                      {post.image_url && (
                        <img
                          src={post.image_url}
                          alt="Post"
                          className="w-full max-h-96 object-cover rounded-lg mb-4"
                        />
                      )}
                      <div className="flex items-center space-x-6 text-sm text-gray-500">
                        <span>{post.likes_count} likes</span>
                        <span>{post.comments_count} comments</span>
                        <span>{new Date(post.created_at).toLocaleDateString()}</span>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'photos' && (
              <div>
                {userPosts.filter(p => p.image_url).length === 0 ? (
                  <div className="text-center py-12">
                    <UserCircleIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No photos yet</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    {userPosts
                      .filter(p => p.image_url)
                      .map((post) => (
                        <motion.div
                          key={post.id}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="relative aspect-square rounded-lg overflow-hidden bg-gray-100 cursor-pointer group"
                        >
                          <img
                            src={post.image_url}
                            alt="Photo"
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                          />
                          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 flex items-center justify-center">
                            <div className="opacity-0 group-hover:opacity-100 text-white text-sm space-x-4 transition-opacity duration-200">
                              <span>❤️ {post.likes_count}</span>
                              <span>💬 {post.comments_count}</span>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'videos' && (
              <div>
                {userPosts.filter(p => p.video_url).length === 0 ? (
                  <div className="text-center py-12">
                    <UserCircleIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No videos yet</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {userPosts
                      .filter(p => p.video_url)
                      .map((post) => (
                        <motion.div
                          key={post.id}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="relative bg-gray-100 rounded-lg overflow-hidden"
                        >
                          <video
                            src={post.video_url}
                            controls
                            className="w-full h-auto max-h-64 object-cover"
                            preload="metadata"
                          >
                            Your browser does not support the video tag.
                          </video>
                          <div className="p-3 bg-white">
                            <p className="text-sm text-gray-900 line-clamp-2">{post.content}</p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
                              <span>❤️ {post.likes_count}</span>
                              <span>💬 {post.comments_count}</span>
                              <span>{new Date(post.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'about' && (
              <div className="space-y-6">
                {profile.bio && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Bio</h3>
                    <p className="text-gray-700">{profile.bio}</p>
                  </div>
                )}

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
                  <div className="space-y-3">
                    {profile.email && (
                      <div className="flex items-center text-gray-700">
                        <EnvelopeIcon className="w-5 h-5 mr-3 text-gray-400" />
                        <span>{profile.email}</span>
                      </div>
                    )}
                    {profile.phone && (
                      <div className="flex items-center text-gray-700">
                        <PhoneIcon className="w-5 h-5 mr-3 text-gray-400" />
                        <span>{profile.phone}</span>
                      </div>
                    )}
                    <div className="flex items-center text-gray-700">
                      <CalendarIcon className="w-5 h-5 mr-3 text-gray-400" />
                      <span>Joined {new Date(profile.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Account Type</h3>
                  <span className="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                    {profile.user_type.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                  </span>
                </div>
              </div>
            )}

            {activeTab === 'followers' && (
              <div>
                {isLoadingFollowers ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading followers...</p>
                  </div>
                ) : followersList.length === 0 ? (
                  <div className="text-center py-12">
                    <UserCircleIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No followers yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {followersList.map((follower) => (
                      <motion.div
                        key={follower.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center justify-between bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
                      >
                        <div
                          className="flex items-center space-x-4 cursor-pointer"
                          onClick={() => navigate(`/user/${follower.id}`)}
                        >
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                            {follower.avatar_url ? (
                              <img
                                src={follower.avatar_url}
                                alt={`${follower.first_name} ${follower.last_name}`}
                                className="w-full h-full rounded-full object-cover"
                              />
                            ) : (
                              <span>{follower.first_name?.[0]}{follower.last_name?.[0]}</span>
                            )}
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900">
                              {follower.first_name} {follower.last_name}
                            </p>
                            {follower.username && (
                              <p className="text-sm text-blue-600">@{follower.username}</p>
                            )}
                            {follower.occupation && (
                              <p className="text-sm text-gray-500">{follower.occupation}</p>
                            )}
                          </div>
                        </div>
                        <div className="text-right text-sm text-gray-500">
                          <p>{follower.followers_count} followers</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'following' && (
              <div>
                {isLoadingFollowing ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading following...</p>
                  </div>
                ) : followingList.length === 0 ? (
                  <div className="text-center py-12">
                    <UserCircleIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">Not following anyone yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {followingList.map((followed) => (
                      <motion.div
                        key={followed.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center justify-between bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
                      >
                        <div
                          className="flex items-center space-x-4 cursor-pointer"
                          onClick={() => navigate(`/user/${followed.id}`)}
                        >
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                            {followed.avatar_url ? (
                              <img
                                src={followed.avatar_url}
                                alt={`${followed.first_name} ${followed.last_name}`}
                                className="w-full h-full rounded-full object-cover"
                              />
                            ) : (
                              <span>{followed.first_name?.[0]}{followed.last_name?.[0]}</span>
                            )}
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900">
                              {followed.first_name} {followed.last_name}
                            </p>
                            {followed.username && (
                              <p className="text-sm text-blue-600">@{followed.username}</p>
                            )}
                            {followed.occupation && (
                              <p className="text-sm text-gray-500">{followed.occupation}</p>
                            )}
                          </div>
                        </div>
                        <div className="text-right text-sm text-gray-500">
                          <p>{followed.followers_count} followers</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
