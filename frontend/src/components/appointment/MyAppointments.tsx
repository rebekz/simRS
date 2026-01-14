"use client";

import React, { useState, useEffect } from 'react';
import { Calendar, Clock, User, Phone, X, RefreshCw, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { cn, formatDateTime } from '@/lib/utils';

// Types
interface Appointment {
  id: string;
  queue_number: string;
  patient_name: string;
  patient_phone: string;
  department: string;
  doctor_name: string;
  appointment_date: string;
  time_slot: string;
  reason: string;
  status: 'scheduled' | 'confirmed' | 'checked_in' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  queue_position?: number;
  estimated_wait_minutes?: number;
  created_at: string;
}

interface MyAppointmentsProps {
  patientId?: string;
  onReschedule?: (appointment: Appointment) => void;
  onCancel?: (appointment: Appointment) => void;
}

export default function MyAppointments({
  patientId,
  onReschedule,
  onCancel,
}: MyAppointmentsProps) {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [expandedAppointment, setExpandedAppointment] = useState<string | null>(null);

  useEffect(() => {
    fetchAppointments();
  }, [patientId, filterStatus]);

  async function fetchAppointments() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterStatus !== 'all') {
        params.append('status', filterStatus);
      }

      const response = await fetch(`/api/v1/appointments/my?${params}`);
      const data = await response.json();
      setAppointments(data.appointments || []);
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    await fetchAppointments();
    setRefreshing(false);
  }

  async function handleCancel(appointment: Appointment) {
    if (!confirm('Apakah Anda yakin ingin membatalkan janji temu ini?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/appointments/${appointment.id}/cancel`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Gagal membatalkan janji temu');
      }

      await fetchAppointments();
      if (onCancel) {
        onCancel(appointment);
      }
    } catch (error: any) {
      console.error('Failed to cancel appointment:', error);
      alert(error.message);
    }
  }

  function handleReschedule(appointment: Appointment) {
    if (onReschedule) {
      onReschedule(appointment);
    }
  }

  function getStatusVariant(status: Appointment['status']): 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral' {
    switch (status) {
      case 'scheduled':
        return 'primary';
      case 'confirmed':
        return 'info';
      case 'checked_in':
      case 'in_progress':
        return 'warning';
      case 'completed':
        return 'success';
      case 'cancelled':
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
      checked_in: 'Sudah Check-in',
      in_progress: 'Sedang Dilayani',
      completed: 'Selesai',
      cancelled: 'Dibatalkan',
      no_show: 'Tidak Hadir',
    };
    return labels[status] || status;
  }

  function getStatusColor(status: Appointment['status']): string {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'confirmed':
        return 'bg-cyan-100 text-cyan-800 border-cyan-200';
      case 'checked_in':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'in_progress':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'no_show':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  }

  function isUpcoming(appointment: Appointment): boolean {
    const appointmentDate = new Date(appointment.appointment_date);
    const now = new Date();
    return appointmentDate > now && !['cancelled', 'no_show', 'completed'].includes(appointment.status);
  }

  function canCancel(appointment: Appointment): boolean {
    return ['scheduled', 'confirmed'].includes(appointment.status);
  }

  function canReschedule(appointment: Appointment): boolean {
    return ['scheduled', 'confirmed'].includes(appointment.status);
  }

  function toggleExpand(appointmentId: string) {
    setExpandedAppointment(expandedAppointment === appointmentId ? null : appointmentId);
  }

  const upcomingAppointments = appointments.filter(isUpcoming);
  const pastAppointments = appointments.filter(apt => !isUpcoming(apt));

  if (loading) {
    return (
      <Card>
        <CardBody className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Memuat janji temu...</span>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Janji Temu Saya</h2>
              <p className="text-gray-600 mt-1">
                {appointments.length} janji temu
                {upcomingAppointments.length > 0 && ` (${upcomingAppointments.length} akan datang)`}
              </p>
            </div>

            <div className="flex items-center gap-2">
              {/* Status Filter */}
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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

              <Button
                variant="icon"
                size="sm"
                onClick={handleRefresh}
                loading={refreshing}
                icon={<RefreshCw className={cn('w-5 h-5', refreshing && 'animate-spin')} />}
              />
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Upcoming Appointments */}
      {upcomingAppointments.length > 0 && (
        <Card>
          <CardHeader title="Akan Datang" />
          <CardBody className="space-y-4">
            {upcomingAppointments.map(appointment => (
              <AppointmentCard
                key={appointment.id}
                appointment={appointment}
                expanded={expandedAppointment === appointment.id}
                onToggleExpand={() => toggleExpand(appointment.id)}
                onCancel={() => handleCancel(appointment)}
                onReschedule={() => handleReschedule(appointment)}
                getStatusColor={getStatusColor}
                getStatusLabel={getStatusLabel}
                canCancel={canCancel}
                canReschedule={canReschedule}
              />
            ))}
          </CardBody>
        </Card>
      )}

      {/* Past Appointments */}
      {pastAppointments.length > 0 && (
        <Card>
          <CardHeader title="Riwayat" />
          <CardBody className="space-y-4">
            {pastAppointments.map(appointment => (
              <AppointmentCard
                key={appointment.id}
                appointment={appointment}
                expanded={expandedAppointment === appointment.id}
                onToggleExpand={() => toggleExpand(appointment.id)}
                onCancel={() => handleCancel(appointment)}
                onReschedule={() => handleReschedule(appointment)}
                getStatusColor={getStatusColor}
                getStatusLabel={getStatusLabel}
                canCancel={canCancel}
                canReschedule={canReschedule}
              />
            ))}
          </CardBody>
        </Card>
      )}

      {/* Empty State */}
      {appointments.length === 0 && (
        <Card>
          <CardBody className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Belum Ada Janji Temu
            </h3>
            <p className="text-gray-600 mb-6">
              Anda belum memiliki janji temu. Buat janji temu sekarang untuk mendapatkan layanan kesehatan.
            </p>
            <Button variant="primary">
              Buat Janji Temu Baru
            </Button>
          </CardBody>
        </Card>
      )}
    </div>
  );
}

// Appointment Card Component
interface AppointmentCardProps {
  appointment: Appointment;
  expanded: boolean;
  onToggleExpand: () => void;
  onCancel: () => void;
  onReschedule: () => void;
  getStatusColor: (status: Appointment['status']) => string;
  getStatusLabel: (status: Appointment['status']) => string;
  canCancel: (appointment: Appointment) => boolean;
  canReschedule: (appointment: Appointment) => boolean;
}

function AppointmentCard({
  appointment,
  expanded,
  onToggleExpand,
  onCancel,
  onReschedule,
  getStatusColor,
  getStatusLabel,
  canCancel,
  canReschedule,
}: AppointmentCardProps) {
  return (
    <div
      className={cn(
        'border-2 rounded-lg transition-all overflow-hidden',
        expanded ? 'border-blue-600' : 'border-gray-200 hover:border-gray-300'
      )}
    >
      {/* Summary */}
      <div
        className="p-4 cursor-pointer bg-white hover:bg-gray-50 transition-colors"
        onClick={onToggleExpand}
      >
        <div className="flex items-start justify-between">
          {/* Left: Queue Number and Date */}
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-xl flex-shrink-0">
              {appointment.queue_number}
            </div>

            <div>
              <div className="font-semibold text-gray-900 text-lg">
                {appointment.patient_name}
              </div>
              <div className="text-gray-600 mt-1">
                {appointment.department} - {appointment.doctor_name}
              </div>
              <div className="flex items-center gap-3 mt-2 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {new Date(appointment.appointment_date).toLocaleDateString('id-ID', {
                    weekday: 'short',
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  })}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {appointment.time_slot}
                </span>
              </div>
            </div>
          </div>

          {/* Right: Status and Actions */}
          <div className="flex flex-col items-end gap-2">
            <span className={cn('px-3 py-1 rounded-full text-sm font-medium border', getStatusColor(appointment.status))}>
              {getStatusLabel(appointment.status)}
            </span>

            {appointment.queue_position !== undefined && appointment.queue_position > 0 && (
              <div className="text-sm text-gray-600">
                Antrian ke-{appointment.queue_position}
              </div>
            )}

            {appointment.estimated_wait_minutes && (
              <div className="text-sm text-gray-600">
                Estimasi: ~{appointment.estimated_wait_minutes} menit
              </div>
            )}

            <button className="text-gray-400 hover:text-gray-600 mt-1">
              {expanded ? <ChevronLeft className="w-5 h-5 rotate-90" /> : <ChevronRight className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="border-t-2 border-gray-200 p-4 bg-gray-50">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Details */}
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-500">No. Telepon</div>
                <div className="font-medium text-gray-900 flex items-center gap-2">
                  <Phone className="w-4 h-4 text-gray-400" />
                  {appointment.patient_phone}
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-500">Alasan Kunjungan</div>
                <div className="font-medium text-gray-900">
                  {appointment.reason || '-'}
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-500">Dibuat Pada</div>
                <div className="font-medium text-gray-900">
                  {formatDateTime(appointment.created_at)}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col justify-end gap-2">
              {canReschedule(appointment) && (
                <Button
                  variant="secondary"
                  onClick={onReschedule}
                  className="w-full"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Jadwal Ulang
                </Button>
              )}

              {canCancel(appointment) && (
                <Button
                  variant="ghost"
                  onClick={onCancel}
                  className="w-full text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <X className="w-4 h-4 mr-2" />
                  Batalkan Janji Temu
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
