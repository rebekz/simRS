"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FolderOpen,
  Search,
  ChevronRight,
  Eye,
  Download,
  Printer,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface MedicalRecord {
  id: string;
  mrn: string;
  patientName: string;
  dateOfBirth: string;
  gender: string;
  lastVisit: string;
  diagnosis: string;
  doctor: string;
}

export default function MedicalRecordsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [records, setRecords] = useState<MedicalRecord[]>([]);
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
        { id: "1", mrn: "MRN-001", patientName: "Ahmad Susanto", dateOfBirth: "1985-05-15", gender: "Laki-laki", lastVisit: "2026-02-27", diagnosis: "Hipertensi", doctor: "Dr. Budi Santoso" },
        { id: "2", mrn: "MRN-002", patientName: "Siti Rahayu", dateOfBirth: "1990-08-22", gender: "Perempuan", lastVisit: "2026-02-26", diagnosis: "Diabetes Mellitus", doctor: "Dr. Dewi Lestari" },
        { id: "3", mrn: "MRN-003", patientName: "Budi Hartono", dateOfBirth: "1978-03-10", gender: "Laki-laki", lastVisit: "2026-02-25", diagnosis: "Pneumonia", doctor: "Dr. Ahmad Yusuf" },
        { id: "4", mrn: "MRN-004", patientName: "Dewi Sartika", dateOfBirth: "1995-12-05", gender: "Perempuan", lastVisit: "2026-02-24", diagnosis: "Gastritis", doctor: "Dr. Siti Nurhaliza" },
        { id: "5", mrn: "MRN-005", patientName: "Eko Prasetyo", dateOfBirth: "1982-07-18", gender: "Laki-laki", lastVisit: "2026-02-23", diagnosis: "Fraktur Radius", doctor: "Dr. Budi Santoso" },
      ]);
    } catch (error) {
      console.error("Failed to load records:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRecords = records.filter((r) =>
    r.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.mrn.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Rekam Medis</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <FolderOpen className="h-6 w-6 mr-2 text-teal-600" />
          Rekam Medis
        </h1>
        <p className="text-gray-600 mt-1">Akses dan kelola rekam medis pasien</p>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Cari nama pasien atau nomor MRN..."
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
          <CardTitle>Daftar Rekam Medis ({filteredRecords.length})</CardTitle>
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
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">MRN</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Nama Pasien</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tgl Lahir</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Jenis Kelamin</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Kunjungan Terakhir</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Diagnosa Terakhir</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((record) => (
                    <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-teal-600">{record.mrn}</td>
                      <td className="py-3 px-4 font-medium text-gray-900">{record.patientName}</td>
                      <td className="py-3 px-4 text-gray-600">{record.dateOfBirth}</td>
                      <td className="py-3 px-4 text-gray-600">{record.gender}</td>
                      <td className="py-3 px-4 text-gray-600">{record.lastVisit}</td>
                      <td className="py-3 px-4 text-gray-600">{record.diagnosis}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100" title="Lihat">
                            <Eye className="h-4 w-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100" title="Cetak">
                            <Printer className="h-4 w-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100" title="Unduh">
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
