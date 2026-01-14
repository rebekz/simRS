"use client"

/**
 * Patient History Page for STORY-011
 *
 * This page displays comprehensive patient medical history:
 * - Patient demographics summary
 * - Complete encounter list with pagination
 * - All diagnoses and chronic conditions
 * - Active and past treatments
 * - Last visit information
 */

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

interface PatientInfo {
  id: number
  medical_record_number: string
  full_name: string
  date_of_birth: string
  gender: string
}

interface Diagnosis {
  id: number
  encounter_id: number
  icd_10_code: string
  diagnosis_name: string
  diagnosis_type: string
  is_chronic: boolean
  notes?: string
  encounter_date: string
  encounter_type: string
}

interface Treatment {
  id: number
  encounter_id: number
  treatment_type: string
  treatment_name: string
  dosage?: string
  frequency?: string
  duration?: string
  notes?: string
  is_active: boolean
  encounter_date: string
  encounter_type: string
}

interface Encounter {
  id: number
  patient_id: number
  encounter_type: string
  encounter_date: string
  start_time: string
  end_time?: string
  department?: string
  doctor_id?: number
  chief_complaint?: string
  status: string
  is_urgent: boolean
  diagnoses: Diagnosis[]
  treatments: Treatment[]
}

interface PatientHistory {
  patient_id: number
  medical_record_number: string
  full_name: string
  date_of_birth: string
  gender: string
  total_encounters: number
  encounters: Encounter[]
  all_diagnoses: Diagnosis[]
  chronic_conditions: Diagnosis[]
  active_treatments: Treatment[]
  all_treatments: Treatment[]
  last_visit_date?: string
  last_department?: string
  last_doctor_id?: number
  total_diagnoses: number
  total_treatments: number
  chronic_condition_count: number
}

export default function PatientHistoryPage() {
  const params = useParams()
  const patientId = params.id as string

  const [history, setHistory] = useState<PatientHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTab, setSelectedTab] = useState<'overview' | 'encounters' | 'diagnoses' | 'treatments'>('overview')

  useEffect(() => {
    if (patientId) {
      fetchHistory()
    }
  }, [patientId])

  const fetchHistory = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/v1/encounters/patients/${patientId}/history`)

      if (!response.ok) {
        if (response.status === 404) {
          setError('Pasien tidak ditemukan')
        } else {
          throw new Error('Failed to fetch patient history')
        }
        return
      }

      const data: PatientHistory = await response.json()
      setHistory(data)
    } catch (err) {
      console.error('Fetch error:', err)
      setError('Terjadi kesalahan saat mengambil riwayat pasien')
    } finally {
      setLoading(false)
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

  // Calculate age
  const calculateAge = (dateOfBirth: string) => {
    try {
      const today = new Date()
      const birthDate = new Date(dateOfBirth)
      let age = today.getFullYear() - birthDate.getFullYear()
      const monthDiff = today.getMonth() - birthDate.getMonth()
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--
      }
      return age
    } catch {
      return 0
    }
  }

  // Get encounter type badge color
  const getEncounterTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      outpatient: 'bg-blue-100 text-blue-800',
      inpatient: 'bg-purple-100 text-purple-800',
      emergency: 'bg-red-100 text-red-800',
      telephone: 'bg-green-100 text-green-800',
      home_visit: 'bg-yellow-100 text-yellow-800'
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  // Get status badge color
  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-red-100 text-red-800',
      scheduled: 'bg-yellow-100 text-yellow-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Memuat riwayat pasien...</p>
        </div>
      </div>
    )
  }

  if (error || !history) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <p className="text-sm text-red-700">{error || 'Terjadi kesalahan'}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Riwayat Medis Pasien
          </h1>
          <p className="text-gray-600">
            Lihat riwayat kunjungan, diagnosa, dan pengobatan pasien
          </p>
        </div>

        {/* Patient Info Card */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">
                {history.full_name}
              </h2>
              <p className="text-lg text-gray-600 mb-4">
                No. RM: <span className="font-semibold text-blue-900">{history.medical_record_number}</span>
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Tanggal Lahir</p>
                  <p className="font-medium">{formatDate(history.date_of_birth)}</p>
                </div>
                <div>
                  <p className="text-gray-500">Usia</p>
                  <p className="font-medium">{calculateAge(history.date_of_birth)} tahun</p>
                </div>
                <div>
                  <p className="text-gray-500">Jenis Kelamin</p>
                  <p className="font-medium">{history.gender === 'male' ? 'Laki-laki' : 'Perempuan'}</p>
                </div>
                <div>
                  <p className="text-gray-500">Total Kunjungan</p>
                  <p className="font-medium">{history.total_encounters}</p>
                </div>
              </div>
            </div>
            {history.last_visit_date && (
              <div className="text-right">
                <p className="text-sm text-gray-500">Kunjungan Terakhir</p>
                <p className="font-semibold text-lg">{formatDate(history.last_visit_date)}</p>
                {history.last_department && (
                  <p className="text-sm text-gray-600">{history.last_department}</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              {[
                { key: 'overview', label: 'Ringkasan', count: null },
                { key: 'encounters', label: 'Kunjungan', count: history.total_encounters },
                { key: 'diagnoses', label: 'Diagnosa', count: history.total_diagnoses },
                { key: 'treatments', label: 'Pengobatan', count: history.total_treatments }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setSelectedTab(tab.key as any)}
                  className={`${
                    selectedTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
                >
                  {tab.label}
                  {tab.count !== null && (
                    <span className={`${
                      selectedTab === tab.key ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                    } py-0.5 px-2 rounded-full text-xs`}>
                      {tab.count}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Overview Tab */}
        {selectedTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Chronic Conditions */}
            {history.chronic_conditions.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                  </svg>
                  Kondisi Kronis
                </h3>
                <ul className="space-y-3">
                  {history.chronic_conditions.map((diag) => (
                    <li key={diag.id} className="flex items-start gap-3">
                      <span className="mt-1 w-2 h-2 bg-red-500 rounded-full flex-shrink-0"></span>
                      <div>
                        <p className="font-medium text-gray-900">{diag.diagnosis_name}</p>
                        <p className="text-sm text-gray-500">{diag.icd_10_code}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Active Treatments */}
            {history.active_treatments.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Pengobatan Aktif
                </h3>
                <ul className="space-y-3">
                  {history.active_treatments.slice(0, 5).map((treatment) => (
                    <li key={treatment.id} className="border-l-4 border-green-500 pl-3">
                      <p className="font-medium text-gray-900">{treatment.treatment_name}</p>
                      <div className="text-sm text-gray-500">
                        {treatment.dosage && <span>{treatment.dosage}</span>}
                        {treatment.frequency && <span> • {treatment.frequency}</span>}
                      </div>
                    </li>
                  ))}
                  {history.active_treatments.length > 5 && (
                    <li className="text-sm text-gray-500 pt-2">
                      +{history.active_treatments.length - 5} pengobatan aktif lainnya
                    </li>
                  )}
                </ul>
              </div>
            )}

            {/* Recent Encounters */}
            {history.encounters.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6 md:col-span-2">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Kunjungan Terakhir</h3>
                <div className="space-y-3">
                  {history.encounters.slice(0, 3).map((encounter) => (
                    <div key={encounter.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getEncounterTypeBadge(encounter.encounter_type)}`}>
                              {encounter.encounter_type}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusBadge(encounter.status)}`}>
                              {encounter.status}
                            </span>
                            {encounter.is_urgent && (
                              <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-800">
                                Urgent
                              </span>
                            )}
                          </div>
                          <p className="font-medium text-gray-900">{formatDate(encounter.encounter_date)}</p>
                        </div>
                        {encounter.department && (
                          <span className="text-sm text-gray-600">{encounter.department}</span>
                        )}
                      </div>
                      {encounter.chief_complaint && (
                        <p className="text-sm text-gray-600 mt-2">
                          <span className="font-medium">Keluhan:</span> {encounter.chief_complaint}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Encounters Tab */}
        {selectedTab === 'encounters' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Semua Kunjungan</h3>
            {history.encounters.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Belum ada data kunjungan</p>
            ) : (
              <div className="space-y-4">
                {history.encounters.map((encounter) => (
                  <div key={encounter.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${getEncounterTypeBadge(encounter.encounter_type)}`}>
                            {encounter.encounter_type}
                          </span>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusBadge(encounter.status)}`}>
                            {encounter.status}
                          </span>
                        </div>
                        <p className="font-semibold text-gray-900">{formatDate(encounter.encounter_date)}</p>
                        <p className="text-sm text-gray-500">{formatDateTime(encounter.start_time)}</p>
                      </div>
                      {encounter.department && (
                        <span className="text-sm font-medium text-gray-700">{encounter.department}</span>
                      )}
                    </div>
                    {encounter.chief_complaint && (
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-700">Keluhan:</p>
                        <p className="text-sm text-gray-600">{encounter.chief_complaint}</p>
                      </div>
                    )}
                    {encounter.diagnoses.length > 0 && (
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-700 mb-1">Diagnosa:</p>
                        <div className="flex flex-wrap gap-1">
                          {encounter.diagnoses.map((diag) => (
                            <span key={diag.id} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                              {diag.icd_10_code} - {diag.diagnosis_name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {encounter.treatments.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Pengobatan:</p>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {encounter.treatments.map((treatment) => (
                            <li key={treatment.id}>
                              • {treatment.treatment_name}
                              {treatment.dosage && <span> ({treatment.dosage}</span>}
                              {treatment.frequency && <span>, {treatment.frequency}</span>}
                              {treatment.dosage && <span>)</span>}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Diagnoses Tab */}
        {selectedTab === 'diagnoses' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Semua Diagnosa</h3>
            {history.all_diagnoses.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Belum ada data diagnosa</p>
            ) : (
              <div className="space-y-3">
                {history.all_diagnoses.map((diag) => (
                  <div key={diag.id} className="border border-gray-200 rounded-lg p-4 flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
                          {diag.icd_10_code}
                        </span>
                        {diag.is_chronic && (
                          <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-800">
                            Kronis
                          </span>
                        )}
                        <span className="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-700 capitalize">
                          {diag.diagnosis_type}
                        </span>
                      </div>
                      <p className="font-medium text-gray-900">{diag.diagnosis_name}</p>
                      <p className="text-sm text-gray-500">{formatDate(diag.encounter_date)} • {diag.encounter_type}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Treatments Tab */}
        {selectedTab === 'treatments' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Semua Pengobatan</h3>
            {history.all_treatments.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Belum ada data pengobatan</p>
            ) : (
              <div className="space-y-3">
                {history.all_treatments.map((treatment) => (
                  <div key={treatment.id} className={`border rounded-lg p-4 ${treatment.is_active ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}>
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="px-2 py-1 text-xs font-medium rounded bg-purple-100 text-purple-800 capitalize">
                            {treatment.treatment_type}
                          </span>
                          {treatment.is_active && (
                            <span className="px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800">
                              Aktif
                            </span>
                          )}
                        </div>
                        <p className="font-medium text-gray-900">{treatment.treatment_name}</p>
                        <div className="text-sm text-gray-500 mt-1">
                          {treatment.dosage && <span>{treatment.dosage}</span>}
                          {treatment.frequency && <span> • {treatment.frequency}</span>}
                          {treatment.duration && <span> • {treatment.duration}</span>}
                        </div>
                        <p className="text-xs text-gray-400 mt-1">{formatDate(treatment.encounter_date)} • {treatment.encounter_type}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Back Button */}
        <div className="mt-6">
          <a
            href="/patients"
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Kembali ke Daftar Pasien
          </a>
        </div>
      </div>
    </div>
  )
}
