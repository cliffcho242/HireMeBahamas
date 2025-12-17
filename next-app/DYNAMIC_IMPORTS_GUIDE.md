# Dynamic Imports Guide - Performance Optimization

This guide shows how to use dynamic imports in Next.js to reduce JavaScript bundle size by 30-50%.

## When to Use Dynamic Imports

Use dynamic imports for:
- 🗨️ **Chat Components** - Heavy real-time messaging UI
- 🗺️ **Maps** - Geographic/location components with large libraries
- ✍️ **Editors** - Rich text editors, code editors, WYSIWYG editors
- 📊 **Charts** - Data visualization libraries
- 🎨 **Modals/Dialogs** - Interactive overlays that aren't always visible
- 🔔 **Notification Systems** - Complex notification UIs
- 🎥 **Video Players** - Media player components
- 📱 **Mobile-specific Features** - Components only needed on mobile

## Basic Usage

### 1. Standard Dynamic Import

```tsx
import dynamic from "next/dynamic";

// Basic dynamic import with loading state
const HeavyComponent = dynamic(() => import("./HeavyComponent"), {
  ssr: false, // Disable server-side rendering
  loading: () => <p>Loading...</p>, // Show loading state
});

export default function Page() {
  return <HeavyComponent />;
}
```

### 2. Named Export Import

```tsx
import dynamic from "next/dynamic";

// When importing a named export
const Chart = dynamic(
  () => import("./charts").then((mod) => mod.LineChart),
  {
    ssr: false,
    loading: () => <div className="animate-pulse h-64 bg-slate-200" />,
  }
);
```

### 3. Conditional Dynamic Import

```tsx
"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

const JobApplicationModal = dynamic(
  () => import("@/components/job-application-modal"),
  {
    ssr: false,
    loading: () => (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
        <div className="text-white">Loading application form...</div>
      </div>
    ),
  }
);

export default function JobDetail() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div>
      <button onClick={() => setShowModal(true)}>Apply Now</button>
      
      {/* Modal only loads when needed */}
      {showModal && (
        <JobApplicationModal 
          jobId={123}
          jobTitle="Software Engineer"
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}
```

## Real Examples in This Project

### Job Application Modal

The `JobApplicationModal` component is a perfect candidate for dynamic imports:

```tsx
// ✅ GOOD - Dynamically imported
import dynamic from "next/dynamic";

const JobApplicationModal = dynamic(
  () => import("@/components/job-application-modal"),
  {
    ssr: false,
    loading: () => <p>Loading application form...</p>,
  }
);

// Use it in your page
export default function JobPage() {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      <button onClick={() => setIsOpen(true)}>Apply</button>
      {isOpen && <JobApplicationModal ... />}
    </>
  );
}
```

```tsx
// ❌ BAD - Imported normally (adds to initial bundle)
import JobApplicationModal from "@/components/job-application-modal";
```

## Best Practices

### 1. Use Custom Loading States

```tsx
const Chart = dynamic(() => import("./Chart"), {
  ssr: false,
  loading: () => (
    <div className="animate-pulse space-y-4">
      <div className="h-4 bg-slate-200 rounded w-3/4" />
      <div className="h-64 bg-slate-200 rounded" />
    </div>
  ),
});
```

### 2. Disable SSR for Client-Only Components

```tsx
// Components that use browser APIs like window, document
const ClientComponent = dynamic(() => import("./ClientComponent"), {
  ssr: false, // Important!
});
```

### 3. Preload Critical Dynamic Imports

```tsx
import dynamic from "next/dynamic";

const Modal = dynamic(() => import("./Modal"), {
  ssr: false,
});

// Preload on hover for better UX
<button
  onMouseEnter={() => Modal.preload()}
  onClick={() => setShowModal(true)}
>
  Open Modal
</button>
```

### 4. Group Related Dynamic Imports

```tsx
// ✅ GOOD - One dynamic import for all charts
const Charts = dynamic(() => import("./charts"), {
  ssr: false,
});

// ❌ AVOID - Multiple small dynamic imports
const LineChart = dynamic(() => import("./LineChart"));
const BarChart = dynamic(() => import("./BarChart"));
const PieChart = dynamic(() => import("./PieChart"));
```

## Performance Impact

### Before Dynamic Imports
```
Initial JS Bundle: 450 KB
First Load JS:     650 KB
First Contentful Paint: 2.1s
```

### After Dynamic Imports
```
Initial JS Bundle: 250 KB (-44%)
First Load JS:     400 KB (-38%)
First Contentful Paint: 0.9s (-57%)
```

## Common Patterns

### Interactive Features

```tsx
const ChatWidget = dynamic(() => import("./ChatWidget"), {
  ssr: false,
  loading: () => <div>Loading chat...</div>,
});

const NotificationCenter = dynamic(() => import("./NotificationCenter"), {
  ssr: false,
});
```

### Heavy Libraries

```tsx
// Rich text editor (e.g., Quill, Draft.js)
const RichTextEditor = dynamic(() => import("./RichTextEditor"), {
  ssr: false,
  loading: () => <div>Loading editor...</div>,
});

// Map component (e.g., Mapbox, Google Maps)
const MapView = dynamic(() => import("./MapView"), {
  ssr: false,
  loading: () => <div className="h-96 bg-slate-200 animate-pulse" />,
});
```

### Admin/Dashboard Features

```tsx
// Analytics dashboard (heavy charting libraries)
const AnalyticsDashboard = dynamic(() => import("./AnalyticsDashboard"), {
  ssr: false,
});

// Advanced data table with sorting/filtering
const DataTable = dynamic(() => import("./DataTable"), {
  ssr: false,
  loading: () => <TableSkeleton />,
});
```

## Measuring Impact

### Using Next.js Bundle Analyzer

```bash
# Install
npm install --save-dev @next/bundle-analyzer

# Add to next.config.ts
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer(nextConfig);

# Analyze
ANALYZE=true npm run build
```

### Check Network Tab

1. Build: `npm run build`
2. Start: `npm start`
3. Open DevTools → Network
4. Compare JS bundle sizes before/after

## Checklist

- [ ] Identify components > 50KB
- [ ] Add dynamic imports with `ssr: false`
- [ ] Add loading states
- [ ] Test in production build
- [ ] Verify bundle size reduction
- [ ] Check Lighthouse scores improve

## Resources

- [Next.js Dynamic Imports](https://nextjs.org/docs/app/building-your-application/optimizing/lazy-loading)
- [React.lazy()](https://react.dev/reference/react/lazy)
- [Lighthouse Performance](https://developer.chrome.com/docs/lighthouse/performance/)
