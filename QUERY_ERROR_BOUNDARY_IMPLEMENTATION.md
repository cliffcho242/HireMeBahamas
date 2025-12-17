# QueryErrorBoundary Implementation

## Overview

This document describes the implementation of a global ErrorBoundary that wraps the QueryClientProvider for React Query v5 with Edge Runtime compatibility.

## Problem Statement

Add global ErrorBoundary wrapping QueryClientProvider for React Query v5 + Edge compatibility.

## Solution

### 1. New Component: QueryErrorBoundary

Created a new error boundary component specifically designed for React Query v5:

**File:** `frontend/src/components/QueryErrorBoundary.tsx`

**Key Features:**
- ✅ React Query v5 compatible (supports `throwOnError` instead of deprecated `useErrorBoundary`)
- ✅ Edge Runtime compatible (no Node.js APIs)
- ✅ Graceful error recovery with reset capability
- ✅ User-friendly error UI with actionable buttons
- ✅ Development-only error details for debugging
- ✅ Proper error logging for monitoring

**Edge Runtime Compatibility:**
- Uses only standard JavaScript and Web APIs
- No Node.js-specific functionality
- Compatible with Vercel Edge Functions
- Class-based component (fully supported)

### 2. Updated App Component Structure

**File:** `frontend/src/App.tsx`

The component hierarchy is now:

```
AIMonitoringProvider
└── AIErrorBoundary (catches all errors)
    └── QueryErrorBoundary (catches React Query errors)
        └── QueryClientProvider (React Query provider)
            └── Router, AuthProvider, etc.
```

**Key Changes:**
1. Added `QueryErrorBoundary` import
2. Wrapped `QueryClientProvider` with `QueryErrorBoundary`
3. Added `onReset` callback to clear query cache on error recovery

```tsx
<QueryErrorBoundary
  onReset={() => {
    // Reset query cache on error boundary reset
    queryClient.clear();
  }}
>
  <QueryClientProvider client={queryClient}>
    {/* App content */}
  </QueryClientProvider>
</QueryErrorBoundary>
```

### 3. React Query Configuration

**File:** `frontend/src/config/reactQuery.ts`

**Updated Configuration:**
- Clarified that `throwOnError` is set to `false` by default for queries
- This allows individual queries to opt-in to error boundary handling
- Mutations still have `throwOnError: true` for predictable error handling

```typescript
queries: {
  // React Query v5: useErrorBoundary removed, use throwOnError instead
  // Set throwOnError to true to enable error boundary integration
  // This ensures React Query errors are caught by the QueryErrorBoundary
  throwOnError: false, // Default is false, can be overridden per-query
  // ... other config
}
```

### 4. Component Exports

**File:** `frontend/src/components/index.ts`

Added exports for:
- `QueryErrorBoundary` - Main error boundary component
- `QueryErrorBoundaryTest` - Test component for manual verification

## Testing

### Manual Testing

A test component is available at: `frontend/src/components/QueryErrorBoundaryTest.tsx`

**To test:**

1. Add the test route to your App.tsx (optional):
   ```tsx
   import { QueryErrorBoundaryTest } from './components'
   
   // In your routes:
   <Route path="/test-error-boundary" element={<QueryErrorBoundaryTest />} />
   ```

2. Navigate to `/test-error-boundary`

3. Test scenarios:
   - **Test 1:** Component error - Verifies error boundary catches component errors
   - **Test 2:** React Query error - Verifies error boundary catches React Query errors with `throwOnError: true`

### Expected Behavior

When an error is caught:
1. The entire page is replaced with the error boundary fallback UI
2. A friendly error message is shown: "Oops! Something went wrong"
3. Two action buttons are provided:
   - **Try Again:** Resets the error state and clears query cache
   - **Go to Home:** Navigates to the home page
4. In development mode, detailed error information is displayed

## React Query v5 Migration Notes

### Key Changes from v4 to v5

1. **useErrorBoundary → throwOnError**
   - v4: `useErrorBoundary: true`
   - v5: `throwOnError: true`

2. **Query Configuration**
   - Default: `throwOnError: false` (errors handled locally)
   - Per-query override: `throwOnError: true` (errors thrown to boundary)

3. **Backward Compatibility**
   - The implementation maintains backward compatibility
   - Existing queries continue to work as expected
   - New queries can opt-in to error boundary handling

## Edge Runtime Compatibility

### What Makes It Edge-Compatible

1. **No Node.js APIs:**
   - No `fs`, `path`, `crypto`, etc.
   - Uses only standard Web APIs

2. **Standard JavaScript:**
   - ES6+ features only
   - No Node.js-specific modules

3. **React Class Component:**
   - Fully supported in Edge Runtime
   - Standard React lifecycle methods

4. **Web APIs Used:**
   - `console.log/error` ✓
   - `window.location` ✓
   - `localStorage` ✓ (available in Edge)
   - `Date.now()` ✓

### Vercel Edge Functions Support

The QueryErrorBoundary is fully compatible with:
- ✅ Vercel Edge Functions
- ✅ Vercel Edge Middleware
- ✅ Vercel Serverless Functions
- ✅ Standard browser environments

## Benefits

1. **Improved Error Handling:**
   - Catches React Query errors at the application level
   - Prevents app crashes from unhandled promise rejections
   - Provides graceful degradation

2. **Better User Experience:**
   - User-friendly error messages
   - Clear recovery options
   - No confusing error screens

3. **Developer Experience:**
   - Easy to debug with development error details
   - Clear error logging
   - Flexible error recovery strategies

4. **Production Ready:**
   - Edge Runtime compatible
   - Optimized for Vercel deployments
   - Proper error tracking capabilities

## Best Practices

### When to Use throwOnError: true

Use `throwOnError: true` in individual queries when:
- The error is critical and should stop the entire component tree
- You want the error boundary to handle the error globally
- The query is essential for the page to function

Example:
```typescript
const { data } = useQuery({
  queryKey: ['critical-data'],
  queryFn: fetchCriticalData,
  throwOnError: true, // Error will be caught by QueryErrorBoundary
});
```

### When to Handle Errors Locally

Keep `throwOnError: false` (default) when:
- The error is recoverable locally
- You want to show inline error messages
- The component can function without the data

Example:
```typescript
const { data, error } = useQuery({
  queryKey: ['optional-data'],
  queryFn: fetchOptionalData,
  // throwOnError: false (default)
});

if (error) {
  return <InlineError error={error} />;
}
```

## Files Changed

1. ✅ `frontend/src/components/QueryErrorBoundary.tsx` (new)
2. ✅ `frontend/src/components/QueryErrorBoundaryTest.tsx` (new)
3. ✅ `frontend/src/components/index.ts` (updated)
4. ✅ `frontend/src/App.tsx` (updated)
5. ✅ `frontend/src/config/reactQuery.ts` (updated)

## Verification

- ✅ Linting passed
- ✅ Build successful
- ✅ No TypeScript errors
- ✅ Edge Runtime compatible
- ✅ React Query v5 compatible

## Future Enhancements

1. **Error Reporting Integration:**
   - Add integration with error tracking services (Sentry, LogRocket, etc.)
   - Track error patterns and frequencies

2. **Retry Strategies:**
   - Implement automatic retry logic for transient errors
   - Add exponential backoff for network errors

3. **Custom Fallback UI:**
   - Allow per-route custom error fallback components
   - Support different error UIs based on error type

4. **Analytics:**
   - Track error occurrences and recovery success rates
   - Monitor user behavior after errors

## Resources

- [React Query v5 Error Handling](https://tanstack.com/query/latest/docs/react/guides/error-handling)
- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [Vercel Edge Runtime](https://vercel.com/docs/functions/edge-functions/edge-runtime)
