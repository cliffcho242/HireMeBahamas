/**
 * SkeletonLoaders - Loading placeholder components for instant perceived performance
 * 
 * These skeleton loaders match the exact structure of the real content,
 * providing users with immediate visual feedback while data loads.
 * This makes the app feel faster than Facebook by eliminating blank screens.
 * 
 * Features:
 * - Shimmer animation for engaging loading state
 * - Exact layout matching for smooth content swap
 * - GPU-accelerated animations for 60fps performance
 * - Responsive design matching the real components
 */

import { memo } from 'react';

// Base skeleton with shimmer animation
interface SkeletonBaseProps {
  className?: string;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

const roundedClasses: Record<string, string> = {
  none: '',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  full: 'rounded-full',
};

export const SkeletonBase = memo(function SkeletonBase({
  className = '',
  rounded = 'md',
}: SkeletonBaseProps) {
  return (
    <div
      className={`
        animate-pulse
        bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200
        ${roundedClasses[rounded]}
        ${className}
      `}
      aria-hidden="true"
    />
  );
});

/**
 * PostCardSkeleton - Loading state for social feed posts
 */
export const PostCardSkeleton = memo(function PostCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm p-4 mb-4 transform-gpu">
      {/* Header with avatar and name */}
      <div className="flex items-center gap-3 mb-4">
        <SkeletonBase className="w-10 h-10" rounded="full" />
        <div className="flex-1">
          <SkeletonBase className="h-4 w-32 mb-2" />
          <SkeletonBase className="h-3 w-24" />
        </div>
      </div>
      
      {/* Content */}
      <div className="space-y-2 mb-4">
        <SkeletonBase className="h-4 w-full" />
        <SkeletonBase className="h-4 w-3/4" />
        <SkeletonBase className="h-4 w-5/6" />
      </div>
      
      {/* Image placeholder */}
      <SkeletonBase className="h-48 w-full mb-4" rounded="lg" />
      
      {/* Actions bar */}
      <div className="flex items-center gap-6 pt-2 border-t border-gray-100">
        <SkeletonBase className="h-8 w-16" />
        <SkeletonBase className="h-8 w-16" />
        <SkeletonBase className="h-8 w-16" />
      </div>
    </div>
  );
});

/**
 * JobCardSkeleton - Loading state for job listings
 */
export const JobCardSkeleton = memo(function JobCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm p-4 mb-3 transform-gpu">
      {/* Company logo and info */}
      <div className="flex items-start gap-4">
        <SkeletonBase className="w-12 h-12 flex-shrink-0" rounded="lg" />
        <div className="flex-1 min-w-0">
          <SkeletonBase className="h-5 w-3/4 mb-2" />
          <SkeletonBase className="h-4 w-1/2 mb-3" />
          <div className="flex flex-wrap gap-2">
            <SkeletonBase className="h-6 w-20" rounded="full" />
            <SkeletonBase className="h-6 w-24" rounded="full" />
            <SkeletonBase className="h-6 w-16" rounded="full" />
          </div>
        </div>
      </div>
    </div>
  );
});

/**
 * UserCardSkeleton - Loading state for user profiles/suggestions
 */
export const UserCardSkeleton = memo(function UserCardSkeleton() {
  return (
    <div className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm transform-gpu">
      <SkeletonBase className="w-12 h-12 flex-shrink-0" rounded="full" />
      <div className="flex-1 min-w-0">
        <SkeletonBase className="h-4 w-28 mb-2" />
        <SkeletonBase className="h-3 w-36" />
      </div>
      <SkeletonBase className="h-8 w-20" rounded="full" />
    </div>
  );
});

/**
 * FeedSkeleton - Full feed loading state
 */
export const FeedSkeleton = memo(function FeedSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <PostCardSkeleton key={i} />
      ))}
    </div>
  );
});

/**
 * JobListSkeleton - Job listing page loading state
 */
export const JobListSkeleton = memo(function JobListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <JobCardSkeleton key={i} />
      ))}
    </div>
  );
});

/**
 * ProfileSkeleton - Profile page loading state
 */
export const ProfileSkeleton = memo(function ProfileSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden transform-gpu">
      {/* Cover photo */}
      <SkeletonBase className="h-32 sm:h-48 w-full" rounded="none" />
      
      {/* Profile info */}
      <div className="px-4 pb-4">
        {/* Avatar - overlapping cover */}
        <div className="-mt-12 mb-4">
          <SkeletonBase className="w-24 h-24 border-4 border-white" rounded="full" />
        </div>
        
        {/* Name and bio */}
        <SkeletonBase className="h-6 w-48 mb-2" />
        <SkeletonBase className="h-4 w-32 mb-4" />
        <SkeletonBase className="h-4 w-full mb-2" />
        <SkeletonBase className="h-4 w-3/4" />
        
        {/* Stats */}
        <div className="flex gap-6 mt-4 pt-4 border-t border-gray-100">
          <div>
            <SkeletonBase className="h-5 w-8 mb-1" />
            <SkeletonBase className="h-3 w-12" />
          </div>
          <div>
            <SkeletonBase className="h-5 w-8 mb-1" />
            <SkeletonBase className="h-3 w-16" />
          </div>
          <div>
            <SkeletonBase className="h-5 w-8 mb-1" />
            <SkeletonBase className="h-3 w-14" />
          </div>
        </div>
      </div>
    </div>
  );
});

/**
 * MessageListSkeleton - Messages page loading state
 */
export const MessageListSkeleton = memo(function MessageListSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="divide-y divide-gray-100">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-4 transform-gpu">
          <SkeletonBase className="w-12 h-12 flex-shrink-0" rounded="full" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <SkeletonBase className="h-4 w-32" />
              <SkeletonBase className="h-3 w-12" />
            </div>
            <SkeletonBase className="h-3 w-full" />
          </div>
        </div>
      ))}
    </div>
  );
});

/**
 * NotificationSkeleton - Notification list loading state
 */
export const NotificationSkeleton = memo(function NotificationSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="divide-y divide-gray-100">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-start gap-3 p-4 transform-gpu">
          <SkeletonBase className="w-10 h-10 flex-shrink-0" rounded="full" />
          <div className="flex-1 min-w-0">
            <SkeletonBase className="h-4 w-full mb-2" />
            <SkeletonBase className="h-3 w-2/3" />
          </div>
          <SkeletonBase className="w-2 h-2 flex-shrink-0" rounded="full" />
        </div>
      ))}
    </div>
  );
});

/**
 * StorySkeleton - Story circles loading state
 */
export const StorySkeleton = memo(function StorySkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex flex-col items-center gap-1 flex-shrink-0 transform-gpu">
          <SkeletonBase className="w-16 h-16" rounded="full" />
          <SkeletonBase className="h-3 w-12" />
        </div>
      ))}
    </div>
  );
});

/**
 * TableRowSkeleton - Table row loading state
 */
export const TableRowSkeleton = memo(function TableRowSkeleton({ columns = 4 }: { columns?: number }) {
  return (
    <tr className="animate-pulse">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <SkeletonBase className="h-4 w-full" />
        </td>
      ))}
    </tr>
  );
});

/**
 * CardGridSkeleton - Grid of card loading states
 */
export const CardGridSkeleton = memo(function CardGridSkeleton({ 
  count = 6,
  columns = 3 
}: { 
  count?: number;
  columns?: 2 | 3 | 4;
}) {
  const gridCols = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  };

  return (
    <div className={`grid gap-4 ${gridCols[columns]}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-white rounded-xl shadow-sm p-4 transform-gpu">
          <SkeletonBase className="h-32 w-full mb-4" rounded="lg" />
          <SkeletonBase className="h-5 w-3/4 mb-2" />
          <SkeletonBase className="h-4 w-full mb-2" />
          <SkeletonBase className="h-4 w-1/2" />
        </div>
      ))}
    </div>
  );
});

export default SkeletonBase;
