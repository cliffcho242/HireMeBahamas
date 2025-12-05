/**
 * Connection Test Utility
 * 
 * Tests connectivity to the backend API and provides diagnostic information.
 * This helps diagnose issues where users can't log in due to connection problems.
 */

interface ConnectionTestResult {
  success: boolean;
  apiUrl: string;
  message: string;
  details: {
    healthCheck: boolean;
    healthStatus?: number;
    healthData?: Record<string, unknown>;
    errorType?: string;
    errorMessage?: string;
    timestamp: number;
  };
}

/**
 * Test connection to the backend API
 * 
 * @param apiUrl - The API base URL to test (e.g., 'https://api.example.com')
 * @returns Promise with connection test results
 */
export async function testConnection(apiUrl: string): Promise<ConnectionTestResult> {
  const timestamp = Date.now();
  
  try {
    console.log(`[ConnectionTest] Testing connection to: ${apiUrl}/api/health`);
    
    // Test health endpoint with timeout
    // Increased to 30 seconds to accommodate backend cold starts (Railway, Render, etc.)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
    const response = await fetch(`${apiUrl}/api/health`, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      },
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json();
      console.log('[ConnectionTest] ✅ Connection successful:', data);
      
      return {
        success: true,
        apiUrl,
        message: 'Backend is reachable and healthy',
        details: {
          healthCheck: true,
          healthStatus: response.status,
          healthData: data,
          timestamp,
        },
      };
    } else {
      console.error(`[ConnectionTest] ❌ Health check failed with status: ${response.status}`);
      
      return {
        success: false,
        apiUrl,
        message: `Backend returned error status: ${response.status}`,
        details: {
          healthCheck: false,
          healthStatus: response.status,
          errorType: 'HTTP_ERROR',
          errorMessage: response.statusText,
          timestamp,
        },
      };
    }
  } catch (error: unknown) {
    console.error('[ConnectionTest] ❌ Connection test failed:', error);
    
    let errorMessage = 'Unknown error';
    let errorType = 'UNKNOWN_ERROR';
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        errorMessage = 'Connection timeout - backend is starting up or not responding. This can take up to 60 seconds for cold starts. Please wait and try again.';
        errorType = 'TIMEOUT';
      } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Cannot reach backend - check if backend URL is correct and backend is running';
        errorType = 'NETWORK_ERROR';
      } else {
        errorMessage = error.message || 'Connection failed';
        errorType = 'CONNECTION_ERROR';
      }
    }
    
    return {
      success: false,
      apiUrl,
      message: errorMessage,
      details: {
        healthCheck: false,
        errorType,
        errorMessage,
        timestamp,
      },
    };
  }
}

/**
 * Get the current API URL being used by the application
 */
export function getCurrentApiUrl(): string {
  // Check environment variable first
  const envApiUrl = import.meta.env.VITE_API_URL;
  if (envApiUrl) {
    return envApiUrl;
  }
  
  // Otherwise, check if we're in production
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const isProduction = hostname === 'hiremebahamas.com' || 
                         hostname === 'www.hiremebahamas.com';
    const isVercel = hostname.includes('.vercel.app');
    
    if (isProduction || isVercel) {
      return window.location.origin;
    }
  }
  
  // Default for local development
  return 'http://127.0.0.1:8000';
}

/**
 * Run connection diagnostic and log results to console
 * This is useful for debugging connection issues
 */
export async function runConnectionDiagnostic(): Promise<void> {
  const apiUrl = getCurrentApiUrl();
  
  console.log('='.repeat(60));
  console.log('🔍 RUNNING CONNECTION DIAGNOSTIC');
  console.log('='.repeat(60));
  console.log('Current API URL:', apiUrl);
  console.log('Window Origin:', typeof window !== 'undefined' ? window.location.origin : 'N/A');
  console.log('Environment:', import.meta.env.MODE);
  console.log('VITE_API_URL:', import.meta.env.VITE_API_URL || 'not set');
  console.log('-'.repeat(60));
  
  const result = await testConnection(apiUrl);
  
  console.log('Test Result:', result.success ? '✅ SUCCESS' : '❌ FAILED');
  console.log('Message:', result.message);
  console.log('Details:', JSON.stringify(result.details, null, 2));
  console.log('='.repeat(60));
  
  if (!result.success) {
    console.error('⚠️  CONNECTION PROBLEM DETECTED');
    console.error('Possible solutions:');
    console.error('1. Check if backend is running');
    console.error('2. Verify VITE_API_URL environment variable is correct');
    console.error('3. Check if CORS is properly configured on backend');
    console.error('4. Try accessing backend directly:', `${apiUrl}/api/health`);
  }
}
