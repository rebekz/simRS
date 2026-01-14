"use client";

import React, { useState, useEffect } from 'react';

// Types
interface RadiologyOrder {
  id: number;
  order_number: string;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  encounter_id?: number;
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'routine' | 'urgent' | 'stat';
  clinical_indication: string;
  notes?: string;
  ordered_by: string;
  ordered_at: string;
  scheduled_at?: string;
  completed_at?: string;
  procedures: RadiologyOrderProcedure[];
  safety_screening?: {
    is_pregnant: boolean;
    has_implants: boolean;
    has_contrast_allergy: boolean;
  };
  images_available?: boolean;
  report_available?: boolean;
}

interface RadiologyOrderProcedure {
  id: number;
  procedure_id: number;
  procedure_code: string;
  procedure_name: string;
  modality: string;
  body_part: string;
  contrast_required: boolean;
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed';
  images_count?: number;
  report?: string;
}

interface RadiologyOrderListProps {
  patientId?: number;
  encounterId?: number;
  status?: string;
  limit?: number;
  onOrderClick?: (order: RadiologyOrder) => void;
  showResults?: boolean;
}

export default function RadiologyOrderList({
  patientId,
  encounterId,
  status,
  limit = 20,
  onOrderClick,
  showResults = true
}: RadiologyOrderListProps) {
  const [orders, setOrders] = useState<RadiologyOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<RadiologyOrder | null>(null);
  const [viewResults, setViewResults] = useState(false);
  const [cancelling, setCancelling] = useState<number | null>(null);

  useEffect(() => {
    fetchOrders();
  }, [patientId, encounterId, status]);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (patientId) params.append('patient_id', patientId.toString());
      if (encounterId) params.append('encounter_id', encounterId.toString());
      if (status) params.append('status', status);
      params.append('limit', limit.toString());

      const response = await fetch(`/api/v1/radiology/orders?${params}`);
      const data = await response.json();
      setOrders(data.results || data.orders || []);
    } catch (error) {
      console.error('Failed to fetch radiology orders:', error);
    } finally {
      setLoading(false);
    }
  };

  function getStatusBadge(status: string): { text: string; className: string } {
    switch (status) {
      case 'pending':
        return { text: 'Menunggu', className: 'bg-yellow-100 text-yellow-800' };
      case 'scheduled':
        return { text: 'Terjadwal', className: 'bg-blue-100 text-blue-800' };
      case 'in_progress':
        return { text: 'Diproses', className: 'bg-purple-100 text-purple-800' };
      case 'completed':
        return { text: 'Selesai', className: 'bg-green-100 text-green-800' };
      case 'cancelled':
        return { text: 'Dibatalkan', className: 'bg-red-100 text-red-800' };
      default:
        return { text: status, className: 'bg-gray-100 text-gray-800' };
    }
  }

  function getPriorityBadge(priority: string): { text: string; className: string } {
    switch (priority) {
      case 'stat':
        return { text: 'STAT', className: 'bg-red-100 text-red-800 border border-red-300' };
      case 'urgent':
        return { text: 'Segera', className: 'bg-orange-100 text-orange-800 border border-orange-300' };
      default:
        return { text: 'Rutin', className: 'bg-gray-100 text-gray-800' };
    }
  }

  function getModalityIcon(modality: string): string {
    const icons: Record<string, string> = {
      'XRAY': '📷',
      'CT': '🔬',
      'MRI': '🧲',
      'USG': '📺',
      'MAMMO': '🔍',
      'FLUORO': '🎥',
      'BONE_DENSITY': '🦴',
      'PET_CT': '⚛️',
    };
    return icons[modality] || '🏥';
  }

  function handleOrderClick(order: RadiologyOrder) {
    if (onOrderClick) {
      onOrderClick(order);
    } else {
      setSelectedOrder(order);
    }
  }

  async function handleCancelOrder(orderId: number) {
    if (!confirm('Apakah Anda yakin ingin membatalkan pesanan ini?')) {
      return;
    }

    setCancelling(orderId);
    try {
      const response = await fetch(`/api/v1/radiology/orders/${orderId}/cancel`, {
        method: 'POST',
      });

      if (response.ok) {
        setOrders(orders.map(o =>
          o.id === orderId ? { ...o, status: 'cancelled' } : o
        ));
        setSelectedOrder(null);
      }
    } catch (error) {
      console.error('Failed to cancel order:', error);
      alert('Gagal membatalkan pesanan');
    } finally {
      setCancelling(null);
    }
  }

  function handleViewResults(order: RadiologyOrder) {
    setSelectedOrder(order);
    setViewResults(true);
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Pesanan Radiologi</h2>
        <button
          onClick={fetchOrders}
          className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Orders List */}
      {!loading && orders.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="mt-2">Belum ada pesanan radiologi</p>
        </div>
      )}

      {!loading && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => {
            const statusBadge = getStatusBadge(order.status);
            const priorityBadge = getPriorityBadge(order.priority);

            // Get unique modalities
            const modalities = Array.from(new Set(order.procedures.map(p => p.modality)));

            return (
              <div
                key={order.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleOrderClick(order)}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="font-semibold text-gray-900">
                        {order.order_number}
                      </span>
                      {modalities.map(mod => (
                        <span key={mod} className="text-lg" title={mod}>
                          {getModalityIcon(mod)}
                        </span>
                      ))}
                      <span className={`px-2 py-1 text-xs font-medium rounded ${statusBadge.className}`}>
                        {statusBadge.text}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${priorityBadge.className}`}>
                        {priorityBadge.text}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {order.patient_name} ({order.medical_record_number})
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Dipesan: {new Date(order.ordered_at).toLocaleString('id-ID')}
                      {order.scheduled_at && (
                        <span className="ml-3">
                          Jadwal: {new Date(order.scheduled_at).toLocaleString('id-ID')}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {order.status === 'completed' && showResults && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleViewResults(order);
                        }}
                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                      >
                        Lihat Hasil
                      </button>
                    )}
                    {(order.status === 'pending' || order.status === 'scheduled') && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCancelOrder(order.id);
                        }}
                        disabled={cancelling === order.id}
                        className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200 disabled:opacity-50"
                      >
                        {cancelling === order.id ? 'Membatalkan...' : 'Batalkan'}
                      </button>
                    )}
                  </div>
                </div>

                {/* Procedures Summary */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="text-sm text-gray-600 mb-2">
                    Prosedur ({order.procedures.length}):
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {order.procedures.slice(0, 4).map((proc) => (
                      <span
                        key={proc.id}
                        className={`px-2 py-1 text-xs rounded flex items-center gap-1 ${
                          proc.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : proc.status === 'in_progress'
                            ? 'bg-blue-100 text-blue-800'
                            : proc.status === 'scheduled'
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        <span>{getModalityIcon(proc.modality)}</span>
                        {proc.procedure_name}
                      </span>
                    ))}
                    {order.procedures.length > 4 && (
                      <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                        +{order.procedures.length - 4} lainnya
                      </span>
                    )}
                  </div>
                </div>

                {/* Safety Indicators */}
                {order.safety_screening && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {order.safety_screening.is_pregnant && (
                      <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded flex items-center gap-1">
                        ⚠️ Hamil
                      </span>
                    )}
                    {order.safety_screening.has_implants && (
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded flex items-center gap-1">
                        🔩 Implan
                      </span>
                    )}
                    {order.safety_screening.has_contrast_allergy && (
                      <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded flex items-center gap-1">
                        💉 Alergi Kontras
                      </span>
                    )}
                  </div>
                )}

                {/* Clinical Indication */}
                {order.clinical_indication && (
                  <div className="mt-3 text-sm">
                    <span className="font-medium text-gray-700">Indikasi:</span>
                    <p className="text-gray-600 mt-1">{order.clinical_indication}</p>
                  </div>
                )}

                {/* Completion Info */}
                {order.status === 'completed' && (
                  <div className="mt-3 pt-3 border-t border-gray-200 flex items-center gap-4 text-sm">
                    {order.images_available && (
                      <div className="flex items-center text-green-700">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                        </svg>
                        {order.procedures.reduce((sum, p) => sum + (p.images_count || 0), 0)} gambar
                      </div>
                    )}
                    {order.report_available && (
                      <div className="flex items-center text-green-700">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                        </svg>
                        Laporan tersedia
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Order Detail Modal */}
      {selectedOrder && !viewResults && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-900">
                  Detail Pesanan {selectedOrder.order_number}
                </h3>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                {/* Patient Info */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Pasien:</span>
                      <p className="text-gray-900">{selectedOrder.patient_name}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">No. RM:</span>
                      <p className="text-gray-900">{selectedOrder.medical_record_number}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Dipesan Oleh:</span>
                      <p className="text-gray-900">{selectedOrder.ordered_by}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Waktu:</span>
                      <p className="text-gray-900">
                        {new Date(selectedOrder.ordered_at).toLocaleString('id-ID')}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Safety Screening */}
                {selectedOrder.safety_screening && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <span className="font-medium text-yellow-900">Screning Keamanan:</span>
                    <div className="mt-2 space-y-1 text-sm">
                      {selectedOrder.safety_screening.is_pregnant && (
                        <div className="text-yellow-800">⚠️ Pasien hamil</div>
                      )}
                      {selectedOrder.safety_screening.has_implants && (
                        <div className="text-yellow-800">🔩 Memiliki implan</div>
                      )}
                      {selectedOrder.safety_screening.has_contrast_allergy && (
                        <div className="text-yellow-800">💉 Alergi kontras</div>
                      )}
                    </div>
                  </div>
                )}

                {/* Procedures List */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Prosedur</h4>
                  <div className="space-y-2">
                    {selectedOrder.procedures.map((proc) => (
                      <div key={proc.id} className="p-3 border border-gray-200 rounded">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xl">{getModalityIcon(proc.modality)}</span>
                              <div>
                                <div className="font-medium text-gray-900">{proc.procedure_name}</div>
                                <div className="text-sm text-gray-600">
                                  {proc.procedure_code} - {proc.body_part}
                                  {proc.contrast_required && (
                                    <span className="ml-2 text-blue-600">• Kontras</span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${
                              proc.status === 'completed'
                                ? 'bg-green-100 text-green-800'
                                : proc.status === 'in_progress'
                                ? 'bg-blue-100 text-blue-800'
                                : proc.status === 'scheduled'
                                ? 'bg-purple-100 text-purple-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {proc.status === 'completed'
                              ? 'Selesai'
                              : proc.status === 'in_progress'
                              ? 'Diproses'
                              : proc.status === 'scheduled'
                              ? 'Terjadwal'
                              : 'Menunggu'}
                          </span>
                        </div>
                        {proc.images_count && proc.images_count > 0 && (
                          <div className="mt-2 text-sm text-green-700">
                            📷 {proc.images_count} gambar tersedia
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Clinical Info */}
                {selectedOrder.clinical_indication && (
                  <div>
                    <span className="font-medium text-gray-700">Indikasi Klinis:</span>
                    <p className="text-gray-900 mt-1">{selectedOrder.clinical_indication}</p>
                  </div>
                )}

                {selectedOrder.notes && (
                  <div>
                    <span className="font-medium text-gray-700">Catatan:</span>
                    <p className="text-gray-900 mt-1">{selectedOrder.notes}</p>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Tutup
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results Modal */}
      {selectedOrder && viewResults && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Hasil Radiologi</h3>
                  <p className="text-sm text-gray-600">{selectedOrder.order_number}</p>
                </div>
                <button
                  onClick={() => {
                    setViewResults(false);
                    setSelectedOrder(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                {selectedOrder.procedures.map((proc) => (
                  <div key={proc.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-2xl">{getModalityIcon(proc.modality)}</span>
                      <h4 className="font-semibold text-gray-900">{proc.procedure_name}</h4>
                    </div>

                    {proc.images_count && proc.images_count > 0 && (
                      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center text-blue-900">
                            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                            </svg>
                            <span className="font-medium">{proc.images_count} gambar tersedia</span>
                          </div>
                          <button className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                            Lihat Gambar
                          </button>
                        </div>
                      </div>
                    )}

                    {proc.report ? (
                      <div className="p-4 bg-gray-50 rounded">
                        <span className="font-medium text-gray-700">Laporan:</span>
                        <p className="text-gray-900 mt-2 whitespace-pre-wrap">{proc.report}</p>
                      </div>
                    ) : (
                      <div className="text-center py-4 text-gray-500">
                        Laporan belum tersedia
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-6 flex justify-between">
                <div className="text-sm text-gray-500">
                  Selesai: {new Date(selectedOrder.completed_at || '').toLocaleString('id-ID')}
                </div>
                <button
                  onClick={() => {
                    setViewResults(false);
                    setSelectedOrder(null);
                  }}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Tutup
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
