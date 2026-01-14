"use client"

/**
 * Returning Patient Check-in Page for STORY-007
 *
 * This page allows reception staff to quickly find and check-in returning patients:
 * - Multiple search methods (MRN, NIK, BPJS number, phone, name)
 * - Display last visit and diagnoses
 * - Insurance status verification
 * - Quick check-in functionality
 * - Patient information updates
 */

import { useState } from 'react'

interface PatientInfo {
  id: number
  medical_record_number: string
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
  blood_type: string
  marital_status: string
  religion?: string
  occupation?: string
  emergency_contacts: Array<{
    id: number
    name: string
    relationship: string
    phone: string
    address?: string
  }>
  insurance_policies: Array<{
    id: number
    insurance_type: string
    insurance_number?: string
    member_name?: string
    expiry_date?: string
  }>
  is_active: boolean
  created_at: string
  updated_at: string
}

interface PatientLookupResult {
  patient: PatientInfo
  last_visit_date?: string
  last_diagnoses?: string[]
  allergies?: string[]
  insurance_status: string
  has_unpaid_bills: boolean
}

interface CheckInResult {
  patient: PatientInfo
  queue_number?: string
  check_in_time: string
  message: string
  last_visit?: string
  insurance_status?: string
}

export default function PatientCheckInPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [foundPatient, setFoundPatient] = useState<PatientLookupResult | null>(null)
  const [checkedIn, setCheckedIn] = useState(false)
  const [checkInResult, setCheckInResult] = useState<CheckInResult | null>(null)
  const [updating, setUpdating] = useState(false)

  // Handle search
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchTerm.trim()) return

    setSearching(true)
    setSearchError(null)
    setFoundPatient(null)
    setCheckedIn(false)
    setCheckInResult(null)

    try {
      const response = await fetch(`/api/v1/patients/lookup/advanced?search=${encodeURIComponent(searchTerm)}`)

      if (!response.ok) {
        if (response.status === 404) {
          setSearchError('Pasien tidak ditemukan')
        } else {
          throw new Error('Search failed')
        }
        return
      }

      const data: PatientLookupResult = await response.json()
      setFoundPatient(data)
    } catch (error) {
      console.error('Search error:', error)
      setSearchError('Terjadi kesalahan saat mencari pasien')
    } finally {
      setSearching(false)
    }
  }

  // Handle check-in
  const handleCheckIn = async () => {
    if (!foundPatient) return

    setUpdating(true)
    try {
      const response = await fetch(`/api/v1/patients/${foundPatient.patient.id}/checkin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error('Check-in failed')
      }

      const data: CheckInResult = await response.json()
      setCheckedIn(true)
      setCheckInResult(data)
    } catch (error) {
      console.error('Check-in error:', error)
      setSearchError('Terjadi kesalahan saat check-in pasien')
    } finally {
      setUpdating(false)
    }
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
    } catch {
      return dateString
    }
  }

  // Format date time for display
  const formatDateTime = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleString('id-ID', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  // Get insurance status color
  const getInsuranceStatusColor = (status: string) => {
    if (status.includes('Active')) return 'text-green-600 bg-green-50'
    if (status.includes('Expired')) return 'text-red-600 bg-red-50'
    return 'text-gray-600 bg-gray-50'
  }

  // Reset for new search
  const handleNewSearch = () => {
    setSearchTerm('')
    setFoundPatient(null)
    setSearchError(null)
    setCheckedIn(false)
    setCheckInResult(null)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Check-In Pasien Lama
          </h1>
          <p className="text-gray-600">
            Cari dan check-in pasien yang sudah terdaftar
          </p>
        </div>

        {/* Search Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <form onSubmit={handleSearch}>
            <div className="flex gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Masukkan No. RM, NIK, No. BPJS, No. Telepon, atau Nama"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={searching}
                  autoFocus
                />
              </div>
              <button
                type="submit"
                disabled={searching || !searchTerm.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {searching ? 'Mencari...' : 'Cari'}
              </button>
            </div>

            {/* Search Error */}
            {searchError && (
              <div className="mt-4 bg-red-50 border-l-4 border-red-400 p-4">
                <p className="text-sm text-red-700">{searchError}</p>
              </div>
            )}

            {/* Search Hints */}
            {!foundPatient && !searching && !searchError && (
              <div className="mt-4 text-sm text-gray-500">
                <p className="font-semibold mb-2">Tips pencarian:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>No. Rekam Medis (MRN) - pencarian paling spesifik</li>
                  <li>NIK - 16 digit nomor induk kependudukan</li>
                  <li>No. BPJS - nomor kartu BPJS</li>
                  <li>No. Telepon - nomor telepon pasien</li>
                  <li>Nama - nama lengkap pasien</li>
                </ul>
              </div>
            )}
          </form>
        </div>

        {/* Patient Found - Check-in Section */}
        {foundPatient && !checkedIn && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-1">
                  {foundPatient.patient.full_name}
                </h2>
                <p className="text-lg text-gray-600">
                  No. RM: <span className="font-semibold text-blue-900">{foundPatient.patient.medical_record_number}</span>
                </p>
              </div>

              {/* Insurance Status Badge */}
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getInsuranceStatusColor(foundPatient.insurance_status)}`}>
                {foundPatient.insurance_status}
              </div>
            </div>

            {/* Patient Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-sm text-gray-500">NIK</p>
                <p className="font-medium">{foundPatient.patient.nik}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Tanggal Lahir</p>
                <p className="font-medium">{formatDate(foundPatient.patient.date_of_birth)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Jenis Kelamin</p>
                <p className="font-medium">{foundPatient.patient.gender === 'male' ? 'Laki-laki' : 'Perempuan'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">No. Telepon</p>
                <p className="font-medium">{foundPatient.patient.phone}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-gray-500">Alamat</p>
                <p className="font-medium">{foundPatient.patient.address}, {foundPatient.patient.city}, {foundPatient.patient.province} {foundPatient.patient.postal_code}</p>
              </div>
            </div>

            {/* Insurance Information */}
            {foundPatient.patient.insurance_policies.length > 0 && (
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm font-semibold text-gray-700 mb-2">Informasi Asuransi</p>
                {foundPatient.patient.insurance_policies.map((insurance, idx) => (
                  <div key={idx} className="text-sm">
                    <span className="font-medium">{insurance.insurance_type.toUpperCase()}:</span>
                    {insurance.insurance_number && <span className="ml-2">{insurance.insurance_number}</span>}
                    {insurance.expiry_date && <span className="ml-2 text-gray-600">(Berlaku sampai: {formatDate(insurance.expiry_date)})</span>}
                  </div>
                ))}
              </div>
            )}

            {/* Last Visit Info */}
            {foundPatient.last_visit_date && (
              <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm font-semibold text-blue-900 mb-1">Kunjungan Terakhir</p>
                <p className="text-sm text-blue-700">{formatDate(foundPatient.last_visit_date)}</p>
                {foundPatient.last_diagnoses && foundPatient.last_diagnoses.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-blue-600">Diagnosa: {foundPatient.last_diagnoses.join(', ')}</p>
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={handleCheckIn}
                disabled={updating}
                className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold"
              >
                {updating ? 'Memproses...' : '✓ Check-In Pasien'}
              </button>
              <button
                onClick={handleNewSearch}
                className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cari Lagi
              </button>
            </div>

            {/* Warning Info */}
            {foundPatient.has_unpaid_bills && (
              <div className="mt-4 bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-yellow-700 font-semibold">
                      Peringatan: Pasien ini memiliki tagihan yang belum dibayar
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Check-in Success */}
        {checkedIn && checkInResult && (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="mb-6">
              <svg className="mx-auto h-16 w-16 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Check-In Berhasil!
            </h2>
            <p className="text-gray-600 mb-6">
              {checkInResult.patient.full_name} telah berhasil check-in
            </p>

            {/* Queue Number */}
            {checkInResult.queue_number && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <p className="text-sm text-gray-600 mb-2">Nomor Antrian:</p>
                <p className="text-4xl font-bold text-blue-900">{checkInResult.queue_number}</p>
              </div>
            )}

            {/* Check-in Details */}
            <div className="text-left bg-gray-50 rounded-lg p-4 mb-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">No. RM</p>
                  <p className="font-semibold">{checkInResult.patient.medical_record_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Nama</p>
                  <p className="font-semibold">{checkInResult.patient.full_name}</p>
                </div>
                <div>
                  <p className="text-gray-600">Waktu Check-In</p>
                  <p className="font-semibold">{formatDateTime(checkInResult.check_in_time)}</p>
                </div>
                <div>
                  <p className="text-gray-600">Status Asuransi</p>
                  <p className={`font-semibold ${getInsuranceStatusColor(checkInResult.insurance_status || '')}`}>
                    {checkInResult.insurance_status || 'Unknown'}
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={handleNewSearch}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Check-In Pasien Berikutnya
            </button>
          </div>
        )}
      </div>
    )
  }
}
