"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  TestTube,
  Search,
  ChevronRight,
  Plus,
  Eye,
  Printer,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface LabOrder {
  id: string;
  patientName: string;
  mrn: string;
  doctorName: string;
  tests: string[];
  status: "ordered" | "collected" | "processing" | "completed";
  orderDate: string;
  priority: "routine" | "urgent" | "stat";
}

export default function LabOrdersPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [orders, setOrders] = useState<LabOrder[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setOrders([
        { id: "LAB-001", patientName: "Ahmad Susanto", mrn: "MRN-001", doctorName: "Dr. Budi Santoso", tests: ["Darah Lengkap", "Gula Darah"], status: "completed", orderDate: "2026-02-27 08:00", priority: "routine" },
        { id: "LAB-002", patientName: "Siti Rahayu", mrn: "MRN-002", doctorName: "Dr. Dewi Lestari", tests: ["Urine Lengkap"], status: "processing", orderDate: "2026-02-27 09:30", priority: "routine" },
        { id: "LAB-003", patientName: "Budi Hartono", mrn: "MRN-003", doctorName: "Dr. Ahmad Yusuf", tests: ["Kolesterol", "Trigliserida", "SGOT", "SGPT"], status: "collected", orderDate: "2026-02-27 10:00", priority: "urgent" },
        { id: "LAB-004", patientName: "Dewi Sartika", mrn: "MRN-004", doctorName: "Dr. Siti Nurhaliza", tests: ["HbA1c", "Ureum", "Kreatinin"], status: "ordered", orderDate: "2026-02-27 10:30", priority: "stat" },
      ]);
    } catch (error) {
      console.error("Failed to load orders:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredOrders = orders.filter((o) =>
    o.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      ordered: "bg-gray-100 text-gray-700",
      collected: "bg-blue-100 text-blue-700",
      processing: "bg-yellow-100 text-yellow-700",
      completed: "bg-green-100 text-green-700",
    };
    const labels: Record<string, string> = {
      ordered: "Dipesan",
      collected: "Sample Diambil",
      processing: "Diproses",
      completed: "Selesai",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      routine: "bg-gray-50 text-gray-600",
      urgent: "bg-orange-100 text-orange-700",
      stat: "bg-red-100 text-red-700",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[priority]}`}>
        {priority.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/lab" className="hover:text-gray-700">Laboratorium</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Pemesanan</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <TestTube className="h-6 w-6 mr-2 text-teal-600" />
              Pemesanan Lab
            </h1>
            <p className="text-gray-600 mt-1">Buat dan kelola pemesanan tes laboratorium</p>
          </div>
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            Pesan Lab Baru
          </Button>
        </div>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Cari nomor order atau nama pasien..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>
        </CardContent>
      </Card>

      {/* Orders Table */}
      <Card>
        <CardHeader>
          <CardTitle>Daftar Pemesanan ({filteredOrders.length})</CardTitle>
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
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">No. Order</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Dokter</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tes</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Prioritas</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOrders.map((order) => (
                    <tr key={order.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-gray-900">{order.id}</td>
                      <td className="py-3 px-4">
                        <div>
                          <p className="text-gray-900">{order.patientName}</p>
                          <p className="text-sm text-gray-500">{order.mrn}</p>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600">{order.doctorName}</td>
                      <td className="py-3 px-4 text-gray-600">{order.tests.join(", ")}</td>
                      <td className="py-3 px-4">{getPriorityBadge(order.priority)}</td>
                      <td className="py-3 px-4">{getStatusBadge(order.status)}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Eye className="h-4 w-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Printer className="h-4 w-4" />
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
