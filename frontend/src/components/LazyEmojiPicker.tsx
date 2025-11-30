import React, { Suspense, lazy } from 'react';
import type { EmojiClickData } from 'emoji-picker-react';
import { Theme } from 'emoji-picker-react';

// Lazy load the heavy emoji picker component (270KB+)
const EmojiPicker = lazy(() => import('emoji-picker-react'));

interface LazyEmojiPickerProps {
  onEmojiClick: (emojiData: EmojiClickData) => void;
  theme?: Theme;
  width?: number | string;
  height?: number | string;
}

// Loading placeholder for emoji picker
const EmojiPickerSkeleton = () => (
  <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4 w-[350px] h-[400px] flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
      <p className="text-gray-500 text-sm">Loading emojis...</p>
    </div>
  </div>
);

/**
 * Lazy-loaded wrapper for emoji-picker-react to reduce initial bundle size.
 * The emoji picker is only loaded when the component is rendered.
 */
const LazyEmojiPicker: React.FC<LazyEmojiPickerProps> = ({
  onEmojiClick,
  theme = Theme.LIGHT,
  width = 350,
  height = 400,
}) => {
  return (
    <Suspense fallback={<EmojiPickerSkeleton />}>
      <EmojiPicker
        onEmojiClick={onEmojiClick}
        theme={theme}
        width={width}
        height={height}
        lazyLoadEmojis={true}
        searchDisabled={false}
        skinTonesDisabled={false}
        previewConfig={{
          showPreview: true,
        }}
      />
    </Suspense>
  );
};

export default LazyEmojiPicker;
