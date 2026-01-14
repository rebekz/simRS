"use client";

/**
 * SOAP Note Editor Component for STORY-015
 *
 * Provides SOAP note template with:
 * - Auto-save every 30 seconds
 * - Digital signature support
 * - Version control with audit trail
 * - Structured SOAP sections
 */

import { useState, useEffect, useCallback } from "react";
import { Save, FileText, Clock, AlertCircle, CheckCircle, Edit3 } from "lucide-react";

// Types
interface SOAPNote {
  id?: number;
  patient_id: number;
  encounter_id?: number;
  note_date: string;
  title: string;
  subjective?: string;
  objective?: string;
  assessment?: string;
  plan?: string;
  status: "draft" | "pending" | "signed" | "amended";
  version: number;
  is_amendment: boolean;
}

interface SOAPNoteEditorProps {
  patientId: number;
  encounterId?: number;
  initialNote?: SOAPNote;
  onSave?: (note: SOAPNote) => void;
  onSign?: (noteId: number) => void;
}

export function SOAPNoteEditor({
  patientId,
  encounterId,
  initialNote,
  onSave,
  onSign,
}: SOAPNoteEditorProps) {
  const [note, setNote] = useState<SOAPNote>(
    initialNote || {
      patient_id: patientId,
      encounter_id: encounterId,
      note_date: new Date().toISOString(),
      title: "Catatan SOAP",
      status: "draft",
      version: 1,
      is_amendment: false,
    }
  );

  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);

  // Auto-save every 30 seconds
  useEffect(() => {
    if (!autoSaveEnabled || !hasChanges || note.status !== "draft") {
      return;
    }

    const timer = setInterval(() => {
      handleAutoSave();
    }, 30000);

    return () => clearInterval(timer);
  }, [note, hasChanges, autoSaveEnabled]);

  const handleAutoSave = async () => {
    if (isSaving || !hasChanges) return;

    setIsSaving(true);
    try {
      const response = await fetch("/api/v1/clinical-notes/autosave", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          ...note,
          note_type: "soap",
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setLastSaved(new Date());
        setHasChanges(false);

        // Update note ID if new note
        if (!note.id && data.note_id) {
          setNote((prev) => ({ ...prev, id: data.note_id }));
        }
      }
    } catch (error) {
      console.error("Auto-save failed:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleManualSave = async () => {
    setIsSaving(true);
    try {
      const url = note.id
        ? `/api/v1/clinical-notes/${note.id}`
        : "/api/v1/clinical-notes";
      const method = note.id ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          ...note,
          note_type: "soap",
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setLastSaved(new Date());
        setHasChanges(false);
        onSave?.(data);
      }
    } catch (error) {
      console.error("Save failed:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSign = async () => {
    if (!note.id) {
      alert("Harap simpan catatan terlebih dahulu");
      return;
    }

    if (hasChanges) {
      if (!confirm("Ada perubahan yang belum disimpan. Lanjutkan tanda tangan?")) {
        return;
      }
    }

    try {
      const response = await fetch(`/api/v1/clinical-notes/${note.id}/sign`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.ok) {
        setNote((prev) => ({ ...prev, status: "signed" }));
        onSign?.(note.id!);
        alert("Catatan berhasil ditandatangani secara digital");
      }
    } catch (error) {
      console.error("Sign failed:", error);
      alert("Gagal menandatangani catatan");
    }
  };

  const handleFieldChange = (field: keyof SOAPNote, value: string) => {
    setNote((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const getStatusBadge = () => {
    switch (note.status) {
      case "draft":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            <Edit3 className="h-3 w-3 mr-1" />
            Draft
          </span>
        );
      case "signed":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3 mr-1" />
            Ditandatangani
          </span>
        );
      case "amended":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <AlertCircle className="h-3 w-3 mr-1" />
            Diamendemen
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <FileText className="h-6 w-6 mr-2" />
              Catatan SOAP
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Pasien ID: {patientId}
              {note.encounter_id && ` • Kunjungan: ${note.encounter_id}`}
            </p>
          </div>
          {getStatusBadge()}
        </div>

        <div className="flex items-center space-x-3">
          {/* Auto-save indicator */}
          <div className="flex items-center text-xs text-gray-500">
            <Clock className="h-4 w-4 mr-1" />
            {isSaving ? (
              <span>Menyimpan...</span>
            ) : lastSaved ? (
              <span>Tersimpan {lastSaved.toLocaleTimeString()}</span>
            ) : (
              <span>Belum disimpan</span>
            )}
          </div>

          {/* Auto-save toggle */}
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={autoSaveEnabled}
              onChange={(e) => setAutoSaveEnabled(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="ml-2 text-sm text-gray-700">Auto-save (30s)</span>
          </label>

          {/* Save button */}
          <button
            onClick={handleManualSave}
            disabled={!hasChanges || isSaving || note.status === "signed"}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? "Menyimpan..." : "Simpan"}
          </button>

          {/* Sign button */}
          {note.status === "draft" && note.id && (
            <button
              onClick={handleSign}
              disabled={hasChanges}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Tanda Tangan Digital
            </button>
          )}
        </div>
      </div>

      {/* Warning for unsaved changes */}
      {hasChanges && note.status === "signed" && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-yellow-400 mr-2" />
            <div className="text-sm text-yellow-700">
              Catatan ini sudah ditandatangani. Perubahan perlu diamendemen.
            </div>
          </div>
        </div>
      )}

      {/* Title */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Judul Catatan
        </label>
        <input
          type="text"
          value={note.title}
          onChange={(e) => handleFieldChange("title", e.target.value)}
          disabled={note.status === "signed"}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
          placeholder="Judul catatan"
        />
      </div>

      {/* SOAP Sections */}
      <div className="space-y-6">
        {/* Subjective */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-blue-600 font-bold">S</span> - Subjektif
            <span className="text-gray-500 font-normal ml-2">
              (Keluhan pasien, gejala, riwayat penyakit)
            </span>
          </label>
          <textarea
            value={note.subjective || ""}
            onChange={(e) => handleFieldChange("subjective", e.target.value)}
            disabled={note.status === "signed"}
            rows={4}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Pasien mengeluh..."
          />
        </div>

        {/* Objective */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-blue-600 font-bold">O</span> - Objektif
            <span className="text-gray-500 font-normal ml-2">
              (Pemeriksaan fisik, tanda vital, hasil lab)
            </span>
          </label>
          <textarea
            value={note.objective || ""}
            onChange={(e) => handleFieldChange("objective", e.target.value)}
            disabled={note.status === "signed"}
            rows={4}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Pada pemeriksaan fisik didapatkan..."
          />
        </div>

        {/* Assessment */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-blue-600 font-bold">A</span> - Asesmen
            <span className="text-gray-500 font-normal ml-2">
              (Diagnosis, kesan klinis, analisis)
            </span>
          </label>
          <textarea
            value={note.assessment || ""}
            onChange={(e) => handleFieldChange("assessment", e.target.value)}
            disabled={note.status === "signed"}
            rows={4}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Berdasarkan pemeriksaan, diduga..."
          />
        </div>

        {/* Plan */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-blue-600 font-bold">P</span> - Rencana
            <span className="text-gray-500 font-normal ml-2">
              (Rencana penatalaksanaan, tatalaksana, follow-up)
            </span>
          </label>
          <textarea
            value={note.plan || ""}
            onChange={(e) => handleFieldChange("plan", e.target.value)}
            disabled={note.status === "signed"}
            rows={4}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Rencana penatalaksanaan..."
          />
        </div>
      </div>

      {/* Version info */}
      {note.is_amendment && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-400 mr-2" />
            <div className="text-sm text-blue-700">
              Ini adalah amandemen versi {note.version}. Catatan asli tetap tersimpan.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
