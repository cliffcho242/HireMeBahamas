# A/B Testing Framework (Lightweight)

A simple, client-side A/B testing framework for the HireMeBahamas platform that requires no backend infrastructure and enables safe, controlled feature rollout without redeployment.

## 🎯 Goals

- **Test UI variations** - Compare different user interface designs
- **Test CTAs** - Optimize call-to-action buttons and messaging
- **Test onboarding flows** - Improve user onboarding experience
- **No redeploy needed** - Changes happen client-side
- **Safe rollout** - Persistent variant assignment per user

## ✨ Features

- ✅ **No Backend Required** - Everything runs in the browser
- ✅ **Persistent Assignment** - Users see the same variant across sessions
- ✅ **Type-Safe** - Full TypeScript support
- ✅ **Error Handling** - Graceful fallbacks for edge cases
- ✅ **Multi-Variant Support** - Test 2+ variations simultaneously
- ✅ **Easy Integration** - Drop into any React component

## 📦 Installation

The A/B testing utilities are already included in the project:

```typescript
import { abVariant } from '@/utils/abTest';
```

## 🚀 Quick Start

### Basic Usage

```tsx
import { abVariant } from '@/utils/abTest';

function SignupButton() {
  const ctaVariant = abVariant("signup-cta", ["A", "B"]);

  return ctaVariant === "A" ? (
    <button>Join Now</button>
  ) : (
    <button>Get Started</button>
  );
}
```

### Multi-Variant Test

```tsx
import { abVariant } from '@/utils/abTest';

function ButtonColorTest() {
  const colorVariant = abVariant("button-color", ["blue", "green", "purple"]);

  const colors = {
    blue: "bg-blue-600",
    green: "bg-green-600", 
    purple: "bg-purple-600"
  };

  return (
    <button className={colors[colorVariant]}>
      Sign Up
    </button>
  );
}
```

## 📚 API Reference

### `abVariant(key: string, variants: string[]): string`

Gets or assigns an A/B test variant for a user. The variant is stored in localStorage to ensure a consistent experience across sessions.

**Parameters:**
- `key` - Unique identifier for the A/B test (e.g., "signup-cta")
- `variants` - Array of variant names (e.g., ["A", "B"] or ["control", "variant1", "variant2"])

**Returns:** The assigned variant for this user

**Example:**
```tsx
const variant = abVariant("homepage-layout", ["grid", "list", "card"]);
```

### `clearAbVariant(key: string): void`

Clears a specific A/B test variant assignment. Useful for testing or resetting experiments.

**Example:**
```tsx
clearAbVariant("signup-cta");
```

### `getAbVariant(key: string): string | null`

Gets the current variant assignment without modifying it. Returns null if no variant has been assigned yet.

**Example:**
```tsx
const currentVariant = getAbVariant("signup-cta");
if (currentVariant) {
  console.log(`User is in variant: ${currentVariant}`);
}
```

### `clearAllAbVariants(): void`

Clears all A/B test variant assignments. Useful for development or testing.

**Example:**
```tsx
clearAllAbVariants();
```

## 💡 Usage Examples

### Example 1: CTA Button Test

Test different call-to-action button text:

```tsx
import { abVariant } from '@/utils/abTest';

function CTAButton() {
  const variant = abVariant("cta-text", ["A", "B"]);
  
  return (
    <button className="bg-blue-600 text-white px-6 py-2 rounded-lg">
      {variant === "A" ? "Join Now" : "Get Started"}
    </button>
  );
}
```

### Example 2: Layout Variation

Test different card layouts:

```tsx
import { abVariant } from '@/utils/abTest';

function JobCard({ job }) {
  const layout = abVariant("job-card-layout", ["compact", "spacious"]);
  
  if (layout === "compact") {
    return (
      <div className="p-3 border rounded">
        <h3 className="text-lg">{job.title}</h3>
        <p className="text-sm">{job.company}</p>
      </div>
    );
  }
  
  return (
    <div className="p-6 border rounded shadow-lg">
      <h3 className="text-2xl font-bold">{job.title}</h3>
      <p className="text-base mt-2">{job.company}</p>
    </div>
  );
}
```

### Example 3: Onboarding Flow

Test different onboarding experiences:

```tsx
import { abVariant } from '@/utils/abTest';

function OnboardingFlow() {
  const flow = abVariant("onboarding", ["single-step", "multi-step"]);
  
  if (flow === "single-step") {
    return <SingleStepOnboarding />;
  }
  
  return <MultiStepOnboarding />;
}
```

### Example 4: Color Scheme Test

Test different color schemes:

```tsx
import { abVariant } from '@/utils/abTest';

function ThemedButton() {
  const theme = abVariant("button-theme", ["blue", "green", "purple"]);
  
  const themes = {
    blue: "bg-blue-600 hover:bg-blue-700",
    green: "bg-green-600 hover:bg-green-700",
    purple: "bg-purple-600 hover:bg-purple-700"
  };
  
  return (
    <button className={`${themes[theme]} text-white px-6 py-2 rounded`}>
      Sign Up
    </button>
  );
}
```

## 🎨 Demo Component

Check out the comprehensive demo at `frontend/src/components/ABTestExample.tsx` which includes:

- CTA button variations
- Button color tests
- Card layout variations
- Onboarding flow tests
- Admin panel for managing tests

To use the demo:

```tsx
import ABTestExamples from '@/components/ABTestExample';

function DemoPage() {
  return <ABTestExamples />;
}
```

## 🧪 Testing

Tests are located in `frontend/test/abTest.test.ts` and cover:

- ✅ Variant assignment
- ✅ Persistence across calls
- ✅ localStorage integration
- ✅ Multi-variant support
- ✅ Error handling
- ✅ Distribution fairness

To run tests (if vitest is configured):
```bash
npm test
```

## 🔒 Error Handling

The framework handles several edge cases gracefully:

- **localStorage unavailable** - Falls back to first variant
- **localStorage quota exceeded** - Falls back to first variant
- **Invalid inputs** - Returns sensible defaults
- **SSR environments** - Returns first variant

## 📊 Best Practices

### 1. Use Descriptive Keys

```tsx
// ✅ Good - Clear and descriptive
abVariant("signup-button-cta", ["A", "B"])

// ❌ Bad - Vague
abVariant("test1", ["A", "B"])
```

### 2. Keep Variant Names Simple

```tsx
// ✅ Good - Simple and clear
abVariant("layout", ["compact", "spacious"])

// ❌ Bad - Too complex
abVariant("layout", ["super-compact-with-icons", "spacious-with-large-text"])
```

### 3. Document Your Tests

```tsx
/**
 * A/B Test: Signup Button CTA
 * Testing: "Join Now" vs "Get Started"
 * Hypothesis: "Get Started" will have higher conversion
 * Started: 2024-12-17
 */
const ctaVariant = abVariant("signup-cta", ["A", "B"]);
```

### 4. Clean Up Old Tests

When an experiment concludes, remove the A/B test code and keep the winning variant:

```tsx
// Before (A/B test)
const variant = abVariant("button-text", ["A", "B"]);
return variant === "A" ? "Join Now" : "Get Started";

// After (winner implemented)
return "Get Started"; // Variant B won
```

### 5. Track Metrics Separately

This framework handles variant assignment. You'll need to track metrics separately:

```tsx
const variant = abVariant("signup-cta", ["A", "B"]);

const handleClick = () => {
  // Track the conversion
  analytics.track('signup_button_clicked', { variant });
  
  // Proceed with signup
  navigateToSignup();
};
```

## 🔧 Integration with Analytics

### With Google Analytics

```tsx
import { abVariant } from '@/utils/abTest';

function TrackedComponent() {
  const variant = abVariant("feature-test", ["A", "B"]);
  
  useEffect(() => {
    // Send variant to Google Analytics
    gtag('event', 'ab_test_assigned', {
      test_name: 'feature-test',
      variant: variant
    });
  }, [variant]);
  
  return <YourComponent variant={variant} />;
}
```

### With Custom Analytics

```tsx
import { abVariant } from '@/utils/abTest';
import { analytics } from '@/services/analytics';

function TrackedComponent() {
  const variant = abVariant("feature-test", ["A", "B"]);
  
  useEffect(() => {
    analytics.track('AB Test Assigned', {
      testName: 'feature-test',
      variant: variant,
      timestamp: new Date().toISOString()
    });
  }, [variant]);
  
  return <YourComponent variant={variant} />;
}
```

## 🚦 Workflow

1. **Create Test** - Add `abVariant()` to your component
2. **Deploy** - Push to production (no backend changes needed)
3. **Collect Data** - Let users interact with both variants
4. **Analyze** - Review metrics from your analytics platform
5. **Implement Winner** - Remove A/B test, keep winning variant
6. **Clean Up** - Clear test data with `clearAbVariant()`

## 🎯 Use Cases

- **Landing Page Optimization** - Test different hero sections
- **Signup Flow** - Compare single-step vs multi-step forms
- **CTA Buttons** - Test button text, colors, and sizes
- **Navigation** - Compare different menu layouts
- **Job Listings** - Test card vs list vs grid layouts
- **Pricing Pages** - Test different pricing presentations
- **Onboarding** - Optimize new user experience
- **Feature Rollouts** - Gradually release new features

## 🛠️ Development Tips

### Testing Locally

```tsx
// In browser console
localStorage.clear(); // Clear all storage
// OR
localStorage.removeItem('ab-signup-cta'); // Clear specific test
// Then refresh page to get new assignment
```

### Debug Mode

Add debug logging to see which variant is assigned:

```tsx
const variant = abVariant("test-name", ["A", "B"]);
console.log(`AB Test: test-name = ${variant}`);
```

## 📝 Notes

- Variants are assigned randomly using `Math.random()`
- Assignment happens on first component render
- localStorage key format: `ab-{test-key}`
- Works in all modern browsers with localStorage support
- No cookies, no tracking, no external dependencies

## 🤝 Contributing

To add new features to the A/B testing framework:

1. Update `frontend/src/utils/abTest.ts`
2. Add tests to `frontend/test/abTest.test.ts`
3. Update this documentation
4. Add examples to `frontend/src/components/ABTestExample.tsx`

## 📄 License

Part of the HireMeBahamas platform.

---

**Happy Testing! 🎉**
