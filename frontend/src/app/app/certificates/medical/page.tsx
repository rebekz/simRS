"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import type {
  CertificatePatientInfo,
  CertificateDoctorInfo,
  SickLeaveDetails,
  MedicalFitnessDetails,
  PregnancyDetails,
  HealthyChildDetails,
  DeathDetails,
  MedicalReportDetails,
  FormValidationError,
} from "@/types/medical-certificate";
import type {
  CertificateType,
} from "@/constants/medical-certificate";
import {
  CERTIFICATE_TYPE_OPTIONS,
  DURATION_OPTIONS,
  ICD10_CATEGORIES,
  VALIDATION_RULES,
  CERTIFICATE_TEMPLATES,
  BPJS_RULES,
  getCertificateTypeLabel,
  validateNIK,
  validateBPJSNumber,
} from "@/constants/medical-certificate";

export default function MedicalCertificatePage() {
  const router = useRouter();

  // Form state
  const [certificateType, setCertificateType] = useState<CertificateType>("sick_leave");
  const [selectedPatient, setSelectedPatient] = useState<CertificatePatientInfo | null>(null);
  const [selectedDoctor, setSelectedDoctor] = useState<CertificateDoctorInfo | null>(null);
  const [purpose, setPurpose] = useState("");
  const [isOfficial, setIsOfficial] = useState(false);
  const [issueDate, setIssueDate] = useState(new Date().toISOString().split("T")[0]);
  const [validFrom, setValidFrom] = useState(new Date().toISOString().split("T")[0]);
  const [validUntil, setValidUntil] = useState("");
  const [durationDays, setDurationDays] = useState<number>(1);
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [diagnosis, setDiagnosis] = useState("");
  const [icd10Code, setIcd10Code] = useState("");
  const [icd10Search, setIcd10Search] = useState("");
  const [findings, setFindings] = useState("");
  const [recommendations, setRecommendations] = useState("");
  const [internalNotes, setInternalNotes] = useState("");

  // Type-specific details
  const [sickLeaveDetails, setSickLeaveDetails] = useState<SickLeaveDetails>({
    duration_days: 1,
    start_date: new Date().toISOString().split("T")[0],
    end_date: "",
    must_rest_at_home: false,
    requires_hospitalization: false,
    can_do_light_activities: false,
    requires_follow_up: false,
  });
  const [medicalFitnessDetails, setMedicalFitnessDetails] = useState<MedicalFitnessDetails>({
    health_status: "fit",
    fitness_category: "general",
    restrictions: [],
    recommendations: [],
  });
  const [pregnancyDetails, setPregnancyDetails] = useState<PregnancyDetails>({
    gestational_age_weeks: 0,
    estimated_due_date: "",
    pregnancy_status: "normal",
    fetus_count: 1,
  });
  const [healthyChildDetails, setHealthyChildDetails] = useState<HealthyChildDetails>({
    age_months: 0,
    weight_kg: 0,
    height_cm: 0,
    nutritional_status: "good",
    development_status: "normal",
    vaccination_status: "unknown",
  });
  const [deathDetails, setDeathDetails] = useState<DeathDetails>({
    death_datetime: "",
    place_of_death: "",
    cause_of_death_primary: "",
    manner_of_death: "natural",
    autopsy_performed: false,
    reported_to_authorities: false,
    body_released_to: "",
    relationship_to_deceased: "",
  });
  const [medicalReportDetails, setMedicalReportDetails] = useState<MedicalReportDetails>({
    report_category: "",
    examination_type: "",
    findings: "",
    diagnosis: "",
    confidentiality: "normal",
  });

  // UI state
  const [loading, setLoading] = useState(false);
  const [searchingPatient, setSearchingPatient] = useState(false);
  const [patientSearchQuery, setPatientSearchQuery] = useState("");
  const [patientSearchResults, setPatientSearchResults] = useState<CertificatePatientInfo[]>([]);
  const [showPatientResults, setShowPatientResults] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<FormValidationError[]>([]);

  // Get current user (doctor) info
  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
      return;
    }

    // Parse JWT to get doctor info
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      if (payload.staff_id) {
        setSelectedDoctor({
          doctor_id: payload.staff_id,
          doctor_name: payload.name || "Dr. Unknown",
          doctor_title: payload.title || "dr.",
          specialization: payload.specialization || "",
          sip_number: payload.sip_number || "",
          department: payload.department || "Umum",
          signature_status: "pending",
        });
      }
    } catch (err) {
      console.error("Error parsing token:", err);
    }
  }, [router]);

  // Calculate duration days when dates change
  useEffect(() => {
    if (sickLeaveDetails.start_date && sickLeaveDetails.end_date) {
      const start = new Date(sickLeaveDetails.start_date);
      const end = new Date(sickLeaveDetails.end_date);
      const diff = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
      if (diff > 0) {
        setDurationDays(diff);
        setSickLeaveDetails((prev) => ({ ...prev, duration_days: diff }));
      }
    }
  }, [sickLeaveDetails.start_date, sickLeaveDetails.end_date]);

  // Update end date when duration changes
  useEffect(() => {
    if (sickLeaveDetails.start_date && durationDays > 0) {
      const start = new Date(sickLeaveDetails.start_date);
      const end = new Date(start.getTime() + durationDays * 24 * 60 * 60 * 1000);
      setSickLeaveDetails((prev) => ({ ...prev, end_date: end.toISOString().split("T")[0] }));
      setValidUntil(end.toISOString().split("T")[0]);
    }
  }, [durationDays, sickLeaveDetails.start_date]);

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

  // Select patient
  const handleSelectPatient = (patient: CertificatePatientInfo) => {
    setSelectedPatient(patient);
    setShowPatientResults(false);
    setPatientSearchQuery("");
  };

  // Validate form
  const validateForm = (): boolean => {
    const errors: FormValidationError[] = [];

    // Patient validation
    if (!selectedPatient) {
      errors.push({ field: "patient", message: "Pilih pasien terlebih dahulu", severity: "error" });
    } else {
      if (!selectedPatient.nik || !validateNIK(selectedPatient.nik)) {
        errors.push({ field: "patient_nik", message: "NIK pasien tidak valid", severity: "error" });
      }
    }

    // Doctor validation
    if (!selectedDoctor) {
      errors.push({ field: "doctor", message: "Dokter tidak ditemukan", severity: "error" });
    } else if (!selectedDoctor.sip_number) {
      errors.push({ field: "doctor_sip", message: "Nomor SIP dokter tidak valid", severity: "error" });
    }

    // Certificate details validation
    if (!purpose || purpose.trim().length < 5) {
      errors.push({ field: "purpose", message: "Tujuan surat harus diisi (minimal 5 karakter)", severity: "error" });
    }

    if (!issueDate) {
      errors.push({ field: "issue_date", message: "Tanggal penerbitan harus diisi", severity: "error" });
    }

    if (!validFrom) {
      errors.push({ field: "valid_from", message: "Tanggal berlaku harus diisi", severity: "error" });
    }

    if (!validUntil) {
      errors.push({ field: "valid_until", message: "Tanggal berakhir harus diisi", severity: "error" });
    } else if (new Date(validUntil) <= new Date(validFrom)) {
      errors.push({ field: "valid_until", message: "Tanggal berakhir harus setelah tanggal berlaku", severity: "error" });
    }

    // Clinical information validation
    if (!chiefComplaint || chiefComplaint.trim().length < 3) {
      errors.push({ field: "chief_complaint", message: "Keluhan utama harus diisi (minimal 3 karakter)", severity: "error" });
    }

    if (!diagnosis || diagnosis.trim().length < 3) {
      errors.push({ field: "diagnosis", message: "Diagnosis harus diisi (minimal 3 karakter)", severity: "error" });
    }

    if (!icd10Code || icd10Code.trim().length < 1) {
      errors.push({ field: "icd10_code", message: "Kode ICD-10 harus diisi", severity: "error" });
    }

    // Type-specific validation
    if (certificateType === "sick_leave") {
      if (!sickLeaveDetails.start_date) {
        errors.push({ field: "start_date", message: "Tanggal mulai istirahat harus diisi", severity: "error" });
      }
      if (!sickLeaveDetails.end_date) {
        errors.push({ field: "end_date", message: "Tanggal selesai istirahat harus diisi", severity: "error" });
      }
      if (sickLeaveDetails.duration_days < 1) {
        errors.push({ field: "duration_days", message: "Durasi istirahat minimal 1 hari", severity: "error" });
      }
      if (sickLeaveDetails.duration_days > VALIDATION_RULES.MAX_DURATION_DAYS.SICK_LEAVE_WITH_APPROVAL) {
        errors.push({
          field: "duration_days",
          message: `Durasi istirahat maksimal ${VALIDATION_RULES.MAX_DURATION_DAYS.SICK_LEAVE_WITH_APPROVAL} hari`,
          severity: "error",
        });
      }
      // BPJS validation
      if (selectedPatient?.bpjs_number && sickLeaveDetails.duration_days > BPJS_RULES.SICK_LEAVE_FORMAT.MAX_DURATION_DAYS) {
        errors.push({
          field: "duration_days",
          message: `Untuk pasien BPJS, maksimal durasi istirahat adalah ${BPJS_RULES.SICK_LEAVE_FORMAT.MAX_DURATION_DAYS} hari. Untuk durasi lebih lama, diperlukan persetujuan spesialis.`,
          severity: "warning",
        });
      }
    } else if (certificateType === "pregnancy") {
      if (!pregnancyDetails.estimated_due_date) {
        errors.push({ field: "estimated_due_date", message: "Tanggal perkiraan lahir harus diisi", severity: "error" });
      }
      if (pregnancyDetails.gestational_age_weeks < 0 || pregnancyDetails.gestational_age_weeks > 42) {
        errors.push({ field: "gestational_age", message: "Usia kehamilan tidak valid (0-42 minggu)", severity: "error" });
      }
    } else if (certificateType === "death_certificate") {
      if (!deathDetails.death_datetime) {
        errors.push({ field: "death_datetime", message: "Tanggal dan jam kematian harus diisi", severity: "error" });
      }
      if (!deathDetails.place_of_death) {
        errors.push({ field: "place_of_death", message: "Tempat kematian harus diisi", severity: "error" });
      }
      if (!deathDetails.cause_of_death_primary) {
        errors.push({ field: "cause_of_death", message: "Penyebab kematian harus diisi", severity: "error" });
      }
    }

    setValidationErrors(errors);
    return errors.filter((e) => e.severity === "error").length === 0;
  };

  // Save certificate
  const handleSaveCertificate = async () => {
    if (!validateForm()) {
      setError("Mohon lengkapi field yang wajib diisi");
      return;
    }

    setLoading(true);
    setError(null);
    const token = localStorage.getItem("staff_access_token");

    try {
      const payload: any = {
        certificate_type: certificateType,
        format: "standard",
        patient_id: selectedPatient!.patient_id,
        doctor_id: selectedDoctor!.doctor_id,
        issue_date: issueDate,
        valid_from: validFrom,
        valid_until: validUntil,
        purpose: purpose,
        is_official: isOfficial,
        copies: 1,
        primary_diagnosis: diagnosis,
        primary_diagnosis_code: icd10Code,
        chief_complaint: chiefComplaint,
        physical_examination: findings,
        clinical_notes: recommendations,
        internal_notes: internalNotes,
      };

      // Add type-specific details
      if (certificateType === "sick_leave") {
        payload.sick_leave_details = sickLeaveDetails;
      } else if (certificateType === "medical_fitness") {
        payload.medical_fitness_details = medicalFitnessDetails;
      } else if (certificateType === "pregnancy") {
        payload.pregnancy_details = pregnancyDetails;
      } else if (certificateType === "healthy_child") {
        payload.healthy_child_details = healthyChildDetails;
      } else if (certificateType === "death_certificate") {
        payload.death_details = deathDetails;
      } else if (certificateType === "medical_report") {
        payload.medical_report_details = medicalReportDetails;
      }

      const response = await fetch("/api/v1/certificates/medical", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Gagal menyimpan surat keterangan medis");
      }

      const data = await response.json();
      setSuccessMessage("Surat keterangan medis berhasil dibuat");
      setTimeout(() => {
        router.push(`/app/certificates/${data.certificate_id}`);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan surat keterangan medis");
    } finally {
      setLoading(false);
    }
  };

  // Calculate patient age
  const calculateAge = (dateOfBirth: string): string => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let years = today.getFullYear() - birthDate.getFullYear();
    let months = today.getMonth() - birthDate.getMonth();
    let days = today.getDate() - birthDate.getDate();

    if (days < 0) {
      months--;
      days += new Date(today.getFullYear(), today.getMonth(), 0).getDate();
    }
    if (months < 0) {
      years--;
      months += 12;
    }

    if (years > 0) {
      return `${years} tahun`;
    } else if (months > 0) {
      return `${months} bulan`;
    } else {
      return `${days} hari`;
    }
  };

  // Format date for display
  const formatDateIndonesian = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  // Filter ICD-10 categories
  const filteredICD10Categories = useMemo(() => {
    if (!icd10Search) return ICD10_CATEGORIES;
    const search = icd10Search.toLowerCase();
    return ICD10_CATEGORIES.filter((cat) =>
      cat.description.toLowerCase().includes(search) ||
      cat.code.toLowerCase().includes(search)
    );
  }, [icd10Search]);

  // Generate certificate preview
  const generatePreview = () => {
    if (!selectedPatient || !selectedDoctor) return null;

    return (
      <div className="bg-white p-8 border-2 border-gray-300 rounded-lg">
        <div className="text-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">SURAT KETERANGAN MEDIS</h2>
          <p className="text-gray-600 mt-1">{getCertificateTypeLabel(certificateType)}</p>
          <p className="text-sm text-gray-500 mt-2">No: {CERTIFICATE_TEMPLATES.CERTIFICATE_NUMBER_FORMAT.EXAMPLE}</p>
        </div>

        <div className="space-y-4 text-sm">
          <div>
            <p className="font-semibold text-gray-900">Yang bertanda tangan di bawah ini:</p>
            <p className="mt-2">Nama: {selectedDoctor.doctor_name}</p>
            <p>SIP: {selectedDoctor.sip_number}</p>
            {selectedDoctor.specialization && <p>Spesialis: {selectedDoctor.specialization}</p>}
          </div>

          <div>
            <p className="font-semibold text-gray-900">Menyatakan bahwa:</p>
            <div className="mt-2 pl-4">
              <p>Nama: {selectedPatient.full_name}</p>
              <p>NIK: {selectedPatient.nik}</p>
              <p>Tanggal Lahir: {formatDateIndonesian(selectedPatient.date_of_birth)}</p>
              <p>Umur: {calculateAge(selectedPatient.date_of_birth)}</p>
              <p>Jenis Kelamin: {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}</p>
              <p>Alamat: {selectedPatient.address}</p>
            </div>
          </div>

          <div>
            <p className="font-semibold text-gray-900">Informasi Medis:</p>
            <div className="mt-2 pl-4">
              <p>Tanggal Pemeriksaan: {formatDateIndonesian(issueDate)}</p>
              {certificateType === "sick_leave" && (
                <>
                  <p>Durasi Istirahat: {durationDays} hari</p>
                  <p>Tanggal: {formatDateIndonesian(sickLeaveDetails.start_date)} s/d {formatDateIndonesian(sickLeaveDetails.end_date)}</p>
                </>
              )}
              <p>Keluhan Utama: {chiefComplaint}</p>
              <p>Diagnosis: {diagnosis} ({icd10Code})</p>
              {findings && <p>Pemeriksaan Fisik: {findings}</p>}
              {recommendations && <p>Rekomendasi: {recommendations}</p>}
            </div>
          </div>

          <div>
            <p>Surat keterangan ini dibuat untuk: {purpose}</p>
          </div>

          <div className="mt-8 text-right">
            <p>{formatDateIndonesian(issueDate)}</p>
            <p className="mt-4">Dokter Pemeriksa,</p>
            <p className="mt-16 font-semibold">{selectedDoctor.doctor_name}</p>
            <p className="text-xs text-gray-500">SIP: {selectedDoctor.sip_number}</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Buat Surat Keterangan Medis</h1>
          <p className="text-gray-600 mt-1">Buat surat keterangan medis untuk pasien</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => router.push("/app/certificates")}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Kembali
          </button>
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            {showPreview ? "Edit" : "Preview"}
          </button>
        </div>
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

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800 mb-2">Mohon periksa kembali:</h3>
          <ul className="list-disc list-inside space-y-1">
            {validationErrors.map((err, idx) => (
              <li key={idx} className={`text-sm ${err.severity === "error" ? "text-red-700" : "text-yellow-700"}`}>
                {err.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      {!showPreview ? (
        <>
          {/* Certificate Type Selection */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Jenis Surat Keterangan</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {CERTIFICATE_TYPE_OPTIONS.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setCertificateType(type.value)}
                  className={`p-4 border rounded-lg text-left transition-colors ${
                    certificateType === type.value
                      ? "border-indigo-500 bg-indigo-50"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{type.icon}</span>
                    <div>
                      <p className="font-medium text-gray-900">{type.label}</p>
                      <p className="text-sm text-gray-600">{type.description}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Patient Selection Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Pilih Pasien</h2>

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
                          {patient.medical_record_number} • {calculateAge(patient.date_of_birth)} •{" "}
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
                  <div>
                    <h3 className="font-semibold text-gray-900">{selectedPatient.full_name}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {selectedPatient.medical_record_number} • {calculateAge(selectedPatient.date_of_birth)} •{" "}
                      {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">NIK: {selectedPatient.nik}</p>
                    <p className="text-sm text-gray-600">Alamat: {selectedPatient.address}</p>
                    {selectedPatient.bpjs_number && (
                      <div className="mt-2">
                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700">
                          BPJS: {selectedPatient.bpjs_number}
                        </span>
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

          {/* Certificate Details Section */}
          {selectedPatient && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Detail Surat</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Penerbitan *</label>
                  <input
                    type="date"
                    value={issueDate}
                    onChange={(e) => setIssueDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Berlaku Dari *</label>
                  <input
                    type="date"
                    value={validFrom}
                    onChange={(e) => setValidFrom(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Berlaku Sampai *</label>
                  <input
                    type="date"
                    value={validUntil}
                    onChange={(e) => setValidUntil(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Untuk Keperluan *</label>
                  <input
                    type="text"
                    value={purpose}
                    onChange={(e) => setPurpose(e.target.value)}
                    placeholder="Contoh: Untuk keperluan cuti sakit"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={isOfficial}
                      onChange={(e) => setIsOfficial(e.target.checked)}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="text-sm text-gray-700">Surat ini untuk keperluan resmi (BPJS/Asuransi)</span>
                  </label>
                </div>
              </div>

              {/* Sick Leave Duration */}
              {certificateType === "sick_leave" && (
                <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-3">Durasi Istirahat</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Durasi</label>
                      <select
                        value={durationDays}
                        onChange={(e) => setDurationDays(parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        {DURATION_OPTIONS.filter((d) => d.value !== "custom").map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Dari Tanggal</label>
                      <input
                        type="date"
                        value={sickLeaveDetails.start_date}
                        onChange={(e) => setSickLeaveDetails({ ...sickLeaveDetails, start_date: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Sampai Tanggal</label>
                      <input
                        type="date"
                        value={sickLeaveDetails.end_date}
                        onChange={(e) => setSickLeaveDetails({ ...sickLeaveDetails, end_date: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                  </div>
                  {selectedPatient?.bpjs_number && sickLeaveDetails.duration_days > BPJS_RULES.SICK_LEAVE_FORMAT.MAX_DURATION_DAYS && (
                    <div className="mt-3 p-3 bg-orange-50 border border-orange-200 rounded">
                      <p className="text-sm text-orange-800">
                        <strong>Catatan BPJS:</strong> Durasi istirahat lebih dari {BPJS_RULES.SICK_LEAVE_FORMAT.MAX_DURATION_DAYS} hari
                        memerlukan persetujuan dokter spesialis.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Pregnancy Details */}
              {certificateType === "pregnancy" && (
                <div className="mt-4 p-4 bg-pink-50 border border-pink-200 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-3">Detail Kehamilan</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Usia Kehamilan (Minggu)</label>
                      <input
                        type="number"
                        min="0"
                        max="42"
                        value={pregnancyDetails.gestational_age_weeks}
                        onChange={(e) => setPregnancyDetails({ ...pregnancyDetails, gestational_age_weeks: parseInt(e.target.value) || 0 })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Perkiraan Lahir (HPL)</label>
                      <input
                        type="date"
                        value={pregnancyDetails.estimated_due_date}
                        onChange={(e) => setPregnancyDetails({ ...pregnancyDetails, estimated_due_date: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Status Kehamilan</label>
                      <select
                        value={pregnancyDetails.pregnancy_status}
                        onChange={(e) => setPregnancyDetails({ ...pregnancyDetails, pregnancy_status: e.target.value as any })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="normal">Normal</option>
                        <option value="high_risk">Risiko Tinggi</option>
                        <option value="complicated">Komplikasi</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Jumlah Janin</label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={pregnancyDetails.fetus_count}
                        onChange={(e) => setPregnancyDetails({ ...pregnancyDetails, fetus_count: parseInt(e.target.value) || 1 })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Death Details */}
              {certificateType === "death_certificate" && (
                <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-3">Detail Kematian</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal & Jam Kematian *</label>
                      <input
                        type="datetime-local"
                        value={deathDetails.death_datetime}
                        onChange={(e) => setDeathDetails({ ...deathDetails, death_datetime: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tempat Kematian *</label>
                      <input
                        type="text"
                        value={deathDetails.place_of_death}
                        onChange={(e) => setDeathDetails({ ...deathDetails, place_of_death: e.target.value })}
                        placeholder="Contoh: RSUD, Rumah, dll"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Penyebab Kematian (Utama) *</label>
                      <input
                        type="text"
                        value={deathDetails.cause_of_death_primary}
                        onChange={(e) => setDeathDetails({ ...deathDetails, cause_of_death_primary: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Cara Kematian</label>
                      <select
                        value={deathDetails.manner_of_death}
                        onChange={(e) => setDeathDetails({ ...deathDetails, manner_of_death: e.target.value as any })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="natural">Alami</option>
                        <option value="accident">Kecelakaan</option>
                        <option value="suicide">Bunuh Diri</option>
                        <option value="homicide">Pembunuhan</option>
                        <option value="pending_investigation">Dalam Penyelidikan</option>
                        <option value="unknown">Tidak Diketahui</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Jasad Diserahkan Kepada</label>
                      <input
                        type="text"
                        value={deathDetails.body_released_to}
                        onChange={(e) => setDeathDetails({ ...deathDetails, body_released_to: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Clinical Information Section */}
          {selectedPatient && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Klinis</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Keluhan Utama *</label>
                  <textarea
                    rows={2}
                    value={chiefComplaint}
                    onChange={(e) => setChiefComplaint(e.target.value)}
                    placeholder="Deskripsikan keluhan utama pasien"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosis *</label>
                  <textarea
                    rows={2}
                    value={diagnosis}
                    onChange={(e) => setDiagnosis(e.target.value)}
                    placeholder="Diagnosis berdasarkan pemeriksaan"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Kode ICD-10 *</label>
                  <input
                    type="text"
                    value={icd10Code}
                    onChange={(e) => setIcd10Code(e.target.value)}
                    placeholder="Contoh: J00 - Nasofaringitis akut"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                  <div className="mt-2">
                    <input
                      type="text"
                      value={icd10Search}
                      onChange={(e) => setIcd10Search(e.target.value)}
                      placeholder="Cari kode ICD-10..."
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    {icd10Search && (
                      <div className="mt-2 border border-gray-200 rounded-lg max-h-40 overflow-y-auto">
                        {filteredICD10Categories.slice(0, 10).map((cat) => (
                          <button
                            key={cat.code}
                            onClick={() => {
                              setIcd10Code(cat.code.split("-")[0].trim());
                              setIcd10Search("");
                            }}
                            className="w-full px-3 py-2 text-left hover:bg-gray-50 border-b last:border-b-0"
                          >
                            <p className="font-medium text-gray-900">{cat.code} - {cat.description}</p>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pemeriksaan Fisik</label>
                  <textarea
                    rows={3}
                    value={findings}
                    onChange={(e) => setFindings(e.target.value)}
                    placeholder="Hasil pemeriksaan fisik"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rekomendasi</label>
                  <textarea
                    rows={3}
                    value={recommendations}
                    onChange={(e) => setRecommendations(e.target.value)}
                    placeholder="Rekomendasi tindakan lanjutan"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Catatan Internal</label>
                  <textarea
                    rows={2}
                    value={internalNotes}
                    onChange={(e) => setInternalNotes(e.target.value)}
                    placeholder="Catatan internal (tidak akan dicetak)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Doctor Information Section */}
          {selectedPatient && selectedDoctor && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Dokter</h2>

              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="font-medium text-gray-900">{selectedDoctor.doctor_name}</p>
                <p className="text-sm text-gray-600">SIP: {selectedDoctor.sip_number}</p>
                {selectedDoctor.specialization && (
                  <p className="text-sm text-gray-600">Spesialis: {selectedDoctor.specialization}</p>
                )}
                <p className="text-sm text-gray-600">Departemen: {selectedDoctor.department}</p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          {selectedPatient && (
            <div className="flex flex-wrap gap-3 justify-end">
              <button
                onClick={() => router.push("/app/certificates")}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={validateForm}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Validasi Form
              </button>
              <button
                onClick={handleSaveCertificate}
                disabled={loading}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? "Menyimpan..." : "Simpan Surat"}
              </button>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Certificate Preview */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Preview Surat</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => window.print()}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Cetak / PDF
                </button>
              </div>
            </div>
            {generatePreview()}
          </div>
        </>
      )}
    </div>
  );
}
