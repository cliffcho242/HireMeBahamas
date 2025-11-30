import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

interface AnimatedButtonProps {
  children: React.ReactNode;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  variant?: 'like' | 'follow' | 'send' | 'default';
  isActive?: boolean;
  className?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  haptic?: boolean;
}

/**
 * Animated button with micro-interactions
 * - Like button → heart burst + haptic feedback
 * - Follow button → scale bounce + ripple
 * - Send button → ripple + flying checkmark
 */
export function AnimatedButton({
  children,
  onClick,
  variant = 'default',
  isActive = false,
  className,
  disabled = false,
  size = 'md',
  haptic = true,
}: AnimatedButtonProps) {
  const [isAnimating, setIsAnimating] = useState(false);
  const [showRipple, setShowRipple] = useState(false);
  const [showCheckmark, setShowCheckmark] = useState(false);
  const [ripplePosition, setRipplePosition] = useState({ x: 0, y: 0 });

  const triggerHaptic = useCallback(() => {
    if (haptic && 'vibrate' in navigator) {
      navigator.vibrate(10);
    }
  }, [haptic]);

  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      if (disabled) return;

      // Calculate ripple position
      const rect = e.currentTarget.getBoundingClientRect();
      setRipplePosition({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });

      setIsAnimating(true);
      setShowRipple(true);
      triggerHaptic();

      if (variant === 'send') {
        setShowCheckmark(true);
        setTimeout(() => setShowCheckmark(false), 600);
      }

      setTimeout(() => {
        setIsAnimating(false);
        setShowRipple(false);
      }, 400);

      onClick?.(e);
    },
    [disabled, onClick, triggerHaptic, variant]
  );

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const variantClasses = {
    like: clsx(
      'relative overflow-hidden rounded-full transition-all duration-300',
      isActive
        ? 'text-red-500 bg-red-50 dark:bg-red-900/20'
        : 'text-gray-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
    ),
    follow: clsx(
      'relative overflow-hidden rounded-full font-semibold transition-all duration-300',
      isActive
        ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200'
        : 'bg-blue-500 hover:bg-blue-600 text-white'
    ),
    send: clsx(
      'relative overflow-hidden rounded-full bg-gradient-to-r from-blue-500 to-purple-500',
      'text-white font-medium transition-all duration-300 hover:shadow-neon-blue'
    ),
    default: clsx(
      'relative overflow-hidden rounded-xl bg-white dark:bg-gray-800',
      'border border-gray-200 dark:border-gray-700 transition-all duration-300',
      'hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-600'
    ),
  };

  // Heart burst particles for like button
  const HeartBurst = () => (
    <AnimatePresence>
      {isAnimating && variant === 'like' && (
        <>
          {[...Array(6)].map((_, i) => (
            <motion.span
              key={i}
              className="absolute text-red-500 text-xs pointer-events-none"
              initial={{
                opacity: 1,
                scale: 0,
                x: 0,
                y: 0,
              }}
              animate={{
                opacity: 0,
                scale: 1,
                x: Math.cos((i * 60 * Math.PI) / 180) * 30,
                y: Math.sin((i * 60 * Math.PI) / 180) * 30,
              }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
              style={{ left: '50%', top: '50%' }}
            >
              ❤️
            </motion.span>
          ))}
        </>
      )}
    </AnimatePresence>
  );

  // Ripple effect
  const Ripple = () => (
    <AnimatePresence>
      {showRipple && (
        <motion.span
          className="absolute rounded-full bg-current opacity-20 pointer-events-none"
          initial={{ width: 0, height: 0, opacity: 0.4 }}
          animate={{ width: 200, height: 200, opacity: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          style={{
            left: ripplePosition.x - 100,
            top: ripplePosition.y - 100,
          }}
        />
      )}
    </AnimatePresence>
  );

  // Flying checkmark for send button
  const FlyingCheckmark = () => (
    <AnimatePresence>
      {showCheckmark && (
        <motion.span
          className="absolute text-white text-lg pointer-events-none"
          initial={{ opacity: 0, y: 0, scale: 0 }}
          animate={{ opacity: [0, 1, 1, 0], y: [-5, -15, -25, -35], scale: [0.5, 1.2, 1, 0.8] }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          style={{ left: '50%', transform: 'translateX(-50%)' }}
        >
          ✓
        </motion.span>
      )}
    </AnimatePresence>
  );

  return (
    <motion.button
      className={twMerge(
        clsx(
          'flex items-center justify-center gap-2',
          sizeClasses[size],
          variantClasses[variant],
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )
      )}
      onClick={handleClick}
      disabled={disabled}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      animate={
        isAnimating && variant === 'like'
          ? {
              scale: [1, 1.3, 0.9, 1.1, 1],
              transition: { duration: 0.45, ease: [0.17, 0.89, 0.32, 1.28] },
            }
          : undefined
      }
    >
      <Ripple />
      <HeartBurst />
      <FlyingCheckmark />
      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </motion.button>
  );
}

/**
 * Like button with heart animation
 */
export function LikeButton({
  isLiked,
  count,
  onToggle,
  className,
}: {
  isLiked: boolean;
  count: number;
  onToggle: () => void;
  className?: string;
}) {
  return (
    <AnimatedButton
      variant="like"
      isActive={isLiked}
      onClick={onToggle}
      className={className}
      size="sm"
    >
      <motion.span
        animate={isLiked ? { scale: [1, 1.2, 1] } : undefined}
        transition={{ duration: 0.3 }}
      >
        {isLiked ? '❤️' : '🤍'}
      </motion.span>
      <span className="font-medium">{count}</span>
    </AnimatedButton>
  );
}

/**
 * Follow button with animation
 */
export function FollowButton({
  isFollowing,
  onToggle,
  className,
}: {
  isFollowing: boolean;
  onToggle: () => void;
  className?: string;
}) {
  return (
    <AnimatedButton
      variant="follow"
      isActive={isFollowing}
      onClick={onToggle}
      className={className}
      size="md"
    >
      {isFollowing ? 'Following' : 'Follow'}
    </AnimatedButton>
  );
}

export default AnimatedButton;
