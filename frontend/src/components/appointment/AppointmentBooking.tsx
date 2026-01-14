"use client";

import React, { useState, useEffect } from 'react';
import { Calendar, Clock, User, Phone, MessageSquare, Check, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card';
import { FormInput } from '@/components/ui/form/FormInput';
import { FormSelect } from '@/components/ui/form/FormSelect';
import { FormTextarea } from '@/components/ui/form/FormTextarea';
import { cn } from '@/lib/utils';

// Types
interface Department {
  id: string;
  name: string;
  description?: string;
}

interface Doctor {
  id: string;
  name: string;
  specialty: string;
  avatar?: string;
}

interface TimeSlot {
  id: string;
  time: string;
  available: boolean;
  bookings_count: number;
  max_bookings: number;
}

interface AppointmentBookingData {
  department_id: string;
  doctor_id: string;
  appointment_date: string;
  time_slot_id: string;
  patient_name: string;
  patient_phone: string;
  patient_nik?: string;
  reason: string;
  send_whatsapp: boolean;
  send_sms: boolean;
}

interface AppointmentBookingProps {
  onSuccess?: (appointment: any) => void;
  onCancel?: () => void;
}

export default function AppointmentBooking({ onSuccess, onCancel }: AppointmentBookingProps) {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Data states
  const [departments, setDepartments] = useState<Department[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');

  // Form state
  const [formData, setFormData] = useState<AppointmentBookingData>({
    department_id: '',
    doctor_id: '',
    appointment_date: '',
    time_slot_id: '',
    patient_name: '',
    patient_phone: '',
    patient_nik: '',
    reason: '',
    send_whatsapp: true,
    send_sms: false,
  });

  // Form errors
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch departments
  useEffect(() => {
    fetchDepartments();
  }, []);

  // Fetch doctors when department changes
  useEffect(() => {
    if (formData.department_id) {
      fetchDoctors(formData.department_id);
    } else {
      setDoctors([]);
      setFormData(prev => ({ ...prev, doctor_id: '' }));
    }
  }, [formData.department_id]);

  // Fetch available slots when date and doctor are selected
  useEffect(() => {
    if (formData.appointment_date && formData.doctor_id) {
      fetchAvailableSlots(formData.doctor_id, formData.appointment_date);
    } else {
      setAvailableSlots([]);
    }
  }, [formData.appointment_date, formData.doctor_id]);

  async function fetchDepartments() {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/appointments/departments');
      const data = await response.json();
      setDepartments(data);
    } catch (error) {
      console.error('Failed to fetch departments:', error);
    } finally {
      setLoading(false);
    }
  }

  async function fetchDoctors(departmentId: string) {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/appointments/departments/${departmentId}/doctors`);
      const data = await response.json();
      setDoctors(data);
    } catch (error) {
      console.error('Failed to fetch doctors:', error);
    } finally {
      setLoading(false);
    }
  }

  async function fetchAvailableSlots(doctorId: string, date: string) {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/v1/appointments/doctors/${doctorId}/slots?date=${date}`
      );
      const data = await response.json();
      setAvailableSlots(data.slots || []);
    } catch (error) {
      console.error('Failed to fetch available slots:', error);
    } finally {
      setLoading(false);
    }
  }

  function handleInputChange(field: keyof AppointmentBookingData, value: any) {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  }

  function validateStep1(): boolean {
    const newErrors: Record<string, string> = {};

    if (!formData.department_id) {
      newErrors.department_id = 'Silakan pilih poli/departemen';
    }
    if (!formData.doctor_id) {
      newErrors.doctor_id = 'Silakan pilih dokter';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  function validateStep2(): boolean {
    const newErrors: Record<string, string> = {};

    if (!formData.appointment_date) {
      newErrors.appointment_date = 'Silakan pilih tanggal kunjungan';
    }
    if (!formData.time_slot_id) {
      newErrors.time_slot_id = 'Silakan pilih jam praktik';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  function validateStep3(): boolean {
    const newErrors: Record<string, string> = {};

    if (!formData.patient_name.trim()) {
      newErrors.patient_name = 'Nama pasien wajib diisi';
    }
    if (!formData.patient_phone.trim()) {
      newErrors.patient_phone = 'Nomor telepon wajib diisi';
    } else if (!/^08\d{8,11}$/.test(formData.patient_phone.replace(/[\s-]/g, ''))) {
      newErrors.patient_phone = 'Format nomor telepon tidak valid';
    }
    if (!formData.reason.trim()) {
      newErrors.reason = 'Alasan kunjungan wajib diisi';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit() {
    if (!validateStep3()) return;

    setSubmitting(true);
    try {
      const response = await fetch('/api/v1/appointments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Gagal membuat janji temu');
      }

      const appointment = await response.json();
      setStep(4); // Success step

      if (onSuccess) {
        onSuccess(appointment);
      }
    } catch (error: any) {
      console.error('Failed to create appointment:', error);
      setErrors({ submit: error.message });
    } finally {
      setSubmitting(false);
    }
  }

  function renderStep1() {
    const departmentOptions = departments.map(dept => ({
      value: dept.id,
      label: dept.name,
    }));

    const doctorOptions = doctors.map(doc => ({
      value: doc.id,
      label: `${doc.name} - ${doc.specialty}`,
    }));

    return (
      <div className="space-y-6">
        {/* Department Selection */}
        <FormSelect
          label="Poli / Departemen"
          placeholder="Pilih poli atau departemen"
          options={departmentOptions}
          value={formData.department_id}
          onChange={(e) => handleInputChange('department_id', e.target.value)}
          error={errors.department_id}
          required
          disabled={loading}
        />

        {/* Doctor Selection */}
        <FormSelect
          label="Dokter"
          placeholder="Pilih dokter"
          options={doctorOptions}
          value={formData.doctor_id}
          onChange={(e) => handleInputChange('doctor_id', e.target.value)}
          error={errors.doctor_id}
          required
          disabled={loading || !formData.department_id}
        />

        {/* Doctor Info */}
        {formData.doctor_id && (() => {
          const doctor = doctors.find(d => d.id === formData.doctor_id);
          return doctor && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  {doctor.name.charAt(0)}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{doctor.name}</div>
                  <div className="text-sm text-gray-600">{doctor.specialty}</div>
                </div>
              </div>
            </div>
          );
        })()}
      </div>
    );
  }

  function renderStep2() {
    // Get min and max dates (today to 30 days ahead)
    const today = new Date();
    const maxDate = new Date();
    maxDate.setDate(today.getDate() + 30);

    const minDateStr = today.toISOString().split('T')[0];
    const maxDateStr = maxDate.toISOString().split('T')[0];

    // Group slots by time period
    const morningSlots = availableSlots.filter(s => {
      const hour = parseInt(s.time.split(':')[0]);
      return hour < 12;
    });
    const afternoonSlots = availableSlots.filter(s => {
      const hour = parseInt(s.time.split(':')[0]);
      return hour >= 12 && hour < 17;
    });
    const eveningSlots = availableSlots.filter(s => {
      const hour = parseInt(s.time.split(':')[0]);
      return hour >= 17;
    });

    return (
      <div className="space-y-6">
        {/* Date Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tanggal Kunjungan <span className="text-red-500">*</span>
          </label>
          <FormInput
            type="date"
            min={minDateStr}
            max={maxDateStr}
            value={formData.appointment_date}
            onChange={(e) => handleInputChange('appointment_date', e.target.value)}
            error={errors.appointment_date}
            required
          />
        </div>

        {/* Time Slot Selection */}
        {formData.appointment_date && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Jam Praktik <span className="text-red-500">*</span>
            </label>

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">Memuat jadwal...</span>
              </div>
            ) : availableSlots.length === 0 ? (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                <p className="text-gray-600">Tidak ada jadwal tersedia pada tanggal ini</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Morning */}
                {morningSlots.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-2">Pagi</div>
                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                      {morningSlots.map(slot => (
                        <button
                          key={slot.id}
                          type="button"
                          onClick={() => handleInputChange('time_slot_id', slot.id)}
                          disabled={!slot.available}
                          className={cn(
                            'px-3 py-2 rounded-lg border-2 text-sm font-medium transition-all',
                            formData.time_slot_id === slot.id
                              ? 'border-blue-600 bg-blue-600 text-white'
                              : slot.available
                              ? 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50'
                              : 'border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed'
                          )}
                        >
                          {slot.time}
                          {!slot.available && (
                            <div className="text-xs">Penuh</div>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Afternoon */}
                {afternoonSlots.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-2">Siang</div>
                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                      {afternoonSlots.map(slot => (
                        <button
                          key={slot.id}
                          type="button"
                          onClick={() => handleInputChange('time_slot_id', slot.id)}
                          disabled={!slot.available}
                          className={cn(
                            'px-3 py-2 rounded-lg border-2 text-sm font-medium transition-all',
                            formData.time_slot_id === slot.id
                              ? 'border-blue-600 bg-blue-600 text-white'
                              : slot.available
                              ? 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50'
                              : 'border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed'
                          )}
                        >
                          {slot.time}
                          {!slot.available && (
                            <div className="text-xs">Penuh</div>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Evening */}
                {eveningSlots.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-2">Sore</div>
                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                      {eveningSlots.map(slot => (
                        <button
                          key={slot.id}
                          type="button"
                          onClick={() => handleInputChange('time_slot_id', slot.id)}
                          disabled={!slot.available}
                          className={cn(
                            'px-3 py-2 rounded-lg border-2 text-sm font-medium transition-all',
                            formData.time_slot_id === slot.id
                              ? 'border-blue-600 bg-blue-600 text-white'
                              : slot.available
                              ? 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50'
                              : 'border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed'
                          )}
                        >
                          {slot.time}
                          {!slot.available && (
                            <div className="text-xs">Penuh</div>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {errors.time_slot_id && (
                  <p className="text-sm text-red-600 mt-1">{errors.time_slot_id}</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  function renderStep3() {
    return (
      <div className="space-y-6">
        {/* Patient Information */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-blue-600" />
            Informasi Pasien
          </h3>

          <div className="space-y-4">
            <FormInput
              label="Nama Lengkap"
              placeholder="Masukkan nama lengkap pasien"
              value={formData.patient_name}
              onChange={(e) => handleInputChange('patient_name', e.target.value)}
              error={errors.patient_name}
              required
            />

            <FormInput
              label="Nomor Telepon / WhatsApp"
              placeholder="Contoh: 081234567890"
              value={formData.patient_phone}
              onChange={(e) => handleInputChange('patient_phone', e.target.value)}
              error={errors.patient_phone}
              required
            />

            <FormInput
              label="NIK (Opsional)"
              placeholder="Nomor Induk Kependudukan"
              value={formData.patient_nik || ''}
              onChange={(e) => handleInputChange('patient_nik', e.target.value)}
              maxLength={16}
            />
          </div>
        </div>

        {/* Reason for Visit */}
        <div>
          <FormTextarea
            label="Alasan Kunjungan"
            placeholder="Jelaskan keluhan atau alasan kunjungan..."
            value={formData.reason}
            onChange={(e) => handleInputChange('reason', e.target.value)}
            error={errors.reason}
            required
            rows={3}
          />
        </div>

        {/* Notification Preferences */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-600" />
            Notifikasi
          </h3>

          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.send_whatsapp}
                onChange={(e) => handleInputChange('send_whatsapp', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Kirim konfirmasi via WhatsApp
              </span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.send_sms}
                onChange={(e) => handleInputChange('send_sms', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Kirim konfirmasi via SMS
              </span>
            </label>
          </div>
        </div>
      </div>
    );
  }

  function renderStep4() {
    return (
      <div className="text-center py-8">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Check className="w-8 h-8 text-green-600" />
        </div>

        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          Janji Temu Berhasil Dibuat!
        </h3>

        <p className="text-gray-600 mb-6">
          Detail janji temu telah dikirim ke nomor telepon Anda
        </p>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 max-w-md mx-auto text-left">
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-gray-500">Nomor Antrian:</span>
              <div className="font-bold text-lg text-blue-600">A-001</div>
            </div>

            <div>
              <span className="text-gray-500">Tanggal:</span>
              <div className="font-semibold">
                {new Date(formData.appointment_date).toLocaleDateString('id-ID', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </div>
            </div>

            <div>
              <span className="text-gray-500">Jam:</span>
              <div className="font-semibold">
                {availableSlots.find(s => s.id === formData.time_slot_id)?.time}
              </div>
            </div>

            <div>
              <span className="text-gray-500">Dokter:</span>
              <div className="font-semibold">
                {doctors.find(d => d.id === formData.doctor_id)?.name}
              </div>
            </div>

            <div>
              <span className="text-gray-500">Pasien:</span>
              <div className="font-semibold">{formData.patient_name}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  function renderStepIndicator() {
    const steps = [
      { number: 1, label: 'Pilih Dokter' },
      { number: 2, label: 'Pilih Jadwal' },
      { number: 3, label: 'Informasi Pasien' },
    ];

    return (
      <div className="flex items-center justify-center mb-8">
        {steps.map((s, index) => (
          <React.Fragment key={s.number}>
            <div className="flex items-center">
              <div
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all',
                  step >= s.number
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                )}
              >
                {step > s.number ? <Check className="w-5 h-5" /> : s.number}
              </div>
              <span
                className={cn(
                  'ml-2 text-sm font-medium hidden sm:block',
                  step >= s.number ? 'text-blue-600' : 'text-gray-500'
                )}
              >
                {s.label}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={cn(
                  'w-12 sm:w-24 h-1 mx-2',
                  step > s.number ? 'bg-blue-600' : 'bg-gray-200'
                )}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    );
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader title="Buat Janji Temu" />

      <CardBody>
        {step < 4 && renderStepIndicator()}

        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}
        {step === 4 && renderStep4()}

        {errors.submit && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}
      </CardBody>

      {step < 4 && (
        <CardFooter className="flex justify-between">
          <div>
            {step > 1 && (
              <Button
                variant="secondary"
                onClick={() => setStep((step - 1) as 1 | 2 | 3)}
                disabled={submitting}
              >
                Kembali
              </Button>
            )}
            {onCancel && step === 1 && (
              <Button
                variant="ghost"
                onClick={onCancel}
                disabled={submitting}
              >
                Batal
              </Button>
            )}
          </div>

          <div>
            {step < 3 ? (
              <Button
                onClick={() => {
                  if (step === 1 && validateStep1()) setStep(2);
                  if (step === 2 && validateStep2()) setStep(3);
                }}
                disabled={loading}
                loading={loading}
              >
                Lanjut
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={submitting}
                loading={submitting}
              >
                {submitting ? 'Memproses...' : 'Buat Janji Temu'}
              </Button>
            )}
          </div>
        </CardFooter>
      )}
    </Card>
  );
}
