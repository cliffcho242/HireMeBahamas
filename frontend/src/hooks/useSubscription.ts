import { useState, useEffect } from 'react';
import api from '../config/axios';
import toast from 'react-hot-toast';

export interface SubscriptionPlan {
  plan: string;
  status: string;
  end_date: string | null;
  is_pro: boolean;
}

export function useSubscription() {
  const [subscription, setSubscription] = useState<SubscriptionPlan | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchSubscription = async () => {
    try {
      const response = await api.get('/api/subscriptions/current');
      setSubscription(response.data);
    } catch (error) {
      console.error('Error fetching subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscription();
  }, []);

  const requirePro = (featureName: string = 'This feature') => {
    if (!subscription?.is_pro) {
      toast.error(`${featureName} requires a Pro subscription or higher`, {
        duration: 5000,
        icon: '⭐',
      });
      return false;
    }
    return true;
  };

  const requireBusiness = (featureName: string = 'This feature') => {
    if (!subscription || !['business', 'enterprise'].includes(subscription.plan)) {
      toast.error(`${featureName} requires a Business subscription or higher`, {
        duration: 5000,
        icon: '💼',
      });
      return false;
    }
    return true;
  };

  const requireEnterprise = (featureName: string = 'This feature') => {
    if (subscription?.plan !== 'enterprise') {
      toast.error(`${featureName} requires an Enterprise subscription`, {
        duration: 5000,
        icon: '🏢',
      });
      return false;
    }
    return true;
  };

  return {
    subscription,
    loading,
    isPro: subscription?.is_pro || false,
    isBusiness: subscription ? ['business', 'enterprise'].includes(subscription.plan) : false,
    isEnterprise: subscription?.plan === 'enterprise',
    requirePro,
    requireBusiness,
    requireEnterprise,
    refetch: fetchSubscription,
  };
}
