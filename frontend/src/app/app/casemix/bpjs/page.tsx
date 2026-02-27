"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  CreditCard,
  Search,
  ChevronRight,
  Send,
  Eye,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface BPJSClaim {
  id: string;
  sepNumber: string;
  patientName: string;
  mrn: string;
  admissionDate: string;
  dischargeDate: string;
  diagnosis: string;
  cbgCode: string;
  tarif: number;
  status: "draft" | "submitted" | "approved" | "rejected";
}

export default function CasemixBPJSPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [claims, setClaims] = useState<BPJSClaim[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    loadClaims();
  }, []);

  const loadClaims = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setClaims([
        { id: "BPJS-001", sepNumber: "0301R0010226V000001", patientName: "Ahmad Susanto", mrn: "MRN-001", admissionDate: "2026-02-25", dischargeDate: "2026-02-27", diagnosis: "Pneumonia", cbgCode: "A-1-1-I", tarif: 2500000, status: "approved" },
        { id: "BPJS-002", sepNumber: "0301R0010226V000002", patientName: "Siti Rahayu", mrn: "MRN-002", admissionDate: "2026-02-26", dischargeDate: "2026-02-27", diagnosis: "Hipertensi", cbgCode: "B-2-2-II", tarif: 1800000, status: "submitted" },
        { id: "BPJS-003", sepNumber: "0301R0010226V000003", patientName: "Budi Hartono", mrn: "MRN-003", admissionDate: "2026-02-27", dischargeDate: null, diagnosis: "Diabetes Mellitus", cbgCode: "C-3-1-I", tarif: 0, status: "draft" },
        { id: "BPJS-004", sepNumber: "0301R0010226V000004", patientName: "Dewi Lestari", mrn: "MRN-004", admissionDate: "2026-02-24", dischargeDate: "2026-02-26", diagnosis: "Fraktur Femur", cbgCode: "D-4-2-III", tarif: 8500000, status: "rejected" },
      ]);
    } catch (error) {
      console.error("Failed to load claims:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredClaims = claims.filter((c) => {
    const matchesSearch = c.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.sepNumber.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      draft: "bg-gray-100 text-gray-700",
      submitted: "bg-blue-100 text-blue-700",
      approved: "bg-green-100 text-green-700",
      rejected: "bg-red-100 text-red-700",
    };
    const labels: Record<string, string> = {
      draft: "Draft",
      submitted: "Terkirim",
      approved: "Disetujui",
      rejected: "Ditolak",
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
          <Link href="/app/casemix" className="hover:text-gray-700">Casemix</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Klaim BPJS</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <CreditCard className="h-6 w-6 mr-2 text-teal-600" />
              Klaim BPJS
            </h1>
            <p className="text-gray-600 mt-1">Submit dan tracking klaim BPJS Kesehatan</p>
          </div>
          <Button variant="primary">
            <RefreshCw className="h-4 w-4 mr-2" />
            Sync SEP
          </Button>
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
                placeholder="Cari SEP atau nama pasien..."
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
              <option value="draft">Draft</option>
              <option value="submitted">Terkirim</option>
              <option value="approved">Disetujui</option>
              <option value="rejected">Ditolak</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Claims Table */}
      <Card>
        <CardHeader>
          <CardTitle>Daftar Klaim ({filteredClaims.length})</CardTitle>
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
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">No. SEP</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Diagnosa</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">CBG</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Tarif</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredClaims.map((claim) => (
                    <tr key={claim.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-sm text-gray-600">{claim.sepNumber}</td>
                      <td className="py-3 px-4">
                        <div>
                          <p className="font-medium text-gray-900">{claim.patientName}</p>
                          <p className="text-sm text-gray-500">{claim.mrn}</p>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600">{claim.diagnosis}</td>
                      <td className="py-3 px-4 font-mono text-gray-600">{claim.cbgCode}</td>
                      <td className="py-3 px-4 text-right text-gray-600">
                        {claim.tarif > 0 ? `Rp ${claim.tarif.toLocaleString()}` : "-"}
                      </td>
                      <td className="py-3 px-4">{getStatusBadge(claim.status)}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Eye className="h-4 w-4" />
                          </button>
                          {claim.status === "draft" && (
                            <button className="p-2 text-gray-400 hover:text-blue-600 rounded-md hover:bg-blue-50">
                              <Send className="h-4 w-4" />
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
