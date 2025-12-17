/**
 * Optimistic UI Updates for Instant Feedback
 * 
 * Implements Facebook-style instant updates:
 * - Update UI immediately on user action
 * - Revert on failure
 * - Background sync with server
 * - Conflict resolution
 */
import { queryClient } from '../config/reactQuery';

export interface OptimisticUpdate<T> {
  queryKey: any[];
  updater: (oldData: T) => T;
  onError?: (error: Error, rollback: () => void) => void;
}

/**
 * Perform an optimistic update
 */
export async function performOptimisticUpdate<T>(
  update: OptimisticUpdate<T>
): Promise<() => void> {
  const { queryKey, updater } = update;

  // Snapshot the previous value
  const previousData = queryClient.getQueryData<T>(queryKey);

  // Optimistically update to the new value
  if (previousData !== undefined) {
    queryClient.setQueryData<T>(queryKey, updater(previousData));
  }

  // Return a rollback function
  return () => {
    if (previousData !== undefined) {
      queryClient.setQueryData<T>(queryKey, previousData);
    }
  };
}

/**
 * Optimistic like/unlike post
 */
export async function optimisticLikePost(postId: number | string, isLiked: boolean) {
  const queryKey = ['posts', 'detail', postId];

  const rollback = await performOptimisticUpdate({
    queryKey,
    updater: (oldPost: any) => ({
      ...oldPost,
      likes_count: isLiked ? oldPost.likes_count + 1 : oldPost.likes_count - 1,
      is_liked: isLiked,
    }),
  });

  return rollback;
}

/**
 * Optimistic follow/unfollow user
 */
export async function optimisticFollowUser(userId: number | string, isFollowing: boolean) {
  const queryKey = ['users', 'detail', userId];

  const rollback = await performOptimisticUpdate({
    queryKey,
    updater: (oldUser: any) => ({
      ...oldUser,
      followers_count: isFollowing ? oldUser.followers_count + 1 : oldUser.followers_count - 1,
      is_following: isFollowing,
    }),
  });

  return rollback;
}

/**
 * Optimistic add comment
 */
export async function optimisticAddComment(
  postId: number | string,
  comment: any
) {
  const queryKey = ['posts', 'comments', postId];

  const rollback = await performOptimisticUpdate({
    queryKey,
    updater: (oldComments: any[]) => {
      // Add temporary ID and timestamp
      const newComment = {
        ...comment,
        id: `temp-${Date.now()}`,
        created_at: new Date().toISOString(),
        is_optimistic: true,
      };
      return [newComment, ...oldComments];
    },
  });

  // Also update post comment count
  const postQueryKey = ['posts', 'detail', postId];
  await performOptimisticUpdate({
    queryKey: postQueryKey,
    updater: (oldPost: any) => ({
      ...oldPost,
      comments_count: oldPost.comments_count + 1,
    }),
  });

  return rollback;
}

/**
 * Optimistic delete post
 */
export async function optimisticDeletePost(postId: number | string) {
  // Remove from feed
  const feedQueryKey = ['posts', 'feed'];
  
  const rollback = await performOptimisticUpdate({
    queryKey: feedQueryKey,
    updater: (oldFeed: any) => {
      if (!oldFeed || !oldFeed.pages) return oldFeed;
      
      return {
        ...oldFeed,
        pages: oldFeed.pages.map((page: any) => ({
          ...page,
          posts: page.posts.filter((post: any) => post.id !== postId),
        })),
      };
    },
  });

  return rollback;
}

/**
 * Optimistic update post
 */
export async function optimisticUpdatePost(
  postId: number | string,
  updates: Partial<any>
) {
  const queryKey = ['posts', 'detail', postId];

  const rollback = await performOptimisticUpdate({
    queryKey,
    updater: (oldPost: any) => ({
      ...oldPost,
      ...updates,
      updated_at: new Date().toISOString(),
    }),
  });

  return rollback;
}

/**
 * Optimistic update user profile
 */
export async function optimisticUpdateProfile(
  userId: number | string,
  updates: Partial<any>
) {
  const queryKey = ['users', 'detail', userId];

  const rollback = await performOptimisticUpdate({
    queryKey,
    updater: (oldProfile: any) => ({
      ...oldProfile,
      ...updates,
    }),
  });

  // Also update current user cache if it's the same user
  const meQueryKey = ['users', 'me'];
  const currentUser = queryClient.getQueryData(meQueryKey) as any;
  
  if (currentUser && currentUser.id === userId) {
    await performOptimisticUpdate({
      queryKey: meQueryKey,
      updater: (oldMe: any) => ({
        ...oldMe,
        ...updates,
      }),
    });
  }

  return rollback;
}

/**
 * Optimistic create post
 */
export async function optimisticCreatePost(post: any) {
  const feedQueryKey = ['posts', 'feed'];

  // Add temporary post to feed
  const rollback = await performOptimisticUpdate({
    queryKey: feedQueryKey,
    updater: (oldFeed: any) => {
      if (!oldFeed || !oldFeed.pages) return oldFeed;

      const tempPost = {
        ...post,
        id: `temp-${Date.now()}`,
        created_at: new Date().toISOString(),
        is_optimistic: true,
        likes_count: 0,
        comments_count: 0,
      };

      // Add to first page
      const pages = [...oldFeed.pages];
      if (pages[0]) {
        pages[0] = {
          ...pages[0],
          posts: [tempPost, ...pages[0].posts],
        };
      }

      return {
        ...oldFeed,
        pages,
      };
    },
  });

  return rollback;
}

/**
 * Mark message as read optimistically
 */
export async function optimisticMarkMessageRead(conversationId: number | string) {
  const queryKey = ['messages', 'conversation', conversationId];

  const rollback = await performOptimisticUpdate({
    queryKey,
    updater: (oldMessages: any[]) => {
      return oldMessages.map((message: any) => ({
        ...message,
        is_read: true,
      }));
    },
  });

  // Update unread count
  const unreadQueryKey = ['messages', 'unread'];
  await performOptimisticUpdate({
    queryKey: unreadQueryKey,
    updater: (oldCount: number) => Math.max(0, oldCount - 1),
  });

  return rollback;
}

/**
 * Optimistic notification clear
 */
export async function optimisticClearNotifications() {
  const queryKey = ['notifications', 'unread'];

  const rollback = await performOptimisticUpdate({
    queryKey,
    updater: () => 0,
  });

  return rollback;
}

/**
 * Generic mutation wrapper with optimistic updates
 */
export async function withOptimisticUpdate<TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  optimisticUpdate: OptimisticUpdate<any>,
  onSuccess?: (data: TData) => void
): Promise<TData> {
  // Perform optimistic update
  const rollback = await performOptimisticUpdate(optimisticUpdate);

  try {
    // Execute mutation
    const result = await mutationFn({} as TVariables);
    
    // Success - keep optimistic update
    onSuccess?.(result);
    
    return result;
  } catch (error) {
    // Failure - rollback optimistic update
    rollback();
    
    // Call error handler if provided
    optimisticUpdate.onError?.(error as Error, rollback);
    
    throw error;
  }
}

/**
 * Batch multiple optimistic updates
 */
export async function batchOptimisticUpdates(
  updates: OptimisticUpdate<any>[]
): Promise<() => void> {
  const rollbacks = await Promise.all(
    updates.map(update => performOptimisticUpdate(update))
  );

  // Return a function that rolls back all updates
  return () => {
    rollbacks.forEach(rollback => rollback());
  };
}

/**
 * Helper to check if data is optimistic (temporary)
 */
export function isOptimistic(data: any): boolean {
  return data?.is_optimistic === true || String(data?.id).startsWith('temp-');
}

/**
 * Replace optimistic data with real data from server
 */
export function replaceOptimisticData<T extends { id: any }>(
  items: T[],
  realItem: T
): T[] {
  return items.map(item => {
    // If this is the optimistic item, replace with real data
    if (isOptimistic(item)) {
      // Match by temporary ID or other criteria
      return realItem;
    }
    return item;
  });
}

export default {
  performOptimisticUpdate,
  optimisticLikePost,
  optimisticFollowUser,
  optimisticAddComment,
  optimisticDeletePost,
  optimisticUpdatePost,
  optimisticUpdateProfile,
  optimisticCreatePost,
  optimisticMarkMessageRead,
  optimisticClearNotifications,
  withOptimisticUpdate,
  batchOptimisticUpdates,
  isOptimistic,
  replaceOptimisticData,
};
