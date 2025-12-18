/**
 * Subscription constants shared across the frontend
 */

export const SUBSCRIPTION_PLANS = {
  FREE: 'free',
  PRO: 'pro',
  BUSINESS: 'business',
  ENTERPRISE: 'enterprise',
} as const;

export type SubscriptionPlan = typeof SUBSCRIPTION_PLANS[keyof typeof SUBSCRIPTION_PLANS];

export const PLAN_NAMES: Record<SubscriptionPlan, string> = {
  [SUBSCRIPTION_PLANS.FREE]: 'Free',
  [SUBSCRIPTION_PLANS.PRO]: 'Pro',
  [SUBSCRIPTION_PLANS.BUSINESS]: 'Business',
  [SUBSCRIPTION_PLANS.ENTERPRISE]: 'Enterprise',
};

export const PLAN_PRICES: Record<SubscriptionPlan, string> = {
  [SUBSCRIPTION_PLANS.FREE]: '$0',
  [SUBSCRIPTION_PLANS.PRO]: '$9.99/mo',
  [SUBSCRIPTION_PLANS.BUSINESS]: '$29.99/mo',
  [SUBSCRIPTION_PLANS.ENTERPRISE]: 'Custom',
};

/**
 * Check if a plan is Pro or higher
 */
export function isPlanPro(plan: string): boolean {
  return [
    SUBSCRIPTION_PLANS.PRO,
    SUBSCRIPTION_PLANS.BUSINESS,
    SUBSCRIPTION_PLANS.ENTERPRISE,
  ].includes(plan as SubscriptionPlan);
}

/**
 * Check if a plan is Business or higher
 */
export function isPlanBusiness(plan: string): boolean {
  return [
    SUBSCRIPTION_PLANS.BUSINESS,
    SUBSCRIPTION_PLANS.ENTERPRISE,
  ].includes(plan as SubscriptionPlan);
}

/**
 * Check if a plan is Enterprise
 */
export function isPlanEnterprise(plan: string): boolean {
  return plan === SUBSCRIPTION_PLANS.ENTERPRISE;
}
