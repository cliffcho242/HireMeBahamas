/**
 * GraphQL queries and mutations for HireMeBahamas.
 * 
 * These replace the existing REST API calls with GraphQL equivalents,
 * enabling efficient data fetching with Relay-style pagination.
 */
import { gql } from '@apollo/client';

// Fragment for post author data (reusable across queries)
export const POST_AUTHOR_FRAGMENT = gql`
  fragment PostAuthor on PostAuthorType {
    id
    firstName
    lastName
    username
    avatarUrl
    occupation
  }
`;

// Fragment for post data
export const POST_FRAGMENT = gql`
  ${POST_AUTHOR_FRAGMENT}
  fragment PostData on PostType {
    id
    content
    imageUrl
    videoUrl
    postType
    relatedJobId
    createdAt
    updatedAt
    likesCount
    commentsCount
    isLiked
    author {
      ...PostAuthor
    }
  }
`;

// Fragment for user data
export const USER_FRAGMENT = gql`
  fragment UserData on UserType {
    id
    email
    firstName
    lastName
    username
    phone
    location
    occupation
    companyName
    bio
    skills
    experience
    education
    avatarUrl
    isAvailableForHire
    role
    createdAt
    followersCount
    followingCount
  }
`;

// Fragment for message data
export const MESSAGE_FRAGMENT = gql`
  fragment MessageData on MessageType {
    id
    content
    senderId
    receiverId
    conversationId
    isRead
    createdAt
    sender {
      id
      firstName
      lastName
      avatarUrl
    }
  }
`;

// Fragment for notification data
export const NOTIFICATION_FRAGMENT = gql`
  fragment NotificationData on NotificationType {
    id
    notificationType
    content
    relatedId
    isRead
    createdAt
    actor {
      id
      firstName
      lastName
      avatarUrl
    }
  }
`;

// ============== QUERIES ==============

/**
 * Get the current authenticated user
 */
export const GET_ME = gql`
  ${USER_FRAGMENT}
  query GetMe {
    me {
      ...UserData
    }
  }
`;

/**
 * Get a user by ID
 */
export const GET_USER = gql`
  ${USER_FRAGMENT}
  query GetUser($id: Int!) {
    user(id: $id) {
      ...UserData
    }
  }
`;

/**
 * Get posts feed with Relay-style pagination
 * Replaces: GET /api/posts
 */
export const GET_POSTS = gql`
  ${POST_FRAGMENT}
  query GetPosts($first: Int, $after: String, $userId: Int) {
    posts(first: $first, after: $after, userId: $userId) {
      edges {
        cursor
        node {
          ...PostData
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
    }
  }
`;

/**
 * Get user posts
 * Replaces: GET /api/posts/user/{userId}
 */
export const GET_USER_POSTS = gql`
  ${POST_FRAGMENT}
  query GetUserPosts($userId: Int!, $first: Int, $after: String) {
    posts(first: $first, after: $after, userId: $userId) {
      edges {
        cursor
        node {
          ...PostData
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
    }
  }
`;

/**
 * Get post comments
 * Replaces: GET /api/posts/{postId}/comments
 */
export const GET_POST_COMMENTS = gql`
  query GetPostComments($postId: Int!) {
    postComments(postId: $postId) {
      id
      postId
      content
      createdAt
      updatedAt
      author {
        id
        firstName
        lastName
        username
        avatarUrl
      }
    }
  }
`;

/**
 * Get all conversations
 * Replaces: GET /api/messages/conversations
 */
export const GET_CONVERSATIONS = gql`
  ${MESSAGE_FRAGMENT}
  query GetConversations {
    conversations {
      id
      participant1Id
      participant2Id
      createdAt
      updatedAt
      participant1 {
        id
        firstName
        lastName
        avatarUrl
      }
      participant2 {
        id
        firstName
        lastName
        avatarUrl
      }
      lastMessage {
        ...MessageData
      }
      messages {
        ...MessageData
      }
    }
  }
`;

/**
 * Get messages for a conversation with pagination
 * Replaces: GET /api/messages/conversations/{conversationId}/messages
 */
export const GET_MESSAGES = gql`
  ${MESSAGE_FRAGMENT}
  query GetMessages($conversationId: Int!, $first: Int, $after: String) {
    messages(conversationId: $conversationId, first: $first, after: $after) {
      edges {
        cursor
        node {
          ...MessageData
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
    }
  }
`;

/**
 * Get notifications with pagination
 * Replaces: GET /api/notifications/list
 */
export const GET_NOTIFICATIONS = gql`
  ${NOTIFICATION_FRAGMENT}
  query GetNotifications($first: Int, $after: String, $unreadOnly: Boolean) {
    notifications(first: $first, after: $after, unreadOnly: $unreadOnly) {
      edges {
        cursor
        node {
          ...NotificationData
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
    }
  }
`;

/**
 * Get friends (mutual follows)
 */
export const GET_FRIENDS = gql`
  query GetFriends {
    friends {
      id
      firstName
      lastName
      username
      avatarUrl
      occupation
      isOnline
    }
  }
`;

// ============== MUTATIONS ==============

/**
 * Like/unlike a post
 * Replaces: POST /api/posts/{postId}/like
 */
export const LIKE_POST = gql`
  mutation LikePost($postId: Int!) {
    likePost(postId: $postId) {
      success
      action
      liked
      likesCount
    }
  }
`;

/**
 * Follow/unfollow a user
 * Replaces: POST /api/users/follow/{userId} & POST /api/users/unfollow/{userId}
 */
export const FOLLOW_USER = gql`
  mutation FollowUser($userId: Int!) {
    followUser(userId: $userId) {
      success
      action
      following
    }
  }
`;

/**
 * Send a message
 * Replaces: POST /api/messages/conversations/{conversationId}/messages
 */
export const SEND_MESSAGE = gql`
  ${MESSAGE_FRAGMENT}
  mutation SendMessage($conversationId: Int!, $content: String!) {
    sendMessage(conversationId: $conversationId, content: $content) {
      success
      message {
        ...MessageData
      }
    }
  }
`;

/**
 * Mark notification as read
 * Replaces: PUT /api/notifications/{notificationId}/read
 */
export const MARK_NOTIFICATION_READ = gql`
  mutation MarkNotificationRead($notificationId: Int!) {
    markNotificationRead(notificationId: $notificationId)
  }
`;

/**
 * Mark all notifications as read
 * Replaces: PUT /api/notifications/mark-all-read
 */
export const MARK_ALL_NOTIFICATIONS_READ = gql`
  mutation MarkAllNotificationsRead {
    markAllNotificationsRead
  }
`;
