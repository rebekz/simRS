'use client'

/**
 * BPJSVerificationCard Component
 *
 * Component for verifying BPJS (Badan Penyelenggara Jaminan Sosial)
 * eligibility and creating SEP (Surat Eligibilitas Peserta).
 */

import { useState } from 'react'

interface BPJSParticipantInfo {
  nomorKartu: string
  nama: string
  noKTP?: string
  mrNo?: string
  statusPeserta?: {
    kode?: string
    keterangan?: string
  }
  tglCetakKartu?: string
  tglTAT?: string
  tglTMT?: string
  umur?: {
    umurSekarang?: string
    umurSaatPelayanan?: string
  }
  peserta?: {
    asuransi?: string
    cob?: {
      nmAsuransi?: string
      noAsuransi?: string
      tglTAT?: string
      tglTMT?: string
    }
  }
  hakKelas?: {
    keterangan?: string
    kode?: string
  }
  jenisPeserta?: string
  foto?: string
}

interface BPJSEligibilityResponse {
  metaData?: {
    code?: string
    message?: string
  }
  response?: {
    peserta?: BPJSParticipantInfo
  }
  peserta?: BPJSParticipantInfo
  is_eligible: boolean
  message: string
}

interface BPJSVerificationCardProps {
  patientId?: number
  patientNIK?: string
  patientName?: string
  onVerificationComplete?: (data: BPJSEligibilityResponse) => void
}

export default function BPJSVerificationCard({
  patientId,
  patientNIK,
  patientName,
  onVerificationComplete
}: BPJSVerificationCardProps) {
  const [loading, setLoading] = useState(false)
  const [cardNumber, setCardNumber] = useState('')
  const [nik, setNik] = useState(patientNIK || '')
  const [sepDate, setSepDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [result, setResult] = useState<BPJSEligibilityResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleCheckEligibility = async () => {
    if (!cardNumber && !nik) {
      setError('Nomor Kartu atau NIK wajib diisi')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/v1/bpjs/eligibility', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          card_number: cardNumber || undefined,
          nik: nik || undefined,
          sep_date: sepDate
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Gagal memverifikasi eligibility BPJS')
      }

      setResult(data)
      onVerificationComplete?.(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Terjadi kesalahan')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status?: string) => {
    if (!status) return 'gray'
    const statusLower = status.toLowerCase()
    if (statusLower.includes('aktif')) return 'green'
    if (statusLower.includes('tidak aktif')) return 'red'
    return 'yellow'
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Verifikasi BPJS
        </h3>
        <p className="text-sm text-gray-600">
          Periksa status eligibility dan buat SEP (Surat Eligibilitas Peserta)
        </p>
      </div>

      <div className="space-y-4">
        {/* Card Number Input */}
        <div>
          <label htmlFor="cardNumber" className="block text-sm font-medium text-gray-700 mb-1">
            Nomor Kartu BPJS
          </label>
          <input
            type="text"
            id="cardNumber"
            value={cardNumber}
            onChange={(e) => setCardNumber(e.target.value)}
            placeholder="Masukkan 13 digit nomor kartu"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            maxLength={13}
          />
        </div>

        {/* NIK Input */}
        <div>
          <label htmlFor="nik" className="block text-sm font-medium text-gray-700 mb-1">
            NIK
          </label>
          <input
            type="text"
            id="nik"
            value={nik}
            onChange={(e) => setNik(e.target.value)}
            placeholder="Masukkan 16 digit NIK"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            maxLength={16}
          />
          {patientNIK && (
            <p className="text-xs text-gray-500 mt-1">
              NIK Pasien: {patientNIK}
            </p>
          )}
        </div>

        {/* SEP Date Input */}
        <div>
          <label htmlFor="sepDate" className="block text-sm font-medium text-gray-700 mb-1">
            Tanggal SEP
          </label>
          <input
            type="date"
            id="sepDate"
            value={sepDate}
            onChange={(e) => setSepDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Check Button */}
        <button
          onClick={handleCheckEligibility}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Memeriksa...' : 'Periksa Eligibility'}
        </button>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Result Display */}
        {result && result.peserta && (
          <div className="mt-4 border-t pt-4">
            <h4 className="text-md font-semibold text-gray-900 mb-3">
              Hasil Verifikasi
            </h4>

            {/* Eligibility Status */}
            <div
              className={`mb-3 p-3 rounded-md ${
                result.is_eligible
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              <p
                className={`text-sm font-medium ${
                  result.is_eligible ? 'text-green-800' : 'text-red-800'
                }`}
              >
                {result.is_eligible ? '✓ Eligible' : '✗ Tidak Eligible'}
              </p>
              {result.message && (
                <p className="text-xs text-gray-600 mt-1">{result.message}</p>
              )}
            </div>

            {/* Participant Information */}
            <div className="bg-gray-50 rounded-md p-4 space-y-2">
              <div>
                <span className="text-xs text-gray-500">Nama Peserta</span>
                <p className="text-sm font-medium text-gray-900">
                  {result.peserta.nama}
                </p>
              </div>

              <div>
                <span className="text-xs text-gray-500">Nomor Kartu</span>
                <p className="text-sm font-medium text-gray-900">
                  {result.peserta.nomorKartu}
                </p>
              </div>

              {result.peserta.noKTP && (
                <div>
                  <span className="text-xs text-gray-500">NIK</span>
                  <p className="text-sm font-medium text-gray-900">
                    {result.peserta.noKTP}
                  </p>
                </div>
              )}

              {result.peserta.statusPeserta && (
                <div>
                  <span className="text-xs text-gray-500">Status Peserta</span>
                  <p
                    className={`text-sm font-medium ${
                      getStatusColor(result.peserta.statusPeserta.keterangan) === 'green'
                        ? 'text-green-700'
                        : getStatusColor(result.peserta.statusPeserta.keterangan) === 'red'
                        ? 'text-red-700'
                        : 'text-yellow-700'
                    }`}
                  >
                    {result.peserta.statusPeserta.keterangan || 'Tidak diketahui'}
                  </p>
                </div>
              )}

              {result.peserta.jenisPeserta && (
                <div>
                  <span className="text-xs text-gray-500">Jenis Peserta</span>
                  <p className="text-sm font-medium text-gray-900">
                    {result.peserta.jenisPeserta}
                  </p>
                </div>
              )}

              {result.peserta.hakKelas && (
                <div>
                  <span className="text-xs text-gray-500">Kelas Hak</span>
                  <p className="text-sm font-medium text-gray-900">
                    {result.peserta.hakKelas.keterangan || result.peserta.hakKelas.kode}
                  </p>
                </div>
              )}

              {result.peserta.umur && (
                <div>
                  <span className="text-xs text-gray-500">Umur</span>
                  <p className="text-sm font-medium text-gray-900">
                    {result.peserta.umur.umurSekarang || result.peserta.umur.umurSaatPelayanan}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
