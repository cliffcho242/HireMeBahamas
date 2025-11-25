import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import EmojiPicker, { EmojiClickData } from 'emoji-picker-react';
import {
  HeartIcon,
  ChatBubbleLeftIcon,
  ShareIcon,
  EllipsisHorizontalIcon,
  FaceSmileIcon,
  TrashIcon,
  PencilIcon,
  WifiIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import { postsAPI } from '../services/api';
import { Post, PostUser } from '../types';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { postCache } from '../services/postCache';

// Type for posts that have a valid user - used after filtering
interface ValidPost extends Post {
  user: PostUser;
}

// Interface for comment user data
interface CommentUser {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  username?: string;
}

// Interface for comment data
interface Comment {
  id: number;
  user?: CommentUser;
  content: string;
  created_at: string;
}

// Type for comments that have a valid user - used after filtering
interface ValidComment extends Comment {
  user: CommentUser;
}

// Type guard to check if a post has a valid user
function hasValidUser(post: Post): post is ValidPost {
  return post.user != null && typeof post.user.id === 'number';
}

// Type guard to check if a comment has a valid user
function hasValidCommentUser(comment: Comment): comment is ValidComment {
  return comment.user != null && typeof comment.user.id === 'number';
}

const PostFeed: React.FC = () => {
  const [posts, setPosts] = useState<ValidPost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const navigate = useNavigate();
  const [showComments, setShowComments] = useState<{ [key: number]: boolean }>({});
  const [commentText, setCommentText] = useState<{ [key: number]: string }>({});
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState<string>('');
  const [comments, setComments] = useState<{ [key: number]: Comment[] }>({});
  const [loadingComments, setLoadingComments] = useState<{ [key: number]: boolean }>({});
  const [showEmojiPicker, setShowEmojiPicker] = useState<{ [key: number]: boolean }>({});
  const { user } = useAuth();
  const syncIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Sync pending actions when online
  const syncPendingActions = useCallback(async () => {
    if (!isOnline || !postCache.isCacheAvailable()) return;

    try {
      const pendingActions = await postCache.getPendingActions();
      
      for (const action of pendingActions) {
        try {
          switch (action.type) {
            case 'create':
              if (action.data.content) {
                await postsAPI.createPost({
                  content: action.data.content,
                  image_url: action.data.image_url,
                  video_url: action.data.video_url
                });
              }
              break;
            case 'update':
              if (action.postId && action.data.content) {
                await postsAPI.updatePost(action.postId, { content: action.data.content });
              }
              break;
            case 'delete':
              if (action.postId) {
                await postsAPI.deletePost(action.postId);
              }
              break;
            case 'like':
              if (action.postId) {
                await postsAPI.likePost(action.postId);
              }
              break;
            case 'comment':
              if (action.postId && action.data.content) {
                await postsAPI.createComment(action.postId, action.data.content);
              }
              break;
          }
          
          // Remove successful action
          await postCache.removePendingAction(action.id);
        } catch {
          // Update retry count
          if (action.retryCount < 3) {
            await postCache.updatePendingActionRetry(action.id);
          } else {
            // Remove after 3 retries
            await postCache.removePendingAction(action.id);
            console.error('Failed to sync action after 3 retries:', action);
          }
        }
      }
    } catch (error) {
      console.error('Failed to sync pending actions:', error);
    }
  }, [isOnline]);

  const fetchPosts = useCallback(async (useCache = true) => {
    try {
      // Load from cache first for instant display
      if (useCache && postCache.isCacheAvailable()) {
        const cachedPosts = await postCache.getCachedPosts();
        // Filter out posts with missing user data using type guard
        const validCachedPosts = cachedPosts.filter(hasValidUser);
        if (validCachedPosts.length > 0) {
          setPosts(validCachedPosts);
          setIsLoading(false);
        }
      }

      // Then fetch fresh data from server if online
      if (isOnline) {
        const postsData = await postsAPI.getPosts();
        
        if (Array.isArray(postsData)) {
          // Filter out posts with missing user data to prevent runtime errors
          const validPosts = postsData.filter(hasValidUser);
          setPosts(validPosts);
          
          // Cache the fresh data
          if (postCache.isCacheAvailable()) {
            await postCache.cachePosts(validPosts);
          }
        } else {
          console.warn('Posts data is not an array:', postsData);
          if (!useCache) {
            setPosts([]);
            toast.error('Received invalid posts data from server');
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch posts:', error);
      // Error toast will be shown by the calling code if needed
    } finally {
      setIsLoading(false);
    }
  }, [isOnline]);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success('Connection restored');
      // Immediately sync and fetch when coming back online
      syncPendingActions();
      fetchPosts();
    };
    
    const handleOffline = () => {
      setIsOnline(false);
      toast.error('You are offline. Changes will be synced when connection is restored.');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [fetchPosts, syncPendingActions]);

  useEffect(() => {
    fetchPosts();
    
    // Setup periodic sync (every 30 seconds)
    if (isOnline) {
      syncIntervalRef.current = setInterval(() => {
        fetchPosts();
        syncPendingActions();
      }, 30000);
    }

    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, [isOnline, fetchPosts, syncPendingActions]);

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
    if (!user) {
      toast.error('Please log in to like posts');
      return;
    }

    // Optimistic update
    const originalPosts = [...posts];
    const postToUpdate = posts.find(p => p.id === postId);
    if (!postToUpdate) return;

    const optimisticUpdate = {
      ...postToUpdate,
      is_liked: !postToUpdate.is_liked,
      likes_count: postToUpdate.is_liked 
        ? postToUpdate.likes_count - 1 
        : postToUpdate.likes_count + 1
    };

    setPosts(prevPosts =>
      prevPosts.map(post =>
        post.id === postId ? optimisticUpdate : post
      )
    );

    // Update cache immediately
    if (postCache.isCacheAvailable()) {
      await postCache.updateCachedPost(postId, optimisticUpdate);
    }

    try {
      if (isOnline) {
        const response = await postsAPI.likePost(postId);
        // Update with server response
        setPosts(prevPosts =>
          prevPosts.map(post =>
            post.id === postId
              ? {
                ...post,
                likes_count: response.likes_count,
                is_liked: response.liked
              }
              : post
          )
        );

        // Update cache with server data
        if (postCache.isCacheAvailable()) {
          await postCache.updateCachedPost(postId, {
            likes_count: response.likes_count,
            is_liked: response.liked
          });
        }
      } else {
        // Queue for later if offline
        await postCache.addPendingAction({
          type: 'like',
          postId,
          data: {},
          timestamp: Date.now(),
          retryCount: 0,
        });
        toast.success('Like saved. Will sync when online.');
      }
    } catch (error) {
      // Rollback on error
      console.error('Failed to like post:', error);
      setPosts(originalPosts);
      
      if (postCache.isCacheAvailable()) {
        await postCache.updateCachedPost(postId, postToUpdate);
      }
      
      toast.error('Failed to like post');
    }
  };

  const handleComment = async (postId: number) => {
    const text = commentText[postId]?.trim();
    if (!text) return;

    if (!user) {
      toast.error('Please log in to comment');
      return;
    }

    try {
      const response = await postsAPI.createComment(postId, text);
      
      // Add comment to local state
      setComments(prev => ({
        ...prev,
        [postId]: [...(prev[postId] || []), response.comment]
      }));
      
      // Update comment count
      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.id === postId
            ? { ...post, comments_count: post.comments_count + 1 }
            : post
        )
      );
      
      setCommentText(prev => ({ ...prev, [postId]: '' }));
      toast.success('Comment added!');
    } catch (error) {
      console.error('Failed to add comment:', error);
      toast.error('Failed to add comment');
    }
  };

  const handleDeleteComment = async (postId: number, commentId: number) => {
    if (!window.confirm('Delete this comment?')) return;

    try {
      await postsAPI.deleteComment(postId, commentId);
      
      // Remove comment from local state
      setComments(prev => ({
        ...prev,
        [postId]: (prev[postId] || []).filter(c => c.id !== commentId)
      }));
      
      // Update comment count
      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.id === postId
            ? { ...post, comments_count: Math.max(0, post.comments_count - 1) }
            : post
        )
      );
      
      toast.success('Comment deleted!');
    } catch (error) {
      console.error('Failed to delete comment:', error);
      toast.error('Failed to delete comment');
    }
  };

  const handleEmojiClick = (postId: number, emojiData: EmojiClickData) => {
    setCommentText(prev => ({
      ...prev,
      [postId]: (prev[postId] || '') + emojiData.emoji
    }));
    setShowEmojiPicker(prev => ({ ...prev, [postId]: false }));
  };

  const toggleEmojiPicker = (postId: number) => {
    setShowEmojiPicker(prev => ({ ...prev, [postId]: !prev[postId] }));
  };

  // Close emoji picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const isEmojiButton = target.closest('.emoji-picker-button');
      const isEmojiPicker = target.closest('.emoji-picker-container');
      
      if (!isEmojiButton && !isEmojiPicker) {
        setShowEmojiPicker({});
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadComments = async (postId: number) => {
    if (comments[postId]) {
      // Already loaded, just toggle
      setShowComments(prev => ({ ...prev, [postId]: !prev[postId] }));
      return;
    }

    setLoadingComments(prev => ({ ...prev, [postId]: true }));
    try {
      const commentsData = await postsAPI.getComments(postId);
      setComments(prev => ({ ...prev, [postId]: commentsData }));
      setShowComments(prev => ({ ...prev, [postId]: true }));
    } catch (error) {
      console.error('Failed to load comments:', error);
      toast.error('Failed to load comments');
    } finally {
      setLoadingComments(prev => ({ ...prev, [postId]: false }));
    }
  };

  const handleDeletePost = async (postId: number) => {
    if (!window.confirm('Are you sure you want to delete this post? This cannot be undone.')) {
      return;
    }

    // Optimistic update
    const originalPosts = [...posts];
    setPosts(prevPosts => prevPosts.filter(p => p.id !== postId));

    // Update cache immediately
    if (postCache.isCacheAvailable()) {
      await postCache.deleteCachedPost(postId);
    }

    try {
      if (isOnline) {
        await postsAPI.deletePost(postId);
        toast.success('Post deleted successfully!');
      } else {
        // Queue for later if offline
        await postCache.addPendingAction({
          type: 'delete',
          postId,
          data: {},
          timestamp: Date.now(),
          retryCount: 0,
        });
        toast.success('Delete saved. Will sync when online.');
      }
    } catch (error) {
      // Rollback on error
      console.error('Failed to delete post:', error);
      setPosts(originalPosts);
      
      if (postCache.isCacheAvailable()) {
        const deletedPost = originalPosts.find(p => p.id === postId);
        if (deletedPost) {
          await postCache.updateCachedPost(postId, deletedPost);
        }
      }
      
      toast.error('Failed to delete post. Please try again.');
    }
  };

  const handleEditPost = (post: ValidPost) => {
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

    // Optimistic update
    const originalPosts = [...posts];
    setPosts(prevPosts =>
      prevPosts.map(p =>
        p.id === postId ? { ...p, content: editContent.trim() } : p
      )
    );

    // Update cache immediately
    if (postCache.isCacheAvailable()) {
      await postCache.updateCachedPost(postId, { content: editContent.trim() });
    }

    try {
      if (isOnline) {
        const response = await postsAPI.updatePost(postId, { content: editContent.trim() });
        setPosts(prevPosts =>
          prevPosts.map(p =>
            p.id === postId ? { ...p, content: response.post.content } : p
          )
        );
        
        if (postCache.isCacheAvailable()) {
          await postCache.updateCachedPost(postId, { content: response.post.content });
        }
        
        setEditingPostId(null);
        setEditContent('');
        toast.success('Post updated successfully!');
      } else {
        // Queue for later if offline
        await postCache.addPendingAction({
          type: 'update',
          postId,
          data: { content: editContent.trim() },
          timestamp: Date.now(),
          retryCount: 0,
        });
        setEditingPostId(null);
        setEditContent('');
        toast.success('Update saved. Will sync when online.');
      }
    } catch (error) {
      // Rollback on error
      console.error('Failed to update post:', error);
      setPosts(originalPosts);
      
      if (postCache.isCacheAvailable()) {
        const originalPost = originalPosts.find(p => p.id === postId);
        if (originalPost) {
          await postCache.updateCachedPost(postId, originalPost);
        }
      }
      
      toast.error('Failed to update post. Please try again.');
    }
  };

  const toggleComments = (postId: number) => {
    if (showComments[postId]) {
      // Just hide comments
      setShowComments(prev => ({ ...prev, [postId]: false }));
    } else {
      // Load and show comments
      loadComments(postId);
    }
  };

  const handleSharePost = async (post: ValidPost) => {
    const shareUrl = `${window.location.origin}/post/${post.id}`;
    // Sanitize content by removing any potentially harmful characters and limiting length
    const sanitizedContent = post.content
      .replace(/[<>]/g, '') // Remove angle brackets
      .substring(0, 100)
      .trim();
    const userName = `${post.user.first_name} ${post.user.last_name}`;
    const shareText = `Check out this post by ${userName}: ${sanitizedContent}${post.content.length > 100 ? '...' : ''}`;

    // Check if Web Share API is supported (mainly mobile devices)
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Post by ${userName}`,
          text: shareText,
          url: shareUrl,
        });
        toast.success('Post shared successfully!');
      } catch (error: unknown) {
        // User cancelled the share or error occurred
        const shareError = error as { name?: string };
        if (shareError.name !== 'AbortError') {
          console.error('Error sharing:', error);
          // Fallback to clipboard
          copyToClipboard(shareUrl);
        }
      }
    } else {
      // Fallback to clipboard for desktop browsers
      copyToClipboard(shareUrl);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Link copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      // Final fallback - create a temporary input element
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        toast.success('Link copied to clipboard!');
      } catch {
        toast.error('Failed to copy link. Please try again.');
      } finally {
        // Ensure cleanup happens regardless of success or failure
        try {
          if (textArea.parentNode) {
            document.body.removeChild(textArea);
          }
        } catch (cleanupError) {
          console.error('Error removing textarea element:', cleanupError);
        }
      }
    }
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
      {/* Connection Status Indicator */}
      {!isOnline && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-center space-x-2">
          <WifiIcon className="w-5 h-5 text-yellow-600" />
          <div className="flex-1">
            <p className="text-sm font-medium text-yellow-800">You're offline</p>
            <p className="text-xs text-yellow-600">Changes will be synced when connection is restored</p>
          </div>
        </div>
      )}
      
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
              <button
                onClick={() => navigate(`/user/${post.user.id}`)}
                className="flex-shrink-0 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
              >
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center hover:scale-105 transition-transform cursor-pointer">
                  <span className="text-white font-semibold text-sm">
                    {post.user.first_name[0]}{post.user.last_name[0]}
                  </span>
                </div>
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => navigate(`/user/${post.user.id}`)}
                    className="text-sm font-semibold text-gray-900 truncate hover:text-blue-600 transition-colors"
                  >
                    {post.user.first_name} {post.user.last_name}
                  </button>
                  <span className="text-sm text-gray-500">·</span>
                  <span className="text-sm text-gray-500">
                    {formatTimeAgo(post.created_at)}
                  </span>
                </div>
                <button
                  onClick={() => navigate(`/user/${post.user.id}`)}
                  className="text-xs text-blue-600 font-medium truncate hover:text-blue-700 transition-colors"
                >
                  @{post.user.username || post.user.email.split('@')[0]}
                </button>
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
                {post.video_url && (
                  <div className="mt-3 rounded-lg overflow-hidden border border-gray-200 bg-black">
                    <video
                      src={post.video_url}
                      controls
                      className="w-full h-auto max-h-96"
                      preload="metadata"
                    >
                      Your browser does not support the video tag.
                    </video>
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

              <button 
                onClick={() => handleSharePost(post)}
                className="flex items-center space-x-2 flex-1 justify-center py-2 px-4 rounded-lg hover:bg-gray-100 transition-colors text-gray-600"
              >
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
                  <div className="flex-1">
                    <div className="flex space-x-2 relative">
                      <input
                        type="text"
                        value={commentText[post.id] || ''}
                        onChange={(e) => setCommentText(prev => ({ ...prev, [post.id]: e.target.value }))}
                        placeholder="Write a comment..."
                        className="flex-1 px-3 py-2 bg-white border border-gray-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onKeyPress={(e) => e.key === 'Enter' && handleComment(post.id)}
                      />
                      <button
                        onClick={() => toggleEmojiPicker(post.id)}
                        className="emoji-picker-button p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                        title="Add emoji"
                      >
                        <FaceSmileIcon className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleComment(post.id)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-full text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={!commentText[post.id]?.trim()}
                      >
                        Post
                      </button>
                    </div>
                    
                    {/* Emoji Picker */}
                    {showEmojiPicker[post.id] && (
                      <div className="emoji-picker-container absolute z-50 mt-2">
                        <EmojiPicker
                          onEmojiClick={(emojiData) => handleEmojiClick(post.id, emojiData)}
                          width={300}
                          height={400}
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Loading Comments */}
              {loadingComments[post.id] && (
                <div className="flex justify-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                </div>
              )}

              {/* Comments List */}
              {!loadingComments[post.id] && comments[post.id] && (() => {
                const validComments = comments[post.id].filter(hasValidCommentUser);
                return (
                  <div className="space-y-3">
                    {validComments.length === 0 ? (
                      <p className="text-center text-gray-500 text-sm py-4">
                        No comments yet. Be the first to comment!
                      </p>
                    ) : (
                      validComments.map((comment) => (
                        <div key={comment.id} className="flex space-x-3">
                          <button
                            onClick={() => navigate(`/user/${comment.user.id}`)}
                            className="flex-shrink-0 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
                          >
                            <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center hover:scale-105 transition-transform cursor-pointer">
                              <span className="text-white font-semibold text-xs">
                                {comment.user.first_name?.[0] || '?'}{comment.user.last_name?.[0] || '?'}
                              </span>
                            </div>
                          </button>
                          <div className="flex-1">
                            <div className="bg-white rounded-2xl px-3 py-2">
                              <div className="flex items-start justify-between">
                                <button
                                  onClick={() => navigate(`/user/${comment.user.id}`)}
                                  className="text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors"
                                >
                                  {comment.user.first_name || ''} {comment.user.last_name || ''}
                                </button>
                                {user && comment.user.id === user.id && (
                                  <button
                                    onClick={() => handleDeleteComment(post.id, comment.id)}
                                    className="text-red-600 hover:text-red-700 text-xs"
                                    title="Delete comment"
                                  >
                                    Delete
                                  </button>
                                )}
                              </div>
                              <p className="text-sm text-gray-700">{comment.content}</p>
                            </div>
                            <div className="flex items-center space-x-4 mt-1 ml-3">
                              <span className="text-xs text-gray-400">
                                {formatTimeAgo(comment.created_at)}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                );
              })()}
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