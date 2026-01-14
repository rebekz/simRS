"use client";

import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock, Filter } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { cn, formatDate } from '@/lib/utils';

// Types
interface Appointment {
  id: string;
  patient_name: string;
  department: string;
  doctor_name: string;
  date: string;
  time: string;
  status: 'scheduled' | 'confirmed' | 'checked_in' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  queue_number?: string;
}

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  appointments: Appointment[];
}

interface AppointmentCalendarProps {
  departmentFilter?: string;
  doctorFilter?: string;
  onDateSelect?: (date: Date) => void;
  onAppointmentClick?: (appointment: Appointment) => void;
  viewMode?: 'month' | 'day';
}

export default function AppointmentCalendar({
  departmentFilter,
  doctorFilter,
  onDateSelect,
  onAppointmentClick,
  viewMode = 'month',
}: AppointmentCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [calendarDays, setCalendarDays] = useState<CalendarDay[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Department and doctor options (in real app, fetch from API)
  const departments = [
    { id: 'all', name: 'Semua Poli' },
    { id: 'umum', name: 'Poli Umum' },
    { id: 'anak', name: 'Poli Anak' },
    { id: 'gigi', name: 'Poli Gigi' },
    { id: 'kandungan', name: 'Poli Kandungan' },
    { id: 'penyakit-dalam', name: 'Poli Penyakit Dalam' },
  ];

  useEffect(() => {
    generateCalendar();
    fetchAppointments();
  }, [currentDate, departmentFilter, doctorFilter]);

  function generateCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // First day of month
    const firstDay = new Date(year, month, 1);
    // Last day of month
    const lastDay = new Date(year, month + 1, 0);

    // Start from Sunday of the week containing first day
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    // End on Saturday of the week containing last day
    const endDate = new Date(lastDay);
    endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()));

    const days: CalendarDay[] = [];
    const current = new Date(startDate);

    while (current <= endDate) {
      days.push({
        date: new Date(current),
        isCurrentMonth: current.getMonth() === month,
        isToday: isSameDay(current, new Date()),
        appointments: [], // Will be filled by fetchAppointments
      });
      current.setDate(current.getDate() + 1);
    }

    setCalendarDays(days);
  }

  async function fetchAppointments() {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        start_date: formatDate(calendarDays[0]?.date || new Date()),
        end_date: formatDate(calendarDays[calendarDays.length - 1]?.date || new Date()),
      });

      if (departmentFilter && departmentFilter !== 'all') {
        params.append('department', departmentFilter);
      }
      if (doctorFilter) {
        params.append('doctor', doctorFilter);
      }

      const response = await fetch(`/api/v1/appointments?${params}`);
      const data = await response.json();

      // Group appointments by date and update calendar days
      const appointmentsByDate: Record<string, Appointment[]> = {};
      data.appointments?.forEach((apt: Appointment) => {
        const dateKey = apt.date.split('T')[0];
        if (!appointmentsByDate[dateKey]) {
          appointmentsByDate[dateKey] = [];
        }
        appointmentsByDate[dateKey].push(apt);
      });

      setCalendarDays(prev =>
        prev.map(day => ({
          ...day,
          appointments: appointmentsByDate[formatDate(day.date)] || [],
        }))
      );

      setAppointments(data.appointments || []);
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
    } finally {
      setLoading(false);
    }
  }

  function isSameDay(date1: Date, date2: Date): boolean {
    return (
      date1.getFullYear() === date2.getFullYear() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getDate() === date2.getDate()
    );
  }

  function previousMonth() {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  }

  function nextMonth() {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  }

  function goToToday() {
    setCurrentDate(new Date());
  }

  function handleDateClick(day: CalendarDay) {
    setSelectedDate(day.date);
    if (onDateSelect) {
      onDateSelect(day.date);
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
      checked_in: 'Check-in',
      in_progress: 'Dilayani',
      completed: 'Selesai',
      cancelled: 'Dibatalkan',
      no_show: 'Tidak Hadir',
    };
    return labels[status] || status;
  }

  function renderMonthView() {
    const weekDays = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'];

    return (
      <div className="space-y-4">
        {/* Calendar Grid */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          {/* Weekday Headers */}
          <div className="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
            {weekDays.map(day => (
              <div
                key={day}
                className="py-3 text-center text-sm font-semibold text-gray-700"
              >
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Days */}
          <div className="grid grid-cols-7">
            {calendarDays.map((day, index) => {
              const hasAppointments = day.appointments.length > 0;
              const isSelected = selectedDate && isSameDay(day.date, selectedDate);

              return (
                <div
                  key={index}
                  onClick={() => handleDateClick(day)}
                  className={cn(
                    'min-h-24 p-2 border-b border-r border-gray-200 cursor-pointer transition-colors',
                    !day.isCurrentMonth && 'bg-gray-50',
                    isSelected && 'bg-blue-50 ring-2 ring-inset ring-blue-600',
                    'hover:bg-gray-50'
                  )}
                >
                  {/* Date Number */}
                  <div className="flex items-center justify-between mb-1">
                    <span
                      className={cn(
                        'text-sm font-medium',
                        day.isToday && 'bg-blue-600 text-white w-7 h-7 rounded-full flex items-center justify-center',
                        !day.isToday && day.isCurrentMonth && 'text-gray-900',
                        !day.isCurrentMonth && 'text-gray-400'
                      )}
                    >
                      {day.date.getDate()}
                    </span>
                    {hasAppointments && (
                      <Badge variant="primary" className="text-xs">
                        {day.appointments.length}
                      </Badge>
                    )}
                  </div>

                  {/* Appointment Indicators */}
                  {hasAppointments && (
                    <div className="space-y-1">
                      {day.appointments.slice(0, 2).map((apt, aptIndex) => (
                        <div
                          key={aptIndex}
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onAppointmentClick) onAppointmentClick(apt);
                          }}
                          className="text-xs p-1 bg-blue-100 text-blue-800 rounded truncate"
                        >
                          {apt.time} {apt.patient_name}
                        </div>
                      ))}
                      {day.appointments.length > 2 && (
                        <div className="text-xs text-gray-500">
                          +{day.appointments.length - 2} lagi
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  function renderDayView() {
    if (!selectedDate) {
      return (
        <div className="text-center py-12">
          <CalendarIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Pilih tanggal untuk melihat jadwal</p>
          <Button
            variant="primary"
            onClick={goToToday}
            className="mt-4"
          >
            Hari Ini
          </Button>
        </div>
      );
    }

    const dayAppointments = calendarDays.find(d =>
      isSameDay(d.date, selectedDate)
    )?.appointments || [];

    // Time slots for the day
    const timeSlots = [];
    for (let hour = 8; hour <= 20; hour++) {
      timeSlots.push(`${hour.toString().padStart(2, '0')}:00`);
      timeSlots.push(`${hour.toString().padStart(2, '0')}:30`);
    }

    return (
      <div className="space-y-4">
        {/* Selected Date Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              {selectedDate.toLocaleDateString('id-ID', {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
                year: 'numeric',
              })}
            </h3>
            <p className="text-gray-600">{dayAppointments.length} janji temu</p>
          </div>
        </div>

        {/* Time Slot Grid */}
        <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-200">
          {timeSlots.map(time => {
            const slotAppointments = dayAppointments.filter(apt => apt.time.startsWith(time.split(':')[0]));

            return (
              <div
                key={time}
                className="flex hover:bg-gray-50 transition-colors"
              >
                {/* Time */}
                <div className="w-24 py-4 px-4 text-sm font-medium text-gray-700 border-r border-gray-200 flex-shrink-0">
                  {time}
                </div>

                {/* Appointments */}
                <div className="flex-1 py-4 px-4">
                  {slotAppointments.length === 0 ? (
                    <div className="text-sm text-gray-400 italic">
                      Tidak ada janji temu
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {slotAppointments.map(apt => (
                        <div
                          key={apt.id}
                          onClick={() => onAppointmentClick?.(apt)}
                          className="bg-blue-50 border border-blue-200 rounded-lg p-3 cursor-pointer hover:bg-blue-100 transition-colors"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="font-semibold text-gray-900">
                                {apt.patient_name}
                              </div>
                              <div className="text-sm text-gray-600 mt-1">
                                {apt.department} - {apt.doctor_name}
                              </div>
                              {apt.queue_number && (
                                <Badge variant="primary" className="mt-2">
                                  No. Antrian: {apt.queue_number}
                                </Badge>
                              )}
                            </div>
                            <Badge variant={getStatusVariant(apt.status)}>
                              {getStatusLabel(apt.status)}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* Month Navigation */}
          <div className="flex items-center gap-4">
            <Button
              variant="icon"
              size="sm"
              onClick={previousMonth}
              icon={<ChevronLeft className="w-5 h-5" />}
            />

            <h2 className="text-xl font-bold text-gray-900 min-w-48 text-center">
              {currentDate.toLocaleDateString('id-ID', {
                month: 'long',
                year: 'numeric',
              })}
            </h2>

            <Button
              variant="icon"
              size="sm"
              onClick={nextMonth}
              icon={<ChevronRight className="w-5 h-5" />}
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={goToToday}
            >
              Hari Ini
            </Button>

            <Button
              variant={viewMode === 'month' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => {/* Toggle view mode */}}
            >
              Bulan
            </Button>

            <Button
              variant={viewMode === 'day' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => {/* Toggle view mode */}}
            >
              Hari
            </Button>

            <Button
              variant="icon"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              icon={<Filter className="w-5 h-5" />}
            />
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-64">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Departemen
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={departmentFilter || 'all'}
                  onChange={(e) => {/* Handle filter change */}}
                >
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex-1 min-w-64">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dokter
                </label>
                <input
                  type="text"
                  placeholder="Cari nama dokter..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        )}
      </CardHeader>

      <CardBody>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : viewMode === 'month' ? (
          renderMonthView()
        ) : (
          renderDayView()
        )}
      </CardBody>
    </Card>
  );
}
