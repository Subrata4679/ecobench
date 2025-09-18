import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { searchAPI, organizationsAPI } from '../services/api';
import {
  MagnifyingGlassIcon,
  DocumentTextIcon,
  SparklesIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Search = () => {
  const { showError } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchStats, setSearchStats] = useState(null);
  const [filters, setFilters] = useState({
    organization_id: '',
    year: '',
    report_type: '',
    limit: 20,
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [orgsResponse, statsResponse, suggestionsResponse] = await Promise.all([
        organizationsAPI.getAll(),
        searchAPI.getStats(),
        searchAPI.getSuggestions({ limit: 5 }),
      ]);
      setOrganizations(orgsResponse.data.items || []);
      setSearchStats(statsResponse.data);
      setSuggestions(suggestionsResponse.data.items || []);
    } catch (error) {
      console.error('Failed to load initial data:', error);
      showError('Failed to load search data');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      const searchParams = {
        query: searchQuery,
        ...filters,
      };
      
      // Remove empty filters
      Object.keys(searchParams).forEach(key => {
        if (searchParams[key] === '') {
          delete searchParams[key];
        }
      });

      const response = await searchAPI.search(searchParams);
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      showError('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion);
    // Trigger search with suggestion
    const event = { preventDefault: () => {} };
    handleSearch(event);
  };

  const highlightText = (text, query) => {
    if (!query || !text) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {part}
        </mark>
      ) : part
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Semantic Search</h1>
        <p className="mt-1 text-sm text-gray-500">
          Search through ESG reports and documents using AI-powered semantic search
        </p>
      </div>

      {/* Search Form */}
      <div className="card">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex space-x-4">
            <div className="flex-1 relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search for ESG metrics, sustainability practices, governance policies..."
                className="input pl-10 text-lg"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="btn-outline flex items-center"
            >
              <AdjustmentsHorizontalIcon className="h-5 w-5 mr-2" />
              Filters
            </button>
            <button
              type="submit"
              disabled={loading || !searchQuery.trim()}
              className="btn-primary px-8"
            >
              {loading ? <LoadingSpinner size="small" /> : 'Search'}
            </button>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t">
              <select
                className="input"
                value={filters.organization_id}
                onChange={(e) => setFilters({ ...filters, organization_id: e.target.value })}
              >
                <option value="">All Organizations</option>
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>
                    {org.name}
                  </option>
                ))}
              </select>
              <input
                type="number"
                placeholder="Year"
                className="input"
                value={filters.year}
                onChange={(e) => setFilters({ ...filters, year: e.target.value })}
              />
              <select
                className="input"
                value={filters.report_type}
                onChange={(e) => setFilters({ ...filters, report_type: e.target.value })}
              >
                <option value="">All Report Types</option>
                <option value="sustainability">Sustainability</option>
                <option value="annual">Annual</option>
                <option value="esg">ESG</option>
                <option value="environmental">Environmental</option>
                <option value="social">Social</option>
                <option value="governance">Governance</option>
              </select>
              <select
                className="input"
                value={filters.limit}
                onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) })}
              >
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
                <option value={50}>50 results</option>
                <option value={100}>100 results</option>
              </select>
            </div>
          )}
        </form>
      </div>

      {/* Search Stats */}
      {searchStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="stat-card">
            <div className="stat-card-content">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="stat-card-icon text-primary-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Documents
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {searchStats.total_documents?.toLocaleString() || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-content">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <SparklesIcon className="stat-card-icon text-success-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Embeddings
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {searchStats.total_embeddings?.toLocaleString() || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-content">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <MagnifyingGlassIcon className="stat-card-icon text-warning-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Avg Similarity
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {searchStats.avg_similarity ? `${(searchStats.avg_similarity * 100).toFixed(1)}%` : 'N/A'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-content">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="stat-card-icon text-purple-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Organizations
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {organizations.length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && searchResults.length === 0 && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Popular Searches</h3>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Search Results ({searchResults.length})
            </h3>
            <p className="text-sm text-gray-500">
              Showing results for "{searchQuery}"
            </p>
          </div>
          
          {searchResults.map((result, index) => (
            <div key={index} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-2">
                    <h4 className="text-lg font-medium text-gray-900">
                      {result.report_title || 'Document'}
                    </h4>
                    <span className="badge-primary text-xs">
                      {(result.similarity * 100).toFixed(1)}% match
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-500 mb-2">
                    {result.organization_name} • {result.year} • Page {result.page_number || 'N/A'}
                  </div>
                  
                  <div className="text-sm text-gray-700 mb-3 p-3 bg-gray-50 rounded-lg">
                    {highlightText(result.content, searchQuery)}
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Chunk {result.chunk_index + 1}</span>
                    <span>Similarity: {(result.similarity * 100).toFixed(2)}%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && searchQuery && searchResults.length === 0 && (
        <div className="text-center py-12">
          <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search terms or filters
          </p>
        </div>
      )}

      {/* Initial State */}
      {!searchQuery && (
        <div className="text-center py-12">
          <SparklesIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Semantic Search</h3>
          <p className="mt-1 text-sm text-gray-500">
            Enter your search query to find relevant information across all ESG reports
          </p>
          <div className="mt-6">
            <p className="text-xs text-gray-400 max-w-md mx-auto">
              Our AI-powered search understands context and meaning, not just keywords. 
              Try searching for concepts like "carbon emissions reduction strategies" or "employee diversity initiatives".
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;
