"use client";

import React, { useState, useEffect } from 'react';

// Types
interface DispensingQueueItem {
  prescription_id: number;
  prescription_number: string;
  patient_id: number;
  patient_name: string;
  patient_bpjs_number?: string;
  priority: 'stat' | 'urgent' | 'routine';
  status: string;
  submitted_date: string;
  estimated_ready_time?: string;
  prescriber_name?: string;
  total_items: number;
  items_dispensed: number;
  narcotic_count: number;
  antibiotic_count: number;
  queue_position?: number;
  estimated_wait_minutes?: number;
  verified: boolean;
  verified_by?: string;
  verified_date?: string;
}

interface DispensingQueueProps {
  pharmacistId?: number;
  onDispenseComplete?: (prescriptionId: number) => void;
}

type FilterStatus = 'all' | 'queued' | 'in_progress' | 'awaiting_verification' | 'verified' | 'ready_for_pickup';

export default function DispensingQueue({ pharmacistId, onDispenseComplete }: DispensingQueueProps) {
  const [queue, setQueue] = useState<DispensingQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [assignedToMe, setAssignedToMe] = useState(false);
  const [selectedItem, setSelectedItem] = useState<DispensingQueueItem | null>(null);
  const [scanningMode, setScanningMode] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);

  useEffect(() => {
    fetchQueue();
    // Refresh every 30 seconds
    const interval = setInterval(fetchQueue, 30000);
    return () => clearInterval(interval);
  }, [filterStatus, assignedToMe]);

  async function fetchQueue() {
    setLoading(true);
    try {
      const statusParam = filterStatus === 'all' ? '' : `&status=${filterStatus}`;
      const assignedParam = assignedToMe ? '&assigned_to_me=true' : '';
      const response = await fetch(`/api/v1/dispensing/queue?page=1&page_size=50${statusParam}${assignedParam}`);
      const data = await response.json();
      setQueue(data.queue || []);
    } catch (error) {
      console.error('Failed to fetch queue:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleStartDispensing(item: DispensingQueueItem) {
    try {
      const response = await fetch(`/api/v1/dispensing/queue/${item.prescription_id}/start`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchQueue();
      }
    } catch (error) {
      console.error('Failed to start dispensing:', error);
    }
  }

  function getPriorityColor(priority: string): string {
    switch (priority) {
      case 'stat':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'urgent':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'routine':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  }

  function getPriorityLabel(priority: string): string {
    switch (priority) {
      case 'stat':
        return 'STAT';
      case 'urgent':
        return 'Segera';
      case 'routine':
        return 'Rutin';
      default:
        return priority;
    }
  }

  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      'queued': 'Antri',
      'in_progress': 'Proses',
      'awaiting_verification': 'Verifikasi',
      'verified': 'Terverifikasi',
      'ready_for_pickup': 'Siap Ambil',
      'dispensed': 'Dispensed',
    };
    return labels[status] || status;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Antrian Dispensing</h2>
        <button
          onClick={fetchQueue}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-4 items-center">
        <div className="flex gap-2">
          {(['all', 'queued', 'in_progress', 'awaiting_verification', 'verified', 'ready_for_pickup'] as FilterStatus[]).map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filterStatus === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {status === 'all' ? 'Semua' : getStatusLabel(status)}
            </button>
          ))}
        </div>
        <label className="flex items-center ml-auto">
          <input
            type="checkbox"
            checked={assignedToMe}
            onChange={(e) => setAssignedToMe(e.target.checked)}
            className="mr-2"
          />
          Hanya tugasan saya
        </label>
      </div>

      {/* Queue Statistics */}
      <div className="mb-6 grid grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-800">{queue.length}</div>
          <div className="text-sm text-blue-600">Total Antrian</div>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-red-800">{queue.filter(q => q.priority === 'stat').length}</div>
          <div className="text-sm text-red-600">STAT</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-orange-800">{queue.filter(q => q.priority === 'urgent').length}</div>
          <div className="text-sm text-orange-600">Segera</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-800">{queue.filter(q => q.priority === 'routine').length}</div>
          <div className="text-sm text-green-600">Rutin</div>
        </div>
      </div>

      {/* Queue List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Memuat antrian...</p>
        </div>
      ) : queue.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Tidak ada antrian untuk ditampilkan
        </div>
      ) : (
        <div className="space-y-4">
          {queue.map((item) => (
            <div
              key={item.prescription_id}
              className={`border rounded-lg p-4 hover:shadow-md transition-shadow ${
                item.priority === 'stat' ? 'border-red-300 bg-red-50' :
                item.priority === 'urgent' ? 'border-orange-300 bg-orange-50' :
                'border-gray-200'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  {/* Header */}
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(item.priority)}`}>
                      {getPriorityLabel(item.priority)}
                    </span>
                    <span className="text-sm text-gray-600">
                      {item.prescription_number}
                    </span>
                    {item.queue_position && (
                      <span className="text-sm text-gray-500">
                        Antrian #{item.queue_position}
                      </span>
                    )}
                    {item.estimated_wait_minutes && (
                      <span className="text-sm text-gray-500">
                        ~{item.estimated_wait_minutes} menit
                      </span>
                    )}
                  </div>

                  {/* Patient Info */}
                  <div className="mb-2">
                    <div className="font-semibold text-gray-900">{item.patient_name}</div>
                    <div className="text-sm text-gray-600">
                      BPJS: {item.patient_bpjs_number || 'N/A'}
                    </div>
                    {item.prescriber_name && (
                      <div className="text-sm text-gray-600">
                        Dokter: {item.prescriber_name}
                      </div>
                    )}
                  </div>

                  {/* Progress */}
                  <div className="mb-2">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-gray-600">Progress:</span>
                      <span className="font-medium">{item.items_dispensed} / {item.total_items} item</span>
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        item.verified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {item.verified ? 'Terverifikasi' : 'Belum verifikasi'}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${(item.items_dispensed / item.total_items) * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Special Drugs */}
                  {(item.narcotic_count > 0 || item.antibiotic_count > 0) && (
                    <div className="flex gap-2 text-sm">
                      {item.narcotic_count > 0 && (
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded">
                          ⚠️ {item.narcotic_count} Narkotik
                        </span>
                      )}
                      {item.antibiotic_count > 0 && (
                        <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                          🧪 {item.antibiotic_count} Antibiotik
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2 ml-4">
                  {item.status === 'queued' && (
                    <button
                      onClick={() => handleStartDispensing(item)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      Mulai Dispensing
                    </button>
                  )}
                  {item.status === 'in_progress' && (
                    <button
                      onClick={() => {
                        setSelectedItem(item);
                        setScanningMode(true);
                      }}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                    >
                      Scan Obat
                    </button>
                  )}
                  {item.status === 'awaiting_verification' && (
                    <button
                      onClick={() => setSelectedItem(item)}
                      className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm"
                    >
                      Verifikasi
                    </button>
                  )}
                  {item.status === 'verified' && (
                    <button
                      onClick={() => setSelectedItem(item)}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                    >
                      Selesaikan
                    </button>
                  )}
                  {item.status === 'ready_for_pickup' && (
                    <div className="text-sm text-green-700 font-medium">
                      Siap Ambil
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Scanning Modal */}
      {scanningMode && selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Scan Obat</h3>
            <p className="text-gray-600 mb-4">
              Resep: {selectedItem.prescription_number}
            </p>
            <input
              type="text"
              autoFocus
              placeholder="Scan barcode obat..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleScan(e.currentTarget.value);
                  e.currentTarget.value = '';
                }
              }}
            />
            {scanResult && (
              <div className={`p-4 rounded-lg mb-4 ${
                scanResult.match ? 'bg-green-50 border border-green-300' : 'bg-red-50 border border-red-300'
              }`}>
                <div className="font-semibold mb-2">
                  {scanResult.match ? '✅ Cocok' : '❌ Tidak Cocok'}
                </div>
                <div className="text-sm">
                  {scanResult.match
                    ? `Obat: ${scanResult.scanned_drug?.name}`
                    : `Error: ${scanResult.errors?.join(', ')}`}
                </div>
              </div>
            )}
            <div className="flex gap-4">
              <button
                onClick={() => {
                  setScanningMode(false);
                  setScanResult(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

async function handleScan(barcode: string) {
  // Handle barcode scanning
  console.log('Scanned:', barcode);
}
