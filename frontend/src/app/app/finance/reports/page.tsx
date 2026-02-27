"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  PieChart,
  FileText,
  Download,
  ChevronRight,
  Calendar,
  Filter,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function FinanceReportsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [reportType, setReportType] = useState("daily");
  const [dateRange, setDateRange] = useState("today");

  const reports = [
    { id: "RPT-001", name: "Laporan Harian Kas", type: "daily", date: "2026-02-27", status: "ready" },
    { id: "RPT-002", name: "Laporan Pendapatan Bulanan", type: "monthly", date: "2026-02", status: "ready" },
    { id: "RPT-003", name: "Laporan Piutang BPJS", type: "bpjs", date: "2026-02-27", status: "ready" },
    { id: "RPT-004", name: "Laporan Laba Rugi", type: "profit", date: "2026-02", status: "processing" },
    { id: "RPT-005", name: "Laporan Neraca", type: "balance", date: "2026-02", status: "ready" },
    { id: "RPT-006", name: "Laporan Arus Kas", type: "cashflow", date: "2026-02", status: "ready" },
  ];

  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
      return;
    }
    setLoading(false);
  }, [router]);

  const filteredReports = reports.filter((r) => {
    if (reportType === "all") return true;
    return r.type === reportType;
  });

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      ready: "bg-green-100 text-green-700",
      processing: "bg-yellow-100 text-yellow-700",
    };
    const labels: Record<string, string> = {
      ready: "Siap",
      processing: "Diproses",
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
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/finance" className="hover:text-gray-700">Keuangan</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Laporan</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <PieChart className="h-6 w-6 mr-2 text-teal-600" />
          Laporan Keuangan
        </h1>
        <p className="text-gray-600 mt-1">Generate dan unduh laporan keuangan</p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">Semua Jenis</option>
              <option value="daily">Harian</option>
              <option value="monthly">Bulanan</option>
              <option value="bpjs">BPJS</option>
              <option value="profit">Laba Rugi</option>
              <option value="balance">Neraca</option>
              <option value="cashflow">Arus Kas</option>
            </select>
            <Button variant="primary">
              <FileText className="h-4 w-4 mr-2" />
              Generate Laporan Baru
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredReports.map((report) => (
          <Card key={report.id}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 bg-teal-100 rounded-lg">
                  <FileText className="h-6 w-6 text-teal-600" />
                </div>
                {getStatusBadge(report.status)}
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">{report.name}</h3>
              <p className="text-sm text-gray-500 mb-4">Periode: {report.date}</p>
              <div className="flex space-x-2">
                <Button variant="secondary" size="sm" className="flex-1" disabled={report.status !== "ready"}>
                  <Download className="h-4 w-4 mr-1" />
                  PDF
                </Button>
                <Button variant="secondary" size="sm" className="flex-1" disabled={report.status !== "ready"}>
                  <Download className="h-4 w-4 mr-1" />
                  Excel
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
