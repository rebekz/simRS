"use client";

import { useEffect, useState } from "react";

interface DashboardStats {
  totalPatients: number;
  activeAppointments: number;
  pendingQueue: number;
  todayAdmissions: number;
}

export default function StaffDashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalPatients: 0,
    activeAppointments: 0,
    pendingQueue: 0,
    todayAdmissions: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const token = localStorage.getItem("staff_access_token");

      // Fetch stats from multiple endpoints
      const [patientsRes, appointmentsRes, queueRes, admissionsRes] = await Promise.all([
        fetch("/api/v1/patients?limit=1", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/appointments?status=scheduled&limit=1", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/queue/active", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/admissions/today", {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      // Parse responses (simplified for demo)
      setStats({
        totalPatients: 1234, // Would come from API
        activeAppointments: 45,
        pendingQueue: 12,
        todayAdmissions: 8,
      });
    } catch (error) {
      console.error("Failed to fetch dashboard stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    { name: "Register Patient", href: "/app/patients/register", icon: "➕", color: "bg-blue-500" },
    { name: "New Appointment", href: "/app/appointments/new", icon: "📅", color: "bg-green-500" },
    { name: "View Queue", href: "/app/queue", icon: "🔢", color: "bg-yellow-500" },
    { name: "Create Prescription", href: "/app/prescriptions/new", icon: "💊", color: "bg-purple-500" },
  ];

  const recentActivities = [
    { id: 1, action: "New patient registered", time: "5 minutes ago", type: "patient" },
    { id: 2, action: "Appointment confirmed", time: "15 minutes ago", type: "appointment" },
    { id: 3, action: "Lab result ready", time: "30 minutes ago", type: "lab" },
    { id: 4, action: "Prescription dispensed", time: "1 hour ago", type: "pharmacy" },
    { id: 5, action: "Patient admitted", time: "2 hours ago", type: "admission" },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Stats Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
              <div className="h-8 bg-gray-200 rounded mb-2"></div>
              <div className="h-12 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Patients */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Patients</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalPatients.toLocaleString()}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">👥</span>
              </div>
            </div>
            <p className="text-xs text-green-600 mt-3">↑ 12% from last month</p>
          </div>

          {/* Active Appointments */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Today's Appointments</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.activeAppointments}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📅</span>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-3">{stats.pendingQueue} pending confirmation</p>
          </div>

          {/* Queue */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Queue</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.pendingQueue}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">🔢</span>
              </div>
            </div>
            <p className="text-xs text-yellow-600 mt-3">Avg wait: 15 min</p>
          </div>

          {/* Today's Admissions */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Today's Admissions</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.todayAdmissions}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">🏥</span>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-3">3 beds available</p>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <a
              key={action.name}
              href={action.href}
              className="flex flex-col items-center justify-center p-6 border border-gray-200 rounded-xl hover:shadow-md hover:border-gray-300 transition-all"
            >
              <span className="text-3xl mb-2">{action.icon}</span>
              <span className="text-sm font-medium text-gray-900">{action.name}</span>
            </a>
          ))}
        </div>
      </div>

      {/* Recent Activity & Upcoming */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0
                  ${activity.type === "patient" ? "bg-blue-100" : ""}
                  ${activity.type === "appointment" ? "bg-green-100" : ""}
                  ${activity.type === "lab" ? "bg-purple-100" : ""}
                  ${activity.type === "pharmacy" ? "bg-yellow-100" : ""}
                  ${activity.type === "admission" ? "bg-red-100" : ""}
                `}>
                  {activity.type === "patient" && "👤"}
                  {activity.type === "appointment" && "📅"}
                  {activity.type === "lab" && "🔬"}
                  {activity.type === "pharmacy" && "💊"}
                  {activity.type === "admission" && "🏥"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Upcoming Appointments */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Appointments</h2>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-blue-600">P{i}</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Patient {i}</p>
                    <p className="text-xs text-gray-500">Dr. Smith • General</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{9 + i}:00</p>
                  <p className="text-xs text-gray-500">{i * 15} min</p>
                </div>
              </div>
            ))}
          </div>
          <a href="/app/appointments" className="mt-4 block text-center text-sm text-blue-600 hover:underline">
            View all appointments →
          </a>
        </div>
      </div>
    </div>
  );
}
