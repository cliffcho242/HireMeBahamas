# A/B Testing Integration Guide

Quick guide for integrating the A/B testing framework into existing HireMeBahamas components.

## Quick Integration Example

Here's how to add A/B testing to an existing button or component in 3 simple steps:

### Step 1: Import the utility

```tsx
import { abVariant } from '@/utils/abTest';
```

### Step 2: Get variant assignment

```tsx
function MyComponent() {
  const buttonVariant = abVariant("my-button-test", ["A", "B"]);
  
  // Rest of component...
}
```

### Step 3: Render based on variant

```tsx
return (
  <div>
    {buttonVariant === "A" ? (
      <button className="bg-blue-600">Join Now</button>
    ) : (
      <button className="bg-green-600">Get Started</button>
    )}
  </div>
);
```

## Real-World Integration Examples

### Example 1: Testing CTA in Login Page

```tsx
// In frontend/src/pages/Login.tsx

import { abVariant } from '@/utils/abTest';

export default function Login() {
  const ctaVariant = abVariant("login-cta", ["A", "B"]);
  
  return (
    <div className="login-container">
      <h1>Welcome Back</h1>
      <form>
        {/* Login form fields */}
      </form>
      
      {/* A/B tested CTA button */}
      <button type="submit" className="btn-primary">
        {ctaVariant === "A" ? "Sign In" : "Login"}
      </button>
      
      {/* Alternative: Test button style instead of text */}
      {/* <button 
        type="submit" 
        className={ctaVariant === "A" ? "btn-blue" : "btn-green"}
      >
        Sign In
      </button> */}
    </div>
  );
}
```

### Example 2: Testing Registration Form Layout

```tsx
// In frontend/src/pages/Register.tsx

import { abVariant } from '@/utils/abTest';

export default function Register() {
  const formLayout = abVariant("register-form", ["single-column", "two-column"]);
  
  if (formLayout === "single-column") {
    return (
      <div className="max-w-md mx-auto">
        <input type="text" placeholder="Full Name" className="w-full" />
        <input type="email" placeholder="Email" className="w-full" />
        <input type="password" placeholder="Password" className="w-full" />
        <button>Sign Up</button>
      </div>
    );
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="grid grid-cols-2 gap-4">
        <input type="text" placeholder="First Name" />
        <input type="text" placeholder="Last Name" />
        <input type="email" placeholder="Email" className="col-span-2" />
        <input type="password" placeholder="Password" className="col-span-2" />
        <button className="col-span-2">Sign Up</button>
      </div>
    </div>
  );
}
```

### Example 3: Testing Job Card Design

```tsx
// In frontend/src/components/JobCard.tsx

import { abVariant } from '@/utils/abTest';

interface JobCardProps {
  job: {
    title: string;
    company: string;
    location: string;
    salary: string;
  };
}

export function JobCard({ job }: JobCardProps) {
  const cardStyle = abVariant("job-card-style", ["minimal", "detailed"]);
  
  if (cardStyle === "minimal") {
    return (
      <div className="border rounded p-4">
        <h3 className="font-bold">{job.title}</h3>
        <p className="text-sm text-gray-600">{job.company}</p>
        <button className="mt-2 text-sm">Apply</button>
      </div>
    );
  }
  
  return (
    <div className="border rounded-lg p-6 shadow-md">
      <h3 className="text-xl font-bold mb-2">{job.title}</h3>
      <p className="text-base text-gray-700 mb-1">{job.company}</p>
      <p className="text-sm text-gray-500 mb-2">{job.location}</p>
      <p className="text-lg font-semibold text-green-600 mb-4">{job.salary}</p>
      <button className="bg-blue-600 text-white px-6 py-2 rounded-lg">
        Apply Now
      </button>
    </div>
  );
}
```

### Example 4: Testing Navigation Menu

```tsx
// In frontend/src/components/Navbar.tsx

import { abVariant } from '@/utils/abTest';

export function Navbar() {
  const navStyle = abVariant("nav-style", ["horizontal", "dropdown"]);
  
  const menuItems = [
    { label: "Jobs", path: "/jobs" },
    { label: "Messages", path: "/messages" },
    { label: "Profile", path: "/profile" },
  ];
  
  if (navStyle === "horizontal") {
    return (
      <nav className="flex space-x-4">
        {menuItems.map(item => (
          <a key={item.path} href={item.path}>{item.label}</a>
        ))}
      </nav>
    );
  }
  
  return (
    <nav>
      <button>Menu ▾</button>
      <div className="dropdown">
        {menuItems.map(item => (
          <a key={item.path} href={item.path}>{item.label}</a>
        ))}
      </div>
    </nav>
  );
}
```

## Testing Your Integration

### 1. Local Testing

After adding A/B test code, test both variants locally:

```javascript
// In browser console:

// Test Variant A
localStorage.setItem('ab-my-test-key', 'A');
location.reload();

// Test Variant B  
localStorage.setItem('ab-my-test-key', 'B');
location.reload();

// Reset (random assignment)
localStorage.removeItem('ab-my-test-key');
location.reload();
```

### 2. Verify Assignment Persistence

1. Open the page
2. Note which variant you see
3. Refresh the page
4. Verify you see the same variant

### 3. Check localStorage

```javascript
// In browser console:
localStorage.getItem('ab-my-test-key'); // Should show 'A' or 'B'
```

## Integration Checklist

Before deploying your A/B test:

- [ ] Import `abVariant` from `@/utils/abTest`
- [ ] Use a unique, descriptive test key
- [ ] Test both/all variants work correctly
- [ ] Verify localStorage persistence
- [ ] Test on different browsers
- [ ] Set up analytics tracking (if needed)
- [ ] Document the test (what, why, when)
- [ ] Plan how to determine the winner
- [ ] Plan cleanup after test concludes

## Common Patterns

### Pattern 1: Simple Toggle

```tsx
const variant = abVariant("feature-toggle", ["on", "off"]);
return variant === "on" ? <NewFeature /> : <OldFeature />;
```

### Pattern 2: Text Variations

```tsx
const text = abVariant("button-text", ["Join", "Start", "Begin"]);
return <button>{text} Now</button>;
```

### Pattern 3: Style Variations

```tsx
const style = abVariant("button-style", ["blue", "green", "red"]);
const colors = { blue: "bg-blue-600", green: "bg-green-600", red: "bg-red-600" };
return <button className={colors[style]}>Click Me</button>;
```

### Pattern 4: Layout Variations

```tsx
const layout = abVariant("layout", ["grid", "list"]);
return layout === "grid" ? (
  <div className="grid grid-cols-3">{children}</div>
) : (
  <div className="flex flex-col">{children}</div>
);
```

## Advanced Usage

### Combining Multiple Tests

```tsx
function ComplexComponent() {
  // Test multiple aspects independently
  const buttonColor = abVariant("button-color", ["blue", "green"]);
  const buttonText = abVariant("button-text", ["Join", "Start"]);
  const layout = abVariant("layout", ["compact", "spacious"]);
  
  return (
    <div className={layout === "compact" ? "p-2" : "p-6"}>
      <button className={`bg-${buttonColor}-600`}>
        {buttonText} Now
      </button>
    </div>
  );
}
```

### Conditional A/B Testing

```tsx
function ConditionalTest() {
  const isNewUser = useIsNewUser();
  
  // Only A/B test for new users
  const variant = isNewUser 
    ? abVariant("new-user-onboarding", ["A", "B"])
    : "default";
  
  return <Onboarding variant={variant} />;
}
```

## Tracking Results

### Option 1: Console Logging (Development)

```tsx
const variant = abVariant("test-name", ["A", "B"]);
console.log(`A/B Test: test-name assigned ${variant}`);
```

### Option 2: Analytics Integration

```tsx
import { abVariant } from '@/utils/abTest';

function TrackedComponent() {
  const variant = abVariant("test-name", ["A", "B"]);
  
  const handleClick = () => {
    // Track the conversion
    analytics.track('button_clicked', {
      test: 'test-name',
      variant: variant,
      timestamp: Date.now()
    });
    
    // Proceed with action
    doSomething();
  };
  
  return <button onClick={handleClick}>Click Me</button>;
}
```

## Cleanup After Test

Once you've determined a winner:

1. **Remove the A/B test code:**

```tsx
// Before (A/B test)
const variant = abVariant("button-test", ["A", "B"]);
return variant === "A" ? <ButtonA /> : <ButtonB />;

// After (winner: ButtonB)
return <ButtonB />;
```

2. **Clear user assignments (optional):**

```tsx
import { clearAbVariant } from '@/utils/abTest';
clearAbVariant("button-test");
```

3. **Document the results:**

```tsx
/**
 * A/B Test Results: button-test
 * Winner: Variant B
 * Tested: 2024-12-01 to 2024-12-15
 * Result: Variant B had 15% higher conversion rate
 * Implemented: 2024-12-17
 */
```

## Troubleshooting

### Variant Not Persisting

**Problem:** Getting different variants on refresh

**Solution:** Check if localStorage is enabled:
```javascript
// In console:
localStorage.setItem('test', 'value');
localStorage.getItem('test'); // Should return 'value'
```

### Same Variant Every Time

**Problem:** Always getting the same variant

**Solution:** Clear localStorage:
```javascript
localStorage.clear();
```

### TypeScript Errors

**Problem:** TypeScript compilation errors

**Solution:** Ensure proper imports:
```tsx
import { abVariant } from '@/utils/abTest';
// NOT: import abVariant from '@/utils/abTest';
```

## Need Help?

- Check the full documentation: `AB_TESTING_FRAMEWORK.md`
- View complete examples: `frontend/src/components/ABTestExample.tsx`
- Review tests: `frontend/test/abTest.test.ts`

---

**Ready to optimize! 🚀**
