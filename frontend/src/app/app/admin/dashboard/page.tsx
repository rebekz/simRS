"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Users,
  Building2,
  Activity,
  AlertTriangle,
  TrendingUp,
  Clock,
  Database,
  Server,
  ChevronRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalPatients: number;
  todayAppointments: number;
  systemHealth: string;
  dbSize: string;
  lastBackup: string;
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<SystemStats>({
    totalUsers: 0,
    activeUsers: 0,
    totalPatients: 0,
    todayAppointments: 0,
    systemHealth: "healthy",
    dbSize: "0 MB",
    lastBackup: "-",
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      // Simulate loading stats
      setStats({
        totalUsers: 45,
        activeUsers: 12,
        totalPatients: 1250,
        todayAppointments: 38,
        systemHealth: "healthy",
        dbSize: "2.4 GB",
        lastBackup: "2026-02-27 02:00:00",
      });
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    { label: "Kelola Pengguna", href: "/app/admin/users", icon: Users },
    { label: "Audit Logs", href: "/app/admin/audit-logs", icon: Activity },
    { label: "Pengaturan", href: "/app/admin/settings", icon: Building2 },
  ];

  const systemMetrics = [
    { label: "CPU Usage", value: "23%", color: "bg-green-500" },
    { label: "Memory", value: "4.2 GB / 8 GB", color: "bg-blue-500" },
    { label: "Disk", value: "156 GB / 500 GB", color: "bg-yellow-500" },
    { label: "Network", value: "1.2 MB/s", color: "bg-purple-500" },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">
            Dashboard
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Admin Dashboard</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-1">System administration and monitoring</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
        </div>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Total Pengguna</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.totalUsers}</p>
                  </div>
                  <Users className="h-8 w-8 text-teal-600" />
                </div>
                <p className="text-xs text-gray-500 mt-2">{stats.activeUsers} aktif sekarang</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Total Pasien</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.totalPatients}</p>
                  </div>
                  <Building2 className="h-8 w-8 text-blue-600" />
                </div>
                <p className="text-xs text-green-600 mt-2">+12 hari ini</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Janji Temu Hari Ini</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.todayAppointments}</p>
                  </div>
                  <Clock className="h-8 w-8 text-orange-600" />
                </div>
                <p className="text-xs text-gray-500 mt-2">15 selesai, 23 tersisa</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Status Sistem</p>
                    <p className="text-2xl font-bold text-green-600 capitalize">{stats.systemHealth}</p>
                  </div>
                  <Server className="h-8 w-8 text-green-600" />
                </div>
                <p className="text-xs text-gray-500 mt-2">Uptime: 99.9%</p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions & System Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Aksi Cepat</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {quickActions.map((action) => (
                  <Link
                    key={action.href}
                    href={action.href}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <action.icon className="h-5 w-5 text-gray-500" />
                      <span className="font-medium text-gray-900">{action.label}</span>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-400" />
                  </Link>
                ))}
              </CardContent>
            </Card>

            {/* System Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Metrik Sistem</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {systemMetrics.map((metric) => (
                  <div key={metric.label}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600">{metric.label}</span>
                      <span className="text-sm font-medium text-gray-900">{metric.value}</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className={`h-full ${metric.color} rounded-full`} style={{ width: "45%" }}></div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Database Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Database className="h-5 w-5 mr-2" />
                Informasi Database
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Ukuran Database</p>
                  <p className="text-lg font-semibold text-gray-900">{stats.dbSize}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Backup Terakhir</p>
                  <p className="text-lg font-semibold text-gray-900">{stats.lastBackup}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Status Backup</p>
                  <p className="text-lg font-semibold text-green-600">Berhasil</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
