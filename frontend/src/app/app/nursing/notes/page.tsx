"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FileText,
  Search,
  ChevronRight,
  Plus,
  Clock,
  User,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface NursingNote {
  id: string;
  patientName: string;
  mrn: string;
  room: string;
  noteType: string;
  content: string;
  nurseName: string;
  createdAt: string;
}

export default function NursingNotesPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState<NursingNote[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showNewNoteModal, setShowNewNoteModal] = useState(false);

  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setNotes([
        { id: "NOTE-001", patientName: "Ahmad Susanto", mrn: "MRN-001", room: "A-101", noteType: "Asuhan Keperawatan", content: "Pasien dalam kondisi stabil, tidak ada keluhan. Tanda vital dalam batas normal. Pasien kooperatif.", nurseName: "Siti Nurhaliza", createdAt: "2026-02-27 10:30:00" },
        { id: "NOTE-002", patientName: "Siti Rahayu", mrn: "MRN-002", room: "B-205", noteType: "Perkembangan", content: "Pasien melaporkan nyeri di area luka operasi skala 4/10. Diberikan analgesik sesuai program.", nurseName: "Dewi Lestari", createdAt: "2026-02-27 09:45:00" },
        { id: "NOTE-003", patientName: "Budi Hartono", mrn: "MRN-003", room: "A-103", noteType: "Serah Terima", content: "Infus RL 20 tts/menit berjalan baik. Kateter urine produksi 300cc/6jam jernih.", nurseName: "Siti Nurhaliza", createdAt: "2026-02-27 07:00:00" },
        { id: "NOTE-004", patientName: "Dewi Sartika", mrn: "MRN-004", room: "C-301", noteType: "Edukasi", content: "Edukasi pasien tentang perawatan luka dan tanda-tanda infeksi yang perlu diwaspadai.", nurseName: "Dewi Lestari", createdAt: "2026-02-26 15:30:00" },
      ]);
    } catch (error) {
      console.error("Failed to load notes:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredNotes = notes.filter((n) =>
    n.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    n.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const noteTypes = [
    { value: "asuhan", label: "Asuhan Keperawatan" },
    { value: "perkembangan", label: "Perkembangan" },
    { value: "serah", label: "Serah Terima" },
    { value: "edukasi", label: "Edukasi" },
    { value: "tindakan", label: "Tindakan" },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/nursing" className="hover:text-gray-700">Keperawatan</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Catatan Keperawatan</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <FileText className="h-6 w-6 mr-2 text-teal-600" />
              Catatan Keperawatan
            </h1>
            <p className="text-gray-600 mt-1">Dokumentasi asuhan keperawatan pasien</p>
          </div>
          <Button variant="primary" onClick={() => setShowNewNoteModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Tambah Catatan
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
              placeholder="Cari nama pasien atau isi catatan..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>
        </CardContent>
      </Card>

      {/* Notes List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
          </div>
        ) : filteredNotes.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Tidak ada catatan ditemukan</p>
            </CardContent>
          </Card>
        ) : (
          filteredNotes.map((note) => (
            <Card key={note.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className="h-10 w-10 rounded-full bg-teal-100 flex items-center justify-center">
                      <User className="h-5 w-5 text-teal-600" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold text-gray-900">{note.patientName}</h3>
                        <span className="text-sm text-gray-500">{note.mrn}</span>
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                          {note.room}
                        </span>
                      </div>
                      <span className="inline-block mt-1 px-2 py-0.5 bg-teal-100 text-teal-700 text-xs rounded-full">
                        {note.noteType}
                      </span>
                      <p className="mt-2 text-gray-700">{note.content}</p>
                      <div className="flex items-center mt-3 text-sm text-gray-500">
                        <Clock className="h-4 w-4 mr-1" />
                        {note.createdAt} • {note.nurseName}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* New Note Modal */}
      {showNewNoteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader>
              <CardTitle>Tambah Catatan Keperawatan</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pasien</label>
                  <input
                    type="text"
                    placeholder="Cari pasien..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipe Catatan</label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500">
                    {noteTypes.map((type) => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Catatan</label>
                  <textarea
                    rows={4}
                    placeholder="Tulis catatan keperawatan..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                  ></textarea>
                </div>
                <div className="flex justify-end space-x-3">
                  <Button variant="secondary" type="button" onClick={() => setShowNewNoteModal(false)}>
                    Batal
                  </Button>
                  <Button variant="primary" type="submit">
                    Simpan
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
