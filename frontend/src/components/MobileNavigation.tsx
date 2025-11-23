import React, { useState, useEffect, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  UserGroupIcon,
  BriefcaseIcon,
  ChatBubbleLeftRightIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  UserGroupIcon as UserGroupIconSolid,
  BriefcaseIcon as BriefcaseIconSolid,
  ChatBubbleLeftRightIcon as ChatIconSolid,
} from '@heroicons/react/24/solid';
import { useAuth } from '../contexts/AuthContext';
import { notificationsAPI } from '../services/api';

interface MobileNavigationProps {
  className?: string;
}

const MobileNavigation: React.FC<MobileNavigationProps> = ({ className = '' }) => {
  const location = useLocation();
  const { user } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState(0);

  const fetchUnreadCount = useCallback(async () => {
    try {
      const response = await notificationsAPI.getUnreadCount();
      setUnreadNotifications(response.unread_count || 0);
    } catch (error) {
      console.error('Error fetching unread count:', error);
      setUnreadNotifications(0);
    }
  }, []);

  // Fetch unread count on mount and periodically
  useEffect(() => {
    // Use async IIFE to handle async call properly
    (async () => {
      await fetchUnreadCount();
    })();
    
    // Set up polling interval
    const interval = setInterval(() => {
      (async () => {
        await fetchUnreadCount();
      })();
    }, 30000); // Poll every 30 seconds
    
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  const navItems = [
    { path: '/', icon: HomeIcon, iconSolid: HomeIconSolid, label: 'Home', badge: null },
    { path: '/friends', icon: UserGroupIcon, iconSolid: UserGroupIconSolid, label: 'Friends', badge: null },
    { path: '/jobs', icon: BriefcaseIcon, iconSolid: BriefcaseIconSolid, label: 'Jobs', badge: null },
    { path: '/messages', icon: ChatBubbleLeftRightIcon, iconSolid: ChatIconSolid, label: 'Messages', badge: null },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <>
      {/* Mobile Top Bar */}
      <div className={`md:hidden fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50 ${className}`}>
        <div className="flex items-center justify-between px-4 h-14 safe-area-inset">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">HB</span>
            </div>
            <span className="text-xl font-bold text-gray-900">HireMeBahamas</span>
          </Link>

          {/* Right Actions */}
          <div className="flex items-center space-x-2">
            <button
              className="p-2 rounded-full hover:bg-gray-100 active:bg-gray-200 touch-manipulation tap-highlight-transparent"
              aria-label="Search"
            >
              <MagnifyingGlassIcon className="w-6 h-6 text-gray-600" />
            </button>
            <button
              className="p-2 rounded-full hover:bg-gray-100 active:bg-gray-200 relative touch-manipulation tap-highlight-transparent"
              aria-label="Notifications"
            >
              <BellIcon className="w-6 h-6 text-gray-600" />
              {unreadNotifications > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              )}
            </button>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-full hover:bg-gray-100 active:bg-gray-200 touch-manipulation tap-highlight-transparent"
              aria-label="Menu"
            >
              {isMenuOpen ? (
                <XMarkIcon className="w-6 h-6 text-gray-600" />
              ) : (
                <Bars3Icon className="w-6 h-6 text-gray-600" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40 animate-fade-in"
          onClick={() => setIsMenuOpen(false)}
        >
          <div 
            className="absolute right-0 top-14 bottom-0 w-64 bg-white shadow-xl animate-slide-in-right"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 space-y-2">
              {user && (
                <Link
                  to="/profile"
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100 active:bg-gray-200"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold text-lg">
                      {user.first_name?.[0]}{user.last_name?.[0]}
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">{user.first_name} {user.last_name}</p>
                    <p className="text-sm text-blue-600 font-medium">
                      @{user.username || user.email?.split('@')[0] || `${user.first_name?.toLowerCase()}${user.last_name?.toLowerCase()}`}
                    </p>
                    <p className="text-xs text-gray-600">
                      {user.occupation || user.company_name || user.user_type?.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </p>
                  </div>
                </Link>
              )}
              
              <div className="border-t border-gray-200 my-2"></div>
              
              <Link to="/saved" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100" onClick={() => setIsMenuOpen(false)}>
                <span className="text-sm font-medium text-gray-700">Saved Items</span>
              </Link>
              <Link to="/settings" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100" onClick={() => setIsMenuOpen(false)}>
                <span className="text-sm font-medium text-gray-700">Settings</span>
              </Link>
              <Link to="/help" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100" onClick={() => setIsMenuOpen(false)}>
                <span className="text-sm font-medium text-gray-700">Help & Support</span>
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Navigation Bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 safe-area-inset">
        <div className="grid grid-cols-4 gap-1 px-2 py-1">
          {navItems.map((item) => {
            const Icon = isActive(item.path) ? item.iconSolid : item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center justify-center py-2 px-3 rounded-lg transition-colors touch-manipulation tap-highlight-transparent relative min-h-touch ${
                  isActive(item.path)
                    ? 'text-blue-600'
                    : 'text-gray-600 active:bg-gray-100'
                }`}
              >
                <Icon className="w-6 h-6 mb-1" />
                <span className="text-xs font-medium">{item.label}</span>
                {item.badge !== null && item.badge > 0 && (
                  <span className="absolute top-1 right-2 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                    {item.badge}
                  </span>
                )}
                {isActive(item.path) && (
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-12 h-1 bg-blue-600 rounded-b-full"></div>
                )}
              </Link>
            );
          })}
        </div>
      </div>
    </>
  );
};

export default MobileNavigation;
