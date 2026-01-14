'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Search, Keyboard } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  className?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Search patients, records...',
  onSearch,
  className,
}) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      setIsOpen(true);
    }
    if (e.key === 'Escape') {
      setIsOpen(false);
    }
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && onSearch) {
      onSearch(query.trim());
    }
  };

  return (
    <div className={cn('topbar-search', className)}>
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="form-input pl-10 pr-12"
          onFocus={() => setIsOpen(true)}
        />
        <Search
          size={18}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          strokeWidth={2}
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
          <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-500 bg-gray-100 border border-gray-300 rounded">
            <Keyboard size={10} />
            <span>⌘K</span>
          </kbd>
        </div>
      </form>

      {isOpen && (
        <div
          className="fixed inset-0 z-50"
          onClick={() => setIsOpen(false)}
        >
          <div className="fixed inset-0 bg-black/20" />
          <div className="fixed left-1/2 top-1/4 -translate-x-1/2 w-full max-w-2xl">
            <div className="card shadow-2xl">
              <div className="card-body p-4">
                <form onSubmit={handleSubmit}>
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={placeholder}
                    className="form-input pl-10 text-lg"
                    autoFocus
                    autoComplete="off"
                  />
                </form>
                <div className="mt-4 text-sm text-gray-500">
                  Press <kbd className="px-1.5 py-0.5 bg-gray-100 rounded">Enter</kbd> to search,
                  <kbd className="px-1.5 py-0.5 bg-gray-100 rounded ml-1">Esc</kbd> to close
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
