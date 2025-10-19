import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!content.trim() && !selectedImage) return;

    setIsPosting(true);
    try {
      // For now, just create post without image upload
      // TODO: Implement proper image upload to a storage service
      await postsAPI.createPost({
        content: content.trim(),
        image_url: imagePreview || undefined
      });
      toast.success('Post created successfully!');
      setContent('');
      setSelectedImage(null);
      setImagePreview(null);
      onPostCreated?.();
      onClose();
    } catch (error) {
      toast.error('Failed to create post');
    } finally {
      setIsPosting(false);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
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

                {/* Image Preview */}
                {imagePreview && (
                  <div className="relative mb-4">
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="w-full max-h-64 object-cover rounded-lg"
                    />
                    <button
                      onClick={removeImage}
                      className="absolute top-2 right-2 p-1 bg-black bg-opacity-50 rounded-full text-white hover:bg-opacity-70 transition-colors"
                    >
                      <XMarkIcon className="w-4 h-4" />
                    </button>
                  </div>
                )}

                {/* Add to Post Options */}
                <div className="border border-gray-200 rounded-lg p-4 mb-4">
                  <p className="text-sm font-medium text-gray-900 mb-3">Add to your post</p>
                  <div className="flex items-center space-x-2">
                    <label className="p-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageSelect}
                        className="hidden"
                      />
                      <PhotoIcon className="w-6 h-6 text-green-600" />
                    </label>
                    <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                      <TagIcon className="w-6 h-6 text-blue-600" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                      <FaceSmileIcon className="w-6 h-6 text-yellow-600" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                      <MapPinIcon className="w-6 h-6 text-red-600" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                      <EllipsisHorizontalIcon className="w-6 h-6 text-gray-600" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="border-t border-gray-200 p-4">
                <button
                  onClick={handleSubmit}
                  disabled={!content.trim() && !selectedImage || isPosting}
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