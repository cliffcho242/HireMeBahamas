import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import Home from 'lucide-react/dist/esm/icons/home';
import Search from 'lucide-react/dist/esm/icons/search';
import Bell from 'lucide-react/dist/esm/icons/bell';
import MessageCircle from 'lucide-react/dist/esm/icons/message-circle';
import User from 'lucide-react/dist/esm/icons/user';
import Settings from 'lucide-react/dist/esm/icons/settings';
import Plus from 'lucide-react/dist/esm/icons/plus';
import Heart from 'lucide-react/dist/esm/icons/heart';
import Share2 from 'lucide-react/dist/esm/icons/share-2';
import MessageSquare from 'lucide-react/dist/esm/icons/message-square';
import Bookmark from 'lucide-react/dist/esm/icons/bookmark';
import TrendingUp from 'lucide-react/dist/esm/icons/trending-up';
import MapPin from 'lucide-react/dist/esm/icons/map-pin';
import Clock from 'lucide-react/dist/esm/icons/clock';
import DollarSign from 'lucide-react/dist/esm/icons/dollar-sign';
import Users from 'lucide-react/dist/esm/icons/users';
import Star from 'lucide-react/dist/esm/icons/star';

interface DashboardJob {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  type: string;
  postedTime: string;
  description: string;
  skills: string[];
  likes: number;
  comments: number;
  applicants: number;
  isLiked: boolean;
  isSaved: boolean;
}

const FacebookLikeDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('feed');

  // Sample data - in real app this would come from API
  const jobPosts = [
    {
      id: 1,
      title: 'Senior Frontend Developer',
      company: 'Paradise Tech Solutions',
      location: 'Nassau, Bahamas',
      salary: '$65,000 - $85,000',
      type: 'Full-time',
      postedTime: '2 hours ago',
      description: 'Join our dynamic team building cutting-edge web applications for the Caribbean market...',
      skills: ['React', 'TypeScript', 'Node.js'],
      likes: 24,
      comments: 8,
      applicants: 45,
      isLiked: false,
      isSaved: true
    },
    {
      id: 2,
      title: 'Hotel Manager',
      company: 'Ocean Breeze Resort',
      location: 'Paradise Island, Bahamas',
      salary: '$55,000 - $70,000',
      type: 'Full-time',
      postedTime: '5 hours ago',
      description: 'Lead operations at our luxury resort with 200+ rooms. Experience in hospitality required...',
      skills: ['Management', 'Hospitality', 'Leadership'],
      likes: 18,
      comments: 12,
      applicants: 67,
      isLiked: true,
      isSaved: false
    },
    {
      id: 3,
      title: 'Marketing Specialist',
      company: 'Bahamas Tourism Board',
      location: 'Nassau, Bahamas',
      salary: '$45,000 - $60,000',
      type: 'Contract',
      postedTime: '1 day ago',
      description: 'Help promote the Bahamas as a premier tourist destination through digital marketing...',
      skills: ['Digital Marketing', 'Social Media', 'Analytics'],
      likes: 31,
      comments: 15,
      applicants: 89,
      isLiked: false,
      isSaved: false
    }
  ];

  const trending = [
    { topic: 'Remote Work Opportunities', posts: 234 },
    { topic: 'Tourism Recovery', posts: 189 },
    { topic: 'Tech Jobs Bahamas', posts: 156 },
    { topic: 'Hospitality Careers', posts: 142 },
    { topic: 'Freelancing Tips', posts: 98 }
  ];

  const suggestions = [
    { name: 'Atlantis Resort', type: 'Company', followers: '12.5k' },
    { name: 'John Smith', type: 'Recruiter', connections: 'mutual 15' },
    { name: 'Caribbean Tech Hub', type: 'Group', members: '8.2k' },
    { name: 'Maria Rodriguez', type: 'HR Manager', connections: 'mutual 8' }
  ];

  interface JobCardProps {
    job: DashboardJob;
  }

  const JobCard = ({ job }: JobCardProps) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">{job.company[0]}</span>
          </div>
          <div>
            <h3 className="font-bold text-lg text-gray-900">{job.title}</h3>
            <p className="text-gray-600">{job.company}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="p-2 hover:bg-gray-50 rounded-lg transition-colors">
            <Bookmark className={`h-5 w-5 ${job.isSaved ? 'text-blue-600 fill-current' : 'text-gray-400'}`} />
          </button>
          <button className="p-2 hover:bg-gray-50 rounded-lg transition-colors">
            <Share2 className="h-5 w-5 text-gray-400" />
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
        <div className="flex items-center space-x-1">
          <MapPin className="h-4 w-4" />
          <span>{job.location}</span>
        </div>
        <div className="flex items-center space-x-1">
          <DollarSign className="h-4 w-4" />
          <span>{job.salary}</span>
        </div>
        <div className="flex items-center space-x-1">
          <Clock className="h-4 w-4" />
          <span>{job.type}</span>
        </div>
      </div>

      <p className="text-gray-700 mb-4">{job.description}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        {job.skills.map((skill: string, index: number) => (
          <span key={index} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">
            {skill}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center space-x-6">
          <button className="flex items-center space-x-2 hover:bg-gray-50 px-3 py-2 rounded-lg transition-colors">
            <Heart className={`h-5 w-5 ${job.isLiked ? 'text-red-500 fill-current' : 'text-gray-400'}`} />
            <span className="text-sm text-gray-600">{job.likes}</span>
          </button>
          <button className="flex items-center space-x-2 hover:bg-gray-50 px-3 py-2 rounded-lg transition-colors">
            <MessageSquare className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-600">{job.comments}</span>
          </button>
          <div className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-600">{job.applicants} applicants</span>
          </div>
        </div>
        <div className="flex space-x-2">
          <button className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
            Save
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Apply Now
          </button>
        </div>
      </div>

      <div className="text-xs text-gray-500 mt-4">
        Posted {job.postedTime}
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 relative overflow-hidden">
      {/* Caribbean Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 right-32 w-40 h-40 bg-yellow-200 rounded-full opacity-10 animate-pulse"></div>
        <div className="absolute bottom-40 left-20 w-32 h-32 bg-pink-200 rounded-full opacity-15 animate-bounce" style={{animationDelay: '3s'}}></div>
        <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-orange-200 rounded-full opacity-20 animate-pulse" style={{animationDelay: '1s'}}></div>
        
        {/* Tropical wave pattern */}
        <div className="absolute bottom-0 left-0 w-full h-20 opacity-20">
          <svg viewBox="0 0 1200 120" className="w-full h-full text-cyan-300">
            <path d="M0,96L48,112C96,128 192,160 288,160C384,160 480,128 576,122.7C672,117 768,139 864,138.7C960,139 1056,117 1152,112L1200,107L1200,120L1152,120C1056,120 960,120 864,120C768,120 672,120 576,120C480,120 384,120 288,120C192,120 96,120 48,120L0,120Z" fill="currentColor"/>
          </svg>
        </div>
      </div>

      {/* Top Navigation */}
      <nav className="bg-white/95 backdrop-blur-sm shadow-lg border-b border-cyan-100/50 sticky top-0 z-50 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left Side */}
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-teal-600 rounded-lg flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold">H</span>
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-600 to-teal-700 bg-clip-text text-transparent">
                  HireMeBahamas
                </h1>
                <span className="hidden sm:inline text-xs text-cyan-600 bg-cyan-50 px-2 py-1 rounded-full">🌴 Paradise Jobs</span>
              </div>
              <div className="hidden md:flex items-center space-x-1">
                <button
                  onClick={() => setActiveTab('feed')}
                  className={`p-3 rounded-xl transition-all ${activeTab === 'feed' ? 'bg-gradient-to-r from-cyan-50 to-teal-50 text-cyan-600 shadow-md' : 'hover:bg-cyan-50/50'}`}
                >
                  <Home className="h-6 w-6" />
                </button>
                <button
                  onClick={() => setActiveTab('search')}
                  className={`p-3 rounded-xl transition-all ${activeTab === 'search' ? 'bg-gradient-to-r from-cyan-50 to-teal-50 text-cyan-600 shadow-md' : 'hover:bg-cyan-50/50'}`}
                >
                  <Search className="h-6 w-6" />
                </button>
                <button className="p-3 rounded-xl hover:bg-cyan-50/50 transition-all relative">
                  <Bell className="h-6 w-6" />
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-pink-400 to-red-500 rounded-full"></span>
                </button>
                <button className="p-3 rounded-xl hover:bg-cyan-50/50 transition-all relative">
                  <MessageCircle className="h-6 w-6" />
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full"></span>
                </button>
              </div>
            </div>

            {/* Search Bar with Caribbean Styling */}
            <div className="flex-1 max-w-lg mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-cyan-400 h-5 w-5" />
                <input
                  type="text"
                  placeholder="🔍 Search paradise jobs, resorts, companies..."
                  className="w-full pl-10 pr-4 py-2 bg-gradient-to-r from-cyan-50 to-teal-50 border-2 border-cyan-100 rounded-full focus:ring-2 focus:ring-cyan-500 focus:bg-white transition-all placeholder-cyan-600/70"
                />
              </div>
            </div>

            {/* Right Side */}
            <div className="flex items-center space-x-4">
              <button className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 to-teal-600 text-white px-4 py-2 rounded-xl hover:from-cyan-600 hover:to-teal-700 transition-all shadow-lg transform hover:scale-105">
                <Plus className="h-4 w-4" />
                <span className="hidden sm:inline">🏝️ Post Job</span>
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-teal-500 rounded-full flex items-center justify-center shadow-md">
                  <User className="h-5 w-5 text-white" />
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
                  <p className="text-xs text-cyan-600 capitalize">🌺 {user?.user_type}</p>
                </div>
                <button
                  onClick={logout}
                  className="p-2 hover:bg-cyan-50 rounded-xl transition-all"
                >
                  <Settings className="h-5 w-5 text-cyan-600" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content with Caribbean Styling */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Sidebar with Caribbean Theme */}
          <div className="lg:col-span-1">
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-cyan-100/50 p-6 mb-6">
              <h3 className="font-bold text-lg mb-4 text-cyan-700">🌴 Trending in Paradise</h3>
              <div className="space-y-3">
                {trending.map((item, index) => (
                  <div key={index} className="flex items-center justify-between hover:bg-gradient-to-r hover:from-cyan-50 hover:to-teal-50 p-3 rounded-xl cursor-pointer transition-all">
                    <div>
                      <p className="font-medium text-sm text-gray-900">#{item.topic}</p>
                      <p className="text-xs text-cyan-600">{item.posts} posts</p>
                    </div>
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-cyan-100/50 p-6">
              <h3 className="font-bold text-lg mb-4 text-cyan-700">🏝️ Island Connections</h3>
              <div className="space-y-4">
                {suggestions.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-cyan-200 to-teal-300 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-cyan-700">{item.name[0]}</span>
                      </div>
                      <div>
                        <p className="font-medium text-sm">{item.name}</p>
                        <p className="text-xs text-cyan-600">
                          {item.type} • {item.followers || item.connections || item.members}
                        </p>
                      </div>
                    </div>
                    <button className="text-cyan-600 text-sm font-medium hover:text-cyan-700 bg-cyan-50 px-3 py-1 rounded-full transition-all">
                      Connect
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Feed */}
          <div className="lg:col-span-2">
            {/* Create Post */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                  <User className="h-6 w-6 text-gray-600" />
                </div>
                <input
                  type="text"
                  placeholder="Share a job opportunity or career tip..."
                  className="flex-1 bg-gray-100 rounded-full px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                <div className="flex space-x-4">
                  <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600">
                    <Plus className="h-5 w-5" />
                    <span className="text-sm">Job Post</span>
                  </button>
                  <button className="flex items-center space-x-2 text-gray-600 hover:text-green-600">
                    <Star className="h-5 w-5" />
                    <span className="text-sm">Review</span>
                  </button>
                </div>
                <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                  Post
                </button>
              </div>
            </div>

            {/* Job Feed */}
            <div>
              {jobPosts.map((job: DashboardJob) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
              <h3 className="font-bold text-lg mb-4">Your Activity</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Profile Views</span>
                  <span className="font-medium text-blue-600">24</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Job Applications</span>
                  <span className="font-medium text-green-600">8</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Saved Jobs</span>
                  <span className="font-medium text-orange-600">12</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Network Growth</span>
                  <span className="font-medium text-purple-600">+5</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="font-bold text-lg mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg transition-colors">
                  <p className="font-medium text-sm">Update Profile</p>
                  <p className="text-xs text-gray-500">Complete your profile to get noticed</p>
                </button>
                <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg transition-colors">
                  <p className="font-medium text-sm">Upload Resume</p>
                  <p className="text-xs text-gray-500">Stand out to employers</p>
                </button>
                <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg transition-colors">
                  <p className="font-medium text-sm">Set Job Alerts</p>
                  <p className="text-xs text-gray-500">Never miss opportunities</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FacebookLikeDashboard;