"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Appointment {
  id: number;
  appointment_number: string;
  appointment_date: string;
  appointment_time: string;
  department_name: string;
  doctor_name: string | null;
  appointment_type: string;
  status: string;
  queue_number: string | null;
  reason_for_visit: string | null;
}

interface MyAppointmentsResponse {
  upcoming: Appointment[];
  past: Appointment[];
  cancelled: Appointment[];
}

export default function MyAppointmentsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [appointments, setAppointments] = useState<MyAppointmentsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"upcoming" | "past" | "cancelled">("upcoming");

  useEffect(() => {
    checkAuth();
    fetchAppointments();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchAppointments = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/appointments/my-appointments?include_past=true&include_cancelled=true", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        throw new Error("Failed to fetch appointments");
      }

      const data = await response.json();
      setAppointments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load appointments");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (appointmentId: number) => {
    if (!confirm("Are you sure you want to cancel this appointment?")) return;

    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/appointments/${appointmentId}/cancel`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ reason: "Patient cancelled" }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to cancel appointment");
      }

      alert("Appointment cancelled successfully");
      fetchAppointments();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to cancel appointment");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scheduled": return "bg-blue-100 text-blue-700";
      case "confirmed": return "bg-green-100 text-green-700";
      case "completed": return "bg-gray-100 text-gray-700";
      case "cancelled": return "bg-red-100 text-red-700";
      case "checked_in": return "bg-yellow-100 text-yellow-700";
      case "in_progress": return "bg-purple-100 text-purple-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading appointments...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <a href="/portal/dashboard" className="text-indigo-600 hover:underline text-sm">
                ← Back to Dashboard
              </a>
              <h1 className="text-2xl font-bold text-gray-900 mt-1">My Appointments</h1>
            </div>
            <a
              href="/portal/appointments/book"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              + Book New Appointment
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {appointments && (
          <>
            <div className="bg-white rounded-lg shadow-md mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab("upcoming")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "upcoming"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Upcoming ({appointments.upcoming.length})
                  </button>
                  <button
                    onClick={() => setActiveTab("past")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "past"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Past ({appointments.past.length})
                  </button>
                  <button
                    onClick={() => setActiveTab("cancelled")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "cancelled"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Cancelled ({appointments.cancelled.length})
                  </button>
                </nav>
              </div>
            </div>

            <div className="space-y-4">
              {activeTab === "upcoming" && (
                <>
                  {appointments.upcoming.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-md p-8 text-center">
                      <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p className="text-gray-500 mb-4">No upcoming appointments</p>
                      <a
                        href="/portal/appointments/book"
                        className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                      >
                        Book an Appointment
                      </a>
                    </div>
                  ) : (
                    appointments.upcoming.map((apt) => (
                      <AppointmentCard key={apt.id} appointment={apt} onCancel={handleCancel} />
                    ))
                  )}
                </>
              )}

              {activeTab === "past" && (
                <>
                  {appointments.past.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                      No past appointments
                    </div>
                  ) : (
                    appointments.past.map((apt) => (
                      <AppointmentCard key={apt.id} appointment={apt} onCancel={undefined} />
                    ))
                  )}
                </>
              )}

              {activeTab === "cancelled" && (
                <>
                  {appointments.cancelled.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                      No cancelled appointments
                    </div>
                  ) : (
                    appointments.cancelled.map((apt) => (
                      <AppointmentCard key={apt.id} appointment={apt} onCancel={undefined} />
                    ))
                  )}
                </>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    scheduled: 'bg-blue-100 text-blue-800',
    confirmed: 'bg-green-100 text-green-800',
    completed: 'bg-gray-100 text-gray-800',
    cancelled: 'bg-red-100 text-red-800',
    no_show: 'bg-yellow-100 text-yellow-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });
}

function AppointmentCard({
  appointment,
  onCancel,
}: {
  appointment: Appointment;
  onCancel?: (id: number) => void;
}) {
  const timeStr = appointment.appointment_time.slice(0, 5);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="text-lg font-semibold text-gray-900">{appointment.department_name}</h3>
            <span className={`px-2 py-1 text-xs font-medium rounded capitalize ${getStatusColor(appointment.status)}`}>
              {appointment.status}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Date</p>
              <p className="font-medium">{formatDate(appointment.appointment_date)}</p>
            </div>
            <div>
              <p className="text-gray-500">Time</p>
              <p className="font-medium">{timeStr}</p>
            </div>
            {appointment.doctor_name && (
              <div>
                <p className="text-gray-500">Doctor</p>
                <p className="font-medium">{appointment.doctor_name}</p>
              </div>
            )}
            {appointment.queue_number && (
              <div>
                <p className="text-gray-500">Queue Number</p>
                <p className="font-medium">{appointment.queue_number}</p>
              </div>
          )}
        </div>

        {appointment.reason_for_visit && (
          <div className="mt-4">
            <p className="text-sm text-gray-500">Reason</p>
            <p className="text-sm text-gray-700">{appointment.reason_for_visit}</p>
          </div>
        )}
      </div>

      {onCancel && appointment.status === "scheduled" && (
        <div className="mt-4 pt-4 border-t border-gray-100 flex gap-3">
          <a
            href={`/portal/appointments/${appointment.id}`}
            className="text-sm text-indigo-600 hover:underline"
          >
            View Details
          </a>
          <button
            onClick={() => onCancel(appointment.id)}
            className="text-sm text-red-600 hover:underline"
          >
            Cancel Appointment
          </button>
        </div>
      )}
      </div>
    </div>
  );
}
