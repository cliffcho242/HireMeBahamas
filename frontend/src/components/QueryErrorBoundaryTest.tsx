/**
 * QueryErrorBoundary Test Component
 * 
 * This component can be used to manually test the QueryErrorBoundary
 * by intentionally throwing errors.
 * 
 * Usage:
 * 1. Import and add to a route: import { QueryErrorBoundaryTest } from './components/QueryErrorBoundaryTest'
 * 2. Add route: <Route path="/test-error-boundary" element={<QueryErrorBoundaryTest />} />
 * 3. Navigate to /test-error-boundary
 * 4. Click "Trigger Error" to test error boundary
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

interface TestComponentProps {
  shouldThrow?: boolean;
}

// Component that throws an error when shouldThrow is true
const ErrorThrowingComponent: React.FC<TestComponentProps> = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test error from QueryErrorBoundaryTest component');
  }
  return <div className="text-green-600">No error - Everything is working correctly! ✓</div>;
};

// Component that simulates a React Query error
const QueryErrorComponent: React.FC = () => {
  const { data, error } = useQuery({
    queryKey: ['test-error'],
    queryFn: async () => {
      // Simulate an API error
      throw new Error('React Query test error');
    },
    retry: false,
    throwOnError: true, // This will cause the error to be caught by ErrorBoundary
  });

  if (error) {
    return <div className="text-red-600">Query error (should be caught by boundary)</div>;
  }

  return <div>{data}</div>;
};

const QueryErrorBoundaryTest: React.FC = () => {
  const [shouldThrow, setShouldThrow] = useState(false);
  const [testQueryError, setTestQueryError] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            QueryErrorBoundary Test
          </h1>

          <div className="space-y-6">
            {/* Test 1: Component Error */}
            <div className="border-2 border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Test 1: Component Throw Error
              </h2>
              <p className="text-gray-600 mb-4">
                This test throws an error in a component. The QueryErrorBoundary should catch it
                and display a fallback UI.
              </p>

              <div className="mb-4 p-4 bg-gray-50 rounded">
                <ErrorThrowingComponent shouldThrow={shouldThrow} />
              </div>

              <button
                onClick={() => setShouldThrow(true)}
                className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Trigger Component Error
              </button>
            </div>

            {/* Test 2: React Query Error */}
            <div className="border-2 border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Test 2: React Query Error (throwOnError: true)
              </h2>
              <p className="text-gray-600 mb-4">
                This test simulates a React Query error with throwOnError: true.
                The QueryErrorBoundary should catch it.
              </p>

              <div className="mb-4 p-4 bg-gray-50 rounded">
                {testQueryError ? (
                  <QueryErrorComponent />
                ) : (
                  <div className="text-gray-600">Click button to trigger query error</div>
                )}
              </div>

              <button
                onClick={() => setTestQueryError(true)}
                className="bg-orange-600 hover:bg-orange-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Trigger Query Error
              </button>
            </div>

            {/* Information */}
            <div className="border-2 border-blue-200 bg-blue-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-blue-900 mb-4">
                📋 Expected Behavior
              </h2>
              <ul className="list-disc list-inside space-y-2 text-blue-800">
                <li>
                  <strong>Test 1:</strong> When you click "Trigger Component Error", the entire page
                  should be replaced with the QueryErrorBoundary fallback UI showing
                  "Oops! Something went wrong".
                </li>
                <li>
                  <strong>Test 2:</strong> When you click "Trigger Query Error", the same fallback UI
                  should appear because React Query will throw the error to the boundary.
                </li>
                <li>
                  The fallback UI should have a "Try Again" button that resets the error state
                  and a "Go to Home" button that navigates to the home page.
                </li>
                <li>
                  In development mode, you should see the error details in the fallback UI.
                </li>
              </ul>
            </div>

            {/* Edge Runtime Info */}
            <div className="border-2 border-green-200 bg-green-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-green-900 mb-4">
                ⚡ Edge Runtime Compatibility
              </h2>
              <p className="text-green-800">
                The QueryErrorBoundary component is designed to be fully compatible with
                Vercel Edge Functions and Edge Runtime. It uses only standard JavaScript
                APIs and React features, avoiding any Node.js-specific functionality.
              </p>
              <ul className="list-disc list-inside space-y-2 text-green-800 mt-4">
                <li>✓ No Node.js APIs used</li>
                <li>✓ Uses only standard Web APIs (fetch, console, window)</li>
                <li>✓ React class component (fully supported in Edge)</li>
                <li>✓ Compatible with React Query v5</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QueryErrorBoundaryTest;
