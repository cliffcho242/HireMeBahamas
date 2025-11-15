import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSocket } from '../contexts/SocketContext';
import api from '../services/api';
import { PaperAirplaneIcon, MagnifyingGlassIcon, UserIcon } from '@heroicons/react/24/outline';

interface Message {
  id: number;
  content: string;
  sender_id: number;
  conversation_id: number;
  created_at: string;
  sender: {
    first_name: string;
    last_name: string;
  };
}

interface Conversation {
  id: number;
  participant_1_id: number;
  participant_2_id: number;
  created_at: string;
  updated_at: string;
  participant_1: {
    first_name: string;
    last_name: string;
  };
  participant_2: {
    first_name: string;
    last_name: string;
  };
  messages: Message[];
}

const Messages: React.FC = () => {
  const { user } = useAuth();
  const { socket } = useSocket();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (user) {
      fetchConversations();
    }
  }, [user]);

  useEffect(() => {
    scrollToBottom();
  }, [selectedConversation?.messages]);

  useEffect(() => {
    if (socket && user) {
      socket.on('new_message', (message: Message) => {
        // Validate that the message belongs to a conversation the user is part of
        if (selectedConversation && message.conversation_id === selectedConversation.id) {
          // Additional check: ensure the message is from/to the current user
          if (selectedConversation.participant_1_id === user.id || 
              selectedConversation.participant_2_id === user.id) {
            setSelectedConversation(prev => prev ? {
              ...prev,
              messages: [...prev.messages, message]
            } : null);
          }
        }

        // Update the conversation list - only if user is participant
        setConversations(prev =>
          prev.map(conv => {
            if (conv.id === message.conversation_id && 
                (conv.participant_1_id === user.id || conv.participant_2_id === user.id)) {
              return { ...conv, messages: [...conv.messages, message] };
            }
            return conv;
          })
        );
      });

      return () => {
        socket.off('new_message');
      };
    }
  }, [socket, user, selectedConversation]);

  const fetchConversations = async () => {
    try {
      const response = await api.get('/messages/conversations');
      // Client-side validation: ensure all conversations involve the current user
      const validConversations = response.data.filter((conv: Conversation) => 
        user && (conv.participant_1_id === user.id || conv.participant_2_id === user.id)
      );
      setConversations(validConversations);
      if (validConversations.length > 0) {
        setSelectedConversation(validConversations[0]);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
      // Show empty state on error
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation || !user) return;

    // Client-side validation: ensure user is a participant
    if (selectedConversation.participant_1_id !== user.id && 
        selectedConversation.participant_2_id !== user.id) {
      alert('You are not authorized to send messages in this conversation.');
      return;
    }

    setSending(true);
    try {
      const response = await api.post('/messages/', {
        conversation_id: selectedConversation.id,
        content: newMessage.trim(),
      });

      setNewMessage('');

      // Update the selected conversation with the new message
      setSelectedConversation(prev => prev ? {
        ...prev,
        messages: [...prev.messages, response.data]
      } : null);

    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const getOtherParticipant = (conversation: Conversation) => {
    return conversation.participant_1_id === user?.id
      ? conversation.participant_2
      : conversation.participant_1;
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return 'now';
    if (diffInMinutes < 60) return `${diffInMinutes}m`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h`;
    return date.toLocaleDateString();
  };

  const filteredConversations = conversations.filter(conversation => {
    const otherParticipant = getOtherParticipant(conversation);
    return otherParticipant.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           otherParticipant.last_name.toLowerCase().includes(searchTerm.toLowerCase());
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
            <div className="text-sm text-gray-500">
              {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden" style={{ height: 'calc(100vh - 200px)' }}>
          <div className="flex h-full">
            {/* Conversations Sidebar */}
            <div className="w-80 border-r border-gray-200 flex flex-col">
              {/* Search */}
              <div className="p-4 border-b border-gray-200">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search conversations..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Conversations List */}
              <div className="flex-1 overflow-y-auto">
                {filteredConversations.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <UserIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium mb-2">No conversations</p>
                    <p className="text-sm">Start connecting with professionals!</p>
                  </div>
                ) : (
                  filteredConversations.map((conversation) => {
                    const otherParticipant = getOtherParticipant(conversation);
                    const lastMessage = conversation.messages[conversation.messages.length - 1];

                    return (
                      <motion.div
                        key={conversation.id}
                        onClick={() => setSelectedConversation(conversation)}
                        className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                          selectedConversation?.id === conversation.id ? 'bg-blue-50 border-blue-200' : ''
                        }`}
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                            <span className="text-white font-semibold">
                              {otherParticipant.first_name[0]}{otherParticipant.last_name[0]}
                            </span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-start">
                              <h3 className="font-semibold text-gray-900 truncate">
                                {otherParticipant.first_name} {otherParticipant.last_name}
                              </h3>
                              {lastMessage && (
                                <span className="text-xs text-gray-400 ml-2">
                                  {formatTime(lastMessage.created_at)}
                                </span>
                              )}
                            </div>
                            {lastMessage && (
                              <p className="text-sm text-gray-500 truncate mt-1">
                                {lastMessage.sender_id === user?.id && 'You: '}
                                {lastMessage.content}
                              </p>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 flex flex-col">
              {selectedConversation ? (
                <>
                  {/* Chat Header */}
                  <div className="p-4 border-b border-gray-200 bg-white">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold text-sm">
                          {getOtherParticipant(selectedConversation).first_name[0]}
                          {getOtherParticipant(selectedConversation).last_name[0]}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {getOtherParticipant(selectedConversation).first_name}{' '}
                          {getOtherParticipant(selectedConversation).last_name}
                        </h3>
                        <p className="text-sm text-gray-500">Active now</p>
                      </div>
                    </div>
                  </div>

                  {/* Messages List */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                    {selectedConversation.messages.map((message, index) => {
                      const isOwnMessage = message.sender_id === user?.id;
                      const showAvatar = index === 0 || selectedConversation.messages[index - 1].sender_id !== message.sender_id;

                      return (
                        <motion.div
                          key={message.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`flex items-end space-x-2 max-w-xs lg:max-w-md ${isOwnMessage ? 'flex-row-reverse space-x-reverse' : ''}`}>
                            {showAvatar && !isOwnMessage && (
                              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                                <span className="text-white font-semibold text-xs">
                                  {message.sender.first_name[0]}{message.sender.last_name[0]}
                                </span>
                              </div>
                            )}
                            {!showAvatar && !isOwnMessage && <div className="w-8" />}
                            <div
                              className={`px-4 py-2 rounded-2xl ${
                                isOwnMessage
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-white text-gray-900 shadow-sm'
                              }`}
                            >
                              <p className="text-sm">{message.content}</p>
                              <p className={`text-xs mt-1 ${
                                isOwnMessage ? 'text-blue-100' : 'text-gray-500'
                              }`}>
                                {formatTime(message.created_at)}
                              </p>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Message Input */}
                  <form onSubmit={sendMessage} className="p-4 border-t border-gray-200 bg-white">
                    <div className="flex space-x-4">
                      <div className="flex-1 relative">
                        <input
                          type="text"
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          placeholder="Type a message..."
                          className="w-full px-4 py-3 border border-gray-200 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                          disabled={sending}
                        />
                      </div>
                      <button
                        type="submit"
                        disabled={sending || !newMessage.trim()}
                        className="bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <PaperAirplaneIcon className="w-5 h-5" />
                      </button>
                    </div>
                  </form>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center bg-gray-50">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <PaperAirplaneIcon className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a conversation</h3>
                    <p className="text-gray-600">Choose a conversation to start messaging</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Messages;