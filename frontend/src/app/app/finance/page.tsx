"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  CreditCard,
  Receipt,
  PieChart,
  ChevronRight,
  Calendar,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function FinanceDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  const stats = [
    { label: "Pendapatan Bulan Ini", value: "Rp 1.250.000.000", change: "+12%", icon: TrendingUp, positive: true },
    { label: "Pengeluaran Bulan Ini", value: "Rp 450.000.000", change: "+5%", icon: TrendingDown, positive: false },
    { label: "Piutang BPJS", value: "Rp 320.000.000", change: "-8%", icon: CreditCard, positive: true },
    { label: "Kas Hari Ini", value: "Rp 85.000.000", change: "+15%", icon: DollarSign, positive: true },
  ];

  const revenueByDepartment = [
    { name: "Poli Umum", value: 250000000, percentage: 20 },
    { name: "IGD", value: 187500000, percentage: 15 },
    { name: "Rawat Inap", value: 437500000, percentage: 35 },
    { name: "Laboratorium", value: 125000000, percentage: 10 },
    { name: "Radiologi", value: 100000000, percentage: 8 },
    { name: "Farmasi", value: 150000000, percentage: 12 },
  ];

  const recentTransactions = [
    { id: "TRX-001", type: "income", desc: "Pembayaran Pasien - Ahmad S.", amount: 1250000, time: "10:30" },
    { id: "TRX-002", type: "income", desc: "Claim BPJS - Siti R.", amount: 2500000, time: "10:15" },
    { id: "TRX-003", type: "expense", desc: "Pembelian Alkes", amount: 5000000, time: "09:45" },
    { id: "TRX-004", type: "income", desc: "Pembayaran Pasien - Budi H.", amount: 850000, time: "09:30" },
    { id: "TRX-005", type: "expense", desc: "Gaji Karyawan", amount: 150000000, time: "08:00" },
  ];

  const quickActions = [
    { label: "Laporan Keuangan", href: "/app/finance/reports", icon: PieChart },
    { label: "Penggajian", href: "/app/finance/payroll", icon: Receipt },
  ];

  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
      return;
    }
    setLoading(false);
  }, [router]);

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
          <span className="text-gray-900">Keuangan</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <DollarSign className="h-6 w-6 mr-2 text-teal-600" />
          Dashboard Keuangan
        </h1>
        <p className="text-gray-600 mt-1">Monitoring dan laporan keuangan rumah sakit</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                  <p className="text-xl font-bold text-gray-900">{stat.value}</p>
                  <p className={`text-sm mt-1 ${stat.positive ? "text-green-600" : "text-red-600"}`}>
                    {stat.change} dari bulan lalu
                  </p>
                </div>
                <stat.icon className={`h-8 w-8 ${stat.positive ? "text-green-600" : "text-red-600"}`} />
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
        {/* Revenue by Department */}
        <Card>
          <CardHeader>
            <CardTitle>Pendapatan per Departemen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {revenueByDepartment.map((dept) => (
                <div key={dept.name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600">{dept.name}</span>
                    <span className="text-sm font-medium text-gray-900">
                      Rp {(dept.value / 1000000).toFixed(0)} jt ({dept.percentage}%)
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-teal-600 rounded-full"
                      style={{ width: `${dept.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Transaksi Terbaru</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentTransactions.map((trx) => (
                <div key={trx.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${trx.type === "income" ? "bg-green-100" : "bg-red-100"}`}>
                      {trx.type === "income" ? (
                        <TrendingUp className="h-4 w-4 text-green-600" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-600" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{trx.desc}</p>
                      <p className="text-xs text-gray-500">{trx.id} - {trx.time}</p>
                    </div>
                  </div>
                  <span className={`font-medium ${trx.type === "income" ? "text-green-600" : "text-red-600"}`}>
                    {trx.type === "income" ? "+" : "-"} Rp {trx.amount.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
