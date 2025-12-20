/**
 * Connection Test Utility
 * 
 * Tests connectivity to the backend API and provides diagnostic information.
 * This helps diagnose issues where users can't log in due to connection problems.
 */

import { apiUrl, getApiBase } from '../lib/api';

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
 * @param baseUrl - The API base URL to test (e.g., 'https://api.example.com')
 * @returns Promise with connection test results
 */
export async function testConnection(baseUrl: string): Promise<ConnectionTestResult> {
  const timestamp = Date.now();
  
  try {
    const healthUrl = apiUrl('/api/health');
    console.log(`[ConnectionTest] Testing connection to: ${healthUrl}`);
    
    // Test health endpoint with timeout
    // 10 seconds timeout - backend is always on (Render Standard plan)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const response = await fetch(healthUrl, {
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
        apiUrl: baseUrl,
        message: 'Backend is reachable and healthy',
        details: {
          healthCheck: true,
          healthStatus: response.status,
          healthData: data,
          timestamp,
        },
      };
    } else if (response.status === 404) {
      console.error('[ConnectionTest] ❌ Backend endpoint not found (404)');
      
      return {
        success: false,
        apiUrl: baseUrl,
        message: 'Cannot connect to the server. The server may be unreachable or the URL may be incorrect.',
        details: {
          healthCheck: false,
          healthStatus: response.status,
          errorType: 'ENDPOINT_NOT_FOUND',
          errorMessage: 'Health check endpoint returned 404. This usually means the backend is unreachable or misconfigured.',
          timestamp,
        },
      };
    } else {
      console.error(`[ConnectionTest] ❌ Health check failed with status: ${response.status}`);
      
      return {
        success: false,
        apiUrl: baseUrl,
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
        errorMessage = 'Connection timeout - server is not responding. Please check your internet connection and try again.';
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
      apiUrl: baseUrl,
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
 * ✅ CORRECT: Use VITE_API_URL environment variable (properly exposed to browser by Vite)
 */
export function getCurrentApiUrl(): string {
  return getApiBase();
}

/**
 * Run connection diagnostic and log results to console
 * This is useful for debugging connection issues
 */
export async function runConnectionDiagnostic(): Promise<void> {
  const baseUrl = getCurrentApiUrl();
  
  console.log('='.repeat(60));
  console.log('🔍 RUNNING CONNECTION DIAGNOSTIC');
  console.log('='.repeat(60));
  console.log('Current API URL:', baseUrl);
  console.log('Window Origin:', typeof window !== 'undefined' ? window.location.origin : 'N/A');
  console.log('Environment:', import.meta.env.MODE);
  console.log('VITE_API_URL:', import.meta.env.VITE_API_URL || 'not set');
  console.log('-'.repeat(60));
  
  const result = await testConnection(baseUrl);
  
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
    console.error('4. Try accessing backend directly:', apiUrl('/api/health'));
  }
}
