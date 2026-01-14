'use client'

/**
 * SEPCreateDialog Component
 *
 * Dialog component for creating SEP (Surat Eligibilitas Peserta).
 */

import { useState } from 'react'

interface SEPCreateDialogProps {
  isOpen: boolean
  onClose: () => void
  cardNumber: string
  patientName: string
  onSuccess?: (sepNumber: string) => void
}

export default function SEPCreateDialog({
  isOpen,
  onClose,
  cardNumber,
  patientName,
  onSuccess
}: SEPCreateDialogProps) {
  const [loading, setLoading] = useState(false)
  const [sepDate, setSepDate] = useState(new Date().toISOString().split('T')[0])
  const [facilityCode, setFacilityCode] = useState('')
  const [serviceType, setServiceType] = useState('RJ')
  const [treatmentClass, setTreatmentClass] = useState('')
  const [diagnosisCode, setDiagnosisCode] = useState('')
  const [polyclinic, setPolyclinic] = useState('')
  const [doctor, setDoctor] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!cardNumber || !facilityCode || !diagnosisCode) {
      setError('Nomor Kartu, Kode Faskes, dan Kode Diagnosa wajib diisi')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/v1/bpjs/sep', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          noKartu: cardNumber,
          tglSEP: sepDate,
          ppkPelayanan: facilityCode,
          jnsPelayanan: serviceType,
          klsRawat: treatmentClass || undefined,
          diagAwal: diagnosisCode,
          poliTujuan: polyclinic || undefined,
          dpjp: doctor ? { kode: doctor } : undefined,
          catatan: notes || undefined,
          user: 'system' // Should be replaced with actual user
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Gagal membuat SEP')
      }

      if (data.nsep) {
        setResult(data.nsep)
        onSuccess?.(data.nsep)
      } else {
        setResult('SEP berhasil dibuat')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Terjadi kesalahan')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              Buat SEP (Surat Eligibilitas Peserta)
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
              disabled={loading}
            >
              ✕
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Pasien: {patientName} ({cardNumber})
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* SEP Date */}
          <div>
            <label htmlFor="sepDate" className="block text-sm font-medium text-gray-700 mb-1">
              Tanggal SEP *
            </label>
            <input
              type="date"
              id="sepDate"
              value={sepDate}
              onChange={(e) => setSepDate(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Facility Code */}
          <div>
            <label htmlFor="facilityCode" className="block text-sm font-medium text-gray-700 mb-1">
              Kode Faskes (PPK Pelayanan) *
            </label>
            <input
              type="text"
              id="facilityCode"
              value={facilityCode}
              onChange={(e) => setFacilityCode(e.target.value)}
              placeholder="Contoh: 0301U010"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Service Type */}
          <div>
            <label htmlFor="serviceType" className="block text-sm font-medium text-gray-700 mb-1">
              Jenis Pelayanan *
            </label>
            <select
              id="serviceType"
              value={serviceType}
              onChange={(e) => setServiceType(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="RJ">Rawat Jalan</option>
              <option value="RI">Rawat Inap</option>
            </select>
          </div>

          {/* Treatment Class */}
          <div>
            <label htmlFor="treatmentClass" className="block text-sm font-medium text-gray-700 mb-1">
              Kelas Rawat
            </label>
            <select
              id="treatmentClass"
              value={treatmentClass}
              onChange={(e) => setTreatmentClass(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Pilih Kelas</option>
              <option value="1">Kelas 1</option>
              <option value="2">Kelas 2</option>
              <option value="3">Kelas 3</option>
            </select>
          </div>

          {/* Diagnosis Code */}
          <div>
            <label htmlFor="diagnosisCode" className="block text-sm font-medium text-gray-700 mb-1">
              Kode Diagnosa Awal (ICD-10) *
            </label>
            <input
              type="text"
              id="diagnosisCode"
              value={diagnosisCode}
              onChange={(e) => setDiagnosisCode(e.target.value)}
              placeholder="Contoh: A00"
              required
              maxLength={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Polyclinic */}
          <div>
            <label htmlFor="polyclinic" className="block text-sm font-medium text-gray-700 mb-1">
              Poli Tujuan
            </label>
            <input
              type="text"
              id="polyclinic"
              value={polyclinic}
              onChange={(e) => setPolyclinic(e.target.value)}
              placeholder="Contoh: INT"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Doctor */}
          <div>
            <label htmlFor="doctor" className="block text-sm font-medium text-gray-700 mb-1">
              DPJP (Dokter Penanggung Jawab)
            </label>
            <input
              type="text"
              id="doctor"
              value={doctor}
              onChange={(e) => setDoctor(e.target.value)}
              placeholder="Kode Dokter"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
              Catatan
            </label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              maxLength={200}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Result Message */}
          {result && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
              <p className="text-sm font-medium">SEP Berhasil Dibuat!</p>
              <p className="text-sm mt-1">Nomor SEP: {result}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              disabled={loading || !!result}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={loading || !!result}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Memproses...' : 'Buat SEP'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
