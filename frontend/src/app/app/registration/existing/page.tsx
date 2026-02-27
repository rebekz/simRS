"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Search,
  ChevronRight,
  User,
  Phone,
  Calendar,
  MapPin,
  CreditCard,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface Patient {
  id: string;
  mrn: string;
  fullName: string;
  nik: string;
  dateOfBirth: string;
  gender: string;
  phone: string;
  address: string;
  bpjsNumber: string | null;
  lastVisit: string;
}

export default function ExistingPatientPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState("mrn");
  const [results, setResults] = useState<Patient[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setHasSearched(true);

    try {
      // Simulate search
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setResults([
        {
          id: "1",
          mrn: "MRN-001",
          fullName: "Ahmad Susanto",
          nik: "3171234567890001",
          dateOfBirth: "1985-05-15",
          gender: "Laki-laki",
          phone: "+62 812-1234-5678",
          address: "Jl. Sudirman No. 123, Jakarta Selatan",
          bpjsNumber: "0001234567890",
          lastVisit: "2026-02-20",
        },
        {
          id: "2",
          mrn: "MRN-002",
          fullName: "Siti Rahayu",
          nik: "3171234567890002",
          dateOfBirth: "1990-08-22",
          gender: "Perempuan",
          phone: "+62 812-2345-6789",
          address: "Jl. Gatot Subroto No. 45, Jakarta Pusat",
          bpjsNumber: "0009876543210",
          lastVisit: "2026-02-25",
        },
      ]);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPatient = (patient: Patient) => {
    // Navigate to registration with patient data
    router.push(`/app/registration/check-in?mrn=${patient.mrn}`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/registration" className="hover:text-gray-700">Registrasi</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Pasien Lama</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Cari Pasien Terdaftar</h1>
        <p className="text-gray-600 mt-1">Cari pasien yang sudah terdaftar untuk check-in kunjungan</p>
      </div>

      {/* Search Card */}
      <Card>
        <CardHeader>
          <CardTitle>Cari Pasien</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 w-full md:w-48"
              >
                <option value="mrn">No. MRN</option>
                <option value="nik">NIK</option>
                <option value="name">Nama Pasien</option>
                <option value="bpjs">No. BPJS</option>
                <option value="phone">No. Telepon</option>
              </select>
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder={
                    searchType === "mrn" ? "Masukkan nomor MRN..." :
                    searchType === "nik" ? "Masukkan NIK 16 digit..." :
                    searchType === "name" ? "Masukkan nama pasien..." :
                    searchType === "bpjs" ? "Masukkan nomor BPJS..." :
                    "Masukkan nomor telepon..."
                  }
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <Button variant="primary" onClick={handleSearch} disabled={loading}>
                {loading ? "Mencari..." : "Cari"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search Results */}
      {hasSearched && (
        <Card>
          <CardHeader>
            <CardTitle>Hasil Pencarian ({results.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-8">
                <User className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Tidak ada pasien yang ditemukan</p>
                <Link href="/app/registration/new-patient" className="text-teal-600 hover:underline mt-2 inline-block">
                  Daftarkan pasien baru
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {results.map((patient) => (
                  <div
                    key={patient.id}
                    className="p-4 border border-gray-200 rounded-lg hover:border-teal-500 hover:bg-teal-50 cursor-pointer transition-colors"
                    onClick={() => handleSelectPatient(patient)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4">
                        <div className="h-12 w-12 rounded-full bg-teal-100 flex items-center justify-center">
                          <User className="h-6 w-6 text-teal-600" />
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <h3 className="font-semibold text-gray-900">{patient.fullName}</h3>
                            <span className="px-2 py-0.5 bg-teal-100 text-teal-700 text-xs rounded-full">
                              {patient.mrn}
                            </span>
                          </div>
                          <div className="mt-2 space-y-1">
                            <div className="flex items-center text-sm text-gray-600">
                              <Calendar className="h-4 w-4 mr-2" />
                              {patient.dateOfBirth} • {patient.gender}
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <Phone className="h-4 w-4 mr-2" />
                              {patient.phone}
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <MapPin className="h-4 w-4 mr-2" />
                              {patient.address}
                            </div>
                            {patient.bpjsNumber && (
                              <div className="flex items-center text-sm text-gray-600">
                                <CreditCard className="h-4 w-4 mr-2" />
                                BPJS: {patient.bpjsNumber}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">Kunjungan terakhir</p>
                        <p className="font-medium text-gray-900">{patient.lastVisit}</p>
                        <Button variant="primary" size="sm" className="mt-2">
                          Check-in
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
