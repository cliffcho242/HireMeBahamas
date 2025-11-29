import React, { useState, Suspense, lazy } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  UserGroupIcon,
  BriefcaseIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  PhotoIcon,
  VideoCameraIcon,
  CalendarDaysIcon,
  TvIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  BookmarkIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { HomeIcon as HomeIconSolid, ChatBubbleLeftRightIcon as MessagesIconSolid } from '@heroicons/react/24/solid';

// Lazy load heavy components for better initial load time
const PostFeed = lazy(() => import('../components/PostFeed'));
const Stories = lazy(() => import('../components/Stories'));
const CreatePostModal = lazy(() => import('../components/CreatePostModal'));
const CreateEventModal = lazy(() => import('../components/CreateEventModal'));
const EventReminderSystem = lazy(() => import('../components/EventReminderSystem'));
const FriendsOnline = lazy(() => import('../components/FriendsOnline'));
const Notifications = lazy(() => import('../components/Notifications'));
const Messages = lazy(() => import('../components/Messages'));

// Loading fallback components
const StoriesLoader = () => (
  <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
    <div className="flex space-x-4 overflow-x-auto pb-2">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="flex-shrink-0 w-20 h-28 bg-gray-200 rounded-lg animate-pulse"></div>
      ))}
    </div>
  </div>
);

const PostFeedLoader = () => (
  <div className="space-y-4">
    {[1, 2].map((i) => (
      <div key={i} className="bg-white rounded-lg shadow-sm p-4">
        <div className="flex space-x-3 mb-4">
          <div className="w-10 h-10 bg-gray-200 rounded-full animate-pulse"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-2 animate-pulse"></div>
            <div className="h-3 bg-gray-200 rounded w-1/4 animate-pulse"></div>
          </div>
        </div>
        <div className="h-4 bg-gray-200 rounded w-full mb-2 animate-pulse"></div>
        <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse"></div>
      </div>
    ))}
  </div>
);

const SidebarLoader = () => (
  <div className="bg-white rounded-lg shadow-sm p-4">
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-24 animate-pulse"></div>
        </div>
      ))}
    </div>
  </div>
);

const IconButtonLoader = () => (
  <div className="w-9 h-9 bg-gray-200 rounded-full animate-pulse"></div>
);

const Home: React.FC = () => {
  const { user } = useAuth();
  const [isCreatePostModalOpen, setIsCreatePostModalOpen] = useState(false);
  const [isCreateEventModalOpen, setIsCreateEventModalOpen] = useState(false);
  const [refreshPosts, setRefreshPosts] = useState(0);

  const sidebarItems = [
    { icon: HomeIconSolid, label: 'Home', href: '/', active: true, badge: null },
    { icon: UserGroupIcon, label: 'Friends', href: '/friends', active: false, badge: '12' },
    { icon: BriefcaseIcon, label: 'Jobs', href: '/jobs', active: false, badge: '5 New' },
    { icon: MessagesIconSolid, label: 'Messages', href: '/messages', active: false, badge: '3' },
    { icon: TvIcon, label: 'Videos', href: '/videos', active: false, badge: null },
    { icon: BookmarkIcon, label: 'Saved', href: '/saved', active: false, badge: null },
  ];

  const quickLinks = [
    { icon: ClockIcon, label: 'Memories', href: '/memories', color: 'text-blue-600' },
    { icon: UserCircleIcon, label: 'Profile', href: '/profile', color: 'text-purple-600' },
    { icon: Cog6ToothIcon, label: 'Settings', href: '/settings', color: 'text-gray-600' },
  ];

  const createPostOptions = [
    { icon: PhotoIcon, label: 'Photo/Video', color: 'text-green-600', bgColor: 'bg-green-50' },
    { icon: VideoCameraIcon, label: 'Live Video', color: 'text-red-600', bgColor: 'bg-red-50' },
    { icon: CalendarDaysIcon, label: 'Event', color: 'text-blue-600', bgColor: 'bg-blue-50' },
  ];

  return (
    <div className="min-h-screen min-h-[100dvh] bg-gray-100">
      {/* Top Navigation Bar - Responsive */}
      <div className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 h-12 sm:h-14 flex items-center justify-between">
          {/* Left Section - Logo and Search */}
          <div className="flex items-center space-x-2 sm:space-x-4 flex-1">
            <Link to="/" className="flex items-center space-x-1 sm:space-x-2">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-sm sm:text-base">HB</span>
              </div>
              <span className="text-lg sm:text-xl font-bold text-gray-900 hidden sm:block truncate">HireMeBahamas</span>
            </Link>

            <div className="hidden md:block relative flex-1 max-w-xs">
              <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search HireMeBahamas"
                className="pl-10 pr-4 py-2 w-full bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>
          </div>

          {/* Center Section - Main Navigation with Icons - Hidden on mobile */}
          <div className="hidden md:flex items-center space-x-1 mx-4">
            <Link 
              to="/" 
              className="relative p-2 lg:p-3 rounded-xl bg-gradient-to-r from-blue-50 to-blue-100 text-blue-600 hover:from-blue-100 hover:to-blue-200 transition-all duration-200 shadow-sm"
              title="Home"
            >
              <HomeIconSolid className="w-6 h-6 lg:w-7 lg:h-7" />
              <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-8 lg:w-10 h-1 bg-blue-600 rounded-full"></div>
            </Link>
            <Link 
              to="/friends" 
              className="relative p-2 lg:p-3 rounded-xl hover:bg-gray-100 transition-all duration-200 group"
              title="Friends"
            >
              <UserGroupIcon className="w-6 h-6 lg:w-7 lg:h-7 text-gray-600 group-hover:text-blue-600 transition-colors" />
              <span className="absolute top-0 right-0 w-4 h-4 lg:w-5 lg:h-5 bg-red-500 text-white text-[10px] lg:text-xs font-bold rounded-full flex items-center justify-center">
                3
              </span>
            </Link>
            <Link 
              to="/jobs" 
              className="relative p-3 rounded-xl hover:bg-gray-100 transition-all duration-200 group"
              title="Jobs"
            >
              <BriefcaseIcon className="w-7 h-7 text-gray-600 group-hover:text-blue-600 transition-colors" />
              <span className="absolute top-1 right-1 w-5 h-5 bg-green-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                5
              </span>
            </Link>
          </div>

          {/* Right Section - User Actions with Enhanced Icons */}
          <div className="flex items-center space-x-2">
            <button 
              onClick={() => setIsCreatePostModalOpen(true)}
              className="p-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 shadow-md hover:shadow-lg"
              title="Create new post"
            >
              <PlusIcon className="w-5 h-5" />
            </button>
            <Suspense fallback={<IconButtonLoader />}>
              <Messages />
            </Suspense>
            <Suspense fallback={<IconButtonLoader />}>
              <Notifications />
            </Suspense>

            {user && (
              <div className="flex items-center space-x-2 ml-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-semibold text-sm">
                    {user.first_name?.[0]}{user.last_name?.[0]}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content - Responsive Grid */}
      <div className="max-w-7xl mx-auto px-2 sm:px-4 py-3 sm:py-4">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 sm:gap-6">
          {/* Left Sidebar - Hidden on mobile and tablet */}
          <div className="hidden lg:block lg:col-span-1">
            <div className="space-y-4">
              {/* User Profile Card */}
              {user && (
                <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                  <Link to="/profile" className="block hover:bg-gray-50 transition-colors">
                    <div className="relative h-16 lg:h-20 bg-gradient-to-r from-blue-500 to-purple-600"></div>
                    <div className="px-3 lg:px-4 pb-3 lg:pb-4 -mt-6 lg:-mt-8">
                      <div className="w-12 h-12 lg:w-16 lg:h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center border-4 border-white shadow-lg">
                        <span className="text-white font-bold text-base lg:text-xl">
                          {user.first_name?.[0]}{user.last_name?.[0]}
                        </span>
                      </div>
                      <h3 className="mt-2 font-semibold text-gray-900 text-base lg:text-lg truncate">
                        {user.first_name} {user.last_name}
                      </h3>
                      <p className="text-xs lg:text-sm text-blue-600 font-medium truncate">
                        @{user.username || user.email?.split('@')[0] || `${user.first_name?.toLowerCase()}${user.last_name?.toLowerCase()}`}
                      </p>
                      <p className="text-xs lg:text-sm text-gray-700 mt-1 font-medium truncate">
                        {user.occupation || user.company_name || user.user_type?.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                      </p>
                    </div>
                  </Link>
                </div>
              )}

              {/* Main Navigation */}
              <div className="bg-white rounded-xl shadow-sm p-2 lg:p-3 sticky top-20">
                <div className="space-y-1">
                  {sidebarItems.map((item) => (
                    <Link
                      key={item.label}
                      to={item.href}
                      className={`flex items-center justify-between p-2 lg:p-3 rounded-lg transition-all duration-200 ${
                        item.active
                          ? 'bg-gradient-to-r from-blue-50 to-purple-50 text-blue-600 shadow-sm'
                          : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className="flex items-center space-x-2 lg:space-x-3">
                        <item.icon className={`w-5 h-5 lg:w-6 lg:h-6 ${item.active ? 'text-blue-600' : ''}`} />
                        <span className="font-medium text-sm lg:text-base">{item.label}</span>
                      </div>
                      {item.badge && (
                        <span className={`px-1.5 lg:px-2 py-0.5 text-[10px] lg:text-xs font-semibold rounded-full ${
                          item.active 
                            ? 'bg-blue-600 text-white' 
                            : 'bg-red-500 text-white'
                        }`}>
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  ))}
                </div>

                {/* Quick Links Section */}
                <div className="mt-3 lg:mt-4 pt-3 lg:pt-4 border-t border-gray-100">
                  <h4 className="px-2 lg:px-3 text-[10px] lg:text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                    Quick Access
                  </h4>
                  <div className="space-y-1">
                    {quickLinks.map((link) => (
                      <Link
                        key={link.label}
                        to={link.href}
                        className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors text-gray-700"
                      >
                        <link.icon className={`w-5 h-5 ${link.color}`} />
                        <span className="text-sm font-medium">{link.label}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Feed - Full width on mobile, centered on desktop */}
          <div className="lg:col-span-2 w-full">
            {/* Stories - Responsive */}
            <div className="mb-3 sm:mb-4">
              <Suspense fallback={<StoriesLoader />}>
                <Stories />
              </Suspense>
            </div>

            {/* Create Post Card - Responsive */}
            {user && (
              <div className="bg-white rounded-lg sm:rounded-xl shadow-sm p-3 sm:p-4 mb-3 sm:mb-4">
                <div className="flex space-x-2 sm:space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold text-sm sm:text-base">
                        {user.first_name?.[0]}{user.last_name?.[0]}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <button
                      onClick={() => setIsCreatePostModalOpen(true)}
                      className="w-full text-left p-2 sm:p-3 bg-gray-100 rounded-full text-gray-500 hover:bg-gray-200 transition-colors text-sm sm:text-base truncate"
                    >
                      What's on your mind, {user.first_name}?
                    </button>
                  </div>
                </div>

                <div className="flex justify-between items-center mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-gray-100 gap-1 sm:gap-2">
                  {createPostOptions.map((option) => (
                    <button
                      key={option.label}
                      onClick={() => {
                        if (option.label === 'Event') {
                          setIsCreateEventModalOpen(true);
                        } else {
                          setIsCreatePostModalOpen(true);
                        }
                      }}
                      className={`flex items-center space-x-2 flex-1 justify-center p-3 rounded-lg ${option.bgColor} hover:opacity-80 transition-all duration-200`}
                    >
                      <option.icon className={`w-5 h-5 ${option.color}`} />
                      <span className={`text-sm font-medium ${option.color} hidden sm:block`}>{option.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Posts Feed */}
            <Suspense fallback={<PostFeedLoader />}>
              <PostFeed key={refreshPosts} />
            </Suspense>
          </div>

          {/* Right Sidebar */}
          <div className="hidden xl:block xl:col-span-1">
            <div className="space-y-4 sticky top-20">
              {/* Friends Online */}
              <Suspense fallback={<SidebarLoader />}>
                <FriendsOnline />
              </Suspense>

              {/* Sponsored/Ads Section */}
              <div className="bg-white rounded-lg shadow-sm p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Sponsored</h3>
                <div className="space-y-4">
                  <div className="border border-gray-200 rounded-lg p-3">
                    <div className="w-full h-32 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg mb-3 flex items-center justify-center">
                      <span className="text-gray-500 text-sm">Ad Space</span>
                    </div>
                    <h4 className="font-medium text-gray-900 text-sm">Find Your Dream Job</h4>
                    <p className="text-xs text-gray-600">Connect with top employers in the Bahamas</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Create Post Modal */}
      <Suspense fallback={null}>
        <CreatePostModal
          isOpen={isCreatePostModalOpen}
          onClose={() => setIsCreatePostModalOpen(false)}
          onPostCreated={() => setRefreshPosts(prev => prev + 1)}
        />
      </Suspense>

      {/* Create Event Modal */}
      <Suspense fallback={null}>
        <CreateEventModal
          isOpen={isCreateEventModalOpen}
          onClose={() => setIsCreateEventModalOpen(false)}
          onEventCreated={() => {
            setRefreshPosts(prev => prev + 1);
            // Additional logic for event creation can be added here
          }}
        />
      </Suspense>

      {/* Event Reminder System - Shows notifications for upcoming video calls */}
      <Suspense fallback={null}>
        <EventReminderSystem events={[]} />
      </Suspense>
    </div>
  );
};

export default Home;
