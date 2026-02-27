"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Activity,
  Search,
  ChevronRight,
  Plus,
  Heart,
  Thermometer,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface VitalsRecord {
  id: string;
  mrn: string;
  patientName: string;
  timestamp: string;
  bloodPressure: string;
  heartRate: number;
  temperature: number;
  respiratoryRate: number;
  oxygenSaturation: number;
  weight: number;
  height: number;
  nurse: string;
}

export default function VitalsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [records, setRecords] = useState<VitalsRecord[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadVitals();
  }, []);

  const loadVitals = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setRecords([
        { id: "1", mrn: "MRN-001", patientName: "Ahmad Susanto", timestamp: "2026-02-27 10:30:00", bloodPressure: "120/80", heartRate: 72, temperature: 36.5, respiratoryRate: 16, oxygenSaturation: 98, weight: 70, height: 175, nurse: "Siti N." },
        { id: "2", mrn: "MRN-002", patientName: "Siti Rahayu", timestamp: "2026-02-27 10:15:00", bloodPressure: "130/85", heartRate: 80, temperature: 36.8, respiratoryRate: 18, oxygenSaturation: 97, weight: 55, height: 160, nurse: "Dewi L." },
        { id: "3", mrn: "MRN-003", patientName: "Budi Hartono", timestamp: "2026-02-27 09:45:00", bloodPressure: "140/90", heartRate: 88, temperature: 37.2, respiratoryRate: 20, oxygenSaturation: 95, weight: 80, height: 170, nurse: "Siti N." },
        { id: "4", mrn: "MRN-004", patientName: "Dewi Sartika", timestamp: "2026-02-27 09:30:00", bloodPressure: "110/70", heartRate: 68, temperature: 36.3, respiratoryRate: 14, oxygenSaturation: 99, weight: 50, height: 158, nurse: "Dewi L." },
      ]);
    } catch (error) {
      console.error("Failed to load vitals:", error);
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
          <span className="text-gray-900">Tanda Vital</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Activity className="h-6 w-6 mr-2 text-teal-600" />
              Pencatatan Tanda Vital
            </h1>
            <p className="text-gray-600 mt-1">Rekam dan pantau tanda vital pasien</p>
          </div>
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            Catat Vital Baru
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
              placeholder="Cari nama pasien atau MRN..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>
        </CardContent>
      </Card>

      {/* Vitals Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredRecords.map((record) => (
          <Card key={record.id}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-semibold text-gray-900">{record.patientName}</p>
                  <p className="text-sm text-gray-500">{record.mrn}</p>
                </div>
                <p className="text-xs text-gray-400">{record.timestamp}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Heart className="h-4 w-4 text-red-500" />
                  <div>
                    <p className="text-xs text-gray-500">TD</p>
                    <p className="font-medium text-gray-900">{record.bloodPressure}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-blue-500" />
                  <div>
                    <p className="text-xs text-gray-500">Nadi</p>
                    <p className="font-medium text-gray-900">{record.heartRate} bpm</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Thermometer className="h-4 w-4 text-orange-500" />
                  <div>
                    <p className="text-xs text-gray-500">Suhu</p>
                    <p className="font-medium text-gray-900">{record.temperature}°C</p>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-gray-500">SpO2</p>
                  <p className="font-medium text-gray-900">{record.oxygenSaturation}%</p>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t text-sm text-gray-500">
                Oleh: {record.nurse}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
