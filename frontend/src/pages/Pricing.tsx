import React, { useState, useEffect } from 'react';
import { Check, X, Zap, TrendingUp, Shield, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '../config/api';

interface SubscriptionTier {
  id: number;
  name: string;
  display_name: string;
  price: number;
  annual_price: number;
  billing_period: string;
  description: string;
  features: Record<string, boolean>;
  limits: Record<string, number>;
}

const Pricing: React.FC = () => {
  const navigate = useNavigate();
  const [tiers, setTiers] = useState<SubscriptionTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly');
  const [currentTier, setCurrentTier] = useState<string>('free');

  useEffect(() => {
    fetchTiers();
    fetchCurrentSubscription();
  }, []);

  const fetchTiers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/subscriptions/tiers`);
      setTiers(response.data);
    } catch (error) {
      console.error('Failed to fetch subscription tiers:', error);
      toast.error('Failed to load pricing plans');
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentSubscription = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/subscriptions/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCurrentTier(response.data.tier);
    } catch (error) {
      console.error('Failed to fetch current subscription:', error);
    }
  };

  const handleSubscribe = async (tier: SubscriptionTier) => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      toast.error('Please log in to subscribe');
      navigate('/login');
      return;
    }

    if (tier.name === 'free') {
      toast.info('You\'re already on the free plan');
      return;
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/subscriptions/checkout`,
        {
          tier_id: tier.id,
          billing_period: billingPeriod
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      // Redirect to Stripe checkout
      window.location.href = response.data.checkout_url;
    } catch (error: any) {
      console.error('Checkout error:', error);
      toast.error(error.response?.data?.detail || 'Failed to start checkout');
    }
  };

  const formatPrice = (tier: SubscriptionTier) => {
    if (tier.price === 0) return 'Free';
    
    const price = billingPeriod === 'annual' && tier.annual_price 
      ? tier.annual_price / 12 
      : tier.price;
    
    return `$${price.toFixed(2)}`;
  };

  const formatLimits = (limits: Record<string, number>) => {
    const format = (value: number) => value === -1 ? 'Unlimited' : value.toString();
    
    return [
      `${format(limits.messages_per_month || 0)} messages/month`,
      `${format(limits.posts_per_month || 0)} posts/month`,
      `${format(limits.job_posts || 0)} job posts`,
      limits.inmails_per_month > 0 ? `${limits.inmails_per_month} InMails/month` : null,
      limits.team_members ? `${format(limits.team_members)} team members` : null,
    ].filter(Boolean);
  };

  const getTierIcon = (tierName: string) => {
    switch (tierName) {
      case 'pro': return <Zap className="w-8 h-8 text-blue-500" />;
      case 'business': return <TrendingUp className="w-8 h-8 text-purple-500" />;
      case 'enterprise': return <Shield className="w-8 h-8 text-green-500" />;
      default: return <Users className="w-8 h-8 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Find the perfect plan for your career goals
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`px-6 py-2 rounded-lg font-medium transition ${
                billingPeriod === 'monthly'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-700 border border-gray-300'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod('annual')}
              className={`px-6 py-2 rounded-lg font-medium transition ${
                billingPeriod === 'annual'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-700 border border-gray-300'
              }`}
            >
              Annual
              <span className="ml-2 text-sm">(Save 17%)</span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {tiers.map((tier) => {
            const isPopular = tier.name === 'pro';
            const isCurrent = tier.name === currentTier;
            
            return (
              <div
                key={tier.id}
                className={`rounded-lg border-2 p-6 bg-white relative ${
                  isPopular
                    ? 'border-blue-500 shadow-xl scale-105'
                    : 'border-gray-200 shadow-md'
                }`}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}

                {isCurrent && (
                  <div className="absolute -top-4 right-4">
                    <span className="bg-green-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Current Plan
                    </span>
                  </div>
                )}

                {/* Icon */}
                <div className="flex justify-center mb-4">
                  {getTierIcon(tier.name)}
                </div>

                {/* Tier Name */}
                <h3 className="text-2xl font-bold text-center mb-2">
                  {tier.display_name}
                </h3>

                {/* Description */}
                <p className="text-gray-600 text-center text-sm mb-4">
                  {tier.description}
                </p>

                {/* Price */}
                <div className="text-center mb-6">
                  <div className="text-4xl font-bold text-gray-900">
                    {formatPrice(tier)}
                  </div>
                  <div className="text-gray-600 text-sm">
                    {tier.price > 0 && `per ${billingPeriod === 'annual' ? 'month' : 'month'}`}
                  </div>
                  {billingPeriod === 'annual' && tier.annual_price && tier.price > 0 && (
                    <div className="text-green-600 text-sm mt-1">
                      Billed ${tier.annual_price}/year
                    </div>
                  )}
                </div>

                {/* Features */}
                <div className="space-y-3 mb-6">
                  {formatLimits(tier.limits).map((limit, index) => (
                    <div key={index} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-700">{limit}</span>
                    </div>
                  ))}
                  
                  {Object.entries(tier.features).map(([feature, enabled]) => {
                    if (!enabled) return null;
                    
                    const featureName = feature
                      .replace(/_/g, ' ')
                      .replace(/\b\w/g, l => l.toUpperCase());
                    
                    return (
                      <div key={feature} className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{featureName}</span>
                      </div>
                    );
                  })}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleSubscribe(tier)}
                  disabled={isCurrent}
                  className={`w-full py-3 rounded-lg font-medium transition ${
                    isCurrent
                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      : isPopular
                      ? 'bg-blue-500 hover:bg-blue-600 text-white'
                      : 'bg-gray-900 hover:bg-gray-800 text-white'
                  }`}
                >
                  {isCurrent ? 'Current Plan' : tier.name === 'free' ? 'Get Started' : `Upgrade to ${tier.display_name}`}
                </button>
              </div>
            );
          })}
        </div>

        {/* FAQ or Additional Info */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Need Help Choosing?
          </h2>
          <p className="text-gray-600 mb-8">
            Contact our sales team for a custom Enterprise solution
          </p>
          <button
            onClick={() => navigate('/contact')}
            className="px-8 py-3 bg-white border-2 border-gray-300 rounded-lg font-medium text-gray-700 hover:border-blue-500 hover:text-blue-500 transition"
          >
            Contact Sales
          </button>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
