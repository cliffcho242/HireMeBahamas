/**
 * Custom React hooks for GraphQL operations.
 * 
 * These hooks provide type-safe access to GraphQL queries and mutations
 * with built-in caching, pagination, and optimistic UI updates.
 */
import { useCallback, useMemo } from 'react';
import { 
  useQuery, 
  useMutation, 
  Reference,
} from '@apollo/client';
import { prefetchQuery } from './client';
import {
  GET_ME,
  GET_USER,
  GET_POSTS,
  GET_POST_COMMENTS,
  GET_CONVERSATIONS,
  GET_MESSAGES,
  GET_NOTIFICATIONS,
  GET_FRIENDS,
  LIKE_POST,
  FOLLOW_USER,
  SEND_MESSAGE,
  MARK_NOTIFICATION_READ,
  MARK_ALL_NOTIFICATIONS_READ,
  MESSAGE_FRAGMENT,
} from './queries';

// ============== TYPES ==============

export interface PostAuthor {
  id: number;
  firstName: string;
  lastName: string;
  username?: string;
  avatarUrl?: string;
  occupation?: string;
}

export interface Post {
  id: number;
  content: string;
  imageUrl?: string;
  videoUrl?: string;
  postType: string;
  relatedJobId?: number;
  createdAt: string;
  updatedAt?: string;
  likesCount: number;
  commentsCount: number;
  isLiked: boolean;
  author: PostAuthor;
}

export interface PostEdge {
  cursor: string;
  node: Post;
}

export interface PageInfo {
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  startCursor?: string;
  endCursor?: string;
}

export interface PostConnection {
  edges: PostEdge[];
  pageInfo: PageInfo;
  totalCount: number;
}

export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  username?: string;
  phone?: string;
  location?: string;
  occupation?: string;
  companyName?: string;
  bio?: string;
  skills?: string;
  experience?: string;
  education?: string;
  avatarUrl?: string;
  isAvailableForHire: boolean;
  role?: string;
  createdAt?: string;
  followersCount: number;
  followingCount: number;
}

export interface MessageSender {
  id: number;
  firstName: string;
  lastName: string;
  avatarUrl?: string;
}

export interface Message {
  id: number;
  content: string;
  senderId: number;
  receiverId: number;
  conversationId: number;
  isRead: boolean;
  createdAt: string;
  sender: MessageSender;
}

export interface ConversationParticipant {
  id: number;
  firstName: string;
  lastName: string;
  avatarUrl?: string;
}

export interface Conversation {
  id: number;
  participant1Id: number;
  participant2Id: number;
  createdAt: string;
  updatedAt?: string;
  participant1: ConversationParticipant;
  participant2: ConversationParticipant;
  messages: Message[];
  lastMessage?: Message;
}

export interface Notification {
  id: number;
  notificationType: string;
  content: string;
  relatedId?: number;
  isRead: boolean;
  createdAt: string;
  actor?: {
    id: number;
    firstName: string;
    lastName: string;
    avatarUrl?: string;
  };
}

export interface Friend {
  id: number;
  firstName: string;
  lastName: string;
  username?: string;
  avatarUrl?: string;
  occupation?: string;
  isOnline: boolean;
}

// ============== QUERY HOOKS ==============

/**
 * Hook to get the current authenticated user
 */
export const useMe = () => {
  const { data, loading, error, refetch } = useQuery<{ me: User | null }>(GET_ME, {
    fetchPolicy: 'cache-and-network',
  });

  return {
    user: data?.me || null,
    loading,
    error,
    refetch,
  };
};

/**
 * Hook to get a user by ID
 */
export const useUser = (userId: number) => {
  const { data, loading, error, refetch } = useQuery<{ user: User | null }>(
    GET_USER,
    {
      variables: { id: userId },
      skip: !userId,
      fetchPolicy: 'cache-and-network',
    }
  );

  return {
    user: data?.user || null,
    loading,
    error,
    refetch,
  };
};

/**
 * Hook to prefetch user data on hover
 */
export const usePrefetchUser = () => {
  const prefetchUserData = useCallback((userId: number) => {
    prefetchQuery(GET_USER, { id: userId });
  }, []);

  return prefetchUserData;
};

/**
 * Hook to get posts feed with pagination
 */
export const usePosts = (userId?: number, pageSize = 20) => {
  const { data, loading, error, fetchMore, refetch } = useQuery<{
    posts: PostConnection;
  }>(GET_POSTS, {
    variables: { first: pageSize, userId },
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  const loadMore = useCallback(() => {
    if (!data?.posts.pageInfo.hasNextPage) return;

    return fetchMore({
      variables: {
        first: pageSize,
        after: data.posts.pageInfo.endCursor,
        userId,
      },
    });
  }, [data, fetchMore, pageSize, userId]);

  const posts = useMemo(() => 
    data?.posts.edges.map(edge => edge.node) || [],
    [data]
  );

  return {
    posts,
    totalCount: data?.posts.totalCount || 0,
    hasMore: data?.posts.pageInfo.hasNextPage || false,
    loading,
    error,
    loadMore,
    refetch,
  };
};

/**
 * Hook to get conversations
 */
export const useConversations = () => {
  const { data, loading, error, refetch } = useQuery<{
    conversations: Conversation[];
  }>(GET_CONVERSATIONS, {
    fetchPolicy: 'cache-and-network',
  });

  return {
    conversations: data?.conversations || [],
    loading,
    error,
    refetch,
  };
};

/**
 * Hook to get messages for a conversation
 */
export const useMessages = (conversationId: number, pageSize = 50) => {
  const { data, loading, error, fetchMore, refetch } = useQuery<{
    messages: {
      edges: Array<{ cursor: string; node: Message }>;
      pageInfo: PageInfo;
      totalCount: number;
    };
  }>(GET_MESSAGES, {
    variables: { conversationId, first: pageSize },
    skip: !conversationId,
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  const loadMore = useCallback(() => {
    if (!data?.messages.pageInfo.hasNextPage) return;

    return fetchMore({
      variables: {
        conversationId,
        first: pageSize,
        after: data.messages.pageInfo.endCursor,
      },
    });
  }, [data, fetchMore, conversationId, pageSize]);

  const messages = useMemo(() =>
    data?.messages.edges.map(edge => edge.node) || [],
    [data]
  );

  return {
    messages,
    totalCount: data?.messages.totalCount || 0,
    hasMore: data?.messages.pageInfo.hasNextPage || false,
    loading,
    error,
    loadMore,
    refetch,
  };
};

/**
 * Hook to get notifications
 */
export const useNotifications = (unreadOnly = false, pageSize = 20) => {
  const { data, loading, error, fetchMore, refetch } = useQuery<{
    notifications: {
      edges: Array<{ cursor: string; node: Notification }>;
      pageInfo: PageInfo;
      totalCount: number;
    };
  }>(GET_NOTIFICATIONS, {
    variables: { first: pageSize, unreadOnly },
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  const loadMore = useCallback(() => {
    if (!data?.notifications.pageInfo.hasNextPage) return;

    return fetchMore({
      variables: {
        first: pageSize,
        after: data.notifications.pageInfo.endCursor,
        unreadOnly,
      },
    });
  }, [data, fetchMore, pageSize, unreadOnly]);

  const notifications = useMemo(() =>
    data?.notifications.edges.map(edge => edge.node) || [],
    [data]
  );

  return {
    notifications,
    totalCount: data?.notifications.totalCount || 0,
    hasMore: data?.notifications.pageInfo.hasNextPage || false,
    loading,
    error,
    loadMore,
    refetch,
  };
};

/**
 * Hook to get friends (mutual follows)
 */
export const useFriends = () => {
  const { data, loading, error, refetch } = useQuery<{
    friends: Friend[];
  }>(GET_FRIENDS, {
    fetchPolicy: 'cache-and-network',
  });

  return {
    friends: data?.friends || [],
    loading,
    error,
    refetch,
  };
};

/**
 * Hook to get post comments
 */
export const usePostComments = (postId: number) => {
  const { data, loading, error, refetch } = useQuery<{
    postComments: Array<{
      id: number;
      postId: number;
      content: string;
      createdAt: string;
      updatedAt?: string;
      author: PostAuthor;
    }>;
  }>(GET_POST_COMMENTS, {
    variables: { postId },
    skip: !postId,
    fetchPolicy: 'cache-and-network',
  });

  return {
    comments: data?.postComments || [],
    loading,
    error,
    refetch,
  };
};

// ============== MUTATION HOOKS ==============

/**
 * Hook for liking/unliking posts with optimistic UI
 */
export const useLikePost = () => {
  const [likePostMutation, { loading, error }] = useMutation<
    {
      likePost: {
        success: boolean;
        action: string;
        liked: boolean;
        likesCount: number;
      };
    },
    { postId: number }
  >(LIKE_POST, {
    optimisticResponse: () => ({
      likePost: {
        __typename: 'LikeResponse' as const,
        success: true,
        action: 'like',
        liked: true,
        likesCount: 0,
      },
    }),
    update: (cache, { data }, { variables }) => {
      if (!data?.likePost.success || !variables) return;

      // Update the post in cache
      cache.modify({
        id: cache.identify({ __typename: 'PostType', id: variables.postId }),
        fields: {
          isLiked: () => data.likePost.liked,
          likesCount: () => data.likePost.likesCount,
        },
      });
    },
  });

  const likePost = useCallback(
    async (postId: number) => {
      const result = await likePostMutation({ variables: { postId } });
      return result.data?.likePost;
    },
    [likePostMutation]
  );

  return { likePost, loading, error };
};

/**
 * Hook for following/unfollowing users with optimistic UI
 */
export const useFollowUser = () => {
  const [followUserMutation, { loading, error }] = useMutation<
    {
      followUser: {
        success: boolean;
        action: string;
        following: boolean;
      };
    },
    { userId: number }
  >(FOLLOW_USER, {
    optimisticResponse: () => ({
      followUser: {
        success: true,
        action: 'follow',
        following: true,
      },
    }),
  });

  const followUser = useCallback(
    async (userId: number) => {
      const result = await followUserMutation({ variables: { userId } });
      return result.data?.followUser;
    },
    [followUserMutation]
  );

  return { followUser, loading, error };
};

/**
 * Hook for sending messages with optimistic UI
 */
export const useSendMessage = () => {
  const [sendMessageMutation, { loading, error }] = useMutation<
    {
      sendMessage: {
        success: boolean;
        message: Message;
      };
    },
    { conversationId: number; content: string }
  >(SEND_MESSAGE, {
    update: (cache, { data }, { variables }) => {
      if (!data?.sendMessage.success || !variables) return;

      // Add new message to the messages cache for this conversation
      cache.modify({
        fields: {
          messages: (existing, { storeFieldName }) => {
            // Only update if it's for the same conversation
            if (!storeFieldName.includes(`conversationId:${variables.conversationId}`)) {
              return existing;
            }

            // Simply append the new message reference to the edges
            const newMessageRef = cache.writeFragment({
              data: data.sendMessage.message,
              fragment: MESSAGE_FRAGMENT,
            });

            return {
              ...existing,
              edges: [
                ...(existing?.edges || []),
                { cursor: '', node: newMessageRef },
              ],
            };
          },
        },
      });
    },
  });

  const sendMessage = useCallback(
    async (conversationId: number, content: string) => {
      const result = await sendMessageMutation({
        variables: { conversationId, content },
      });
      return result.data?.sendMessage;
    },
    [sendMessageMutation]
  );

  return { sendMessage, loading, error };
};

/**
 * Hook for marking notifications as read
 */
export const useMarkNotificationRead = () => {
  const [markReadMutation, { loading, error }] = useMutation<
    { markNotificationRead: boolean },
    { notificationId: number }
  >(MARK_NOTIFICATION_READ, {
    update: (cache, { data }, { variables }) => {
      if (!data?.markNotificationRead || !variables) return;

      cache.modify({
        id: cache.identify({
          __typename: 'NotificationType',
          id: variables.notificationId,
        }),
        fields: {
          isRead: () => true,
        },
      });
    },
  });

  const markRead = useCallback(
    async (notificationId: number) => {
      const result = await markReadMutation({ variables: { notificationId } });
      return result.data?.markNotificationRead;
    },
    [markReadMutation]
  );

  return { markRead, loading, error };
};

/**
 * Hook for marking all notifications as read
 */
export const useMarkAllNotificationsRead = () => {
  const [markAllReadMutation, { loading, error }] = useMutation<{
    markAllNotificationsRead: boolean;
  }>(MARK_ALL_NOTIFICATIONS_READ, {
    update: (cache) => {
      cache.modify({
        fields: {
          notifications: (existing) => {
            if (!existing?.edges) return existing;

            return {
              ...existing,
              edges: existing.edges.map((edge: { node: Reference }) => ({
                ...edge,
                node: {
                  ...edge.node,
                  isRead: true,
                },
              })),
            };
          },
        },
      });
    },
  });

  const markAllRead = useCallback(async () => {
    const result = await markAllReadMutation();
    return result.data?.markAllNotificationsRead;
  }, [markAllReadMutation]);

  return { markAllRead, loading, error };
};
