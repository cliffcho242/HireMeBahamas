import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import {
  ChartBarIcon,
  UserGroupIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  UserIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

// Use environment variable or fall back to same-origin for serverless deployments
const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

interface UserLoginStats {
  total_users: number;
  active_users: {
    last_30_days: number;
    last_7_days: number;
  };
  never_logged_in: number;
  inactive_users_30d: number;
  authentication_methods: {
    oauth_users: number;
    password_users: number;
    distribution: Record<string, number>;
  };
  failed_login_attempts: {
    users_with_failures_30d: number;
  };
  login_activity: {
    total_logins_30d: number;
    avg_logins_per_day: number;
    avg_logins_per_week: number;
  };
  generated_at: string;
}

interface InactiveUser {
  id: number;
  email: string;
  name: string;
  last_login: string | null;
  created_at: string;
  days_since_login: number | null;
  authentication_method: string;
  is_active: boolean;
}

const UserAnalytics: React.FC = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [loadingInactive, setLoadingInactive] = useState(false);
  const [stats, setStats] = useState<UserLoginStats | null>(null);
  const [inactiveUsers, setInactiveUsers] = useState<InactiveUser[]>([]);
  const [inactiveDays, setInactiveDays] = useState(30);
  const [showInactiveUsers, setShowInactiveUsers] = useState(false);

  useEffect(() => {
    // Check if user is admin
    if (!user?.is_admin && user?.user_type !== 'admin') {
      toast.error('Admin access required');
      navigate('/');
      return;
    }

    fetchAnalytics();
  }, [user, navigate]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/analytics/user-logins`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const fetchInactiveUsers = async () => {
    setLoadingInactive(true);
    try {
      const response = await axios.get(
        `${API_URL}/api/analytics/inactive-users?days=${inactiveDays}&limit=100`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setInactiveUsers(response.data.users);
      setShowInactiveUsers(true);
    } catch (error) {
      console.error('Failed to fetch inactive users:', error);
      toast.error('Failed to load inactive users');
    } finally {
      setLoadingInactive(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatAuthMethod = (method: string) => {
    if (method === 'password') return 'Password';
    if (method.startsWith('oauth_')) {
      const provider = method.replace('oauth_', '');
      return `OAuth (${provider.charAt(0).toUpperCase() + provider.slice(1)})`;
    }
    return method;
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <ArrowPathIcon className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const activityRate = stats.total_users > 0
    ? Math.round((stats.active_users.last_30_days / stats.total_users) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                <ChartBarIcon className="w-8 h-8 text-blue-600" />
                User Login Analytics
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Monitor user activity and identify login issues
              </p>
            </div>
            <button
              onClick={fetchAnalytics}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <ArrowPathIcon className="w-5 h-5" />
              Refresh
            </button>
          </div>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Users */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Users</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats.total_users}
                </p>
              </div>
              <UserGroupIcon className="w-12 h-12 text-blue-600 opacity-80" />
            </div>
          </div>

          {/* Active Users (30d) */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Active (30 days)</p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-500 mt-2">
                  {stats.active_users.last_30_days}
                </p>
                <p className="text-xs text-gray-500 mt-1">{activityRate}% activity rate</p>
              </div>
              <ShieldCheckIcon className="w-12 h-12 text-green-600 opacity-80" />
            </div>
          </div>

          {/* Never Logged In */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Never Logged In</p>
                <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-500 mt-2">
                  {stats.never_logged_in}
                </p>
                <p className="text-xs text-gray-500 mt-1">Registered but inactive</p>
              </div>
              <ExclamationTriangleIcon className="w-12 h-12 text-yellow-600 opacity-80" />
            </div>
          </div>

          {/* Inactive Users */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Inactive (30+ days)</p>
                <p className="text-3xl font-bold text-red-600 dark:text-red-500 mt-2">
                  {stats.inactive_users_30d}
                </p>
                <p className="text-xs text-gray-500 mt-1">No recent activity</p>
              </div>
              <ClockIcon className="w-12 h-12 text-red-600 opacity-80" />
            </div>
          </div>
        </div>

        {/* Authentication Methods */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Authentication Methods
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">OAuth Users</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {stats.authentication_methods.oauth_users}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${(stats.authentication_methods.oauth_users / stats.total_users) * 100}%`
                    }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Password Users</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {stats.authentication_methods.password_users}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${(stats.authentication_methods.password_users / stats.total_users) * 100}%`
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Login Activity (30 days)
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Total Logins</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {stats.login_activity.total_logins_30d}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Avg per Day</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {stats.login_activity.avg_logins_per_day}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Avg per Week</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {stats.login_activity.avg_logins_per_week}
                </span>
              </div>
              <div className="flex justify-between items-center border-t border-gray-200 dark:border-gray-700 pt-3">
                <span className="text-sm text-gray-600 dark:text-gray-400">Failed Attempts</span>
                <span className="font-semibold text-red-600 dark:text-red-500">
                  {stats.failed_login_attempts.users_with_failures_30d} users
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Inactive Users Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Inactive Users
            </h3>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600 dark:text-gray-400">
                  Days:
                </label>
                <select
                  value={inactiveDays}
                  onChange={(e) => setInactiveDays(Number(e.target.value))}
                  className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value={7}>7</option>
                  <option value={14}>14</option>
                  <option value={30}>30</option>
                  <option value={60}>60</option>
                  <option value={90}>90</option>
                </select>
              </div>
              <button
                onClick={fetchInactiveUsers}
                disabled={loadingInactive}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loadingInactive ? 'Loading...' : 'Load Inactive Users'}
              </button>
            </div>
          </div>

          {showInactiveUsers && inactiveUsers.length > 0 && (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-900">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Last Login
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Days Inactive
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Auth Method
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {inactiveUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <UserIcon className="w-5 h-5 text-gray-400 mr-2" />
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {user.name}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {user.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {formatDate(user.last_login)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {user.days_since_login !== null ? `${user.days_since_login} days` : 'Never'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {formatAuthMethod(user.authentication_method)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.is_active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {showInactiveUsers && inactiveUsers.length === 0 && (
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">
              No inactive users found for the selected threshold.
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
          Last updated: {new Date(stats.generated_at).toLocaleString()}
        </div>
      </div>
    </div>
  );
};

export default UserAnalytics;
