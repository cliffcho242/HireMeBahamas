// Common API error type
export interface ApiError {
  response?: {
    data?: {
      detail?: string;
      message?: string;
    };
    status?: number;
  };
  message?: string;
  code?: string;
  config?: {
    timeout?: number;
  };
}

// Google OAuth credential response
export interface GoogleCredentialResponse {
  credential?: string;
}

// Apple OAuth response  
export interface AppleSignInResponse {
  authorization?: {
    id_token?: string;
  };
}

// Socket message data type
export interface SocketMessageData {
  conversationId: string;
  content: string;
  receiverId: string;
}

// Vite import.meta environment
export interface ImportMetaEnv {
  VITE_API_BASE_URL?: string;
  VITE_API_URL?: string;
  VITE_SOCKET_URL?: string;
  VITE_GOOGLE_CLIENT_ID?: string;
  VITE_APPLE_CLIENT_ID?: string;
}

// Message type matching the backend API response (snake_case)
export interface BackendMessage {
  id: number;
  content: string;
  sender_id: number;
  conversation_id: number;
  created_at: string;
  is_read?: boolean;
  sender: {
    first_name: string;
    last_name: string;
  };
}

// Frontend-normalized Message type (camelCase)
export interface Message {
  id: string;
  content: string;
  senderId: string;
  receiverId: string;
  conversationId: string;
  isRead: boolean;
  createdAt: string;
}

export interface Conversation {
  id: string;
  participants: {
    id: string;
    firstName: string;
    lastName: string;
    profileImage?: string;
  }[];
  lastMessage?: Message;
  unreadCount: number;
  updatedAt: string;
}

export interface Review {
  id: string;
  rating: number;
  comment: string;
  reviewerId: string;
  revieweeId: string;
  jobId: string;
  reviewer: {
    id: string;
    firstName: string;
    lastName: string;
    profileImage?: string;
  };
  createdAt: string;
}

export interface PostUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  username?: string;
  occupation?: string;
  company_name?: string;
}

export interface Post {
  id: number;
  content: string;
  image_url?: string;
  video_url?: string;
  created_at: string;
  user?: PostUser;
  likes_count: number;
  comments_count: number;
  is_liked?: boolean;
}
