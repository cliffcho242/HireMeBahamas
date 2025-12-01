import { useState, useCallback, useMemo } from 'react';
import { Job } from '../types/job';
import {
  smartSearch,
  JobSearchResult,
  generateSearchSuggestions,
  detectCategories,
  BAHAMAS_LOCATIONS
} from '../utils/searchAlgorithm';

interface SearchFilters {
  category?: string;
  location?: string;
  minRelevance?: number;
}

interface UseSearchResult {
  /** Current search query */
  query: string;
  /** Set the search query */
  setQuery: (query: string) => void;
  /** Current search filters */
  filters: SearchFilters;
  /** Set search filters */
  setFilters: (filters: SearchFilters) => void;
  /** Filtered results based on query and filters */
  results: JobSearchResult[];
  /** Whether search is active (query is not empty) */
  isSearching: boolean;
  /** Search suggestions based on current query */
  suggestions: string[];
  /** Detected categories from query */
  detectedCategories: Array<{ category: string; confidence: number; icon: string }>;
  /** Detected location from query */
  detectedLocation: string;
  /** Perform search with query and optional filters */
  search: (query: string, filters?: SearchFilters) => void;
  /** Clear search and reset to original data */
  clearSearch: () => void;
  /** Recent searches (persisted in localStorage) */
  recentSearches: string[];
  /** Add a search to recent searches */
  addToRecent: (query: string) => void;
  /** Clear recent searches */
  clearRecentSearches: () => void;
}

/** Default relevance score for unfiltered results */
const DEFAULT_RELEVANCE_SCORE = 100;

/**
 * Detect location from a search query string
 */
function detectLocationFromQuery(searchQuery: string): string {
  const queryLower = searchQuery.toLowerCase();
  for (const location of BAHAMAS_LOCATIONS) {
    if (queryLower.includes(location.toLowerCase())) {
      return location;
    }
  }
  return '';
}

/**
 * useSearch - A comprehensive, reusable search hook
 *
 * Features:
 * - Smart search with fuzzy matching
 * - Category detection
 * - Location detection
 * - Search suggestions
 * - Recent searches (persisted)
 * - Relevance scoring
 *
 * @example
 * ```tsx
 * const { query, setQuery, results, search, suggestions } = useSearch(jobs);
 *
 * // In your component:
 * <input value={query} onChange={(e) => setQuery(e.target.value)} />
 * <button onClick={() => search(query)}>Search</button>
 * {suggestions.map(s => <div onClick={() => search(s)}>{s}</div>)}
 * {results.map(job => <JobCard job={job} score={job.relevanceScore} />)}
 * ```
 */
export function useSearch(data: Job[]): UseSearchResult {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});
  const [results, setResults] = useState<JobSearchResult[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem('recentSearches');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // Compute suggestions based on query
  const suggestions = useMemo(() => {
    if (query.length < 2) return [];
    return generateSearchSuggestions(query, 8);
  }, [query]);

  // Detect categories from query
  const detectedCategories = useMemo(() => {
    if (query.length < 2) return [];
    return detectCategories(query).slice(0, 3);
  }, [query]);

  // Detect location from query
  const detectedLocation = useMemo(() => {
    return detectLocationFromQuery(query);
  }, [query]);

  // Add to recent searches (defined early to be available for search)
  const addToRecent = useCallback((searchQuery: string) => {
    const trimmed = searchQuery.trim();
    if (!trimmed) return;

    setRecentSearches(prev => {
      const updated = [trimmed, ...prev.filter(s => s !== trimmed)].slice(0, 5);
      try {
        localStorage.setItem('recentSearches', JSON.stringify(updated));
      } catch {
        // Ignore storage errors
      }
      return updated;
    });
  }, []);

  // Clear recent searches
  const clearRecentSearches = useCallback(() => {
    setRecentSearches([]);
    try {
      localStorage.removeItem('recentSearches');
    } catch {
      // Ignore storage errors
    }
  }, []);

  // Search function
  const search = useCallback((searchQuery: string, searchFilters?: SearchFilters) => {
    const mergedFilters = { ...filters, ...searchFilters };

    // Detect location if not provided
    if (!mergedFilters.location) {
      mergedFilters.location = detectLocationFromQuery(searchQuery);
    }

    // Detect category if not provided
    if (!mergedFilters.category) {
      const detected = detectCategories(searchQuery);
      if (detected.length > 0) {
        mergedFilters.category = detected[0].category;
      }
    }

    const searchResults = smartSearch(data, searchQuery, mergedFilters);
    setResults(searchResults);
    setQuery(searchQuery);
    setFilters(mergedFilters);

    // Add to recent searches
    if (searchQuery.trim()) {
      addToRecent(searchQuery);
    }
  }, [data, filters, addToRecent]);

  // Clear search
  const clearSearch = useCallback(() => {
    setQuery('');
    setFilters({});
    setResults(data.map(job => ({
      ...job,
      relevanceScore: DEFAULT_RELEVANCE_SCORE,
      matchedFields: []
    })));
  }, [data]);

  return {
    query,
    setQuery,
    filters,
    setFilters,
    results: results.length > 0 || query ? results : data.map(job => ({
      ...job,
      relevanceScore: DEFAULT_RELEVANCE_SCORE,
      matchedFields: []
    })),
    isSearching: query.length > 0,
    suggestions,
    detectedCategories,
    detectedLocation,
    search,
    clearSearch,
    recentSearches,
    addToRecent,
    clearRecentSearches
  };
}

export default useSearch;
