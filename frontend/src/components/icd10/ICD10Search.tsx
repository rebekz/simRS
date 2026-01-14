"use client";

/**
 * ICD-10 Code Search Component for STORY-012
 *
 * Provides real-time search functionality for ICD-10 codes with:
 * - Full-text search on Indonesian and English descriptions
 * - Chapter and severity filtering
 * - Common codes filter
 * - User favorites integration
 * - Usage-based ranking
 */

import { useState, useCallback, useEffect } from "react";
import { Search, Star, Filter, Clock, TrendingUp } from "lucide-react";

// Types
interface ICD10Code {
  id: number;
  code: string;
  code_full: string;
  chapter: string;
  block: string;
  description_indonesian: string;
  description_english?: string;
  severity?: string;
  is_common: boolean;
  usage_count: number;
}

interface ICD10Chapter {
  code: string;
  chapter: string;
  description: string;
}

interface ICD10SearchProps {
  onSelectCode: (code: ICD10Code) => void;
  selectedCodeId?: number;
  disabled?: boolean;
  placeholder?: string;
}

export function ICD10Search({
  onSelectCode,
  selectedCodeId,
  disabled = false,
  placeholder = "Cari kode ICD-10...",
}: ICD10SearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ICD10Code[]>([]);
  const [chapters, setChapters] = useState<ICD10Chapter[]>([]);
  const [total, setTotal] = useState(0);
  const [searchTime, setSearchTime] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Filters
  const [chapterFilter, setChapterFilter] = useState<string>("");
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [commonOnly, setCommonOnly] = useState(false);

  // Debounced search
  const [debouncedQuery, setDebouncedQuery] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Fetch chapters on mount
  useEffect(() => {
    fetchChapters();
  }, []);

  // Search when query or filters change
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      searchCodes();
    } else {
      setResults([]);
      setTotal(0);
    }
  }, [debouncedQuery, chapterFilter, severityFilter, commonOnly]);

  const fetchChapters = async () => {
    try {
      const response = await fetch("/api/v1/icd10/chapters", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setChapters(data);
      }
    } catch (error) {
      console.error("Failed to fetch chapters:", error);
    }
  };

  const searchCodes = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        query: debouncedQuery,
        limit: "50",
      });

      if (chapterFilter) params.append("chapter_filter", chapterFilter);
      if (severityFilter) params.append("severity_filter", severityFilter);
      if (commonOnly) params.append("common_only", "true");

      const response = await fetch(`/api/v1/icd10/search?${params}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          query: debouncedQuery,
          limit: 50,
          chapter_filter: chapterFilter || undefined,
          severity_filter: severityFilter || undefined,
          common_only: commonOnly,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data.results);
        setTotal(data.total);
        setSearchTime(data.search_time_ms);
      }
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case "mild":
        return "bg-green-100 text-green-800";
      case "moderate":
        return "bg-yellow-100 text-yellow-800";
      case "severe":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={disabled}
          placeholder={placeholder}
          className="block w-full pl-10 pr-12 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
        >
          <Filter className="h-5 w-5" />
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-gray-50 p-4 rounded-md space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* Chapter Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Chapter
              </label>
              <select
                value={chapterFilter}
                onChange={(e) => setChapterFilter(e.target.value)}
                className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">All Chapters</option>
                {chapters.map((ch) => (
                  <option key={ch.code} value={ch.code}>
                    {ch.code} - {ch.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Severity Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Severity
              </label>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">All Severities</option>
                <option value="mild">Mild</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
            </div>

            {/* Common Only */}
            <div className="flex items-end">
              <label className="inline-flex items-center">
                <input
                  type="checkbox"
                  checked={commonOnly}
                  onChange={(e) => setCommonOnly(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
                <span className="ml-2 text-sm text-gray-700">Common codes only</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Search Stats */}
      {debouncedQuery.length >= 2 && (
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            {total} result{total !== 1 ? "s" : ""} found
          </span>
          {searchTime > 0 && (
            <span className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              {searchTime.toFixed(2)}ms
            </span>
          )}
        </div>
      )}

      {/* Results */}
      <div className="border border-gray-300 rounded-md divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">Loading...</div>
        ) : results.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            {debouncedQuery.length >= 2
              ? "No codes found. Try a different search term."
              : "Enter at least 2 characters to search."}
          </div>
        ) : (
          results.map((code) => (
            <button
              key={code.id}
              onClick={() => {
                onSelectCode(code);
                setQuery("");
              }}
              disabled={disabled}
              className={`w-full text-left px-4 py-3 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed ${
                selectedCodeId === code.id ? "bg-blue-50" : ""
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-sm font-semibold text-blue-600">
                      {code.code_full}
                    </span>
                    {code.is_common && (
                      <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    )}
                  </div>
                  <p className="text-sm text-gray-900 mt-1">
                    {code.description_indonesian}
                  </p>
                  {code.description_english && (
                    <p className="text-xs text-gray-500 mt-0.5 italic">
                      {code.description_english}
                    </p>
                  )}
                </div>
                <div className="flex flex-col items-end space-y-1">
                  {code.severity && (
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(
                        code.severity
                      )}`}
                    >
                      {code.severity}
                    </span>
                  )}
                  <span className="flex items-center text-xs text-gray-500">
                    <TrendingUp className="h-3 w-3 mr-0.5" />
                    {code.usage_count}
                  </span>
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
