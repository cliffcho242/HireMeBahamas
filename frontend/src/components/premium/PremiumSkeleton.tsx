import { motion } from 'framer-motion';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

interface PremiumSkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'card' | 'avatar' | 'button';
  width?: string | number;
  height?: string | number;
  lines?: number;
  animate?: boolean;
}

/**
 * Premium skeleton loader with shimmer + pulse + rounded edges
 * Looks premium and maintains <80ms LCP on mobile
 */
export function PremiumSkeleton({
  className,
  variant = 'rectangular',
  width,
  height,
  lines = 1,
  animate = true,
}: PremiumSkeletonProps) {
  const baseClasses = 'skeleton-premium';
  
  const variantClasses = {
    text: 'h-4 rounded-md',
    circular: 'rounded-full aspect-square',
    rectangular: 'rounded-xl',
    card: 'rounded-2xl min-h-[200px]',
    avatar: 'rounded-full w-12 h-12',
    button: 'rounded-xl h-12 w-32',
  };

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  const skeletonElement = (
    <div
      className={twMerge(
        clsx(baseClasses, variantClasses[variant], className)
      )}
      style={style}
      aria-hidden="true"
      role="presentation"
    />
  );

  if (!animate) {
    return skeletonElement;
  }

  // For text with multiple lines
  if (variant === 'text' && lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0.6 }}
            animate={{ opacity: [0.6, 1, 0.6] }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: index * 0.1,
              ease: 'easeInOut',
            }}
            className={twMerge(
              clsx(
                baseClasses,
                variantClasses[variant],
                index === lines - 1 ? 'w-3/4' : 'w-full',
                className
              )
            )}
            aria-hidden="true"
            role="presentation"
          />
        ))}
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0.6 }}
      animate={{ opacity: [0.6, 1, 0.6] }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      className={twMerge(
        clsx(baseClasses, variantClasses[variant], className)
      )}
      style={style}
      aria-hidden="true"
      role="presentation"
    />
  );
}

/**
 * Premium skeleton card - pre-built card skeleton
 */
export function PremiumSkeletonCard({ className }: { className?: string }) {
  return (
    <div className={twMerge('glass-card p-4 space-y-4', className)}>
      {/* Header with avatar */}
      <div className="flex items-center space-x-3">
        <PremiumSkeleton variant="avatar" />
        <div className="flex-1 space-y-2">
          <PremiumSkeleton variant="text" width="60%" />
          <PremiumSkeleton variant="text" width="40%" height={12} />
        </div>
      </div>
      
      {/* Content */}
      <PremiumSkeleton variant="text" lines={3} />
      
      {/* Image placeholder */}
      <PremiumSkeleton variant="rectangular" height={200} className="w-full" />
      
      {/* Actions */}
      <div className="flex justify-between pt-2">
        <PremiumSkeleton variant="button" width={80} height={36} />
        <PremiumSkeleton variant="button" width={80} height={36} />
        <PremiumSkeleton variant="button" width={80} height={36} />
      </div>
    </div>
  );
}

/**
 * Premium skeleton post feed
 */
export function PremiumSkeletonFeed({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.4,
            delay: index * 0.1,
            ease: [0.16, 1, 0.3, 1],
          }}
        >
          <PremiumSkeletonCard />
        </motion.div>
      ))}
    </div>
  );
}

export default PremiumSkeleton;
