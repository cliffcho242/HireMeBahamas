import React, { useEffect, useState } from 'react';
import { Check, Star, Zap, TrendingUp, Award, Shield } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '@/lib/api';

const API_URL = API_BASE_URL;

interface PricingTier {
  tier: string;
  name: string;
  monthly_price: number;
  annual_price: number;
  features: string[];
  job_posts_per_month: number;
  recommended: boolean;
}

interface JobPackage {
  name: string;
  credits: number;
  price: number;
  price_per_post: number;
  expires_in_days: number;
  popular?: boolean;
}

interface BoostOption {
  type: string;
  name: string;
  description: string;
  price: number;
  duration_days: number;
  estimated_impressions: string;
  popular?: boolean;
}

interface PricingData {
  subscription_tiers: PricingTier[];
  job_posting_packages: JobPackage[];
  boost_options: BoostOption[];
}

const Pricing: React.FC = () => {
  const [pricingData, setPricingData] = useState<PricingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  useEffect(() => {
    fetchPricingData();
  }, []);

  const fetchPricingData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/monetization/pricing`);
      setPricingData(response.data);
    } catch (error) {
      console.error('Error fetching pricing:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!pricingData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Unable to load pricing information</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Choose Your Plan
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Unlock powerful features to accelerate your career or grow your business
        </p>
        
        {/* Billing Toggle */}
        <div className="flex items-center justify-center gap-4">
          <span className={`text-lg ${billingCycle === 'monthly' ? 'text-gray-900 font-semibold' : 'text-gray-500'}`}>
            Monthly
          </span>
          <button
            onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'annual' : 'monthly')}
            className="relative inline-flex h-8 w-14 items-center rounded-full bg-blue-600"
          >
            <span
              className={`inline-block h-6 w-6 transform rounded-full bg-white transition ${
                billingCycle === 'annual' ? 'translate-x-7' : 'translate-x-1'
              }`}
            />
          </button>
          <span className={`text-lg ${billingCycle === 'annual' ? 'text-gray-900 font-semibold' : 'text-gray-500'}`}>
            Annual
          </span>
          {pricingData.subscription_tiers.some(t => t.annual_price > 0 && t.monthly_price > 0) && (
            <span className="ml-2 bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
              Save up to 17%
            </span>
          )}
        </div>
      </div>

      {/* Subscription Tiers */}
      <div className="max-w-7xl mx-auto mb-20">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {pricingData.subscription_tiers.map((tier) => (
            <div
              key={tier.tier}
              className={`relative bg-white rounded-xl shadow-lg p-6 ${
                tier.recommended ? 'ring-2 ring-blue-600 transform scale-105' : ''
              }`}
            >
              {tier.recommended && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{tier.name}</h3>
                <div className="flex items-baseline justify-center">
                  <span className="text-4xl font-bold text-gray-900">
                    ${billingCycle === 'monthly' ? tier.monthly_price : tier.annual_price}
                  </span>
                  {tier.monthly_price > 0 && (
                    <span className="text-gray-500 ml-2">/{billingCycle === 'monthly' ? 'mo' : 'yr'}</span>
                  )}
                </div>
                {tier.name === 'Enterprise' && (
                  <p className="text-sm text-gray-500 mt-2">Custom pricing</p>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {tier.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <Check className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-gray-600">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                  tier.recommended
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                }`}
              >
                {tier.name === 'Free' ? 'Get Started' : tier.name === 'Enterprise' ? 'Contact Sales' : 'Subscribe'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Job Posting Packages */}
      <div className="max-w-7xl mx-auto mb-20">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <TrendingUp className="h-8 w-8 text-blue-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Job Posting Packages</h2>
          <p className="text-lg text-gray-600">
            Purchase job posting credits without a subscription
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {pricingData.job_posting_packages.map((pkg) => (
            <div
              key={pkg.name}
              className={`bg-white rounded-xl shadow-lg p-8 ${
                pkg.popular ? 'ring-2 ring-blue-600' : ''
              }`}
            >
              {pkg.popular && (
                <span className="inline-block bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold mb-4">
                  Best Value
                </span>
              )}
              
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{pkg.name}</h3>
              <div className="flex items-baseline mb-4">
                <span className="text-4xl font-bold text-gray-900">${pkg.price}</span>
              </div>
              
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-2" />
                  <span className="text-gray-600">{pkg.credits} job posts</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-2" />
                  <span className="text-gray-600">${pkg.price_per_post.toFixed(2)} per post</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-2" />
                  <span className="text-gray-600">Valid for {pkg.expires_in_days} days</span>
                </li>
              </ul>

              <button className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                Purchase Package
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Boost Options */}
      <div className="max-w-7xl mx-auto mb-20">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
            <Zap className="h-8 w-8 text-purple-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Boost Your Posts</h2>
          <p className="text-lg text-gray-600">
            Increase visibility and reach more potential candidates or employers
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {pricingData.boost_options.map((boost) => (
            <div
              key={boost.type}
              className={`bg-white rounded-xl shadow-lg p-8 ${
                boost.popular ? 'ring-2 ring-purple-600' : ''
              }`}
            >
              {boost.popular && (
                <span className="inline-block bg-purple-600 text-white px-3 py-1 rounded-full text-sm font-semibold mb-4">
                  Popular
                </span>
              )}
              
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{boost.name}</h3>
              <p className="text-gray-600 mb-4">{boost.description}</p>
              
              <div className="flex items-baseline mb-6">
                <span className="text-4xl font-bold text-gray-900">${boost.price}</span>
              </div>
              
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <Star className="h-5 w-5 text-yellow-500 mr-2" />
                  <span className="text-gray-600">{boost.duration_days} days duration</span>
                </li>
                <li className="flex items-center">
                  <Award className="h-5 w-5 text-yellow-500 mr-2" />
                  <span className="text-gray-600">{boost.estimated_impressions} impressions</span>
                </li>
              </ul>

              <button className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-purple-700 transition-colors">
                Boost Post
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Enterprise Section */}
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-12 text-center text-white">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 rounded-full mb-6">
            <Shield className="h-10 w-10 text-white" />
          </div>
          <h2 className="text-4xl font-bold mb-4">Enterprise Solutions</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Custom solutions for large organizations with dedicated support, API access, and unlimited features
          </p>
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <span className="bg-white/20 px-4 py-2 rounded-full">Unlimited Job Posts</span>
            <span className="bg-white/20 px-4 py-2 rounded-full">Dedicated Account Manager</span>
            <span className="bg-white/20 px-4 py-2 rounded-full">Custom Branding</span>
            <span className="bg-white/20 px-4 py-2 rounded-full">API Access</span>
            <span className="bg-white/20 px-4 py-2 rounded-full">Priority Support</span>
          </div>
          <button className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors">
            Contact Sales Team
          </button>
        </div>
      </div>

      {/* FAQ/Trust Section */}
      <div className="max-w-4xl mx-auto mt-20 text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">Trusted by Businesses Across the Bahamas</h3>
        <p className="text-gray-600 mb-8">
          All plans include secure payment processing, instant activation, and 30-day money-back guarantee
        </p>
        <div className="flex justify-center gap-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">$50k+</div>
            <div className="text-gray-600">Enterprise Revenue</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">$200k</div>
            <div className="text-gray-600">Subscription Potential</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">$100k</div>
            <div className="text-gray-600">Job Posts Revenue</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
