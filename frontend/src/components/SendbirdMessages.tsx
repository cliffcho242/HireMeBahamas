/**
 * Sendbird Messages Component
 * 
 * This component integrates Sendbird UIKit for real-time messaging.
 * It provides a complete messaging interface with channels, conversations, and real-time updates.
 */

import React from 'react';
import '@sendbird/uikit-react/dist/index.css';
import '../styles/sendbird.css';
import { App as SendbirdApp } from '@sendbird/uikit-react';
import { useAuth } from '../contexts/AuthContext';
import { getSendbirdAppId, isSendbirdConfigured } from '../config/sendbird';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const SendbirdMessages: React.FC = () => {
  const { user } = useAuth();

  // Check if Sendbird is configured
  if (!isSendbirdConfigured()) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Sendbird Not Configured
          </h2>
          <p className="text-gray-600 mb-4">
            To enable messaging with Sendbird, you need to set up your Sendbird App ID.
          </p>
          <div className="bg-gray-50 rounded-md p-4 text-left">
            <p className="text-sm text-gray-700 mb-2">
              <strong>Setup Instructions:</strong>
            </p>
            <ol className="text-sm text-gray-600 list-decimal list-inside space-y-1">
              <li>Create a Sendbird account at <a href="https://sendbird.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">sendbird.com</a></li>
              <li>Create a new application in the Sendbird Dashboard</li>
              <li>Copy your Application ID</li>
              <li>Add it to your <code className="bg-gray-200 px-1 rounded">.env</code> file as <code className="bg-gray-200 px-1 rounded">VITE_SENDBIRD_APP_ID</code></li>
              <li>Restart your development server</li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Please log in to access messaging.</p>
        </div>
      </div>
    );
  }

  const appId = getSendbirdAppId();
  const userId = user.id.toString();
  const nickname = `${user.first_name} ${user.last_name}`;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">Messages (Sendbird)</h1>
            <div className="text-sm text-gray-500">
              Powered by Sendbird
            </div>
          </div>
        </div>
      </header>

      {/* Sendbird Chat Interface */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div 
          className="bg-white rounded-2xl shadow-sm overflow-hidden sendbird-wrapper"
          style={{ height: 'calc(100vh - 200px)' }}
        >
          <SendbirdApp
            appId={appId}
            userId={userId}
            nickname={nickname}
            theme="light"
            // Optional: Customize colors to match your brand
            colorSet={{
              '--sendbird-light-primary-500': '#2563eb',
              '--sendbird-light-primary-400': '#3b82f6',
              '--sendbird-light-primary-300': '#60a5fa',
            }}
          />
        </div>
      </div>


    </div>
  );
};

export default SendbirdMessages;
