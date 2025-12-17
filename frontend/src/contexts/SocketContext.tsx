/* eslint-disable react-refresh/only-export-components */
// Context files export both Provider components and custom hooks
import { ReactNode, createContext, useContext, useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from './AuthContext';
import { toast } from 'react-hot-toast';
import { SocketMessageData } from '../types';

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  onlineUsers: string[];
  joinConversation: (conversationId: string) => void;
  leaveConversation: (conversationId: string) => void;
  sendMessage: (data: SocketMessageData) => void;
  sendTyping: (conversationId: string, isTyping: boolean) => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

interface SocketProviderProps {
  children: ReactNode;
}

export const SocketProvider = ({ children }): SocketProviderProps => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const { user, token } = useAuth();

  useEffect(() => {
    if (!user || !token) return;

    // Use environment variable or fall back to same-origin for serverless deployments
    const socketUrl = import.meta.env.VITE_SOCKET_URL || window.location.origin;
    
    // Create socket connection
    const newSocket = io(socketUrl, {
      auth: {
        token: token
      },
      transports: ['websocket', 'polling']
    });

    // Connection events
    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to server');
    });

    newSocket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from server');
    });

    newSocket.on('connected', (data) => {
      console.log('Socket authenticated:', data);
    });

    newSocket.on('error', (error) => {
      console.error('Socket error:', error);
      toast.error('Connection error: ' + error.message);
    });

    // Message events
    newSocket.on('new_message', (message) => {
      // Handle new message
      console.log('New message received:', message);
      // You can dispatch this to a global state or handle it in components
    });

    // Typing events
    newSocket.on('typing', (data) => {
      console.log('Typing indicator:', data);
      // Handle typing indicator
    });

    // User status events
    newSocket.on('user_status', (data) => {
      console.log('User status update:', data);
      if (data.status === 'online') {
        setOnlineUsers(prev => [...prev.filter(id => id !== data.user_id), data.user_id]);
      } else if (data.status === 'offline') {
        setOnlineUsers(prev => prev.filter(id => id !== data.user_id));
      }
    });

    // Set socket after all event listeners are attached
    // This is a valid subscription pattern for external systems (WebSocket)
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSocket(newSocket);

    return () => {
      newSocket.close();
      setSocket(null);
      setIsConnected(false);
    };
  }, [user, token]);

  const joinConversation = (conversationId: string) => {
    if (socket) {
      socket.emit('join_conversation', { conversation_id: conversationId });
    }
  };

  const leaveConversation = (conversationId: string) => {
    if (socket) {
      socket.emit('leave_conversation', { conversation_id: conversationId });
    }
  };

  const sendMessage = (data: SocketMessageData) => {
    if (socket) {
      socket.emit('send_message', data);
    }
  };

  const sendTyping = (conversationId: string, isTyping: boolean) => {
    if (socket) {
      socket.emit('typing', { conversation_id: conversationId, is_typing: isTyping });
    }
  };

  const value: SocketContextType = {
    socket,
    isConnected,
    onlineUsers,
    joinConversation,
    leaveConversation,
    sendMessage,
    sendTyping
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = (): SocketContextType => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};