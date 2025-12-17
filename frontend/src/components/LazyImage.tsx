/**
 * LazyImage Component - Final Optimized Version
 * 
 * Features:
 * - Native lazy loading with loading attribute
 * - Async decoding for better performance
 * - Priority prop for above-the-fold images
 * - Object-fit cover for proper sizing
 * - Core Web Vitals optimization
 */
import React from 'react';

interface LazyImageProps {
  src: string;
  alt?: string;
  width?: number;
  height?: number;
  priority?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

export default function LazyImage({
  src,
  alt = "",
  width,
  height,
  priority = false,
  className = "",
  style = {},
}: LazyImageProps) {
  return (
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      loading={priority ? "eager" : "lazy"}
      decoding="async"
      className={className}
      style={{ ...style, objectFit: style.objectFit || "cover" }}
    />
  );
}
