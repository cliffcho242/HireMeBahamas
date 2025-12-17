import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api, { hireMeAPI, usersAPI, postsAPI } from '../services/api';
import {
  MapPinIcon,
  BriefcaseIcon,
  BuildingOfficeIcon,
  EnvelopeIcon,
  PhoneIcon,
  UserCircleIcon,
  PencilIcon,
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolidIcon } from '@heroicons/react/24/solid';
import { motion } from 'framer-motion';
import ProfilePictureGallery from '../components/ProfilePictureGallery';
import LazyImage from '../components/LazyImage';

interface Profile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  username?: string;
  phone?: string;
  location?: string;
  bio?: string;
  skills?: string;
  experience?: string;
  education?: string;
  occupation?: string;
  company_name?: string;
  avatar_url?: string;
  followers_count?: number;
  following_count?: number;
  user_type?: string;
  created_at?: string;
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
  followers_count?: number;
}

type ProfileTab = 'posts' | 'about' | 'photos' | 'videos' | 'followers' | 'following' | 'gallery';

const Profile: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isAvailable, setIsAvailable] = useState(false);
  const [togglingAvailability, setTogglingAvailability] = useState(false);
  const [followersCount, setFollowersCount] = useState(0);
  const [followingCount, setFollowingCount] = useState(0);
  const [activeTab, setActiveTab] = useState<ProfileTab>('posts');
  const [userPosts, setUserPosts] = useState<Post[]>([]);
  const [followersList, setFollowersList] = useState<FollowUser[]>([]);
  const [followingList, setFollowingList] = useState<FollowUser[]>([]);
  const [isLoadingFollowers, setIsLoadingFollowers] = useState(false);
  const [isLoadingFollowing, setIsLoadingFollowing] = useState(false);
  const [followersLoaded, setFollowersLoaded] = useState(false);
  const [followingLoaded, setFollowingLoaded] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    phone: '',
    location: '',
    bio: '',
    skills: '',
    experience: '',
    education: '',
    occupation: '',
    company_name: '',
  });

  const fetchProfile = useCallback(async () => {
    try {
      const response = await api.get('/api/auth/profile');
      setProfile(response.data);
      setIsAvailable(response.data.is_available_for_hire || false);
      setFormData({
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
        username: response.data.username || '',
        phone: response.data.phone || '',
        location: response.data.location || '',
        bio: response.data.bio || '',
        skills: response.data.skills || '',
        experience: response.data.experience || '',
        education: response.data.education || '',
        occupation: response.data.occupation || '',
        company_name: response.data.company_name || '',
      });

      // Fetch user's posts
      if (response.data.id) {
        try {
          const posts = await postsAPI.getUserPosts(response.data.id);
          setUserPosts(posts);
        } catch (postsError) {
          console.error('Error fetching user posts:', postsError);
          setUserPosts([]);
        }
      }

      // Fetch follower and following counts
      try {
        const [followersResponse, followingResponse] = await Promise.all([
          usersAPI.getFollowers(),
          usersAPI.getFollowing(),
        ]);
        setFollowersCount(followersResponse.followers?.length || 0);
        setFollowingCount(followingResponse.following?.length || 0);
      } catch (followError) {
        console.error('Error fetching follow stats:', followError);
        // Don't fail the whole page if follow stats fail
        setFollowersCount(0);
        setFollowingCount(0);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      fetchProfile();
    }
  }, [user, fetchProfile]);

  const fetchFollowers = async (forceRefresh = false) => {
    if (!profile?.id) return;
    if (followersLoaded && !forceRefresh) return;
    
    setIsLoadingFollowers(true);
    try {
      const response = await usersAPI.getFollowers();
      const followers = Array.isArray(response?.followers) ? response.followers : [];
      setFollowersList(followers);
      setFollowersLoaded(true);
    } catch (error) {
      console.error('Failed to fetch followers:', error);
      setFollowersLoaded(false);
    } finally {
      setIsLoadingFollowers(false);
    }
  };

  const fetchFollowing = async (forceRefresh = false) => {
    if (!profile?.id) return;
    if (followingLoaded && !forceRefresh) return;
    
    setIsLoadingFollowing(true);
    try {
      const response = await usersAPI.getFollowing();
      const following = Array.isArray(response?.following) ? response.following : [];
      setFollowingList(following);
      setFollowingLoaded(true);
    } catch (error) {
      console.error('Failed to fetch following:', error);
      setFollowingLoaded(false);
    } finally {
      setIsLoadingFollowing(false);
    }
  };

  const handleTabChange = (tab: ProfileTab) => {
    setActiveTab(tab);
    if (tab === 'followers' && !followersLoaded && !isLoadingFollowers) {
      fetchFollowers();
    } else if (tab === 'following' && !followingLoaded && !isLoadingFollowing) {
      fetchFollowing();
    }
  };

  const formatUserType = (userType: string): string => {
    return userType.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  const toggleAvailability = async () => {
    setTogglingAvailability(true);
    try {
      const response = await hireMeAPI.toggleAvailability();
      setIsAvailable(response.is_available);
    } catch (error) {
      console.error('Error toggling availability:', error);
    } finally {
      setTogglingAvailability(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const response = await api.put('/api/auth/profile', formData);
      setProfile(response.data);
      setEditing(false);
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Error updating profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  // Edit mode - show form in a modal-like layout
  if (editing) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-md p-8"
          >
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Edit Profile</h1>
              <button
                onClick={() => setEditing(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">@</span>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    placeholder="yourusername"
                    className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">Your unique username for mentions and profile URL</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Occupation / Job Title
                  </label>
                  <input
                    type="text"
                    name="occupation"
                    value={formData.occupation}
                    onChange={handleInputChange}
                    placeholder="e.g., Software Developer, Plumber, Chef"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name
                  </label>
                  <input
                    type="text"
                    name="company_name"
                    value={formData.company_name}
                    onChange={handleInputChange}
                    placeholder="e.g., ABC Construction, Tech Solutions Ltd"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleInputChange}
                    placeholder="Nassau, Freeport, etc."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bio
                </label>
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Tell employers about yourself..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Skills
                </label>
                <textarea
                  name="skills"
                  value={formData.skills}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="List your key skills..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Experience
                </label>
                <textarea
                  name="experience"
                  value={formData.experience}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Describe your work experience..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Education
                </label>
                <textarea
                  name="education"
                  value={formData.education}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="List your educational background..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={saving}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={() => setEditing(false)}
                  className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4">
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
                {profile?.avatar_url ? (
                  <LazyImage
                    src={profile.avatar_url}
                    alt={`${profile.first_name} ${profile.last_name}`}
                    priority={true}
                    className="w-full h-full rounded-full"
                  />
                ) : (
                  <span className="text-white text-4xl font-bold">
                    {profile?.first_name?.[0]}{profile?.last_name?.[0]}
                  </span>
                )}
              </div>
            </div>

            {/* Profile Info */}
            <div className="pt-20">
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">
                    {profile?.first_name} {profile?.last_name}
                  </h1>
                  {profile?.username && (
                    <p className="text-blue-600 font-medium mt-1">@{profile.username}</p>
                  )}
                  {profile?.occupation && (
                    <p className="text-gray-600 mt-2 flex items-center">
                      <BriefcaseIcon className="w-5 h-5 mr-2" />
                      {profile.occupation}
                    </p>
                  )}
                  {profile?.company_name && (
                    <p className="text-gray-600 mt-1 flex items-center">
                      <BuildingOfficeIcon className="w-5 h-5 mr-2" />
                      {profile.company_name}
                    </p>
                  )}
                  {profile?.location && (
                    <p className="text-gray-600 mt-1 flex items-center">
                      <MapPinIcon className="w-5 h-5 mr-2" />
                      {profile.location}
                    </p>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3">
                  <button
                    onClick={() => setEditing(true)}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <PencilIcon className="w-5 h-5 mr-2" />
                    Edit Profile
                  </button>
                  <button
                    onClick={toggleAvailability}
                    disabled={togglingAvailability}
                    className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                      isAvailable
                        ? 'bg-green-600 text-white hover:bg-green-700'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {togglingAvailability ? (
                      <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
                    ) : (
                      <CheckCircleSolidIcon className="w-5 h-5 mr-2" />
                    )}
                    {isAvailable ? 'Available for Hire' : 'Not Available'}
                  </button>
                </div>
              </div>

              {/* Stats */}
              <div className="flex space-x-8 mt-6 pt-6 border-t border-gray-200">
                <button
                  onClick={() => handleTabChange('posts')}
                  className="text-center hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors"
                >
                  <p className="text-2xl font-bold text-gray-900">{userPosts.length}</p>
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
                {isAvailable && (
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
                Posts ({userPosts.length})
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
              <button
                onClick={() => handleTabChange('gallery')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'gallery'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Gallery
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
                        <LazyImage
                          src={post.image_url}
                          alt="Post"
                          className="w-full max-h-96 rounded-lg mb-4"
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
                          <LazyImage
                            src={post.image_url}
                            alt="Photo"
                            className="w-full h-full group-hover:scale-105 transition-transform duration-200"
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
                {profile?.bio && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Bio</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{profile.bio}</p>
                  </div>
                )}

                {profile?.skills && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Skills</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{profile.skills}</p>
                  </div>
                )}

                {profile?.experience && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Experience</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{profile.experience}</p>
                  </div>
                )}

                {profile?.education && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Education</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{profile.education}</p>
                  </div>
                )}

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
                  <div className="space-y-3">
                    {profile?.email && (
                      <div className="flex items-center text-gray-700">
                        <EnvelopeIcon className="w-5 h-5 mr-3 text-gray-400" />
                        <span>{profile.email}</span>
                      </div>
                    )}
                    {profile?.phone && (
                      <div className="flex items-center text-gray-700">
                        <PhoneIcon className="w-5 h-5 mr-3 text-gray-400" />
                        <span>{profile.phone}</span>
                      </div>
                    )}
                    {profile?.location && (
                      <div className="flex items-center text-gray-700">
                        <MapPinIcon className="w-5 h-5 mr-3 text-gray-400" />
                        <span>{profile.location}</span>
                      </div>
                    )}
                  </div>
                </div>

                {profile?.user_type && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Account Type</h3>
                    <span className="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                      {formatUserType(profile.user_type)}
                    </span>
                  </div>
                )}
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
                              <LazyImage
                                src={follower.avatar_url}
                                alt={`${follower.first_name} ${follower.last_name}`}
                                className="w-full h-full rounded-full"
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
                              <LazyImage
                                src={followed.avatar_url}
                                alt={`${followed.first_name} ${followed.last_name}`}
                                className="w-full h-full rounded-full"
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

            {activeTab === 'gallery' && (
              <ProfilePictureGallery />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;