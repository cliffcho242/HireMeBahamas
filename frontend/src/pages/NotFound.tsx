import { Link, useLocation } from 'react-router-dom';
import { HomeIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

/**
 * NotFound Page Component
 * 
 * Displays a user-friendly 404 error page when users navigate to invalid routes.
 * Prevents users from being lost by providing clear navigation options.
 */
export default function NotFound() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        {/* 404 Illustration */}
        <div className="mb-8">
          <div className="text-9xl font-bold text-blue-600 dark:text-blue-400 opacity-20">
            404
          </div>
        </div>

        {/* Error Message */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Page Not Found
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-2">
            Sorry, we couldn't find the page you're looking for.
          </p>
          {location.pathname && (
            <p className="text-sm text-gray-500 dark:text-gray-400 break-all">
              <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                {location.pathname}
              </code>
            </p>
          )}
        </div>

        {/* Navigation Options */}
        <div className="space-y-4">
          <Link
            to="/"
            className="w-full inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
          >
            <HomeIcon className="h-5 w-5 mr-2" />
            Go to Home
          </Link>
          
          <button
            onClick={() => window.history.back()}
            className="w-full inline-flex items-center justify-center px-6 py-3 border border-gray-300 dark:border-gray-600 text-base font-medium rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Go Back
          </button>
        </div>

        {/* Help Text */}
        <div className="mt-8">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            If you believe this is an error, please{' '}
            <Link
              to="/messages"
              className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
            >
              contact support
            </Link>
            .
          </p>
        </div>
      </div>
    </div>
  );
}
