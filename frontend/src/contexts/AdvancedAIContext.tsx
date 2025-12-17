/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-refresh/only-export-components */
// AI Context uses dynamic types for AI responses - any types are intentional
import { ReactNode, createContext, useCallback, useContext, useEffect, useState } from 'react';
import axios from 'axios';

interface AdvancedAIContextType {
  // User Analysis
  analyzeUserProfile: (userData: any) => Promise<any>;
  getUserInsights: (userId: number) => Promise<any>;

  // Job Matching
  findJobMatches: (userProfile: any, jobs: any[]) => Promise<any[]>;
  getJobRecommendations: (userId: number) => Promise<any[]>;

  // Content Generation
  generateContent: (contentType: string, context: any) => Promise<string>;
  generateJobDescription: (jobData: any) => Promise<string>;
  generateCoverLetter: (userData: any, jobData: any) => Promise<string>;
  generateInterviewQuestions: (jobData: any) => Promise<string>;
  generateCareerAdvice: (userData: any) => Promise<string>;

  // Resume Analysis
  analyzeResume: (file: File) => Promise<any>;
  extractResumeData: (imageData: string) => Promise<any>;

  // Career Prediction
  predictCareerTrajectory: (userProfile: any) => Promise<any>;
  getCareerInsights: (userId: number) => Promise<any>;

  // Real-time Recommendations
  getRealTimeRecommendations: (userId: number, context?: any) => Promise<any[]>;

  // AI Chat
  sendChatMessage: (message: string, context?: any) => Promise<string>;
  getChatHistory: (userId: number) => Promise<any[]>;

  // Analytics & Feedback
  getAIAnalytics: () => Promise<any>;
  submitFeedback: (feedback: any) => Promise<void>;

  // System Status
  aiSystemHealth: any;
  isAIOnline: boolean;
  aiCapabilities: string[];
}

const AdvancedAIContext = createContext<AdvancedAIContextType | undefined>(undefined);

interface AdvancedAIProviderProps {
  children: ReactNode;
  apiBaseUrl?: string;
}

export const AdvancedAIProvider = ({
  children,
  apiBaseUrl = import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}/api/ai`
    : (typeof window !== 'undefined' ? `${window.location.origin}/api/ai` : '/api/ai')
}: AdvancedAIProviderProps) => {
  const [aiSystemHealth, setAISystemHealth] = useState<any>({});
  const [isAIOnline, setIsAIOnline] = useState(false);
  const [aiCapabilities, setAICapabilities] = useState<string[]>([]);

  const checkAISystemHealth = useCallback(async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/health`);
      setAISystemHealth(response.data);
      setIsAIOnline(response.data.status === 'healthy');
      setAICapabilities(response.data.capabilities || []);
    } catch (error) {
      console.error('AI system health check failed:', error);
      setIsAIOnline(false);
      setAICapabilities([]);
    }
  }, [apiBaseUrl]);

  // Initialize AI system health check - this is a subscription to external system state
  useEffect(() => {
    // Initial check and set up polling
    // Note: checkAISystemHealth is stable (wrapped in useCallback) and this is a valid
    // subscription pattern for polling external APIs
    checkAISystemHealth();
    
    // Set up polling interval for continuous health monitoring
    const interval = setInterval(checkAISystemHealth, 30000); // Check every 30 seconds
    
    return () => clearInterval(interval);
  }, [checkAISystemHealth]);

  // User Profile Analysis
  const analyzeUserProfile = useCallback(async (userData: any) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/analyze-profile`, {
        user_data: userData
      });
      return response.data;
    } catch (error) {
      console.error('User profile analysis failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  const getUserInsights = useCallback(async (userId: number) => {
    try {
      const response = await axios.get(`${apiBaseUrl}/user-insights/${userId}`);
      return response.data;
    } catch (error) {
      console.error('User insights fetch failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  // Job Matching
  const findJobMatches = useCallback(async (userProfile: any, jobs: any[]) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/job-matching`, {
        user_profile: userProfile,
        jobs: jobs
      });
      return response.data.matches || [];
    } catch (error) {
      console.error('Job matching failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  const getJobRecommendations = useCallback(async (userId: number) => {
    try {
      const response = await axios.get(`${apiBaseUrl}/job-recommendations/${userId}`);
      return response.data.recommendations || [];
    } catch (error) {
      console.error('Job recommendations fetch failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  // Content Generation
  const generateContent = useCallback(async (contentType: string, context: any) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/generate-content`, {
        content_type: contentType,
        context: context
      });
      return response.data.content || '';
    } catch (error) {
      console.error('Content generation failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  const generateJobDescription = useCallback(async (jobData: any) => {
    return generateContent('job_description', jobData);
  }, [generateContent]);

  const generateCoverLetter = useCallback(async (userData: any, jobData: any) => {
    const context = { userData, jobData };
    return generateContent('cover_letter', context);
  }, [generateContent]);

  const generateInterviewQuestions = useCallback(async (jobData: any) => {
    return generateContent('interview_questions', jobData);
  }, [generateContent]);

  const generateCareerAdvice = useCallback(async (userData: any) => {
    return generateContent('career_advice', userData);
  }, [generateContent]);

  // Resume Analysis
  const analyzeResume = useCallback(async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${apiBaseUrl}/analyze-resume`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data.analysis || {};
    } catch (error) {
      console.error('Resume analysis failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  const extractResumeData = useCallback(async (imageData: string) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/extract-resume-data`, {
        image_data: imageData
      });
      return response.data;
    } catch (error) {
      console.error('Resume data extraction failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  // Career Prediction
  const predictCareerTrajectory = useCallback(async (userProfile: any) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/career-prediction`, {
        user_profile: userProfile
      });
      return response.data.prediction || {};
    } catch (error) {
      console.error('Career prediction failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  const getCareerInsights = useCallback(async (userId: number) => {
    try {
      const response = await axios.get(`${apiBaseUrl}/career-insights/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Career insights fetch failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  // Real-time Recommendations
  const getRealTimeRecommendations = useCallback(async (userId: number, context?: any) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/recommendations`, {
        user_id: userId,
        context: context || {}
      });
      return response.data.recommendations || [];
    } catch (error) {
      console.error('Real-time recommendations failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  // AI Chat
  const sendChatMessage = useCallback(async (message: string, context?: any) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/chat`, {
        message: message,
        context: context || {}
      });
      return response.data.response || '';
    } catch (error) {
      console.error('AI chat failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  const getChatHistory = useCallback(async (userId: number) => {
    try {
      const response = await axios.get(`${apiBaseUrl}/chat-history/${userId}`);
      return response.data.history || [];
    } catch (error) {
      console.error('Chat history fetch failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  // Analytics & Feedback
  const getAIAnalytics = useCallback(async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/analytics`);
      return response.data.analytics || {};
    } catch (error) {
      console.error('AI analytics fetch failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  const submitFeedback = useCallback(async (feedback: any) => {
    try {
      await axios.post(`${apiBaseUrl}/feedback`, feedback);
    } catch (error) {
      console.error('Feedback submission failed:', error);
      throw error;
    }
  }, [apiBaseUrl]);

  const value: AdvancedAIContextType = {
    // User Analysis
    analyzeUserProfile,
    getUserInsights,

    // Job Matching
    findJobMatches,
    getJobRecommendations,

    // Content Generation
    generateContent,
    generateJobDescription,
    generateCoverLetter,
    generateInterviewQuestions,
    generateCareerAdvice,

    // Resume Analysis
    analyzeResume,
    extractResumeData,

    // Career Prediction
    predictCareerTrajectory,
    getCareerInsights,

    // Real-time Recommendations
    getRealTimeRecommendations,

    // AI Chat
    sendChatMessage,
    getChatHistory,

    // Analytics & Feedback
    getAIAnalytics,
    submitFeedback,

    // System Status
    aiSystemHealth,
    isAIOnline,
    aiCapabilities
  };

  return (
    <AdvancedAIContext.Provider value={value}>
      {children}
    </AdvancedAIContext.Provider>
  );
};

export const useAdvancedAI = () => {
  const context = useContext(AdvancedAIContext);
  if (!context) {
    throw new Error('useAdvancedAI must be used within AdvancedAIProvider');
  }
  return context;
};

// Custom hooks for specific AI features
export const useAIJobMatching = () => {
  const { findJobMatches, getJobRecommendations } = useAdvancedAI();
  return { findJobMatches, getJobRecommendations };
};

export const useAIContentGeneration = () => {
  const {
    generateContent,
    generateJobDescription,
    generateCoverLetter,
    generateInterviewQuestions,
    generateCareerAdvice
  } = useAdvancedAI();

  return {
    generateContent,
    generateJobDescription,
    generateCoverLetter,
    generateInterviewQuestions,
    generateCareerAdvice
  };
};

export const useAIResumeAnalysis = () => {
  const { analyzeResume, extractResumeData } = useAdvancedAI();
  return { analyzeResume, extractResumeData };
};

export const useAICareerPrediction = () => {
  const { predictCareerTrajectory, getCareerInsights } = useAdvancedAI();
  return { predictCareerTrajectory, getCareerInsights };
};

export const useAIChat = () => {
  const { sendChatMessage, getChatHistory } = useAdvancedAI();
  return { sendChatMessage, getChatHistory };
};

export const useAIRecommendations = () => {
  const { getRealTimeRecommendations } = useAdvancedAI();
  return { getRealTimeRecommendations };
};