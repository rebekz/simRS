"use client";

/**
 * Clinical Notes List Component for STORY-015: Clinical Notes (SOAP)
 *
 * Displays patient clinical notes with filtering, search, and actions.
 * Integrates with SOAP note editor for creating/editing notes.
 */

import { useState, useEffect } from "react";
import { Plus, FileText, Edit, Eye, Calendar, User, Filter } from "lucide-react";
import { SOAPNoteEditor } from "./SOAPNoteEditor";

interface ClinicalNote {
  id: number;
  uuid: string;
  patient_id: number;
  encounter_id?: number;
  note_type: string;
  title: string;
  note_date: string;
  subjective?: string;
  objective?: string;
  assessment?: string;
  plan?: string;
  content?: string;
  status: "draft" | "pending" | "signed" | "amended";
  version: number;
  is_amendment: boolean;
  author_id: number;
  author_name?: string;
  signed_by_id?: number;
  signed_at?: string;
  created_at: string;
  updated_at: string;
}

interface ClinicalNotesListProps {
  patientId: number;
  encounterId?: number;
}

export function ClinicalNotesList({ patientId, encounterId }: ClinicalNotesListProps) {
  const [notes, setNotes] = useState<ClinicalNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEditor, setShowEditor] = useState(false);
  const [selectedNote, setSelectedNote] = useState<ClinicalNote | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [filterType, setFilterType] = useState<string>("");

  useEffect(() => {
    fetchNotes();
  }, [patientId, filterStatus, filterType]);

  const fetchNotes = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.append("status_filter", filterStatus);
      if (filterType) params.append("note_type_filter", filterType);

      const response = await fetch(
        `/api/v1/clinical-notes/patient/${patientId}${params.toString() ? "?" + params.toString() : ""}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("staff_access_token")}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setNotes(data.notes || []);
      }
    } catch (error) {
      console.error("Failed to fetch clinical notes:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "draft":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            Draft
          </span>
        );
      case "signed":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Signed
          </span>
        );
      case "amended":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            Amended
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {status}
          </span>
        );
    }
  };

  const getNoteTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      soap: "bg-blue-100 text-blue-800",
      admission: "bg-purple-100 text-purple-800",
      progress: "bg-green-100 text-green-800",
      discharge: "bg-orange-100 text-orange-800",
      consultation: "bg-pink-100 text-pink-800",
    };

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[type] || "bg-gray-100 text-gray-800"}`}>
        {type.toUpperCase()}
      </span>
    );
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleCreateNote = () => {
    setSelectedNote(null);
    setShowEditor(true);
  };

  const handleEditNote = (note: ClinicalNote) => {
    if (note.status === "signed") {
      alert("Catatan yang sudah ditandatangani tidak dapat diedit. Buat amandemen jika perlu mengubah.");
      return;
    }
    setSelectedNote(note);
    setShowEditor(true);
  };

  const handleViewNote = (note: ClinicalNote) => {
    setSelectedNote(note);
    setShowEditor(true);
  };

  if (showEditor) {
    return (
      <SOAPNoteEditor
        patientId={patientId}
        encounterId={encounterId}
        initialNote={selectedNote || undefined}
        onSave={() => {
          setShowEditor(false);
          fetchNotes();
        }}
        onSign={(noteId) => {
          setShowEditor(false);
          fetchNotes();
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            Catatan Klinis
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Total {notes.length} catatan
          </p>
        </div>
        <button
          onClick={handleCreateNote}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Buat Catatan Baru
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <Filter className="h-5 w-5 text-gray-400" />
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua</option>
              <option value="draft">Draft</option>
              <option value="signed">Signed</option>
              <option value="amended">Amended</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Tipe:</span>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua</option>
              <option value="soap">SOAP</option>
              <option value="admission">Admission</option>
              <option value="progress">Progress</option>
              <option value="discharge">Discharge</option>
              <option value="consultation">Consultation</option>
            </select>
          </div>
        </div>
      </div>

      {/* Notes List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : notes.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Tidak ada catatan</h3>
          <p className="mt-1 text-sm text-gray-500">
            Belum ada catatan klinis untuk pasien ini.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {notes.map((note) => (
            <div
              key={note.id}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
            >
              {/* Note Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{note.title}</h3>
                    {getNoteTypeBadge(note.note_type)}
                    {getStatusBadge(note.status)}
                    {note.is_amendment && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        v{note.version}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1" />
                      {formatDate(note.note_date)}
                    </div>
                    <div className="flex items-center">
                      <User className="h-4 w-4 mr-1" />
                      {note.author_name || "Unknown"}
                    </div>
                    {note.signed_at && (
                      <div className="text-green-600">
                        ✓ Signed {formatDate(note.signed_at)}
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleViewNote(note)}
                    className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                    title="View"
                  >
                    <Eye className="h-5 w-5" />
                  </button>
                  {note.status === "draft" && (
                    <button
                      onClick={() => handleEditNote(note)}
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                      title="Edit"
                    >
                      <Edit className="h-5 w-5" />
                    </button>
                  )}
                </div>
              </div>

              {/* Note Content Preview */}
              {note.note_type === "soap" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  {note.subjective && (
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="font-medium text-blue-900 mb-1">S - Subjektif</p>
                      <p className="text-blue-800 line-clamp-3">{note.subjective}</p>
                    </div>
                  )}
                  {note.objective && (
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="font-medium text-green-900 mb-1">O - Objektif</p>
                      <p className="text-green-800 line-clamp-3">{note.objective}</p>
                    </div>
                  )}
                  {note.assessment && (
                    <div className="bg-yellow-50 p-3 rounded-lg">
                      <p className="font-medium text-yellow-900 mb-1">A - Asesmen</p>
                      <p className="text-yellow-800 line-clamp-3">{note.assessment}</p>
                    </div>
                  )}
                  {note.plan && (
                    <div className="bg-purple-50 p-3 rounded-lg">
                      <p className="font-medium text-purple-900 mb-1">P - Rencana</p>
                      <p className="text-purple-800 line-clamp-3">{note.plan}</p>
                    </div>
                  )}
                </div>
              )}

              {note.content && note.note_type !== "soap" && (
                <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 line-clamp-3">
                  {note.content}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
