import { ChangeEvent, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MagnifyingGlassIcon,
  XMarkIcon,
  ClockIcon,
  FireIcon,
  SparklesIcon,
  MapPinIcon
} from '@heroicons/react/24/outline';
import {
  generateSearchSuggestions,
  detectCategories,
  POPULAR_SEARCHES,
  BAHAMAS_LOCATIONS
} from '../utils/searchAlgorithm';

interface SearchFilters {
  category?: string;
  location?: string;
  minRelevance?: number;
}

interface SmartSearchBarProps {
  onSearch: (query: string, filters?: SearchFilters) => void;
  placeholder?: string;
  showPopularSearches?: boolean;
  className?: string;
}

const SmartSearchBar = ({
  onSearch,
  placeholder = "Search for jobs, skills, or services (e.g., 'plumber in Nassau')...",
  showPopularSearches = true,
  className = ''
}): SmartSearchBarProps => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showSuggestionsOverride, setShowSuggestionsOverride] = useState(false);
  
  // Use lazy initialization for localStorage to avoid cascading renders
  const [recentSearches, setRecentSearches] = useState<string[]>(() => {
    const stored = localStorage.getItem('recentSearches');
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (e) {
        console.error('Error loading recent searches:', e);
        return [];
      }
    }
    return [];
  });
  
  const [isFocused, setIsFocused] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Compute suggestions and categories during render (derived state)
  const suggestions = searchQuery.length >= 2 
    ? generateSearchSuggestions(searchQuery, 8)
    : [];
    
  const detectedCategories = searchQuery.length >= 2
    ? detectCategories(searchQuery).slice(0, 3)
    : [];
    
  // Compute whether to show suggestions
  const showSuggestions = showSuggestionsOverride || (searchQuery.length >= 2 
    ? true 
    : (searchQuery.length === 0 && isFocused));

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestionsOverride(false);
        setIsFocused(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (query: string) => {
    if (!query.trim()) return;

    // Save to recent searches
    const updated = [query, ...recentSearches.filter(s => s !== query)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));

    // Detect location in query
    let detectedLocation = '';
    BAHAMAS_LOCATIONS.forEach(location => {
      if (query.toLowerCase().includes(location.toLowerCase())) {
        detectedLocation = location;
      }
    });

    // Detect category
    let detectedCategory = '';
    if (detectedCategories.length > 0) {
      detectedCategory = detectedCategories[0].category;
    }

    onSearch(query, {
      location: detectedLocation,
      category: detectedCategory
    });

    setShowSuggestionsOverride(false);
    setSearchQuery(query);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };



  const clearSearch = () => {
    setSearchQuery('');
    setShowSuggestionsOverride(false);
    onSearch('');
  };

  const selectSuggestion = (suggestion: string) => {
    setSearchQuery(suggestion);
    handleSearch(suggestion);
  };

  return (
    <div ref={searchRef} className={`relative ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={handleInputChange}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
          onFocus={() => {
            setIsFocused(true);
            setShowSuggestionsOverride(true);
          }}
          placeholder={placeholder}
          className="w-full pl-12 pr-12 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all text-gray-900 placeholder-gray-400"
        />
        {searchQuery && (
          <button
            onClick={clearSearch}
            aria-label="Clear search"
            title="Clear search"
            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Suggestions Dropdown */}
      <AnimatePresence>
        {showSuggestions && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden z-50 max-h-[500px] overflow-y-auto"
          >
            {/* Detected Categories */}
            {detectedCategories.length > 0 && (
              <div className="p-4 border-b border-gray-100">
                <div className="flex items-center gap-2 mb-3">
                  <SparklesIcon className="h-4 w-4 text-purple-500" />
                  <span className="text-xs font-semibold text-gray-500 uppercase">Smart Match</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {detectedCategories.map((cat, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => selectSuggestion(cat.category)}
                      className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-purple-50 to-blue-50 hover:from-purple-100 hover:to-blue-100 rounded-lg text-sm font-medium text-gray-700 transition-all"
                    >
                      <span className="text-lg">{cat.icon}</span>
                      <span>{cat.category}</span>
                      <span className="text-xs text-gray-500">
                        ({Math.round(cat.confidence * 100)}% match)
                      </span>
                    </motion.button>
                  ))}
                </div>
              </div>
            )}

            {/* Search Suggestions */}
            {suggestions.length > 0 && (
              <div className="p-2">
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase flex items-center gap-2">
                  <MagnifyingGlassIcon className="h-4 w-4" />
                  Suggestions
                </div>
                {suggestions.map((suggestion, index) => (
                  <motion.button
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                    onClick={() => selectSuggestion(suggestion)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 group"
                  >
                    <MagnifyingGlassIcon className="h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    <span className="text-gray-700 group-hover:text-gray-900 capitalize">
                      {suggestion}
                    </span>
                  </motion.button>
                ))}
              </div>
            )}

            {/* Recent Searches */}
            {recentSearches.length > 0 && searchQuery.length === 0 && (
              <div className="p-2 border-t border-gray-100">
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase flex items-center gap-2">
                  <ClockIcon className="h-4 w-4" />
                  Recent Searches
                </div>
                {recentSearches.map((search, index) => (
                  <motion.button
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                    onClick={() => selectSuggestion(search)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 group"
                  >
                    <ClockIcon className="h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    <span className="text-gray-700 group-hover:text-gray-900">
                      {search}
                    </span>
                  </motion.button>
                ))}
              </div>
            )}

            {/* Popular Searches */}
            {showPopularSearches && searchQuery.length === 0 && (
              <div className="p-2 border-t border-gray-100">
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase flex items-center gap-2">
                  <FireIcon className="h-4 w-4 text-orange-500" />
                  Popular Searches
                </div>
                <div className="grid grid-cols-2 gap-2 p-2">
                  {POPULAR_SEARCHES.slice(0, 6).map((popular, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => selectSuggestion(popular.text)}
                      className="flex items-center gap-2 px-3 py-2 bg-gray-50 hover:bg-blue-50 rounded-lg text-sm text-gray-700 hover:text-blue-600 transition-all group"
                    >
                      <span className="text-lg">{popular.icon}</span>
                      <span className="font-medium">{popular.text}</span>
                    </motion.button>
                  ))}
                </div>
              </div>
            )}

            {/* Location Quick Filters */}
            {searchQuery.length === 0 && (
              <div className="p-2 border-t border-gray-100">
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase flex items-center gap-2">
                  <MapPinIcon className="h-4 w-4 text-green-500" />
                  Popular Locations
                </div>
                <div className="flex flex-wrap gap-2 p-2">
                  {['Nassau', 'Freeport', 'Paradise Island', 'Grand Bahama'].map((location, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => selectSuggestion(`Jobs in ${location}`)}
                      className="px-3 py-1.5 bg-green-50 hover:bg-green-100 text-green-700 rounded-full text-xs font-medium transition-all"
                    >
                      📍 {location}
                    </motion.button>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SmartSearchBar;
