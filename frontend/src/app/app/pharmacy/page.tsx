"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Pill,
  Package,
  FileText,
  AlertTriangle,
  TrendingUp,
  Clock,
  ChevronRight,
  Search,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function PharmacyDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  const stats = [
    { label: "Resep Hari Ini", value: 45, icon: FileText, color: "text-blue-600", bgColor: "bg-blue-100" },
    { label: "Resep Pending", value: 12, icon: Clock, color: "text-orange-600", bgColor: "bg-orange-100" },
    { label: "Stok Rendah", value: 8, icon: AlertTriangle, color: "text-red-600", bgColor: "bg-red-100" },
    { label: "Total Item", value: 1250, icon: Package, color: "text-green-600", bgColor: "bg-green-100" },
  ];

  const quickActions = [
    { label: "Daftar Resep", href: "/app/pharmacy/prescriptions", icon: FileText },
    { label: "Inventori", href: "/app/pharmacy/inventory", icon: Package },
  ];

  const recentPrescriptions = [
    { id: "RX-001", patient: "Ahmad Susanto", doctor: "Dr. Budi", status: "pending", time: "10:30" },
    { id: "RX-002", patient: "Siti Rahayu", doctor: "Dr. Dewi", status: "processing", time: "10:15" },
    { id: "RX-003", patient: "Budi Santoso", doctor: "Dr. Ahmad", status: "completed", time: "09:45" },
    { id: "RX-004", patient: "Dewi Lestari", doctor: "Dr. Siti", status: "completed", time: "09:30" },
  ];

  const lowStockItems = [
    { name: "Paracetamol 500mg", stock: 50, min: 100, unit: "tablet" },
    { name: "Amoxicillin 500mg", stock: 30, min: 100, unit: "kapsul" },
    { name: "Vitamin C 1000mg", stock: 25, min: 50, unit: "tablet" },
    { name: "Omeprazole 20mg", stock: 40, min: 80, unit: "kapsul" },
  ];

  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
      return;
    }
    setLoading(false);
  }, [router]);

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-700",
      processing: "bg-blue-100 text-blue-700",
      completed: "bg-green-100 text-green-700",
    };
    const labels: Record<string, string> = {
      pending: "Menunggu",
      processing: "Diproses",
      completed: "Selesai",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">
            Dashboard
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Farmasi</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Pill className="h-6 w-6 mr-2 text-teal-600" />
          Dashboard Farmasi
        </h1>
        <p className="text-gray-600 mt-1">Kelola resep dan inventori obat</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Aksi Cepat</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {quickActions.map((action) => (
              <Link
                key={action.href}
                href={action.href}
                className="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:border-teal-500 hover:bg-teal-50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <action.icon className="h-5 w-5 text-teal-600" />
                  <span className="font-medium text-gray-900">{action.label}</span>
                </div>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Prescriptions */}
        <Card>
          <CardHeader>
            <CardTitle>Resep Terbaru</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentPrescriptions.map((rx) => (
                <div key={rx.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{rx.id}</p>
                    <p className="text-sm text-gray-500">{rx.patient} - {rx.doctor}</p>
                  </div>
                  <div className="text-right">
                    {getStatusBadge(rx.status)}
                    <p className="text-xs text-gray-400 mt-1">{rx.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Low Stock Alert */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-red-600">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Peringatan Stok Rendah
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {lowStockItems.map((item) => (
                <div key={item.name} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{item.name}</p>
                    <p className="text-sm text-red-600">
                      Stok: {item.stock} {item.unit} (Min: {item.min})
                    </p>
                  </div>
                  <Button variant="secondary" size="sm">
                    Pesan
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
