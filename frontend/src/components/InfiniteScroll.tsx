/**
 * Addictive Infinite Scroll Component
 * 
 * Features:
 * - Cursor-based pagination (no page numbers)
 * - Prefetch next page on scroll
 * - Pull-to-refresh with overscroll glow
 * - Skeleton shimmer loading states
 * - Smooth scroll restoration
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { motion, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';

interface InfiniteScrollProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  loadMore: () => Promise<void>;
  hasMore: boolean;
  isLoading: boolean;
  onRefresh?: () => Promise<void>;
  keyExtractor: (item: T) => string | number;
  skeleton?: React.ReactNode;
  skeletonCount?: number;
  threshold?: number;
  className?: string;
  emptyState?: React.ReactNode;
}

/**
 * Skeleton shimmer component
 */
export function SkeletonShimmer({ 
  className = '', 
  width = '100%',
  height = 20,
  rounded = 'md'
}: { 
  className?: string;
  width?: string | number;
  height?: number;
  rounded?: 'sm' | 'md' | 'lg' | 'full';
}) {
  const roundedClasses = {
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  };

  // Normalize width to a valid CSS value
  const normalizedWidth = typeof width === 'number' ? `${width}px` : width;

  return (
    <div
      className={`animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 
        dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 
        bg-[length:200%_100%] ${roundedClasses[rounded]} ${className}`}
      style={{ width: normalizedWidth, height }}
    />
  );
}

/**
 * Post skeleton for feed loading
 */
export function PostSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <SkeletonShimmer width={48} height={48} rounded="full" />
        <div className="flex-1 space-y-2">
          <SkeletonShimmer width="40%" height={14} />
          <SkeletonShimmer width="25%" height={12} />
        </div>
      </div>
      
      {/* Content */}
      <div className="space-y-2 mb-4">
        <SkeletonShimmer width="100%" height={14} />
        <SkeletonShimmer width="90%" height={14} />
        <SkeletonShimmer width="75%" height={14} />
      </div>
      
      {/* Image placeholder */}
      <SkeletonShimmer width="100%" height={200} rounded="lg" className="mb-3" />
      
      {/* Actions */}
      <div className="flex gap-4">
        <SkeletonShimmer width={60} height={32} rounded="full" />
        <SkeletonShimmer width={60} height={32} rounded="full" />
        <SkeletonShimmer width={60} height={32} rounded="full" />
      </div>
    </div>
  );
}

/**
 * Pull to refresh indicator
 */
function PullToRefreshIndicator({ progress, isRefreshing }: { progress: number; isRefreshing: boolean }) {
  return (
    <motion.div
      className="absolute top-0 left-0 right-0 flex items-center justify-center overflow-hidden"
      style={{ height: Math.min(progress * 80, 80) }}
    >
      <motion.div
        className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full"
        animate={isRefreshing ? { rotate: 360 } : { rotate: progress * 360 }}
        transition={isRefreshing ? { duration: 1, repeat: Infinity, ease: 'linear' } : { duration: 0 }}
      />
      
      {/* Overscroll glow effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-b from-blue-100/50 to-transparent dark:from-blue-900/30"
        style={{ opacity: Math.min(progress, 1) * 0.5 }}
      />
    </motion.div>
  );
}

/**
 * Loading more indicator
 */
function LoadingMoreIndicator() {
  return (
    <div className="flex items-center justify-center py-6 gap-2">
      <motion.div
        className="flex gap-1"
        initial="start"
        animate="end"
        variants={{
          start: {},
          end: {},
        }}
      >
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="w-2 h-2 bg-blue-500 rounded-full"
            animate={{
              y: [0, -8, 0],
            }}
            transition={{
              duration: 0.6,
              repeat: Infinity,
              delay: i * 0.1,
              ease: [0.45, 0, 0.55, 1],
            }}
          />
        ))}
      </motion.div>
      <span className="text-sm text-gray-500 dark:text-gray-400">Loading more...</span>
    </div>
  );
}

/**
 * Main Infinite Scroll Component
 */
export function InfiniteScroll<T>({
  items,
  renderItem,
  loadMore,
  hasMore,
  isLoading,
  onRefresh,
  keyExtractor,
  skeleton = <PostSkeleton />,
  skeletonCount = 3,
  threshold = 0.8,
  className = '',
  emptyState,
}: InfiniteScrollProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadingRef = useRef<HTMLDivElement>(null);
  const touchStartY = useRef<number>(0);
  
  const [isRefreshing, setIsRefreshing] = useState(false);
  const pullProgress = useMotionValue(0);
  const translateY = useTransform(pullProgress, [0, 1], [0, 80]);

  // Prefetch trigger - start loading when 80% scrolled
  const handleIntersection = useCallback((entries: IntersectionObserverEntry[]) => {
    const entry = entries[0];
    if (entry.isIntersecting && hasMore && !isLoading) {
      loadMore();
    }
  }, [hasMore, isLoading, loadMore]);

  // Setup intersection observer for infinite scroll
  useEffect(() => {
    if (loadingRef.current) {
      observerRef.current = new IntersectionObserver(handleIntersection, {
        root: null,
        rootMargin: `${(1 - threshold) * 100}%`,
        threshold: 0,
      });
      observerRef.current.observe(loadingRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [handleIntersection, threshold]);

  // Pull to refresh handlers
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (containerRef.current?.scrollTop === 0) {
      touchStartY.current = e.touches[0].clientY;
    }
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!onRefresh || isRefreshing) return;
    
    const scrollTop = containerRef.current?.scrollTop ?? 0;
    if (scrollTop > 0) return;
    
    const currentY = e.touches[0].clientY;
    const diff = currentY - touchStartY.current;
    
    if (diff > 0) {
      e.preventDefault();
      // Elastic effect - diminishing returns as you pull more
      const progress = Math.min(diff / 150, 1.5);
      pullProgress.set(progress);
    }
  }, [onRefresh, isRefreshing, pullProgress]);

  const handleTouchEnd = useCallback(async () => {
    if (!onRefresh) return;
    
    const progress = pullProgress.get();
    
    if (progress >= 1 && !isRefreshing) {
      setIsRefreshing(true);
      pullProgress.set(1);
      
      try {
        await onRefresh();
      } finally {
        setIsRefreshing(false);
        pullProgress.set(0);
      }
    } else {
      pullProgress.set(0);
    }
  }, [onRefresh, pullProgress, isRefreshing]);

  // Initial loading state
  if (isLoading && items.length === 0) {
    return (
      <div className={`space-y-4 ${className}`}>
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <div key={i} className="animate-fade-in" style={{ animationDelay: `${i * 100}ms` }}>
            {skeleton}
          </div>
        ))}
      </div>
    );
  }

  // Empty state
  if (!isLoading && items.length === 0) {
    return (
      <div className={className}>
        {emptyState || (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">📭</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No content yet
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              Check back later for updates!
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <motion.div
      ref={containerRef}
      className={`relative overflow-y-auto ${className}`}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{ y: translateY }}
    >
      {/* Pull to refresh indicator */}
      {onRefresh && (
        <PullToRefreshIndicator 
          progress={pullProgress.get()} 
          isRefreshing={isRefreshing} 
        />
      )}

      {/* Items */}
      <AnimatePresence mode="popLayout">
        {items.map((item, index) => (
          <motion.div
            key={keyExtractor(item)}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ 
              duration: 0.3, 
              delay: Math.min(index * 0.05, 0.3),
              ease: [0.25, 0.1, 0.25, 1]
            }}
          >
            {renderItem(item, index)}
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Loading trigger element */}
      <div ref={loadingRef} className="h-1" />

      {/* Loading more indicator */}
      {isLoading && items.length > 0 && <LoadingMoreIndicator />}

      {/* End of list indicator */}
      {!hasMore && items.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-8 text-gray-400 dark:text-gray-500"
        >
          <span className="text-2xl mb-2 block">🎉</span>
          You've seen it all!
        </motion.div>
      )}
    </motion.div>
  );
}

/**
 * Hook for cursor-based pagination
 */
// eslint-disable-next-line react-refresh/only-export-components
export function useCursorPagination<T>(
  fetchFn: (cursor?: string) => Promise<{ items: T[]; nextCursor?: string }>,
  initialItems: T[] = []
) {
  const [items, setItems] = useState<T[]>(initialItems);
  const [cursor, setCursor] = useState<string | undefined>();
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loadMore = useCallback(async () => {
    if (isLoading || !hasMore) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await fetchFn(cursor);
      setItems(prev => [...prev, ...result.items]);
      setCursor(result.nextCursor);
      setHasMore(!!result.nextCursor && result.items.length > 0);
    } catch (e) {
      setError(e instanceof Error ? e : new Error('Failed to load'));
    } finally {
      setIsLoading(false);
    }
  }, [cursor, fetchFn, hasMore, isLoading]);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await fetchFn();
      setItems(result.items);
      setCursor(result.nextCursor);
      setHasMore(!!result.nextCursor && result.items.length > 0);
    } catch (e) {
      setError(e instanceof Error ? e : new Error('Failed to refresh'));
    } finally {
      setIsLoading(false);
    }
  }, [fetchFn]);

  const reset = useCallback(() => {
    setItems([]);
    setCursor(undefined);
    setHasMore(true);
    setError(null);
  }, []);

  return {
    items,
    hasMore,
    isLoading,
    error,
    loadMore,
    refresh,
    reset,
    setItems,
  };
}

export default InfiniteScroll;
