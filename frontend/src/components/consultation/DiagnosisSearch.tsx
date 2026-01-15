"use client";

/**
 * WEB-S-4.3: ICD-10 Diagnosis Search for Consultation Workspace
 *
 * Key Features:
 * - Autocomplete search with <2 second response (debounced 300ms)
 * - Keyboard shortcut (Ctrl+K/Cmd+K) to focus search
 * - Favorites/frequently used diagnoses (quick chips)
 * - Recently used diagnoses (quick chips)
 * - Selected diagnosis chips with remove button
 * - Primary vs secondary diagnosis designation
 */

import { useState, useCallback, useEffect, useRef } from "react";
import { Search, Star, Clock, X, ChevronRight, RotateCcw } from "lucide-react";

// ============================================================================
// TYPES
// ============================================================================

export interface Diagnosis {
  code: string;
  name: string;
  isPrimary?: boolean;
}

export interface DiagnosisSearchResult {
  code: string;
  name: string;
  isFrequent?: boolean;
  category?: string;
}

export interface DiagnosisSearchProps {
  onSelectDiagnosis?: (diagnosis: Diagnosis) => void;
  onRemoveDiagnosis?: (code: string) => void;
  onSetPrimary?: (code: string) => void;
  selectedDiagnoses?: Diagnosis[];
  favorites?: DiagnosisSearchResult[];
  recentDiagnoses?: DiagnosisSearchResult[];
  disabled?: boolean;
  placeholder?: string;
  maxSelections?: number;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const MOCK_FAVORITES: DiagnosisSearchResult[] = [
  { code: "J00", name: "Nasofaringitis akut (Common cold)", isFrequent: true, category: "INF" },
  { code: "I10", name: "Hipertensi esensial (primer)", isFrequent: true, category: "CIR" },
  { code: "E11", name: "Diabetes mellitus tipe 2", isFrequent: true, category: "END" },
  { code: "J01", name: "Sinusitis akut", isFrequent: true, category: "INF" },
  { code: "J02", name: "Faringitis akut", isFrequent: true, category: "INF" },
  { code: "J03", name: "Tonsilitis akut", isFrequent: true, category: "INF" },
  { code: "J06", name: "Infeksi saluran pernapasan atas", isFrequent: true, category: "INF" },
  { code: "I50", name: "Gagal jantung", isFrequent: true, category: "CIR" },
  { code: "A01", name: "Tifoid dan paratifoid", isFrequent: true, category: "INF" },
  { code: "R50", name: "Demam", isFrequent: true, category: "GEN" },
];

const MOCK_RECENT: DiagnosisSearchResult[] = [
  { code: "J18", name: "Pneumonia", category: "INF" },
  { code: "I11", name: "Penyakit jantung hipertensi", category: "CIR" },
  { code: "K59", name: "Konstipasi", category: "DIG" },
];

const MOCK_DATABASE: DiagnosisSearchResult[] = [
  ...MOCK_FAVORITES,
  ...MOCK_RECENT,
  { code: "A02", name: "Infeksi Salmonella lainnya", category: "INF" },
  { code: "A03", name: "Shigellosis", category: "INF" },
  { code: "A04", name: "Infeksi bakteri intestium lainnya", category: "INF" },
  { code: "A05", name: "Keracunan makanan bakteri lainnya", category: "INF" },
  { code: "A06", name: "Amebiasis", category: "INF" },
  { code: "A07", name: "Penyakit diare lainnya", category: "INF" },
  { code: "A08", name: "Infeksi intestinus virus", category: "INF" },
  { code: "A09", name: "Gastroenteritis dan kolitis", category: "INF" },
  { code: "B01", name: "Varicella", category: "INF" },
  { code: "B02", name: "Herpes zoster", category: "INF" },
  { code: "C00", name: "Tumor ganas bibir", category: " NEO" },
  { code: "C01", name: "Tumor ganas lidah", category: "NEO" },
  { code: "D50", name: "Anemia defisiensi besi", category: "BLD" },
  { code: "E10", name: "Diabetes mellitus tipe 1", category: "END" },
  { code: "F00", name: "Demensia Alzheimer", category: "NER" },
  { code: "F01", name: "Demensia vaskular", category: "NER" },
  { code: "F32", name: "Episode depresif", category: "NER" },
  { code: "G01", name: "Meningitis bakteri", category: "NER" },
  { code: "H10", name: "Konjungtivitis", category: "EYE" },
  { code: "I20", name: "Angina pectoris", category: "CIR" },
  { code: "I21", name: "Infark miokard akut", category: "CIR" },
  { code: "I25", name: "Penyakit jantung iskemik kronis", category: "CIR" },
  { code: "J04", name: "Laringitis dan trakeitis akut", category: "INF" },
  { code: "J05", name: "Obstruksi saluran napas atas", category: "INF" },
  { code: "J09", name: "Influenza virus diidentifikasi", category: "INF" },
  { code: "J10", name: "Influenza virus tidak diidentifikasi", category: "INF" },
  { code: "J11", name: "Influenza virus tidak diidentifikasi", category: "INF" },
  { code: "J12", name: "Pneumonia virus", category: "INF" },
  { code: "J13", name: "Pneumonia Streptokokus", category: "INF" },
  { code: "J14", name: "Pneumonia Haemophilus", category: "INF" },
  { code: "J15", name: "Pneumonia bakteri lainnya", category: "INF" },
  { code: "J40", name: "Bronkitis akut", category: "INF" },
  { code: "K21", name: "Gastroesophageal reflux", category: "DIG" },
  { code: "K25", name: "Ulkus lambung", category: "DIG" },
  { code: "K26", name: "Ulkus duodenum", category: "DIG" },
  { code: "K35", name: "Apendisitis akut", category: "DIG" },
  { code: "M00", name: "Artritis piogen bakteri", category: "MSK" },
  { code: "M01", name: "Infeksi langsung artritis", category: "MSK" },
  { code: "M05", name: "Artritis reumatoid seropositif", category: "MSK" },
  { code: "M06", name: "Artritis reumatoid lainnya", category: "MSK" },
  { code: "M10", name: "Gout", category: "MSK" },
  { code: "M54", name: "Nyeri punggung", category: "MSK" },
  { code: "N18", name: "Gagal ginjal kronis", category: "URI" },
  { code: "N20", name: "Batu ginjal", category: "URI" },
  { code: "O01", name: "Kehamilan ektopik", category: "OBG" },
  { code: "O03", name: "Keguguran spontan", category: "OBG" },
  { code: "O10", name: "Hipertensi gestasional", category: "OBG" },
  { code: "R05", name: "Batuk", category: "GEN" },
  { code: "R06", name: "Gangguan pernapasan", category: "GEN" },
  { code: "R07", name: "Nyeri tenggorokan dan dada", category: "GEN" },
  { code: "S01", name: "Luka terbuka kepala", category: "INJ" },
  { code: "S02", name: "Fraktur tulang tengkorak", category: "INJ" },
  { code: "T36", name: "Keracunan antibiotik sistemik", category: "POI" },
  { code: "U07", name: "COVID-19", category: "INF" },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function fuzzyMatch(query: string, text: string): boolean {
  const queryLower = query.toLowerCase();
  const textLower = text.toLowerCase();

  // Exact match
  if (textLower.includes(queryLower)) {
    return true;
  }

  // Fuzzy match - check if all characters appear in order
  let queryIndex = 0;
  for (const char of textLower) {
    if (queryIndex < queryLower.length && char === queryLower[queryIndex]) {
      queryIndex++;
    }
  }
  return queryIndex === queryLower.length;
}

// ============================================================================
// COMPONENTS
// ============================================================================

/**
 * Diagnosis Chip Component - displays selected diagnosis with remove and primary toggle
 */
function DiagnosisChip({
  diagnosis,
  onRemove,
  onTogglePrimary,
  canRemove = true,
}: {
  diagnosis: Diagnosis;
  onRemove?: () => void;
  onTogglePrimary?: () => void;
  canRemove?: boolean;
}) {
  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${
        diagnosis.isPrimary
          ? "bg-blue-50 border-blue-300"
          : "bg-gray-50 border-gray-200"
      }`}
    >
      {/* Primary Radio */}
      <button
        type="button"
        onClick={onTogglePrimary}
        className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
          diagnosis.isPrimary
            ? "bg-blue-600 border-blue-600"
            : "border-gray-300 hover:border-blue-400"
        }`}
        aria-label="Set as primary diagnosis"
      >
        {diagnosis.isPrimary && (
          <div className="w-1.5 h-1.5 bg-white rounded-full" />
        )}
      </button>

      {/* Code */}
      <span className="font-mono text-sm font-semibold text-blue-600">
        {diagnosis.code}
      </span>

      {/* Name */}
      <span className="text-sm text-gray-700 max-w-xs truncate">
        {diagnosis.name}
      </span>

      {/* Remove Button */}
      {canRemove && onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-1 text-gray-400 hover:text-red-600 transition-colors"
          aria-label={`Remove ${diagnosis.code}`}
        >
          <X className="w-4 h-4" />
        </button>
      )}

      {/* Primary Badge */}
      {diagnosis.isPrimary && (
        <span className="text-xs font-medium text-blue-600">Utama</span>
      )}
    </div>
  );
}

/**
 * Quick Chip Component - for favorites and recent diagnoses
 */
function QuickChip({
  diagnosis,
  onClick,
  variant = "favorite",
}: {
  diagnosis: DiagnosisSearchResult;
  onClick: () => void;
  variant?: "favorite" | "recent";
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={variant === "favorite" && !diagnosis.isFrequent}
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
        diagnosis.isFrequent
          ? "bg-amber-50 border-amber-200 text-amber-800 hover:bg-amber-100"
          : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
      }`}
    >
      {variant === "favorite" && <Star className="w-3 h-3 fill-current" />}
      {variant === "recent" && <Clock className="w-3 h-3" />}
      <span className="font-mono text-xs">{diagnosis.code}</span>
      <ChevronRight className="w-3 h-3" />
      <span className="max-w-[200px] truncate">{diagnosis.name}</span>
    </button>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function DiagnosisSearch({
  onSelectDiagnosis,
  onRemoveDiagnosis,
  onSetPrimary,
  selectedDiagnoses = [],
  favorites = MOCK_FAVORITES,
  recentDiagnoses = MOCK_RECENT,
  disabled = false,
  placeholder = "Cari diagnosa ICD-10... (Ctrl+K)",
  maxSelections = 10,
}: DiagnosisSearchProps) {
  // Search state
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<DiagnosisSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Internal state
  const [internalSelected, setInternalSelected] = useState<Diagnosis[]>(selectedDiagnoses);

  // Sync with external state
  useEffect(() => {
    setInternalSelected(selectedDiagnoses);
  }, [selectedDiagnoses]);

  // Refs
  const searchInputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const searchStartTimeRef = useRef<number>(0);

  // Determine which state/props to use
  const diagnoses = selectedDiagnoses.length > 0 ? selectedDiagnoses : internalSelected;

  // ============================================================================
  // KEYBOARD SHORTCUT (Ctrl+K / Cmd+K)
  // ============================================================================

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }

      // Close results on Escape
      if (e.key === "Escape" && showResults) {
        setShowResults(false);
        searchInputRef.current?.blur();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [showResults]);

  // ============================================================================
  // SEARCH FUNCTIONALITY (Debounced)
  // ============================================================================

  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.length >= 2) {
        performSearch(query);
      } else {
        setResults([]);
        setShowResults(false);
      }
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [query]);

  const performSearch = useCallback((searchQuery: string) => {
    searchStartTimeRef.current = Date.now();
    setIsSearching(true);

    // Simulate API delay
    setTimeout(() => {
      const filtered = MOCK_DATABASE.filter((item) => fuzzyMatch(searchQuery, item.name) || fuzzyMatch(searchQuery, item.code));
      const searchTime = Date.now() - searchStartTimeRef.current;

      // Log search time for monitoring
      if (searchTime > 2000) {
        console.warn(`ICD-10 search took ${searchTime}ms - exceeds 2s target`);
      }

      setResults(filtered.slice(0, 10)); // Limit to 10 results
      setShowResults(true);
      setIsSearching(false);
    }, 100); // Simulate 100ms network delay
  }, []);

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleSelectDiagnosis = useCallback(
    (result: DiagnosisSearchResult) => {
      const newDiagnosis: Diagnosis = {
        code: result.code,
        name: result.name,
        isPrimary: diagnoses.length === 0, // First diagnosis is primary by default
      };

      // Check max selections
      if (diagnoses.length >= maxSelections) {
        alert(`Maksimal ${maxSelections} diagnosa`);
        return;
      }

      // Check for duplicates
      if (diagnoses.some((d) => d.code === result.code)) {
        return;
      }

      if (onSelectDiagnosis) {
        onSelectDiagnosis(newDiagnosis);
      } else {
        setInternalSelected([...diagnoses, newDiagnosis]);
      }

      // Clear search
      setQuery("");
      setShowResults(false);
    },
    [diagnoses, maxSelections, onSelectDiagnosis]
  );

  const handleRemoveDiagnosis = useCallback(
    (code: string) => {
      const updated = diagnoses.filter((d) => d.code !== code);

      // If removing primary, set first remaining as primary
      if (updated.length > 0 && !updated.some((d) => d.isPrimary)) {
        updated[0].isPrimary = true;
      }

      if (onRemoveDiagnosis) {
        onRemoveDiagnosis(code);
      } else {
        setInternalSelected(updated);
      }
    },
    [diagnoses, onRemoveDiagnosis]
  );

  const handleTogglePrimary = useCallback(
    (code: string) => {
      const updated = diagnoses.map((d) => ({
        ...d,
        isPrimary: d.code === code,
      }));

      if (onSetPrimary) {
        onSetPrimary(code);
      } else {
        setInternalSelected(updated);
      }
    },
    [diagnoses, onSetPrimary]
  );

  const handleClearSearch = useCallback(() => {
    setQuery("");
    setShowResults(false);
    searchInputRef.current?.focus();
  }, []);

  // ============================================================================
  // RENDER
  // ============================================================================

  const hasReachedMax = diagnoses.length >= maxSelections;

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          ref={searchInputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length >= 2 && setShowResults(true)}
          disabled={disabled || hasReachedMax}
          placeholder={hasReachedMax ? `Maksimal ${maxSelections} diagnosa` : placeholder}
          className={`block w-full pl-10 pr-10 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors ${
            disabled || hasReachedMax
              ? "bg-gray-100 border-gray-300 text-gray-500 cursor-not-allowed"
              : "bg-white border-gray-300 text-gray-900"
          }`}
        />
        {query && (
          <button
            type="button"
            onClick={handleClearSearch}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Quick Selection - Favorites */}
      {favorites.length > 0 && !query && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <Star className="w-4 h-4 text-amber-500 fill-current" />
            <span>Sering Digunakan</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {favorites.map((diagnosis) => (
              <QuickChip
                key={`fav-${diagnosis.code}`}
                diagnosis={diagnosis}
                variant="favorite"
                onClick={() => handleSelectDiagnosis(diagnosis)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Quick Selection - Recent */}
      {recentDiagnoses.length > 0 && !query && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <Clock className="w-4 h-4 text-blue-500" />
            <span>Baru Saja Digunakan</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentDiagnoses.map((diagnosis) => (
              <QuickChip
                key={`rec-${diagnosis.code}`}
                diagnosis={diagnosis}
                variant="recent"
                onClick={() => handleSelectDiagnosis(diagnosis)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Search Results Dropdown */}
      {showResults && query.length >= 2 && (
        <div
          ref={resultsRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-80 overflow-y-auto"
        >
          {isSearching ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mb-2" />
              <p className="text-sm">Mencari diagnosa...</p>
            </div>
          ) : results.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <Search className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p className="text-sm font-medium">Tidak ada hasil</p>
              <p className="text-xs text-gray-400 mt-1">
                Coba kata kunci lain atau kode ICD-10
              </p>
            </div>
          ) : (
            results.map((result) => (
              <button
                key={result.code}
                type="button"
                onClick={() => handleSelectDiagnosis(result)}
                className="w-full text-left px-4 py-3 hover:bg-blue-50 focus:outline-none focus:bg-blue-50 transition-colors border-b border-gray-100 last:border-0"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-bold text-blue-600">
                        {result.code}
                      </span>
                      {result.isFrequent && (
                        <Star className="w-3.5 h-3.5 text-amber-500 fill-current flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-sm text-gray-900 mt-0.5 line-clamp-2">
                      {result.name}
                    </p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />
                </div>
              </button>
            ))
          )}
        </div>
      )}

      {/* Selected Diagnoses */}
      {diagnoses.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">
              Diagnosa Terpilih ({diagnoses.length}/{maxSelections})
            </h3>
            {diagnoses.length > 1 && (
              <button
                type="button"
                onClick={() => {
                  // Reset all and set first as primary
                  const reset = [diagnoses[0]];
                  if (onSetPrimary) {
                    onSetPrimary(diagnoses[0].code);
                  }
                  setInternalSelected(reset);
                }}
                className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" />
                Reset
              </button>
            )}
          </div>

          <div className="flex flex-wrap gap-2">
            {diagnoses.map((diagnosis) => (
              <DiagnosisChip
                key={diagnosis.code}
                diagnosis={diagnosis}
                onRemove={() => handleRemoveDiagnosis(diagnosis.code)}
                onTogglePrimary={() => handleTogglePrimary(diagnosis.code)}
                canRemove={diagnoses.length > 1} // Always keep at least one
              />
            ))}
          </div>

          {/* Primary Selection Hint */}
          {diagnoses.length > 1 && (
            <p className="text-xs text-gray-500">
              <span className="font-medium">Klik lingkaran</span> untuk menandai diagnosa utama
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default DiagnosisSearch;
