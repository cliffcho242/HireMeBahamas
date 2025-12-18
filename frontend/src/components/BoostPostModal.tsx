import React, { useState } from 'react';
import { X, Zap, Star, Award, TrendingUp } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface BoostOption {
  type: 'local' | 'national' | 'featured';
  name: string;
  description: string;
  price: number;
  duration_days: number;
  estimated_impressions: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

interface BoostPostModalProps {
  postId: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const boostOptions: BoostOption[] = [
  {
    type: 'local',
    name: 'Local Boost',
    description: 'Reach users in your area',
    price: 9.99,
    duration_days: 7,
    estimated_impressions: '500-1,000',
    icon: <TrendingUp className="h-6 w-6" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  {
    type: 'national',
    name: 'National Boost',
    description: 'Reach users across the Bahamas',
    price: 29.99,
    duration_days: 7,
    estimated_impressions: '2,000-5,000',
    icon: <Zap className="h-6 w-6" />,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
  },
  {
    type: 'featured',
    name: 'Featured',
    description: 'Homepage and top of feeds',
    price: 49.99,
    duration_days: 14,
    estimated_impressions: '10,000+',
    icon: <Award className="h-6 w-6" />,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
  },
];

const BoostPostModal: React.FC<BoostPostModalProps> = ({ postId, isOpen, onClose, onSuccess }) => {
  const [selectedBoost, setSelectedBoost] = useState<BoostOption | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleBoostPost = async () => {
    if (!selectedBoost) {
      toast.error('Please select a boost option');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const expiresAt = new Date();
      expiresAt.setDate(expiresAt.getDate() + selectedBoost.duration_days);

      await axios.post(
        `${API_URL}/api/monetization/boosted-posts`,
        {
          post_id: postId,
          boost_type: selectedBoost.type,
          price_paid: selectedBoost.price,
          impressions_target: parseInt(selectedBoost.estimated_impressions.replace(/[^0-9]/g, '')),
          expires_at: expiresAt.toISOString(),
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      toast.success(`Post boosted with ${selectedBoost.name}!`);
      onSuccess?.();
      onClose();
    } catch (error: any) {
      console.error('Error boosting post:', error);
      toast.error(error.response?.data?.detail || 'Failed to boost post. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <Star className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Boost Your Post</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Increase visibility and reach more people
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {boostOptions.map((option) => (
            <button
              key={option.type}
              onClick={() => setSelectedBoost(option)}
              className={`w-full text-left p-6 rounded-xl border-2 transition-all ${
                selectedBoost?.type === option.type
                  ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 ${option.bgColor} rounded-xl flex items-center justify-center ${option.color}`}>
                    {option.icon}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {option.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {option.description}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    ${option.price}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{option.duration_days} days</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <span>{option.estimated_impressions} views</span>
                </div>
              </div>

              {selectedBoost?.type === option.type && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium">Selected</span>
                  </div>
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${selectedBoost?.price.toFixed(2) || '0.00'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600 dark:text-gray-400">Duration</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {selectedBoost?.duration_days || 0} days
              </p>
            </div>
          </div>

          <button
            onClick={handleBoostPost}
            disabled={!selectedBoost || loading}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <Zap className="h-5 w-5" />
                Boost Post Now
              </span>
            )}
          </button>

          <p className="text-xs text-center text-gray-500 dark:text-gray-400 mt-4">
            💳 Payment integration coming soon. This is a preview of the boost feature.
          </p>
        </div>
      </div>
    </div>
  );
};

export default BoostPostModal;
