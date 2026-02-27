"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Receipt,
  Search,
  ChevronRight,
  Plus,
  Eye,
  Printer,
  Download,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface Invoice {
  id: string;
  patientName: string;
  mrn: string;
  date: string;
  items: number;
  subtotal: number;
  discount: number;
  total: number;
  status: "unpaid" | "partial" | "paid" | "cancelled";
  paymentMethod: string;
}

export default function BillingInvoicesPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setInvoices([
        { id: "INV-2026-0227-001", patientName: "Ahmad Susanto", mrn: "MRN-001", date: "2026-02-27", items: 5, subtotal: 1500000, discount: 0, total: 1500000, status: "paid", paymentMethod: "Tunai" },
        { id: "INV-2026-0227-002", patientName: "Siti Rahayu", mrn: "MRN-002", date: "2026-02-27", items: 8, subtotal: 3200000, discount: 320000, total: 2880000, status: "paid", paymentMethod: "BPJS" },
        { id: "INV-2026-0227-003", patientName: "Budi Hartono", mrn: "MRN-003", date: "2026-02-27", items: 3, subtotal: 850000, discount: 0, total: 850000, status: "unpaid", paymentMethod: "-" },
        { id: "INV-2026-0227-004", patientName: "Dewi Sartika", mrn: "MRN-004", date: "2026-02-26", items: 6, subtotal: 2100000, discount: 105000, total: 1995000, status: "partial", paymentMethod: "Tunai" },
        { id: "INV-2026-0227-005", patientName: "Eko Prasetyo", mrn: "MRN-005", date: "2026-02-26", items: 4, subtotal: 1200000, discount: 0, total: 1200000, status: "cancelled", paymentMethod: "-" },
      ]);
    } catch (error) {
      console.error("Failed to load invoices:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredInvoices = invoices.filter((inv) => {
    const matchesSearch = inv.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || inv.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      unpaid: "bg-red-100 text-red-700",
      partial: "bg-yellow-100 text-yellow-700",
      paid: "bg-green-100 text-green-700",
      cancelled: "bg-gray-100 text-gray-700",
    };
    const labels: Record<string, string> = {
      unpaid: "Belum Bayar",
      partial: "Sebagian",
      paid: "Lunas",
      cancelled: "Dibatalkan",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const totalRevenue = filteredInvoices
    .filter((inv) => inv.status === "paid")
    .reduce((sum, inv) => sum + inv.total, 0);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/billing" className="hover:text-gray-700">Billing</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Invoice</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Receipt className="h-6 w-6 mr-2 text-teal-600" />
              Manajemen Invoice
            </h1>
            <p className="text-gray-600 mt-1">Kelola faktur dan pembayaran pasien</p>
          </div>
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            Buat Invoice
          </Button>
        </div>
      </div>

      {/* Summary */}
      <Card className="bg-gradient-to-r from-teal-500 to-teal-600 text-white">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-teal-100">Total Pendapatan Hari Ini</p>
              <p className="text-3xl font-bold">Rp {totalRevenue.toLocaleString()}</p>
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
                placeholder="Cari nomor invoice atau nama pasien..."
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
              <option value="unpaid">Belum Bayar</option>
              <option value="partial">Sebagian</option>
              <option value="paid">Lunas</option>
              <option value="cancelled">Dibatalkan</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Invoices Table */}
      <Card>
        <CardHeader>
          <CardTitle>Daftar Invoice ({filteredInvoices.length})</CardTitle>
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
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">No. Invoice</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tanggal</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Total</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Metode Bayar</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredInvoices.map((invoice) => (
                    <tr key={invoice.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-gray-900">{invoice.id}</td>
                      <td className="py-3 px-4">
                        <div>
                          <p className="text-gray-900">{invoice.patientName}</p>
                          <p className="text-sm text-gray-500">{invoice.mrn}</p>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600">{invoice.date}</td>
                      <td className="py-3 px-4 text-right font-medium text-gray-900">
                        Rp {invoice.total.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-gray-600">{invoice.paymentMethod}</td>
                      <td className="py-3 px-4">{getStatusBadge(invoice.status)}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Eye className="h-4 w-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Printer className="h-4 w-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Download className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
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
