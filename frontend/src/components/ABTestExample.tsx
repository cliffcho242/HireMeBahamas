/**
 * A/B Test Example Component
 * 
 * This component demonstrates how to use the A/B testing framework
 * to test different UI variations, CTAs, and user experiences.
 * 
 * These examples can be integrated into any component in the application.
 */

import { useState } from 'react';
import { abVariant, getAbVariant, clearAbVariant } from '@/utils/abTest';

/**
 * Example 1: Simple CTA Button A/B Test
 * Test different call-to-action button text
 */
export function SignupCTAExample() {
  const ctaVariant = abVariant("signup-cta", ["A", "B"]);

  return (
    <div className="space-y-2">
      {ctaVariant === "A" ? (
        <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Join Now
        </button>
      ) : (
        <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Get Started
        </button>
      )}
      <p className="text-xs text-gray-500">Testing variant: {ctaVariant}</p>
    </div>
  );
}

/**
 * Example 2: Multi-variant Color Test
 * Test different button colors to see which performs best
 */
export function ButtonColorTest() {
  const colorVariant = abVariant("button-color", ["blue", "green", "purple"]);

  const colorClasses = {
    blue: "bg-blue-600 hover:bg-blue-700",
    green: "bg-green-600 hover:bg-green-700",
    purple: "bg-purple-600 hover:bg-purple-700",
  };

  return (
    <div className="space-y-2">
      <button 
        className={`px-6 py-2 text-white rounded-lg ${colorClasses[colorVariant as keyof typeof colorClasses]}`}
      >
        Sign Up Now
      </button>
      <p className="text-xs text-gray-500">Color variant: {colorVariant}</p>
    </div>
  );
}

/**
 * Example 3: Layout Variation Test
 * Test different card layouts to optimize user engagement
 */
export function CardLayoutTest() {
  const layoutVariant = abVariant("card-layout", ["compact", "spacious"]);

  if (layoutVariant === "compact") {
    return (
      <div className="border rounded-lg p-3 space-y-1">
        <h3 className="text-lg font-semibold">Job Title</h3>
        <p className="text-sm text-gray-600">Company Name</p>
        <p className="text-xs text-gray-500">Location</p>
        <button className="mt-2 text-sm px-3 py-1 bg-blue-600 text-white rounded">
          Apply
        </button>
        <p className="text-xs text-gray-400 mt-2">Layout: {layoutVariant}</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg p-6 space-y-3">
      <h3 className="text-xl font-bold">Job Title</h3>
      <p className="text-base text-gray-600">Company Name</p>
      <p className="text-sm text-gray-500">Location</p>
      <button className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg">
        Apply Now
      </button>
      <p className="text-xs text-gray-400 mt-2">Layout: {layoutVariant}</p>
    </div>
  );
}

/**
 * Example 4: Onboarding Flow Test
 * Test different onboarding experiences
 */
export function OnboardingFlowTest() {
  const flowVariant = abVariant("onboarding-flow", ["single-step", "multi-step"]);

  if (flowVariant === "single-step") {
    return (
      <div className="max-w-md mx-auto p-6 border rounded-lg">
        <h2 className="text-2xl font-bold mb-4">Complete Your Profile</h2>
        <form className="space-y-4">
          <input 
            type="text" 
            placeholder="Full Name" 
            className="w-full px-3 py-2 border rounded"
          />
          <input 
            type="email" 
            placeholder="Email" 
            className="w-full px-3 py-2 border rounded"
          />
          <input 
            type="text" 
            placeholder="Job Title" 
            className="w-full px-3 py-2 border rounded"
          />
          <button 
            type="submit" 
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Complete Setup
          </button>
        </form>
        <p className="text-xs text-gray-400 mt-4">Flow: {flowVariant}</p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-6 border rounded-lg">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-600">Step 1 of 3</span>
          <div className="flex space-x-1">
            <div className="w-8 h-1 bg-blue-600 rounded"></div>
            <div className="w-8 h-1 bg-gray-300 rounded"></div>
            <div className="w-8 h-1 bg-gray-300 rounded"></div>
          </div>
        </div>
        <h2 className="text-2xl font-bold">What's your name?</h2>
      </div>
      <form className="space-y-4">
        <input 
          type="text" 
          placeholder="Full Name" 
          className="w-full px-3 py-2 border rounded"
        />
        <button 
          type="submit" 
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg"
        >
          Continue
        </button>
      </form>
      <p className="text-xs text-gray-400 mt-4">Flow: {flowVariant}</p>
    </div>
  );
}

/**
 * Example 5: Admin Panel for A/B Tests
 * Shows current assignments and allows clearing for testing
 */
export function ABTestAdmin() {
  const tests = [
    { key: "signup-cta", variants: ["A", "B"] },
    { key: "button-color", variants: ["blue", "green", "purple"] },
    { key: "card-layout", variants: ["compact", "spacious"] },
    { key: "onboarding-flow", variants: ["single-step", "multi-step"] },
  ];

  // Use state to force re-render when variants are cleared
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="max-w-2xl mx-auto p-6 bg-gray-50 rounded-lg">
      <h2 className="text-2xl font-bold mb-4">A/B Test Dashboard</h2>
      <div className="space-y-3">
        {tests.map(test => {
          const currentVariant = getAbVariant(test.key);
          return (
            <div 
              key={`${test.key}-${refreshKey}`}
              className="bg-white p-4 rounded-lg border flex justify-between items-center"
            >
              <div>
                <h3 className="font-semibold">{test.key}</h3>
                <p className="text-sm text-gray-600">
                  Current: <span className="font-mono">{currentVariant || 'Not assigned'}</span>
                </p>
                <p className="text-xs text-gray-500">
                  Variants: {test.variants.join(', ')}
                </p>
              </div>
              <button
                onClick={() => {
                  clearAbVariant(test.key);
                  // Force re-render without page reload
                  setRefreshKey(prev => prev + 1);
                }}
                className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
              >
                Reset
              </button>
            </div>
          );
        })}
      </div>
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
        <h3 className="font-semibold text-blue-900 mb-2">How to Use</h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Variants are randomly assigned on first visit</li>
          <li>Assignment persists across page reloads</li>
          <li>Click "Reset" to clear and reassign a variant</li>
          <li>No backend or deployment needed for changes</li>
        </ul>
      </div>
    </div>
  );
}

/**
 * Combined Demo Component
 * Shows all examples together for testing
 */
export default function ABTestExamples() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">A/B Testing Examples</h1>
        <p className="text-gray-600 mb-6">
          Demonstrating lightweight client-side A/B testing for UI, CTAs, and user flows
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">CTA Button Test</h2>
          <SignupCTAExample />
        </div>

        <div className="border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Button Color Test</h2>
          <ButtonColorTest />
        </div>

        <div className="border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Card Layout Test</h2>
          <CardLayoutTest />
        </div>

        <div className="border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Onboarding Flow Test</h2>
          <OnboardingFlowTest />
        </div>
      </div>

      <ABTestAdmin />
    </div>
  );
}
