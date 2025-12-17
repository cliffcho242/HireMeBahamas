import { useState, useRef, ImgHTMLAttributes, useCallback } from 'react';
import { useInView } from 'react-intersection-observer';

interface OptimizedImageProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'srcSet'> {
  src: string;
  alt: string;
  /**
   * Responsive image sources for different screen densities
   * Example: "image.jpg 1x, image@2x.jpg 2x"
   */
  srcSet?: string;
  /**
   * Fallback image URL if the main image fails to load
   */
  fallbackSrc?: string;
  /**
   * Placeholder color while loading
   */
  placeholderColor?: string;
  /**
   * Whether to show a blur placeholder
   */
  blur?: boolean;
  /**
   * Priority loading - skips lazy loading
   */
  priority?: boolean;
  /**
   * Container aspect ratio (e.g., "16/9", "1/1", "4/3")
   */
  aspectRatio?: string;
  /**
   * Object fit style
   */
  objectFit?: 'cover' | 'contain' | 'fill' | 'none' | 'scale-down';
}

/**
 * OptimizedImage component for better performance:
 * - Lazy loading with Intersection Observer
 * - Native loading="lazy" attribute
 * - Blur placeholder during load
 * - Error fallback handling
 * - Proper sizing with aspect ratio
 */
const OptimizedImage = ({
  src,
  alt,
  fallbackSrc,
  placeholderColor = '#f3f4f6',
  blur = true,
  priority = false,
  aspectRatio,
  objectFit = 'cover',
  className = '',
  style,
  ...props
}: OptimizedImageProps) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [currentSrc, setCurrentSrc] = useState<string>(src);
  const imgRef = useRef<HTMLImageElement>(null);
  
  // Use intersection observer for lazy loading
  const { ref: inViewRef, inView } = useInView({
    triggerOnce: true,
    rootMargin: '200px 0px', // Start loading 200px before viewport
    skip: priority, // Skip intersection observer for priority images
  });

  // Combine refs
  const setRefs = useCallback((node: HTMLImageElement | null) => {
    (imgRef as React.MutableRefObject<HTMLImageElement | null>).current = node;
    if (!priority) {
      inViewRef(node);
    }
  }, [priority, inViewRef]);

  // Handle image load
  const handleLoad = useCallback(() => {
    setIsLoaded(true);
  }, []);

  // Handle image error
  const handleError = useCallback(() => {
    if (fallbackSrc && currentSrc !== fallbackSrc) {
      setCurrentSrc(fallbackSrc);
    } else {
      setHasError(true);
    }
  }, [fallbackSrc, currentSrc]);

  // Determine if we should load the image
  const shouldLoad = priority || inView;

  // Container styles
  const containerStyle: React.CSSProperties = {
    backgroundColor: placeholderColor,
    position: 'relative',
    overflow: 'hidden',
    ...(aspectRatio && { aspectRatio }),
    ...style,
  };

  // Image styles
  const imageStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit,
    transition: blur ? 'filter 0.3s ease-out, opacity 0.3s ease-out' : 'opacity 0.3s ease-out',
    filter: !isLoaded && blur ? 'blur(10px)' : 'none',
    opacity: isLoaded ? 1 : blur ? 0.8 : 0,
  };

  // Error placeholder
  if (hasError) {
    return (
      <div 
        className={className}
        style={containerStyle}
        role="img"
        aria-label={alt}
      >
        <div 
          className="absolute inset-0 flex items-center justify-center bg-gray-100"
        >
          <svg 
            className="w-8 h-8 text-gray-400" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
            />
          </svg>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={className}
      style={containerStyle}
    >
      {shouldLoad && (
        <img
          ref={setRefs}
          src={currentSrc}
          alt={alt}
          loading={priority ? 'eager' : 'lazy'}
          decoding="async"
          onLoad={handleLoad}
          onError={handleError}
          style={imageStyle}
          {...props}
        />
      )}
      
      {/* Placeholder shown while loading */}
      {!isLoaded && !hasError && (
        <div 
          className="absolute inset-0 animate-pulse"
          style={{ backgroundColor: placeholderColor }}
        />
      )}
    </div>
  );
};

export default OptimizedImage;
