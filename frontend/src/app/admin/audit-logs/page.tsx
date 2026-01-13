/**
 * Audit Logs Admin Page
 *
 * Allows administrators to view and filter audit logs.
 * Only accessible to users with audit:read permission.
 */
"use client";

import { useState, useEffect } from "react";

interface AuditLog {
  id: number;
  timestamp: string;
  user_id: number | null;
  username: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  ip_address: string | null;
  request_path: string | null;
  request_method: string | null;
  success: boolean;
  failure_reason: string | null;
}

interface AuditLogsResponse {
  total: number;
  items: AuditLog[];
  limit: number;
  offset: number;
  has_more: boolean;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    action: "",
    resource_type: "",
    username: "",
    start_date: "",
    end_date: "",
  });
  const [pagination, setPagination] = useState({
    limit: 50,
    offset: 0,
  });

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
        ...(filters.action && { action: filters.action }),
        ...(filters.resource_type && { resource_type: filters.resource_type }),
        ...(filters.username && { username: filters.username }),
        ...(filters.start_date && { start_date: filters.start_date }),
        ...(filters.end_date && { end_date: filters.end_date }),
      });

      const response = await fetch(`${API_BASE}/api/v1/audit/logs?${params}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch audit logs");
      }

      const data: AuditLogsResponse = await response.json();
      setLogs(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const exportLogs = async () => {
    try {
      const params = new URLSearchParams({
        format: "csv",
        ...(filters.action && { action: filters.action }),
        ...(filters.resource_type && { resource_type: filters.resource_type }),
        ...(filters.start_date && { start_date: filters.start_date }),
        ...(filters.end_date && { end_date: filters.end_date }),
      });

      const response = await fetch(`${API_BASE}/api/v1/audit/logs/export?${params}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to export logs");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `audit_logs_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [pagination]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPagination((prev) => ({ ...prev, offset: 0 }));
  };

  const handleSearch = () => {
    setPagination((prev) => ({ ...prev, offset: 0 }));
    fetchLogs();
  };

  const handlePageChange = (newOffset: number) => {
    setPagination((prev) => ({ ...prev, offset: newOffset }));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
              <p className="text-gray-600 mt-1">
                View and filter system activity logs
              </p>
            </div>
            <button
              onClick={exportLogs}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
            >
              Export to CSV
            </button>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-6">
            <input
              type="text"
              placeholder="Username"
              value={filters.username}
              onChange={(e) => handleFilterChange("username", e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
            <select
              value={filters.action}
              onChange={(e) => handleFilterChange("action", e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              <option value="">All Actions</option>
              <option value="CREATE">Create</option>
              <option value="READ">Read</option>
              <option value="UPDATE">Update</option>
              <option value="DELETE">Delete</option>
              <option value="LOGIN">Login</option>
              <option value="LOGOUT">Logout</option>
              <option value="EXPORT">Export</option>
            </select>
            <select
              value={filters.resource_type}
              onChange={(e) => handleFilterChange("resource_type", e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              <option value="">All Resources</option>
              <option value="Patient">Patient</option>
              <option value="User">User</option>
              <option value="Encounter">Encounter</option>
              <option value="Prescription">Prescription</option>
              <option value="Diagnosis">Diagnosis</option>
            </select>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange("start_date", e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
            >
              Search
            </button>
          </div>

          {/* Results count */}
          <div className="mt-4 text-sm text-gray-600">
            Showing {logs.length} of {total} logs
          </div>
        </div>

        {/* Logs table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-600">Loading...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-600">{error}</div>
          ) : logs.length === 0 ? (
            <div className="p-8 text-center text-gray-600">No logs found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Timestamp
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      User
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Action
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Resource
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      IP Address
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {log.username || "-"}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          log.action === "CREATE" ? "bg-green-100 text-green-800" :
                          log.action === "READ" ? "bg-blue-100 text-blue-800" :
                          log.action === "UPDATE" ? "bg-yellow-100 text-yellow-800" :
                          log.action === "DELETE" ? "bg-red-100 text-red-800" :
                          "bg-gray-100 text-gray-800"
                        }`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {log.resource_type}
                        {log.resource_id && ` (${log.resource_id})`}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {log.ip_address || "-"}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {log.success ? (
                          <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                            Success
                          </span>
                        ) : (
                          <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                            Failed
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {total > pagination.limit && (
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
              <button
                onClick={() => handlePageChange(Math.max(0, pagination.offset - pagination.limit))}
                disabled={pagination.offset === 0}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {Math.floor(pagination.offset / pagination.limit) + 1} of {Math.ceil(total / pagination.limit)}
              </span>
              <button
                onClick={() => handlePageChange(pagination.offset + pagination.limit)}
                disabled={pagination.offset + pagination.limit >= total}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
