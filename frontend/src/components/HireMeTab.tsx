import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Switch } from '@headlessui/react';
import api, { hireMeAPI } from '../services/api';
import {
  UserIcon,
  MapPinIcon,
  PhoneIcon,
  EnvelopeIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
  WrenchScrewdriverIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolidIcon } from '@heroicons/react/24/solid';

interface AvailableUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  user_type: string;
  location: string;
  phone: string;
  bio: string;
  avatar_url: string;
  created_at: string;
  trade: string;
}

const HireMeTab: React.FC = () => {
  const [availableUsers, setAvailableUsers] = useState<AvailableUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [userAvailability, setUserAvailability] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    fetchAvailableUsers();
    fetchUserAvailability();
  }, []);

  const fetchAvailableUsers = async (query: string = '') => {
    try {
      setSearching(true);
      const response = await hireMeAPI.getAvailableUsers(query);
      setAvailableUsers(response.users || []);
    } catch (error) {
      console.error('Error fetching available users:', error);
    } finally {
      setLoading(false);
      setSearching(false);
    }
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    fetchAvailableUsers(query);
  };

  const clearSearch = () => {
    setSearchQuery('');
    fetchAvailableUsers('');
  };

  const fetchUserAvailability = async () => {
    try {
      const response = await api.get('/api/auth/profile');
      setUserAvailability(response.data.is_available_for_hire || false);
    } catch (error) {
      console.error('Error fetching user availability:', error);
    }
  };

  const toggleAvailability = async () => {
    setToggling(true);
    try {
      const response = await hireMeAPI.toggleAvailability();
      setUserAvailability(response.is_available);
      await fetchAvailableUsers(); // Refresh the list
    } catch (error) {
      console.error('Error toggling availability:', error);
    } finally {
      setToggling(false);
    }
  };

  const getUserTypeColor = (userType: string) => {
    switch (userType) {
      case 'freelancer': return 'bg-green-100 text-green-800';
      case 'employer': return 'bg-blue-100 text-blue-800';
      case 'recruiter': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* User Availability Toggle */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              HireMe
            </h3>
            <p className="text-gray-600">
              {userAvailability
                ? "You're visible to employers searching for talent."
                : "Turn on to appear in job searches and be discoverable."
              }
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className={`text-sm font-medium ${userAvailability ? 'text-green-600' : 'text-gray-500'}`}>
              {userAvailability ? 'On' : 'Off'}
            </span>
            <Switch
              checked={userAvailability}
              onChange={toggleAvailability}
              disabled={toggling}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                userAvailability ? 'bg-green-600' : 'bg-gray-200'
              } ${toggling ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  userAvailability ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </Switch>
          </div>
        </div>
      </motion.div>

      {/* Available Users List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search by trade, name, or skills (e.g., plumber, electrician, developer)..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
            />
            {searchQuery && (
              <button
                onClick={clearSearch}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                title="Clear search"
              >
                <XCircleIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              </button>
            )}
          </div>
          {searchQuery && (
            <p className="mt-2 text-sm text-gray-600">
              {searching ? 'Searching...' : `Found ${availableUsers.length} available professional${availableUsers.length !== 1 ? 's' : ''}`}
            </p>
          )}
        </div>

        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Available Talent ({availableUsers.length})
          </h2>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : availableUsers.length === 0 ? (
          <div className="text-center py-12">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No talent available right now
            </h3>
            <p className="text-gray-600">
              Check back later or encourage users to make themselves available for hire.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {availableUsers.map((availableUser, index) => (
              <motion.div
                key={availableUser.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {availableUser.first_name?.[0] || availableUser.email[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {availableUser.first_name} {availableUser.last_name}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getUserTypeColor(availableUser.user_type)}`}>
                        {availableUser.user_type}
                      </span>
                      {availableUser.trade && (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 flex items-center gap-1">
                          <WrenchScrewdriverIcon className="h-3 w-3" />
                          {availableUser.trade}
                        </span>
                      )}
                    </div>

                    {availableUser.location && (
                      <div className="flex items-center gap-1 text-gray-600 mb-2">
                        <MapPinIcon className="h-4 w-4" />
                        <span className="text-sm">{availableUser.location}</span>
                      </div>
                    )}

                    {availableUser.bio && (
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {availableUser.bio}
                      </p>
                    )}

                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      {availableUser.phone && (
                        <div className="flex items-center gap-1">
                          <PhoneIcon className="h-4 w-4" />
                          <span>{availableUser.phone}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-1">
                        <EnvelopeIcon className="h-4 w-4" />
                        <span>{availableUser.email}</span>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center gap-2">
                      <CheckCircleSolidIcon className="h-5 w-5 text-green-600" />
                      <span className="text-sm font-medium text-green-600">
                        Available for hire
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default HireMeTab;