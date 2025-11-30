/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Inter Variable font family
      fontFamily: {
        'sans': ['Inter Variable', 'Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        'display': ['Inter Variable', 'Inter', 'system-ui', 'sans-serif'],
      },
      // Enhanced breakpoints for all devices - Mobile, Tablet, Desktop, 4K, 5K displays
      screens: {
        'xs': '320px',      // Extra small phones (iPhone SE, older Android)
        'sm': '640px',      // Large phones (iPhone 12/13/14, most Android)
        'md': '768px',      // Tablets (iPad Mini, Android tablets)
        'lg': '1024px',     // Small laptops / iPad Pro
        'xl': '1280px',     // Desktops / Large laptops
        '2xl': '1536px',    // Large desktops
        '3xl': '1920px',    // Full HD monitors
        '4xl': '2560px',    // 2K/QHD monitors
        '5xl': '3840px',    // 4K UHD displays
        '6xl': '5120px',    // 5K displays (iMac 5K, Studio Display)
        // Landscape orientations
        'landscape': { 'raw': '(orientation: landscape)' },
        'portrait': { 'raw': '(orientation: portrait)' },
        // Device-specific
        'touch': { 'raw': '(hover: none) and (pointer: coarse)' },
        'mouse': { 'raw': '(hover: hover) and (pointer: fine)' },
        // High DPI / Retina displays
        'retina': { 'raw': '(-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)' },
        'retina-3x': { 'raw': '(-webkit-min-device-pixel-ratio: 3), (min-resolution: 288dpi)' },
      },
      // Enhanced spacing for better mobile UX
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      // Optimized font sizes for all devices
      fontSize: {
        'xxs': ['0.625rem', { lineHeight: '0.75rem' }],
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },
      // Touch-friendly sizes (Apple/Android HIG guidelines)
      minHeight: {
        'touch': '44px',  // iOS minimum
        'touch-android': '48px',  // Android minimum
      },
      minWidth: {
        'touch': '44px',
        'touch-android': '48px',
      },
      // Premium animations optimized for smooth 60fps on all displays including 5K
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'fade-in-fast': 'fadeIn 0.15s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-up-smooth': 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-down-smooth': 'slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'scale-in': 'scaleIn 0.2s ease-out',
        'scale-in-smooth': 'scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'bounce-subtle': 'bounceSubtle 0.5s ease-in-out',
        'pulse-soft': 'pulseSoft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'like-pop': 'likePop 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'comment-slide': 'commentSlide 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'share-ripple': 'shareRipple 0.6s ease-out',
        'shimmer': 'shimmer 2s linear infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
        // Premium micro-animations
        'heart-burst': 'heartBurst 0.45s cubic-bezier(0.17, 0.89, 0.32, 1.28)',
        'ripple-out': 'rippleOut 0.6s ease-out',
        'checkmark-fly': 'checkmarkFly 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'card-lift': 'cardLift 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        'text-reveal': 'textReveal 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
        'skeleton-pulse': 'skeletonPulse 1.5s ease-in-out infinite',
        'neon-pulse': 'neonPulse 2s ease-in-out infinite',
        'gradient-shift': 'gradientShift 8s ease infinite',
        'cursor-glow': 'cursorGlow 1.5s ease-in-out infinite',
        'page-transition': 'pageTransition 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'pull-refresh': 'pullRefresh 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'bottom-sheet': 'bottomSheet 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
        'story-ring': 'storyRing 3s linear infinite',
        'verified-badge': 'verifiedBadge 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'particle-float': 'particleFloat 4s ease-in-out infinite',
        'tilt-3d': 'tilt3d 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        likePop: {
          '0%': { transform: 'scale(1)' },
          '25%': { transform: 'scale(1.25)' },
          '50%': { transform: 'scale(0.95)' },
          '100%': { transform: 'scale(1)' },
        },
        commentSlide: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        shareRipple: {
          '0%': { transform: 'scale(0)', opacity: '1' },
          '100%': { transform: 'scale(2.5)', opacity: '0' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(59, 130, 246, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.8), 0 0 30px rgba(59, 130, 246, 0.4)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        // Premium keyframes
        heartBurst: {
          '0%': { transform: 'scale(1)' },
          '15%': { transform: 'scale(1.35)' },
          '30%': { transform: 'scale(0.9)' },
          '45%': { transform: 'scale(1.15)' },
          '60%': { transform: 'scale(0.95)' },
          '100%': { transform: 'scale(1)' },
        },
        rippleOut: {
          '0%': { transform: 'scale(0)', opacity: '0.6' },
          '100%': { transform: 'scale(4)', opacity: '0' },
        },
        checkmarkFly: {
          '0%': { transform: 'translateY(0) scale(0)', opacity: '0' },
          '50%': { transform: 'translateY(-15px) scale(1.2)', opacity: '1' },
          '100%': { transform: 'translateY(-30px) scale(1)', opacity: '0' },
        },
        cardLift: {
          '0%': { transform: 'translateY(0) scale(1)', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' },
          '100%': { transform: 'translateY(-8px) scale(1.02)', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)' },
        },
        textReveal: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        skeletonPulse: {
          '0%, 100%': { opacity: '1', backgroundPosition: '-200% 0' },
          '50%': { opacity: '0.6', backgroundPosition: '200% 0' },
        },
        neonPulse: {
          '0%, 100%': { boxShadow: '0 0 5px currentColor, 0 0 10px currentColor, 0 0 20px currentColor' },
          '50%': { boxShadow: '0 0 10px currentColor, 0 0 20px currentColor, 0 0 40px currentColor' },
        },
        gradientShift: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        cursorGlow: {
          '0%, 100%': { opacity: '0.8', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.1)' },
        },
        pageTransition: {
          '0%': { opacity: '0', filter: 'blur(10px)', transform: 'scale(0.98)' },
          '100%': { opacity: '1', filter: 'blur(0)', transform: 'scale(1)' },
        },
        pullRefresh: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bottomSheet: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        storyRing: {
          '0%': { backgroundPosition: '0% 50%' },
          '100%': { backgroundPosition: '200% 50%' },
        },
        verifiedBadge: {
          '0%': { transform: 'scale(0) rotate(-180deg)', opacity: '0' },
          '70%': { transform: 'scale(1.2) rotate(10deg)', opacity: '1' },
          '100%': { transform: 'scale(1) rotate(0)', opacity: '1' },
        },
        particleFloat: {
          '0%, 100%': { transform: 'translateY(0) translateX(0) rotate(0deg)', opacity: '0.7' },
          '25%': { transform: 'translateY(-20px) translateX(10px) rotate(90deg)', opacity: '1' },
          '50%': { transform: 'translateY(-10px) translateX(20px) rotate(180deg)', opacity: '0.7' },
          '75%': { transform: 'translateY(-30px) translateX(5px) rotate(270deg)', opacity: '1' },
        },
        tilt3d: {
          '0%': { transform: 'perspective(1000px) rotateX(0) rotateY(0)' },
          '100%': { transform: 'perspective(1000px) rotateX(var(--tilt-x, 0deg)) rotateY(var(--tilt-y, 0deg))' },
        },
      },
      // Safe area for mobile devices (notch support)
      padding: {
        'safe': 'env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)',
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
      },
      // Premium brand colors with glass-morphism + neon gradients
      colors: {
        'bahamas-blue': {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // Premium neon accent colors
        'neon': {
          'blue': '#00d4ff',
          'purple': '#a855f7',
          'pink': '#ec4899',
          'cyan': '#22d3ee',
          'green': '#10b981',
          'orange': '#f97316',
        },
        // Glass morphism surface colors
        'glass': {
          'light': 'rgba(255, 255, 255, 0.8)',
          'dark': 'rgba(15, 23, 42, 0.8)',
          'overlay': 'rgba(255, 255, 255, 0.1)',
        },
        // Premium dark theme
        'dark': {
          'bg': '#0a0a0f',
          'surface': '#111118',
          'card': '#1a1a24',
          'border': '#2a2a3a',
          'text': '#e4e4e7',
          'muted': '#a1a1aa',
        },
        // Semantic social interaction colors for consistent UX
        'social': {
          'like': '#ef4444',
          'like-hover': '#dc2626',
          'comment': '#3b82f6',
          'comment-hover': '#2563eb',
          'share': '#10b981',
          'share-hover': '#059669',
        },
      },
      // Premium gradient backgrounds
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-premium': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient-neon': 'linear-gradient(135deg, #00d4ff 0%, #a855f7 50%, #ec4899 100%)',
        'gradient-glass': 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        'gradient-dark': 'linear-gradient(180deg, #0a0a0f 0%, #1a1a24 100%)',
        'shimmer-gradient': 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%)',
        'story-ring': 'linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888, #f09433, #e6683c)',
      },
      // Enhanced 5K-optimized backdrop blur values
      backdropBlur: {
        'xs': '2px',
        '4xl': '72px',
        '5xl': '100px',
      },
      // Premium box shadows for high-resolution displays
      boxShadow: {
        'social': '0 2px 8px -2px rgba(0, 0, 0, 0.1), 0 4px 16px -4px rgba(0, 0, 0, 0.15)',
        'social-hover': '0 4px 12px -2px rgba(0, 0, 0, 0.15), 0 8px 24px -6px rgba(0, 0, 0, 0.2)',
        'card-5k': '0 1px 3px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.05)',
        'card-5k-hover': '0 4px 8px rgba(0, 0, 0, 0.1), 0 8px 24px rgba(0, 0, 0, 0.1)',
        'glow-blue': '0 0 20px rgba(59, 130, 246, 0.35)',
        'glow-purple': '0 0 20px rgba(139, 92, 246, 0.35)',
        // Premium neon glow shadows
        'neon-blue': '0 0 20px rgba(0, 212, 255, 0.4), 0 0 40px rgba(0, 212, 255, 0.2)',
        'neon-purple': '0 0 20px rgba(168, 85, 247, 0.4), 0 0 40px rgba(168, 85, 247, 0.2)',
        'neon-pink': '0 0 20px rgba(236, 72, 153, 0.4), 0 0 40px rgba(236, 72, 153, 0.2)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.1), inset 0 0 0 1px rgba(255, 255, 255, 0.1)',
        'glass-dark': '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 0 0 1px rgba(255, 255, 255, 0.05)',
        'card-lift': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'premium': '0 20px 60px -10px rgba(0, 0, 0, 0.2), 0 10px 20px -5px rgba(0, 0, 0, 0.1)',
      },
      // GPU-accelerated transitions for smooth 5K performance
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'bounce-out': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'elastic': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
      transitionDuration: {
        '400': '400ms',
        '600': '600ms',
      },
    },
  },
  plugins: [
    // Plugin for touch-friendly interactions and 5K display optimization
    function ({ addUtilities }) {
      const newUtilities = {
        '.tap-highlight-transparent': {
          '-webkit-tap-highlight-color': 'transparent',
        },
        '.touch-manipulation': {
          'touch-action': 'manipulation',
        },
        '.safe-area-inset': {
          'padding-top': 'env(safe-area-inset-top)',
          'padding-right': 'env(safe-area-inset-right)',
          'padding-bottom': 'env(safe-area-inset-bottom)',
          'padding-left': 'env(safe-area-inset-left)',
        },
        // GPU acceleration for smooth animations on 5K displays
        '.gpu-accelerated': {
          'transform': 'translateZ(0)',
          'backface-visibility': 'hidden',
          '-webkit-backface-visibility': 'hidden',
          'perspective': '1000px',
          '-webkit-perspective': '1000px',
        },
        '.will-change-transform': {
          'will-change': 'transform',
        },
        '.will-change-opacity': {
          'will-change': 'opacity',
        },
        // High-DPI image rendering optimization
        '.image-render-crisp': {
          'image-rendering': '-webkit-optimize-contrast',
          'image-rendering': 'crisp-edges',
        },
        '.image-render-smooth': {
          'image-rendering': 'auto',
          '-webkit-font-smoothing': 'antialiased',
        },
        // Smooth scrolling with hardware acceleration
        '.scroll-smooth-gpu': {
          'scroll-behavior': 'smooth',
          '-webkit-overflow-scrolling': 'touch',
          'overscroll-behavior': 'contain',
        },
        // Social interaction micro-interactions
        '.social-hover': {
          'transition': 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        },
        '.social-active': {
          'transform': 'scale(0.95)',
          'transition': 'transform 0.1s ease-out',
        },
        // 5K-optimized text rendering
        '.text-render-5k': {
          '-webkit-font-smoothing': 'antialiased',
          '-moz-osx-font-smoothing': 'grayscale',
          'text-rendering': 'optimizeLegibility',
          'font-feature-settings': '"kern" 1',
        },
        // Glass morphism effect for modern UI
        '.glass-effect': {
          'background': 'rgba(255, 255, 255, 0.7)',
          'backdrop-filter': 'blur(10px)',
          '-webkit-backdrop-filter': 'blur(10px)',
          'border': '1px solid rgba(255, 255, 255, 0.2)',
        },
        '.glass-effect-dark': {
          'background': 'rgba(0, 0, 0, 0.5)',
          'backdrop-filter': 'blur(10px)',
          '-webkit-backdrop-filter': 'blur(10px)',
          'border': '1px solid rgba(255, 255, 255, 0.1)',
        },
      }
      addUtilities(newUtilities)
    },
  ],
}
