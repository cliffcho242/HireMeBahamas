import { ChangeEvent, useState, useEffect } from 'react';
import { PlusIcon, XMarkIcon } from '@heroicons/react/24/solid';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { apiUrl } from '@/lib/api';

interface Story {
  id: number;
  content: string;
  image_url: string;
  video_url: string;
  created_at: string;
  user: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    user_type: string;
  };
}

const Stories = () => {
  const { user, token } = useAuth();
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [storyContent, setStoryContent] = useState('');
  const [storyImageFile, setStoryImageFile] = useState<File | null>(null);
  const [storyVideoFile, setStoryVideoFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [videoPreview, setVideoPreview] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchStories();
  }, []);

  const fetchStories = async () => {
    try {
      const storiesUrl = apiUrl('/api/stories');
      const response = await axios.get(storiesUrl);
      if (response.data.success) {
        setStories(response.data.stories);
      }
    } catch (error) {
      console.error('Error fetching stories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event: ChangeEvent<HTMLInputElement>, type: 'image' | 'video') => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    const allowedVideoTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/webm'];

    if (type === 'image' && !allowedImageTypes.includes(file.type)) {
      alert('Please select a valid image file (JPEG, PNG, GIF)');
      return;
    }

    if (type === 'video' && !allowedVideoTypes.includes(file.type)) {
      alert('Please select a valid video file (MP4, MOV, AVI, WebM)');
      return;
    }

    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      alert('File size must be less than 50MB');
      return;
    }

    if (type === 'image') {
      setStoryImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    } else {
      setStoryVideoFile(file);
      setVideoPreview(URL.createObjectURL(file));
    }
  };

  const uploadFile = async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);

    const uploadUrl = apiUrl('/api/upload/story-file');
    const response = await axios.post(
      uploadUrl,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    if (response.data.success) {
      return response.data.file_path;
    } else {
      throw new Error(response.data.message || 'Upload failed');
    }
  };

  const handleCreateStory = async () => {
    if (!storyContent.trim()) {
      alert('Please enter some content for your story');
      return;
    }

    setCreating(true);
    try {
      let imagePath = '';
      let videoPath = '';

      // Upload image if selected
      if (storyImageFile) {
        setUploading(true);
        try {
          imagePath = await uploadFile(storyImageFile);
        } catch {
          alert('Failed to upload image. Please try again.');
          return;
        } finally {
          setUploading(false);
        }
      }

      // Upload video if selected
      if (storyVideoFile) {
        setUploading(true);
        try {
          videoPath = await uploadFile(storyVideoFile);
        } catch {
          alert('Failed to upload video. Please try again.');
          return;
        } finally {
          setUploading(false);
        }
      }

      // Create story
      const createStoryUrl = apiUrl('/api/stories');
      const response = await axios.post(
        createStoryUrl,
        {
          content: storyContent,
          image_path: imagePath,
          video_path: videoPath
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        setStories(prev => [response.data.story, ...prev]);
        setShowCreateModal(false);
        setStoryContent('');
        setStoryImageFile(null);
        setStoryVideoFile(null);
        setImagePreview('');
        setVideoPreview('');
      }
    } catch (error) {
      console.error('Error creating story:', error);
      alert('Failed to create story. Please try again.');
    } finally {
      setCreating(false);
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
        <div className="flex space-x-4 overflow-x-auto pb-2">
          <div className="flex-shrink-0 w-20 h-28 bg-gray-200 rounded-lg animate-pulse"></div>
          <div className="flex-shrink-0 w-20 h-28 bg-gray-200 rounded-lg animate-pulse"></div>
          <div className="flex-shrink-0 w-20 h-28 bg-gray-200 rounded-lg animate-pulse"></div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm p-4 4xl:p-6 mb-4 post-card-smooth">
        <div className="flex space-x-4 4xl:space-x-6 overflow-x-auto pb-2 stories-scroll scroll-smooth-gpu">
          {/* Create Story */}
          {user && (
            <div className="flex-shrink-0 story-item">
              <div
                className="relative w-20 h-28 4xl:w-24 4xl:h-32 bg-gray-100 rounded-lg overflow-hidden cursor-pointer avatar-interactive"
                onClick={() => setShowCreateModal(true)}
              >
                <div className="w-full h-3/4 bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
                  <div className="w-8 h-8 4xl:w-10 4xl:h-10 bg-white rounded-full flex items-center justify-center social-btn">
                    <PlusIcon className="w-5 h-5 4xl:w-6 4xl:h-6 text-blue-600" />
                  </div>
                </div>
                <div className="absolute bottom-0 left-0 right-0 bg-white p-2">
                  <p className="text-xs 4xl:text-sm font-medium text-center text-gray-900 text-render-5k">Create Story</p>
                </div>
                <div className="absolute -top-1 -left-1 w-6 h-6 4xl:w-7 4xl:h-7 bg-blue-600 rounded-full flex items-center justify-center border-2 border-white story-ring-animated">
                  <div className="w-3 h-3 4xl:w-4 4xl:h-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-xs text-render-5k">
                      {user.first_name?.[0]}{user.last_name?.[0]}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Stories */}
          {stories.map((story) => (
            <div key={story.id} className="flex-shrink-0 story-item">
              <div
                onClick={() => setSelectedStory(story)}
                className="relative w-20 h-28 4xl:w-24 4xl:h-32 rounded-lg overflow-hidden cursor-pointer avatar-interactive ring-2 ring-blue-500 story-ring-animated"
              >
                {story.video_url ? (
                  <video
                    src={story.video_url}
                    className="w-full h-full object-cover gpu-accelerated"
                    muted
                    loop
                    playsInline
                    onMouseEnter={(e) => e.currentTarget.play()}
                    onMouseLeave={(e) => e.currentTarget.pause()}
                  />
                ) : story.image_url ? (
                  <img
                    src={story.image_url}
                    alt={`${story.user.first_name} ${story.user.last_name}`}
                    className="w-full h-full object-cover image-fade-in loaded"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
                    <span className="text-white font-bold text-lg 4xl:text-xl text-render-5k">
                      {story.user.first_name[0]}{story.user.last_name[0]}
                    </span>
                  </div>
                )}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                  <p className="text-xs 4xl:text-sm font-medium text-white text-center truncate text-render-5k">
                    {story.user.first_name}
                  </p>
                </div>
                {story.video_url && (
                  <div className="absolute top-2 right-2 w-4 h-4 4xl:w-5 4xl:h-5 bg-black/50 rounded-full flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  </div>
                )}
                <div className="absolute top-2 left-2 w-3 h-3 4xl:w-4 4xl:h-4 bg-blue-500 rounded-full border border-white"></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Story Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
          <div className="glass-modal rounded-xl p-6 w-full max-w-md mx-4 4xl:max-w-lg animate-scale-in">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg 4xl:text-xl font-semibold text-render-5k">Create Story</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-500 hover:text-gray-700 social-btn p-1 rounded-full"
              >
                <XMarkIcon className="w-6 h-6 4xl:w-7 4xl:h-7" />
              </button>
            </div>

            <div className="space-y-4 4xl:space-y-5">
              <div>
                <label className="block text-sm 4xl:text-base font-medium text-gray-700 mb-2">
                  Story Content *
                </label>
                <textarea
                  value={storyContent}
                  onChange={(e) => setStoryContent(e.target.value)}
                  placeholder="What's on your mind?"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                  maxLength={500}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {storyContent.length}/500 characters
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image (optional)
                </label>
                <div className="space-y-2">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileSelect(e, 'image')}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    capture="environment"
                  />
                  {imagePreview && (
                    <div className="relative">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="w-full h-32 object-cover rounded-lg"
                      />
                      <button
                        onClick={() => {
                          setStoryImageFile(null);
                          setImagePreview('');
                        }}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                      >
                        ×
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Video (optional)
                </label>
                <div className="space-y-2">
                  <input
                    type="file"
                    accept="video/*"
                    onChange={(e) => handleFileSelect(e, 'video')}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    capture="environment"
                  />
                  {videoPreview && (
                    <div className="relative">
                      <video
                        src={videoPreview}
                        className="w-full h-32 object-cover rounded-lg"
                        controls
                      />
                      <button
                        onClick={() => {
                          setStoryVideoFile(null);
                          setVideoPreview('');
                        }}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                      >
                        ×
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  disabled={creating || uploading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateStory}
                  disabled={creating || uploading || !storyContent.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors"
                >
                  {uploading ? 'Uploading...' : creating ? 'Creating...' : 'Create Story'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View Story Modal */}
      {selectedStory && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Story</h3>
              <button
                onClick={() => setSelectedStory(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>

            <div className="relative max-w-md mx-auto">
              {selectedStory.video_url ? (
                <video
                  src={selectedStory.video_url}
                  className="w-full max-h-96 object-contain rounded-lg"
                  controls
                  autoPlay
                  muted
                />
              ) : selectedStory.image_url ? (
                <img
                  src={selectedStory.image_url}
                  alt={`${selectedStory.user.first_name} ${selectedStory.user.last_name}`}
                  className="w-full max-h-96 object-contain rounded-lg"
                />
              ) : (
                <div className="w-full h-64 bg-gradient-to-br from-purple-400 to-pink-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-4xl">
                    {selectedStory.user.first_name[0]}{selectedStory.user.last_name[0]}
                  </span>
                </div>
              )}
              <div className="mt-4">
                <p className="text-sm text-gray-700 mb-2">{selectedStory.content}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{selectedStory.user.first_name} {selectedStory.user.last_name}</span>
                  <span>{new Date(selectedStory.created_at).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Stories;
