"use client";

/**
 * WEB-S-4.5: Lab/Radiology Ordering for Consultation Workspace
 *
 * Key Features:
 * - Test catalog search and package selection (Lab + Radiology)
 * - Priority assignment (routine, urgent, STAT)
 * - Clinical indication (required for some tests)
 * - Insurance pre-authorization
 * - Order tracking (pending, in-progress, completed)
 * - Result viewing and attachment to encounter
 */

import { useState, useCallback, useEffect } from "react";
import {
  Search,
  TestTube2,
  Activity,
  Plus,
  X,
  Clock,
  CheckCircle,
  AlertCircle,
  FileText,
  Shield,
  Zap,
  User,
  Calendar,
  ChevronRight,
  Download,
  Paperclip,
} from "lucide-react";

// ============================================================================
// TYPES
// ============================================================================

export type TestType = "lab" | "radiology";

export interface TestItem {
  id: string;
  code: string;
  name: string;
  nameId: string;
  category: string;
  type: TestType;
  specimenType?: string;
  fastingRequired?: boolean;
  preparationInstructions?: string;
  tatHours?: number;
  price?: number;
  bpjsCode?: string;
  requiresPriorAuth?: boolean;
  requiresIndication?: boolean;
}

export interface OrderedTest {
  test: TestItem;
  priority: "routine" | "urgent" | "stat";
  clinicalIndication?: string;
  status: "pending" | "in-progress" | "completed" | "cancelled";
  orderId?: string;
  orderDate?: Date;
  estimatedCompletion?: Date;
  results?: TestResult[];
  priorAuthStatus?: "none" | "requested" | "approved" | "rejected";
  priorAuthNumber?: string;
}

export interface TestResult {
  testName: string;
  value: string;
  unit: string;
  referenceRange: string;
  isAbnormal: boolean;
  flag?: "high" | "low" | "critical";
  notes?: string;
  resultDate?: Date;
}

export interface TestOrderingProps {
  patientId: number;
  encounterId: number;
  patientDiagnoses?: string[];
  patientInsurance?: string;
  onOrderSubmit?: (order: OrderedTest[]) => void;
  onResultAttach?: (result: TestResult) => void;
  disabled?: boolean;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const MOCK_LAB_TESTS: TestItem[] = [
  {
    id: "lab-001",
    code: "CBC",
    name: "Complete Blood Count",
    nameId: "Hematologi Lengkap",
    category: "Hematologi",
    type: "lab",
    specimenType: "blood",
    fastingRequired: false,
    tatHours: 2,
    price: 150000,
    bpjsCode: "LAB-001",
    requiresIndication: true,
  },
  {
    id: "lab-002",
    code: "HBA1C",
    name: "Hemoglobin A1c",
    nameId: "HbA1c",
    category: "Kimia Klinis",
    type: "lab",
    specimenType: "blood",
    fastingRequired: false,
    tatHours: 4,
    price: 200000,
    bpjsCode: "LAB-002",
  },
  {
    id: "lab-003",
    code: "LIPID",
    name: "Lipid Profile",
    nameId: "Profil Lipid",
    category: "Kimia Klinis",
    type: "lab",
    specimenType: "blood",
    fastingRequired: true,
    preparationInstructions: "Puasa minimal 10-12 jam",
    tatHours: 4,
    price: 250000,
    bpjsCode: "LAB-003",
    requiresPriorAuth: true,
  },
  {
    id: "lab-004",
    code: "GLU",
    name: "Fasting Blood Glucose",
    nameId: "Gula Darah Puasa",
    category: "Kimia Klinis",
    type: "lab",
    specimenType: "blood",
    fastingRequired: true,
    preparationInstructions: "Puasa minimal 8 jam",
    tatHours: 1,
    price: 80000,
    bpjsCode: "LAB-004",
  },
  {
    id: "lab-005",
    code: "URINE",
    name: "Urinalysis",
    nameId: "Urinalisis Lengkap",
    category: "Urinalisis",
    type: "lab",
    specimenType: "urine",
    fastingRequired: false,
    tatHours: 2,
    price: 100000,
    bpjsCode: "LAB-005",
  },
  {
    id: "lab-006",
    code: "HBS",
    name: "Hepatitis B Surface Antigen",
    nameId: "Hepatitis B Surface Ag",
    category: "Imunologi",
    type: "lab",
    specimenType: "blood",
    fastingRequired: false,
    tatHours: 4,
    price: 180000,
    bpjsCode: "LAB-006",
  },
];

const MOCK_RADIOLOGY_TESTS: TestItem[] = [
  {
    id: "rad-001",
    code: "CXR",
    name: "Chest X-Ray",
    nameId: "Foto Thorax PA/AP",
    category: "X-Ray",
    type: "radiology",
    tatHours: 4,
    price: 250000,
    bpjsCode: "RAD-001",
    requiresIndication: true,
  },
  {
    id: "rad-002",
    code: "USG",
    name: "Abdominal Ultrasound",
    nameId: "USG Abdomen",
    category: "Ultrasound",
    type: "radiology",
    preparationInstructions: "Puasa minimal 6 jam",
    tatHours: 8,
    price: 450000,
    bpjsCode: "RAD-002",
    requiresPriorAuth: true,
  },
  {
    id: "rad-003",
    code: "CT",
    name: "CT Scan Head",
    nameId: "CT Scan Kepala",
    category: "CT Scan",
    type: "radiology",
    tatHours: 24,
    price: 1500000,
    requiresPriorAuth: true,
  },
  {
    id: "rad-004",
    code: "MRI",
    name: "MRI Brain",
    nameId: "MRI Otak",
    category: "MRI",
    type: "radiology",
    tatHours: 48,
    price: 3000000,
    requiresPriorAuth: true,
  },
  {
    id: "rad-005",
    code: "EXT",
    name: "X-Ray Extremity",
    nameId: "Foto Ekstremitas",
    category: "X-Ray",
    type: "radiology",
    tatHours: 2,
    price: 150000,
    bpjsCode: "RAD-005",
  },
];

const MOCK_RESULTS: TestResult[] = [
  {
    testName: "Hemoglobin",
    value: "14.2",
    unit: "g/dL",
    referenceRange: "13.5 - 17.5",
    isAbnormal: false,
  },
  {
    testName: "Leukocytes",
    value: "11.5",
    unit: "10^3/uL",
    referenceRange: "4.5 - 11.0",
    isAbnormal: true,
    flag: "high",
  },
  {
    testName: "Platelets",
    value: "250",
    unit: "10^3/uL",
    referenceRange: "150 - 400",
    isAbnormal: false,
  },
];

const ALL_TESTS = [...MOCK_LAB_TESTS, ...MOCK_RADIOLOGY_TESTS];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================++

function getTestIcon(type: TestType) {
  return type === "lab" ? TestTube2 : Activity;
}

function getStatusColor(status: OrderedTest["status"]) {
  switch (status) {
    case "pending":
      return "bg-yellow-100 text-yellow-800 border-yellow-300";
    case "in-progress":
      return "bg-blue-100 text-blue-800 border-blue-300";
    case "completed":
      return "bg-green-100 text-green-800 border-green-300";
    case "cancelled":
      return "bg-gray-100 text-gray-800 border-gray-300";
  }
}

function getPriorityColor(priority: OrderedTest["priority"]) {
  switch (priority) {
    case "routine":
      return "bg-gray-100 text-gray-800";
    case "urgent":
      return "bg-orange-100 text-orange-800";
    case "stat":
      return "bg-red-100 text-red-800";
  }
}

function getAuthStatusColor(status?: OrderedTest["priorAuthStatus"]) {
  switch (status) {
    case "approved":
      return "bg-green-100 text-green-800 border-green-300";
    case "rejected":
      return "bg-red-100 text-red-800 border-red-300";
    case "requested":
      return "bg-yellow-100 text-yellow-800 border-yellow-300";
    default:
      return "bg-gray-100 text-gray-800 border-gray-300";
  }
}

// ============================================================================
// COMPONENTS
// ============================================================================

interface TestCardProps {
  test: TestItem;
  onAdd: () => void;
  disabled?: boolean;
}

function TestCard({ test, onAdd, disabled }: TestCardProps) {
  const Icon = getTestIcon(test.type);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Icon className="w-4 h-4 text-blue-600 flex-shrink-0" />
            <span className="font-mono text-xs font-semibold text-blue-600">{test.code}</span>
            {test.requiresPriorAuth && (
              <Shield className="w-3.5 h-3.5 text-amber-500" />
            )}
            {test.fastingRequired && (
              <Clock className="w-3.5 h-3.5 text-orange-500" />
            )}
          </div>
          <h4 className="font-medium text-gray-900 text-sm truncate">{test.name}</h4>
          <p className="text-xs text-gray-600 truncate">{test.nameId}</p>
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
            <span className="bg-gray-100 px-2 py-0.5 rounded">{test.category}</span>
            <span>TAT: {test.tatHours} jam</span>
            {test.price && <span>Rp {test.price.toLocaleString()}</span>}
          </div>
        </div>
        <button
          type="button"
          onClick={onAdd}
          disabled={disabled}
          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
          title="Add to order"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {(test.fastingRequired || test.preparationInstructions) && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          {test.fastingRequired && (
            <p className="text-xs text-orange-700 bg-orange-50 px-2 py-1 rounded">
              ⚠️ Puasa diperlukan
            </p>
          )}
          {test.preparationInstructions && (
            <p className="text-xs text-gray-600 mt-1">ℹ️ {test.preparationInstructions}</p>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function TestOrdering({
  patientId,
  encounterId,
  patientDiagnoses = [],
  patientInsurance = "BPJS",
  onOrderSubmit,
  onResultAttach,
  disabled = false,
}: TestOrderingProps) {
  // State
  const [activeTab, setActiveTab] = useState<"catalog" | "orders" | "results">("catalog");
  const [testType, setTestType] = useState<TestType>("lab");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [orderedTests, setOrderedTests] = useState<OrderedTest[]>([]);
  const [searchResults, setSearchResults] = useState<TestItem[]>([]);

  // Form state
  const [clinicalIndication, setClinicalIndication] = useState("");
  const [priority, setPriority] = useState<"routine" | "urgent" | "stat">("routine");

  // Derived state
  const categories = Array.from(new Set(ALL_TESTS.filter((t) => t.type === testType).map((t) => t.category)));
  const filteredTests = searchQuery
    ? searchResults
    : selectedCategory
    ? ALL_TESTS.filter((t) => t.type === testType && t.category === selectedCategory)
    : ALL_TESTS.filter((t) => t.type === testType);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const query = searchQuery.toLowerCase();
      const results = ALL_TESTS.filter(
        (t) =>
          t.code.toLowerCase().includes(query) ||
          t.name.toLowerCase().includes(query) ||
          t.nameId.toLowerCase().includes(query)
      );
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleAddTest = useCallback(
    (test: TestItem) => {
      // Check if already added
      if (orderedTests.some((ot) => ot.test.id === test.id)) {
        return;
      }

      const orderedTest: OrderedTest = {
        test,
        priority,
        clinicalIndication: test.requiresIndication ? clinicalIndication : undefined,
        status: "pending",
        orderDate: new Date(),
        estimatedCompletion: new Date(Date.now() + (test.tatHours || 4) * 60 * 60 * 1000),
        priorAuthStatus: test.requiresPriorAuth ? "none" : undefined,
      };

      setOrderedTests([...orderedTests, orderedTest]);
    },
    [orderedTests, priority, clinicalIndication]
  );

  const handleRemoveTest = useCallback((testId: string) => {
    setOrderedTests(orderedTests.filter((ot) => ot.test.id !== testId));
  }, [orderedTests]);

  const handleUpdatePriority = useCallback((testId: string, newPriority: OrderedTest["priority"]) => {
    setOrderedTests(orderedTests.map((ot) => (ot.test.id === testId ? { ...ot, priority: newPriority } : ot)));
  }, [orderedTests]);

  const handleRequestAuth = useCallback(async (testId: string) => {
    // Mock prior auth request
    setOrderedTests(orderedTests.map((ot) =>
      ot.test.id === testId ? { ...ot, priorAuthStatus: "requested" } : ot
    ));

    // Simulate API call
    setTimeout(() => {
      const approved = Math.random() > 0.3; // 70% approval rate
      setOrderedTests((prev) =>
        prev.map((ot) =>
          ot.test.id === testId
            ? {
                ...ot,
                priorAuthStatus: approved ? "approved" : "rejected",
                priorAuthNumber: approved ? `AUTH-${Date.now()}` : undefined,
              }
            : ot
        )
      );
    }, 2000);
  }, [orderedTests]);

  const handleSubmitOrders = useCallback(async () => {
    // Mock order submission
    const updatedOrders = orderedTests.map((ot) => ({
      ...ot,
      orderId: `ORD-${Date.now()}-${ot.test.id}`,
      status: "pending" as const,
    }));

    setOrderedTests(updatedOrders);
    onOrderSubmit?.(updatedOrders);

    // Simulate order processing
    setTimeout(() => {
      setOrderedTests((prev) =>
        prev.map((ot, idx) =>
          idx === 0 ? { ...ot, status: "in-progress" as const } : ot
        )
      );
    }, 5000);
  }, [orderedTests, onOrderSubmit]);

  const handleViewResults = useCallback((testId: string) => {
    // Mock results viewing
    const testWithResults = orderedTests.find((ot) => ot.test.id === testId);
    if (testWithResults && !testWithResults.results) {
      setOrderedTests(orderedTests.map((ot) =>
        ot.test.id === testId
          ? {
              ...ot,
              status: "completed",
              results: MOCK_RESULTS,
            }
          : ot
      ));
    }
  }, [orderedTests]);

  const handleAttachResult = useCallback((testId: string) => {
    const test = orderedTests.find((ot) => ot.test.id === testId);
    if (test?.results) {
      onResultAttach?.(test.results[0]);
    }
  }, [orderedTests, onResultAttach]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab("catalog")}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === "catalog"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <Search className="w-4 h-4" />
            Katalog Pemeriksaan
          </button>
          <button
            onClick={() => setActiveTab("orders")}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === "orders"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <FileText className="w-4 h-4" />
            Pesanan Saya ({orderedTests.length})
          </button>
          <button
            onClick={() => setActiveTab("results")}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === "results"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <CheckCircle className="w-4 h-4" />
            Hasil ({orderedTests.filter((ot) => ot.status === "completed").length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "catalog" && (
        <div className="space-y-6">
          {/* Search and Filter */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 space-y-4">
            {/* Test Type Toggle */}
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-700">Tipe Pemeriksaan:</span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setTestType("lab")}
                  className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 ${
                    testType === "lab"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <TestTube2 className="w-4 h-4" />
                  Laboratorium
                </button>
                <button
                  type="button"
                  onClick={() => setTestType("radiology")}
                  className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 ${
                    testType === "radiology"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <Activity className="w-4 h-4" />
                  Radiologi
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Cari pemeriksaan berdasarkan nama atau kode..."
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 rounded"
                >
                  <X className="h-4 w-4 text-gray-400" />
                </button>
              )}
            </div>

            {/* Category Filter */}
            {!searchQuery && (
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedCategory("")}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium ${
                    !selectedCategory
                      ? "bg-blue-100 text-blue-800 border border-blue-300"
                      : "bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200"
                  }`}
                >
                  Semua Kategori
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium ${
                      selectedCategory === cat
                        ? "bg-blue-100 text-blue-800 border border-blue-300"
                        : "bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            )}

            {/* Common Settings */}
            {!searchQuery && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prioritas Default
                  </label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="routine">Routine</option>
                    <option value="urgent">Urgent</option>
                    <option value="stat">STAT (Segera)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Indikasi Klinis (Default)
                  </label>
                  <input
                    type="text"
                    value={clinicalIndication}
                    onChange={(e) => setClinicalIndication(e.target.value)}
                    placeholder="Indikasi untuk semua pemeriksaan..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Test List */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTests.map((test) => (
              <TestCard
                key={test.id}
                test={test}
                onAdd={() => handleAddTest(test)}
                disabled={disabled}
              />
            ))}
          </div>

          {filteredTests.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Search className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-sm">Tidak ada pemeriksaan yang ditemukan</p>
            </div>
          )}
        </div>
      )}

      {activeTab === "orders" && (
        <div className="space-y-6">
          {/* Order Actions */}
          {orderedTests.length > 0 && (
            <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="text-sm">
                <span className="font-medium text-blue-900">{orderedTests.length} pemeriksaan dipilih</span>
                <span className="text-blue-700 ml-2">Total: Rp {orderedTests.reduce((sum, ot) => sum + (ot.test.price || 0), 0).toLocaleString()}</span>
              </div>
              <button
                type="button"
                onClick={handleSubmitOrders}
                disabled={disabled}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Kirim Pesanan
              </button>
            </div>
          )}

          {/* Ordered Tests */}
          {orderedTests.length === 0 ? (
            <div className="text-center py-12 text-gray-500 bg-white rounded-lg border-2 border-dashed border-gray-300">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-sm">Belum ada pemeriksaan yang dipesan</p>
              <button
                type="button"
                onClick={() => setActiveTab("catalog")}
                className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
              >
                + Tambah Pemeriksaan
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {orderedTests.map((orderedTest) => {
                const Icon = getTestIcon(orderedTest.test.type);
                return (
                  <div key={orderedTest.test.id} className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Icon className="w-5 h-5 text-blue-600" />
                          <span className="font-mono text-sm font-bold text-blue-600">{orderedTest.test.code}</span>
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(orderedTest.status)}`}>
                            {orderedTest.status === "pending" && "Menunggu"}
                            {orderedTest.status === "in-progress" && "Sedang Diperiksa"}
                            {orderedTest.status === "completed" && "Selesai"}
                            {orderedTest.status === "cancelled" && "Dibatalkan"}
                          </span>
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(orderedTest.priority)}`}>
                            {orderedTest.priority.toUpperCase()}
                          </span>
                        </div>
                        <h4 className="font-medium text-gray-900">{orderedTest.test.name}</h4>
                        <p className="text-sm text-gray-600">{orderedTest.test.nameId}</p>

                        {/* Prior Auth */}
                        {orderedTest.test.requiresPriorAuth && (
                          <div className="mt-3 flex items-center gap-3">
                            {orderedTest.priorAuthStatus === "none" && (
                              <button
                                type="button"
                                onClick={() => handleRequestAuth(orderedTest.test.id)}
                                className="text-xs flex items-center gap-1 px-3 py-1.5 bg-amber-100 text-amber-800 rounded hover:bg-amber-200"
                              >
                                <Shield className="w-3 h-3" />
                                Request Otorisasi BPJS
                              </button>
                            )}
                            {orderedTest.priorAuthStatus === "requested" && (
                              <span className="text-xs flex items-center gap-1 px-3 py-1.5 bg-yellow-100 text-yellow-800 rounded">
                                <Clock className="w-3 h-3 animate-spin" />
                                Menunggu Otorisasi...
                              </span>
                            )}
                            {orderedTest.priorAuthStatus === "approved" && (
                              <span className="text-xs flex items-center gap-1 px-3 py-1.5 bg-green-100 text-green-800 rounded">
                                <CheckCircle className="w-3 h-3" />
                                Otorisasi Disetujui
                                {orderedTest.priorAuthNumber && <span>({orderedTest.priorAuthNumber})</span>}
                              </span>
                            )}
                            {orderedTest.priorAuthStatus === "rejected" && (
                              <span className="text-xs flex items-center gap-1 px-3 py-1.5 bg-red-100 text-red-800 rounded">
                                <AlertCircle className="w-3 h-3" />
                                Otorisasi Ditolak
                              </span>
                            )}
                          </div>
                        )}

                        {/* Estimated Time */}
                        {orderedTest.status !== "completed" && orderedTest.estimatedCompletion && (
                          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            Estimasi selesai:{" "}
                            {orderedTest.estimatedCompletion.toLocaleTimeString("id-ID", {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2">
                        {orderedTest.status === "pending" && (
                          <>
                            <select
                              value={orderedTest.priority}
                              onChange={(e) => handleUpdatePriority(orderedTest.test.id, e.target.value as any)}
                              className="text-xs border border-gray-300 rounded px-2 py-1"
                            >
                              <option value="routine">Routine</option>
                              <option value="urgent">Urgent</option>
                              <option value="stat">STAT</option>
                            </select>
                            <button
                              type="button"
                              onClick={() => handleRemoveTest(orderedTest.test.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        {orderedTest.status === "completed" && orderedTest.results && (
                          <button
                            type="button"
                            onClick={() => setActiveTab("results")}
                            className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                          >
                            Lihat Hasil
                            <ChevronRight className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {activeTab === "results" && (
        <div className="space-y-6">
          {/* Completed Tests with Results */}
          {orderedTests.filter((ot) => ot.status === "completed").length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-sm">Belum ada hasil pemeriksaan</p>
            </div>
          ) : (
            orderedTests
              .filter((ot) => ot.status === "completed")
              .map((orderedTest) => {
                const Icon = getTestIcon(orderedTest.test.type);
                const hasResults = orderedTest.results && orderedTest.results.length > 0;

                return (
                  <div key={orderedTest.test.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    {/* Test Header */}
                    <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Icon className="w-5 h-5 text-blue-600" />
                        <span className="font-mono text-sm font-bold text-blue-600">{orderedTest.test.code}</span>
                        <span className="font-medium text-gray-900">{orderedTest.test.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {hasResults && (
                          <button
                            type="button"
                            onClick={() => handleAttachResult(orderedTest.test.id)}
                            className="text-xs flex items-center gap-1 px-3 py-1.5 bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                          >
                            <Paperclip className="w-3 h-3" />
                            Lampirkan ke Kunjungan
                          </button>
                        )}
                        <button
                          type="button"
                          className="text-xs flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-800 rounded hover:bg-gray-200"
                        >
                          <Download className="w-3 h-3" />
                          Download PDF
                        </button>
                      </div>
                    </div>

                    {/* Results */}
                    {hasResults ? (
                      <div className="p-4">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-gray-200">
                              <th className="text-left py-2 font-medium text-gray-700">Parameter</th>
                              <th className="text-center py-2 font-medium text-gray-700">Hasil</th>
                              <th className="text-center py-2 font-medium text-gray-700">Nilai Rujuk</th>
                              <th className="text-center py-2 font-medium text-gray-700">Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {orderedTest.results!.map((result, idx) => (
                              <tr key={idx} className={result.isAbnormal ? "bg-red-50" : ""}>
                                <td className="py-2">{result.testName}</td>
                                <td className="text-center font-mono font-semibold">
                                  {result.value} <span className="text-gray-500">{result.unit}</span>
                                </td>
                                <td className="text-center text-gray-600">{result.referenceRange}</td>
                                <td className="text-center">
                                  {result.isAbnormal ? (
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                      result.flag === "critical"
                                        ? "bg-red-100 text-red-800"
                                        : result.flag === "high"
                                        ? "bg-orange-100 text-orange-800"
                                        : "bg-yellow-100 text-yellow-800"
                                    }`}>
                                      {result.flag === "high" && "↑"}
                                      {result.flag === "low" && "↓"}
                                      {result.flag === "critical" && "⚠"}
                                      {" "}
                                      Abnormal
                                    </span>
                                  ) : (
                                    <span className="text-green-600">Normal</span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        {orderedTest.orderDate && (
                          <div className="mt-3 text-xs text-gray-500 text-right">
                            Tanggal pemeriksaan: {orderedTest.orderDate.toLocaleDateString("id-ID")}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="p-8 text-center text-gray-500">
                        <p className="text-sm">Hasil belum tersedia</p>
                        <button
                          type="button"
                          onClick={() => handleViewResults(orderedTest.test.id)}
                          className="mt-2 text-blue-600 hover:text-blue-700 text-sm"
                        >
                          Muat Hasil (Demo)
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
          )}
        </div>
      )}
    </div>
  );
}

export default TestOrdering;
