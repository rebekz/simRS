"use client";

import React, { useState, useEffect } from 'react';

// Types
interface Bed {
  id: number;
  bed_number: string;
  bed_type: string;
  status: 'available' | 'occupied' | 'maintenance' | 'reserved';
  room_number: string;
  room_class: string;
  ward_id: number;
  floor: number;
  current_patient_id?: number;
  current_patient_name?: string;
}

interface DashboardSummary {
  hospital_name: string;
  last_updated: string;
  total_beds: number;
  total_available: number;
  total_occupied: number;
  total_maintenance: number;
  occupancy_rate: number;
  by_class: Record<string, { total: number; available: number; occupied: number; maintenance: number }>;
  by_ward: Record<string, { total: number; available: number; occupied: number }>;
  icu_total: number;
  icu_available: number;
  icu_occupancy_rate: number;
  available_vvip: number;
  available_vip: number;
  available_class_1: number;
  available_class_2: number;
  available_class_3: number;
}

interface WardSummary {
  ward_id: number;
  ward_name: string;
  room_class: string;
  total_beds: number;
  available_beds: number;
  occupied_beds: number;
  maintenance_beds: number;
  reserved_beds: number;
  occupancy_rate: number;
  male_available: number;
  female_available: number;
  mixed_available: number;
}

interface BedRequest {
  request_id: number;
  patient_id: number;
  patient_name: string;
  priority: string;
  requested_room_class?: string;
  requested_ward_id?: number;
  status: string;
  created_at: string;
}

interface DashboardData {
  summary: DashboardSummary;
  wards: WardSummary[];
  recently_assigned: any[];
  bed_requests_pending: BedRequest[];
  available_beds: Bed[];
}

const ROOM_CLASS_NAMES: Record<string, string> = {
  'vvip': 'VVIP',
  'vip': 'VIP',
  '1': 'Kelas 1',
  '2': 'Kelas 2',
  '3': 'Kelas 3',
};

const STATUS_COLORS: Record<string, string> = {
  'available': 'bg-green-100 text-green-800 border-green-300',
  'occupied': 'bg-red-100 text-red-800 border-red-300',
  'maintenance': 'bg-yellow-100 text-yellow-800 border-yellow-300',
  'reserved': 'bg-blue-100 text-blue-800 border-blue-300',
};

const STATUS_LABELS: Record<string, string> = {
  'available': 'Tersedia',
  'occupied': 'Terisi',
  'maintenance': 'Perbaikan',
  'reserved': 'Reservasi',
};

export default function BedDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedWard, setSelectedWard] = useState<number | null>(null);
  const [selectedClass, setSelectedClass] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  async function fetchDashboard() {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/bed/dashboard');
      const dashboardData = await response.json();
      setData(dashboardData);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    } finally {
      setLoading(false);
    }
  }

  function getFilteredBeds(): Bed[] {
    if (!data) return [];
    let beds = data.available_beds;

    if (selectedWard) {
      beds = beds.filter(b => b.ward_id === selectedWard);
    }
    if (selectedClass) {
      beds = beds.filter(b => b.room_class === selectedClass);
    }

    return beds;
  }

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const filteredBeds = getFilteredBeds();

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Manajemen Tempat Tidur</h1>
        <p className="text-gray-600">Sistem Informasi Manajemen Rumah Sakit</p>
        <p className="text-sm text-gray-500 mt-1">
          Terakhir diperbarui: {new Date(data.summary.last_updated).toLocaleString('id-ID')}
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Total Tempat Tidur</div>
          <div className="text-3xl font-bold text-gray-900">{data.summary.total_beds}</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-6 border border-green-200">
          <div className="text-sm text-green-700 mb-1">Tersedia</div>
          <div className="text-3xl font-bold text-green-700">{data.summary.total_available}</div>
        </div>
        <div className="bg-red-50 rounded-lg shadow p-6 border border-red-200">
          <div className="text-sm text-red-700 mb-1">Terisi</div>
          <div className="text-3xl font-bold text-red-700">{data.summary.total_occupied}</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-6 border border-blue-200">
          <div className="text-sm text-blue-700 mb-1">Tingkat Okupansi</div>
          <div className="text-3xl font-bold text-blue-700">{data.summary.occupancy_rate.toFixed(1)}%</div>
        </div>
      </div>

      {/* ICU Status */}
      <div className="bg-white rounded-lg shadow p-6 mb-6 border-l-4 border-orange-500">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Unit Perawatan Intensif (ICU)</h3>
            <p className="text-sm text-gray-600">Ketersediaan tempat tidur ICU</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-orange-600">
              {data.summary.icu_available} / {data.summary.icu_total}
            </div>
            <div className="text-sm text-gray-600">
              Okupansi: {data.summary.icu_occupancy_rate.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Available Beds by Class */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tempat Tidur Tersedia per Kelas</h3>
        <div className="grid grid-cols-5 gap-4">
          {[
            { class: 'vvip', label: 'VVIP', count: data.summary.available_vvip },
            { class: 'vip', label: 'VIP', count: data.summary.available_vip },
            { class: '1', label: 'Kelas 1', count: data.summary.available_class_1 },
            { class: '2', label: 'Kelas 2', count: data.summary.available_class_2 },
            { class: '3', label: 'Kelas 3', count: data.summary.available_class_3 },
          ].map((item) => (
            <div key={item.class} className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{item.count}</div>
              <div className="text-sm text-gray-600">{item.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Tempat Tidur</h3>
        <div className="flex gap-4">
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedWard || ''}
            onChange={(e) => setSelectedWard(e.target.value ? parseInt(e.target.value) : null)}
          >
            <option value="">Semua Ruang Rawat</option>
            {data.wards
              .filter((w, i, arr) => arr.findIndex(x => x.ward_id === w.ward_id) === i)
              .map(ward => (
                <option key={ward.ward_id} value={ward.ward_id}>{ward.ward_name}</option>
              ))}
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedClass || ''}
            onChange={(e) => setSelectedClass(e.target.value || null)}
          >
            <option value="">Semua Kelas</option>
            <option value="vvip">VVIP</option>
            <option value="vip">VIP</option>
            <option value="1">Kelas 1</option>
            <option value="2">Kelas 2</option>
            <option value="3">Kelas 3</option>
          </select>
        </div>
      </div>

      {/* Available Beds Grid */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Tempat Tidur Tersedia ({filteredBeds.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredBeds.map(bed => (
            <div key={bed.id} className="border-2 rounded-lg p-4 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="text-lg font-bold text-gray-900">{bed.bed_number}</div>
                  <div className="text-sm text-gray-600">Kamar {bed.room_number}</div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${STATUS_COLORS[bed.status]}`}>
                  {STATUS_LABELS[bed.status]}
                </span>
              </div>
              <div className="text-sm text-gray-700">
                <div>Kelas: {ROOM_CLASS_NAMES[bed.room_class] || bed.room_class}</div>
                <div>Lantai: {bed.floor}</div>
                <div>Tipe: {bed.bed_type}</div>
              </div>
            </div>
          ))}
        </div>
        {filteredBeds.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Tidak ada tempat tidur tersedia dengan filter yang dipilih
          </div>
        )}
      </div>

      {/* Pending Bed Requests */}
      {data.bed_requests_pending.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Permintaan Tempat Tidur Pending ({data.bed_requests_pending.length})
          </h3>
          <div className="space-y-3">
            {data.bed_requests_pending.map(request => (
              <div key={request.request_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-semibold text-gray-900">{request.patient_name}</div>
                    <div className="text-sm text-gray-600">
                      Prioritas: <span className="font-semibold">{request.priority.toUpperCase()}</span>
                    </div>
                    {request.requested_room_class && (
                      <div className="text-sm text-gray-600">
                        Kelas: {ROOM_CLASS_NAMES[request.requested_room_class]}
                      </div>
                    )}
                    <div className="text-xs text-gray-500">
                      {new Date(request.created_at).toLocaleString('id-ID')}
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                    Assign
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
