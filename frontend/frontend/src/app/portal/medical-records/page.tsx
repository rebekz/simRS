"use client";

import { useState } from "react";
import Link from "next/link";
import { FileText, ChevronRight, Search, Download, Eye } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function PortalMedicalRecordsPage() {
  const [searchQuery, setSearchQuery] = useState("");

  const records = [
    { id: "1", date: "2026-02-20", type: "Rawat Jalan", doctor: "Dr. Ahmad Yusuf", diagnosis: "Flu", summary: "Pemeriksaan normal, obat simptomatik" },
    { id: "2", date: "2026-02-15", type: "IGD", doctor: "Dr. Emergency", diagnosis: "Luka Sayat", summary: "Penjahitan luka" },
    { id: "3", date: "2026-01-10", type: "Rawat Jalan", doctor: "Dr. Siti Rahayu", diagnosis: "Hipertensi", summary: "Kontrol rutin" },
  ];

  const filteredRecords = records.filter((r) =>
    r.diagnosis.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/portal/dashboard">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Rekam Medis</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Rekam Medis</h1>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Cari diagnosa..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {filteredRecords.map((record) => (
          <Card key={record.id}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <FileText className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">{record.type}</span>
                    <p className="text-sm text-gray-500">{record.date}</p>
                    <h3 className="font-semibold text-gray-900 mt-1">{record.diagnosis}</h3>
                    <p className="text-sm text-gray-500">{record.doctor}</p>
                    <p className="text-gray-600 mt-2">{record.summary}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="secondary" size="sm"><Eye className="h-4 w-4 mr-1" />Lihat</Button>
                  <Button variant="secondary" size="sm"><Download className="h-4 w-4 mr-1" />Unduh</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
