"use client";

import React, { useState, useEffect } from 'react';
import { Search, Filter, CheckCircle, XCircle, Clock, Calendar, RefreshCw, Edit, Trash2, Eye, Loader2, Plus } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { FormInput } from '@/components/ui/form/FormInput';
import { FormSelect } from '@/components/ui/form/FormSelect';
import { cn } from '@/lib/utils';

// Types
interface Appointment {
  id: string;
  queue_number: string;
  patient_name: string;
  patient_phone: string;
  patient_nik?: string;
  department: string;
  department_id: string;
  doctor_name: string;
  doctor_id: string;
  appointment_date: string;
  time_slot: string;
  time_slot_id: string;
  reason: string;
  status: 'scheduled' | 'confirmed' | 'checked_in' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  queue_position?: number;
  estimated_wait_minutes?: number;
  check_in_time?: string;
  start_time?: string;
  end_time?: string;
  notes?: string;
  created_at: string;
}

interface Department {
  id: string;
  name: string;
}

interface Doctor {
  id: string;
  name: string;
}

interface SlotConfig {
  id: string;
  doctor_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  slot_duration: number;
  max_bookings: number;
  is_active: boolean;
}

interface AppointmentAdminProps {
  department?: string;
  onEdit?: (appointment: Appointment) => void;
  onDelete?: (appointment: Appointment) => void;
}

export default function AppointmentAdmin({ department, onEdit, onDelete }: AppointmentAdminProps) {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [showSlotConfig, setShowSlotConfig] = useState(false);

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState(department || 'all');
  const [filterDoctor, setFilterDoctor] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterDate, setFilterDate] = useState('');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  useEffect(() => {
    fetchDepartments();
    fetchAppointments();
  }, []);

  useEffect(() => {
    if (filterDepartment && filterDepartment !== 'all') {
      fetchDoctors(filterDepartment);
    }
  }, [filterDepartment]);

  async function fetchDepartments() {
    try {
      const response = await fetch('/api/v1/appointments/departments');
      const data = await response.json();
      setDepartments(data);
    } catch (error) {
      console.error('Failed to fetch departments:', error);
    }
  }

  async function fetchDoctors(departmentId: string) {
    try {
      const response = await fetch(`/api/v1/appointments/departments/${departmentId}/doctors`);
      const data = await response.json();
      setDoctors(data);
    } catch (error) {
      console.error('Failed to fetch doctors:', error);
    }
  }

  async function fetchAppointments() {
    setLoading(true);
    try {
      const params = new URLSearchParams();

      if (filterDepartment && filterDepartment !== 'all') {
        params.append('department', filterDepartment);
      }
      if (filterDoctor && filterDoctor !== 'all') {
        params.append('doctor', filterDoctor);
      }
      if (filterStatus && filterStatus !== 'all') {
        params.append('status', filterStatus);
      }
      if (filterDate) {
        params.append('date', filterDate);
      }

      const response = await fetch(`/api/v1/appointments?${params}`);
      const data = await response.json();
      setAppointments(data.appointments || []);
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleStatusChange(appointment: Appointment, newStatus: Appointment['status']) {
    try {
      const response = await fetch(`/api/v1/appointments/${appointment.id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) throw new Error('Gagal mengubah status');

      await fetchAppointments();
    } catch (error: any) {
      alert(error.message);
    }
  }

  async function handleDelete(appointment: Appointment) {
    if (!confirm(`Hapus janji temu ${appointment.queue_number} - ${appointment.patient_name}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/appointments/${appointment.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Gagal menghapus janji temu');

      await fetchAppointments();
      if (onDelete) onDelete(appointment);
    } catch (error: any) {
      alert(error.message);
    }
  }

  function getStatusVariant(status: Appointment['status']): 'success' | 'warning' | 'error' | 'info' | 'primary' | 'neutral' {
    switch (status) {
      case 'scheduled':
        return 'primary';
      case 'confirmed':
        return 'info';
      case 'checked_in':
        return 'warning';
      case 'in_progress':
        return 'warning';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'error';
      case 'no_show':
        return 'error';
      default:
        return 'neutral';
    }
  }

  function getStatusLabel(status: Appointment['status']): string {
    const labels: Record<string, string> = {
      scheduled: 'Terjadwal',
      confirmed: 'Dikonfirmasi',
      checked_in: 'Check-in',
      in_progress: 'Dilayani',
      completed: 'Selesai',
      cancelled: 'Dibatalkan',
      no_show: 'Tidak Hadir',
    };
    return labels[status] || status;
  }

  // Filter appointments
  const filteredAppointments = appointments.filter(apt => {
    const matchesSearch = searchTerm === '' ||
      apt.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      apt.queue_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      apt.patient_phone.includes(searchTerm);

    return matchesSearch;
  });

  // Paginate
  const totalPages = Math.ceil(filteredAppointments.length / itemsPerPage);
  const paginatedAppointments = filteredAppointments.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Manajemen Janji Temu</h2>
              <p className="text-gray-600 mt-1">
                {filteredAppointments.length} janji temu
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button variant="primary">
                <Plus className="w-4 h-4 mr-2" />
                Buat Janji Temu
              </Button>

              <Button
                variant="icon"
                onClick={() => setShowFilters(!showFilters)}
                icon={<Filter className="w-5 h-5" />}
              />

              <Button
                variant="icon"
                onClick={fetchAppointments}
                icon={<RefreshCw className="w-5 h-5" />}
              />

              <Button
                variant="secondary"
                onClick={() => setShowSlotConfig(!showSlotConfig)}
              >
                <Calendar className="w-4 h-4 mr-2" />
                Konfigurasi Jadwal
              </Button>
            </div>
          </div>

          {/* Search */}
          <div className="mt-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Cari nama pasien, nomor antrian, atau telepon..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid md:grid-cols-4 gap-4">
                {/* Department Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Departemen
                  </label>
                  <select
                    value={filterDepartment}
                    onChange={(e) => {
                      setFilterDepartment(e.target.value);
                      setFilterDoctor('all');
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all">Semua Departemen</option>
                    {departments.map(dept => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Doctor Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dokter
                  </label>
                  <select
                    value={filterDoctor}
                    onChange={(e) => setFilterDoctor(e.target.value)}
                    disabled={!filterDepartment || filterDepartment === 'all'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    <option value="all">Semua Dokter</option>
                    {doctors.map(doc => (
                      <option key={doc.id} value={doc.id}>
                        {doc.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all">Semua Status</option>
                    <option value="scheduled">Terjadwal</option>
                    <option value="confirmed">Dikonfirmasi</option>
                    <option value="checked_in">Check-in</option>
                    <option value="in_progress">Dilayani</option>
                    <option value="completed">Selesai</option>
                    <option value="cancelled">Dibatalkan</option>
                    <option value="no_show">Tidak Hadir</option>
                  </select>
                </div>

                {/* Date Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tanggal
                  </label>
                  <input
                    type="date"
                    value={filterDate}
                    onChange={(e) => setFilterDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="mt-4 flex gap-2">
                <Button variant="primary" onClick={fetchAppointments}>
                  Terapkan Filter
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setFilterDepartment('all');
                    setFilterDoctor('all');
                    setFilterStatus('all');
                    setFilterDate('');
                    setSearchTerm('');
                  }}
                >
                  Reset
                </Button>
              </div>
            </div>
          )}
        </CardHeader>
      </Card>

      {/* Slot Configuration */}
      {showSlotConfig && (
        <SlotConfiguration
          department={filterDepartment}
          onClose={() => setShowSlotConfig(false)}
          onSave={fetchAppointments}
        />
      )}

      {/* Appointments List */}
      <Card>
        <CardBody>
          {loading ? (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-3" />
              <p className="text-gray-600">Memuat janji temu...</p>
            </div>
          ) : paginatedAppointments.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Tidak ada janji temu ditemukan</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">No. Antrian</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Pasien</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Jadwal</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Dokter</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedAppointments.map((apt) => (
                    <tr key={apt.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="font-mono font-bold text-blue-600">{apt.queue_number}</div>
                        {apt.queue_position && (
                          <div className="text-xs text-gray-500">Antrian #{apt.queue_position}</div>
                        )}
                      </td>

                      <td className="py-3 px-4">
                        <div className="font-semibold text-gray-900">{apt.patient_name}</div>
                        <div className="text-sm text-gray-600">{apt.patient_phone}</div>
                      </td>

                      <td className="py-3 px-4">
                        <div className="text-gray-900">
                          {new Date(apt.appointment_date).toLocaleDateString('id-ID', {
                            weekday: 'short',
                            day: 'numeric',
                            month: 'short',
                          })}
                        </div>
                        <div className="text-sm text-gray-600">{apt.time_slot}</div>
                        {apt.estimated_wait_minutes && (
                          <div className="text-xs text-gray-500">
                            ~{apt.estimated_wait_minutes} menit
                          </div>
                        )}
                      </td>

                      <td className="py-3 px-4">
                        <div className="text-gray-900">{apt.doctor_name}</div>
                        <div className="text-sm text-gray-600">{apt.department}</div>
                      </td>

                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {getStatusLabel(apt.status)}
                        </span>
                      </td>

                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1">
                          {/* Check-in */}
                          {['scheduled', 'confirmed'].includes(apt.status) && (
                            <button
                              onClick={() => handleStatusChange(apt, 'checked_in')}
                              className="p-2 rounded hover:bg-green-50 text-green-600 transition-colors"
                              title="Check-in"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                          )}

                          {/* Start Serving */}
                          {apt.status === 'checked_in' && (
                            <button
                              onClick={() => handleStatusChange(apt, 'in_progress')}
                              className="p-2 rounded hover:bg-blue-50 text-blue-600 transition-colors"
                              title="Mulai Layani"
                            >
                              <Clock className="w-5 h-5" />
                            </button>
                          )}

                          {/* Complete */}
                          {apt.status === 'in_progress' && (
                            <button
                              onClick={() => handleStatusChange(apt, 'completed')}
                              className="p-2 rounded hover:bg-green-50 text-green-600 transition-colors"
                              title="Selesai"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                          )}

                          {/* View */}
                          <button
                            onClick={() => setSelectedAppointment(apt)}
                            className="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors"
                            title="Lihat Detail"
                          >
                            <Eye className="w-5 h-5" />
                          </button>

                          {/* Edit */}
                          <button
                            onClick={() => onEdit?.(apt)}
                            className="p-2 rounded hover:bg-blue-50 text-blue-600 transition-colors"
                            title="Edit"
                          >
                            <Edit className="w-5 h-5" />
                          </button>

                          {/* Delete */}
                          <button
                            onClick={() => handleDelete(apt)}
                            className="p-2 rounded hover:bg-red-50 text-red-600 transition-colors"
                            title="Hapus"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
              <div className="text-sm text-gray-600">
                Menampilkan {(currentPage - 1) * itemsPerPage + 1} -{' '}
                {Math.min(currentPage * itemsPerPage, filteredAppointments.length)} dari{' '}
                {filteredAppointments.length} janji temu
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  Sebelumnya
                </Button>

                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page)}
                      className={cn(
                        'w-10 h-10 rounded-lg font-medium transition-colors',
                        currentPage === page
                          ? 'bg-blue-600 text-white'
                          : 'hover:bg-gray-100 text-gray-700'
                      )}
                    >
                      {page}
                    </button>
                  ))}
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  Selanjutnya
                </Button>
              </div>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Appointment Detail Modal */}
      {selectedAppointment && (
        <AppointmentDetailModal
          appointment={selectedAppointment}
          onClose={() => setSelectedAppointment(null)}
          onStatusChange={(status) => {
            handleStatusChange(selectedAppointment, status);
            setSelectedAppointment(null);
          }}
        />
      )}
    </div>
  );
}

// Slot Configuration Component
function SlotConfiguration({ department, onClose, onSave }: { department: string; onClose: () => void; onSave: () => void }) {
  const [slots, setSlots] = useState<SlotConfig[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (department && department !== 'all') {
      fetchSlots();
    }
  }, [department]);

  async function fetchSlots() {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/appointments/departments/${department}/slots`);
      const data = await response.json();
      setSlots(data.slots || []);
    } catch (error) {
      console.error('Failed to fetch slots:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card variant="elevated">
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-gray-900">Konfigurasi Jadwal</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            Tutup
          </Button>
        </div>
      </CardHeader>

      <CardBody>
        {loading ? (
          <div className="text-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-gray-600">
              Konfigurasikan jadwal praktik dokter dan slot waktu yang tersedia.
            </p>

            {slots.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Belum ada konfigurasi jadwal. Silakan tambah jadwal baru.
              </div>
            ) : (
              <div className="space-y-3">
                {slots.map(slot => (
                  <div
                    key={slot.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-semibold text-gray-900">
                        Hari ke-{slot.day_of_week}
                      </div>
                      <div className="text-sm text-gray-600">
                        {slot.start_time} - {slot.end_time}
                      </div>
                      <div className="text-sm text-gray-600">
                        Durasi: {slot.slot_duration} menit | Max: {slot.max_bookings}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className={cn(
                        'px-2 py-1 rounded text-xs font-medium',
                        slot.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                      )}>
                        {slot.is_active ? 'Aktif' : 'Nonaktif'}
                      </span>

                      <Button variant="icon" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>

                      <Button variant="icon" size="sm">
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <Button variant="primary" className="w-full">
              <Plus className="w-4 h-4 mr-2" />
              Tambah Jadwal Baru
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  );
}

// Appointment Detail Modal
function AppointmentDetailModal({
  appointment,
  onClose,
  onStatusChange
}: {
  appointment: Appointment;
  onClose: () => void;
  onStatusChange: (status: Appointment['status']) => void;
}) {
  const statuses: { value: Appointment['status']; label: string }[] = [
    { value: 'scheduled', label: 'Terjadwal' },
    { value: 'confirmed', label: 'Dikonfirmasi' },
    { value: 'checked_in', label: 'Check-in' },
    { value: 'in_progress', label: 'Dilayani' },
    { value: 'completed', label: 'Selesai' },
    { value: 'cancelled', label: 'Dibatalkan' },
    { value: 'no_show', label: 'Tidak Hadir' },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-900">Detail Janji Temu</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XCircle className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Queue Number */}
          <div className="text-center py-6 bg-blue-50 rounded-lg">
            <div className="text-sm text-blue-600 mb-2">Nomor Antrian</div>
            <div className="text-5xl font-bold text-blue-600">{appointment.queue_number}</div>
          </div>

          {/* Patient Info */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Informasi Pasien</h4>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Nama</span>
                <span className="font-medium text-gray-900">{appointment.patient_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Telepon</span>
                <span className="font-medium text-gray-900">{appointment.patient_phone}</span>
              </div>
              {appointment.patient_nik && (
                <div className="flex justify-between">
                  <span className="text-gray-600">NIK</span>
                  <span className="font-medium text-gray-900">{appointment.patient_nik}</span>
                </div>
              )}
            </div>
          </div>

          {/* Appointment Info */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Jadwal</h4>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Tanggal</span>
                <span className="font-medium text-gray-900">
                  {new Date(appointment.appointment_date).toLocaleDateString('id-ID', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Jam</span>
                <span className="font-medium text-gray-900">{appointment.time_slot}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Departemen</span>
                <span className="font-medium text-gray-900">{appointment.department}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Dokter</span>
                <span className="font-medium text-gray-900">{appointment.doctor_name}</span>
              </div>
            </div>
          </div>

          {/* Reason */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Alasan Kunjungan</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-700">{appointment.reason || '-'}</p>
            </div>
          </div>

          {/* Status Change */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Ubah Status</h4>
            <div className="grid grid-cols-2 gap-2">
              {statuses.map(status => (
                <button
                  key={status.value}
                  onClick={() => onStatusChange(status.value)}
                  className={cn(
                    'p-3 rounded-lg border-2 text-left transition-all',
                    appointment.status === status.value
                      ? 'border-blue-600 bg-blue-50 text-blue-700 font-medium'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  )}
                >
                  {status.label}
                </button>
              ))}
            </div>
          </div>

          {/* Timestamps */}
          <div className="text-sm text-gray-500 space-y-1">
            <div>Dibuat: {new Date(appointment.created_at).toLocaleString('id-ID')}</div>
            {appointment.check_in_time && (
              <div>Check-in: {new Date(appointment.check_in_time).toLocaleString('id-ID')}</div>
            )}
            {appointment.start_time && (
              <div>Mulai: {new Date(appointment.start_time).toLocaleString('id-ID')}</div>
            )}
            {appointment.end_time && (
              <div>Selesai: {new Date(appointment.end_time).toLocaleString('id-ID')}</div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white border-t border-gray-200 p-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>
            Tutup
          </Button>
        </div>
      </div>
    </div>
  );
}
