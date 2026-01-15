"use client";

import { useState, useEffect } from "react";

interface ICD10Code {
  id: number;
  code: string;
  code_full: string;
  description_indonesian: string;
  description_english?: string;
  chapter: string;
  is_common: boolean;
}

interface ICD10SelectorProps {
  onSelect: (code: ICD10Code) => void;
  onClose: () => void;
  currentCodeId?: number | null;
}

export function ICD10Selector({ onSelect, onClose, currentCodeId }: ICD10SelectorProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<ICD10Code[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFavorites, setShowFavorites] = useState(false);
  const [favorites, setFavorites] = useState<ICD10Code[]>([]);

  useEffect(() => {
    if (showFavorites) {
      fetchFavorites();
    }
  }, [showFavorites]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery.length >= 2) {
        searchCodes();
      } else {
        setResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const searchCodes = async () => {
    const token = localStorage.getItem("staff_access_token");
    setLoading(true);

    try {
      const response = await fetch("/api/v1/icd10/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: searchQuery,
          limit: 20,
          common_only: false,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
      }
    } catch (error) {
      console.error("Failed to search ICD-10 codes:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFavorites = async () => {
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch("/api/v1/icd10/favorites?limit=50", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setFavorites(data.favorites || []);
      }
    } catch (error) {
      console.error("Failed to fetch favorites:", error);
    }
  };

  const addToFavorites = async (codeId: number) => {
    const token = localStorage.getItem("staff_access_token");

    try {
      await fetch("/api/v1/icd10/favorites", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          icd10_code_id: codeId,
        }),
      });

      // Refresh favorites
      fetchFavorites();
    } catch (error) {
      console.error("Failed to add favorite:", error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Select ICD-10 Diagnosis Code</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div className="flex space-x-4">
            <button
              onClick={() => setShowFavorites(false)}
              className={`px-4 py-2 text-sm font-medium rounded-lg ${
                !showFavorites
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Search
            </button>
            <button
              onClick={() => setShowFavorites(true)}
              className={`px-4 py-2 text-sm font-medium rounded-lg ${
                showFavorites
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Favorites ({favorites.length})
            </button>
          </div>
        </div>

        {/* Search */}
        {!showFavorites && (
          <div className="p-6 border-b border-gray-200">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by code or description (e.g., 'diabetes', 'J18', 'hypertension')..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              autoFocus
            />
            <p className="text-xs text-gray-500 mt-2">
              Search Indonesian ICD-10 codes by diagnosis name or code
            </p>
          </div>
        )}

        {/* Results */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : showFavorites ? (
            // Favorites
            <div className="space-y-2">
              {favorites.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No favorites yet. Search and add codes to your favorites.</p>
              ) : (
                favorites.map((code) => (
                  <div
                    key={code.id}
                    onClick={() => onSelect(code)}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-sm bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                            {code.code}
                          </span>
                          <span className="text-sm text-gray-600">
                            {code.chapter}
                          </span>
                        </div>
                        <p className="text-gray-900 mt-1">{code.description_indonesian}</p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // Could add to favorites management
                        }}
                        className="text-yellow-500 hover:text-yellow-600 ml-2"
                      >
                        ⭐
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          ) : (
            // Search Results
            <div className="space-y-2">
              {searchQuery.length < 2 ? (
                <p className="text-gray-500 text-center py-8">Enter at least 2 characters to search</p>
              ) : results.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No results found for "{searchQuery}"</p>
              ) : (
                results.map((code) => (
                  <div
                    key={code.id}
                    onClick={() => onSelect(code)}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-sm bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                            {code.code}
                          </span>
                          <span className="text-xs text-gray-600">
                            {code.chapter}
                          </span>
                          {code.is_common && (
                            <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">
                              Common
                            </span>
                          )}
                        </div>
                        <p className="text-gray-900 mt-1">{code.description_indonesian}</p>
                        {code.description_english && (
                          <p className="text-sm text-gray-600 mt-1 italic">{code.description_english}</p>
                        )}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          addToFavorites(code.id);
                        }}
                        className="text-gray-300 hover:text-yellow-500 ml-2"
                        title="Add to favorites"
                      >
                        ☆
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
