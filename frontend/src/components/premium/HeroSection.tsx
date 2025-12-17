import { useState, useRef , ReactNode , MouseEvent } from 'react';
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

interface HeroSectionProps {
  title: string;
  subtitle?: string;
  children?: ReactNode;
  variant?: 'particles' | 'tilt-cards' | 'gradient';
  className?: string;
}

/**
 * Premium hero section with:
 * - 3D tilt cards
 * - Floating particles
 * - Animated gradient background
 */
export function HeroSection({
  title,
  subtitle,
  children,
  variant = 'gradient',
  className,
}: HeroSectionProps) {
  return (
    <section
      className={twMerge(
        clsx(
          'relative min-h-[60vh] flex items-center justify-center overflow-hidden',
          'px-4 py-16 md:py-24',
          className
        )
      )}
    >
      {/* Background effects */}
      {variant === 'particles' && <FloatingParticles />}
      {variant === 'gradient' && <AnimatedGradient />}
      
      {/* Content */}
      <div className="relative z-10 max-w-4xl mx-auto text-center">
        {/* Animated title */}
        <motion.h1
          className="text-4xl md:text-6xl lg:text-7xl font-bold"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 dark:from-blue-400 dark:via-purple-400 dark:to-pink-400">
            {title}
          </span>
        </motion.h1>

        {/* Subtitle with reveal animation */}
        {subtitle && (
          <motion.p
            className="mt-6 text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            {subtitle}
          </motion.p>
        )}

        {/* Additional content */}
        {children && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="mt-8"
          >
            {children}
          </motion.div>
        )}
      </div>

      {/* Tilt cards overlay */}
      {variant === 'tilt-cards' && <TiltCardsOverlay />}
    </section>
  );
}

/**
 * 3D tilt card component
 */
interface TiltCardProps {
  children: ReactNode;
  className?: string;
  glareEnabled?: boolean;
  tiltAmount?: number;
}

export function TiltCard({
  children,
  className,
  glareEnabled = true,
  tiltAmount = 15,
}: TiltCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const mouseX = useSpring(x, { stiffness: 500, damping: 50 });
  const mouseY = useSpring(y, { stiffness: 500, damping: 50 });
  
  const rotateX = useTransform(mouseY, [-0.5, 0.5], [tiltAmount, -tiltAmount]);
  const rotateY = useTransform(mouseX, [-0.5, 0.5], [-tiltAmount, tiltAmount]);
  
  const glareX = useTransform(mouseX, [-0.5, 0.5], ['0%', '100%']);
  const glareY = useTransform(mouseY, [-0.5, 0.5], ['0%', '100%']);

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    
    const rect = cardRef.current.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const posX = e.clientX - rect.left;
    const posY = e.clientY - rect.top;
    
    x.set((posX - centerX) / rect.width);
    y.set((posY - centerY) / rect.height);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={cardRef}
      className={twMerge(
        clsx(
          'relative rounded-2xl p-6 overflow-hidden',
          'bg-white/80 dark:bg-gray-800/80',
          'backdrop-blur-xl border border-white/20',
          'shadow-xl transition-shadow duration-300',
          isHovered && 'shadow-2xl shadow-blue-500/20',
          className
        )
      )}
      style={{
        rotateX,
        rotateY,
        transformStyle: 'preserve-3d',
        perspective: 1000,
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
    >
      {/* Glare effect */}
      {glareEnabled && isHovered && (
        <motion.div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255,255,255,0.3) 0%, transparent 60%)`,
          }}
        />
      )}
      
      {/* Content with 3D depth */}
      <div style={{ transform: 'translateZ(50px)' }}>
        {children}
      </div>
    </motion.div>
  );
}

/**
 * Floating particles background
 */
function FloatingParticles() {
  // Generate particles once using useState initializer
  const [particles] = useState(() => Array.from({ length: 20 }, (_, i) => ({
    id: i,
    size: Math.random() * 6 + 2,
    x: Math.random() * 100,
    y: Math.random() * 100,
    duration: Math.random() * 10 + 10,
    delay: Math.random() * 5,
    randomX: Math.random() * 20 - 10,
  })));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full"
          style={{
            width: particle.size,
            height: particle.size,
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            background: `linear-gradient(135deg, var(--neon-blue), var(--neon-purple))`,
            boxShadow: '0 0 10px var(--neon-blue)',
          }}
          animate={{
            y: [0, -30, 0],
            x: [0, particle.randomX, 0],
            opacity: [0.3, 0.8, 0.3],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: particle.duration,
            repeat: Infinity,
            delay: particle.delay,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}

/**
 * Animated gradient background
 */
function AnimatedGradient() {
  return (
    <div className="absolute inset-0 overflow-hidden">
      {/* Main gradient */}
      <motion.div
        className="absolute inset-0"
        style={{
          background:
            'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 50%, rgba(236, 72, 153, 0.1) 100%)',
        }}
        animate={{
          backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
      
      {/* Orbs */}
      <motion.div
        className="absolute w-96 h-96 rounded-full blur-3xl opacity-30"
        style={{
          background: 'var(--neon-blue)',
          left: '10%',
          top: '20%',
        }}
        animate={{
          x: [0, 50, 0],
          y: [0, 30, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      <motion.div
        className="absolute w-80 h-80 rounded-full blur-3xl opacity-30"
        style={{
          background: 'var(--neon-purple)',
          right: '10%',
          bottom: '20%',
        }}
        animate={{
          x: [0, -50, 0],
          y: [0, -30, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </div>
  );
}

/**
 * Tilt cards overlay for hero
 */
function TiltCardsOverlay() {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div className="grid grid-cols-3 gap-8 opacity-20 scale-75">
        {[1, 2, 3].map((i) => (
          <motion.div
            key={i}
            className="w-48 h-64 rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm border border-white/10"
            animate={{
              rotateY: [0, 10, -10, 0],
              rotateX: [0, -5, 5, 0],
            }}
            transition={{
              duration: 6,
              repeat: Infinity,
              delay: i * 0.5,
              ease: 'easeInOut',
            }}
            style={{
              transformStyle: 'preserve-3d',
            }}
          />
        ))}
      </div>
    </div>
  );
}

export default HeroSection;
