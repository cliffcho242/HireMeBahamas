import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface CustomCursorProps {
  enabled?: boolean;
  color?: string;
  size?: number;
  trailLength?: number;
}

/**
 * Custom cursor with glowing ring that follows mouse
 * Only visible on desktop (hover: hover devices)
 * Automatically disabled on touch devices
 */
export function CustomCursor({
  enabled = true,
  color = 'rgba(0, 212, 255, 0.6)',
  size = 40,
  trailLength = 8,
}: CustomCursorProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isPointer, setIsPointer] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [isTouch, setIsTouch] = useState(false);

  // Detect touch device - robust detection using multiple methods
  useEffect(() => {
    const checkTouch = () => {
      setIsTouch(
        'ontouchstart' in window ||
          navigator.maxTouchPoints > 0 ||
          window.matchMedia('(hover: none)').matches ||
          window.matchMedia('(pointer: coarse)').matches
      );
    };
    
    checkTouch();
    window.addEventListener('resize', checkTouch);
    return () => window.removeEventListener('resize', checkTouch);
  }, []);

  const updatePosition = useCallback((e: MouseEvent) => {
    setPosition({ x: e.clientX, y: e.clientY });
    setIsVisible(true);
  }, []);

  const updateCursorType = useCallback((e: MouseEvent) => {
    const target = e.target as HTMLElement;
    const isClickable =
      target.tagName === 'A' ||
      target.tagName === 'BUTTON' ||
      !!target.closest('a') ||
      !!target.closest('button') ||
      window.getComputedStyle(target).cursor === 'pointer';
    setIsPointer(!!isClickable);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsVisible(false);
  }, []);

  useEffect(() => {
    if (!enabled || isTouch) return;

    document.addEventListener('mousemove', updatePosition);
    document.addEventListener('mousemove', updateCursorType);
    document.addEventListener('mouseleave', handleMouseLeave);

    // Hide default cursor on the document - use less aggressive approach
    document.body.style.cursor = 'none';
    
    // Add cursor: none to interactive elements only (not forcing with !important)
    const style = document.createElement('style');
    style.id = 'custom-cursor-style';
    style.textContent = `
      body, a, button, [role="button"], input[type="button"], input[type="submit"] { cursor: none; }
    `;
    document.head.appendChild(style);

    return () => {
      document.removeEventListener('mousemove', updatePosition);
      document.removeEventListener('mousemove', updateCursorType);
      document.removeEventListener('mouseleave', handleMouseLeave);
      document.body.style.cursor = '';
      
      const existingStyle = document.getElementById('custom-cursor-style');
      if (existingStyle) {
        existingStyle.remove();
      }
    };
  }, [enabled, isTouch, updatePosition, updateCursorType, handleMouseLeave]);

  // Don't render on touch devices or if disabled
  if (!enabled || isTouch) return null;

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Main cursor ring */}
          <motion.div
            className="fixed pointer-events-none z-[9999] mix-blend-difference"
            style={{
              left: position.x - size / 2,
              top: position.y - size / 2,
              width: size,
              height: size,
            }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{
              scale: isPointer ? 1.5 : 1,
              opacity: 1,
            }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{
              type: 'spring',
              stiffness: 500,
              damping: 28,
              mass: 0.5,
            }}
          >
            <div
              className="w-full h-full rounded-full animate-cursor-glow"
              style={{
                border: `2px solid ${color}`,
                boxShadow: `0 0 20px ${color}, 0 0 40px ${color.replace('0.6', '0.3')}`,
              }}
            />
          </motion.div>

          {/* Center dot */}
          <motion.div
            className="fixed pointer-events-none z-[9999] rounded-full"
            style={{
              left: position.x - 4,
              top: position.y - 4,
              width: 8,
              height: 8,
              backgroundColor: color.replace('0.6', '1'),
              boxShadow: `0 0 10px ${color}`,
            }}
            initial={{ scale: 0 }}
            animate={{ scale: isPointer ? 0 : 1 }}
            transition={{
              type: 'spring',
              stiffness: 500,
              damping: 28,
            }}
          />

          {/* Trail effect */}
          {[...Array(trailLength)].map((_, i) => (
            <motion.div
              key={i}
              className="fixed pointer-events-none z-[9998] rounded-full"
              style={{
                width: 6 - i * 0.5,
                height: 6 - i * 0.5,
                backgroundColor: color.replace('0.6', `${0.4 - i * 0.04}`),
              }}
              animate={{
                left: position.x - (6 - i * 0.5) / 2,
                top: position.y - (6 - i * 0.5) / 2,
              }}
              transition={{
                type: 'spring',
                stiffness: 400 - i * 30,
                damping: 30 + i * 2,
                mass: 0.5 + i * 0.1,
              }}
            />
          ))}
        </>
      )}
    </AnimatePresence>
  );
}

export default CustomCursor;
