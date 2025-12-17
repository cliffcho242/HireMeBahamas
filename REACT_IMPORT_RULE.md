# React Import Rule (PERMANENT)

## 📍 Rule:
**❌ NEVER import React unless you explicitly use it**

### ❌ Wrong
```typescript
import React from "react";
import { Component, ErrorInfo, ReactNode } from "react";
```

### ✅ Correct
```typescript
import { Component, ErrorInfo, ReactNode } from "react";
```
or nothing at all if you don't need any React imports.

## 🔒 Why?
The JSX runtime handles React automatically. With the new JSX transform introduced in React 17, you no longer need to import React for JSX to work.

## Configuration

Both `frontend` and `admin-panel` projects use:
- TypeScript with `"jsx": "react-jsx"` in `tsconfig.json`
- ESLint with rules to enforce this pattern

## ESLint Rules

The following ESLint rules are configured to enforce this pattern:

```javascript
{
  // Turn off the requirement to import React for JSX
  'react/react-in-jsx-scope': 'off',
  'react/jsx-uses-react': 'off',
}
```

## Examples from Codebase

### ✅ Correct Usage
```typescript
// frontend/src/App.tsx
import { useMemo, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
```

```typescript
// admin-panel/src/App.tsx
import { ReactNode } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

function PrivateRoute({ children }: { children: ReactNode }) {
  // ...
}
```

```typescript
// admin-panel/src/pages/Login.tsx
import { useState, FormEvent } from 'react';

const handleSubmit = async (e: FormEvent) => {
  // ...
}
```

### ❌ Wrong Usage (Fixed)
```typescript
// Before (Wrong):
function PrivateRoute({ children }: { children: React.ReactNode }) {
  // ...
}

// After (Correct):
import { ReactNode } from 'react';

function PrivateRoute({ children }: { children: ReactNode }) {
  // ...
}
```

## Files Modified

### admin-panel/src/App.tsx
- Added: `import { ReactNode } from 'react';`
- Changed: `React.ReactNode` → `ReactNode`

### admin-panel/src/pages/Login.tsx
- Added: `import { FormEvent } from 'react';`
- Changed: `React.FormEvent` → `FormEvent`

### admin-panel/src/pages/Settings.tsx
- Added: `import { FormEvent } from 'react';`
- Changed: `React.FormEvent` → `FormEvent`

### ESLint Configuration
- Updated: `frontend/eslint.config.js`
- Created: `admin-panel/eslint.config.js`
- Added: `eslint-plugin-react` to enforce rules

## Verification

Both projects have been verified to:
1. ✅ Lint successfully with no React import violations
2. ✅ Build successfully
3. ✅ Follow the permanent React import rule

## Linting

To check for violations:

```bash
# Frontend
cd frontend && npm run lint

# Admin Panel
cd admin-panel && npm run lint
```

## References
- [React 17 - Introducing the New JSX Transform](https://react.dev/blog/2020/09/22/introducing-the-new-jsx-transform)
- [ESLint Plugin React - react-in-jsx-scope](https://github.com/jsx-eslint/eslint-plugin-react/blob/master/docs/rules/react-in-jsx-scope.md)
