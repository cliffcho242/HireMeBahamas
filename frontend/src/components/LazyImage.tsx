/**
 * Lazy Image Component for Optimal Performance
 * 
 * Features:
 * - Lazy loading with Intersection Observer
 * - Progressive image loading (blur placeholder)
 * - Automatic WebP format with fallback
 * - Responsive images with srcset
 * - Error handling with fallback
 */
import React, { useState, useEffect, ImgHTMLAttributes } from 'react';

// Union type for srcSet to support both string and object formats
type SrcSet =
  | string
  | {
      '1x'?: string;
      '2x'?: string;
      '3x'?: string;
    };

// Utility function to convert srcSet to string format
function convertSrcSetToString(srcSet: SrcSet | undefined): string | undefined {
  if (!srcSet) return undefined;
  
  // If srcSet is already a string, return it as-is
  if (typeof srcSet === 'string') {
    return srcSet;
  }
  
  // If srcSet is an object, build the srcSet string
  // Filter out undefined values to avoid 'undefined 1x' in the output
  return Object.entries(srcSet)
    .filter((entry): entry is [string, string] => entry[1] !== undefined)
    .map(([density, url]) => `${url} ${density}`)
    .join(', ');
}

// LazyImageProps extends ImgHTMLAttributes and explicitly defines srcSet to support both
// string format (standard HTML) and object format (for responsive images)
interface LazyImageProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'srcSet'> {
  src: string;
  alt: string;
  srcSet?: SrcSet;
  placeholderSrc?: string;
  threshold?: number;
  rootMargin?: string;
  onLoad?: () => void;
  onError?: () => void;
  fallbackSrc?: string; // Default: use a data URL for inline placeholder
  className?: string;
  width?: number | string;
  height?: number | string;
}

// Default inline SVG placeholder to avoid broken image requests
const DEFAULT_FALLBACK = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23f0f0f0" width="100" height="100"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="14"%3EImage%3C/text%3E%3C/svg%3E';

export function LazyImage({
  src,
  alt,
  srcSet,
  placeholderSrc,
  threshold = 0.1,
  rootMargin = '50px',
  onLoad,
  onError,
  fallbackSrc = DEFAULT_FALLBACK,
  className = '',
  width,
  height,
  ...props
}: LazyImageProps) {
  const [imageSrc, setImageSrc] = useState(placeholderSrc || '');
  const [imageRef, setImageRef] = useState<HTMLImageElement | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Convert srcSet to string format if it's an object
  const srcSetString = convertSrcSetToString(srcSet);

  useEffect(() => {
    if (!imageRef) return;

    // Create intersection observer
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Load the actual image
            loadImage();
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(imageRef);

    return () => {
      if (imageRef) {
        observer.unobserve(imageRef);
      }
    };
  }, [imageRef, src, threshold, rootMargin]);

  const loadImage = () => {
    const img = new Image();
    
    img.onload = () => {
      setImageSrc(src);
      setIsLoaded(true);
      setHasError(false);
      onLoad?.();
    };

    img.onerror = () => {
      setImageSrc(fallbackSrc);
      setHasError(true);
      onError?.();
    };

    img.src = src;
  };

  return (
    <img
      ref={setImageRef}
      src={imageSrc}
      alt={alt}
      srcSet={srcSetString}
      className={`${className} ${isLoaded ? 'loaded' : 'loading'} ${hasError ? 'error' : ''}`}
      width={width}
      height={height}
      loading="lazy"
      decoding="async"
      {...props}
      style={{
        ...props.style,
        transition: 'opacity 0.3s ease-in-out',
        opacity: isLoaded ? 1 : 0.5,
      }}
    />
  );
}

/**
 * Progressive Image Component with Blur Placeholder
 */
interface ProgressiveImageProps extends LazyImageProps {
  lowQualitySrc?: string;
}

export function ProgressiveImage({
  src,
  lowQualitySrc,
  alt,
  className = '',
  ...props
}: ProgressiveImageProps) {
  const [currentSrc, setCurrentSrc] = useState(lowQualitySrc || '');
  const [isHighQualityLoaded, setIsHighQualityLoaded] = useState(false);

  useEffect(() => {
    // Load high quality image in background
    const img = new Image();
    img.onload = () => {
      setCurrentSrc(src);
      setIsHighQualityLoaded(true);
    };
    img.src = src;
  }, [src]);

  return (
    <div className={`progressive-image-container ${className}`} style={{ position: 'relative' }}>
      <LazyImage
        src={currentSrc}
        alt={alt}
        className={`${isHighQualityLoaded ? 'high-quality' : 'low-quality'}`}
        style={{
          filter: isHighQualityLoaded ? 'none' : 'blur(10px)',
          transition: 'filter 0.3s ease-in-out',
        }}
        {...props}
      />
    </div>
  );
}

/**
 * Responsive Image Component with srcset
 */
interface ResponsiveImageProps extends LazyImageProps {
  sizes?: string;
}

export function ResponsiveImage({
  src,
  srcSet,
  sizes,
  alt,
  ...props
}: ResponsiveImageProps) {
  return (
    <LazyImage
      src={src}
      alt={alt}
      srcSet={srcSet}
      sizes={sizes}
      {...props}
    />
  );
}

/**
 * Avatar Image Component with Optimizations
 */
interface AvatarImageProps {
  src: string;
  alt: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export function AvatarImage({ src, alt, size = 'md', className = '' }: AvatarImageProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };

  // Default avatar SVG placeholder
  const avatarFallback = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Ccircle fill="%23ddd" cx="50" cy="50" r="50"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="40"%3E👤%3C/text%3E%3C/svg%3E';

  return (
    <LazyImage
      src={src}
      alt={alt}
      className={`rounded-full object-cover ${sizeClasses[size]} ${className}`}
      fallbackSrc={avatarFallback}
    />
  );
}

/**
 * Hook for preloading images
 */
export function useImagePreload(urls: string[]) {
  useEffect(() => {
    urls.forEach((url) => {
      const img = new Image();
      img.src = url;
    });
  }, [urls]);
}

/**
 * Utility to generate responsive image URLs
 * For use with image CDN or server-side image processing
 */
export function getResponsiveImageUrls(
  baseUrl: string,
  widths: number[] = [320, 640, 768, 1024, 1280, 1920]
): { [key: string]: string } {
  const urls: { [key: string]: string } = {};
  
  widths.forEach((width) => {
    // Assuming image processing service that accepts width parameter
    urls[`${width}w`] = `${baseUrl}?w=${width}&q=80&auto=format`;
  });

  return urls;
}

/**
 * Generate optimized image URL with transformations
 */
export function optimizeImageUrl(
  url: string,
  options: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'avif' | 'jpeg' | 'png';
    fit?: 'cover' | 'contain' | 'fill';
  } = {}
): string {
  const {
    width,
    height,
    quality = 80,
    format = 'webp',
    fit = 'cover',
  } = options;

  // Build query parameters
  const params = new URLSearchParams();
  if (width) params.append('w', width.toString());
  if (height) params.append('h', height.toString());
  params.append('q', quality.toString());
  params.append('fmt', format);
  params.append('fit', fit);
  params.append('auto', 'format');

  // Return URL with parameters
  return `${url}?${params.toString()}`;
}

export default LazyImage;
