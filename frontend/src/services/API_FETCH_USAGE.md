# apiFetch Usage Guide

The `apiFetch` function is a clean, typed wrapper around the native Fetch API that integrates with our API URL builder.

## Features

- ✅ **Type-safe**: Generic type parameter for response data
- ✅ **Credentials**: Automatically includes credentials for authenticated requests
- ✅ **Headers**: Sets `Content-Type: application/json` by default
- ✅ **Error handling**: Throws clear errors for non-OK responses
- ✅ **URL building**: Uses the `apiUrl` helper to construct full URLs

## Basic Usage

```typescript
import { apiFetch } from '@/services/api';

// Simple GET request
const user = await apiFetch<User>("/api/auth/me");
console.log(user.name);

// With options
const posts = await apiFetch<Post[]>("/api/posts", {
  method: "GET",
});
```

## POST Request

```typescript
import { apiFetch } from '@/services/api';

interface CreatePostData {
  content: string;
  image_url?: string;
}

interface CreatePostResponse {
  success: boolean;
  post: Post;
}

const response = await apiFetch<CreatePostResponse>("/api/posts", {
  method: "POST",
  body: JSON.stringify({
    content: "Hello world!",
    image_url: "https://example.com/image.jpg"
  })
});
```

## Custom Headers

```typescript
import { apiFetch } from '@/services/api';

const data = await apiFetch<Data>("/api/endpoint", {
  headers: {
    "Authorization": "Bearer token123",
    "X-Custom-Header": "custom-value"
  }
});

// Note: Content-Type: application/json is automatically added
// and merged with your custom headers
```

## Error Handling

```typescript
import { apiFetch } from '@/services/api';

try {
  const data = await apiFetch<User>("/api/auth/me");
  console.log("Success:", data);
} catch (error) {
  console.error("API Error:", error.message);
  // Error message format: "API error {status}"
  // e.g., "API error 404", "API error 500"
}
```

## Type Safety

```typescript
import { apiFetch } from '@/services/api';

// Define your response type
interface UserProfile {
  id: number;
  email: string;
  name: string;
  avatar_url?: string;
}

// TypeScript will enforce the type
const profile = await apiFetch<UserProfile>("/api/auth/profile");

// ✅ This works - TypeScript knows about these properties
console.log(profile.id);
console.log(profile.email);

// ❌ This fails - TypeScript catches the error
console.log(profile.nonExistentField); // Error!
```

## Comparison with Axios API

If you're used to the existing axios-based API, here's the comparison:

```typescript
// OLD: Using axios (still available)
import { authAPI } from '@/services/api';
const profile = await authAPI.getProfile();

// NEW: Using apiFetch (lighter, native Fetch API)
import { apiFetch } from '@/services/api';
const profile = await apiFetch<User>("/api/auth/profile");
```

Both approaches are valid. Use `apiFetch` when you want:
- Lightweight fetch-based requests
- Direct control over fetch options
- To avoid axios overhead

Use the existing axios APIs (authAPI, jobsAPI, etc.) when you want:
- Automatic retry logic
- Circuit breaker protection
- Backend wake-up handling (for Render free tier)
- Complex request interceptors

## Implementation Details

The `apiFetch` function:
1. Uses `apiUrl()` from `@/lib/api` to build full URLs
2. Automatically sets `credentials: "include"` for cookie-based auth
3. Sets `Content-Type: application/json` header by default
4. Merges any custom headers you provide
5. Throws an error if `response.ok` is false
6. Parses the response as JSON

```typescript
// Source code (for reference)
export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(apiUrl(path), {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {})
    }
  });

  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }

  return res.json();
}
```
