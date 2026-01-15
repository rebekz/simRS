"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type {
  ReferralType,
  ReferralPriority,
  ReferralStatus,
  FacilityType,
  SpecializationCategory,
  ReferralPatientInfo,
  ReferringDoctorInfo,
  DestinationFacility,
  VitalSigns,
  BPJSReferralDetails,
} from "@/types/referral";
import {
  REFERRAL_TYPE_OPTIONS,
  REFERRAL_PRIORITY_OPTIONS,
  FACILITY_TYPE_OPTIONS,
  SPECIALIZATION_CATEGORY_OPTIONS,
  REFERRAL_STATUS_OPTIONS,
} from "@/types/referral";
import {
  REFERRAL_TYPES,
  REFERRAL_PRIORITIES,
  FACILITY_TYPES,
  SPECIALIST_CATEGORIES,
  REFERRAL_FORM_LABELS,
  REFERRAL_ERROR_MESSAGES,
} from "@/constants/referral";

// Patient search result type
interface PatientSearchResult {
  id: number;
  medical_record_number: string;
  name: string;
  date_of_birth: string;
  gender: "male" | "female";
  phone: string;
  address: string;
  city: string;
  province: string;
  bpjs_number?: string;
  bpjs_class?: number;
  insurance_provider?: string;
  insurance_policy_number?: string;
}

// Facility search result type
interface FacilitySearchResult {
  id: number;
  facility_name: string;
  facility_type: FacilityType;
  address: string;
  city: string;
  province: string;
  phone: string;
  bpjs_facility_code?: string;
  is_bpjs_accredited?: boolean;
}

// ICD-10 diagnosis result
interface ICD10Diagnosis {
  code: string;
  description: string;
}

export default function NewReferralPage() {
  const router = useRouter();

  // Form state
  const [referralType, setReferralType] = useState<ReferralType>("INTERNAL");
  const [priority, setPriority] = useState<ReferralPriority>("ROUTINE");
  const [referralDate, setReferralDate] = useState(new Date().toISOString().split("T")[0]);
  const [validFrom, setValidFrom] = useState(new Date().toISOString().split("T")[0]);
  const [validUntil, setValidUntil] = useState(
    new Date(Date.now() + 180 * 24 * 60 * 60 * 1000).toISOString().split("T")[0]
  );

  // Patient state
  const [selectedPatient, setSelectedPatient] = useState<PatientSearchResult | null>(null);
  const [patientSearchQuery, setPatientSearchQuery] = useState("");
  const [patientSearchResults, setPatientSearchResults] = useState<PatientSearchResult[]>([]);
  const [showPatientResults, setShowPatientResults] = useState(false);
  const [searchingPatient, setSearchingPatient] = useState(false);

  // Facility state
  const [selectedFacility, setSelectedFacility] = useState<FacilitySearchResult | null>(null);
  const [facilitySearchQuery, setFacilitySearchQuery] = useState("");
  const [facilitySearchResults, setFacilitySearchResults] = useState<FacilitySearchResult[]>([]);
  const [showFacilityResults, setShowFacilityResults] = useState(false);
  const [searchingFacility, setSearchingFacility] = useState(false);
  const [facilityType, setFacilityType] = useState<FacilityType>("hospital");
  const [department, setDepartment] = useState("");
  const [specialization, setSpecialization] = useState<SpecializationCategory | "">("");
  const [targetDoctor, setTargetDoctor] = useState("");
  const [contactPhone, setContactPhone] = useState("");

  // Clinical information state
  const [primaryDiagnosis, setPrimaryDiagnosis] = useState("");
  const [primaryDiagnosisCode, setPrimaryDiagnosisCode] = useState("");
  const [secondaryDiagnoses, setSecondaryDiagnoses] = useState<string[]>([]);
  const [secondaryDiagnosisInput, setSecondaryDiagnosisInput] = useState("");
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [physicalExamination, setPhysicalExamination] = useState("");
  const [labResults, setLabResults] = useState("");
  const [imagingResults, setImagingResults] = useState("");
  const [treatmentGiven, setTreatmentGiven] = useState("");
  const [currentMedications, setCurrentMedications] = useState("");
  const [severity, setSeverity] = useState<"mild" | "moderate" | "severe" | "critical">("moderate");

  // Vital signs state
  const [systolicBP, setSystolicBP] = useState("");
  const [diastolicBP, setDiastolicBP] = useState("");
  const [heartRate, setHeartRate] = useState("");
  const [respiratoryRate, setRespiratoryRate] = useState("");
  const [temperature, setTemperature] = useState("");
  const [oxygenSaturation, setOxygenSaturation] = useState("");

  // Referral reason state
  const [referralReason, setReferralReason] = useState("");
  const [clinicalSummary, setClinicalSummary] = useState("");

  // BPJS state
  const [bpjsReferralNumber, setBpjsReferralNumber] = useState("");
  const [bpjsDiagnosisCode, setBpjsDiagnosisCode] = useState("");
  const [bpjsFacilityCode, setBpjsFacilityCode] = useState("");
  const [bpjsProcedureCode, setBpjsProcedureCode] = useState("");
  const [investigationRequired, setInvestigationRequired] = useState(false);

  // Doctor state
  const [doctorName, setDoctorName] = useState("");
  const [doctorSIP, setDoctorSIP] = useState("");
  const [doctorDepartment, setDoctorDepartment] = useState("");
  const [doctorContact, setDoctorContact] = useState("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  }, [router]);

  // Load doctor information from localStorage (simulated)
  useEffect(() => {
    // In a real app, this would come from the logged-in user
    const staffName = localStorage.getItem("staff_name") || "Dr. Ahmad Dani";
    const staffDept = localStorage.getItem("staff_department") || "Poli Penyakit Dalam";
    const staffSIP = localStorage.getItem("staff_sip") || "1234567890";

    setDoctorName(staffName);
    setDoctorDepartment(staffDept);
    setDoctorSIP(staffSIP);
  }, []);

  // Debounced patient search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchPatients(patientSearchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [patientSearchQuery]);

  // Debounced facility search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchFacilities(facilitySearchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [facilitySearchQuery]);

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

  // Search facilities
  const searchFacilities = async (query: string) => {
    if (!query || query.length < 2) {
      setFacilitySearchResults([]);
      setShowFacilityResults(false);
      return;
    }

    setSearchingFacility(true);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch(
        `/api/v1/facilities/search?q=${encodeURIComponent(query)}&type=${facilityType}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Gagal mencari fasilitas");
      }

      const data = await response.json();
      setFacilitySearchResults(data.facilities || []);
      setShowFacilityResults(true);
    } catch (err) {
      console.error("Error searching facilities:", err);
      setFacilitySearchResults([]);
    } finally {
      setSearchingFacility(false);
    }
  };

  // Select patient
  const handleSelectPatient = (patient: PatientSearchResult) => {
    setSelectedPatient(patient);
    setShowPatientResults(false);
    setPatientSearchQuery("");

    // Auto-populate BPJS information if available
    if (patient.bpjs_number && referralType === "BPJS") {
      setBpjsFacilityCode(patient.bpjs_number.substring(0, 5));
    }
  };

  // Select facility
  const handleSelectFacility = (facility: FacilitySearchResult) => {
    setSelectedFacility(facility);
    setShowFacilityResults(false);
    setFacilitySearchQuery("");
    setContactPhone(facility.phone);

    // Auto-populate BPJS facility code if available
    if (facility.bpjs_facility_code && referralType === "BPJS") {
      setBpjsFacilityCode(facility.bpjs_facility_code);
    }
  };

  // Add secondary diagnosis
  const handleAddSecondaryDiagnosis = () => {
    if (secondaryDiagnosisInput.trim()) {
      setSecondaryDiagnoses([...secondaryDiagnoses, secondaryDiagnosisInput.trim()]);
      setSecondaryDiagnosisInput("");
    }
  };

  // Remove secondary diagnosis
  const handleRemoveSecondaryDiagnosis = (index: number) => {
    setSecondaryDiagnoses(secondaryDiagnoses.filter((_, i) => i !== index));
  };

  // Validate form
  const validateForm = (): boolean => {
    const errors: string[] = [];

    if (!selectedPatient) {
      errors.push("Pilih pasien terlebih dahulu");
    }

    if (!referralReason.trim()) {
      errors.push("Alasan rujukan wajib diisi");
    }

    if (!primaryDiagnosis.trim()) {
      errors.push("Diagnosis utama wajib diisi");
    }

    if (!chiefComplaint.trim()) {
      errors.push("Keluhan utama wajib diisi");
    }

    if (referralType === "BPJS" && !selectedPatient?.bpjs_number) {
      errors.push("Pasien harus memiliki nomor BPJS untuk rujukan BPJS");
    }

    if (referralType === "BPJS" && !bpjsFacilityCode) {
      errors.push("Kode faskes BPJS wajib diisi untuk rujukan BPJS");
    }

    if (referralType !== "INTERNAL" && !selectedFacility) {
      errors.push("Pilih fasilitas tujuan");
    }

    if (!doctorName.trim()) {
      errors.push("Nama dokter perujuk wajib diisi");
    }

    if (!doctorSIP.trim()) {
      errors.push("Nomor SIP dokter wajib diisi");
    }

    setValidationErrors(errors);
    return errors.length === 0;
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

  // Generate referral number
  const generateReferralNumber = (): string => {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const random = Math.floor(Math.random() * 10000).toString().padStart(4, "0");
    return `RJ${year}${month}${day}${random}`;
  };

  // Save referral
  const handleSaveReferral = async (status: ReferralStatus = "draft") => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    const token = localStorage.getItem("staff_access_token");

    try {
      const vitalSigns: VitalSigns = {
        blood_pressure_systolic: systolicBP ? parseInt(systolicBP) : undefined,
        blood_pressure_diastolic: diastolicBP ? parseInt(diastolicBP) : undefined,
        heart_rate: heartRate ? parseInt(heartRate) : undefined,
        respiratory_rate: respiratoryRate ? parseInt(respiratoryRate) : undefined,
        temperature: temperature ? parseFloat(temperature) : undefined,
        oxygen_saturation: oxygenSaturation ? parseInt(oxygenSaturation) : undefined,
      };

      let bpjsDetails: BPJSReferralDetails | undefined;
      if (referralType === "BPJS") {
        bpjsDetails = {
          bpjs_referral_number: bpjsReferralNumber || generateReferralNumber(),
          referral_type: "rujuk_spesialis",
          tier: "tier_2",
          referring_facility_code: "00001", // Would come from hospital config
          destination_facility_code: bpjsFacilityCode,
          diagnosis_code: bpjsDiagnosisCode || primaryDiagnosisCode,
          procedure_code: bpjsProcedureCode,
          poli_name: department,
          is_prb: false,
          approval_status: "pending",
        };
      }

      const payload = {
        referral_type: referralType,
        priority: priority,
        format: referralType === "BPJS" ? "bpjs" : "standard",
        patient_id: selectedPatient!.id,
        doctor_id: 1, // Would come from logged-in user
        referral_date: referralDate,
        valid_from: validFrom,
        valid_until: validUntil,
        reason_for_referral: referralReason,
        reason_details: clinicalSummary,

        // Destination
        destination_type: referralType === "INTERNAL" ? "internal" : "external",
        destination_facility_id: selectedFacility?.id,
        internal_department_id: referralType === "INTERNAL" ? 1 : undefined,

        // BPJS information (if applicable)
        bpjs_details: bpjsDetails,

        // Clinical information
        primary_diagnosis: primaryDiagnosis,
        primary_diagnosis_code: primaryDiagnosisCode,
        secondary_diagnoses: secondaryDiagnoses.length > 0 ? secondaryDiagnoses : undefined,
        chief_complaint: chiefComplaint,
        history_present_illness: clinicalSummary,
        physical_examination: physicalExamination,
        vital_signs: vitalSigns,
        lab_findings: labResults,
        imaging_findings: imagingResults,
        treatment_given: treatmentGiven,
        treatment_response: currentMedications,
        severity: severity,
        clinical_notes: clinicalSummary,

        status: status,
        is_urgent: priority === "URGENT",
        is_emergency: priority === "EMERGENCY",
      };

      const response = await fetch("/api/v1/referrals", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Gagal menyimpan rujukan");
      }

      const data = await response.json();
      setSuccessMessage(
        status === "draft" ? "Draft rujukan berhasil disimpan" : "Rujukan berhasil dibuat"
      );

      setTimeout(() => {
        router.push(`/app/referrals/${data.referral_id}`);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan rujukan");
    } finally {
      setLoading(false);
    }
  };

  // Print referral
  const handlePrint = () => {
    window.print();
  };

  // Download PDF
  const handleDownloadPDF = () => {
    // In a real app, this would generate a PDF using a library like jsPDF
    alert("Fitur download PDF akan segera tersedia");
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Buat Surat Rujukan Baru</h1>
          <p className="text-gray-600 mt-1">Buat surat rujukan untuk pasien</p>
        </div>
        <button
          onClick={() => router.push("/app/referrals")}
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

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-semibold text-red-800 mb-2">Mohon lengkapi field berikut:</h3>
          <ul className="list-disc list-inside text-red-700 space-y-1">
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
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

      {/* Referral Type and Priority Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Jenis Rujukan</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Jenis Rujukan <span className="text-red-600">*</span>
            </label>
            <select
              value={referralType}
              onChange={(e) => setReferralType(e.target.value as ReferralType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {REFERRAL_TYPE_OPTIONS.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label_indonesian}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prioritas <span className="text-red-600">*</span>
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as ReferralPriority)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {REFERRAL_PRIORITY_OPTIONS.map((prio) => (
                <option key={prio.value} value={prio.value}>
                  {prio.label_indonesian}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tanggal Rujukan <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              value={referralDate}
              onChange={(e) => setReferralDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Berlaku Dari <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              value={validFrom}
              onChange={(e) => setValidFrom(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Berlaku Sampai <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              value={validUntil}
              onChange={(e) => setValidUntil(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Patient Information Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Pasien</h2>

        <div className="relative mb-4">
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
          <div className="mb-4 border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-64 overflow-y-auto">
            {patientSearchResults.map((patient) => (
              <button
                key={patient.id}
                onClick={() => handleSelectPatient(patient)}
                className="w-full px-4 py-3 hover:bg-gray-50 text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{patient.name}</p>
                    <p className="text-sm text-gray-600">
                      {patient.medical_record_number} • {calculateAge(patient.date_of_birth)} tahun •{" "}
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
          <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                <div>
                  <p className="text-sm text-gray-500">Nama Pasien</p>
                  <p className="font-semibold text-gray-900">{selectedPatient.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">No. Rekam Medis</p>
                  <p className="font-medium text-gray-900">{selectedPatient.medical_record_number}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Tanggal Lahir</p>
                  <p className="font-medium text-gray-900">
                    {new Date(selectedPatient.date_of_birth).toLocaleDateString("id-ID")}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Usia</p>
                  <p className="font-medium text-gray-900">{calculateAge(selectedPatient.date_of_birth)} tahun</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Jenis Kelamin</p>
                  <p className="font-medium text-gray-900">
                    {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">No. Telepon</p>
                  <p className="font-medium text-gray-900">{selectedPatient.phone}</p>
                </div>
                <div className="md:col-span-2">
                  <p className="text-sm text-gray-500">Alamat</p>
                  <p className="font-medium text-gray-900">
                    {selectedPatient.address}, {selectedPatient.city}, {selectedPatient.province}
                  </p>
                </div>

                {selectedPatient.bpjs_number && (
                  <div className="md:col-span-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700">
                      BPJS: {selectedPatient.bpjs_number} (Kelas {selectedPatient.bpjs_class})
                    </span>
                  </div>
                )}

                {selectedPatient.insurance_provider && (
                  <div className="md:col-span-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700">
                      Asuransi: {selectedPatient.insurance_provider} - {selectedPatient.insurance_policy_number}
                    </span>
                  </div>
                )}
              </div>
              <button
                onClick={() => {
                  setSelectedPatient(null);
                  setValidationErrors([]);
                }}
                className="ml-4 text-gray-400 hover:text-red-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Destination Facility Section */}
      {referralType !== "INTERNAL" && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Fasilitas Tujuan</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Jenis Fasilitas <span className="text-red-600">*</span>
              </label>
              <select
                value={facilityType}
                onChange={(e) => {
                  setFacilityType(e.target.value as FacilityType);
                  setSelectedFacility(null);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {FACILITY_TYPE_OPTIONS.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label_indonesian}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nama Fasilitas <span className="text-red-600">*</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Cari nama fasilitas..."
                  value={facilitySearchQuery}
                  onChange={(e) => setFacilitySearchQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  disabled={!!selectedFacility}
                />
                {searchingFacility && (
                  <div className="absolute right-3 top-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
                  </div>
                )}
              </div>

              {/* Facility Search Results */}
              {showFacilityResults && facilitySearchResults.length > 0 && (
                <div className="mt-2 border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-48 overflow-y-auto">
                  {facilitySearchResults.map((facility) => (
                    <button
                      key={facility.id}
                      onClick={() => handleSelectFacility(facility)}
                      className="w-full px-3 py-2 hover:bg-gray-50 text-left text-sm"
                    >
                      <p className="font-medium text-gray-900">{facility.facility_name}</p>
                      <p className="text-gray-600">
                        {facility.city}, {facility.province}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Departemen/Unit</label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="Contoh: Poli Penyakit Dalam"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Spesialisasi</label>
              <select
                value={specialization}
                onChange={(e) => setSpecialization(e.target.value as SpecializationCategory | "")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Pilih Spesialisasi</option>
                {SPECIALIZATION_CATEGORY_OPTIONS.map((spec) => (
                  <option key={spec.value} value={spec.value}>
                    {spec.label_indonesian}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Dokter Tujuan (Opsional)</label>
              <input
                type="text"
                value={targetDoctor}
                onChange={(e) => setTargetDoctor(e.target.value)}
                placeholder="Nama dokter spesialis"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">No. Telepon</label>
              <input
                type="tel"
                value={contactPhone}
                onChange={(e) => setContactPhone(e.target.value)}
                placeholder="No. telepon fasilitas"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Selected Facility Card */}
          {selectedFacility && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">{selectedFacility.facility_name}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {selectedFacility.address}, {selectedFacility.city}, {selectedFacility.province}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Telepon: {selectedFacility.phone}
                  </p>
                  {selectedFacility.bpjs_facility_code && (
                    <div className="mt-2">
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700">
                        BPJS: {selectedFacility.bpjs_facility_code}
                        {selectedFacility.is_bpjs_accredited && " (Akreditasi)"}
                      </span>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => {
                    setSelectedFacility(null);
                    setFacilitySearchQuery("");
                  }}
                  className="ml-4 text-gray-400 hover:text-red-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Clinical Information Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Klinis</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Diagnosis Utama <span className="text-red-600">*</span>
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              <input
                type="text"
                value={primaryDiagnosisCode}
                onChange={(e) => setPrimaryDiagnosisCode(e.target.value)}
                placeholder="Kode ICD-10 (Opsional)"
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
              />
              <input
                type="text"
                value={primaryDiagnosis}
                onChange={(e) => setPrimaryDiagnosis(e.target.value)}
                placeholder="Nama diagnosis"
                className="md:col-span-2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosis Sekunder</label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={secondaryDiagnosisInput}
                onChange={(e) => setSecondaryDiagnosisInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAddSecondaryDiagnosis()}
                placeholder="Tambah diagnosis sekunder"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <button
                onClick={handleAddSecondaryDiagnosis}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Tambah
              </button>
            </div>
            {secondaryDiagnoses.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {secondaryDiagnoses.map((diagnosis, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700"
                  >
                    {diagnosis}
                    <button
                      onClick={() => handleRemoveSecondaryDiagnosis(index)}
                      className="ml-2 text-gray-400 hover:text-red-600"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Keluhan Utama <span className="text-red-600">*</span>
            </label>
            <textarea
              rows={3}
              value={chiefComplaint}
              onChange={(e) => setChiefComplaint(e.target.value)}
              placeholder="Keluhan utama pasien"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pemeriksaan Fisik</label>
            <textarea
              rows={3}
              value={physicalExamination}
              onChange={(e) => setPhysicalExamination(e.target.value)}
              placeholder="Hasil pemeriksaan fisik"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tanda Vital</label>
            <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Tekanan Darah (mmHg)</label>
                <div className="flex space-x-1">
                  <input
                    type="number"
                    value={systolicBP}
                    onChange={(e) => setSystolicBP(e.target.value)}
                    placeholder="Sistolik"
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                  <input
                    type="number"
                    value={diastolicBP}
                    onChange={(e) => setDiastolicBP(e.target.value)}
                    placeholder="Diastolik"
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Nadi (bpm)</label>
                <input
                  type="number"
                  value={heartRate}
                  onChange={(e) => setHeartRate(e.target.value)}
                  placeholder="bpm"
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Pernapasan (x/menit)</label>
                <input
                  type="number"
                  value={respiratoryRate}
                  onChange={(e) => setRespiratoryRate(e.target.value)}
                  placeholder="x/menit"
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Suhu (°C)</label>
                <input
                  type="number"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(e.target.value)}
                  placeholder="°C"
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">SpO2 (%)</label>
                <input
                  type="number"
                  value={oxygenSaturation}
                  onChange={(e) => setOxygenSaturation(e.target.value)}
                  placeholder="%"
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value as "mild" | "moderate" | "severe" | "critical")}
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                >
                  <option value="mild">Ringan</option>
                  <option value="moderate">Sedang</option>
                  <option value="severe">Berat</option>
                  <option value="critical">Kritis</option>
                </select>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Hasil Laboratorium</label>
            <textarea
              rows={2}
              value={labResults}
              onChange={(e) => setLabResults(e.target.value)}
              placeholder="Hasil pemeriksaan laboratorium (jika ada)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Hasil Radiologi</label>
            <textarea
              rows={2}
              value={imagingResults}
              onChange={(e) => setImagingResults(e.target.value)}
              placeholder="Hasil pemeriksaan radiologi (jika ada)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pengobatan yang Diberikan</label>
            <textarea
              rows={2}
              value={treatmentGiven}
              onChange={(e) => setTreatmentGiven(e.target.value)}
              placeholder="Ringkasan pengobatan yang telah diberikan"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Obat Saat Ini</label>
            <textarea
              rows={2}
              value={currentMedications}
              onChange={(e) => setCurrentMedications(e.target.value)}
              placeholder="Daftar obat yang sedang dikonsumsi pasien"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Referral Reason Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Alasan Rujukan</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Alasan Rujukan <span className="text-red-600">*</span>
            </label>
            <textarea
              rows={4}
              value={referralReason}
              onChange={(e) => setReferralReason(e.target.value)}
              placeholder="Jelaskan alasan rujukan secara detail"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ringkasan Klinis</label>
            <textarea
              rows={4}
              value={clinicalSummary}
              onChange={(e) => setClinicalSummary(e.target.value)}
              placeholder="Ringkasan klinis pasien untuk dokter tujuan"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* BPJS Information Section */}
      {referralType === "BPJS" && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi BPJS</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nomor Rujukan BPJS
              </label>
              <input
                type="text"
                value={bpjsReferralNumber}
                onChange={(e) => setBpjsReferralNumber(e.target.value)}
                placeholder="Auto-generated atau input manual"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Kode Faskes BPJS Tujuan <span className="text-red-600">*</span>
              </label>
              <input
                type="text"
                value={bpjsFacilityCode}
                onChange={(e) => setBpjsFacilityCode(e.target.value)}
                placeholder="Kode faskes BPJS"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Kode Diagnosis BPJS
              </label>
              <input
                type="text"
                value={bpjsDiagnosisCode}
                onChange={(e) => setBpjsDiagnosisCode(e.target.value)}
                placeholder="Kode diagnosis ICD-10 untuk BPJS"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Kode Prosedur BPJS
              </label>
              <input
                type="text"
                value={bpjsProcedureCode}
                onChange={(e) => setBpjsProcedureCode(e.target.value)}
                placeholder="Kode prosedur (jika ada)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
              />
            </div>

            <div className="md:col-span-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={investigationRequired}
                  onChange={(e) => setInvestigationRequired(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-sm font-medium text-gray-700">Investigasi Diperlukan</span>
              </label>
            </div>
          </div>

          {selectedPatient?.bpjs_number && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm font-medium text-green-800">
                Status BPJS: Aktif ({selectedPatient.bpjs_number})
              </p>
              <p className="text-xs text-green-600 mt-1">
                Kelas {selectedPatient.bpjs_class} - Peserta dapat dirujuk
              </p>
            </div>
          )}
        </div>
      )}

      {/* Doctor Information Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Dokter Perujuk</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nama Dokter <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              value={doctorName}
              onChange={(e) => setDoctorName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nomor SIP <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              value={doctorSIP}
              onChange={(e) => setDoctorSIP(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Departemen/Unit</label>
            <input
              type="text"
              value={doctorDepartment}
              onChange={(e) => setDoctorDepartment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Kontak</label>
            <input
              type="tel"
              value={doctorContact}
              onChange={(e) => setDoctorContact(e.target.value)}
              placeholder="No. telepon dokter"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Preview Section */}
      {showPreview && selectedPatient && (
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-xl font-bold text-center text-gray-900 mb-6">SURAT RUJUKAN</h2>
          <div className="text-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">RUMAH SAKIT SIMRS</h3>
            <p className="text-sm text-gray-600">Jl. Kesehatan No. 123, Jakarta</p>
            <p className="text-sm text-gray-600">Telp: (021) 1234567</p>
          </div>

          <div className="border-t border-gray-300 pt-4 space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-gray-600">Nomor Rujukan:</p>
                <p className="font-medium">{generateReferralNumber()}</p>
              </div>
              <div>
                <p className="text-gray-600">Tanggal Rujukan:</p>
                <p className="font-medium">{new Date(referralDate).toLocaleDateString("id-ID")}</p>
              </div>
            </div>

            <div className="border-t pt-3 mt-3">
              <h4 className="font-semibold text-gray-900 mb-2">Informasi Pasien</h4>
              <div className="grid grid-cols-2 gap-2">
                <p><span className="text-gray-600">Nama:</span> {selectedPatient.name}</p>
                <p><span className="text-gray-600">No RM:</span> {selectedPatient.medical_record_number}</p>
                <p><span className="text-gray-600">Tanggal Lahir:</span> {new Date(selectedPatient.date_of_birth).toLocaleDateString("id-ID")}</p>
                <p><span className="text-gray-600">Jenis Kelamin:</span> {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}</p>
                <p className="col-span-2"><span className="text-gray-600">Alamat:</span> {selectedPatient.address}, {selectedPatient.city}</p>
              </div>
            </div>

            <div className="border-t pt-3 mt-3">
              <h4 className="font-semibold text-gray-900 mb-2">Diagnosis</h4>
              <p><span className="text-gray-600">Utama:</span> {primaryDiagnosis} {primaryDiagnosisCode && `(${primaryDiagnosisCode})`}</p>
              {secondaryDiagnoses.length > 0 && (
                <p><span className="text-gray-600">Sekunder:</span> {secondaryDiagnoses.join(", ")}</p>
              )}
            </div>

            <div className="border-t pt-3 mt-3">
              <h4 className="font-semibold text-gray-900 mb-2">Keluhan Utama</h4>
              <p>{chiefComplaint}</p>
            </div>

            <div className="border-t pt-3 mt-3">
              <h4 className="font-semibold text-gray-900 mb-2">Alasan Rujukan</h4>
              <p>{referralReason}</p>
            </div>

            {referralType !== "INTERNAL" && selectedFacility && (
              <div className="border-t pt-3 mt-3">
                <h4 className="font-semibold text-gray-900 mb-2">Fasilitas Tujuan</h4>
                <p>{selectedFacility.facility_name}</p>
                <p className="text-gray-600">{selectedFacility.address}, {selectedFacility.city}</p>
              </div>
            )}

            <div className="border-t pt-3 mt-3">
              <h4 className="font-semibold text-gray-900 mb-2">Dokter Perujuk</h4>
              <p>{doctorName}</p>
              <p className="text-gray-600">SIP: {doctorSIP}</p>
              <p className="text-gray-600">{doctorDepartment}</p>
            </div>
          </div>

          <div className="border-t pt-6 mt-6 flex justify-between">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-16">Pasien</p>
              <p className="border-t pt-2">( ........................ )</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-16">Dokter Perujuk</p>
              <p className="border-t pt-2">{doctorName}</p>
              <p className="text-xs text-gray-600">SIP: {doctorSIP}</p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 justify-end sticky bottom-0 bg-white py-4 border-t">
        <button
          onClick={() => router.push("/app/referrals")}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Batal
        </button>
        <button
          onClick={() => setShowPreview(!showPreview)}
          className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          {showPreview ? "Sembunyikan Preview" : "Preview Rujukan"}
        </button>
        <button
          onClick={handlePrint}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Print
        </button>
        <button
          onClick={handleDownloadPDF}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Download PDF
        </button>
        <button
          onClick={() => handleSaveReferral("draft")}
          disabled={loading}
          className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50"
        >
          {loading ? "Menyimpan..." : "Simpan Draft"}
        </button>
        <button
          onClick={() => handleSaveReferral("approved")}
          disabled={loading}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? "Menyimpan..." : "Buat & Cetak Rujukan"}
        </button>
      </div>
    </div>
  );
}
