"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type {
  SurgeryConsentType,
  ConsentPatientInfo,
  SurgicalProcedureInfo,
  AnesthesiaType,
  AnesthesiaInfo,
  SurgeonInfo,
  ConsentSignature,
  ConsentWitness,
  EmergencyClassification,
  ProcedureRisk,
  ProcedureBenefit,
  AlternativeTreatment,
  ConsentRelationshipType,
} from "@/types/surgery-consent";
import {
  CONSENT_TYPES,
  SURGICAL_CATEGORIES,
  ANESTHESIA_TYPES,
  RISK_TEMPLATES,
  LEGAL_COMPLIANCE,
  CONSENT_TEMPLATES,
  COMMON_CONSTANTS,
} from "@/constants/surgery-consent";
import { SURGERY_CONSENT_TYPE_OPTIONS, ANESTHESIA_TYPE_OPTIONS } from "@/types/surgery-consent";

interface ProcedureCode {
  code: string;
  name: string;
  name_indonesian: string;
  category: string;
  description: string;
}

export default function SurgeryConsentPage() {
  const router = useRouter();

  // Form state
  const [consentType, setConsentType] = useState<SurgeryConsentType>("SURGERY");
  const [selectedPatient, setSelectedPatient] = useState<ConsentPatientInfo | null>(null);
  const [procedureName, setProcedureName] = useState("");
  const [procedureCode, setProcedureCode] = useState("");
  const [procedureDescription, setProcedureDescription] = useState("");
  const [surgicalCategory, setSurgicalCategory] = useState("");
  const [surgicalSpecialty, setSurgicalSpecialty] = useState("");
  const [plannedDate, setPlannedDate] = useState("");
  const [plannedTime, setPlannedTime] = useState("");
  const [expectedDuration, setExpectedDuration] = useState(60);
  const [alternativeTreatments, setAlternativeTreatments] = useState("");
  const [anesthesiaType, setAnesthesiaType] = useState<AnesthesiaType>("general");
  const [anesthesiaRisks, setAnesthesiaRisks] = useState("");
  const [anesthesiologistName, setAnesthesiologistName] = useState("");
  const [preAnesthesiaRequirements, setPreAnesthesiaRequirements] = useState("");
  const [generalRisks, setGeneralRisks] = useState("");
  const [procedureSpecificRisks, setProcedureSpecificRisks] = useState("");
  const [benefits, setBenefits] = useState("");
  const [consequencesOfRefusal, setConsequencesOfRefusal] = useState("");
  const [successRate, setSuccessRate] = useState(90);
  const [emergencyClassification, setEmergencyClassification] = useState<EmergencyClassification>("elective");
  const [surgeonInfo, setSurgeonInfo] = useState<SurgeonInfo | null>(null);
  const [surgeonSignature, setSurgeonSignature] = useState("");
  const [witnessName, setWitnessName] = useState("");
  const [witnessRelationship, setWitnessRelationship] = useState("");
  const [witnessSignature, setWitnessSignature] = useState("");
  const [patientConsentGiven, setPatientConsentGiven] = useState(false);
  const [patientSignature, setPatientSignature] = useState("");
  const [consentDate, setConsentDate] = useState(new Date().toISOString().split("T")[0]);
  const [consentTime, setConsentTime] = useState("");
  const [guardianName, setGuardianName] = useState("");
  const [guardianRelationship, setGuardianRelationship] = useState<ConsentRelationshipType>("guardian");
  const [guardianSignature, setGuardianSignature] = useState("");
  const [patientComments, setPatientComments] = useState("");
  const [internalNotes, setInternalNotes] = useState("");

  // Understanding checkboxes
  const [understandsProcedure, setUnderstandsProcedure] = useState(false);
  const [understandsRisks, setUnderstandsRisks] = useState(false);
  const [understandsBenefits, setUnderstandsBenefits] = useState(false);
  const [understandsAlternatives, setUnderstandsAlternatives] = useState(false);
  const [understandsConsequences, setUnderstandsConsequences] = useState(false);
  const [understandsCanWithdraw, setUnderstandsCanWithdraw] = useState(false);
  const [questionsAnswered, setQuestionsAnswered] = useState(false);
  const [consentVoluntary, setConsentVoluntary] = useState(false);

  // UI state
  const [loading, setLoading] = useState(false);
  const [searchingPatient, setSearchingPatient] = useState(false);
  const [patientSearchQuery, setPatientSearchQuery] = useState("");
  const [patientSearchResults, setPatientSearchResults] = useState<ConsentPatientInfo[]>([]);
  const [showPatientResults, setShowPatientResults] = useState(false);
  const [searchingProcedure, setSearchingProcedure] = useState(false);
  const [procedureSearchQuery, setProcedureSearchQuery] = useState("");
  const [procedureSearchResults, setProcedureSearchResults] = useState<ProcedureCode[]>([]);
  const [showProcedureResults, setShowProcedureResults] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }

    // Load current surgeon info from token
    loadSurgeonInfo();
  }, [router]);

  // Set current time
  useEffect(() => {
    const now = new Date();
    const timeString = now.toTimeString().slice(0, 5);
    setConsentTime(timeString);
  }, []);

  // Load surgeon information from JWT token
  const loadSurgeonInfo = () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      // Decode JWT (basic decode - in production, use proper JWT library)
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      );
      const payload = JSON.parse(jsonPayload);

      // Set surgeon info from token
      setSurgeonInfo({
        doctor_id: payload.id || payload.user_id || 0,
        doctor_name: payload.name || payload.full_name || "Dokter",
        doctor_title: payload.title || "dr.",
        specialization: payload.specialization || "Spesialis Bedah",
        sub_specialization: payload.sub_specialization,
        sip_number: payload.sip_number || payload.license_number || "",
        sip_issue_date: payload.sip_issue_date || "",
        sip_expiry_date: payload.sip_expiry_date || "",
        str_number: payload.str_number || "",
        hospital_id_number: payload.hospital_id,
        department: payload.department || "Bedah",
        phone: payload.phone,
        email: payload.email,
        signature_status: "pending",
      });
    } catch (err) {
      console.error("Error decoding token:", err);
    }
  };

  // Search patients
  const searchPatients = async (query: string) => {
    if (!query || query.length < 2) {
      setPatientSearchResults([]);
      setShowPatientResults(false);
      return;
    }

    setSearchingPatient(true);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch(
        `/api/v1/patients/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Gagal mencari pasien");
      }

      const data = await response.json();
      setPatientSearchResults(data.patients || []);
      setShowPatientResults(true);
    } catch (err) {
      console.error("Error searching patients:", err);
      setPatientSearchResults([]);
    } finally {
      setSearchingPatient(false);
    }
  };

  // Debounced patient search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchPatients(patientSearchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [patientSearchQuery]);

  // Search procedure codes
  const searchProcedures = async (query: string) => {
    if (!query || query.length < 2) {
      setProcedureSearchResults([]);
      setShowProcedureResults(false);
      return;
    }

    setSearchingProcedure(true);

    try {
      // Mock procedure search - in production, this would call an actual API
      const mockProcedures: ProcedureCode[] = [
        {
          code: "ICD-47.0",
          name: "Appendectomy",
          name_indonesian: "Apendisektomi",
          category: "general_surgery",
          description: "Pengangkatan usus buntu",
        },
        {
          code: "ICD-47.1",
          name: "Cholecystectomy",
          name_indonesian: "Kolesistektomi",
          category: "abdominal",
          description: "Pengangkatan kandung empedu",
        },
        {
          code: "ICD-78.1",
          name: "Open Reduction Internal Fixation",
          name_indonesian: "Fiksasi Reduksi Terbuka",
          category: "orthopedic",
          description: "Pemasangan pen untuk patah tulang",
        },
        {
          code: "ICD-81.0",
          name: "Arthroscopy",
          name_indonesian: "Artroskopi",
          category: "orthopedic",
          description: "Pemeriksaan sendi dengan kamera",
        },
        {
          code: "ICD-01.0",
          name: "Craniotomy",
          name_indonesian: "Kraniotomi",
          category: "neurosurgery",
          description: "Operasi pada otak",
        },
        {
          code: "ICD-36.0",
          name: "Hernia Repair",
          name_indonesian: "Perbaikan Hernia",
          category: "general_surgery",
          description: "Perbaikan penonjolan organ",
        },
        {
          code: "ICD-68.0",
          name: "Hysterectomy",
          name_indonesian: "Histerktomi",
          category: "gynecology",
          description: "Pengangkatan rahim",
        },
        {
          code: "ICD-85.0",
          name: "Cataract Surgery",
          name_indonesian: "Operasi Katarak",
          category: "ophthalmology",
          description: "Pengangkatan lensa keruh",
        },
      ];

      const filtered = mockProcedures.filter(
        (p) =>
          p.code.toLowerCase().includes(query.toLowerCase()) ||
          p.name.toLowerCase().includes(query.toLowerCase()) ||
          p.name_indonesian.toLowerCase().includes(query.toLowerCase())
      );

      setProcedureSearchResults(filtered);
      setShowProcedureResults(true);
    } catch (err) {
      console.error("Error searching procedures:", err);
      setProcedureSearchResults([]);
    } finally {
      setSearchingProcedure(false);
    }
  };

  // Debounced procedure search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchProcedures(procedureSearchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [procedureSearchQuery]);

  // Select patient
  const handleSelectPatient = (patient: ConsentPatientInfo) => {
    setSelectedPatient(patient);
    setShowPatientResults(false);
    setPatientSearchQuery("");
  };

  // Select procedure
  const handleSelectProcedure = (procedure: ProcedureCode) => {
    setProcedureCode(procedure.code);
    setProcedureName(procedure.name_indonesian);
    setProcedureDescription(procedure.description);
    setSurgicalCategory(procedure.category);
    setShowProcedureResults(false);
    setProcedureSearchQuery("");

    // Auto-populate risks based on category
    const categoryRisks = RISK_TEMPLATES.GENERAL_SURGICAL_RISKS;
    const riskText = categoryRisks.risks
      .map((r) => `${r.label}: ${r.description}`)
      .join("\n");
    setGeneralRisks(riskText);
  };

  // Calculate patient age
  const calculateAge = (dateOfBirth: string): number => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  // Validate form
  const validateForm = (): boolean => {
    if (!selectedPatient) {
      setError("Pilih pasien terlebih dahulu");
      return false;
    }

    if (!procedureName.trim()) {
      setError("Nama prosedur wajib diisi");
      return false;
    }

    if (!procedureDescription.trim()) {
      setError("Deskripsi prosedur wajib diisi");
      return false;
    }

    if (!plannedDate) {
      setError("Tanggal rencana tindakan wajib diisi");
      return false;
    }

    if (!plannedTime) {
      setError("Waktu rencana tindakan wajib diisi");
      return false;
    }

    if (!generalRisks.trim()) {
      setError("Risiko umum wajib diisi");
      return false;
    }

    if (!benefits.trim()) {
      setError("Manfaat tindakan wajib diisi");
      return false;
    }

    if (!consequencesOfRefusal.trim()) {
      setError("Konsekuensi penolakan wajib diisi");
      return false;
    }

    if (!understandsProcedure || !understandsRisks || !understandsBenefits ||
        !understandsAlternatives || !understandsConsequences ||
        !understandsCanWithdraw || !questionsAnswered || !consentVoluntary) {
      setError("Pasien harus menyetujui semua pernyataan pemahaman");
      return false;
    }

    if (!patientConsentGiven) {
      setError("Pasien harus memberikan persetujuan");
      return false;
    }

    if (selectedPatient.is_minor && !guardianName.trim()) {
      setError("Nama wali wajib diisi untuk pasien di bawah umur");
      return false;
    }

    if (!witnessName.trim()) {
      setError("Nama saksi wajib diisi");
      return false;
    }

    return true;
  };

  // Save consent form
  const handleSaveConsent = async (status: "draft" | "pending" = "pending") => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch("/api/v1/consents/surgery", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          consent_type: consentType,
          patient_id: selectedPatient?.patient_id,
          primary_surgeon_id: surgeonInfo?.doctor_id,
          scheduled_date: plannedDate,
          scheduled_time: plannedTime,
          emergency_classification: emergencyClassification,
          procedure_info: {
            procedure_name_id: procedureName,
            procedure_code: procedureCode,
            procedure_description_id: procedureDescription,
            surgical_category: surgicalCategory,
            surgical_approach: surgicalSpecialty,
            expected_duration_minutes: expectedDuration,
            expected_blood_loss_ml: 0,
            expected_hospital_stay_days: 0,
            is_repeat_procedure: false,
            alternative_procedures: alternativeTreatments ? alternativeTreatments.split("\n") : [],
            consequences_of_refusal: consequencesOfRefusal,
            success_rate_percentage: successRate,
            is_experimental: false,
            complexity: "intermediate",
            body_system: surgicalCategory,
          },
          anesthesia_info: {
            anesthesia_type: anesthesiaType,
            anesthesia_description_id: ANESTHESIA_TYPE_OPTIONS.find(a => a.value === anesthesiaType)?.description || "",
            anesthesiologist_id: 0,
            anesthesiologist_name: anesthesiologistName,
            anesthesiologist_license: "",
            requires_pre_assessment: preAnesthesiaRequirements.length > 0,
            pre_assessment_date: plannedDate,
            asa_classification: "ASA_I",
            requires_post_anesthesia_care: true,
          },
          risks_and_benefits: {
            common_risks: parseRisks(generalRisks),
            uncommon_risks: [],
            rare_risks: [],
            very_rare_risks: [],
            benefits: parseBenefits(benefits),
            expected_success_rate_percentage: successRate,
            alternative_treatments: parseAlternatives(alternativeTreatments),
            consequences_of_refusal: {
              expected_progression: consequencesOfRefusal,
              delay_risks: [],
              irreversible_consequences: [],
              quality_of_life_impact: consequencesOfRefusal,
            },
          },
          informed_consent_process: {
            information_provided_date: new Date().toISOString().split("T")[0],
            information_provided_time: new Date().toTimeString().slice(0, 5),
            provider_name: surgeonInfo?.doctor_name || "",
            provider_role: "Dokter Bedah",
            session_duration_minutes: 15,
            topics_discussed: [
              "Diagnosis",
              "Prosedur",
              "Risiko",
              "Manfaat",
              "Alternatif",
              "Konsekuensi penolakan",
            ],
          },
          patient_consent: {
            consent_type: consentType,
            relationship_type: selectedPatient?.is_minor ? "guardian" : "self",
            is_consent_given: patientConsentGiven,
            consent_date: consentDate,
            consent_time: consentTime,
            is_withdrawn: false,
            understands_procedure: understandsProcedure,
            understands_risks: understandsRisks,
            understands_benefits: understandsBenefits,
            understands_alternatives: understandsAlternatives,
            understands_consequences_of_refusal: understandsConsequences,
            has_opportunity_to_ask_questions: questionsAnswered,
            questions_answered_satisfactorily: questionsAnswered,
            understands_can_withdraw: understandsCanWithdraw,
            is_voluntary: consentVoluntary,
            patient_signature: {
              full_name: selectedPatient?.full_name || "",
              signature_type: "digital",
              date_signed: consentDate,
              time_signed: consentTime,
            },
            guardian_signature: selectedPatient?.is_minor ? {
              full_name: guardianName,
              relationship: guardianRelationship,
              signature_type: "digital",
              date_signed: consentDate,
              time_signed: consentTime,
            } : undefined,
          },
          witness: {
            witness_type: "healthcare_witness",
            full_name: witnessName,
            relationship: witnessRelationship,
            signature: {
              full_name: witnessName,
              signature_type: "digital",
              date_signed: consentDate,
              time_signed: consentTime,
            },
          },
          internal_notes: internalNotes,
        }),
      });

      if (!response.ok) {
        throw new Error("Gagal menyimpan formulir persetujuan");
      }

      const data = await response.json();
      setSuccessMessage(status === "draft" ? "Draft berhasil disimpan" : "Persetujuan berhasil dibuat");

      setTimeout(() => {
        router.push(`/app/consents/surgery/${data.consent_form_id}`);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan formulir persetujuan");
    } finally {
      setLoading(false);
    }
  };

  // Parse risks from text
  const parseRisks = (text: string): ProcedureRisk[] => {
    if (!text) return [];
    return text.split("\n")
      .filter(line => line.trim())
      .map((line, index) => ({
        id: index,
        category: "common",
        risk_name_id: line.split(":")[0] || line,
        risk_description_id: line.includes(":") ? line.split(":")[1] : line,
        severity: "moderate",
        is_life_threatening: false,
        probability_percentage: 5,
      }));
  };

  // Parse benefits from text
  const parseBenefits = (text: string): ProcedureBenefit[] => {
    if (!text) return [];
    return text.split("\n")
      .filter(line => line.trim())
      .map((line, index) => ({
        id: index,
        benefit_id: line.split(":")[0] || line,
        description: line.includes(":") ? line.split(":")[1] : line,
        expected_outcome: line,
      }));
  };

  // Parse alternatives from text
  const parseAlternatives = (text: string): AlternativeTreatment[] => {
    if (!text) return [];
    return text.split("\n")
      .filter(line => line.trim())
      .map((line) => ({
        treatment_name: line.split(":")[0] || line,
        description: line.includes(":") ? line.split(":")[1] : line,
        pros: [],
        cons: [],
      }));
  };

  // Download/Print consent as PDF
  const handlePrintConsent = () => {
    window.print();
  };

  // Get consent type label
  const getConsentTypeLabel = (type: SurgeryConsentType): string => {
    return SURGERY_CONSENT_TYPE_OPTIONS.find(t => t.value === type)?.label_indonesian || type;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Formulir Persetujuan Tindakan Medis</h1>
          <p className="text-gray-600 mt-1">Buat formulir informed consent untuk tindakan bedah</p>
        </div>
        <button
          onClick={() => router.push("/app/consents")}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Kembali
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <p className="text-green-800">{successMessage}</p>
        </div>
      )}

      {/* Consent Type Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">I. Jenis Persetujuan</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {SURGERY_CONSENT_TYPE_OPTIONS.map((type) => (
            <button
              key={type.value}
              onClick={() => setConsentType(type.value as SurgeryConsentType)}
              className={`p-4 border rounded-lg text-left transition-colors ${
                consentType === type.value
                  ? "border-indigo-500 bg-indigo-50"
                  : "border-gray-200 hover:bg-gray-50"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-gray-900">{type.label_indonesian}</p>
                  <p className="text-sm text-gray-600 mt-1">{type.description}</p>
                </div>
                {consentType === type.value && (
                  <svg className="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </button>
          ))}
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Klasifikasi Kondisi
          </label>
          <select
            value={emergencyClassification}
            onChange={(e) => setEmergencyClassification(e.target.value as EmergencyClassification)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="elective">Elektif (Terjadwal)</option>
            <option value="urgent">Urgent</option>
            <option value="emergency">Emergensi</option>
            <option value="emergency_life_threatening">Gawat Darurat Mengancam Nyawa</option>
          </select>
        </div>
      </div>

      {/* Patient Information Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">II. Informasi Pasien</h2>

        <div className="relative">
          <input
            type="text"
            placeholder="Cari berdasarkan No RM, nama, atau nomor BPJS..."
            value={patientSearchQuery}
            onChange={(e) => setPatientSearchQuery(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            disabled={!!selectedPatient}
          />
          {searchingPatient && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
            </div>
          )}
        </div>

        {/* Patient Search Results */}
        {showPatientResults && patientSearchResults.length > 0 && (
          <div className="mt-4 border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-64 overflow-y-auto">
            {patientSearchResults.map((patient) => (
              <button
                key={patient.patient_id}
                onClick={() => handleSelectPatient(patient)}
                className="w-full px-4 py-3 hover:bg-gray-50 text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{patient.full_name}</p>
                    <p className="text-sm text-gray-600">
                      {patient.medical_record_number} • {patient.age_years} tahun •{" "}
                      {patient.gender === "male" ? "Laki-laki" : "Perempuan"}
                    </p>
                  </div>
                  {patient.bpjs_number && (
                    <div className="text-right">
                      <p className="text-xs text-gray-500">BPJS</p>
                      <p className="text-sm font-medium text-gray-900">{patient.bpjs_number}</p>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Selected Patient Card */}
        {selectedPatient && (
          <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{selectedPatient.full_name}</h3>
                <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                  <div>
                    <p className="text-gray-600">No RM</p>
                    <p className="font-medium">{selectedPatient.medical_record_number}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">NIK</p>
                    <p className="font-medium">{selectedPatient.nik}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Tanggal Lahir / Umur</p>
                    <p className="font-medium">{selectedPatient.date_of_birth} / {selectedPatient.age_years} tahun</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Jenis Kelamin</p>
                    <p className="font-medium">{selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Golongan Darah</p>
                    <p className="font-medium">{selectedPatient.blood_type} {selectedPatient.rh_factor !== "unknown" ? `(${selectedPatient.rh_factor})` : ""}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Status Perkawinan</p>
                    <p className="font-medium">
                      {selectedPatient.marital_status === "married" ? "Kawin" :
                       selectedPatient.marital_status === "single" ? "Belum Kawin" :
                       selectedPatient.marital_status === "widowed" ? "Janda/Duda" : "Cerai"}
                    </p>
                  </div>
                </div>
                <div className="mt-3">
                  <p className="text-gray-600 text-sm">Alamat</p>
                  <p className="text-sm">{selectedPatient.address}, {selectedPatient.city}</p>
                </div>

                {/* Age verification alert */}
                {selectedPatient.is_minor && (
                  <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-yellow-800">Pasien Di Bawah Umur</p>
                        <p className="text-xs text-yellow-700 mt-1">Wajib mendapatkan persetujuan dari orang tua/wali</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* BPJS Status */}
                {selectedPatient.bpjs_number && (
                  <div className="mt-3">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                      BPJS: {selectedPatient.bpjs_number} (Aktif)
                    </span>
                  </div>
                )}

                {/* Allergies */}
                {selectedPatient.allergies && selectedPatient.allergies.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-red-600">Alergi:</p>
                    <p className="text-sm text-red-600">{selectedPatient.allergies.join(", ")}</p>
                  </div>
                )}
              </div>
              <button
                onClick={() => setSelectedPatient(null)}
                className="text-gray-400 hover:text-red-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Procedure Information Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">III. Informasi Prosedur</h2>

          <div className="space-y-4">
            {/* Procedure Code Lookup */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Kode Prosedur <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Cari kode atau nama prosedur..."
                  value={procedureSearchQuery}
                  onChange={(e) => setProcedureSearchQuery(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                {searchingProcedure && (
                  <div className="absolute right-3 top-3">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
                  </div>
                )}
              </div>

              {/* Procedure Search Results */}
              {showProcedureResults && procedureSearchResults.length > 0 && (
                <div className="mt-2 border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-48 overflow-y-auto">
                  {procedureSearchResults.map((procedure) => (
                    <button
                      key={procedure.code}
                      onClick={() => handleSelectProcedure(procedure)}
                      className="w-full px-4 py-3 hover:bg-gray-50 text-left"
                    >
                      <p className="font-medium text-gray-900">{procedure.name_indonesian}</p>
                      <p className="text-sm text-gray-600">{procedure.code} - {procedure.description}</p>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Procedure Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nama Prosedur/Tindakan <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={procedureName}
                onChange={(e) => setProcedureName(e.target.value)}
                placeholder="Contoh: Apendisektomi"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Procedure Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Deskripsi Prosedur <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={4}
                value={procedureDescription}
                onChange={(e) => setProcedureDescription(e.target.value)}
                placeholder="Jelaskan secara rinci prosedur yang akan dilakukan..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Surgical Category and Specialty */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Kategori Bedah
                </label>
                <select
                  value={surgicalCategory}
                  onChange={(e) => setSurgicalCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Pilih Kategori</option>
                  {Object.values(SURGICAL_CATEGORIES).map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Spesialisasi Bedah
                </label>
                <input
                  type="text"
                  value={surgicalSpecialty}
                  onChange={(e) => setSurgicalSpecialty(e.target.value)}
                  placeholder="Contoh: Bedah Digestif"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Date, Time, Duration */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tanggal Rencana Tindakan <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={plannedDate}
                  onChange={(e) => setPlannedDate(e.target.value)}
                  min={new Date().toISOString().split("T")[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Waktu Rencana Tindakan <span className="text-red-500">*</span>
                </label>
                <input
                  type="time"
                  value={plannedTime}
                  onChange={(e) => setPlannedTime(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Perkiraan Durasi (menit)
                </label>
                <input
                  type="number"
                  value={expectedDuration}
                  onChange={(e) => setExpectedDuration(parseInt(e.target.value) || 60)}
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Alternative Treatments */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Alternatif Pengobatan Lain
              </label>
              <textarea
                rows={3}
                value={alternativeTreatments}
                onChange={(e) => setAlternativeTreatments(e.target.value)}
                placeholder="Sebutkan alternatif pengobatan lain yang tersedia..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Anesthesia Information Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">IV. Informasi Anestesi</h2>

          <div className="space-y-4">
            {/* Anesthesia Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Jenis Anestesi
              </label>
              <select
                value={anesthesiaType}
                onChange={(e) => setAnesthesiaType(e.target.value as AnesthesiaType)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {ANESTHESIA_TYPE_OPTIONS.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label_indonesian} - {type.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Anesthesia Risks */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Risiko Anestesi
              </label>
              <textarea
                rows={3}
                value={anesthesiaRisks}
                onChange={(e) => setAnesthesiaRisks(e.target.value)}
                placeholder="Jelaskan risiko yang terkait dengan jenis anestesi yang dipilih..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Template risiko anestesi tersedia dari konstanta RISK_TEMPLATES.ANESTHESIA_RISKS
              </p>
            </div>

            {/* Anesthesiologist */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dokter Anestesi
              </label>
              <input
                type="text"
                value={anesthesiologistName}
                onChange={(e) => setAnesthesiologistName(e.target.value)}
                placeholder="Nama dokter anestesi..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Pre-anesthesia Requirements */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Persiapan Pra-Anestesi
              </label>
              <textarea
                rows={3}
                value={preAnesthesiaRequirements}
                onChange={(e) => setPreAnesthesiaRequirements(e.target.value)}
                placeholder="Puasa, penghentian obat tertentu, dll..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Risks and Benefits Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">V. Risiko dan Manfaat</h2>

          <div className="space-y-4">
            {/* General Risks */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Risiko Umum Bedah <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={6}
                value={generalRisks}
                onChange={(e) => setGeneralRisks(e.target.value)}
                placeholder="Sebutkan risiko umum seperti perdarahan, infeksi, dll..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Gunakan template dari RISK_TEMPLATES.GENERAL_SURGICAL_RISKS
              </p>
            </div>

            {/* Procedure-Specific Risks */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Risiko Khusus Prosedur
              </label>
              <textarea
                rows={4}
                value={procedureSpecificRisks}
                onChange={(e) => setProcedureSpecificRisks(e.target.value)}
                placeholder="Risiko spesifik untuk prosedur ini..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Benefits */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Manfaat Tindakan <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={4}
                value={benefits}
                onChange={(e) => setBenefits(e.target.value)}
                placeholder="Jelaskan manfaat dan hasil yang diharapkan..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Consequences of Refusal */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Konsekuensi Menolak Tindakan <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={4}
                value={consequencesOfRefusal}
                onChange={(e) => setConsequencesOfRefusal(e.target.value)}
                placeholder="Jelaskan apa yang terjadi jika pasien menolak tindakan..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Success Rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tingkat Keberhasilan (%)
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={successRate}
                  onChange={(e) => setSuccessRate(parseInt(e.target.value))}
                  className="flex-1"
                />
                <span className="text-lg font-semibold text-indigo-600 w-16 text-right">
                  {successRate}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Patient Consent Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">VI. Pernyataan Pemahaman dan Persetujuan</h2>

          <div className="space-y-4">
            <p className="text-sm text-gray-600 mb-4">
              Saya yang bertanda tangan di bawah ini, pasien/wali dari pasien:
            </p>

            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <p className="font-semibold">{selectedPatient.full_name}</p>
              <p className="text-sm text-gray-600">
                {selectedPatient.medical_record_number} • {selectedPatient.age_years} tahun
              </p>
            </div>

            {/* Understanding Checkboxes */}
            <div className="space-y-3">
              <p className="font-medium text-gray-900">Dengan ini saya menyatakan bahwa:</p>

              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={understandsProcedure}
                  onChange={(e) => setUnderstandsProcedure(e.target.checked)}
                  className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Saya telah mendapatkan penjelasan yang cukup mengenai diagnosis dan penyakit saya
                </span>
              </label>

              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={understandsRisks}
                  onChange={(e) => setUnderstandsRisks(e.target.checked)}
                  className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Saya mengerti tindakan yang akan dilakukan beserta tujuannya
                </span>
              </label>

              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={understandsBenefits}
                  onChange={(e) => setUnderstandsBenefits(e.target.checked)}
                  className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Saya mengerti risiko dan komplikasi yang mungkin terjadi
                </span>
              </label>

              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={understandsAlternatives}
                  onChange={(e) => setUnderstandsAlternatives(e.target.checked)}
                  className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Saya mengerti ada alternatif tindakan lain yang tersedia
                </span>
              </label>

              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={understandsConsequences}
                  onChange={(e) => setUnderstandsConsequences(e.target.checked)}
                  className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Saya mengerti konsekuensi jika menolak tindakan yang disarankan
                </span>
              </label>

              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={understandsCanWithdraw}
                  onChange={(e) => setUnderstandsCanWithdraw(e.target.checked)}
                  className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Saya mengerti bahwa saya dapat menarik persetujuan ini kapan saja sebelum tindakan dimulai
                </span>
              </label>

              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={questionsAnswered}
                  onChange={(e) => setQuestionsAnswered(e.target.checked)}
                  className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Saya telah diberikan kesempatan untuk bertanya dan semua jawaban telah memuaskan
                </span>
              </label>

              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consentVoluntary}
                  onChange={(e) => setConsentVoluntary(e.target.checked)}
                  className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Persetujuan ini saya berikan secara sukarela tanpa paksaan dari pihak manapun
                </span>
              </label>
            </div>

            {/* Consent Decision */}
            <div className="mt-6 pt-6 border-t">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Keputusan Pasien:
              </label>
              <div className="space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    name="consentDecision"
                    checked={patientConsentGiven}
                    onChange={() => setPatientConsentGiven(true)}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700">Saya menyetujui tindakan</span>
                </label>
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    name="consentDecision"
                    checked={!patientConsentGiven}
                    onChange={() => setPatientConsentGiven(false)}
                    className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700">Saya menolak tindakan</span>
                </label>
              </div>
            </div>

            {/* Date and Time of Consent */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tanggal Persetujuan
                </label>
                <input
                  type="date"
                  value={consentDate}
                  onChange={(e) => setConsentDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Waktu Persetujuan
                </label>
                <input
                  type="time"
                  value={consentTime}
                  onChange={(e) => setConsentTime(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Patient Signature */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tanda Tangan Pasien <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={patientSignature}
                onChange={(e) => setPatientSignature(e.target.value)}
                placeholder="Ketik nama lengkap sebagai tanda tangan digital..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Dalam implementasi produksi, gunakan komponen signature capture
              </p>
            </div>

            {/* Guardian Section (for minors) */}
            {selectedPatient.is_minor && (
              <div className="mt-6 pt-6 border-t bg-yellow-50 p-4 rounded-lg">
                <p className="font-medium text-yellow-800 mb-3">Persetujuan Orang Tua/Wali (Wajib untuk pasien di bawah umur)</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nama Orang Tua/Wali <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={guardianName}
                      onChange={(e) => setGuardianName(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Hubungan dengan Pasien <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={guardianRelationship}
                      onChange={(e) => setGuardianRelationship(e.target.value as ConsentRelationshipType)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="parent">Orang Tua</option>
                      <option value="guardian">Wali</option>
                      <option value="spouse">Suami/Istri</option>
                    </select>
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tanda Tangan Wali <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={guardianSignature}
                    onChange={(e) => setGuardianSignature(e.target.value)}
                    placeholder="Ketik nama lengkap sebagai tanda tangan digital..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
            )}

            {/* Patient Comments */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Komentar Tambahan Pasien
              </label>
              <textarea
                rows={3}
                value={patientComments}
                onChange={(e) => setPatientComments(e.target.value)}
                placeholder="Pertanyaan atau komentar tambahan..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Witness Information Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">VII. Informasi Saksi</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nama Saksi <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={witnessName}
                onChange={(e) => setWitnessName(e.target.value)}
                placeholder="Nama lengkap saksi..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hubungan dengan Pasien
              </label>
              <input
                type="text"
                value={witnessRelationship}
                onChange={(e) => setWitnessRelationship(e.target.value)}
                placeholder="Jika ada hubungan keluarga..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tanda Tangan Saksi <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={witnessSignature}
                onChange={(e) => setWitnessSignature(e.target.value)}
                placeholder="Ketik nama lengkap sebagai tanda tangan digital..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Doctor Information Section */}
      {selectedPatient && surgeonInfo && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">VIII. Informasi Dokter</h2>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Nama Dokter</p>
                <p className="font-semibold">{surgeonInfo.doctor_title} {surgeonInfo.doctor_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Spesialisasi</p>
                <p className="font-semibold">{surgeonInfo.specialization}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">No. SIP</p>
                <p className="font-semibold">{surgeonInfo.sip_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">No. STR</p>
                <p className="font-semibold">{surgeonInfo.str_number}</p>
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tanda Tangan Dokter
              </label>
              <input
                type="text"
                value={surgeonSignature}
                onChange={(e) => setSurgeonSignature(e.target.value)}
                placeholder="Ketik nama lengkap sebagai tanda tangan digital..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Internal Notes Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">IX. Catatan Internal</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Catatan untuk Dokumentasi Medis
            </label>
            <textarea
              rows={4}
              value={internalNotes}
              onChange={(e) => setInternalNotes(e.target.value)}
              placeholder="Catatan internal untuk dokumentasi..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Catatan ini tidak akan dicetak di formulir persetujuan pasien
            </p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {selectedPatient && (
        <div className="flex flex-wrap gap-3 justify-end">
          <button
            onClick={() => router.push("/app/consents")}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Batal
          </button>
          <button
            onClick={() => handleSaveConsent("draft")}
            disabled={loading}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            {loading ? "Menyimpan..." : "Simpan Draft"}
          </button>
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            {showPreview ? "Tutup Preview" : "Preview Formulir"}
          </button>
          <button
            onClick={handlePrintConsent}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Cetak PDF
          </button>
          <button
            onClick={() => handleSaveConsent("pending")}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? "Menyimpan..." : "Simpan & Selesaikan"}
          </button>
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">Preview Formulir Persetujuan</h3>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-6 overflow-y-auto max-h-[70vh] bg-white text-sm">
              {/* Hospital Header */}
              <div className="text-center mb-6 pb-4 border-b-2">
                <h1 className="text-xl font-bold">FORMULIR PERSETUJUAN INFORMASI (INFORMED CONSENT)</h1>
                <p className="text-gray-600 mt-1">{getConsentTypeLabel(consentType)}</p>
              </div>

              {/* Patient Info */}
              <div className="mb-6">
                <h2 className="font-bold text-base mb-2">I. INFORMASI PASIEN</h2>
                <div className="grid grid-cols-2 gap-2">
                  <div><span className="font-semibold">Nama Lengkap:</span> {selectedPatient.full_name}</div>
                  <div><span className="font-semibold">No RM:</span> {selectedPatient.medical_record_number}</div>
                  <div><span className="font-semibold">NIK:</span> {selectedPatient.nik}</div>
                  <div><span className="font-semibold">Umur:</span> {selectedPatient.age_years} tahun</div>
                  <div><span className="font-semibold">Jenis Kelamin:</span> {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}</div>
                  <div><span className="font-semibold">Golongan Darah:</span> {selectedPatient.blood_type}</div>
                </div>
              </div>

              {/* Procedure Info */}
              <div className="mb-6">
                <h2 className="font-bold text-base mb-2">II. INFORMASI MEDIS</h2>
                <div className="space-y-1">
                  <div><span className="font-semibold">Diagnosis:</span> {procedureDescription}</div>
                  <div><span className="font-semibold">Rencana Tindakan:</span> {procedureName}</div>
                  <div><span className="font-semibold">Tanggal:</span> {plannedDate} {plannedTime}</div>
                  <div><span className="font-semibold">Dokter:</span> {surgeonInfo?.doctor_title} {surgeonInfo?.doctor_name}</div>
                  <div><span className="font-semibold">Anestesi:</span> {ANESTHESIA_TYPE_OPTIONS.find(a => a.value === anesthesiaType)?.label_indonesian}</div>
                </div>
              </div>

              {/* Risks and Benefits */}
              <div className="mb-6">
                <h2 className="font-bold text-base mb-2">III. PENJELASAN INFORMASI</h2>
                <div className="space-y-2">
                  <div>
                    <p className="font-semibold">A. Tindakan yang akan dilakukan:</p>
                    <p className="mt-1">{procedureDescription}</p>
                  </div>
                  <div>
                    <p className="font-semibold">B. Risiko dan komplikasi:</p>
                    <p className="mt-1 whitespace-pre-line">{generalRisks}</p>
                  </div>
                  <div>
                    <p className="font-semibold">C. Alternatif tindakan:</p>
                    <p className="mt-1 whitespace-pre-line">{alternativeTreatments || "Tidak ada alternatif lain"}</p>
                  </div>
                  <div>
                    <p className="font-semibold">D. Konsekuensi menolak tindakan:</p>
                    <p className="mt-1">{consequencesOfRefusal}</p>
                  </div>
                </div>
              </div>

              {/* Understanding Statement */}
              <div className="mb-6">
                <h2 className="font-bold text-base mb-2">IV. PERNYATAAN PEMAHAMAN</h2>
                <p className="text-xs leading-relaxed">
                  Saya yang bertanda tangan di bawah ini menyatakan bahwa saya telah mendapatkan penjelasan yang cukup
                  mengenai penyakit saya, tindakan yang akan dilakukan beserta tujuannya, risiko dan komplikasi yang mungkin terjadi,
                  alternatif tindakan lain, dan konsekuensi jika menolak tindakan. Saya diberikan kesempatan untuk bertanya
                  dan semua jawaban telah memuaskan. Saya mengerti bahwa saya dapat menarik persetujuan ini kapan saja
                  sebelum tindakan dimulai.
                </p>
              </div>

              {/* Consent Statement */}
              <div className="mb-6">
                <h2 className="font-bold text-base mb-2">V. PERSETUJUAN</h2>
                <div className="bg-gray-50 p-3 rounded">
                  <p className="font-semibold text-lg">
                    Saya {patientConsentGiven ? "MENYETUJUI" : "MENOLAK"} tindakan yang dijelaskan di atas
                  </p>
                  <p className="text-xs mt-2 text-gray-600">
                    Diberikan pada: {consentDate} pukul {consentTime}
                  </p>
                </div>
              </div>

              {/* Signatures */}
              <div className="mb-6">
                <h2 className="font-bold text-base mb-2">VI. TANDA TANGAN</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="border p-3 rounded">
                    <p className="font-semibold">Pasien/Keluarga</p>
                    <p className="mt-2">{patientSignature || selectedPatient.full_name}</p>
                    <p className="text-xs text-gray-600 mt-1">{consentDate} - {consentTime}</p>
                  </div>
                  <div className="border p-3 rounded">
                    <p className="font-semibold">Saksi</p>
                    <p className="mt-2">{witnessSignature || witnessName}</p>
                    <p className="text-xs text-gray-600 mt-1">{consentDate} - {consentTime}</p>
                  </div>
                  {selectedPatient.is_minor && (
                    <div className="border p-3 rounded">
                      <p className="font-semibold">Wali</p>
                      <p className="mt-2">{guardianSignature || guardianName}</p>
                      <p className="text-xs text-gray-600 mt-1">{guardianRelationship}</p>
                    </div>
                  )}
                  <div className="border p-3 rounded">
                    <p className="font-semibold">Dokter Penanggung Jawab</p>
                    <p className="mt-2">{surgeonSignature || surgeonInfo?.doctor_name}</p>
                    <p className="text-xs text-gray-600 mt-1">SIP: {surgeonInfo?.sip_number}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 border-t bg-gray-50 flex justify-end space-x-3">
              <button
                onClick={handlePrintConsent}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Cetak PDF
              </button>
              <button
                onClick={() => setShowPreview(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
