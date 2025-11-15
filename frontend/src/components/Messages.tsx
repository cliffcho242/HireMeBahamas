import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';

interface Message {
  id: number;
  sender: {
    name: string;
    avatar: string;
  };
  content: string;
  time: string;
  isFromMe: boolean;
}

interface Conversation {
  id: number;
  user: {
    name: string;
    avatar: string;
    isOnline: boolean;
  };
  lastMessage: string;
  time: string;
  unreadCount: number;
  messages: Message[];
}

const Messages: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const [newMessage, setNewMessage] = useState('');

  // NOTE: Real conversations should be fetched from the API at /api/messages/conversations
  // This widget component has been cleaned of test data. 
  // Use the /messages page for full messaging functionality.
  const conversations: Conversation[] = [];

  const selectedConv = conversations.find(c => c.id === selectedConversation);

  const sendMessage = () => {
    if (!newMessage.trim() || !selectedConv) return;

    // In a real app, this would send to API
    console.log('Sending message:', newMessage);
    setNewMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="relative">
      {/* Messages Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
      >
        <ChatBubbleLeftRightIcon className="w-6 h-6 text-gray-600" />
        {conversations.some(c => c.unreadCount > 0) && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
            {conversations.reduce((sum, c) => sum + c.unreadCount, 0)}
          </span>
        )}
      </button>

      {/* Messages Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute right-0 top-12 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Messages</h3>
              <div className="flex items-center space-x-2">
                <button className="p-1 rounded-full hover:bg-gray-100 transition-colors">
                  <EllipsisVerticalIcon className="w-5 h-5 text-gray-600" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                >
                  <XMarkIcon className="w-5 h-5 text-gray-600" />
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="p-4 border-b border-gray-200">
              <div className="relative">
                <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search messages..."
                  className="w-full pl-9 pr-4 py-2 bg-gray-100 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Conversations List or Chat */}
            {!selectedConversation ? (
              <div className="max-h-96 overflow-y-auto">
                {conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className="flex items-center space-x-3 p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                    onClick={() => setSelectedConversation(conversation.id)}
                  >
                    {/* Avatar */}
                    <div className="relative flex-shrink-0">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold">
                          {conversation.user.avatar}
                        </span>
                      </div>
                      {conversation.user.isOnline && (
                        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                      )}
                    </div>

                    {/* Conversation Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {conversation.user.name}
                        </p>
                        <span className="text-xs text-gray-500">{conversation.time}</span>
                      </div>
                      <p className="text-sm text-gray-600 truncate">{conversation.lastMessage}</p>
                    </div>

                    {/* Unread Badge */}
                    {conversation.unreadCount > 0 && (
                      <div className="flex-shrink-0">
                        <span className="bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                          {conversation.unreadCount}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col h-96">
                {/* Chat Header */}
                <div className="flex items-center space-x-3 p-4 border-b border-gray-200">
                  <button
                    onClick={() => setSelectedConversation(null)}
                    className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                  >
                    <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold text-sm">
                          {selectedConv?.user.avatar}
                        </span>
                      </div>
                      {selectedConv?.user.isOnline && (
                        <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full border border-white"></div>
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{selectedConv?.user.name}</p>
                      <p className="text-xs text-gray-500">
                        {selectedConv?.user.isOnline ? 'Active now' : 'Offline'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {selectedConv?.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.isFromMe ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs px-3 py-2 rounded-lg ${
                          message.isFromMe
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.isFromMe ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {message.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Message Input */}
                <div className="p-4 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type a message..."
                      className="flex-1 px-3 py-2 bg-gray-100 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim()}
                      className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <PaperAirplaneIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Messages;