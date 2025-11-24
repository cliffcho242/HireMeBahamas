/**
 * Sendbird Demo Component
 * 
 * This component demonstrates how to use Sendbird in HireMeBahamas.
 * It can be used for testing and as a reference for integration.
 * 
 * To use this demo:
 * 1. Get a Sendbird App ID from https://dashboard.sendbird.com/
 * 2. Set VITE_SENDBIRD_APP_ID in your .env file
 * 3. Navigate to /sendbird-demo in your app
 */

import React, { useState } from 'react';
import { useSendbird } from '../contexts/SendbirdContext';
import { useAuth } from '../contexts/AuthContext';
import SendbirdMessages from '../components/SendbirdMessages';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ExclamationCircleIcon,
  ChatBubbleLeftRightIcon 
} from '@heroicons/react/24/outline';

const SendbirdDemo: React.FC = () => {
  const { user } = useAuth();
  const { 
    sdk, 
    currentUser, 
    isConnected, 
    isConnecting, 
    connect, 
    disconnect, 
    error 
  } = useSendbird();
  
  const [showChat, setShowChat] = useState(false);

  const handleConnect = async () => {
    if (!user) return;
    try {
      await connect(user.id.toString(), `${user.first_name} ${user.last_name}`);
    } catch (err) {
      console.error('Connection failed:', err);
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnect();
      setShowChat(false);
    } catch (err) {
      console.error('Disconnect failed:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center space-x-4">
            <ChatBubbleLeftRightIcon className="w-12 h-12 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Sendbird Demo</h1>
              <p className="text-gray-600 mt-1">
                Test and explore Sendbird integration
              </p>
            </div>
          </div>
        </div>

        {/* Status Panel */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Connection Status</h2>
          
          <div className="space-y-3">
            {/* SDK Status */}
            <div className="flex items-center space-x-3">
              {sdk ? (
                <CheckCircleIcon className="w-6 h-6 text-green-500" />
              ) : (
                <XCircleIcon className="w-6 h-6 text-red-500" />
              )}
              <span className="text-gray-700">
                Sendbird SDK: {sdk ? 'Initialized' : 'Not Initialized'}
              </span>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-3">
              {isConnected ? (
                <CheckCircleIcon className="w-6 h-6 text-green-500" />
              ) : isConnecting ? (
                <ExclamationCircleIcon className="w-6 h-6 text-yellow-500 animate-pulse" />
              ) : (
                <XCircleIcon className="w-6 h-6 text-red-500" />
              )}
              <span className="text-gray-700">
                Connection: {isConnected ? 'Connected' : isConnecting ? 'Connecting...' : 'Disconnected'}
              </span>
            </div>

            {/* User Status */}
            {currentUser && (
              <div className="flex items-center space-x-3">
                <CheckCircleIcon className="w-6 h-6 text-green-500" />
                <span className="text-gray-700">
                  Logged in as: <strong>{currentUser.nickname || currentUser.userId}</strong>
                </span>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                <XCircleIcon className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-red-800 font-medium">Error</p>
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="mt-6 flex space-x-4">
            {!isConnected ? (
              <button
                onClick={handleConnect}
                disabled={!sdk || !user || isConnecting}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isConnecting ? 'Connecting...' : 'Connect to Sendbird'}
              </button>
            ) : (
              <>
                <button
                  onClick={() => setShowChat(!showChat)}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  {showChat ? 'Hide Chat' : 'Show Chat'}
                </button>
                <button
                  onClick={handleDisconnect}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Disconnect
                </button>
              </>
            )}
          </div>
        </div>

        {/* Info Panel */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            How to use this demo:
          </h3>
          <ol className="list-decimal list-inside space-y-2 text-blue-800">
            <li>Make sure you have set <code className="bg-blue-100 px-2 py-0.5 rounded">VITE_SENDBIRD_APP_ID</code> in your .env file</li>
            <li>Click "Connect to Sendbird" to establish a connection</li>
            <li>Once connected, click "Show Chat" to open the messaging interface</li>
            <li>Test sending messages between different accounts</li>
            <li>Explore the Sendbird features like typing indicators, read receipts, etc.</li>
          </ol>
        </div>

        {/* Chat Interface */}
        {showChat && isConnected && (
          <div className="animate-fadeIn">
            <SendbirdMessages />
          </div>
        )}

        {/* Documentation Links */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Documentation & Resources
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a
              href="/SENDBIRD_SETUP_GUIDE.md"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 font-bold">📚</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Setup Guide</p>
                <p className="text-sm text-gray-600">Complete setup instructions</p>
              </div>
            </a>

            <a
              href="/SENDBIRD_INTEGRATION.md"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-green-600 font-bold">🔧</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Integration Guide</p>
                <p className="text-sm text-gray-600">Quick integration steps</p>
              </div>
            </a>

            <a
              href="https://sendbird.com/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-purple-600 font-bold">📖</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Sendbird Docs</p>
                <p className="text-sm text-gray-600">Official documentation</p>
              </div>
            </a>

            <a
              href="https://dashboard.sendbird.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <span className="text-yellow-600 font-bold">⚙️</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Sendbird Dashboard</p>
                <p className="text-sm text-gray-600">Manage your app</p>
              </div>
            </a>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default SendbirdDemo;
