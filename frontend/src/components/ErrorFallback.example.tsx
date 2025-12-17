/**
 * ErrorFallback Component - Usage Examples
 * 
 * This file demonstrates how to use the ErrorFallback component with ErrorBoundary
 * for better error recovery UX in your React application.
 */

import { AIErrorBoundary } from './AIErrorBoundary';
import ErrorFallback from './ErrorFallback';

/**
 * Example 1: Basic Usage with Page Reload
 * This is the most common usage - simply reload the page on error
 */
export function Example1() {
  return (
    <AIErrorBoundary fallback={<ErrorFallback onRetry={() => location.reload()} />}>
      <YourComponent />
    </AIErrorBoundary>
  );
}

/**
 * Example 2: Custom Retry Logic
 * You can implement custom retry logic instead of just reloading
 */
export function Example2() {
  const handleRetry = () => {
    // Clear error state in your app
    console.log('Retrying...');
    
    // Optionally clear cached data
    localStorage.removeItem('temp_data');
    
    // Reload the page
    location.reload();
  };

  return (
    <AIErrorBoundary fallback={<ErrorFallback onRetry={handleRetry} />}>
      <YourComponent />
    </AIErrorBoundary>
  );
}

/**
 * Example 3: Navigate to Home on Error
 * Sometimes you want to navigate to a safe route instead of reloading
 */
export function Example3() {
  const handleRetry = () => {
    // Navigate to home page
    window.location.href = '/';
  };

  return (
    <AIErrorBoundary fallback={<ErrorFallback onRetry={handleRetry} />}>
      <YourComponent />
    </AIErrorBoundary>
  );
}

/**
 * Example 4: Wrap Specific Components
 * You can wrap individual components that might fail
 */
export function Example4() {
  return (
    <div>
      <Header />
      
      <AIErrorBoundary fallback={<ErrorFallback onRetry={() => location.reload()} />}>
        <CriticalDataComponent />
      </AIErrorBoundary>
      
      <Footer />
    </div>
  );
}

// Placeholder components for examples
function YourComponent() {
  return <div>Your app content here</div>;
}

function Header() {
  return <header>Header</header>;
}

function CriticalDataComponent() {
  return <div>Important data component</div>;
}

function Footer() {
  return <footer>Footer</footer>;
}
