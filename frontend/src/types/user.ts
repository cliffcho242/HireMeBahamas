export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name?: string;
  username?: string;
  user_type: 'freelancer' | 'client' | 'admin' | 'employer' | 'recruiter';
  phone?: string;
  location?: string;
  bio?: string;
  skills?: string;
  experience?: string;
  education?: string;
  occupation?: string; // User's job title or occupation
  company_name?: string; // Company name for employers/clients
  avatar_url?: string;
  profileImage?: string;
  profile_picture?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}