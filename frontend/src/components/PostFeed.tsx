import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  HeartIcon,
  ChatBubbleLeftIcon,
  ShareIcon,
  EllipsisHorizontalIcon,
  PhotoIcon,
  FaceSmileIcon,
  TrashIcon,
  PencilIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import { postsAPI } from '../services/api';
import { Post } from '../types';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const PostFeed: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  // const [newPostContent, setNewPostContent] = useState('');
  // const [isPosting, setIsPosting] = useState(false);
  // const [postType, setPostType] = useState<'post' | 'job'>('post');
  const [showComments, setShowComments] = useState<{ [key: number]: boolean }>({});
  const [commentText, setCommentText] = useState<{ [key: number]: string }>({});
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState<string>('');
  const { user } = useAuth();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const postsData = await postsAPI.getPosts();
      // Ensure postsData is an array
      if (Array.isArray(postsData)) {
        setPosts(postsData);
      } else {
        console.warn('Posts data is not an array:', postsData);
        setPosts([]);
        toast.error('Received invalid posts data from server');
      }
    } catch (error) {
      console.error('Failed to fetch posts:', error);
      setPosts([]); // Set empty array on error
      toast.error('Failed to load posts. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  // TODO: Implement create post inline functionality
  // const handleCreatePost = async (e: React.FormEvent) => {
  //   e.preventDefault();
  //   if (!newPostContent.trim()) return;
  //   setIsPosting(true);
  //   try {
  //     if (postType === 'job' && user?.user_type === 'employer') {
  //       window.location.href = '/post-job';
  //       return;
  //     }
  //     await postsAPI.createPost({ content: newPostContent.trim() });
  //     setNewPostContent('');
  //     toast.success('Post created!');
  //     fetchPosts();
  //   } catch (error) {
  //     console.error('Failed to create post:', error);
  //     toast.error('Failed to create post');
  //   } finally {
  //     setIsPosting(false);
  //   }
  // };

  const handleLikePost = async (postId: number) => {
    try {
      await postsAPI.likePost(postId.toString());
      // Update local state optimistically
      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.id === postId
            ? {
              ...post,
              likes_count: post.likes_count + 1,
              is_liked: !post.is_liked
            }
            : post
        )
      );
    } catch (error) {
      console.error('Failed to like post:', error);
      toast.error('Failed to like post');
    }
  };

  const handleComment = async (postId: number) => {
    const text = commentText[postId]?.trim();
    if (!text) return;

    try {
      // For now, just show a toast - in a real app you'd call an API
      toast.success('Comment added!');
      setCommentText(prev => ({ ...prev, [postId]: '' }));
    } catch (error) {
      toast.error('Failed to add comment');
    }
  };

  const handleDeletePost = async (postId: number) => {
    if (!window.confirm('Are you sure you want to delete this post? This cannot be undone.')) {
      return;
    }

    try {
      await postsAPI.deletePost(postId);
      setPosts(prevPosts => prevPosts.filter(p => p.id !== postId));
      toast.success('Post deleted successfully!');
    } catch (error) {
      console.error('Failed to delete post:', error);
      toast.error('Failed to delete post. Please try again.');
    }
  };

  const handleEditPost = (post: Post) => {
    setEditingPostId(post.id);
    setEditContent(post.content);
  };

  const handleCancelEdit = () => {
    setEditingPostId(null);
    setEditContent('');
  };

  const handleSaveEdit = async (postId: number) => {
    if (!editContent.trim()) {
      toast.error('Post content cannot be empty');
      return;
    }

    try {
      const response = await postsAPI.updatePost(postId, { content: editContent.trim() });
      setPosts(prevPosts =>
        prevPosts.map(p =>
          p.id === postId ? { ...p, content: response.post.content } : p
        )
      );
      setEditingPostId(null);
      setEditContent('');
      toast.success('Post updated successfully!');
    } catch (error) {
      console.error('Failed to update post:', error);
      toast.error('Failed to update post. Please try again.');
    }
  };

  const toggleComments = (postId: number) => {
    setShowComments(prev => ({ ...prev, [postId]: !prev[postId] }));
  };

  const formatTimeAgo = (dateString: string) => {
    const now = new Date();
    const postDate = new Date(dateString);
    const diffInMinutes = Math.floor((now.getTime() - postDate.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return 'now';
    if (diffInMinutes < 60) return `${diffInMinutes}m`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h`;
    return `${Math.floor(diffInMinutes / 1440)}d`;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Posts Feed */}
      {posts.map((post, index) => (
        <motion.div
          key={post.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
        >
          {/* Post Header */}
          <div className="p-4 pb-3">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-semibold text-sm">
                    {post.user.first_name[0]}{post.user.last_name[0]}
                  </span>
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <h3 className="text-sm font-semibold text-gray-900 truncate">
                    {post.user.first_name} {post.user.last_name}
                  </h3>
                  <span className="text-sm text-gray-500">·</span>
                  <span className="text-sm text-gray-500">
                    {formatTimeAgo(post.created_at)}
                  </span>
                </div>
                <p className="text-xs text-blue-600 font-medium truncate">
                  @{post.user.username || post.user.email.split('@')[0]}
                </p>
                <p className="text-xs text-gray-600 truncate">
                  {post.user.occupation || post.user.company_name || 'Professional'}
                </p>
              </div>
              {/* Show Edit/Delete buttons only for post owner */}
              {user && post.user.id === user.id && (
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleEditPost(post)}
                    className="text-blue-600 hover:text-blue-700 p-2 rounded-full hover:bg-blue-50 transition-colors"
                    title="Edit post"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeletePost(post.id)}
                    className="text-red-600 hover:text-red-700 p-2 rounded-full hover:bg-red-50 transition-colors"
                    title="Delete post"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              )}
              {/* Show menu button for non-owners */}
              {(!user || post.user.id !== user.id) && (
                <button
                  className="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100"
                  title="More options"
                >
                  <EllipsisHorizontalIcon className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>

          {/* Post Content */}
          <div className="px-4 pb-3">
            {editingPostId === post.id ? (
              // Edit mode
              <div className="space-y-2">
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                  placeholder="Edit your post..."
                />
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={handleCancelEdit}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleSaveEdit(post.id)}
                    disabled={!editContent.trim()}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            ) : (
              // View mode
              <>
                <p className="text-gray-900 whitespace-pre-wrap text-sm leading-relaxed">{post.content}</p>
                {post.image_url && (
                  <div className="mt-3 rounded-lg overflow-hidden border border-gray-200">
                    <img
                      src={post.image_url}
                      alt="Post image"
                      className="w-full h-auto max-h-96 object-cover"
                    />
                  </div>
                )}
              </>
            )}
          </div>

          {/* Post Stats */}
          {(post.likes_count > 0) && (
            <div className="px-4 py-2 text-sm text-gray-500 border-b border-gray-100">
              <span className="flex items-center space-x-1">
                <div className="w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                  <HeartIconSolid className="w-2.5 h-2.5 text-white" />
                </div>
                <span>{post.likes_count} {post.likes_count === 1 ? 'like' : 'likes'}</span>
              </span>
            </div>
          )}

          {/* Post Actions */}
          <div className="px-4 py-2 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <button
                onClick={() => handleLikePost(post.id)}
                className={`flex items-center space-x-2 flex-1 justify-center py-2 px-4 rounded-lg hover:bg-gray-100 transition-colors ${
                  post.is_liked ? 'text-red-600' : 'text-gray-600'
                }`}
              >
                {post.is_liked ? (
                  <HeartIconSolid className="w-5 h-5" />
                ) : (
                  <HeartIcon className="w-5 h-5" />
                )}
                <span className="text-sm font-medium">Like</span>
              </button>

              <button
                onClick={() => toggleComments(post.id)}
                className="flex items-center space-x-2 flex-1 justify-center py-2 px-4 rounded-lg hover:bg-gray-100 transition-colors text-gray-600"
              >
                <ChatBubbleLeftIcon className="w-5 h-5" />
                <span className="text-sm font-medium">Comment</span>
              </button>

              <button className="flex items-center space-x-2 flex-1 justify-center py-2 px-4 rounded-lg hover:bg-gray-100 transition-colors text-gray-600">
                <ShareIcon className="w-5 h-5" />
                <span className="text-sm font-medium">Share</span>
              </button>
            </div>
          </div>

          {/* Comments Section */}
          {showComments[post.id] && (
            <div className="px-4 py-3 bg-gray-50">
              {/* Add Comment */}
              {user && (
                <div className="flex space-x-3 mb-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold text-xs">
                        {user.first_name?.[0]}{user.last_name?.[0]}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1 flex space-x-2">
                    <input
                      type="text"
                      value={commentText[post.id] || ''}
                      onChange={(e) => setCommentText(prev => ({ ...prev, [post.id]: e.target.value }))}
                      placeholder="Write a comment..."
                      className="flex-1 px-3 py-2 bg-white border border-gray-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onKeyPress={(e) => e.key === 'Enter' && handleComment(post.id)}
                    />
                    <button className="p-2 text-gray-400 hover:text-blue-600">
                      <FaceSmileIcon className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-green-600">
                      <PhotoIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              )}

              {/* Comments List */}
              <div className="space-y-3">
                {/* Sample comments - in real app these would come from API */}
                <div className="flex space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold text-xs">JD</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="bg-white rounded-2xl px-3 py-2">
                      <p className="text-sm font-medium text-gray-900">John Doe</p>
                      <p className="text-sm text-gray-700">Great post! Very inspiring.</p>
                    </div>
                    <div className="flex items-center space-x-4 mt-1 ml-3">
                      <button className="text-xs text-gray-500 hover:text-gray-700">Like</button>
                      <button className="text-xs text-gray-500 hover:text-gray-700">Reply</button>
                      <span className="text-xs text-gray-400">2h</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      ))}

      {posts.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <ChatBubbleLeftIcon className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No posts yet</h3>
          <p className="text-gray-600">Be the first to share something!</p>
        </div>
      )}
    </div>
  );
};

export default PostFeed;