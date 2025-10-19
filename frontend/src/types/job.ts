export interface Job {
  id: number;
  title: string;
  company: string;
  description: string;
  requirements?: string;
  benefits?: string;
  category: string;
  job_type: 'full-time' | 'part-time' | 'contract' | 'temporary' | 'internship';
  location: string;
  salary_min?: number;
  salary_max?: number;
  budget?: number;
  budgetType?: 'hourly' | 'fixed';
  isRemote?: boolean;
  skills?: string[];
  employer_id: number;
  employer: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  client?: {
    id: number;
    first_name: string;
    last_name: string;
    lastName: string;
    profileImage?: string;
    rating?: number;
  };
  status: 'active' | 'inactive' | 'closed';
  applications: JobApplication[];
  created_at: string;
  createdAt?: string;
  updated_at: string;
}

export interface JobApplication {
  id: number;
  job_id: number;
  applicant_id: number;
  applicant: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  cover_letter?: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
}

export interface CreateJobData {
  title: string;
  company: string;
  description: string;
  requirements?: string;
  benefits?: string;
  category: string;
  job_type: 'full-time' | 'part-time' | 'contract' | 'temporary' | 'internship';
  location: string;
  salary_min?: number;
  salary_max?: number;
}