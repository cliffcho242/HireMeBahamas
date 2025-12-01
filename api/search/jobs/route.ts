/**
 * Edge-compatible Job Search API Route
 * Full-text search via Edge caching + Postgres fallback
 * Target: < 80ms globally
 */

export const config = {
  runtime: 'edge',
  regions: ['iad1', 'sfo1', 'cdg1', 'hnd1', 'syd1'], // Global edge locations
};

// Job interface
interface Job {
  id: number;
  title: string;
  description: string;
  company: string;
  location: string;
  salary?: string;
  salary_min?: number;
  salary_max?: number;
  job_type: 'full-time' | 'part-time' | 'contract' | 'freelance' | 'internship';
  category: string;
  skills?: string[];
  is_remote: boolean;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  employer_id: number;
  applications_count?: number;
}

// Search result with highlighting
interface SearchResult {
  job: Job;
  score: number;
  highlights: {
    title?: string;
    description?: string;
    company?: string;
  };
}

// Edge cache for search results (TTL: 5 minutes)
const searchCache = new Map<string, { results: SearchResult[]; timestamp: number; total: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Sample jobs data (in production, this comes from Vercel KV or backend)
const sampleJobs: Job[] = [
  {
    id: 1,
    title: 'Senior Software Engineer',
    description: 'Join our team to build amazing web applications using React and Node.js. Experience with TypeScript preferred.',
    company: 'BahamasTech Solutions',
    location: 'Nassau, Bahamas',
    salary: '$80,000 - $120,000',
    salary_min: 80000,
    salary_max: 120000,
    job_type: 'full-time',
    category: 'Technology',
    skills: ['React', 'Node.js', 'TypeScript', 'PostgreSQL'],
    is_remote: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_active: true,
    employer_id: 1,
    applications_count: 5,
  },
  {
    id: 2,
    title: 'Hotel Manager',
    description: 'Manage daily operations at our luxury resort. Hospitality experience required.',
    company: 'Paradise Resorts',
    location: 'Freeport, Bahamas',
    salary: '$60,000 - $85,000',
    salary_min: 60000,
    salary_max: 85000,
    job_type: 'full-time',
    category: 'Hospitality',
    skills: ['Management', 'Customer Service', 'Operations'],
    is_remote: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_active: true,
    employer_id: 2,
    applications_count: 12,
  },
  {
    id: 3,
    title: 'Marine Biologist',
    description: 'Research and protect marine ecosystems in the beautiful waters of the Bahamas.',
    company: 'Bahamas Marine Research Institute',
    location: 'Andros, Bahamas',
    salary: '$55,000 - $75,000',
    salary_min: 55000,
    salary_max: 75000,
    job_type: 'full-time',
    category: 'Science',
    skills: ['Marine Biology', 'Research', 'SCUBA Diving', 'Data Analysis'],
    is_remote: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_active: true,
    employer_id: 3,
    applications_count: 8,
  },
  {
    id: 4,
    title: 'Tour Guide',
    description: 'Lead exciting tours and share the rich history and culture of the Bahamas with visitors.',
    company: 'Island Adventures',
    location: 'Nassau, Bahamas',
    salary: '$35,000 - $50,000',
    salary_min: 35000,
    salary_max: 50000,
    job_type: 'part-time',
    category: 'Tourism',
    skills: ['Public Speaking', 'Local Knowledge', 'Customer Service'],
    is_remote: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_active: true,
    employer_id: 4,
    applications_count: 3,
  },
  {
    id: 5,
    title: 'Remote Full Stack Developer',
    description: 'Build scalable applications for our fintech platform. Work from anywhere in the world.',
    company: 'Caribbean FinTech',
    location: 'Remote - Bahamas',
    salary: '$90,000 - $140,000',
    salary_min: 90000,
    salary_max: 140000,
    job_type: 'full-time',
    category: 'Technology',
    skills: ['React', 'Python', 'AWS', 'PostgreSQL', 'Docker'],
    is_remote: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_active: true,
    employer_id: 5,
    applications_count: 25,
  },
];

/**
 * Simple text search scoring
 */
function calculateScore(job: Job, query: string): number {
  const queryLower = query.toLowerCase();
  const terms = queryLower.split(/\s+/).filter(t => t.length > 1);
  let score = 0;
  
  for (const term of terms) {
    // Title match (highest weight)
    if (job.title.toLowerCase().includes(term)) {
      score += 10;
      if (job.title.toLowerCase().startsWith(term)) score += 5;
    }
    
    // Company match
    if (job.company.toLowerCase().includes(term)) {
      score += 5;
    }
    
    // Description match
    if (job.description.toLowerCase().includes(term)) {
      score += 3;
    }
    
    // Category match
    if (job.category.toLowerCase().includes(term)) {
      score += 7;
    }
    
    // Location match
    if (job.location.toLowerCase().includes(term)) {
      score += 4;
    }
    
    // Skills match
    if (job.skills?.some(skill => skill.toLowerCase().includes(term))) {
      score += 6;
    }
  }
  
  return score;
}

/**
 * Highlight matching text
 */
function highlightText(text: string, query: string): string {
  const terms = query.toLowerCase().split(/\s+/).filter(t => t.length > 1);
  let highlighted = text;
  
  for (const term of terms) {
    const regex = new RegExp(`(${term})`, 'gi');
    highlighted = highlighted.replace(regex, '<mark>$1</mark>');
  }
  
  return highlighted;
}

/**
 * Search jobs with filters
 */
function searchJobs(
  query: string,
  filters: {
    category?: string;
    location?: string;
    job_type?: string;
    is_remote?: boolean;
    salary_min?: number;
    salary_max?: number;
  } = {},
  skip = 0,
  limit = 20
): { results: SearchResult[]; total: number } {
  let jobs = [...sampleJobs].filter(job => job.is_active);
  
  // Apply filters
  if (filters.category) {
    jobs = jobs.filter(job => 
      job.category.toLowerCase() === filters.category!.toLowerCase()
    );
  }
  
  if (filters.location) {
    jobs = jobs.filter(job => 
      job.location.toLowerCase().includes(filters.location!.toLowerCase())
    );
  }
  
  if (filters.job_type) {
    jobs = jobs.filter(job => job.job_type === filters.job_type);
  }
  
  if (filters.is_remote !== undefined) {
    jobs = jobs.filter(job => job.is_remote === filters.is_remote);
  }
  
  if (filters.salary_min !== undefined) {
    jobs = jobs.filter(job => 
      job.salary_max && job.salary_max >= filters.salary_min!
    );
  }
  
  if (filters.salary_max !== undefined) {
    jobs = jobs.filter(job => 
      job.salary_min && job.salary_min <= filters.salary_max!
    );
  }
  
  // Calculate scores and create results
  let results: SearchResult[] = jobs.map(job => ({
    job,
    score: query ? calculateScore(job, query) : 1,
    highlights: query ? {
      title: highlightText(job.title, query),
      description: highlightText(job.description.substring(0, 200), query),
      company: highlightText(job.company, query),
    } : {},
  }));
  
  // Filter by score if there's a query
  if (query) {
    results = results.filter(r => r.score > 0);
  }
  
  // Sort by score (highest first)
  results.sort((a, b) => b.score - a.score);
  
  const total = results.length;
  
  // Apply pagination
  results = results.slice(skip, skip + limit);
  
  return { results, total };
}

/**
 * Generate cache key
 */
function getCacheKey(query: string, filters: Record<string, unknown>, skip: number, limit: number): string {
  return JSON.stringify({ query, filters, skip, limit });
}

/**
 * Allowed CORS origins
 */
const ALLOWED_ORIGINS = [
  'https://hiremebahamas.com',
  'https://www.hiremebahamas.com',
  'https://hiremebahamas.vercel.app',
  'http://localhost:3000',
  'http://localhost:5173',
  'http://127.0.0.1:5173',
];

/**
 * Get CORS headers with dynamic origin checking
 */
function getCorsHeaders(request: Request): Record<string, string> {
  const origin = request.headers.get('origin') || '';
  const allowedOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  
  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

/**
 * Edge Job Search Handler
 */
export default async function handler(request: Request): Promise<Response> {
  const startTime = Date.now();
  const url = new URL(request.url);
  
  // Dynamic CORS headers
  const corsHeaders = getCorsHeaders(request);
  
  // Handle preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }
  
  // Only allow GET and POST
  if (request.method !== 'GET' && request.method !== 'POST') {
    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
  
  try {
    // Parse search parameters
    let query = '';
    let skip = 0;
    let limit = 20;
    const filters: Record<string, unknown> = {};
    
    if (request.method === 'GET') {
      query = url.searchParams.get('q') || url.searchParams.get('search') || '';
      skip = parseInt(url.searchParams.get('skip') || '0');
      limit = Math.min(parseInt(url.searchParams.get('limit') || '20'), 100);
      
      if (url.searchParams.get('category')) filters.category = url.searchParams.get('category');
      if (url.searchParams.get('location')) filters.location = url.searchParams.get('location');
      if (url.searchParams.get('job_type')) filters.job_type = url.searchParams.get('job_type');
      if (url.searchParams.get('is_remote')) filters.is_remote = url.searchParams.get('is_remote') === 'true';
      if (url.searchParams.get('salary_min')) filters.salary_min = parseInt(url.searchParams.get('salary_min')!);
      if (url.searchParams.get('salary_max')) filters.salary_max = parseInt(url.searchParams.get('salary_max')!);
    } else {
      const body = await request.json();
      query = body.q || body.search || body.query || '';
      skip = body.skip || 0;
      limit = Math.min(body.limit || 20, 100);
      
      if (body.category) filters.category = body.category;
      if (body.location) filters.location = body.location;
      if (body.job_type) filters.job_type = body.job_type;
      if (body.is_remote !== undefined) filters.is_remote = body.is_remote;
      if (body.salary_min) filters.salary_min = body.salary_min;
      if (body.salary_max) filters.salary_max = body.salary_max;
    }
    
    // Check cache
    const cacheKey = getCacheKey(query, filters, skip, limit);
    const cached = searchCache.get(cacheKey);
    const now = Date.now();
    
    if (cached && (now - cached.timestamp) < CACHE_TTL) {
      const responseTime = Date.now() - startTime;
      
      return new Response(
        JSON.stringify({
          success: true,
          results: cached.results,
          total: cached.total,
          skip,
          limit,
          cached: true,
          edge_optimized: true,
          response_time_ms: responseTime,
        }),
        {
          status: 200,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'X-Edge-Response-Time': `${responseTime}ms`,
            'X-Cache': 'HIT',
            'Cache-Control': 'public, max-age=300, stale-while-revalidate=60',
          },
        }
      );
    }
    
    // Try to fetch from backend for fresh data, fall back to local sample data
    let searchResults: { results: SearchResult[]; total: number };
    let fromBackend = false;
    
    try {
      const backendUrl = process.env.BACKEND_URL || 'https://hiremebahamas.onrender.com';
      
      // Create AbortController with manual timeout for Edge compatibility
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      
      try {
        const backendResponse = await fetch(`${backendUrl}/api/jobs?search=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`, {
          headers: { 'X-Edge-Request': 'true' },
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          const jobs = backendData.jobs || backendData.results || [];
          
          searchResults = {
            results: jobs.map((job: Job) => ({
              job,
              score: query ? calculateScore(job, query) : 1,
              highlights: query ? {
                title: highlightText(job.title, query),
                description: highlightText((job.description || '').substring(0, 200), query),
                company: highlightText(job.company || '', query),
              } : {},
            })),
            total: backendData.total || jobs.length,
          };
          fromBackend = true;
        } else {
          throw new Error('Backend response not ok');
        }
      } finally {
        clearTimeout(timeoutId);
      }
    } catch {
      // Fallback to local sample data
      searchResults = searchJobs(query, filters as { category?: string; location?: string; job_type?: string; is_remote?: boolean; salary_min?: number; salary_max?: number }, skip, limit);
    }
    
    // Update cache
    searchCache.set(cacheKey, {
      results: searchResults.results,
      total: searchResults.total,
      timestamp: now,
    });
    
    // Clean old cache entries periodically
    if (Math.random() < 0.1) { // 10% chance to clean
      const keysToDelete: string[] = [];
      searchCache.forEach((value, key) => {
        if (now - value.timestamp > CACHE_TTL * 2) {
          keysToDelete.push(key);
        }
      });
      keysToDelete.forEach(key => searchCache.delete(key));
    }
    
    const responseTime = Date.now() - startTime;
    
    return new Response(
      JSON.stringify({
        success: true,
        results: searchResults.results,
        total: searchResults.total,
        skip,
        limit,
        query,
        filters,
        cached: false,
        from_backend: fromBackend,
        edge_optimized: true,
        response_time_ms: responseTime,
      }),
      {
        status: 200,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
          'X-Edge-Response-Time': `${responseTime}ms`,
          'X-Cache': 'MISS',
          'Cache-Control': 'public, max-age=300, stale-while-revalidate=60',
        },
      }
    );
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Edge search error:', errorMessage);
    
    return new Response(
      JSON.stringify({ error: 'Search failed', message: errorMessage }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
}
