"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface InventoryItem {
  id: number;
  item_code: string;
  item_name: string;
  generic_name?: string;
  category: "medication" | "consumable" | "equipment" | "reagent" | "supply";
  unit: string;
  manufacturer?: string;
  supplier?: string;
  current_stock: number;
  minimum_stock: number;
  maximum_stock: number;
  reorder_point: number;
  reorder_quantity: number;
  unit_cost: number;
  selling_price?: number;
  expiry_date?: string;
  batch_number?: string;
  location: string;
  status: "available" | "low_stock" | "out_of_stock" | "expired" | "discontinued";
  last_restocked?: string;
  created_at: string;
  updated_at: string;
}

interface StockMovement {
  id: number;
  item_id: number;
  item_name: string;
  movement_type: "in" | "out" | "adjustment" | "transfer" | "return" | "expired";
  quantity: number;
  reference_number?: string;
  reference_type?: "purchase" | "sale" | "usage" | "transfer" | "adjustment" | "return";
  notes?: string;
  performed_by: string;
  performed_at: string;
}

export default function InventoryPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [expandedItem, setExpandedItem] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"items" | "movements">("items");
  const [filters, setFilters] = useState({
    category: "",
    status: "",
    location: "",
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState({
    totalItems: 0,
    lowStock: 0,
    outOfStock: 0,
    expired: 0,
    totalValue: 0,
  });

  useEffect(() => {
    checkAuth();
    fetchItems();
    fetchMovements();
    fetchStats();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  };

  const fetchItems = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const queryParams = new URLSearchParams();
      if (filters.category) queryParams.append("category", filters.category);
      if (filters.status) queryParams.append("status", filters.status);
      if (filters.location) queryParams.append("location", filters.location);
      if (searchQuery) queryParams.append("search", searchQuery);

      const response = await fetch(`/api/v1/inventory/items?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch inventory items");
      }

      const data = await response.json();
      setItems(data.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load inventory");
    } finally {
      setLoading(false);
    }
  };

  const fetchMovements = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/inventory/movements?limit=20", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMovements(data.movements || []);
      }
    } catch (err) {
      console.error("Failed to fetch movements:", err);
    }
  };

  const fetchStats = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/inventory/statistics", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats({
          totalItems: data.total_items || 0,
          lowStock: data.low_stock || 0,
          outOfStock: data.out_of_stock || 0,
          expired: data.expired || 0,
          totalValue: data.total_value || 0,
        });
      }
    } catch (err) {
      console.error("Failed to fetch statistics:", err);
    }
  };

  const handleStockAdjustment = async (itemId: number, quantity: number, type: string) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/inventory/items/${itemId}/adjust`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ quantity, type }),
      });

      if (!response.ok) {
        throw new Error("Failed to adjust stock");
      }

      alert("Penyesuaian stok berhasil");
      fetchItems();
      fetchMovements();
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to adjust stock");
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; className: string }> = {
      available: { label: "Tersedia", className: "bg-green-100 text-green-700" },
      low_stock: { label: "Stok Rendah", className: "bg-yellow-100 text-yellow-700" },
      out_of_stock: { label: "Habis", className: "bg-red-100 text-red-700" },
      expired: { label: "Kedaluwarsa", className: "bg-red-100 text-red-700" },
      discontinued: { label: "Discontinue", className: "bg-gray-100 text-gray-500" },
    };

    const config = statusConfig[status] || statusConfig.available;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const getCategoryBadge = (category: string) => {
    const categoryConfig: Record<string, { label: string; icon: string; className: string }> = {
      medication: { label: "Obat", icon: "💊", className: "bg-blue-100 text-blue-700" },
      consumable: { label: "Consumable", icon: "🩹", className: "bg-purple-100 text-purple-700" },
      equipment: { label: "Peralatan", icon: "🔧", className: "bg-orange-100 text-orange-700" },
      reagent: { label: "Reagen", icon: "🧪", className: "bg-green-100 text-green-700" },
      supply: { label: "Supplies", icon: "📦", className: "bg-indigo-100 text-indigo-700" },
    };

    const config = categoryConfig[category] || categoryConfig.medication;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        {config.icon} {config.label}
      </span>
    );
  };

  const getMovementTypeBadge = (type: string) => {
    const typeConfig: Record<string, { label: string; className: string; icon: string }> = {
      in: { label: "Masuk", className: "bg-green-100 text-green-700", icon: "↓" },
      out: { label: "Keluar", className: "bg-red-100 text-red-700", icon: "↑" },
      adjustment: { label: "Penyesuaian", className: "bg-blue-100 text-blue-700", icon: "↔" },
      transfer: { label: "Transfer", className: "bg-purple-100 text-purple-700", icon: "→" },
      return: { label: "Retur", className: "bg-yellow-100 text-yellow-700", icon: "↩" },
      expired: { label: "Kedaluwarsa", className: "bg-red-100 text-red-700", icon: "⚠" },
    };

    const config = typeConfig[type] || typeConfig.adjustment;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        {config.icon} {config.label}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const isExpired = (expiryDate?: string) => {
    if (!expiryDate) return false;
    return new Date(expiryDate) < new Date();
  };

  const isExpiringSoon = (expiryDate?: string) => {
    if (!expiryDate) return false;
    const expiry = new Date(expiryDate);
    const warningDate = new Date();
    warningDate.setMonth(warningDate.getMonth() + 3); // 3 months warning
    return expiry < warningDate && expiry > new Date();
  };

  const toggleExpand = (itemId: number) => {
    setExpandedItem(expandedItem === itemId ? null : itemId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventaris</h1>
          <p className="text-gray-600 mt-1">Kelola stok obat, consumable, dan peralatan medis</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => router.push("/app/inventory/movements")}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>Mutasi</span>
          </button>
          <button
            onClick={() => router.push("/app/inventory/new")}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Tambah Item</span>
          </button>
        </div>
      </div>

      {/* Statistics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Item</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalItems}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📦</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Stok Rendah</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.lowStock}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⚠️</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Stok Habis</p>
              <p className="text-2xl font-bold text-red-600">{stats.outOfStock}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🚫</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Kedaluwarsa</p>
              <p className="text-2xl font-bold text-red-600">{stats.expired}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⏰</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Nilai</p>
              <p className="text-xl font-bold text-indigo-600">{formatCurrency(stats.totalValue)}</p>
            </div>
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">💰</span>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab("items")}
              className={`px-6 py-4 text-sm font-medium ${
                activeTab === "items"
                  ? "border-b-2 border-indigo-500 text-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Item Inventaris
            </button>
            <button
              onClick={() => setActiveTab("movements")}
              className={`px-6 py-4 text-sm font-medium ${
                activeTab === "movements"
                  ? "border-b-2 border-indigo-500 text-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Mutasi Stok Terkini
            </button>
          </nav>
        </div>

        {/* Items Tab */}
        {activeTab === "items" && (
          <div className="p-6">
            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Kategori</label>
                <select
                  value={filters.category}
                  onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Semua</option>
                  <option value="medication">Obat</option>
                  <option value="consumable">Consumable</option>
                  <option value="equipment">Peralatan</option>
                  <option value="reagent">Reagen</option>
                  <option value="supply">Supplies</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Semua</option>
                  <option value="available">Tersedia</option>
                  <option value="low_stock">Stok Rendah</option>
                  <option value="out_of_stock">Habis</option>
                  <option value="expired">Kedaluwarsa</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Lokasi</label>
                <input
                  type="text"
                  placeholder="Cari lokasi..."
                  value={filters.location}
                  onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => {
                    setFilters({ category: "", status: "", location: "" });
                    setSearchQuery("");
                    fetchItems();
                  }}
                  className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Reset
                </button>
              </div>
            </div>

            <div className="mb-6">
              <input
                type="text"
                placeholder="Cari berdasarkan nama, kode, atau batch number..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Items List */}
            {items.length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada item ditemukan</h3>
                <p className="text-gray-600">Coba sesuaikan filter atau tambah item baru</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kategori</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Stok</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Harga</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lokasi</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {items.map((item) => (
                      <>
                        <tr key={item.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => toggleExpand(item.id)}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-3">
                              <div className="flex-1">
                                <div className="text-sm font-medium text-gray-900">{item.item_name}</div>
                                <div className="text-xs text-gray-500">{item.item_code}</div>
                                {item.generic_name && (
                                  <div className="text-xs text-gray-400">{item.generic_name}</div>
                                )}
                              </div>
                              {(isExpired(item.expiry_date) || isExpiringSoon(item.expiry_date)) && (
                                <span className="animate-pulse">⚠️</span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {getCategoryBadge(item.category)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {getStatusBadge(item.status)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm font-medium text-gray-900">
                              {item.current_stock} {item.unit}
                            </div>
                            <div className="text-xs text-gray-500">
                              Min: {item.minimum_stock} {item.unit}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right">
                            <div className="text-sm text-gray-900">{formatCurrency(item.unit_cost)}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-700">{item.location}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="flex items-center justify-center space-x-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  router.push(`/app/inventory/${item.id}/edit`);
                                }}
                                className="p-1 text-gray-400 hover:text-indigo-600"
                                title="Edit"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleExpand(item.id);
                                }}
                                className="p-1 text-gray-400 hover:text-indigo-600"
                                title="Detail"
                              >
                                {expandedItem === item.id ? (
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                  </svg>
                                ) : (
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                  </svg>
                                )}
                              </button>
                            </div>
                          </td>
                        </tr>
                        {expandedItem === item.id && (
                          <tr>
                            <td colSpan={7} className="px-6 py-4 bg-gray-50">
                              <div className="space-y-4">
                                {/* Item Details */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                  <div>
                                    <p className="text-xs text-gray-500">Produsen</p>
                                    <p className="text-sm font-medium text-gray-900">{item.manufacturer || "-"}</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500">Supplier</p>
                                    <p className="text-sm font-medium text-gray-900">{item.supplier || "-"}</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500">Batch Number</p>
                                    <p className="text-sm font-medium text-gray-900">{item.batch_number || "-"}</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500">Tanggal Kedaluwarsa</p>
                                    <p className={`text-sm font-medium ${isExpired(item.expiry_date) ? "text-red-600" : isExpiringSoon(item.expiry_date) ? "text-yellow-600" : "text-gray-900"}`}>
                                      {item.expiry_date ? new Date(item.expiry_date).toLocaleDateString("id-ID") : "-"}
                                    </p>
                                  </div>
                                </div>

                                {/* Stock Levels */}
                                <div className="bg-white rounded-lg p-4 border border-gray-200">
                                  <h4 className="text-sm font-medium text-gray-900 mb-3">Level Stok</h4>
                                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                    <div>
                                      <p className="text-xs text-gray-500">Stok Saat Ini</p>
                                      <p className="text-lg font-bold text-indigo-600">{item.current_stock} {item.unit}</p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Stok Minimum</p>
                                      <p className="text-sm font-medium text-gray-700">{item.minimum_stock} {item.unit}</p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Stok Maksimum</p>
                                      <p className="text-sm font-medium text-gray-700">{item.maximum_stock} {item.unit}</p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Reorder Point</p>
                                      <p className="text-sm font-medium text-gray-700">{item.reorder_point} {item.unit}</p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Jumlah Reorder</p>
                                      <p className="text-sm font-medium text-gray-700">{item.reorder_quantity} {item.unit}</p>
                                    </div>
                                  </div>

                                  {/* Stock Level Bar */}
                                  <div className="mt-4">
                                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                                      <span>Level Stok</span>
                                      <span>{Math.round((item.current_stock / item.maximum_stock) * 100)}%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                      <div
                                        className={`h-2 rounded-full ${
                                          item.current_stock <= item.minimum_stock
                                            ? "bg-red-500"
                                            : item.current_stock <= item.reorder_point
                                            ? "bg-yellow-500"
                                            : "bg-green-500"
                                        }`}
                                        style={{ width: `${Math.min((item.current_stock / item.maximum_stock) * 100, 100)}%` }}
                                      ></div>
                                    </div>
                                  </div>
                                </div>

                                {/* Pricing */}
                                {item.selling_price && (
                                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                                    <h4 className="text-sm font-medium text-gray-900 mb-3">Harga</h4>
                                    <div className="grid grid-cols-2 gap-4">
                                      <div>
                                        <p className="text-xs text-gray-500">Harga Beli (Unit)</p>
                                        <p className="text-sm font-medium text-gray-700">{formatCurrency(item.unit_cost)}</p>
                                      </div>
                                      <div>
                                        <p className="text-xs text-gray-500">Harga Jual (Unit)</p>
                                        <p className="text-sm font-medium text-green-600">{formatCurrency(item.selling_price)}</p>
                                      </div>
                                    </div>
                                  </div>
                                )}

                                {/* Warning for Expired/Expiring */}
                                {isExpired(item.expiry_date) && (
                                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
                                    <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <div>
                                      <h4 className="text-sm font-medium text-red-800">Item Kedaluwarsa</h4>
                                      <p className="text-sm text-red-700">Item ini telah kedaluwarsa dan harus dikeluarkan dari stok.</p>
                                    </div>
                                  </div>
                                )}

                                {isExpiringSoon(item.expiry_date) && !isExpired(item.expiry_date) && (
                                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start space-x-3">
                                    <svg className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <div>
                                      <h4 className="text-sm font-medium text-yellow-800">Akan Kedaluwarsa</h4>
                                      <p className="text-sm text-yellow-700">
                                        Item ini akan kedaluwarsa pada{" "}
                                        {new Date(item.expiry_date!).toLocaleDateString("id-ID")}
                                      </p>
                                    </div>
                                  </div>
                                )}

                                {/* Actions */}
                                <div className="flex flex-wrap gap-2 pt-4 border-t">
                                  <button
                                    onClick={() => router.push(`/app/inventory/${item.id}/adjust`)}
                                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                                  >
                                    Penyesuaian Stok
                                  </button>
                                  <button
                                    onClick={() => router.push(`/app/inventory/${item.id}/transfer`)}
                                    className="px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700"
                                  >
                                    Transfer Stok
                                  </button>
                                  <button
                                    onClick={() => router.push(`/app/inventory/${item.id}/history`)}
                                    className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                                  >
                                    Riwayat Mutasi
                                  </button>
                                  {item.current_stock <= item.reorder_point && item.status !== "discontinued" && (
                                    <button
                                      onClick={() => router.push(`/app/inventory/${item.id}/reorder`)}
                                      className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 animate-pulse"
                                    >
                                      Pesan Restock
                                    </button>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Movements Tab */}
        {activeTab === "movements" && (
          <div className="p-6">
            {movements.length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Belum ada mutasi stok</h3>
                <p className="text-gray-600">Mutasi stok akan muncul di sini</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tanggal</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipe</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Referensi</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Oleh</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {movements.map((movement) => (
                      <tr key={movement.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {new Date(movement.performed_at).toLocaleDateString("id-ID")}
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(movement.performed_at).toLocaleTimeString("id-ID")}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{movement.item_name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getMovementTypeBadge(movement.movement_type)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <div className={`text-sm font-medium ${
                            movement.movement_type === "in" || movement.movement_type === "return"
                              ? "text-green-600"
                              : "text-red-600"
                          }`}>
                            {movement.movement_type === "in" || movement.movement_type === "return" ? "+" : "-"}
                            {movement.quantity}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{movement.reference_number || "-"}</div>
                          <div className="text-xs text-gray-500">{movement.reference_type || "-"}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-700">{movement.performed_by}</div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
