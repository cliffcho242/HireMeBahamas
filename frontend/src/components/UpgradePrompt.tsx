import { Link } from 'react-router-dom';
import { SparklesIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { PLAN_NAMES, PLAN_PRICES, SUBSCRIPTION_PLANS } from '../constants/subscriptions';

type RequiredPlan = 'pro' | 'business' | 'enterprise';

interface UpgradePromptProps {
  featureName: string;
  requiredPlan?: RequiredPlan;
  onClose?: () => void;
  inline?: boolean;
}

export default function UpgradePrompt({ 
  featureName, 
  requiredPlan = 'pro',
  onClose,
  inline = false 
}: UpgradePromptProps) {
  // Map requiredPlan to actual plan constant safely
  const planKey = requiredPlan === 'pro' ? SUBSCRIPTION_PLANS.PRO
    : requiredPlan === 'business' ? SUBSCRIPTION_PLANS.BUSINESS
    : SUBSCRIPTION_PLANS.ENTERPRISE;
  
  const planName = PLAN_NAMES[planKey] || 'Pro';
  const planPrice = PLAN_PRICES[planKey] || '$9.99/mo';

  if (inline) {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <SparklesIcon className="h-6 w-6 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-gray-900 mb-1">
              {featureName} requires {planName} subscription
            </h3>
            <p className="text-sm text-gray-600 mb-3">
              Upgrade to unlock this feature and many more starting at {planPrice}
            </p>
            <Link
              to="/subscriptions"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              <SparklesIcon className="h-4 w-4 mr-2" />
              View Plans
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-8 text-white relative">
          {onClose && (
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-white hover:text-gray-200 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          )}
          <SparklesIcon className="h-12 w-12 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Upgrade Required</h2>
          <p className="text-blue-100">
            Unlock premium features with {planName}
          </p>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {featureName}
            </h3>
            <p className="text-gray-600">
              This feature is available for {planName} subscribers and above.
            </p>
          </div>

          {/* Benefits */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-gray-900 mb-3">
              What you'll get:
            </h4>
            <ul className="space-y-2">
              {requiredPlan === 'pro' && (
                <>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>Unlimited job applications</span>
                  </li>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>Priority in search results</span>
                  </li>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>Advanced profile customization</span>
                  </li>
                </>
              )}
              {requiredPlan === 'business' && (
                <>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>Post unlimited jobs</span>
                  </li>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>Featured job listings</span>
                  </li>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>Analytics dashboard</span>
                  </li>
                </>
              )}
              {requiredPlan === 'enterprise' && (
                <>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>Custom integrations</span>
                  </li>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>Dedicated account manager</span>
                  </li>
                  <li className="flex items-start text-sm text-gray-700">
                    <SparklesIcon className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" />
                    <span>White-label options</span>
                  </li>
                </>
              )}
            </ul>
          </div>

          {/* Actions */}
          <div className="flex flex-col space-y-3">
            <Link
              to="/subscriptions"
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all text-center"
            >
              View All Plans
            </Link>
            {onClose && (
              <button
                onClick={onClose}
                className="w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
              >
                Maybe Later
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
