import { useState, useEffect } from 'react';
import { Check, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';

interface PlanFeature {
  name: string;
  price: number | null;
  price_display: string;
  billing_period: string | null;
  features: string[];
}

interface SubscriptionPlans {
  free: PlanFeature;
  pro: PlanFeature;
  business: PlanFeature;
  enterprise: PlanFeature;
}

interface CurrentSubscription {
  plan: string;
  status: string;
  end_date: string | null;
  is_pro: boolean;
}

export default function Subscriptions() {
  const [plans, setPlans] = useState<SubscriptionPlans | null>(null);
  const [currentSubscription, setCurrentSubscription] = useState<CurrentSubscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await api.get('/api/subscriptions/plans');
      setPlans(response.data.plans);
    } catch (error) {
      console.error('Error fetching plans:', error);
      toast.error('Failed to load subscription plans');
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const response = await api.get('/api/subscriptions/current');
      setCurrentSubscription(response.data);
    } catch (error) {
      console.error('Error fetching current subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (plan: string) => {
    if (plan === 'enterprise') {
      toast.success('Please contact sales for Enterprise plans');
      return;
    }

    setUpgrading(plan);
    try {
      const response = await api.post('/api/subscriptions/upgrade', { plan });
      toast.success(response.data.message);
      await fetchCurrentSubscription();
    } catch (error: any) {
      // Provide specific error messages based on error status
      if (error.response?.status === 400) {
        const detail = error.response.data?.detail || '';
        if (detail.includes('already subscribed')) {
          toast.error('You are already on this plan');
        } else if (detail.includes('Invalid plan')) {
          toast.error('Invalid subscription plan selected');
        } else {
          toast.error(detail || 'Cannot upgrade to this plan');
        }
      } else if (error.response?.status === 402) {
        toast.error('Payment required. Please update your payment method.');
      } else if (error.response?.status === 401) {
        toast.error('Please log in to upgrade your subscription');
      } else {
        toast.error('Failed to upgrade subscription. Please try again later.');
      }
    } finally {
      setUpgrading(null);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription?')) {
      return;
    }

    try {
      const response = await api.post('/api/subscriptions/cancel');
      toast.success(response.data.message);
      await fetchCurrentSubscription();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to cancel subscription';
      toast.error(message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const planOrder: Array<keyof SubscriptionPlans> = ['free', 'pro', 'business', 'enterprise'];

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600">
            Upgrade to unlock premium features and grow your career
          </p>
        </div>

        {/* Current Plan Alert */}
        {currentSubscription && currentSubscription.plan !== 'free' && (
          <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-blue-800">
                <strong>Current Plan:</strong> {plans?.[currentSubscription.plan as keyof SubscriptionPlans]?.name || currentSubscription.plan}
                {currentSubscription.end_date && (
                  <> - Renews on {new Date(currentSubscription.end_date).toLocaleDateString()}</>
                )}
              </p>
              <button
                onClick={handleCancel}
                className="text-sm text-blue-600 hover:text-blue-800 underline mt-2"
              >
                Cancel subscription
              </button>
            </div>
          </div>
        )}

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {plans && planOrder.map((planKey) => {
            const plan = plans[planKey];
            const isCurrentPlan = currentSubscription?.plan === planKey;
            const isPro = planKey === 'pro';
            const isBusiness = planKey === 'business';

            return (
              <div
                key={planKey}
                className={`bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 ${
                  isPro ? 'ring-2 ring-blue-500' : ''
                }`}
              >
                {isPro && (
                  <div className="bg-blue-500 text-white text-center py-2 text-sm font-semibold">
                    MOST POPULAR
                  </div>
                )}
                {isBusiness && (
                  <div className="bg-green-500 text-white text-center py-2 text-sm font-semibold">
                    BEST VALUE
                  </div>
                )}
                
                <div className="p-6">
                  {/* Plan Header */}
                  <div className="mb-6">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      {plan.name}
                    </h3>
                    <div className="flex items-baseline">
                      <span className="text-4xl font-bold text-gray-900">
                        {plan.price === null ? 'Custom' : `$${plan.price}`}
                      </span>
                      {plan.price !== null && plan.price > 0 && (
                        <span className="text-gray-600 ml-2">/month</span>
                      )}
                    </div>
                  </div>

                  {/* Features List */}
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  {isCurrentPlan ? (
                    <button
                      disabled
                      className="w-full py-3 px-4 bg-gray-300 text-gray-700 rounded-lg font-semibold cursor-not-allowed"
                    >
                      Current Plan
                    </button>
                  ) : (
                    <button
                      onClick={() => handleUpgrade(planKey)}
                      disabled={upgrading === planKey}
                      className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                        planKey === 'free'
                          ? 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                          : isPro
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-900 text-white hover:bg-gray-800'
                      } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      {upgrading === planKey ? (
                        <span className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Upgrading...
                        </span>
                      ) : planKey === 'free' ? (
                        'Downgrade'
                      ) : planKey === 'enterprise' ? (
                        'Contact Sales'
                      ) : (
                        'Upgrade Now'
                      )}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="mt-16 max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Can I change my plan later?
              </h3>
              <p className="text-gray-600">
                Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-gray-600">
                We accept all major credit cards, PayPal, and bank transfers for Enterprise plans.
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Is there a free trial for paid plans?
              </h3>
              <p className="text-gray-600">
                Yes! All paid plans come with a 14-day money-back guarantee. Try risk-free!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
