"use client"

/**
 * Patient Registration Page for STORY-006
 *
 * This page allows reception staff to register new patients with:
 * - NIK validation (16 digits)
 * - Duplicate patient detection
 * - Emergency contact information
 * - Insurance information (BPJS, Asuransi, Umum)
 * - Offline-first support
 */

import { useState } from 'react'

// Types for patient registration
interface EmergencyContact {
  name: string
  relationship: string
  phone: string
  address?: string
}

interface PatientInsurance {
  insurance_type: 'bpjs' | 'asuransi' | 'umum'
  insurance_number?: string
  member_name?: string
  expiry_date?: string
}

interface PatientFormData {
  nik: string
  full_name: string
  date_of_birth: string
  gender: 'male' | 'female'
  phone: string
  email?: string
  address: string
  city: string
  province: string
  postal_code: string
  blood_type: 'A' | 'B' | 'AB' | 'O' | 'none'
  marital_status: 'single' | 'married' | 'widowed' | 'divorced'
  religion?: string
  occupation?: string
  emergency_contacts: EmergencyContact[]
  insurance: PatientInsurance
}

// Constants
const GENDER_OPTIONS = [
  { value: 'male', label: 'Laki-laki' },
  { value: 'female', label: 'Perempuan' }
]

const BLOOD_TYPE_OPTIONS = [
  { value: 'A', label: 'A' },
  { value: 'B', label: 'B' },
  { value: 'AB', label: 'AB' },
  { value: 'O', label: 'O' },
  { value: 'none', label: 'Tidak tahu' }
]

const MARITAL_STATUS_OPTIONS = [
  { value: 'single', label: 'Belum menikah' },
  { value: 'married', label: 'Menikah' },
  { value: 'widowed', label: 'Duda/Janda' },
  { value: 'divorced', label: 'Cerai' }
]

const INSURANCE_TYPE_OPTIONS = [
  { value: 'bpjs', label: 'BPJS' },
  { value: 'asuransi', label: 'Asuransi' },
  { value: 'umum', label: 'Umum' }
]

export default function PatientRegistrationPage() {
  const [loading, setLoading] = useState(false)
  const [duplicateWarning, setDuplicateWarning] = useState<string | null>(null)
  const [registrationSuccess, setRegistrationSuccess] = useState(false)
  const [generatedMRN, setGeneratedMRN] = useState('')

  const [formData, setFormData] = useState<PatientFormData>({
    nik: '',
    full_name: '',
    date_of_birth: '',
    gender: 'male',
    phone: '',
    email: '',
    address: '',
    city: '',
    province: '',
    postal_code: '',
    blood_type: 'none',
    marital_status: 'single',
    religion: '',
    occupation: '',
    emergency_contacts: [{
      name: '',
      relationship: '',
      phone: '',
      address: ''
    }],
    insurance: {
      insurance_type: 'umum',
      insurance_number: '',
      member_name: '',
      expiry_date: ''
    }
  })

  // Handle NIK input with validation
  const handleNIKChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 16)
    setFormData({ ...formData, nik: value })

    // Clear duplicate warning when NIK changes
    if (value.length === 16) {
      checkForDuplicates(value, formData.full_name, formData.date_of_birth)
    } else {
      setDuplicateWarning(null)
    }
  }

  // Check for duplicate patients
  const checkForDuplicates = async (nik: string, name: string, dob: string) => {
    try {
      const params = new URLSearchParams()
      if (nik) params.append('nik', nik)
      if (name) params.append('full_name', name)
      if (dob) params.append('date_of_birth', dob)

      const response = await fetch(`/api/v1/patients/duplicate-check?${params}`)
      const data = await response.json()

      if (data.is_duplicate) {
        setDuplicateWarning(data.message)
      } else {
        setDuplicateWarning(null)
      }
    } catch (error) {
      console.error('Error checking for duplicates:', error)
    }
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setDuplicateWarning(null)

    try {
      // Convert date format from YYYY-MM-DD to proper format
      const submitData = {
        ...formData,
        date_of_birth: new Date(formData.date_of_birth).toISOString().split('T')[0]
      }

      const response = await fetch('/api/v1/patients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Authorization header would be added here
        },
        body: JSON.stringify(submitData)
      })

      if (!response.ok) {
        const error = await response.json()
        if (error.detail) {
          setDuplicateWarning(error.detail)
        }
        throw new Error(error.detail || 'Registration failed')
      }

      const patient = await response.json()
      setGeneratedMRN(patient.medical_record_number)
      setRegistrationSuccess(true)

      // Reset form after successful registration
      setTimeout(() => {
        setFormData({
          nik: '',
          full_name: '',
          date_of_birth: '',
          gender: 'male',
          phone: '',
          email: '',
          address: '',
          city: '',
          province: '',
          postal_code: '',
          blood_type: 'none',
          marital_status: 'single',
          religion: '',
          occupation: '',
          emergency_contacts: [{
            name: '',
            relationship: '',
            phone: '',
            address: ''
          }],
          insurance: {
            insurance_type: 'umum',
            insurance_number: '',
            member_name: '',
            expiry_date: ''
          }
        })
        setRegistrationSuccess(false)
        setGeneratedMRN('')
      }, 5000)

    } catch (error) {
      console.error('Registration error:', error)
    } finally {
      setLoading(false)
    }
  }

  if (registrationSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="mb-6">
              <svg className="mx-auto h-16 w-16 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Pendaftaran Berhasil!
            </h2>
            <p className="text-gray-600 mb-4">
              Pasien telah berhasil didaftar ke dalam sistem.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-600 mb-1">Nomor Rekam Medis (No. RM):</p>
              <p className="text-3xl font-bold text-blue-900">{generatedMRN}</p>
            </div>
            <p className="text-sm text-gray-500">
              Halaman ini akan refresh secara otomatis dalam 5 detik...
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Pendaftaran Pasien Baru
          </h1>
          <p className="text-gray-600">
            Isi formulir di bawah ini untuk mendaftarkan pasien baru
          </p>
        </div>

        {/* Duplicate Warning */}
        {duplicateWarning && (
          <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">{duplicateWarning}</p>
              </div>
            </div>
          </div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Patient Information Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Informasi Pasien
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* NIK */}
              <div>
                <label htmlFor="nik" className="block text-sm font-medium text-gray-700 mb-1">
                  NIK (Nomor Induk Kependudukan) <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="nik"
                  required
                  maxLength={16}
                  value={formData.nik}
                  onChange={handleNIKChange}
                  placeholder="Masukkan 16 digit NIK"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="mt-1 text-xs text-gray-500">
                  {formData.nik.length}/16 digit
                </p>
              </div>

              {/* Full Name */}
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Nama Lengkap <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="full_name"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  placeholder="Nama lengkap pasien"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Date of Birth */}
              <div>
                <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700 mb-1">
                  Tanggal Lahir <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  id="date_of_birth"
                  required
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Gender */}
              <div>
                <label htmlFor="gender" className="block text-sm font-medium text-gray-700 mb-1">
                  Jenis Kelamin <span className="text-red-500">*</span>
                </label>
                <select
                  id="gender"
                  required
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value as 'male' | 'female' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {GENDER_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Phone */}
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                  No. Telepon <span className="text-red-500">*</span>
                </label>
                <input
                  type="tel"
                  id="phone"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="Contoh: 081234567890"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="email@contoh.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Blood Type */}
              <div>
                <label htmlFor="blood_type" className="block text-sm font-medium text-gray-700 mb-1">
                  Golongan Darah
                </label>
                <select
                  id="blood_type"
                  value={formData.blood_type}
                  onChange={(e) => setFormData({ ...formData, blood_type: e.target.value as 'A' | 'B' | 'AB' | 'O' | 'none' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {BLOOD_TYPE_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Marital Status */}
              <div>
                <label htmlFor="marital_status" className="block text-sm font-medium text-gray-700 mb-1">
                  Status Perkawinan
                </label>
                <select
                  id="marital_status"
                  value={formData.marital_status}
                  onChange={(e) => setFormData({ ...formData, marital_status: e.target.value as 'single' | 'married' | 'widowed' | 'divorced' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {MARITAL_STATUS_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Address */}
            <div className="mt-4">
              <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
                Alamat Lengkap <span className="text-red-500">*</span>
              </label>
              <textarea
                id="address"
                required
                rows={2}
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                placeholder="Alamat lengkap pasien"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* City, Province, Postal Code */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div>
                <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
                    Kota/Kabupaten <span className="text-red-500">*</span>
                  </label>
                <input
                  type="text"
                  id="city"
                  required
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  placeholder="Nama kota"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="province" className="block text-sm font-medium text-gray-700 mb-1">
                    Provinsi <span className="text-red-500">*</span>
                  </label>
                <input
                  type="text"
                  id="province"
                  required
                  value={formData.province}
                  onChange={(e) => setFormData({ ...formData, province: e.target.value })}
                  placeholder="Nama provinsi"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700 mb-1">
                    Kode Pos <span className="text-red-500">*</span>
                  </label>
                <input
                  type="text"
                  id="postal_code"
                  required
                  value={formData.postal_code}
                  onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                  placeholder="5 digit kode pos"
                  maxLength={5}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Religion and Occupation */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label htmlFor="religion" className="block text-sm font-medium text-gray-700 mb-1">
                    Agama
                  </label>
                <input
                  type="text"
                  id="religion"
                  value={formData.religion}
                  onChange={(e) => setFormData({ ...formData, religion: e.target.value })}
                  placeholder="Agama"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="occupation" className="block text-sm font-medium text-gray-700 mb-1">
                    Pekerjaan
                  </label>
                <input
                  type="text"
                  id="occupation"
                  value={formData.occupation}
                  onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                  placeholder="Pekerjaan"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Emergency Contact Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Kontak Darurat
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="emergency_name" className="block text-sm font-medium text-gray-700 mb-1">
                    Nama Lengkap <span className="text-red-500">*</span>
                  </label>
                <input
                  type="text"
                  id="emergency_name"
                  required
                  value={formData.emergency_contacts[0]?.name || ''}
                  onChange={(e) => {
                    const contacts = [...formData.emergency_contacts]
                    contacts[0] = { ...contacts[0], name: e.target.value }
                    setFormData({ ...formData, emergency_contacts: contacts })
                  }}
                  placeholder="Nama kontak darurat"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="emergency_relationship" className="block text-sm font-medium text-gray-700 mb-1">
                    Hubungan <span className="text-red-500">*</span>
                  </label>
                <input
                  type="text"
                  id="emergency_relationship"
                  required
                  value={formData.emergency_contacts[0]?.relationship || ''}
                  onChange={(e) => {
                    const contacts = [...formData.emergency_contacts]
                    contacts[0] = { ...contacts[0], relationship: e.target.value }
                    setFormData({ ...formData, emergency_contacts: contacts })
                  }}
                  placeholder="Contoh: Suami, Istri, Orang Tua"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="emergency_phone" className="block text-sm font-medium text-gray-700 mb-1">
                    No. Telepon <span className="text-red-500">*</span>
                  </label>
                <input
                  type="tel"
                  id="emergency_phone"
                  required
                  value={formData.emergency_contacts[0]?.phone || ''}
                  onChange={(e) => {
                    const contacts = [...formData.emergency_contacts]
                    contacts[0] = { ...contacts[0], phone: e.target.value }
                    setFormData({ ...formData, emergency_contacts: contacts })
                  }}
                  placeholder="No. telepon kontak darurat"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Insurance Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Informasi Asuransi
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="insurance_type" className="block text-sm font-medium text-gray-700 mb-1">
                    Jenis Asuransi <span className="text-red-500">*</span>
                  </label>
                <select
                  id="insurance_type"
                  value={formData.insurance.insurance_type}
                  onChange={(e) => {
                    setFormData({
                      ...formData,
                      insurance: { ...formData.insurance, insurance_type: e.target.value as 'bpjs' | 'asuransi' | 'umum' }
                    })
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {INSURANCE_TYPE_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="insurance_number" className="block text-sm font-medium text-gray-700 mb-1">
                    Nomor Asuransi/BPJS
                  </label>
                <input
                  type="text"
                  id="insurance_number"
                  value={formData.insurance.insurance_number}
                  onChange={(e) => {
                    setFormData({ ...formData, insurance: { ...formData.insurance, insurance_number: e.target.value } })
                  }}
                  placeholder="Nomor kartu asuransi/bpjs"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="member_name" className="block text-sm font-medium text-gray-700 mb-1">
                    Nama Peserta (jika berbeda)
                  </label>
                <input
                  type="text"
                  id="member_name"
                  value={formData.insurance.member_name}
                  onChange={(e) => {
                    setFormData({ ...formData, insurance: { ...formData.insurance, member_name: e.target.value } })
                  }}
                  placeholder="Nama peserta asuransi"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="expiry_date" className="block text-sm font-medium text-gray-700 mb-1">
                    Tanggal Berlaku
                  </label>
                <input
                  type="date"
                  id="expiry_date"
                  value={formData.insurance.expiry_date}
                  onChange={(e) => {
                    setFormData({ ...formData, insurance: { ...formData.insurance, expiry_date: e.target.value } })
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => window.history.back()}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={loading || !!duplicateWarning}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Memproses...' : 'Daftarkan Pasien'}
            </button>
          </div>

          {/* Form Instructions */}
          <div className="mt-6 text-sm text-gray-500">
            <p className="font-semibold mb-2">Informasi:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Tanda (*) wajib diisi</li>
              <li>NIK harus 16 digit angka</li>
              <li>No. telepon harus dimulai dengan 0 atau 62</li>
              <li>Sistem akan otomatis membuat Nomor Rekam Medis (No. RM)</li>
              <li>Pastikan data yang diisi sudah benar</li>
            </ul>
          </div>
        </form>
      </div>
    )
  }
}
