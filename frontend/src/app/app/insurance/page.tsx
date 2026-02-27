"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Shield,
  Search,
  ChevronRight,
  Plus,
  Eye,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface InsuranceRecord {
  id: string;
  patientName: string;
  mrn: string;
  provider: string;
  policyNumber: string;
  type: string;
  status: "active" | "expired" | "pending";
  validUntil: string;
}

export default function InsurancePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [records, setRecords] = useState<InsuranceRecord[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadRecords();
  }, []);

  const loadRecords = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setRecords([
        { id: "INS-001", patientName: "Ahmad Susanto", mrn: "MRN-001", provider: "BPJS Kesehatan", policyNumber: "0001234567890", type: "Kelas 3", status: "active", validUntil: "2027-12-31" },
        { id: "INS-002", patientName: "Siti Rahayu", mrn: "MRN-002", provider: "Prudential", policyNumber: "PRU-2024-001234", type: "Premier", status: "active", validUntil: "2026-06-30" },
        { id: "INS-003", patientName: "Budi Hartono", mrn: "MRN-003", provider: "BPJS Kesehatan", policyNumber: "0009876543210", type: "Kelas 2", status: "expired", validUntil: "2026-01-31" },
        { id: "INS-004", patientName: "Dewi Sartika", mrn: "MRN-004", provider: "Allianz", policyNumber: "ALL-2024-567890", type: "Executive", status: "pending", validUntil: "2026-12-31" },
      ]);
    } catch (error) {
      console.error("Failed to load records:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRecords = records.filter((r) =>
    r.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.policyNumber.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      active: "bg-green-100 text-green-700",
      expired: "bg-red-100 text-red-700",
      pending: "bg-yellow-100 text-yellow-700",
    };
    const labels: Record<string, string> = {
      active: "Aktif",
      expired: "Kadaluarsa",
      pending: "Pending",
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
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Asuransi</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Shield className="h-6 w-6 mr-2 text-teal-600" />
              Manajemen Asuransi
            </h1>
            <p className="text-gray-600 mt-1">Kelola data asuransi pasien</p>
          </div>
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            Tambah Asuransi
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
              placeholder="Cari nama pasien atau nomor polis..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>
        </CardContent>
      </Card>

      {/* Records Table */}
      <Card>
        <CardHeader>
          <CardTitle>Daftar Asuransi ({filteredRecords.length})</CardTitle>
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
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Provider</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">No. Polis</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tipe</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Berlaku Sampai</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((record) => (
                    <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div>
                          <p className="font-medium text-gray-900">{record.patientName}</p>
                          <p className="text-sm text-gray-500">{record.mrn}</p>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600">{record.provider}</td>
                      <td className="py-3 px-4 font-mono text-sm text-gray-600">{record.policyNumber}</td>
                      <td className="py-3 px-4 text-gray-600">{record.type}</td>
                      <td className="py-3 px-4 text-gray-600">{record.validUntil}</td>
                      <td className="py-3 px-4">{getStatusBadge(record.status)}</td>
                      <td className="py-3 px-4 text-right">
                        <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                          <Eye className="h-4 w-4" />
                        </button>
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
