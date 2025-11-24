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