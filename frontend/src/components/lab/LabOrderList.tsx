"use client";

import React, { useState, useEffect } from 'react';

// Types
interface LabOrder {
  id: number;
  order_number: string;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  encounter_id?: number;
  status: 'pending' | 'sample_collected' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'routine' | 'urgent' | 'stat';
  clinical_indication: string;
  notes?: string;
  ordered_by: string;
  ordered_at: string;
  tests: LabOrderTest[];
  sample_collected_at?: string;
  completed_at?: string;
  results_available?: boolean;
}

interface LabOrderTest {
  id: number;
  test_id: number;
  test_code: string;
  test_name: string;
  specimen_type: string;
  status: 'pending' | 'in_progress' | 'completed';
  result?: string;
  reference_range?: string;
  abnormal_flag?: boolean;
  unit?: string;
}

interface LabOrderListProps {
  patientId?: number;
  encounterId?: number;
  status?: string;
  limit?: number;
  onOrderClick?: (order: LabOrder) => void;
  showResults?: boolean;
}

export default function LabOrderList({
  patientId,
  encounterId,
  status,
  limit = 20,
  onOrderClick,
  showResults = true
}: LabOrderListProps) {
  const [orders, setOrders] = useState<LabOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<LabOrder | null>(null);
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

      const response = await fetch(`/api/v1/lab/orders?${params}`);
      const data = await response.json();
      setOrders(data.results || data.orders || []);
    } catch (error) {
      console.error('Failed to fetch lab orders:', error);
    } finally {
      setLoading(false);
    }
  };

  function getStatusBadge(status: string): { text: string; className: string } {
    switch (status) {
      case 'pending':
        return { text: 'Menunggu', className: 'bg-yellow-100 text-yellow-800' };
      case 'sample_collected':
        return { text: 'Sampel Diambil', className: 'bg-blue-100 text-blue-800' };
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

  function handleOrderClick(order: LabOrder) {
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
      const response = await fetch(`/api/v1/lab/orders/${orderId}/cancel`, {
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

  function handleViewResults(order: LabOrder) {
    setSelectedOrder(order);
    setViewResults(true);
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Pesanan Laboratorium</h2>
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
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="mt-2">Belum ada pesanan laboratorium</p>
        </div>
      )}

      {!loading && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => {
            const statusBadge = getStatusBadge(order.status);
            const priorityBadge = getPriorityBadge(order.priority);

            return (
              <div
                key={order.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleOrderClick(order)}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-gray-900">
                        {order.order_number}
                      </span>
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
                      {order.sample_collected_at && (
                        <span className="ml-3">
                          Sampel: {new Date(order.sample_collected_at).toLocaleString('id-ID')}
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
                    {(order.status === 'pending' || order.status === 'sample_collected') && (
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

                {/* Tests Summary */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="text-sm text-gray-600 mb-2">
                    Pemeriksaan ({order.tests.length}):
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {order.tests.slice(0, 5).map((test) => (
                      <span
                        key={test.id}
                        className={`px-2 py-1 text-xs rounded ${
                          test.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : test.status === 'in_progress'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {test.test_name}
                      </span>
                    ))}
                    {order.tests.length > 5 && (
                      <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                        +{order.tests.length - 5} lainnya
                      </span>
                    )}
                  </div>
                </div>

                {/* Clinical Indication */}
                {order.clinical_indication && (
                  <div className="mt-3 text-sm">
                    <span className="font-medium text-gray-700">Indikasi:</span>
                    <p className="text-gray-600 mt-1">{order.clinical_indication}</p>
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

                {/* Tests List */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Pemeriksaan</h4>
                  <div className="space-y-2">
                    {selectedOrder.tests.map((test) => (
                      <div key={test.id} className="p-3 border border-gray-200 rounded">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-gray-900">{test.test_name}</div>
                            <div className="text-sm text-gray-600">
                              {test.test_code} - {test.specimen_type}
                            </div>
                          </div>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${
                              test.status === 'completed'
                                ? 'bg-green-100 text-green-800'
                                : test.status === 'in_progress'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {test.status === 'completed'
                              ? 'Selesai'
                              : test.status === 'in_progress'
                              ? 'Diproses'
                              : 'Menunggu'}
                          </span>
                        </div>
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
                  <h3 className="text-xl font-bold text-gray-900">Hasil Laboratorium</h3>
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
                {selectedOrder.tests.map((test) => (
                  <div key={test.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{test.test_name}</h4>
                        <p className="text-sm text-gray-600">{test.test_code}</p>
                      </div>
                      {test.abnormal_flag && (
                        <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded">
                          Abnormal
                        </span>
                      )}
                    </div>

                    {test.result ? (
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Hasil:</span>
                          <p className={`text-lg font-semibold ${
                            test.abnormal_flag ? 'text-red-600' : 'text-gray-900'
                          }`}>
                            {test.result} {test.unit || ''}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Nilai Rujukan:</span>
                          <p className="text-gray-900">{test.reference_range || '-'}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Status:</span>
                          <p className="text-green-700 font-medium">Selesai</p>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-4 text-gray-500">
                        Hasil belum tersedia
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
