import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { Job } from '../types/job';
import JobCard from '../components/JobCard';
import PostFeed from '../components/PostFeed';
import SmartSearchBar from '../components/SmartSearchBar';
import HireMeTab from '../components/HireMeTab';
import { smartSearch, JobSearchResult } from '../utils/searchAlgorithm';
import {
  MapPinIcon,
  AdjustmentsHorizontalIcon,
  BriefcaseIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

const Jobs: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<JobSearchResult[]>([]);
  const [locationFilter, setLocationFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [activeTab, setActiveTab] = useState<'feed' | 'jobs' | 'hireme'>('feed');
  const { user } = useAuth();

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await api.get('/api/jobs');
      setJobs(response.data);
      setSearchResults(response.data.map((job: Job) => ({
        ...job,
        relevanceScore: 100,
        matchedFields: []
      })));
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSmartSearch = (query: string, filters?: { location?: string; category?: string }) => {
    setSearchTerm(query);
    
    // Apply smart search algorithm
    const results = smartSearch(jobs, query, {
      category: filters?.category || categoryFilter,
      location: filters?.location || locationFilter,
      minRelevance: 30
    });
    
    setSearchResults(results);
    
    // Update filters if detected
    if (filters?.location) setLocationFilter(filters.location);
    if (filters?.category) setCategoryFilter(filters.category);
  };

  const filteredJobs = searchResults.length > 0 ? searchResults : jobs.map(job => ({
    ...job,
    relevanceScore: 100,
    matchedFields: []
  }));

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">HB</span>
                </div>
                <span className="text-xl font-bold text-gray-900">HireMeBahamas</span>
              </Link>
            </div>

            {/* Smart Search Bar */}
            <div className="flex-1 max-w-2xl mx-8">
              <SmartSearchBar
                onSearch={handleSmartSearch}
                placeholder="🔍 Find plumbers, electricians, chefs, hotels, or any service..."
                showPopularSearches={true}
              />
            </div>

            <div className="flex items-center space-x-4">
              <Link
                to="/post-job"
                className="bg-blue-600 text-white px-4 py-2 rounded-full font-semibold hover:bg-blue-700 transition-colors"
              >
                Post a Job
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Tab Navigation */}
        <div className="flex items-center justify-center mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-1">
            <button
              onClick={() => setActiveTab('feed')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'feed'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🏠 Feed
            </button>
            <button
              onClick={() => setActiveTab('hireme')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'hireme'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              � HireMe
            </button>
          </div>
        </div>

        {activeTab === 'feed' ? (
          <div className="max-w-2xl mx-auto">
            {/* Welcome Banner */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 mb-6 text-white"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Welcome to HireMeBahamas!</h2>
                  <p className="text-blue-100 mb-4">Connect with professionals, discover opportunities, and build your career in the Bahamas</p>
                  <div className="flex space-x-4">
                    <Link
                      to="/jobs"
                      onClick={() => setActiveTab('jobs')}
                      className="bg-white text-blue-600 px-4 py-2 rounded-full font-semibold hover:bg-gray-50 transition-colors"
                    >
                      Find Jobs
                    </Link>
                    {!user && (
                      <Link
                        to="/register"
                        className="border-2 border-white text-white px-4 py-2 rounded-full font-semibold hover:bg-white hover:text-blue-600 transition-colors"
                      >
                        Join Now
                      </Link>
                    )}
                  </div>
                </div>
                <div className="hidden md:block">
                  <SparklesIcon className="w-16 h-16 text-white opacity-20" />
                </div>
              </div>
            </motion.div>

            <PostFeed />
          </div>
            ) : activeTab === 'hireme' ? (
          <HireMeTab />
        ) : (
          <div>
            {/* Filters */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="relative">
                  <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Location"
                    value={locationFilter}
                    onChange={(e) => setLocationFilter(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="relative">
                  <BriefcaseIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Category"
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="flex items-center">
                  <button className="w-full bg-gray-100 text-gray-700 px-4 py-3 rounded-xl hover:bg-gray-200 transition-colors flex items-center justify-center">
                    <AdjustmentsHorizontalIcon className="w-5 h-5 mr-2" />
                    More Filters
                  </button>
                </div>
              </div>
            </div>

            {/* Job Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">{jobs.length}</div>
                <div className="text-gray-600">Active Jobs</div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">24</div>
                <div className="text-gray-600">Companies Hiring</div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">156</div>
                <div className="text-gray-600">New This Week</div>
              </div>
            </div>

            {/* Search Results Summary */}
            {searchTerm && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <SparklesIcon className="h-6 w-6 text-blue-600" />
                    <div>
                      <p className="text-sm font-semibold text-gray-900">
                        Found {filteredJobs.length} {filteredJobs.length === 1 ? 'result' : 'results'} for "{searchTerm}"
                      </p>
                      {(categoryFilter || locationFilter) && (
                        <p className="text-xs text-gray-600 mt-1">
                          {categoryFilter && <span>Category: {categoryFilter}</span>}
                          {categoryFilter && locationFilter && <span> • </span>}
                          {locationFilter && <span>Location: {locationFilter}</span>}
                        </p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setSearchTerm('');
                      setCategoryFilter('');
                      setLocationFilter('');
                      setSearchResults(jobs.map(job => ({ ...job, relevanceScore: 100, matchedFields: [] })));
                    }}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Clear
                  </button>
                </div>
              </motion.div>
            )}

            {/* Jobs Grid */}
            {filteredJobs.length === 0 ? (
              <div className="text-center py-12">
                <BriefcaseIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No jobs found</h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm ? `No results for "${searchTerm}"` : 'Try adjusting your search criteria'}
                </p>
                {searchTerm && (
                  <button
                    onClick={() => {
                      setSearchTerm('');
                      setCategoryFilter('');
                      setLocationFilter('');
                      handleSmartSearch('');
                    }}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Clear search and show all jobs
                  </button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredJobs.map((job, index) => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="relative"
                  >
                    {/* Relevance Score Badge (only show if search is active) */}
                    {Boolean(searchTerm && job.relevanceScore && job.relevanceScore < 100) && (
                      <div className="absolute -top-2 -right-2 z-10">
                        <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg flex items-center gap-1">
                          <SparklesIcon className="h-3 w-3" />
                          {Math.round(job.relevanceScore)}% Match
                        </div>
                      </div>
                    )}
                    
                    {/* Matched Fields Indicator */}
                    {Boolean(searchTerm && job.matchedFields && job.matchedFields.length > 0) && (
                      <div className="absolute -top-2 -left-2 z-10">
                        <div className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-[10px] font-semibold">
                          {job.matchedFields.join(', ')}
                        </div>
                      </div>
                    )}
                    
                    <JobCard job={job as any} />
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Jobs;