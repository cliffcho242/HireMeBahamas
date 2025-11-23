import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api, { hireMeAPI, usersAPI } from '../services/api';
import { XCircleIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolidIcon } from '@heroicons/react/24/solid';
import { motion } from 'framer-motion';

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
}

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isAvailable, setIsAvailable] = useState(false);
  const [togglingAvailability, setTogglingAvailability] = useState(false);
  const [followersCount, setFollowersCount] = useState(0);
  const [followingCount, setFollowingCount] = useState(0);
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

  useEffect(() => {
    if (user) {
      fetchProfile();
    }
  }, [user]);

  const fetchProfile = async () => {
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
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
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
        <div className="text-xl">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit Profile
              </button>
            )}
          </div>

          {/* Availability Toggle */}
          {!editing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6 mb-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    HireMe
                  </h3>
                  <p className="text-gray-600">
                    {isAvailable
                      ? "You're visible to employers looking for talent on the HireMe board."
                      : "Turn on availability to appear on the HireMe board and get discovered by employers."
                    }
                  </p>
                </div>
                <button
                  onClick={toggleAvailability}
                  disabled={togglingAvailability}
                  className={`flex items-center gap-3 px-6 py-3 rounded-lg font-medium transition-all ${
                    isAvailable
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                  } ${togglingAvailability ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {togglingAvailability ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-current"></div>
                  ) : isAvailable ? (
                    <CheckCircleSolidIcon className="h-5 w-5" />
                  ) : (
                    <XCircleIcon className="h-5 w-5" />
                  )}
                  {isAvailable ? 'Available for Hire' : 'Not Available'}
                </button>
              </div>
            </motion.div>
          )}

          {/* Profile Stats */}
          {!editing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 mb-6"
            >
              <div className="flex justify-around items-center">
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">{followersCount}</p>
                  <p className="text-sm text-gray-600 mt-1">Followers</p>
                </div>
                <div className="h-12 w-px bg-blue-200"></div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-indigo-600">{followingCount}</p>
                  <p className="text-sm text-gray-600 mt-1">Following</p>
                </div>
              </div>
            </motion.div>
          )}

          {editing ? (
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
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Name</h3>
                  <p className="text-gray-900">
                    {profile?.first_name} {profile?.last_name}
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Email</h3>
                  <p className="text-gray-900">{profile?.email}</p>
                </div>
              </div>

              {profile?.username && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Username</h3>
                  <p className="text-gray-900">@{profile.username}</p>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {profile?.occupation && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-1">Occupation / Job Title</h3>
                    <p className="text-gray-900">{profile.occupation}</p>
                  </div>
                )}
                {profile?.company_name && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-1">Company Name</h3>
                    <p className="text-gray-900">{profile.company_name}</p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Phone</h3>
                  <p className="text-gray-900">{profile?.phone || 'Not provided'}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Location</h3>
                  <p className="text-gray-900">{profile?.location || 'Not provided'}</p>
                </div>
              </div>

              {profile?.bio && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Bio</h3>
                  <p className="text-gray-900 whitespace-pre-wrap">{profile.bio}</p>
                </div>
              )}

              {profile?.skills && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Skills</h3>
                  <p className="text-gray-900 whitespace-pre-wrap">{profile.skills}</p>
                </div>
              )}

              {profile?.experience && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Experience</h3>
                  <p className="text-gray-900 whitespace-pre-wrap">{profile.experience}</p>
                </div>
              )}

              {profile?.education && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Education</h3>
                  <p className="text-gray-900 whitespace-pre-wrap">{profile.education}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;