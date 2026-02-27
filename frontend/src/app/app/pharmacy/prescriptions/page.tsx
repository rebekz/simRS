"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FileText,
  Search,
  Filter,
  ChevronRight,
  Eye,
  CheckCircle,
  Clock,
  Pill,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface Prescription {
  id: string;
  patientName: string;
  patientMrn: string;
  doctorName: string;
  department: string;
  items: number;
  status: "pending" | "processing" | "completed" | "cancelled";
  createdAt: string;
}

export default function PharmacyPrescriptionsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    loadPrescriptions();
  }, []);

  const loadPrescriptions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setPrescriptions([
        {
          id: "RX-2026-0227-001",
          patientName: "Ahmad Susanto",
          patientMrn: "MRN-001",
          doctorName: "Dr. Budi Santoso",
          department: "Poli Umum",
          items: 3,
          status: "pending",
          createdAt: "2026-02-27 10:30:00",
        },
        {
          id: "RX-2026-0227-002",
          patientName: "Siti Rahayu",
          patientMrn: "MRN-002",
          doctorName: "Dr. Dewi Lestari",
          department: "Poli Jantung",
          items: 2,
          status: "processing",
          createdAt: "2026-02-27 10:15:00",
        },
        {
          id: "RX-2026-0227-003",
          patientName: "Budi Hartono",
          patientMrn: "MRN-003",
          doctorName: "Dr. Ahmad Yusuf",
          department: "Poli Anak",
          items: 4,
          status: "completed",
          createdAt: "2026-02-27 09:45:00",
        },
        {
          id: "RX-2026-0227-004",
          patientName: "Dewi Sartika",
          patientMrn: "MRN-004",
          doctorName: "Dr. Siti Nurhaliza",
          department: "Poli Kandungan",
          items: 1,
          status: "completed",
          createdAt: "2026-02-27 09:30:00",
        },
        {
          id: "RX-2026-0227-005",
          patientName: "Eko Prasetyo",
          patientMrn: "MRN-005",
          doctorName: "Dr. Budi Santoso",
          department: "Poli Umum",
          items: 2,
          status: "cancelled",
          createdAt: "2026-02-27 09:00:00",
        },
      ]);
    } catch (error) {
      console.error("Failed to load prescriptions:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredPrescriptions = prescriptions.filter((rx) => {
    const matchesSearch =
      rx.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rx.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rx.patientMrn.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || rx.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-700",
      processing: "bg-blue-100 text-blue-700",
      completed: "bg-green-100 text-green-700",
      cancelled: "bg-red-100 text-red-700",
    };
    const labels: Record<string, string> = {
      pending: "Menunggu",
      processing: "Diproses",
      completed: "Selesai",
      cancelled: "Dibatalkan",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
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
          <Link href="/app/pharmacy" className="hover:text-gray-700">
            Farmasi
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Resep</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Pill className="h-6 w-6 mr-2 text-teal-600" />
          Daftar Resep
        </h1>
        <p className="text-gray-600 mt-1">Kelola dan proses resep dokter</p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari nomor resep, nama pasien, atau MRN..."
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
              <option value="processing">Diproses</option>
              <option value="completed">Selesai</option>
              <option value="cancelled">Dibatalkan</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Prescriptions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Daftar Resep ({filteredPrescriptions.length})</CardTitle>
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
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">No. Resep</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Dokter</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Departemen</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Items</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Waktu</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredPrescriptions.map((rx) => (
                    <tr key={rx.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-gray-900">{rx.id}</td>
                      <td className="py-3 px-4">
                        <div>
                          <p className="text-gray-900">{rx.patientName}</p>
                          <p className="text-sm text-gray-500">{rx.patientMrn}</p>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600">{rx.doctorName}</td>
                      <td className="py-3 px-4 text-gray-600">{rx.department}</td>
                      <td className="py-3 px-4 text-gray-600">{rx.items} obat</td>
                      <td className="py-3 px-4">{getStatusBadge(rx.status)}</td>
                      <td className="py-3 px-4 text-sm text-gray-500">{rx.createdAt}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Eye className="h-4 w-4" />
                          </button>
                          {rx.status === "pending" && (
                            <button className="p-2 text-gray-400 hover:text-blue-600 rounded-md hover:bg-blue-50">
                              <CheckCircle className="h-4 w-4" />
                            </button>
                          )}
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
