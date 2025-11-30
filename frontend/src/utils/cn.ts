/**
 * Utility function that combines clsx and tailwind-merge
 * for clean, conflict-free Tailwind CSS class merging
 */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combines clsx and tailwind-merge for optimal class name handling
 * - clsx: Conditionally join class names together
 * - twMerge: Merge Tailwind classes without conflicts
 * 
 * @example
 * cn('px-4 py-2', condition && 'bg-blue-500', 'px-8')
 * // Result: 'py-2 bg-blue-500 px-8' (px-4 is overridden by px-8)
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export default cn;
