import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Crown, TrendingUp, Zap } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '@/lib/api';

const API_URL = API_BASE_URL;

interface Subscription {
  id: number;
  tier: 'free' | 'basic' | 'professional' | 'business' | 'enterprise';
  is_active: boolean;
  expires_at: string | null;
  price_paid: number | null;
}

const tierInfo = {
  free: {
    name: 'Free',
    color: 'gray',
    icon: '🆓',
  },
  basic: {
    name: 'Basic',
    color: 'blue',
    icon: '💼',
  },
  professional: {
    name: 'Professional',
    color: 'purple',
    icon: '⭐',
  },
  business: {
    name: 'Business',
    color: 'indigo',
    icon: '🚀',
  },
  enterprise: {
    name: 'Enterprise',
    color: 'yellow',
    icon: '👑',
  },
};

const SubscriptionStatus: React.FC = () => {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/monetization/subscriptions/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSubscription(response.data);
    } catch (error) {
      console.error('Error fetching subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 animate-pulse">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
      </div>
    );
  }

  if (!subscription) {
    return null;
  }

  const tier = tierInfo[subscription.tier];
  const isUpgradeable = subscription.tier === 'free' || subscription.tier === 'basic';

  return (
    <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 rounded-xl shadow-sm p-6 border border-blue-100 dark:border-gray-700">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{tier.icon}</span>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {tier.name} Plan
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {subscription.is_active ? 'Active' : 'Inactive'}
            </p>
          </div>
        </div>
        
        {subscription.tier !== 'free' && (
          <Crown className="h-6 w-6 text-yellow-500" />
        )}
      </div>

      {subscription.expires_at && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {subscription.is_active ? 'Renews' : 'Expired'} on{' '}
            {new Date(subscription.expires_at).toLocaleDateString()}
          </p>
        </div>
      )}

      {isUpgradeable && (
        <div className="mt-4 space-y-3">
          <Link
            to="/pricing"
            className="flex items-center justify-center gap-2 w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
          >
            <TrendingUp className="h-5 w-5" />
            Upgrade to Premium
          </Link>
          
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-white/50 dark:bg-gray-800/50 p-3 rounded-lg">
              <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 mb-1">
                <Zap className="h-4 w-4" />
                <span className="font-semibold">More Jobs</span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Post up to 20 jobs/month
              </p>
            </div>
            
            <div className="bg-white/50 dark:bg-gray-800/50 p-3 rounded-lg">
              <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 mb-1">
                <Crown className="h-4 w-4" />
                <span className="font-semibold">Priority</span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Featured in search
              </p>
            </div>
          </div>
        </div>
      )}

      {(subscription.tier === 'professional' || subscription.tier === 'business') && (
        <div className="mt-4">
          <Link
            to="/pricing"
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            View plan details →
          </Link>
        </div>
      )}

      {subscription.tier === 'enterprise' && (
        <div className="mt-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            💼 Contact your account manager for custom features and support
          </p>
        </div>
      )}
    </div>
  );
};

export default SubscriptionStatus;
