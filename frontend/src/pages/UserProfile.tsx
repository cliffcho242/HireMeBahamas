import React, { useState, useEffect } from 'react';
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
  is_following?: boolean;
  followers_count?: number;
  following_count?: number;
}

interface Post {
  id: number;
  content: string;
  image_url?: string;
  created_at: string;
  likes_count: number;
  comments_count: number;
}

const UserProfile: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [userPosts, setUserPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'posts' | 'about'>('posts');
  const [isFollowing, setIsFollowing] = useState(false);
  const [followersCount, setFollowersCount] = useState(0);
  const [isFollowLoading, setIsFollowLoading] = useState(false);
  const [redirectCountdown, setRedirectCountdown] = useState<number | null>(null);

  useEffect(() => {
    if (userId) {
      fetchUserProfile();
    }
  }, [userId]);

  const fetchUserProfile = async () => {
    if (!userId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await authAPI.getUserProfile(userId);
      const userData = response.user;
      setProfile(userData as unknown as UserProfile);
      
      // Set follow state
      setIsFollowing(userData.is_following || false);
      setFollowersCount(userData.followers_count || 0);

      // Fetch user's posts
      const allPosts = await postsAPI.getPosts();
      const filteredPosts = allPosts.filter((post: any) => post.user_id === parseInt(userId));
      setUserPosts(filteredPosts);
    } catch (error: any) {
      console.error('Failed to fetch user profile:', error);
      
      // Extract error message with more detail
      let errorMessage = 'Failed to load user profile';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.response?.status === 404) {
        errorMessage = `User with ID "${userId}" not found`;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
      toast.error(errorMessage);
      
      // Auto-redirect to users page after 3 seconds for 404 errors
      if (error.response?.status === 404) {
        console.log('User not found. Auto-redirecting to users page in 3 seconds...');
        setRedirectCountdown(3);
        
        // Countdown timer
        const countdownInterval = setInterval(() => {
          setRedirectCountdown((prev) => {
            if (prev === null || prev <= 1) {
              clearInterval(countdownInterval);
              navigate('/friends');
              return null;
            }
            return prev - 1;
          });
        }, 1000);
        
        // Cleanup on unmount
        return () => clearInterval(countdownInterval);
      }
    } finally {
      setIsLoading(false);
    }
  };

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
    } catch (error: any) {
      console.error('Failed to toggle follow:', error);
      toast.error(error.response?.data?.message || 'Failed to update follow status');
    } finally {
      setIsFollowLoading(false);
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
                onClick={() => navigate('/friends')}
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
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{profile.posts_count}</p>
                  <p className="text-sm text-gray-600">Posts</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{followersCount}</p>
                  <p className="text-sm text-gray-600">Followers</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{profile.following_count || 0}</p>
                  <p className="text-sm text-gray-600">Following</p>
                </div>
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
            <nav className="flex">
              <button
                onClick={() => setActiveTab('posts')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'posts'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Posts ({profile.posts_count})
              </button>
              <button
                onClick={() => setActiveTab('about')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'about'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                About
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
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
