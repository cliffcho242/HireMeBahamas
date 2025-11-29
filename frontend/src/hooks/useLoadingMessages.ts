import { useState, useCallback } from 'react';

/**
 * Loading message configuration for progressive loading states.
 * Each entry defines a message and the delay (in ms) after which it should appear.
 */
interface LoadingMessageConfig {
  message: string;
  delay: number;
}

/**
 * Default loading messages for authentication operations.
 * These provide simple feedback without exposing server state details.
 */
const DEFAULT_AUTH_MESSAGES: LoadingMessageConfig[] = [
  { message: 'Signing in...', delay: 0 },
];

const DEFAULT_REGISTER_MESSAGES: LoadingMessageConfig[] = [
  { message: 'Creating Account...', delay: 0 },
];

interface UseLoadingMessagesOptions {
  /** Custom messages configuration. Defaults to auth-specific messages. */
  messages?: LoadingMessageConfig[];
  /** Initial message to show. Defaults to first message in config. */
  initialMessage?: string;
}

interface UseLoadingMessagesReturn {
  /** Current loading message to display */
  loadingMessage: string;
  /** Whether the loading state is active */
  isLoading: boolean;
  /** Start showing loading messages */
  startLoading: () => void;
  /** Stop loading and reset to initial state */
  stopLoading: () => void;
}

/**
 * Custom hook for managing progressive loading messages.
 * 
 * During slow operations (like login during cold starts), this hook updates
 * the loading message at configured intervals to provide feedback to users.
 * 
 * @example
 * ```tsx
 * const { loadingMessage, isLoading, startLoading, stopLoading } = useLoadingMessages({
 *   messages: DEFAULT_AUTH_MESSAGES
 * });
 * 
 * const handleSubmit = async () => {
 *   startLoading();
 *   try {
 *     await login(email, password);
 *   } finally {
 *     stopLoading();
 *   }
 * };
 * 
 * return (
 *   <button disabled={isLoading}>
 *     {isLoading ? loadingMessage : 'Sign In'}
 *   </button>
 * );
 * ```
 */
export function useLoadingMessages(
  options: UseLoadingMessagesOptions = {}
): UseLoadingMessagesReturn {
  const messages = options.messages || DEFAULT_AUTH_MESSAGES;
  const initialMessage = options.initialMessage || messages[0]?.message || 'Loading...';
  
  const [loadingMessage, setLoadingMessage] = useState(initialMessage);
  const [isLoading, setIsLoading] = useState(false);
  const [timeoutIds, setTimeoutIds] = useState<ReturnType<typeof setTimeout>[]>([]);

  const startLoading = useCallback(() => {
    // Clear any existing timeouts
    timeoutIds.forEach((id) => clearTimeout(id));
    
    setIsLoading(true);
    setLoadingMessage(initialMessage);
    
    // Set up timeouts for each message transition
    const newTimeoutIds = messages
      .filter((config) => config.delay > 0)
      .map((config) => {
        return setTimeout(() => {
          setLoadingMessage(config.message);
        }, config.delay);
      });
    
    setTimeoutIds(newTimeoutIds);
  }, [messages, initialMessage, timeoutIds]);

  const stopLoading = useCallback(() => {
    // Clear all timeouts
    timeoutIds.forEach((id) => clearTimeout(id));
    setTimeoutIds([]);
    
    setIsLoading(false);
    setLoadingMessage(initialMessage);
  }, [timeoutIds, initialMessage]);

  return {
    loadingMessage,
    isLoading,
    startLoading,
    stopLoading,
  };
}

// Export default message configurations for use in components
export { DEFAULT_AUTH_MESSAGES, DEFAULT_REGISTER_MESSAGES };
export type { LoadingMessageConfig };
