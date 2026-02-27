"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Activity,
  Search,
  Filter,
  ChevronRight,
  Download,
  RefreshCw,
  User,
  Clock,
  Monitor,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface AuditLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  module: string;
  details: string;
  ipAddress: string;
  userAgent: string;
  status: "success" | "failed" | "warning";
}

export default function AuditLogsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [actionFilter, setActionFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("today");

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      // Simulate loading audit logs
      setLogs([
        {
          id: "1",
          timestamp: "2026-02-27 10:45:32",
          user: "admin",
          action: "LOGIN",
          module: "Authentication",
          details: "User logged in successfully",
          ipAddress: "192.168.1.100",
          userAgent: "Chrome/120.0.0",
          status: "success",
        },
        {
          id: "2",
          timestamp: "2026-02-27 10:42:15",
          user: "doctor1",
          action: "CREATE",
          module: "Prescriptions",
          details: "Created prescription #RX-2026-0227-001",
          ipAddress: "192.168.1.105",
          userAgent: "Firefox/122.0",
          status: "success",
        },
        {
          id: "3",
          timestamp: "2026-02-27 10:38:00",
          user: "nurse1",
          action: "UPDATE",
          module: "Patient Records",
          details: "Updated vitals for patient MRN-001",
          ipAddress: "192.168.1.110",
          userAgent: "Chrome/120.0.0",
          status: "success",
        },
        {
          id: "4",
          timestamp: "2026-02-27 10:30:45",
          user: "unknown",
          action: "LOGIN",
          module: "Authentication",
          details: "Failed login attempt - invalid password",
          ipAddress: "203.45.67.89",
          userAgent: "Chrome/120.0.0",
          status: "failed",
        },
        {
          id: "5",
          timestamp: "2026-02-27 10:25:12",
          user: "billing1",
          action: "CREATE",
          module: "Invoices",
          details: "Created invoice #INV-2026-0227-015",
          ipAddress: "192.168.1.115",
          userAgent: "Edge/120.0.0",
          status: "success",
        },
        {
          id: "6",
          timestamp: "2026-02-27 10:15:33",
          user: "pharmacist1",
          action: "UPDATE",
          module: "Inventory",
          details: "Updated stock for Paracetamol 500mg",
          ipAddress: "192.168.1.120",
          userAgent: "Chrome/120.0.0",
          status: "warning",
        },
        {
          id: "7",
          timestamp: "2026-02-27 10:00:00",
          user: "system",
          action: "BACKUP",
          module: "System",
          details: "Automated database backup completed",
          ipAddress: "127.0.0.1",
          userAgent: "System/1.0",
          status: "success",
        },
        {
          id: "8",
          timestamp: "2026-02-27 09:45:22",
          user: "admin",
          action: "DELETE",
          module: "Users",
          details: "Deleted user account: test_user",
          ipAddress: "192.168.1.100",
          userAgent: "Chrome/120.0.0",
          status: "success",
        },
      ]);
    } catch (error) {
      console.error("Failed to load audit logs:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.filter((log) => {
    const matchesSearch =
      log.user.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.details.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.module.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesAction = actionFilter === "all" || log.action.toLowerCase() === actionFilter;
    return matchesSearch && matchesAction;
  });

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      success: "bg-green-100 text-green-700",
      failed: "bg-red-100 text-red-700",
      warning: "bg-yellow-100 text-yellow-700",
    };
    const labels: Record<string, string> = {
      success: "Berhasil",
      failed: "Gagal",
      warning: "Peringatan",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const getActionBadge = (action: string) => {
    const styles: Record<string, string> = {
      LOGIN: "bg-blue-100 text-blue-700",
      LOGOUT: "bg-gray-100 text-gray-700",
      CREATE: "bg-green-100 text-green-700",
      UPDATE: "bg-yellow-100 text-yellow-700",
      DELETE: "bg-red-100 text-red-700",
      BACKUP: "bg-purple-100 text-purple-700",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[action] || "bg-gray-100 text-gray-700"}`}>
        {action}
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">
            Dashboard
          </Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/admin/dashboard" className="hover:text-gray-700">
            Admin
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Audit Logs</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
            <p className="text-gray-600 mt-1">Riwayat aktivitas sistem dan pengguna</p>
          </div>
          <div className="flex space-x-2">
            <Button variant="secondary" onClick={loadAuditLogs}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button variant="secondary">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari user, aksi, atau detail..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">Semua Aksi</option>
              <option value="login">Login</option>
              <option value="logout">Logout</option>
              <option value="create">Create</option>
              <option value="update">Update</option>
              <option value="delete">Delete</option>
            </select>
            <select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="today">Hari Ini</option>
              <option value="yesterday">Kemarin</option>
              <option value="week">Minggu Ini</option>
              <option value="month">Bulan Ini</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            Log Aktivitas ({filteredLogs.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Waktu</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">User</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Module</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Detail</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">IP Address</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLogs.map((log) => (
                    <tr key={log.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2 text-sm">
                          <Clock className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600">{log.timestamp}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <User className="h-4 w-4 text-gray-400" />
                          <span className="font-medium text-gray-900">{log.user}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">{getActionBadge(log.action)}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{log.module}</td>
                      <td className="py-3 px-4 text-sm text-gray-600 max-w-xs truncate">{log.details}</td>
                      <td className="py-3 px-4 text-sm text-gray-500 font-mono">{log.ipAddress}</td>
                      <td className="py-3 px-4">{getStatusBadge(log.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
