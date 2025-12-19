/**
 * User-Friendly Error Handler
 * 
 * Converts technical errors into friendly, actionable messages for users.
 * NO GENERIC ERRORS. Every error gets a clear explanation and next steps.
 */

export interface FriendlyError {
  title: string;
  message: string;
  actions: string[];
  severity: 'info' | 'warning' | 'error';
  icon: '✅' | '⚠️' | '❌' | 'ℹ️';
  helpLink?: string;
}

/**
 * Convert API error to user-friendly format
 */
export function makeErrorFriendly(error: unknown): FriendlyError {
  // Type guard to check if error is an Error-like object
  const isErrorLike = (err: unknown): err is { 
    code?: string; 
    message?: string; 
    response?: { status?: number; data?: unknown } 
  } => {
    return typeof err === 'object' && err !== null;
  };

  if (!isErrorLike(error)) {
    return {
      title: 'Unexpected Error',
      message: 'An unexpected error occurred. Please try again.',
      icon: '⚠️',
      severity: 'warning',
      actions: ['Try refreshing the page'],
    };
  }

  // Network errors
  if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
    return {
      title: 'Cannot Connect to Server',
      message: 'We couldn\'t reach the server. This usually happens when your internet connection is unstable or the server is starting up.',
      actions: [
        'Check your internet connection',
        'Wait 30 seconds and try again',
        'The server may be waking up (this can take up to 60 seconds)',
        'If the problem persists, contact support'
      ],
      severity: 'error',
      icon: '❌',
      helpLink: '/help/connection-issues'
    };
  }
  
  // Timeout errors
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return {
      title: 'Server Taking Too Long',
      message: 'The server is taking longer than expected to respond. This may be due to network congestion or high server load.',
      actions: [
        'Check your internet connection',
        'Wait a moment and try again',
        'Try refreshing the page',
        'If this happens frequently, contact support'
      ],
      severity: 'warning',
      icon: '⚠️',
      helpLink: '/help/slow-response'
    };
  }
  
  // Authentication errors
  if (error.response?.status === 401) {
    const responseData = error.response.data as { detail?: string } | undefined;
    const detail = responseData?.detail || '';
    
    if (detail.includes('Incorrect email or password')) {
      return {
        title: 'Login Failed',
        message: 'The email or password you entered is incorrect.',
        actions: [
          'Double-check your email address (no typos)',
          'Make sure CAPS LOCK is off',
          'Try resetting your password if you forgot it',
          'Contact support if you need help'
        ],
        severity: 'warning',
        icon: '⚠️',
        helpLink: '/forgot-password'
      };
    }
    
    if (detail.includes('OAuth') || detail.includes('social login')) {
      return {
        title: 'Wrong Login Method',
        message: 'This account was created using Google or Apple sign-in. Please use the same method to log in.',
        actions: [
          'Click the "Sign in with Google" or "Sign in with Apple" button',
          'Use the same account you used to sign up',
          'If you don\'t remember which one, try both',
          'Contact support if you need to change login methods'
        ],
        severity: 'info',
        icon: 'ℹ️',
        helpLink: '/help/oauth-login'
      };
    }
    
    if (detail.includes('Token') || detail.includes('expired')) {
      return {
        title: 'Session Expired',
        message: 'Your login session has expired. Please log in again.',
        actions: [
          'This is normal for security',
          'Just log in again - it only takes a second',
          'Check "Remember me" to stay logged in longer',
        ],
        severity: 'info',
        icon: 'ℹ️'
      };
    }
    
    return {
      title: 'Authentication Error',
      message: 'We couldn\'t verify your identity.',
      actions: [
        'Try logging in again',
        'Make sure you\'re using the correct credentials',
        'Contact support if the problem persists'
      ],
      severity: 'warning',
      icon: '⚠️'
    };
  }
  
  // Rate limiting
  if (error.response?.status === 429) {
    return {
      title: 'Too Many Attempts',
      message: 'You\'ve tried to log in too many times. This is a security feature to protect your account.',
      actions: [
        'Wait 15 minutes before trying again',
        'Use "Forgot Password" if you don\'t remember your password',
        'Make sure you\'re entering the correct email and password',
        'Contact support if you think your account is locked'
      ],
      severity: 'warning',
      icon: '⚠️',
      helpLink: '/help/rate-limit'
    };
  }
  
  // Forbidden (account deactivated)
  if (error.response?.status === 403) {
    return {
      title: 'Account Deactivated',
      message: 'Your account has been deactivated. This may be temporary or permanent.',
      actions: [
        'Contact support to reactivate your account',
        'Check your email for any notifications about your account',
        'If you believe this is a mistake, reach out to us immediately'
      ],
      severity: 'error',
      icon: '❌',
      helpLink: '/help/account-deactivated'
    };
  }
  
  // Server errors (500s)
  if (error.response?.status && error.response.status >= 500) {
    const status = error.response.status;
    const responseData = error.response.data as { detail?: string; error?: string } | undefined;
    const detail = (responseData?.detail || responseData?.error || '').toLowerCase();
    
    // Check for database configuration errors
    if (detail.includes('database') && (detail.includes('pattern') || detail.includes('invalid') || detail.includes('format'))) {
      return {
        title: 'Server Configuration Issue',
        message: 'The server has a database configuration problem. This is a temporary issue.',
        actions: [
          'Our team has been automatically notified',
          'The server will be back up shortly',
          'Try again in a few minutes',
          'Contact support if this persists'
        ],
        severity: 'error',
        icon: '❌',
        helpLink: '/help/server-config'
      };
    }
    
    if (status === 502) {
      return {
        title: 'Server Temporarily Unavailable',
        message: 'The server is temporarily unavailable. It\'s probably just starting up.',
        actions: [
          'Wait a moment and try again',
          'Then try logging in again',
          'This is normal after periods of inactivity',
          'Contact support if it persists for more than 5 minutes'
        ],
        severity: 'warning',
        icon: '⚠️',
        helpLink: '/help/502-error'
      };
    }
    
    if (status === 503) {
      return {
        title: 'Server Temporarily Unavailable',
        message: 'The server is temporarily unavailable. Please try again in a moment.',
        actions: [
          'Wait a moment and try again',
          'Check your internet connection',
          'Try refreshing the page',
          'Contact support if it persists'
        ],
        severity: 'info',
        icon: 'ℹ️',
        helpLink: '/help/cold-start'
      };
    }
    
    if (status === 504) {
      return {
        title: 'Request Timed Out',
        message: 'The server took too long to respond. It might be overloaded or starting up.',
        actions: [
          'Wait a moment and try again',
          'If this is your first login in a while, it can take longer',
          'Try again in 30 seconds',
          'Contact support if it keeps happening'
        ],
        severity: 'warning',
        icon: '⚠️'
      };
    }
    
    return {
      title: 'Server Error',
      message: 'Something went wrong on the server. This is not your fault.',
      actions: [
        'Try again in a few moments',
        'The issue has been automatically reported',
        'If it keeps happening, contact support',
        'Include what you were trying to do when you saw this error'
      ],
      severity: 'error',
      icon: '❌',
      helpLink: '/help/server-error'
    };
  }
  
  // Generic fallback (but still friendly!)
  return {
    title: 'Something Went Wrong',
    message: 'We encountered an unexpected issue. Don\'t worry, we\'re here to help!',
    actions: [
      'Try refreshing the page',
      'Check your internet connection',
      'Try logging in again',
      'Contact support if the problem persists'
    ],
    severity: 'error',
    icon: '❌',
    helpLink: '/help/general'
  };
}

/**
 * Display friendly error to user with toast
 */
export function showFriendlyError(
  error: unknown, 
  toast: { 
    error: (message: string, options?: { duration?: number }) => void;
    (message: string, options?: { duration?: number }): void;
  }
): void {
  const friendly = makeErrorFriendly(error);
  
  // Create formatted message with actions
  const message = `
${friendly.icon} ${friendly.title}

${friendly.message}

What to do:
${friendly.actions.map((action, i) => `${i + 1}. ${action}`).join('\n')}
  `.trim();
  
  // Show appropriate toast based on severity
  if (friendly.severity === 'error') {
    toast.error(message, { duration: 10000 });
  } else if (friendly.severity === 'warning') {
    toast.error(message, { duration: 8000 });
  } else {
    // For info severity, try to call toast as a function if possible
    const toastFn = toast as unknown as (message: string, options?: { duration?: number }) => void;
    if (typeof toastFn === 'function') {
      toastFn(message, { duration: 6000 });
    } else {
      // Fallback to error method
      toast.error(message, { duration: 6000 });
    }
  }
  
  // Log to console for developers
  console.error('[Friendly Error]', friendly);
  console.error('[Original Error]', error);
}

/**
 * Get help text for connection issues
 */
export function getConnectionHelpText(): string {
  return `
🔧 Connection Troubleshooting

If you're having trouble connecting:

1. Check Your Internet
   - Make sure you're connected to WiFi or mobile data
   - Try opening another website to verify
   - Restart your router if needed

2. Check Your Connection
   - Ensure you have a stable internet connection
   - Try refreshing the page
   - Close other apps using bandwidth

3. Clear Browser Cache
   - Press Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
   - Clear cached images and files
   - Try again

4. Try Different Browser
   - Sometimes browser extensions block connections
   - Try in incognito/private mode
   - Or use a different browser

5. Check Server Status
   - Visit our status page
   - See if others are reporting issues
   - We'll post updates there

Still having trouble? Contact support at support@hiremebahamas.com
  `.trim();
}

/**
 * Get friendly loading messages based on stage
 */
export function getLoadingMessage(stage: 'connecting' | 'authenticating' | 'loading'): string {
  const messages = {
    connecting: [
      'Connecting to server...',
      'Waking up the backend...',
      'This may take a moment if the server was sleeping...',
      'Almost there! Server is starting up...'
    ],
    authenticating: [
      'Verifying your credentials...',
      'Checking your account...',
      'Logging you in...',
      'Setting up your session...'
    ],
    loading: [
      'Loading your data...',
      'Fetching your profile...',
      'Getting everything ready...',
      'Just a moment...'
    ]
  };
  
  return messages[stage][Math.floor(Math.random() * messages[stage].length)];
}
