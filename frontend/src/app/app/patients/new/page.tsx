"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  GENDER_OPTIONS,
  MARITAL_STATUS_OPTIONS,
  RELIGION_OPTIONS,
  BLOOD_TYPE_OPTIONS,
  EDUCATION_LEVEL_OPTIONS,
  OCCUPATION_OPTIONS,
  BPJS_CLASS_OPTIONS,
  INSURANCE_TYPE_OPTIONS,
  RELATIONSHIP_OPTIONS,
  VALIDATION_RULES,
  FIELD_LABELS,
} from "@/constants/patient-registration";
import type {
  PatientGender,
  MaritalStatus,
  Religion,
  BloodType,
  EducationLevel,
  BPJSStatus,
  BPJSClass,
  InsuranceCoverageType,
  EmergencyContactRelationship,
} from "@/types/patient-registration";

interface ValidationError {
  field: string;
  message: string;
}

interface DuplicatePatient {
  patient_id: number;
  medical_record_number: string;
  full_name: string;
  nik: string;
  date_of_birth: string;
  gender: PatientGender;
  phone: string;
}

export default function NewPatientPage() {
  const router = useRouter();

  // Form state
  const [fullName, setFullName] = useState("");
  const [nik, setNik] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [placeOfBirth, setPlaceOfBirth] = useState("");
  const [gender, setGender] = useState<PatientGender | "">("");
  const [bloodType, setBloodType] = useState<BloodType | "">("");
  const [maritalStatus, setMaritalStatus] = useState<MaritalStatus | "">("");
  const [religion, setReligion] = useState<Religion | "">("");
  const [occupation, setOccupation] = useState("");
  const [educationLevel, setEducationLevel] = useState<EducationLevel | "">("");

  // Contact information
  const [phoneNumber, setPhoneNumber] = useState("");
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState("");
  const [province, setProvince] = useState("");
  const [city, setCity] = useState("");
  const [district, setDistrict] = useState("");
  const [village, setVillage] = useState("");
  const [postalCode, setPostalCode] = useState("");

  // BPJS information
  const [hasBPJS, setHasBPJS] = useState(false);
  const [bpjsNumber, setBpjsNumber] = useState("");
  const [bpjsStatus, setBpjsStatus] = useState<BPJSStatus>("active");
  const [bpjsClass, setBpjsClass] = useState<BPJSClass | "">("");
  const [bpjsFacility, setBpjsFacility] = useState("");
  const [showBPJS, setShowBPJS] = useState(false);

  // Insurance information
  const [hasInsurance, setHasInsurance] = useState(false);
  const [insuranceProvider, setInsuranceProvider] = useState("");
  const [insurancePolicyNumber, setInsurancePolicyNumber] = useState("");
  const [insuranceMemberName, setInsuranceMemberName] = useState("");
  const [insuranceExpiryDate, setInsuranceExpiryDate] = useState("");
  const [insuranceType, setInsuranceType] = useState<InsuranceCoverageType>("both");
  const [showInsurance, setShowInsurance] = useState(false);

  // Emergency contact
  const [emergencyName, setEmergencyName] = useState("");
  const [emergencyRelationship, setEmergencyRelationship] = useState<EmergencyContactRelationship | "">("");
  const [emergencyPhone, setEmergencyPhone] = useState("");

  // Medical information
  const [allergies, setAllergies] = useState("");
  const [chronicConditions, setChronicConditions] = useState("");
  const [medicalNotes, setMedicalNotes] = useState("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [checkingDuplicate, setCheckingDuplicate] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [duplicateWarning, setDuplicateWarning] = useState<DuplicatePatient | null>(null);
  const [age, setAge] = useState<number | null>(null);

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  }, [router]);

  // Calculate age from date of birth
  useEffect(() => {
    if (dateOfBirth) {
      const today = new Date();
      const birthDate = new Date(dateOfBirth);
      let calculatedAge = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        calculatedAge--;
      }
      setAge(calculatedAge);
    } else {
      setAge(null);
    }
  }, [dateOfBirth]);

  // Check for duplicate patient by NIK
  useEffect(() => {
    const checkDuplicate = async () => {
      if (nik.length === 16 && VALIDATION_RULES.NIK.PATTERN.test(nik)) {
        setCheckingDuplicate(true);
        const token = localStorage.getItem("staff_access_token");

        try {
          const response = await fetch(
            `/api/v1/patients/check-duplicate?nik=${encodeURIComponent(nik)}`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (response.ok) {
            const data = await response.json();
            if (data.data?.has_duplicates && data.data?.duplicates?.length > 0) {
              setDuplicateWarning(data.data.duplicates[0]);
            } else {
              setDuplicateWarning(null);
            }
          }
        } catch (err) {
          console.error("Error checking duplicate:", err);
        } finally {
          setCheckingDuplicate(false);
        }
      } else {
        setDuplicateWarning(null);
      }
    };

    const timeoutId = setTimeout(() => {
      checkDuplicate();
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [nik]);

  // Validate form
  const validateForm = (): boolean => {
    const errors: ValidationError[] = [];

    // Patient Information validation
    if (!fullName.trim()) {
      errors.push({ field: "fullName", message: "Nama lengkap wajib diisi" });
    }

    if (!nik) {
      errors.push({ field: "nik", message: "NIK wajib diisi" });
    } else if (!VALIDATION_RULES.NIK.PATTERN.test(nik)) {
      errors.push({ field: "nik", message: VALIDATION_RULES.NIK.ERROR_MESSAGE });
    }

    if (!dateOfBirth) {
      errors.push({ field: "dateOfBirth", message: "Tanggal lahir wajib diisi" });
    }

    if (!placeOfBirth.trim()) {
      errors.push({ field: "placeOfBirth", message: "Tempat lahir wajib diisi" });
    }

    if (!gender) {
      errors.push({ field: "gender", message: "Jenis kelamin wajib dipilih" });
    }

    if (!maritalStatus) {
      errors.push({ field: "maritalStatus", message: "Status perkawinan wajib dipilih" });
    }

    if (!religion) {
      errors.push({ field: "religion", message: "Agama wajib dipilih" });
    }

    if (!occupation.trim()) {
      errors.push({ field: "occupation", message: "Pekerjaan wajib diisi" });
    }

    if (!educationLevel) {
      errors.push({ field: "educationLevel", message: "Pendidikan terakhir wajib dipilih" });
    }

    // Contact Information validation
    if (!phoneNumber) {
      errors.push({ field: "phoneNumber", message: "Nomor telepon wajib diisi" });
    } else if (!VALIDATION_RULES.PHONE.PATTERN.test(phoneNumber)) {
      errors.push({ field: "phoneNumber", message: VALIDATION_RULES.PHONE.ERROR_MESSAGE });
    }

    if (email && !VALIDATION_RULES.EMAIL.PATTERN.test(email)) {
      errors.push({ field: "email", message: VALIDATION_RULES.EMAIL.ERROR_MESSAGE });
    }

    if (!address.trim()) {
      errors.push({ field: "address", message: "Alamat wajib diisi" });
    }

    if (!province.trim()) {
      errors.push({ field: "province", message: "Provinsi wajib diisi" });
    }

    if (!city.trim()) {
      errors.push({ field: "city", message: "Kabupaten/Kota wajib diisi" });
    }

    if (!district.trim()) {
      errors.push({ field: "district", message: "Kecamatan wajib diisi" });
    }

    if (!village.trim()) {
      errors.push({ field: "village", message: "Kelurahan/Desa wajib diisi" });
    }

    if (!postalCode) {
      errors.push({ field: "postalCode", message: "Kode pos wajib diisi" });
    } else if (!VALIDATION_RULES.POSTAL_CODE.PATTERN.test(postalCode)) {
      errors.push({ field: "postalCode", message: VALIDATION_RULES.POSTAL_CODE.ERROR_MESSAGE });
    }

    // BPJS validation
    if (hasBPJS && !bpjsNumber.trim()) {
      errors.push({ field: "bpjsNumber", message: "Nomor BPJS wajib diisi" });
    }

    // Insurance validation
    if (hasInsurance) {
      if (!insuranceProvider.trim()) {
        errors.push({ field: "insuranceProvider", message: "Nama penyedia asuransi wajib diisi" });
      }
      if (!insurancePolicyNumber.trim()) {
        errors.push({ field: "insurancePolicyNumber", message: "Nomor polis wajib diisi" });
      }
    }

    // Emergency Contact validation
    if (!emergencyName.trim()) {
      errors.push({ field: "emergencyName", message: "Nama kontak darurat wajib diisi" });
    }

    if (!emergencyRelationship) {
      errors.push({ field: "emergencyRelationship", message: "Hubungan dengan pasien wajib dipilih" });
    }

    if (!emergencyPhone) {
      errors.push({ field: "emergencyPhone", message: "Nomor telepon kontak darurat wajib diisi" });
    } else if (!VALIDATION_RULES.PHONE.PATTERN.test(emergencyPhone)) {
      errors.push({ field: "emergencyPhone", message: "Nomor telepon tidak valid" });
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  // Get field error message
  const getFieldError = (field: string): string | undefined => {
    return validationErrors.find((e) => e.field === field)?.message;
  };

  // Save patient
  const handleSavePatient = async () => {
    if (!validateForm()) {
      setError("Mohon lengkapi semua field yang wajib diisi");
      return;
    }

    setLoading(true);
    setError(null);
    const token = localStorage.getItem("staff_access_token");

    try {
      const payload = {
        personal_info: {
          full_name: fullName,
          nik: nik,
          date_of_birth: dateOfBirth,
          place_of_birth: placeOfBirth,
          gender: gender,
          blood_type: bloodType || "unknown",
          marital_status: maritalStatus,
          religion: religion,
          occupation: occupation,
          education_level: educationLevel,
        },
        contact_info: {
          phone: phoneNumber,
          email: email || undefined,
          address: address,
          province: province,
          city: city,
          district: district,
          village: village,
          postal_code: postalCode,
        },
        bpjs_info: hasBPJS
          ? {
              bpjs_number: bpjsNumber,
              bpjs_status: bpjsStatus,
              health_care_class: parseInt(bpjsClass as string) as BPJSClass,
              faskes_tk1: bpjsFacility,
              is_primary_insurance: !hasInsurance,
            }
          : undefined,
        insurance_info: hasInsurance
          ? {
              provider_name: insuranceProvider,
              policy_number: insurancePolicyNumber,
              member_name: insuranceMemberName || fullName,
              insurance_type: "individual",
              coverage_type: insuranceType,
              effective_date: new Date().toISOString().split("T")[0],
              expiry_date: insuranceExpiryDate,
              is_primary_insurance: !hasBPJS,
            }
          : undefined,
        emergency_contact: {
          full_name: emergencyName,
          relationship: emergencyRelationship,
          phone: emergencyPhone,
        },
        medical_background: {
          allergies: allergies
            ? [{ allergen: allergies, type: "other" as const, severity: "mild" as const, reaction: "" }]
            : [],
          chronic_conditions: chronicConditions
            ? [{ condition_name: chronicConditions, diagnosis_date: dateOfBirth, is_active: true }]
            : [],
          blood_type: bloodType || "unknown",
          medical_notes: medicalNotes || undefined,
        },
      };

      const response = await fetch("/api/v1/patients", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Gagal membuat pasien baru" }));
        throw new Error(errorData.message || "Gagal membuat pasien baru");
      }

      const data = await response.json();
      setSuccessMessage("Pasien berhasil didaftarkan!");

      setTimeout(() => {
        router.push(`/app/patients/${data.data.patient_id}`);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal membuat pasien baru");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pendaftaran Pasien Baru</h1>
          <p className="text-gray-600 mt-1">Isi formulir untuk mendaftarkan pasien baru</p>
        </div>
        <button
          onClick={() => router.push("/app/patients")}
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

      {/* Duplicate Warning */}
      {duplicateWarning && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="flex-1">
              <p className="font-medium text-yellow-800">Peringatan: Pasien Duplikat</p>
              <p className="text-sm text-yellow-700 mt-1">
                Pasien dengan NIK ini sudah terdaftar:
              </p>
              <div className="mt-2 p-3 bg-yellow-100 rounded-lg">
                <p className="text-sm font-medium text-yellow-900">
                  {duplicateWarning.full_name} ({duplicateWarning.medical_record_number})
                </p>
                <p className="text-xs text-yellow-800 mt-1">
                  {duplicateWarning.gender === "male" ? "Laki-laki" : "Perempuan"} •{" "}
                  {new Date(duplicateWarning.date_of_birth).toLocaleDateString("id-ID")}
                </p>
              </div>
              <p className="text-sm text-yellow-700 mt-2">
                Anda dapat melanjutkan pendaftaran jika ini adalah pasien yang berbeda.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Patient Information Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Pasien</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Full Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nama Lengkap <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("fullName") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Masukkan nama lengkap sesuai KTP"
            />
            {getFieldError("fullName") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("fullName")}</p>
            )}
          </div>

          {/* NIK */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              NIK <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="text"
                value={nik}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, "").slice(0, 16);
                  setNik(value);
                }}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                  getFieldError("nik") ? "border-red-500" : "border-gray-300"
                }`}
                placeholder="16 digit NIK"
                maxLength={16}
              />
              {checkingDuplicate && (
                <div className="absolute right-3 top-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
                </div>
              )}
            </div>
            {getFieldError("nik") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("nik")}</p>
            )}
          </div>

          {/* Date of Birth */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tanggal Lahir <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={dateOfBirth}
              onChange={(e) => setDateOfBirth(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("dateOfBirth") ? "border-red-500" : "border-gray-300"
              }`}
            />
            {getFieldError("dateOfBirth") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("dateOfBirth")}</p>
            )}
            {age !== null && dateOfBirth && (
              <p className="text-sm text-gray-600 mt-1">Usia: {age} tahun</p>
            )}
          </div>

          {/* Place of Birth */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tempat Lahir <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={placeOfBirth}
              onChange={(e) => setPlaceOfBirth(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("placeOfBirth") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Masukkan tempat lahir"
            />
            {getFieldError("placeOfBirth") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("placeOfBirth")}</p>
            )}
          </div>

          {/* Gender */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Jenis Kelamin <span className="text-red-500">*</span>
            </label>
            <div className="flex space-x-4">
              {GENDER_OPTIONS.map((option) => (
                <label key={option.value} className="flex items-center">
                  <input
                    type="radio"
                    value={option.value}
                    checked={gender === option.value}
                    onChange={(e) => setGender(e.target.value as PatientGender)}
                    className="mr-2"
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
            {getFieldError("gender") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("gender")}</p>
            )}
          </div>

          {/* Blood Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Golongan Darah</label>
            <select
              value={bloodType}
              onChange={(e) => setBloodType(e.target.value as BloodType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Pilih Golongan Darah</option>
              {BLOOD_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Marital Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status Perkawinan <span className="text-red-500">*</span>
            </label>
            <select
              value={maritalStatus}
              onChange={(e) => setMaritalStatus(e.target.value as MaritalStatus)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("maritalStatus") ? "border-red-500" : "border-gray-300"
              }`}
            >
              <option value="">Pilih Status Perkawinan</option>
              {MARITAL_STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {getFieldError("maritalStatus") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("maritalStatus")}</p>
            )}
          </div>

          {/* Religion */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Agama <span className="text-red-500">*</span>
            </label>
            <select
              value={religion}
              onChange={(e) => setReligion(e.target.value as Religion)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("religion") ? "border-red-500" : "border-gray-300"
              }`}
            >
              <option value="">Pilih Agama</option>
              {RELIGION_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {getFieldError("religion") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("religion")}</p>
            )}
          </div>

          {/* Occupation */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pekerjaan <span className="text-red-500">*</span>
            </label>
            <select
              value={occupation}
              onChange={(e) => setOccupation(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("occupation") ? "border-red-500" : "border-gray-300"
              }`}
            >
              <option value="">Pilih Pekerjaan</option>
              {OCCUPATION_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {getFieldError("occupation") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("occupation")}</p>
            )}
          </div>

          {/* Education Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pendidikan Terakhir <span className="text-red-500">*</span>
            </label>
            <select
              value={educationLevel}
              onChange={(e) => setEducationLevel(e.target.value as EducationLevel)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("educationLevel") ? "border-red-500" : "border-gray-300"
              }`}
            >
              <option value="">Pilih Pendidikan</option>
              {EDUCATION_LEVEL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {getFieldError("educationLevel") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("educationLevel")}</p>
            )}
          </div>
        </div>
      </div>

      {/* Contact Information Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Kontak</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Phone Number */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nomor Telepon <span className="text-red-500">*</span>
            </label>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("phoneNumber") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Contoh: 081234567890"
            />
            {getFieldError("phoneNumber") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("phoneNumber")}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email (Opsional)</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("email") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="contoh@email.com"
            />
            {getFieldError("email") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("email")}</p>
            )}
          </div>

          {/* Address */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Alamat Lengkap <span className="text-red-500">*</span>
            </label>
            <textarea
              rows={3}
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("address") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Masukkan alamat lengkap"
            />
            {getFieldError("address") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("address")}</p>
            )}
          </div>

          {/* Province */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Provinsi <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={province}
              onChange={(e) => setProvince(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("province") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Masukkan nama provinsi"
            />
            {getFieldError("province") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("province")}</p>
            )}
          </div>

          {/* City */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kabupaten/Kota <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("city") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Masukkan nama kabupaten/kota"
            />
            {getFieldError("city") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("city")}</p>
            )}
          </div>

          {/* District */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kecamatan <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("district") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Masukkan nama kecamatan"
            />
            {getFieldError("district") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("district")}</p>
            )}
          </div>

          {/* Village */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kelurahan/Desa <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={village}
              onChange={(e) => setVillage(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("village") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Masukkan nama kelurahan/desa"
            />
            {getFieldError("village") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("village")}</p>
            )}
          </div>

          {/* Postal Code */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kode Pos <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={postalCode}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, "").slice(0, 5);
                setPostalCode(value);
              }}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("postalCode") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="5 digit kode pos"
              maxLength={5}
            />
            {getFieldError("postalCode") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("postalCode")}</p>
            )}
          </div>
        </div>
      </div>

      {/* BPJS Information Section (Collapsible) */}
      <div className="bg-white rounded-lg shadow p-6">
        <button
          onClick={() => setShowBPJS(!showBPJS)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={hasBPJS}
              onChange={(e) => {
                setHasBPJS(e.target.checked);
                if (e.target.checked) {
                  setShowBPJS(true);
                }
              }}
              className="rounded"
            />
            <h2 className="text-lg font-semibold text-gray-900">Informasi BPJS</h2>
          </div>
          <svg
            className={`w-5 h-5 text-gray-500 transition-transform ${showBPJS ? "transform rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {showBPJS && hasBPJS && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* BPJS Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nomor BPJS <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={bpjsNumber}
                onChange={(e) => setBpjsNumber(e.target.value.replace(/\D/g, ""))}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                  getFieldError("bpjsNumber") ? "border-red-500" : "border-gray-300"
                }`}
                placeholder="13 digit nomor BPJS"
              />
              {getFieldError("bpjsNumber") && (
                <p className="text-sm text-red-600 mt-1">{getFieldError("bpjsNumber")}</p>
              )}
            </div>

            {/* BPJS Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status BPJS</label>
              <select
                value={bpjsStatus}
                onChange={(e) => setBpjsStatus(e.target.value as BPJSStatus)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="active">Aktif</option>
                <option value="inactive">Tidak Aktif</option>
                <option value="expired">Kadaluarsa</option>
                <option value="suspended">Ditangguhkan</option>
              </select>
            </div>

            {/* BPJS Class */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Kelas BPJS</label>
              <select
                value={bpjsClass}
                onChange={(e) => setBpjsClass(e.target.value as BPJSClass | "")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Pilih Kelas</option>
                {BPJS_CLASS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* BPJS Facility */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Faskes (Fasilitas Kesehatan)</label>
              <input
                type="text"
                value={bpjsFacility}
                onChange={(e) => setBpjsFacility(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Nama faskes tingkat 1"
              />
            </div>
          </div>
        )}
      </div>

      {/* Insurance Information Section (Collapsible) */}
      <div className="bg-white rounded-lg shadow p-6">
        <button
          onClick={() => setShowInsurance(!showInsurance)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={hasInsurance}
              onChange={(e) => {
                setHasInsurance(e.target.checked);
                if (e.target.checked) {
                  setShowInsurance(true);
                }
              }}
              className="rounded"
            />
            <h2 className="text-lg font-semibold text-gray-900">Informasi Asuransi</h2>
          </div>
          <svg
            className={`w-5 h-5 text-gray-500 transition-transform ${showInsurance ? "transform rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {showInsurance && hasInsurance && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Insurance Provider */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nama Penyedia Asuransi <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={insuranceProvider}
                onChange={(e) => setInsuranceProvider(e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                  getFieldError("insuranceProvider") ? "border-red-500" : "border-gray-300"
                }`}
                placeholder="Nama perusahaan asuransi"
              />
              {getFieldError("insuranceProvider") && (
                <p className="text-sm text-red-600 mt-1">{getFieldError("insuranceProvider")}</p>
              )}
            </div>

            {/* Policy Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nomor Polis <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={insurancePolicyNumber}
                onChange={(e) => setInsurancePolicyNumber(e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                  getFieldError("insurancePolicyNumber") ? "border-red-500" : "border-gray-300"
                }`}
                placeholder="Nomor polis asuransi"
              />
              {getFieldError("insurancePolicyNumber") && (
                <p className="text-sm text-red-600 mt-1">{getFieldError("insurancePolicyNumber")}</p>
              )}
            </div>

            {/* Member Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nama Peserta</label>
              <input
                type="text"
                value={insuranceMemberName}
                onChange={(e) => setInsuranceMemberName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Nama peserta asuransi"
              />
            </div>

            {/* Expiry Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Kadaluarsa</label>
              <input
                type="date"
                value={insuranceExpiryDate}
                onChange={(e) => setInsuranceExpiryDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Insurance Type */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Jenis Pertanggungan</label>
              <div className="flex flex-wrap gap-4">
                {INSURANCE_TYPE_OPTIONS.map((option) => (
                  <label key={option.value} className="flex items-center">
                    <input
                      type="radio"
                      value={option.value}
                      checked={insuranceType === option.value}
                      onChange={(e) => setInsuranceType(e.target.value as InsuranceCoverageType)}
                      className="mr-2"
                    />
                    <span>{option.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Emergency Contact Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Kontak Darurat</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Contact Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nama Kontak <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={emergencyName}
              onChange={(e) => setEmergencyName(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("emergencyName") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Nama lengkap kontak darurat"
            />
            {getFieldError("emergencyName") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("emergencyName")}</p>
            )}
          </div>

          {/* Relationship */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hubungan dengan Pasien <span className="text-red-500">*</span>
            </label>
            <select
              value={emergencyRelationship}
              onChange={(e) => setEmergencyRelationship(e.target.value as EmergencyContactRelationship | "")}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("emergencyRelationship") ? "border-red-500" : "border-gray-300"
              }`}
            >
              <option value="">Pilih Hubungan</option>
              {RELATIONSHIP_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {getFieldError("emergencyRelationship") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("emergencyRelationship")}</p>
            )}
          </div>

          {/* Emergency Phone */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nomor Telepon <span className="text-red-500">*</span>
            </label>
            <input
              type="tel"
              value={emergencyPhone}
              onChange={(e) => setEmergencyPhone(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                getFieldError("emergencyPhone") ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Contoh: 081234567890"
            />
            {getFieldError("emergencyPhone") && (
              <p className="text-sm text-red-600 mt-1">{getFieldError("emergencyPhone")}</p>
            )}
          </div>
        </div>
      </div>

      {/* Medical Information Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Medis</h2>

        <div className="space-y-4">
          {/* Allergies */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Alergi yang Diketahui</label>
            <textarea
              rows={3}
              value={allergies}
              onChange={(e) => setAllergies(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Sebutkan semua alergi yang diketahui (obat, makanan, lingkungan, dll)"
            />
          </div>

          {/* Chronic Conditions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Penyakit Kronis</label>
            <textarea
              rows={3}
              value={chronicConditions}
              onChange={(e) => setChronicConditions(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Sebutkan penyakit kronis atau kondisi medis jangka panjang"
            />
          </div>

          {/* Additional Medical Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Catatan Medis Tambahan</label>
            <textarea
              rows={3}
              value={medicalNotes}
              onChange={(e) => setMedicalNotes(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Catatan medis tambahan yang perlu diketahui"
            />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 justify-end">
        <button
          onClick={() => router.push("/app/patients")}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Batal
        </button>
        <button
          onClick={handleSavePatient}
          disabled={loading}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? "Menyimpan..." : "Simpan Pasien"}
        </button>
      </div>
    </div>
  );
}
