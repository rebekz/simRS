"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface Department {
  id: number;
  name: string;
}

interface Doctor {
  id: number;
  full_name: string;
  department_id: number;
}

interface AvailableSlot {
  slot_id: number | null;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

function BookAppointmentPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedDept = searchParams.get("department");

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);

  // Form state
  const [departments, setDepartments] = useState<Department[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [availableSlots, setAvailableSlots] = useState<AvailableSlot[]>([]);

  const [formData, setFormData] = useState({
    department_id: preselectedDept ? parseInt(preselectedDept) : 0,
    doctor_id: 0,
    appointment_date: "",
    appointment_time: "",
    appointment_type: "consultation",
    reason_for_visit: "",
    symptoms: "",
  });

  useEffect(() => {
    checkAuth();
    fetchDepartments();
  }, []);

  useEffect(() => {
    if (formData.department_id > 0) {
      fetchDoctors(formData.department_id);
    }
  }, [formData.department_id]);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await fetch("/api/v1/hospital/departments");
      if (response.ok) {
        const data = await response.json();
        setDepartments(data.departments || []);
      }
    } catch (err) {
      console.error("Failed to fetch departments");
    }
  };

  const fetchDoctors = async (departmentId: number) => {
    try {
      const response = await fetch(`/api/v1/hospital/departments/${departmentId}/doctors`);
      if (response.ok) {
        const data = await response.json();
        setDoctors(data.doctors || []);
      }
    } catch (err) {
      console.error("Failed to fetch doctors");
    }
  };

  const checkAvailability = async () => {
    if (!formData.department_id || !formData.appointment_date) return;

    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    setLoading(true);
    try {
      const dateStr = new Date(formData.appointment_date).toISOString().split("T")[0];
      const response = await fetch(
        `/api/v1/portal/appointments/available-slots?department_id=${formData.department_id}&date_str=${dateStr}${formData.doctor_id > 0 ? `&doctor_id=${formData.doctor_id}` : ""}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAvailableSlots(data.slots || []);
      }
    } catch (err) {
      console.error("Failed to fetch available slots");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
      return;
    }

    try {
      const response = await fetch("/api/v1/portal/appointments/book", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Booking failed");
      }

      const data = await response.json();
      router.push(`/portal/appointments/${data.id}?success=true`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Booking failed");
    } finally {
      setSubmitting(false);
    }
  };

  const updateForm = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <a href="/portal/appointments" className="text-indigo-600 hover:underline text-sm">
            ← Back to My Appointments
          </a>
          <h1 className="text-2xl font-bold text-gray-900 mt-2">Book an Appointment</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
          {/* Department Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Department <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.department_id}
              onChange={(e) => updateForm("department_id", parseInt(e.target.value))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value={0}>Select a department</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>

          {/* Doctor Selection (Optional) */}
          {doctors.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Doctor (Optional)
              </label>
              <select
                value={formData.doctor_id}
                onChange={(e) => updateForm("doctor_id", parseInt(e.target.value))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value={0}>Any available doctor</option>
                {doctors.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    Dr. {doc.full_name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Appointment Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Appointment Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={formData.appointment_date}
              onChange={(e) => updateForm("appointment_date", e.target.value)}
              min={new Date().toISOString().split("T")[0]}
              onBlur={checkAvailability}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          {/* Available Slots */}
          {formData.appointment_date && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Available Time Slots <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-3 gap-3">
                {availableSlots.length === 0 ? (
                  <p className="text-sm text-gray-500 col-span-3">
                    {loading ? "Checking availability..." : "No slots available for this date"}
                  </p>
                ) : (
                  availableSlots.map((slot) => (
                    <button
                      key={slot.slot_id}
                      type="button"
                      disabled={!slot.is_available}
                      onClick={() => updateForm("appointment_time", slot.start_time)}
                      className={`px-4 py-3 border rounded-lg text-center transition-colors ${
                        formData.appointment_time === slot.start_time
                          ? "bg-indigo-600 text-white border-indigo-600"
                          : slot.is_available
                          ? "bg-white border-gray-300 hover:border-indigo-300"
                          : "bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed"
                      }`}
                    >
                      {slot.start_time}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Appointment Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Appointment Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.appointment_type}
              onChange={(e) => updateForm("appointment_type", e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="consultation">Consultation</option>
              <option value="follow_up">Follow-up</option>
              <option value="procedure">Procedure</option>
              <option value="vaccination">Vaccination</option>
            </select>
          </div>

          {/* Reason for Visit */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Visit <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.reason_for_visit}
              onChange={(e) => updateForm("reason_for_visit", e.target.value)}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="Briefly describe why you need this appointment"
              required
            />
          </div>

          {/* Symptoms (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Symptoms (Optional)
            </label>
            <textarea
              value={formData.symptoms}
              onChange={(e) => updateForm("symptoms", e.target.value)}
              rows={2}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="Describe any symptoms you're experiencing"
            />
          </div>

          {/* Submit */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={submitting || !formData.appointment_time}
              className="flex-1 py-3 px-6 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? "Booking..." : "Book Appointment"}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}

export default function BookAppointmentPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    }>
      <BookAppointmentPageContent />
    </Suspense>
  );
}
