/**
 * Sendbird Context
 * 
 * This context provides Sendbird functionality throughout the application.
 * It manages the connection to Sendbird and provides helper methods.
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import SendbirdChat, { User as SendbirdUser } from '@sendbird/chat';
import { GroupChannelModule } from '@sendbird/chat/groupChannel';
import { getSendbirdAppId, isSendbirdConfigured } from '../config/sendbird';

interface SendbirdContextType {
  sdk: SendbirdChat | null;
  currentUser: SendbirdUser | null;
  isConnected: boolean;
  isConnecting: boolean;
  connect: (userId: string, nickname?: string) => Promise<void>;
  disconnect: () => Promise<void>;
  error: string | null;
}

const SendbirdContext = createContext<SendbirdContextType | undefined>(undefined);

interface SendbirdProviderProps {
  children: React.ReactNode;
}

export const SendbirdProvider: React.FC<SendbirdProviderProps> = ({ children }) => {
  const [sdk, setSdk] = useState<SendbirdChat | null>(null);
  const [currentUser, setCurrentUser] = useState<SendbirdUser | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize Sendbird SDK
  useEffect(() => {
    if (!isSendbirdConfigured()) {
      setError('Sendbird App ID is not configured. Please set VITE_SENDBIRD_APP_ID in your .env file.');
      return;
    }

    const appId = getSendbirdAppId();
    if (!appId) {
      setError('Invalid Sendbird App ID');
      return;
    }

    try {
      const sendbirdInstance = SendbirdChat.init({
        appId,
        modules: [new GroupChannelModule()],
      });
      setSdk(sendbirdInstance);
    } catch (err) {
      console.error('Failed to initialize Sendbird:', err);
      setError('Failed to initialize Sendbird SDK');
    }
  }, []);

  const connect = async (userId: string, nickname?: string) => {
    if (!sdk) {
      throw new Error('Sendbird SDK is not initialized');
    }

    setIsConnecting(true);
    setError(null);

    try {
      const user = await sdk.connect(userId, undefined);
      
      // Update user nickname if provided
      if (nickname && user.nickname !== nickname) {
        await sdk.updateCurrentUserInfo({
          nickname,
        });
      }

      setCurrentUser(user);
      setIsConnected(true);
    } catch (err) {
      console.error('Failed to connect to Sendbird:', err);
      setError('Failed to connect to Sendbird');
      throw err;
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnect = async () => {
    if (!sdk) {
      return;
    }

    try {
      await sdk.disconnect();
      setCurrentUser(null);
      setIsConnected(false);
    } catch (err) {
      console.error('Failed to disconnect from Sendbird:', err);
      setError('Failed to disconnect from Sendbird');
      throw err;
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (sdk && isConnected) {
        sdk.disconnect().catch(console.error);
      }
    };
  }, [sdk, isConnected]);

  return (
    <SendbirdContext.Provider
      value={{
        sdk,
        currentUser,
        isConnected,
        isConnecting,
        connect,
        disconnect,
        error,
      }}
    >
      {children}
    </SendbirdContext.Provider>
  );
};

export const useSendbird = (): SendbirdContextType => {
  const context = useContext(SendbirdContext);
  if (context === undefined) {
    throw new Error('useSendbird must be used within a SendbirdProvider');
  }
  return context;
};
