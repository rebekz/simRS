'use client'

/**
 * BPJS Eligibility History Page
 *
 * Displays the history of BPJS eligibility verification checks for a patient.
 */

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

interface BPJSEligibilityCheck {
  id: number
  search_type: string
  search_value: string
  is_eligible: boolean
  response_message?: string
  participant_info?: any
  verified_at: string
  verification_method: string
  is_cached: boolean
  cache_hit: boolean
  is_manual_override: boolean
  override_reason?: string
  api_error?: string
}

interface EligibilityHistoryResponse {
  patient_id: number
  medical_record_number: string
  full_name: string
  checks: BPJSEligibilityCheck[]
  total: number
  page: number
  page_size: number
}

export default function BPJSEligibilityHistoryPage() {
  const params = useParams()
  const patientId = params.id as string

  const [history, setHistory] = useState<EligibilityHistoryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const pageSize = 20

  useEffect(() => {
    if (patientId) {
      fetchHistory()
    }
  }, [patientId, page])

  const fetchHistory = async () => {
    setLoading(true)
    setError(null)

    try {
      const skip = (page - 1) * pageSize
      const response = await fetch(
        `/api/v1/bpjs-verification/history/${patientId}?skip=${skip}&limit=${pageSize}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Gagal mengambil riwayat eligibility')
      }

      setHistory(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Terjadi kesalahan')
    } finally {
      setLoading(false)
    }
  }

  const getVerificationMethodBadge = (method: string) => {
    const badges: Record<string, { label: string; className: string }> = {
      api: { label: 'API', className: 'bg-blue-100 text-blue-800' },
      manual: { label: 'Manual', className: 'bg-purple-100 text-purple-800' },
      override: { label: 'Override', className: 'bg-orange-100 text-orange-800' }
    }
    const badge = badges[method] || { label: method, className: 'bg-gray-100 text-gray-800' }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${badge.className}`}>
        {badge.label}
      </span>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('id-ID', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Memuat riwayat eligibility...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        {error}
      </div>
    )
  }

  if (!history || history.checks.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 px-4 py-8 rounded-md text-center">
        <p className="text-gray-500">Belum ada riwayat pemeriksaan eligibility BPJS</p>
      </div>
    )
  }

  const totalPages = Math.ceil(history.total / pageSize)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          Riwayat Eligibility BPJS
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          Pasien: {history.full_name} ({history.medical_record_number})
        </p>
      </div>

      {/* Statistics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-500">Total Pemeriksaan</p>
          <p className="text-2xl font-semibold text-gray-900">{history.total}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-500">Eligible</p>
          <p className="text-2xl font-semibold text-green-600">
            {history.checks.filter(c => c.is_eligible).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-500">Tidak Eligible</p>
          <p className="text-2xl font-semibold text-red-600">
            {history.checks.filter(c => !c.is_eligible).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-500">Cache Hit</p>
          <p className="text-2xl font-semibold text-blue-600">
            {history.checks.filter(c => c.cache_hit).length}
          </p>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tanggal
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Jenis Pencarian
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nilai
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metode
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cache
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.checks.map((check) => (
                <tr key={check.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(check.verified_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {check.search_type === 'card' ? 'Nomor Kartu' : 'NIK'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                    {check.search_value}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {check.is_eligible ? (
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Eligible
                      </span>
                    ) : (
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                        Tidak Eligible
                      </span>
                    )}
                    {check.is_manual_override && (
                      <span className="ml-2 px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-orange-100 text-orange-800">
                        Override
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getVerificationMethodBadge(check.verification_method)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {check.cache_hit ? (
                      <span className="text-green-600">✓ Hit</span>
                    ) : check.is_cached ? (
                      <span className="text-blue-600">→ Miss</span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white px-4 py-3 border-t rounded-lg">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Sebelumnya
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Selanjutnya
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Menampilkan <span className="font-medium">{(page - 1) * pageSize + 1}</span> sampai{' '}
                <span className="font-medium">{Math.min(page * pageSize, history.total)}</span> dari{' '}
                <span className="font-medium">{history.total}</span> hasil
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Sebelumnya
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                      page === pageNum
                        ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    {pageNum}
                  </button>
                ))}
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Selanjutnya
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
