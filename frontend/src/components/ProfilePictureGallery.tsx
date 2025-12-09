import React, { useState, useEffect } from 'react';
import { profilePicturesAPI } from '../services/api';
import { PhotoIcon, TrashIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';
import toast from 'react-hot-toast';
import { ApiError } from '../types';

interface ProfilePicture {
  id: number;
  file_url: string;
  filename: string;
  file_size: number;
  is_current: boolean;
  created_at: string;
}

const ProfilePictureGallery: React.FC = () => {
  const [pictures, setPictures] = useState<ProfilePicture[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchPictures();
  }, []);

  const fetchPictures = async () => {
    try {
      const response = await profilePicturesAPI.listPictures();
      setPictures(response.pictures || []);
    } catch (error) {
      console.error('Error fetching profile pictures:', error);
      toast.error('Failed to load profile pictures');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      const fileArray: File[] = Array.from(files);
      
      // Validate files
      const validFiles: File[] = fileArray.filter((file): file is File => {
        if (!file.type.startsWith('image/')) {
          toast.error(`${file.name} is not an image file`);
          return false;
        }
        if (file.size > 10 * 1024 * 1024) {
          toast.error(`${file.name} is too large (max 10MB)`);
          return false;
        }
        return true;
      });

      if (validFiles.length === 0) {
        setUploading(false);
        return;
      }

      // Upload files
      if (validFiles.length === 1) {
        await profilePicturesAPI.uploadPicture(validFiles[0]);
        toast.success('Profile picture uploaded successfully!');
      } else {
        await profilePicturesAPI.uploadMultiplePictures(validFiles);
        toast.success(`${validFiles.length} profile pictures uploaded successfully!`);
      }

      // Refresh the gallery
      await fetchPictures();
      
      // Clear the input
      event.target.value = '';
    } catch (error: unknown) {
      const apiError = error as ApiError;
      console.error('Error uploading pictures:', error);
      toast.error(apiError.response?.data?.detail || 'Failed to upload pictures');
    } finally {
      setUploading(false);
    }
  };

  const handleSetCurrent = async (pictureId: number) => {
    try {
      await profilePicturesAPI.setCurrentPicture(pictureId);
      toast.success('Profile picture updated!');
      await fetchPictures();
    } catch (error: unknown) {
      const apiError = error as ApiError;
      console.error('Error setting current picture:', error);
      toast.error(apiError.response?.data?.detail || 'Failed to set profile picture');
    }
  };

  const handleDelete = async (pictureId: number) => {
    if (!confirm('Are you sure you want to delete this picture?')) return;

    try {
      await profilePicturesAPI.deletePicture(pictureId);
      toast.success('Picture deleted successfully!');
      await fetchPictures();
    } catch (error: unknown) {
      const apiError = error as ApiError;
      console.error('Error deleting picture:', error);
      toast.error(apiError.response?.data?.detail || 'Failed to delete picture');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Profile Pictures</h3>
        <label className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors cursor-pointer">
          <PhotoIcon className="h-5 w-5" />
          {uploading ? 'Uploading...' : 'Add Pictures'}
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileSelect}
            disabled={uploading}
            className="hidden"
          />
        </label>
      </div>

      {pictures.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">No profile pictures yet</p>
          <p className="text-xs text-gray-500 mt-1">Click "Add Pictures" to upload</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {pictures.map((picture) => (
            <div
              key={picture.id}
              className={`relative group rounded-lg overflow-hidden border-2 transition-all ${
                picture.is_current
                  ? 'border-blue-500 ring-2 ring-blue-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {/* Image */}
              <div className="aspect-square">
                <img
                  src={picture.file_url}
                  alt={picture.filename}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Current badge */}
              {picture.is_current && (
                <div className="absolute top-2 right-2 bg-blue-600 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1 shadow-lg">
                  <CheckCircleSolid className="h-3 w-3" />
                  Current
                </div>
              )}

              {/* Hover overlay with actions */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                {!picture.is_current && (
                  <button
                    onClick={() => handleSetCurrent(picture.id)}
                    className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition-colors shadow-lg"
                    title="Set as current profile picture"
                  >
                    <CheckCircleIcon className="h-5 w-5" />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(picture.id)}
                  className="bg-red-600 hover:bg-red-700 text-white p-2 rounded-lg transition-colors shadow-lg"
                  title="Delete picture"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>

              {/* File info */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <p className="text-white text-xs truncate">{picture.filename}</p>
                <p className="text-white text-xs">
                  {(picture.file_size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="text-sm text-gray-500 space-y-1">
        <p>• You can upload multiple pictures at once</p>
        <p>• Click on any picture to set it as your current profile picture</p>
        <p>• Maximum file size: 10MB per image</p>
        <p>• Supported formats: JPEG, PNG, GIF, WebP</p>
      </div>
    </div>
  );
};

export default ProfilePictureGallery;
