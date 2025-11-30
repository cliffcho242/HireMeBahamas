import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

interface ProfileCardProps {
  name: string;
  title?: string;
  avatar?: string;
  isOnline?: boolean;
  isVerified?: boolean;
  hasStory?: boolean;
  followers?: number;
  following?: number;
  className?: string;
  onClick?: () => void;
  children?: React.ReactNode;
}

/**
 * Premium profile card with:
 * - Floating lift + subtle glow on hover
 * - 3D tilt effect on mouse move
 * - Avatar rings (online, story, verified)
 */
export function ProfileCard({
  name,
  title,
  avatar,
  isOnline = false,
  isVerified = false,
  hasStory = false,
  followers,
  following,
  className,
  onClick,
  children,
}: ProfileCardProps) {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    // Calculate tilt (max ±10 degrees)
    const tiltX = ((y - centerY) / centerY) * -10;
    const tiltY = ((x - centerX) / centerX) * 10;
    
    setTilt({ x: tiltX, y: tiltY });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
    setIsHovered(false);
  };

  return (
    <motion.div
      ref={cardRef}
      className={twMerge(
        clsx(
          'glass-card p-6 cursor-pointer',
          'transform-gpu transition-shadow duration-300',
          isHovered && 'shadow-premium',
          className
        )
      )}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: `perspective(1000px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
        transformStyle: 'preserve-3d',
      }}
      animate={{
        y: isHovered ? -8 : 0,
        boxShadow: isHovered
          ? '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 40px rgba(0, 212, 255, 0.1)'
          : '0 8px 32px rgba(0, 0, 0, 0.1)',
      }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* Glow effect on hover */}
      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        animate={{
          opacity: isHovered ? 1 : 0,
          background: isHovered
            ? 'radial-gradient(600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(0, 212, 255, 0.1), transparent 40%)'
            : 'none',
        }}
        transition={{ duration: 0.3 }}
      />

      <div className="relative z-10 flex flex-col items-center text-center">
        {/* Avatar with rings */}
        <AvatarRing
          src={avatar}
          name={name}
          size="lg"
          isOnline={isOnline}
          hasStory={hasStory}
          isVerified={isVerified}
        />

        {/* Name and verification */}
        <div className="mt-4 flex items-center gap-2">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {name}
          </h3>
          {isVerified && <VerifiedBadge />}
        </div>

        {/* Title */}
        {title && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {title}
          </p>
        )}

        {/* Stats */}
        {(followers !== undefined || following !== undefined) && (
          <div className="mt-4 flex gap-6 text-sm">
            {followers !== undefined && (
              <div>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {formatCount(followers)}
                </span>
                <span className="ml-1 text-gray-500 dark:text-gray-400">
                  followers
                </span>
              </div>
            )}
            {following !== undefined && (
              <div>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {formatCount(following)}
                </span>
                <span className="ml-1 text-gray-500 dark:text-gray-400">
                  following
                </span>
              </div>
            )}
          </div>
        )}

        {children}
      </div>
    </motion.div>
  );
}

interface AvatarRingProps {
  src?: string;
  name: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  isOnline?: boolean;
  hasStory?: boolean;
  isVerified?: boolean;
  className?: string;
  onClick?: () => void;
}

/**
 * Avatar with premium rings:
 * - Online status (green dot with glow)
 * - Story ring (Instagram-like gradient)
 * - Verified badge
 */
export function AvatarRing({
  src,
  name,
  size = 'md',
  isOnline = false,
  hasStory = false,
  isVerified = false,
  className,
  onClick,
}: AvatarRingProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };

  const onlineIndicatorSize = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
    xl: 'w-5 h-5',
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const avatarContent = src ? (
    <img
      src={src}
      alt={name}
      className={twMerge(
        clsx('rounded-full object-cover', sizeClasses[size], className)
      )}
    />
  ) : (
    <div
      className={twMerge(
        clsx(
          'rounded-full flex items-center justify-center',
          'bg-gradient-to-br from-blue-500 to-purple-500 text-white font-semibold',
          sizeClasses[size],
          className
        )
      )}
    >
      {getInitials(name)}
    </div>
  );

  return (
    <div className="relative inline-block" onClick={onClick}>
      {/* Story ring wrapper */}
      {hasStory ? (
        <div className="avatar-ring-story">{avatarContent}</div>
      ) : (
        avatarContent
      )}

      {/* Online indicator */}
      {isOnline && (
        <motion.div
          className={clsx(
            'absolute bottom-0 right-0 rounded-full border-2',
            'bg-green-500 border-white dark:border-gray-900',
            onlineIndicatorSize[size]
          )}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          style={{
            boxShadow: '0 0 8px rgba(34, 197, 94, 0.6)',
          }}
        />
      )}

      {/* Verified badge positioned */}
      {isVerified && (
        <div className="absolute -bottom-1 -right-1">
          <VerifiedBadge size={size === 'sm' ? 'sm' : 'md'} />
        </div>
      )}
    </div>
  );
}

interface VerifiedBadgeProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Verified badge with animation
 */
export function VerifiedBadge({ size = 'md', className }: VerifiedBadgeProps) {
  const sizeClasses = {
    sm: 'w-4 h-4 text-[10px]',
    md: 'w-5 h-5 text-xs',
    lg: 'w-6 h-6 text-sm',
  };

  return (
    <motion.div
      className={twMerge(
        clsx(
          'inline-flex items-center justify-center rounded-full',
          'bg-gradient-to-r from-blue-500 to-cyan-400 text-white',
          sizeClasses[size],
          className
        )
      )}
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      title="Verified"
    >
      <svg
        className="w-3/4 h-3/4"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          fillRule="evenodd"
          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
          clipRule="evenodd"
        />
      </svg>
    </motion.div>
  );
}

// Helper function to format large numbers
function formatCount(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  }
  return num.toString();
}

export default ProfileCard;
