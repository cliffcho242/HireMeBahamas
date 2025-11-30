import { useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence, useDragControls, PanInfo } from 'framer-motion';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  snapPoints?: number[];
  initialSnap?: number;
  className?: string;
  showHandle?: boolean;
}

/**
 * Premium mobile bottom sheet modal
 * - Swipe to dismiss
 * - Snap points
 * - Glass morphism styling
 * - Smooth animations
 */
export function BottomSheet({
  isOpen,
  onClose,
  children,
  title,
  snapPoints = [0.5, 0.9],
  initialSnap = 0,
  className,
  showHandle = true,
}: BottomSheetProps) {
  const dragControls = useDragControls();
  const sheetRef = useRef<HTMLDivElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  // Calculate height based on snap point
  const getHeight = (snapIndex: number) => {
    const vh = window.innerHeight;
    return vh * snapPoints[snapIndex];
  };

  // Handle drag end
  const handleDragEnd = useCallback(
    (_: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
      const velocity = info.velocity.y;
      const offset = info.offset.y;

      // If dragged down fast or far enough, close
      if (velocity > 500 || offset > 100) {
        onClose();
      }
    },
    [onClose]
  );

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop overlay */}
          <motion.div
            ref={overlayRef}
            className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Sheet */}
          <motion.div
            ref={sheetRef}
            className={twMerge(
              clsx(
                'fixed inset-x-0 bottom-0 z-50 rounded-t-3xl',
                'bg-white dark:bg-gray-900',
                'shadow-2xl',
                'touch-none',
                className
              )
            )}
            style={{
              background: 'var(--bg-glass)',
              backdropFilter: 'blur(20px) saturate(180%)',
              WebkitBackdropFilter: 'blur(20px) saturate(180%)',
              borderTop: '1px solid var(--border-glass)',
              maxHeight: '90vh',
            }}
            initial={{ y: '100%' }}
            animate={{ y: 0, height: getHeight(initialSnap) }}
            exit={{ y: '100%' }}
            transition={{
              type: 'spring',
              damping: 30,
              stiffness: 300,
            }}
            drag="y"
            dragControls={dragControls}
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0.1, bottom: 0.5 }}
            onDragEnd={handleDragEnd}
          >
            {/* Handle */}
            {showHandle && (
              <div
                className="flex justify-center py-3 cursor-grab active:cursor-grabbing"
                onPointerDown={(e) => dragControls.start(e)}
              >
                <div className="w-10 h-1.5 rounded-full bg-gray-300 dark:bg-gray-600" />
              </div>
            )}

            {/* Title */}
            {title && (
              <div className="px-6 pb-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {title}
                </h2>
              </div>
            )}

            {/* Content */}
            <div
              className="overflow-y-auto overscroll-contain"
              style={{ maxHeight: 'calc(90vh - 60px)' }}
            >
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

interface SwipeableItemProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  leftAction?: React.ReactNode;
  rightAction?: React.ReactNode;
  threshold?: number;
  className?: string;
}

/**
 * Swipeable item for lists (swipe-to-reply, swipe-to-delete, etc.)
 */
export function SwipeableItem({
  children,
  onSwipeLeft,
  onSwipeRight,
  leftAction,
  rightAction,
  threshold = 100,
  className,
}: SwipeableItemProps) {
  const handleDragEnd = useCallback(
    (_: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
      if (info.offset.x > threshold && onSwipeRight) {
        onSwipeRight();
      } else if (info.offset.x < -threshold && onSwipeLeft) {
        onSwipeLeft();
      }
    },
    [threshold, onSwipeLeft, onSwipeRight]
  );

  return (
    <div className={twMerge('relative overflow-hidden', className)}>
      {/* Left action background */}
      {leftAction && (
        <div className="absolute inset-y-0 left-0 flex items-center px-4 bg-green-500">
          {leftAction}
        </div>
      )}

      {/* Right action background */}
      {rightAction && (
        <div className="absolute inset-y-0 right-0 flex items-center px-4 bg-red-500">
          {rightAction}
        </div>
      )}

      {/* Main content */}
      <motion.div
        className="relative bg-white dark:bg-gray-900"
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.2}
        onDragEnd={handleDragEnd}
      >
        {children}
      </motion.div>
    </div>
  );
}

export default BottomSheet;
