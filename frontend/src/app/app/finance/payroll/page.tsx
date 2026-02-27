"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Receipt,
  Search,
  ChevronRight,
  Filter,
  Download,
  CheckCircle,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface PayrollRecord {
  id: string;
  employeeName: string;
  employeeId: string;
  department: string;
  position: string;
  basicSalary: number;
  allowances: number;
  deductions: number;
  netSalary: number;
  status: "pending" | "processed" | "paid";
  period: string;
}

export default function PayrollPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [records, setRecords] = useState<PayrollRecord[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    loadPayroll();
  }, []);

  const loadPayroll = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setRecords([
        { id: "PAY-001", employeeName: "Dr. Ahmad Susanto", employeeId: "EMP-001", department: "Poli Umum", position: "Dokter Spesialis", basicSalary: 25000000, allowances: 5000000, deductions: 500000, netSalary: 29500000, status: "paid", period: "2026-02" },
        { id: "PAY-002", employeeName: "Siti Nurhaliza", employeeId: "EMP-002", department: "IGD", position: "Perawat", basicSalary: 8000000, allowances: 1500000, deductions: 200000, netSalary: 9300000, status: "paid", period: "2026-02" },
        { id: "PAY-003", employeeName: "Budi Santoso", employeeId: "EMP-003", department: "Farmasi", position: "Farmasis", basicSalary: 10000000, allowances: 2000000, deductions: 250000, netSalary: 11750000, status: "processed", period: "2026-02" },
        { id: "PAY-004", employeeName: "Dewi Lestari", employeeId: "EMP-004", department: "Kasir", position: "Staff Billing", basicSalary: 6000000, allowances: 1000000, deductions: 150000, netSalary: 6850000, status: "processed", period: "2026-02" },
        { id: "PAY-005", employeeName: "Eko Prasetyo", employeeId: "EMP-005", department: "Lab", position: "Teknisi Lab", basicSalary: 9000000, allowances: 1500000, deductions: 200000, netSalary: 10300000, status: "pending", period: "2026-02" },
      ]);
    } catch (error) {
      console.error("Failed to load payroll:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRecords = records.filter((r) => {
    const matchesSearch = r.employeeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.employeeId.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || r.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-700",
      processed: "bg-blue-100 text-blue-700",
      paid: "bg-green-100 text-green-700",
    };
    const labels: Record<string, string> = {
      pending: "Menunggu",
      processed: "Diproses",
      paid: "Dibayar",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const totalPayroll = filteredRecords.reduce((sum, r) => sum + r.netSalary, 0);

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
          <span className="text-gray-900">Penggajian</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Receipt className="h-6 w-6 mr-2 text-teal-600" />
              Penggajian
            </h1>
            <p className="text-gray-600 mt-1">Kelola penggajian karyawan</p>
          </div>
          <div className="flex space-x-2">
            <Button variant="secondary">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="primary">
              Proses Gaji
            </Button>
          </div>
        </div>
      </div>

      {/* Summary Card */}
      <Card className="bg-gradient-to-r from-teal-500 to-teal-600 text-white">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-teal-100">Total Penggajian Bulan Ini</p>
              <p className="text-3xl font-bold">Rp {totalPayroll.toLocaleString()}</p>
            </div>
            <Receipt className="h-12 w-12 text-teal-200" />
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari nama atau ID karyawan..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">Semua Status</option>
              <option value="pending">Menunggu</option>
              <option value="processed">Diproses</option>
              <option value="paid">Dibayar</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Payroll Table */}
      <Card>
        <CardHeader>
          <CardTitle>Daftar Gaji - Periode Februari 2026</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Karyawan</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Departemen</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Gaji Pokok</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Tunjangan</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Potongan</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Gaji Bersih</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((record) => (
                  <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium text-gray-900">{record.employeeName}</p>
                        <p className="text-sm text-gray-500">{record.employeeId} - {record.position}</p>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-600">{record.department}</td>
                    <td className="py-3 px-4 text-right text-gray-600">Rp {record.basicSalary.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right text-green-600">+ Rp {record.allowances.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right text-red-600">- Rp {record.deductions.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right font-medium text-gray-900">Rp {record.netSalary.toLocaleString()}</td>
                    <td className="py-3 px-4">{getStatusBadge(record.status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
