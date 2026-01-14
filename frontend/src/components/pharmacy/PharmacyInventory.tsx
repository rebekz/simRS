"""Pharmacy Inventory Management UI Component for STORY-024

Provides comprehensive inventory management with:
- Real-time stock levels dashboard
- Near expiry alerts (3 months)
- Expired drug quarantine
- Low stock alerts with reorder points
- FIFO dispensing logic
"""

import { useState, useEffect } from "react";
import {
  Package,
  AlertTriangle,
  TrendingDown,
  Clock,
  RefreshCw,
  Search,
  Filter,
  Plus,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

// Types
interface StockLevel {
  drug_id: number;
  drug_name: string;
  drug_code: string;
  generic_name: string;
  dosage_form: string;
  current_stock: number;
  min_stock_level: number;
  max_stock_level: number;
  reorder_point: number;
  is_below_min: boolean;
  batches: Batch[];
  last_purchase_price: number | null;
  total_value: number | null;
}

interface Batch {
  id: number;
  batch_number: string;
  expiry_date: string;
  quantity: number;
  is_quarantined: boolean;
  is_expired: boolean;
  is_near_expiry: boolean;
  days_to_expiry: number | null;
}

interface InventoryAlert {
  alert_type: string;
  drug_id: number;
  drug_name: string;
  drug_code: string;
  current_stock: number;
  message: string;
  severity: "critical" | "warning" | "info";
}

interface InventorySummary {
  total_drugs: number;
  total_items: number;
  total_value: number;
  drugs_below_min: number;
  drugs_near_expiry: number;
  drugs_expired: number;
  drugs_out_of_stock: number;
  purchase_orders_pending: number;
  purchase_orders_approved: number;
}

export function PharmacyInventory() {
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [alerts, setAlerts] = useState<InventoryAlert[]>([]);
  const [stockLevels, setStockLevels] = useState<StockLevel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [showOnlyAlerts, setShowOnlyAlerts] = useState(true);

  useEffect(() => {
    loadData();
  }, [showOnlyAlerts]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // Load summary
      const summaryResponse = await fetch("/api/v1/inventory/summary", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        setSummary(summaryData);
      }

      // Load alerts
      const alertsResponse = await fetch("/api/v1/inventory/alerts", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData);
      }

      // Load stock levels
      const stockLevelsResponse = await fetch(
        `/api/v1/inventory/stock-levels?only_alerts=${showOnlyAlerts}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      if (stockLevelsResponse.ok) {
        const stockLevelsData = await stockLevelsResponse.json();
        setStockLevels(stockLevelsData);
      }
    } catch (error) {
      console.error("Failed to load inventory data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-50 border-red-200 text-red-800";
      case "warning":
        return "bg-yellow-50 border-yellow-200 text-yellow-800";
      case "info":
        return "bg-blue-50 border-blue-200 text-blue-800";
      default:
        return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  const getAlertIcon = (alertType: string) => {
    switch (alertType) {
      case "out_of_stock":
        return AlertCircle;
      case "low_stock":
        return TrendingDown;
      case "near_expiry":
      case "expired":
        return Clock;
      default:
        return AlertTriangle;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("id-ID", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (isLoading && !summary) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Package className="h-6 w-6 mr-2" />
            Manajemen Inventori Farmasi
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Pantau stok obat, tanggal kedaluwarsa, dan peringatan stok
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white shadow rounded-lg p-4">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Package className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Obat</p>
                <p className="text-xl font-bold text-gray-900">{summary.total_drugs}</p>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-4">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Item</p>
                <p className="text-xl font-bold text-gray-900">{summary.total_items}</p>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-4">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Stok Rendah</p>
                <p className="text-xl font-bold text-gray-900">{summary.drugs_below_min}</p>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-4">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <Clock className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Kadaluarsa</p>
                <p className="text-xl font-bold text-gray-900">{summary.drugs_expired}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2 text-yellow-600" />
            Peringatan Inventori ({alerts.length})
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {alerts.map((alert, idx) => {
              const Icon = getAlertIcon(alert.alert_type);
              return (
                <div
                  key={idx}
                  className={`border-l-4 p-4 rounded-md ${getSeverityClass(alert.severity)}`}
                >
                  <div className="flex items-start">
                    <Icon className="h-5 w-5 mr-3 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{alert.message}</p>
                      <p className="text-xs mt-1 opacity-75">
                        {alert.drug_code} - Stok: {alert.current_stock}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Stock Levels */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Level Stok Obat</h3>
          <div className="flex items-center space-x-3">
            <label className="flex items-center text-sm text-gray-600">
              <input
                type="checkbox"
                checked={showOnlyAlerts}
                onChange={(e) => setShowOnlyAlerts(e.target.checked)}
                className="mr-2"
              />
              Hanya peringatan
            </label>
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Cari obat..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Nama Obat
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Kode
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Stok Saat Ini
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Min/Max
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Batch Terdekat
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stockLevels
                .filter(
                  (stock) =>
                    !searchTerm ||
                    stock.drug_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    stock.drug_code.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .map((stock) => {
                  // Get nearest expiry batch (FEFO)
                  const sortedBatches = [...stock.batches].sort(
                    (a, b) =>
                      new Date(a.expiry_date).getTime() - new Date(b.expiry_date).getTime()
                  );
                  const nearestBatch = sortedBatches[0];

                  const stockPercentage =
                    stock.max_stock_level > 0
                      ? (stock.current_stock / stock.max_stock_level) * 100
                      : 0;

                  const stockColor =
                    stock.current_stock === 0
                      ? "bg-red-100 text-red-800"
                      : stock.current_stock < stock.min_stock_level
                      ? "bg-yellow-100 text-yellow-800"
                      : stockPercentage > 80
                      ? "bg-green-100 text-green-800"
                      : "bg-blue-100 text-blue-800";

                  return (
                    <tr key={stock.drug_id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {stock.drug_name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {stock.generic_name} - {stock.dosage_form}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.drug_code}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-sm font-medium text-gray-900 mr-2">
                            {stock.current_stock}
                          </span>
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                stockPercentage > 80
                                  ? "bg-green-500"
                                  : stockPercentage > 50
                                  ? "bg-blue-500"
                                  : stockPercentage > 20
                                  ? "bg-yellow-500"
                                  : "bg-red-500"
                              }`}
                              style={{ width: `${Math.min(stockPercentage, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.min_stock_level} / {stock.max_stock_level}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {nearestBatch ? (
                          <div>
                            <div className="font-medium">{nearestBatch.batch_number}</div>
                            <div className="text-xs text-gray-500">
                              {formatDate(nearestBatch.expiry_date)}
                            </div>
                          </div>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        {stock.current_stock === 0 ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Habis
                          </span>
                        ) : stock.current_stock < stock.min_stock_level ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            Stok Rendah
                          </span>
                        ) : nearestBatch?.is_near_expiry ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            Mendekati Kedaluwarsa
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Normal
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>

          {stockLevels.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Package className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Tidak ada data inventori</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
