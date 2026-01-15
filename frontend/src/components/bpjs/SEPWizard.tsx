"use client";

import React, { useState } from "react";
import { ChevronLeft, ChevronRight, CheckCircle, Clock, AlertCircle, Loader2, FileText, Calendar, User, Stethoscope } from "lucide-react";
import { FormInput } from "@/components/ui/form/FormInput";
import { FormSelect } from "@/components/ui/form/FormSelect";
import { FormTextarea } from "@/components/ui/form/FormTextarea";
import { BPJSData } from "@/types";
import { Badge } from "@/components/ui/Badge";

// ============================================================================
// TYPES
// ============================================================================

export interface SEPWizardProps {
  bpjsData?: BPJSData;
  onSubmit?: (sepData: SEPFormData) => void;
  onCancel?: () => void;
  className?: string;
}

export interface SEPFormData {
  // Step 1: Patient Information (from BPJS)
  patientName: string;
  bpjsCardNumber: string;
  nik: string;

  // Step 2: Service Information
  sepDate: string;
  serviceType: "RJ" | "RI"; // Rawat Jalan / Rawat Inap
  ppkCode: string;
  polyclinicCode: string;
  treatmentClass: string;

  // Step 3: Diagnosis
  initialDiagnosisCode: string;
  initialDiagnosisName: string;

  // Step 4: Doctor
  doctorCode: string;
  doctorName: string;

  // Step 5: Additional Info
  referralNumber?: string;
  referralPPKCode?: string;
  patientPhone: string;
  isExecutive: boolean;
  cobFlag?: boolean;
  notes: string;
}

type WizardStep = 1 | 2 | 3 | 4 | 5;

// ============================================================================
// MOCK DATA
// ============================================================================

const SERVICE_TYPE_OPTIONS = [
  { value: "RJ", label: "Rawat Jalan" },
  { value: "RI", label: "Rawat Inap" },
];

const POLYCLINIC_OPTIONS = [
  { value: "INT", label: "Poli Penyakit Dalam" },
  { value: "ANA", label: "Poli Anak" },
  { value: "OBG", label: "Poli Kandungan" },
  { value: "BED", label: "Poli Bedah" },
  { value: "MAT", label: "Poli Mata" },
  { value: "THT", label: "Poli THT" },
  { value: "JANTUNG", label: "Poli Jantung" },
  { value: "SYARAF", label: "Peli Syaraf" },
  { value: "PARU", label: "Poli Paru" },
  { value: "GIGI", label: "Poli Gigi" },
];

const TREATMENT_CLASS_OPTIONS = [
  { value: "K1", label: "Kelas 1" },
  { value: "K2", label: "Kelas 2" },
  { value: "K3", label: "Kelas 3" },
];

const DIAGNOSIS_OPTIONS = [
  { value: "A00", label: "A00 - Kolera" },
  { value: "A01", label: "A01 - Tifus dan Paratifus" },
  { value: "A02", label: "A02 - Infeksi Salmonella lainnya" },
  { value: "A03", label: "A03 - Shigellosis" },
  { value: "A04", label: "A04 - Infeksi bakteri intestinus lain" },
  { value: "A05", label: "A05 - Keracunan makanan bakteri lain" },
  { value: "A06", label: "A06 - Amebiasis" },
  { value: "A07", label: "A07 - Diare entritis lain" },
  { value: "A08", label: "A08 - Diare karena infeksi viral" },
  { value: "A09", label: "A09 - Diare dan gastroenteritis" },
  { value: "I10", label: "I10 - Hipertensi esensial" },
  { value: "I11", label: "I11 - Hipertensi penyakit jantung" },
  { value: "I20", label: "I20 - Angina pektoris" },
  { value: "I21", label: "I21 - Infark miokard akut" },
  { value: "I50", label: "I50 - Gagal jantung" },
  { value: "J00", label: "J00 - Nasofaringitis akut" },
  { value: "J01", label: "J01 - Sinusitis akut" },
  { value: "J02", label: "J02 - Faringitis akut" },
  { value: "J03", label: "J03 - Tonsilitis akut" },
  { value: "J18", label: "J18 - Pneumonia" },
];

const DOCTOR_OPTIONS = [
  { value: "DR001", label: "dr. Budi Santoso, Sp.PD" },
  { value: "DR002", label: "dr. Siti Aminah, Sp.A" },
  { value: "DR003", label: "dr. Ahmad Hidayat, Sp.B" },
  { value: "DR004", label: "dr. Dewi Sartika, Sp.OG" },
  { value: "DR005", label: "dr. Eko Prasetyo, Sp.M" },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function SEPWizard({ bpjsData, onSubmit, onCancel, className = "" }: SEPWizardProps) {
  const [currentStep, setCurrentStep] = useState<WizardStep>(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sepData, setSepData] = useState<SEPFormData>({
    // Step 1: Auto-populated from BPJS
    patientName: bpjsData?.nama || "",
    bpjsCardNumber: bpjsData?.cardNumber || "",
    nik: bpjsData?.nik || "",
    // Step 2
    sepDate: new Date().toISOString().split("T")[0],
    serviceType: "RJ",
    ppkCode: "12345678", // Default PPK code
    polyclinicCode: "",
    treatmentClass: "K3",
    // Step 3
    initialDiagnosisCode: "",
    initialDiagnosisName: "",
    // Step 4
    doctorCode: "",
    doctorName: "",
    // Step 5
    referralNumber: "",
    referralPPKCode: "",
    patientPhone: "",
    isExecutive: false,
    cobFlag: false,
    notes: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [validationResult, setValidationResult] = useState<{
    isValid: boolean;
    message: string;
  } | null>(null);

  // Auto-populate when BPJS data changes
  React.useEffect(() => {
    if (bpjsData) {
      setSepData(prev => ({
        ...prev,
        patientName: bpjsData.nama,
        bpjsCardNumber: bpjsData.cardNumber,
        nik: bpjsData.nik,
      }));
    }
  }, [bpjsData]);

  const handleNext = () => {
    const stepErrors = validateStep(currentStep);
    if (Object.keys(stepErrors).length === 0) {
      if (currentStep < 5) {
        setCurrentStep((currentStep + 1) as WizardStep);
        setErrors({});
      }
    } else {
      setErrors(stepErrors);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((currentStep - 1) as WizardStep);
      setErrors({});
    }
  };

  const validateStep = (step: WizardStep): Record<string, string> => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!sepData.patientName.trim()) newErrors.patientName = "Nama pasien wajib diisi";
        if (!sepData.bpjsCardNumber.trim()) newErrors.bpjsCardNumber = "Nomor kartu BPJS wajib diisi";
        if (!sepData.nik.trim()) newErrors.nik = "NIK wajib diisi";
        break;

      case 2:
        if (!sepData.sepDate) newErrors.sepDate = "Tanggal SEP wajib diisi";
        if (!sepData.serviceType) newErrors.serviceType = "Jenis pelayanan wajib dipilih";
        if (!sepData.polyclinicCode) newErrors.polyclinicCode = "Poli wajib dipilih";
        if (!sepData.treatmentClass) newErrors.treatmentClass = "Kelas rawat wajib dipilih";
        break;

      case 3:
        if (!sepData.initialDiagnosisCode) newErrors.initialDiagnosisCode = "Kode diagnosis wajib diisi";
        if (!sepData.initialDiagnosisName.trim()) newErrors.initialDiagnosisName = "Nama diagnosis wajib diisi";
        break;

      case 4:
        if (!sepData.doctorCode) newErrors.doctorCode = "Dokter wajib dipilih";
        if (!sepData.doctorName.trim()) newErrors.doctorName = "Nama dokter wajib diisi";
        break;

      case 5:
        if (!sepData.patientPhone.trim()) newErrors.patientPhone = "No. telepon pasien wajib diisi";
        break;
    }

    return newErrors;
  };

  const handleSubmit = async () => {
    setErrors({});
    setIsSubmitting(true);

    // Validate final step
    const stepErrors = validateStep(5);
    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors);
      setIsSubmitting(false);
      return;
    }

    // Simulate BPJS validation
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Mock validation result
    const validation = {
      isValid: true,
      message: "SEP berhasil dibuat. Nomor SEP: 1234567890123456",
    };

    setValidationResult(validation);

    if (validation.isValid) {
      onSubmit?.(sepData);
    }

    setIsSubmitting(false);
  };

  const updateField = (field: keyof SEPFormData, value: any) => {
    setSepData(prev => ({ ...prev, [field]: value }));
    // Clear error when field is updated
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const getStepIcon = (step: WizardStep) => {
    if (step < currentStep) {
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    }
    if (step === currentStep) {
      return <div className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-bold">{step}</div>;
    }
    return <div className="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center text-gray-500 text-sm font-medium">{step}</div>;
  };

  const getStepTitle = (step: WizardStep): string => {
    const titles = {
      1: "Informasi Pasien",
      2: "Pelayanan",
      3: "Diagnosis",
      4: "Dokter",
      5: "Konfirmasi",
    };
    return titles[step];
  };

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Buat SEP Baru</h3>
            <p className="text-sm text-gray-600">Surat Eligibilitas Peserta BPJS</p>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="px-6 pt-6">
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4, 5].map((step) => (
            <React.Fragment key={step}>
              <div className="flex flex-col items-center">
                {getStepIcon(step as WizardStep)}
                <p className={`text-xs mt-2 ${step === currentStep ? "font-semibold text-blue-600" : "text-gray-500"}`}>
                  {getStepTitle(step as WizardStep)}
                </p>
              </div>
              {step < 5 && (
                <div className={`flex-1 h-0.5 mx-2 ${step < currentStep ? "bg-green-500" : "bg-gray-200"}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="p-6">
        {currentStep === 1 && (
          <Step1PatientInfo
            sepData={sepData}
            errors={errors}
            updateField={updateField}
            bpjsData={bpjsData}
          />
        )}

        {currentStep === 2 && (
          <Step2Service
            sepData={sepData}
            errors={errors}
            updateField={updateField}
          />
        )}

        {currentStep === 3 && (
          <Step3Diagnosis
            sepData={sepData}
            errors={errors}
            updateField={updateField}
          />
        )}

        {currentStep === 4 && (
          <Step4Doctor
            sepData={sepData}
            errors={errors}
            updateField={updateField}
          />
        )}

        {currentStep === 5 && (
          <Step5Confirm
            sepData={sepData}
            errors={errors}
            updateField={updateField}
            validationResult={validationResult}
            isSubmitting={isSubmitting}
          />
        )}
      </div>

      {/* Action Buttons */}
      <div className="px-6 pb-6 flex justify-between">
        <button
          type="button"
          onClick={() => {
            handleBack();
            onCancel?.();
          }}
          disabled={currentStep === 1}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <ChevronLeft className="w-4 h-4" />
          {currentStep === 1 ? "Batal" : "Kembali"}
        </button>

        {currentStep < 5 ? (
          <button
            type="button"
            onClick={handleNext}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            Lanjut
            <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting || !!validationResult?.isValid}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Memproses...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4" />
                Buat SEP
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// STEP COMPONENTS
// ============================================================================

function Step1PatientInfo({
  sepData,
  errors,
  updateField,
  bpjsData,
}: {
  sepData: SEPFormData;
  errors: Record<string, string>;
  updateField: (field: keyof SEPFormData, value: any) => void;
  bpjsData?: BPJSData;
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <User className="w-5 h-5 text-blue-600" />
        <h4 className="text-lg font-semibold text-gray-900">Informasi Pasien (Dari BPJS)</h4>
      </div>

      {bpjsData && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <p className="text-sm font-medium text-green-900">Data tersinkronisasi dari BPJS</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormInput
          label="Nama Peserta"
          value={sepData.patientName}
          onChange={(e) => updateField("patientName", e.target.value)}
          error={errors.patientName}
          disabled
          hint="Dari data BPJS"
        />

        <FormInput
          label="Nomor Kartu BPJS"
          value={sepData.bpjsCardNumber}
          onChange={(e) => updateField("bpjsCardNumber", e.target.value)}
          error={errors.bpjsCardNumber}
          disabled
          hint="Dari data BPJS"
        />

        <FormInput
          label="NIK"
          value={sepData.nik}
          onChange={(e) => updateField("nik", e.target.value)}
          error={errors.nik}
          disabled
          hint="Dari data BPJS"
        />
      </div>
    </div>
  );
}

function Step2Service({
  sepData,
  errors,
  updateField,
}: {
  sepData: SEPFormData;
  errors: Record<string, string>;
  updateField: (field: keyof SEPFormData, value: any) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="w-5 h-5 text-blue-600" />
        <h4 className="text-lg font-semibold text-gray-900">Informasi Pelayanan</h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormInput
          label="Tanggal SEP"
          type="date"
          value={sepData.sepDate}
          onChange={(e) => updateField("sepDate", e.target.value)}
          error={errors.sepDate}
        />

        <FormSelect
          label="Jenis Pelayanan"
          options={SERVICE_TYPE_OPTIONS}
          value={sepData.serviceType}
          onChange={(e) => updateField("serviceType", e.target.value)}
          error={errors.serviceType}
        />

        <FormSelect
          label="Poli"
          options={POLYCLINIC_OPTIONS}
          value={sepData.polyclinicCode}
          onChange={(e) => updateField("polyclinicCode", e.target.value)}
          error={errors.polyclinicCode}
          hint="Pilih poli tujuan"
        />

        <FormSelect
          label="Kelas Rawat"
          options={TREATMENT_CLASS_OPTIONS}
          value={sepData.treatmentClass}
          onChange={(e) => updateField("treatmentClass", e.target.value)}
          error={errors.treatmentClass}
          hint="Kelas perawatan"
        />
      </div>
    </div>
  );
}

function Step3Diagnosis({
  sepData,
  errors,
  updateField,
}: {
  sepData: SEPFormData;
  errors: Record<string, string>;
  updateField: (field: keyof SEPFormData, value: any) => void;
}) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredDiagnoses = DIAGNOSIS_OPTIONS.filter(d =>
    d.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.value.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <Stethoscope className="w-5 h-5 text-blue-600" />
        <h4 className="text-lg font-semibold text-gray-900">Diagnosis Awal</h4>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Cari Diagnosis</label>
        <input
          type="text"
          placeholder="Cari berdasarkan kode atau nama diagnosis..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <FormSelect
        label="Diagnosis (ICD-10)"
        options={searchTerm ? filteredDiagnoses : DIAGNOSIS_OPTIONS}
        value={sepData.initialDiagnosisCode}
          onChange={(e) => {
            const selected = DIAGNOSIS_OPTIONS.find(d => d.value === e.target.value);
            updateField("initialDiagnosisCode", e.target.value);
            if (selected) {
              updateField("initialDiagnosisName", selected.label);
            }
          }}
        error={errors.initialDiagnosisCode}
        hint={sepData.initialDiagnosisName || "Pilih diagnosis awal"}
      />
    </div>
  );
}

function Step4Doctor({
  sepData,
  errors,
  updateField,
}: {
  sepData: SEPFormData;
  errors: Record<string, string>;
  updateField: (field: keyof SEPFormData, value: any) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <Stethoscope className="w-5 h-5 text-blue-600" />
        <h4 className="text-lg font-semibold text-gray-900">Dokter Penanggung Jawab</h4>
      </div>

      <FormSelect
        label="Dokter"
        options={DOCTOR_OPTIONS}
        value={sepData.doctorCode}
        onChange={(e) => {
          const selected = DOCTOR_OPTIONS.find(d => d.value === e.target.value);
          updateField("doctorCode", e.target.value);
          if (selected) {
            updateField("doctorName", selected.label);
          }
        }}
        error={errors.doctorCode}
        hint="Dokter yang akan menangani pasien"
      />
    </div>
  );
}

function Step5Confirm({
  sepData,
  errors,
  updateField,
  validationResult,
  isSubmitting,
}: {
  sepData: SEPFormData;
  errors: Record<string, string>;
  updateField: (field: keyof SEPFormData, value: any) => void;
  validationResult: { isValid: boolean; message: string } | null;
  isSubmitting: boolean;
}) {
  const serviceTypeLabel = sepData.serviceType === "RJ" ? "Rawat Jalan" : "Rawat Inap";
  const treatmentClassLabel = {
    K1: "Kelas 1",
    K2: "Kelas 2",
    K3: "Kelas 3",
  }[sepData.treatmentClass];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-blue-600" />
        <h4 className="text-lg font-semibold text-gray-900">Konfirmasi Data SEP</h4>
      </div>

      {/* Summary */}
      <div className="bg-gray-50 rounded-lg p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500">Nama Peserta</p>
            <p className="text-sm font-medium text-gray-900">{sepData.patientName}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">No. Kartu BPJS</p>
            <p className="text-sm font-medium text-gray-900">{sepData.bpjsCardNumber}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Tanggal SEP</p>
            <p className="text-sm font-medium text-gray-900">
              {new Date(sepData.sepDate).toLocaleDateString("id-ID", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Jenis Pelayanan</p>
            <p className="text-sm font-medium text-gray-900">{serviceTypeLabel}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Poli</p>
            <p className="text-sm font-medium text-gray-900">
              {POLYCLINIC_OPTIONS.find(p => p.value === sepData.polyclinicCode)?.label}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Kelas Rawat</p>
            <p className="text-sm font-medium text-gray-900">{treatmentClassLabel}</p>
          </div>
          <div className="col-span-2">
            <p className="text-xs text-gray-500">Diagnosis Awal</p>
            <p className="text-sm font-medium text-gray-900">{sepData.initialDiagnosisName}</p>
          </div>
          <div className="col-span-2">
            <p className="text-xs text-gray-500">Dokter</p>
            <p className="text-sm font-medium text-gray-900">{sepData.doctorName}</p>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      <div className="space-y-4">
        <FormInput
          label="No. Telepon Pasien"
          type="tel"
          placeholder="08xxxxxxxxxx"
          value={sepData.patientPhone}
          onChange={(e) => updateField("patientPhone", e.target.value)}
          error={errors.patientPhone}
          required
        />

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={sepData.isExecutive}
              onChange={(e) => updateField("isExecutive", e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Pasien Eksekutif</span>
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={sepData.cobFlag || false}
              onChange={(e) => updateField("cobFlag", e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">COB (Coordinate of Benefit)</span>
          </label>
        </div>

        <FormTextarea
          label="Catatan"
          placeholder="Catatan tambahan..."
          value={sepData.notes}
          onChange={(e) => updateField("notes", e.target.value)}
          rows={3}
        />
      </div>

      {/* Validation Result */}
      {validationResult && (
        <div className={`border-2 rounded-lg p-4 ${
          validationResult.isValid
            ? "bg-green-50 border-green-500"
            : "bg-red-50 border-red-500"
        }`}>
          <div className="flex items-center gap-2">
            {validationResult.isValid ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <p className={`font-medium ${
              validationResult.isValid ? "text-green-900" : "text-red-900"
            }`}>
              {validationResult.message}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

SEPWizard.displayName = "SEPWizard";
