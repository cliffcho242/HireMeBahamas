import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import EmojiPicker, { EmojiClickData } from 'emoji-picker-react';
import {
  XMarkIcon,
  PhotoIcon,
  FaceSmileIcon,
  MapPinIcon,
  TagIcon,
  EllipsisHorizontalIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { postsAPI } from '../services/api';

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPostCreated?: () => void;
}

const CreatePostModal: React.FC<CreatePostModalProps> = ({ isOpen, onClose, onPostCreated }) => {
  const { user } = useAuth();
  const [content, setContent] = useState('');
  const [isPosting, setIsPosting] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const emojiPickerRef = useRef<HTMLDivElement>(null);

  // Close emoji picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target as Node)) {
        setShowEmojiPicker(false);
      }
    };

    if (showEmojiPicker) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showEmojiPicker]);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const fileArray = Array.from(files).slice(0, 4); // Limit to 4 images
      setSelectedImages(fileArray);
      
      // Create previews
      const previews: string[] = [];
      fileArray.forEach((file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          previews.push(e.target?.result as string);
          if (previews.length === fileArray.length) {
            setImagePreviews(previews);
          }
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const handleEmojiClick = (emojiData: EmojiClickData) => {
    const emoji = emojiData.emoji;
    const textarea = textareaRef.current;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newContent = content.substring(0, start) + emoji + content.substring(end);
      setContent(newContent);
      
      // Set cursor position after emoji
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
        textarea.focus();
      }, 0);
    } else {
      setContent(content + emoji);
    }
    setShowEmojiPicker(false);
  };

  const handleSubmit = async () => {
    if (!content.trim() && selectedImages.length === 0) return;

    setIsPosting(true);
    try {
      // For now, just create post with first image
      // TODO: Implement proper multi-image upload to a storage service
      await postsAPI.createPost({
        content: content.trim(),
        image_url: imagePreviews[0] || undefined
      });
      toast.success('Post created successfully! 🎉');
      setContent('');
      setSelectedImages([]);
      setImagePreviews([]);
      setShowEmojiPicker(false);
      onPostCreated?.();
      onClose();
    } catch (error) {
      toast.error('Failed to create post');
    } finally {
      setIsPosting(false);
    }
  };

  const removeImage = (index?: number) => {
    if (index !== undefined && selectedImages.length > 0) {
      // Remove specific image from gallery
      const newImages = [...selectedImages];
      const newPreviews = [...imagePreviews];
      newImages.splice(index, 1);
      newPreviews.splice(index, 1);
      setSelectedImages(newImages);
      setImagePreviews(newPreviews);
    } else {
      // Remove all images
      setSelectedImages([]);
      setImagePreviews([]);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={onClose}
          >
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Create Post</h2>
                <button
                  onClick={onClose}
                  className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                >
                  <XMarkIcon className="w-6 h-6 text-gray-500" />
                </button>
              </div>

              {/* Content */}
              <div className="p-4">
                {/* User Info */}
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">
                      {user?.first_name?.[0]}{user?.last_name?.[0]}
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">
                      {user?.first_name} {user?.last_name}
                    </p>
                    <p className="text-xs text-blue-600 font-medium">
                      @{user?.username || user?.email?.split('@')[0] || `${user?.first_name?.toLowerCase()}${user?.last_name?.toLowerCase()}`}
                    </p>
                    <p className="text-xs text-gray-600">
                      {user?.occupation || user?.company_name || user?.user_type?.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className="flex items-center space-x-1 text-sm text-gray-600 hover:bg-gray-100 px-2 py-1 rounded">
                      <span>🌐</span>
                      <span>Public</span>
                    </button>
                  </div>
                </div>

                {/* Text Input */}
                <textarea
                  ref={textareaRef}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder={`What's on your mind, ${user?.first_name}?`}
                  className="w-full border-0 resize-none focus:ring-0 text-lg placeholder-gray-500 mb-4"
                  rows={4}
                  maxLength={280}
                />

                {/* Character Count */}
                <div className="text-right text-sm text-gray-500 mb-4">
                  {content.length}/280
                </div>

                {/* Image Gallery Preview */}
                {imagePreviews.length > 0 && (
                  <div className={`grid gap-2 mb-4 ${
                    imagePreviews.length === 1 ? 'grid-cols-1' :
                    imagePreviews.length === 2 ? 'grid-cols-2' :
                    imagePreviews.length === 3 ? 'grid-cols-3' :
                    'grid-cols-2'
                  }`}>
                    {imagePreviews.map((preview, index) => (
                      <div key={index} className="relative">
                        <img
                          src={preview}
                          alt={`Preview ${index + 1}`}
                          className="w-full h-48 object-cover rounded-lg"
                        />
                        <button
                          onClick={() => removeImage(index)}
                          className="absolute top-2 right-2 p-1 bg-black bg-opacity-50 rounded-full text-white hover:bg-opacity-70 transition-colors"
                          title="Remove image"
                        >
                          <XMarkIcon className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add to Post Options */}
                <div className="border border-gray-200 rounded-lg p-4 mb-4">
                  <p className="text-sm font-medium text-gray-900 mb-3">Add to your post</p>
                  <div className="flex items-center space-x-2 relative">
                    <label className="p-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors" title="Add photos">
                      <input
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handleImageSelect}
                        className="hidden"
                        aria-label="Upload images"
                      />
                      <PhotoIcon className="w-6 h-6 text-green-600" />
                    </label>
                    <button 
                      className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                      title="Add emoji"
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                    >
                      <FaceSmileIcon className="w-6 h-6 text-yellow-600" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors" title="Tag people">
                      <TagIcon className="w-6 h-6 text-blue-600" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors" title="Add location">
                      <MapPinIcon className="w-6 h-6 text-red-600" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors" title="More options">
                      <EllipsisHorizontalIcon className="w-6 h-6 text-gray-600" />
                    </button>
                    
                    {/* Emoji Picker */}
                    {showEmojiPicker && (
                      <div ref={emojiPickerRef} className="absolute bottom-12 left-0 z-50">
                        <EmojiPicker onEmojiClick={handleEmojiClick} />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="border-t border-gray-200 p-4">
                <button
                  onClick={handleSubmit}
                  disabled={(content.trim().length === 0 && selectedImages.length === 0) || isPosting}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isPosting ? 'Posting...' : 'Post'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default CreatePostModal;