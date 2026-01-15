"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import {
  FileText,
  Bold,
  Italic,
  List,
  ListOrdered,
  Save,
  Clock,
  Type,
  User,
  PenTool,
  CheckCircle,
  AlertCircle,
  RotateCcw,
  File
} from "lucide-react";

/**
 * WEB-S-4.2: SOAP Notes Editor
 *
 * Key Features:
 * - SOAP sections (Subjective, Objective, Assessment, Plan)
 * - Auto-save every 30 seconds with debouncing
 * - Templates for common cases (UMUM, DEMAM, BATUK)
 * - Rich text formatting (bold, italic, lists)
 * - Character counter for each section
 * - Digital signature required to finalize
 * - Version control with audit trail
 */

// ============================================================================
// TYPES
// ============================================================================

export interface SOAPData {
  subjective: string;
  objective: string;
  assessment: string;
  assessmentCodes: string[]; // ICD-10 codes
  plan: string;
}

export interface SOAPNote {
  id: string;
  encounterId: string;
  patientId: string;
  doctorId: string;
  doctorName: string;
  data: SOAPData;
  status: "draft" | "signed";
  version: number;
  createdAt: Date;
  updatedAt: Date;
  lastSavedAt?: Date;
  signedAt?: Date;
}

export interface SOAPTemplate {
  id: string;
  name: string;
  category: "UMUM" | "DEMAM" | "BATUK" | "NYERI" | "SESAK";
  data: Partial<SOAPData>;
}

export interface SOAPVersion {
  version: number;
  timestamp: Date;
  doctor: string;
  changes: string;
}

// ============================================================================
// TEMPLATES
// ============================================================================

const SOAP_TEMPLATES: SOAPTemplate[] = [
  {
    id: "umum-1",
    name: "Pemeriksaan Umum",
    category: "UMUM",
    data: {
      subjective: "Pasien datang dengan keluhan utama [isi keluhan]. Keluhan ini sudah dirasakan selama [durasi]. Pasien mengeluh [keluhan tambahan]. Tidak ada keluhan [lainnya].",
      objective: "Keadaan umum: compos mentis, kesadaran baik, vital sign stabil.\n\nInspeksi: [hasil pemeriksaan fisik].\n\nPenunjang: [hasil lab/radiologi jika ada].",
      assessment: "[Diagnosis sementara kerja]\n\nDD: [diagnosis diferensial]",
      plan: "1. [Tatalaksana]\n2. [Edukasi pasien]\n3. Kontrol [tanggal]",
    },
  },
  {
    id: "demam-1",
    name: "Demam",
    category: "DEMAM",
    data: {
      subjective: "Pasien datang dengan keluhan demam sejak [durasi]. Demam [tingkat demam]. Diukur suhu tubuh [suhu maksimal]. Pasien mengeluh [gejala tambahan: menggigil, sakit kepala, nyeri otot, dll]. Tidak ada [gejala berbahaya lainnya].",
      objective: "Keadaan umum: [kondisi pasien].\n\nVital sign: TD [nilai], HR [nilai], RR [nilai], Temp [nilai], SpO2 [nilai]%\n\nInspeksi: [pemeriksaan fisik terkait demam - tenggorokan, kelenjar, dll].",
      assessment: "Diagnosis kerja:\n- Demam [tipe demam]\n- DD: [diagnosis diferensial]\n\nTriage: [Merah/Kuning/Hijau]",
      plan: "1. [Tatalaksana demam]\n2. [Obat penurun demam/analgesik]\n3. [Tindak lanjut jika perlu]\n4. Edukasi: [pantauan suhu, minum, istirahat]\n5. Kontrol [kondisi]",
    },
  },
  {
    id: "batuk-1",
    name: "Batuk",
    category: "BATUK",
    data: {
      subjective: "Pasien datang dengan keluhan batuk sejak [durasi]. Batuk berupa [jenis: kering/berdahak/berlendir]. Pasien mengeluh [gejala tambahan: sesak, nyeri dada, demam, dll]. Batuk [worse/better] pada [waktu/hari]. Riwayat [kontak/penyakit sebelumnya].",
      objective: "Keadaan umum: [kondisi pasien]\n\nVital sign: TD [nilai], HR [nilai], RR [nilai], Temp [nilai], SpO2 [nilai]%, Au [nilai]%\n\nInspeksi thorak: [hasil auskultasi/inspeksi/perkusi]\n\nPenunjang: [CXR/lab jika ada]",
      assessment: "Diagnosis kerja:\n- [Diagnosis primair]\n- DD: [diagnosis diferensial]\n\nTriage: [Merah/Kuning/Hijau]",
      plan: "1. [Tatalaksana batuk]\n2. [Obat-obatan: mucolytic, bronchodilator, dll]\n3. [Nebulisasi jika perlu]\n4. Edukasi: [cara batuk efektif, minum, hindari pemicu]\n5. Kontrol [kondisi]",
    },
  },
];

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

interface SOAPSectionProps {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  maxLength?: number;
}

function SOAPSection({ label, placeholder, value, onChange, required = false, maxLength = 5000 }: SOAPSectionProps) {
  const charCount = value.length;
  const charPercent = (charCount / (maxLength || 1)) * 100;

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Section Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">{label}</h3>
          <div className="flex items-center gap-2">
            <span className={`text-xs ${charPercent > 90 ? "text-red-600" : charPercent > 75 ? "text-yellow-600" : "text-gray-500"}`}>
              {charCount}/{maxLength}
            </span>
          </div>
        </div>
      </div>

      {/* Section Content */}
      <div className="p-4">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          maxLength={maxLength}
          rows={8}
          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y"
          required={required}
        />
      </div>
    </div>
  );
}

interface AssessmentSectionProps {
  value: string;
  codes: string[];
  onChange: (value: string) => void;
  onCodesChange: (codes: string[]) => void;
}

function AssessmentSection({ value, codes, onChange, onCodesChange }: AssessmentSectionProps) {
  const [showICD10Search, setShowICD10Search] = useState(false);

  const removeCode = (codeToRemove: string) => {
    onCodesChange(codes.filter((c) => c !== codeToRemove));
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Section Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">Assessment (A)</h3>
      </div>

      {/* Section Content */}
      <div className="p-4 space-y-3">
        {/* Free Text Assessment */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Deskripsi Assessment
          </label>
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Diagnosa sementara dan diagnosis diferensial"
            rows={4}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y"
          />
          <div className="flex justify-between mt-1">
            <span className="text-xs text-gray-500">{value.length} karakter</span>
          </div>
        </div>

        {/* ICD-10 Codes */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-medium text-gray-700">
              Kode ICD-10
            </label>
            <button
              type="button"
              onClick={() => setShowICD10Search(!showICD10Search)}
              className="text-xs text-blue-600 hover:text-blue-700"
            >
              {showICD10Search ? "Tutup" : "+ Tambah"}
            </button>
          </div>

          {/* Selected Codes */}
          {codes.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-2">
              {codes.map((code) => (
                <span
                  key={code}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md border border-blue-200"
                >
                  {code}
                  <button
                    type="button"
                    onClick={() => removeCode(code)}
                    className="hover:text-blue-900"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}

          {/* Simple ICD-10 Input */}
          {showICD10Search && (
            <div className="border border-gray-300 rounded-lg p-2 bg-gray-50">
              <input
                type="text"
                placeholder="Ketik kode atau nama diagnosa (contoh: J00, Influenza, Demam)..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-2"
                autoFocus
              />
              <div className="space-y-1">
                <button
                  type="button"
                  onClick={() => {
                    onCodesChange([...codes, "J00 - Influenza"]);
                    setShowICD10Search(false);
                  }}
                  className="w-full text-left px-3 py-2 text-xs hover:bg-blue-100 rounded"
                >
                  J00 - Influenza
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onCodesChange([...codes, "A01 - Tifus"]);
                    setShowICD10Search(false);
                  }}
                  className="w-full text-left px-3 py-2 text-xs hover:bg-blue-100 rounded"
                >
                  A01 - Tifoid dan Paratifoid
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onCodesChange([...codes, "I10 - Hipertensi Esensial"]);
                    setShowICD10Search(false);
                  }}
                  className="w-full text-left px-3 py-2 text-xs hover:bg-blue-100 rounded"
                >
                  I10 - Hipertensi Esensial
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

interface SOAPNotesEditorProps {
  encounterId: string;
  patientId: string;
  doctorId: string;
  doctorName: string;
  initialData?: Partial<SOAPData>;
  onSave?: (data: SOAPData) => Promise<void>;
  onSign?: (data: SOAPData) => Promise<void>;
  existingNote?: SOAPNote;
  versions?: SOAPVersion[];
}

export function SOAPNotesEditor({
  encounterId,
  patientId,
  doctorId,
  doctorName,
  initialData,
  onSave,
  onSign,
  existingNote,
  versions = [],
}: SOAPNotesEditorProps) {
  // SOAP data state
  const [subjective, setSubjective] = useState(initialData?.subjective || existingNote?.data.subjective || "");
  const [objective, setObjective] = useState(initialData?.objective || existingNote?.data.objective || "");
  const [assessment, setAssessment] = useState(initialData?.assessment || existingNote?.data.assessment || "");
  const [assessmentCodes, setAssessmentCodes] = useState<string[]>(initialData?.assessmentCodes || existingNote?.data.assessmentCodes || []);
  const [plan, setPlan] = useState(initialData?.plan || existingNote?.data.plan || "");

  // UI state
  const [isSaving, setIsSaving] = useState(false);
  const [isSigning, setIsSigning] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | undefined>(existingNote?.lastSavedAt);
  const [activeTemplate, setActiveTemplate] = useState<string | null>(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [signatureDialog, setSignatureDialog] = useState(false);

  // Auto-save effect (every 30 seconds)
  useEffect(() => {
    const interval = setInterval(() => {
      if (hasUnsavedChanges) {
        autoSave();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [subjective, objective, assessment, assessmentCodes, plan]);

  // Check if there are unsaved changes
  const hasUnsavedChanges =
    subjective !== (existingNote?.data.subjective || "") ||
    objective !== (existingNote?.data.objective || "") ||
    assessment !== (existingNote?.data.assessment || "") ||
    JSON.stringify(assessmentCodes) !== JSON.stringify(existingNote?.data.assessmentCodes || []) ||
    plan !== (existingNote?.data.plan || "");

  /**
   * Auto-save function (debounced)
   */
  const autoSave = useCallback(async () => {
    if (!onSave) return;

    setSaveStatus("saving");
    setIsSaving(true);

    try {
      await onSave({
        subjective,
        objective,
        assessment,
        assessmentCodes,
        plan,
      });
      setLastSaved(new Date());
      setSaveStatus("saved");
    } catch (error) {
      console.error("Auto-save error:", error);
      setSaveStatus("error");
    } finally {
      setIsSaving(false);
    }
  }, [subjective, objective, assessment, assessmentCodes, plan, onSave]);

  /**
   * Load template
   */
  const loadTemplate = useCallback((templateId: string) => {
    const template = SOAP_TEMPLATES.find((t) => t.id === templateId);
    if (!template) return;

    if (template.data.subjective) setSubjective(template.data.subjective);
    if (template.data.objective) setObjective(template.data.objective);
    if (template.data.assessment) setAssessment(template.data.assessment);
    if (template.data.plan) setPlan(template.data.plan);

    setActiveTemplate(templateId);
    setShowTemplates(false);
  }, []);

  /**
   * Save draft
   */
  const handleSaveDraft = async () => {
    if (!onSave) return;

    setIsSaving(true);
    setSaveStatus("saving");

    try {
      await onSave({
        subjective,
        objective,
        assessment,
        assessmentCodes,
        plan,
      });
      setLastSaved(new Date());
      setSaveStatus("saved");
    } catch (error) {
      console.error("Save error:", error);
      setSaveStatus("error");
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Sign SOAP note
   */
  const handleSignSOAP = async () => {
    setSignatureDialog(true);
  };

  const confirmSignature = async () => {
    if (!onSign) return;

    setIsSigning(true);
    setSignatureDialog(false);

    try {
      await onSign({
        subjective,
        objective,
        assessment,
        assessmentCodes,
        plan,
      });
      setSaveStatus("saved");
    } catch (error) {
      console.error("Signature error:", error);
      setSaveStatus("error");
    } finally {
      setIsSigning(false);
    }
  };

  /**
   * Format text (simple rich text)
   * Note: assessmentCodes is excluded since it's an array, not text
   */
  const formatText = useCallback((section: keyof Pick<SOAPData, "subjective" | "objective" | "assessment" | "plan">, type: "bold" | "italic" | "list") => {
    const setters: Record<keyof Pick<SOAPData, "subjective" | "objective" | "assessment" | "plan">, (val: string) => void> = {
      subjective: setSubjective,
      objective: setObjective,
      assessment: setAssessment,
      plan: setPlan,
    };

    const currentText = { subjective, objective, assessment, plan }[section];
    if (!currentText) return;

    let formatted = "";

    switch (type) {
      case "bold":
        formatted = `**${currentText}**`;
        break;
      case "italic":
        formatted = `_${currentText}_`;
        break;
      case "list":
        formatted = currentText.split("\n").map((line) => `• ${line}`).join("\n");
        break;
    }

    setters[section](formatted);
  }, [subjective, objective, assessment, plan]);

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* Title */}
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">SOAP Notes</h2>
            {existingNote?.status === "signed" && (
              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Signed
              </span>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {/* Last Saved */}
            {lastSaved && (
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                <span>Tersimpan {lastSaved.toLocaleTimeString("id-ID")}</span>
              </div>
            )}

            {/* Save Status */}
            {saveStatus === "saving" && (
              <div className="flex items-center gap-1 text-xs text-blue-600">
                <RotateCcw className="w-3 h-3 animate-spin" />
                <span>Menyimpan...</span>
              </div>
            )}
            {saveStatus === "saved" && (
              <div className="flex items-center gap-1 text-xs text-green-600">
                <CheckCircle className="w-3 h-3" />
                <span>Tersimpan</span>
              </div>
            )}

            {/* Versions Button */}
            {versions.length > 0 && (
              <button
                type="button"
                onClick={() => setShowVersions(!showVersions)}
                className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-700 hover:text-gray-900 border border-gray-300 rounded hover:bg-gray-50"
              >
                <File className="w-3 h-3" />
                {versions.length} versi
              </button>
            )}

            {/* Save Draft */}
            <button
              type="button"
              onClick={handleSaveDraft}
              disabled={isSaving || existingNote?.status === "signed"}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-700 hover:text-gray-900 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-3 h-3" />
              Simpan Draft
            </button>

            {/* Sign Button */}
            {existingNote?.status !== "signed" && (
              <button
                type="button"
                onClick={handleSignSOAP}
                disabled={isSigning}
                className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PenTool className="w-3 h-3" />
                {isSigning ? "Menandatangani..." : "Tandatangan & Simpan"}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Templates Bar */}
      {existingNote?.status !== "signed" && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-gray-700">Template Cepat</span>
            <button
              type="button"
              onClick={() => setShowTemplates(!showTemplates)}
              className="text-xs text-blue-600 hover:text-blue-700"
            >
              {showTemplates ? "Tutup" : "Lihat Semua"}
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {SOAP_TEMPLATES.slice(0, showTemplates ? undefined : 3).map((template) => (
              <button
                key={template.id}
                type="button"
                onClick={() => loadTemplate(template.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
                  activeTemplate === template.id
                    ? "bg-blue-600 text-white border-blue-600"
                    : "text-gray-700 bg-white border-gray-300 hover:bg-gray-50"
                }`}
              >
                {template.category}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* SOAP Sections */}
      <div className="space-y-4">
        <SOAPSection
          label="Subjective (S)"
          placeholder="Keluhan pasien menurut pasien sendiri..."
          value={subjective}
          onChange={setSubjective}
          maxLength={5000}
        />

        <SOAPSection
          label="Objective (O)"
          placeholder="Pemeriksaan fisik dan penunjang..."
          value={objective}
          onChange={setObjective}
          maxLength={5000}
        />

        <AssessmentSection
          value={assessment}
          codes={assessmentCodes}
          onChange={setAssessment}
          onCodesChange={setAssessmentCodes}
        />

        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          {/* Section Header with Rich Text Tools */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-900">Plan (P)</h3>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => formatText("plan", "bold")}
                  className="p-1.5 hover:bg-gray-100 rounded"
                  title="Bold"
                  disabled={existingNote?.status === "signed"}
                >
                  <Bold className="w-3 h-3 text-gray-600" />
                </button>
                <button
                  type="button"
                  onClick={() => formatText("plan", "italic")}
                  className="p-1.5 hover:bg-gray-100 rounded"
                  title="Italic"
                  disabled={existingNote?.status === "signed"}
                >
                  <Italic className="w-3 h-3 text-gray-600" />
                </button>
                <button
                  type="button"
                  onClick={() => formatText("plan", "list")}
                  className="p-1.5 hover:bg-gray-100 rounded"
                  title="Bullet List"
                  disabled={existingNote?.status === "signed"}
                >
                  <List className="w-3 h-3 text-gray-600" />
                </button>
              </div>
            </div>
          </div>

          {/* Section Content */}
          <div className="p-4">
            <textarea
              value={plan}
              onChange={(e) => setPlan(e.target.value)}
              placeholder="Rencana tatalaksana..."
              rows={8}
              maxLength={5000}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y"
              disabled={existingNote?.status === "signed"}
            />
            <div className="flex justify-between mt-1">
              <span className="text-xs text-gray-500">{plan.length}/5000 karakter</span>
            </div>
          </div>
        </div>
      </div>

      {/* Version History Panel */}
      {showVersions && versions.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Riwayat Versi</h3>
          <div className="space-y-2">
            {versions.map((version) => (
              <div key={version.version} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">
                  v{version.version}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <User className="w-3 h-3 text-gray-500" />
                    <span className="text-xs font-medium text-gray-900">{version.doctor}</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{version.changes}</p>
                  <p className="text-xs text-gray-500">
                    {version.timestamp.toLocaleString("id-ID")}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Signature Confirmation Dialog */}
      {signatureDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
                <PenTool className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Konfirmasi Tanda Tangan</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Dokumen akan ditandatangani secara elektronik dan tidak dapat diubah setelah ini.
                </p>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-yellow-800">
                  Pastikan semua data SOAP sudah benar. Tanda tangan digital menyatakan bahwa Anda telah menyelesaikan dan memverifikasi catatan klinis ini.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setSignatureDialog(false)}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                type="button"
                onClick={confirmSignature}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg"
              >
                Ya, Tandatangani
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// DEMO PAGE
// ============================================================================

const DEMO_VERSIONS: SOAPVersion[] = [
  {
    version: 1,
    timestamp: new Date("2026-01-16T08:00:00"),
    doctor: "dr. Ahmad Sp.PD",
    changes: "Versi awal",
  },
  {
    version: 2,
    timestamp: new Date("2026-01-16T10:30:00"),
    doctor: "dr. Ahmad Sp.PD",
    changes: "Menambah diagnosa ICD-10: J00",
  },
];

export function SOAPNotesEditorDemo() {
  const handleSave = async (data: SOAPData) => {
    console.log("Saving SOAP:", data);
    await new Promise((resolve) => setTimeout(resolve, 1000));
  };

  const handleSign = async (data: SOAPData) => {
    console.log("Signing SOAP:", data);
    await new Promise((resolve) => setTimeout(resolve, 1500));
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">SOAP Notes Editor Demo</h1>
        <p className="text-gray-600 mt-2">Demo halaman editor SOAP notes dengan auto-save, template, dan tanda tangan digital.</p>
      </div>

      <SOAPNotesEditor
        encounterId="ENC-001"
        patientId="PAT-001"
        doctorId="DOC-001"
        doctorName="dr. Ahmad Sp.PD"
        onSave={handleSave}
        onSign={handleSign}
        versions={DEMO_VERSIONS}
      />
    </div>
  );
}
