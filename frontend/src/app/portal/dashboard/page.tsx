"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface HealthSummary {
  patient_name: string;
  medical_record_number: string;
  age: number;
  gender: string;
  blood_type: string | null;
  allergies_count: number;
  has_severe_allergies: boolean;
  chronic_conditions_count: number;
  current_medications_count: number;
  total_visits: number;
  last_visit_date: string | null;
  last_visit_department: string | null;
  record_completeness: string;
  last_updated: string;
}

export default function PatientPortalDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<HealthSummary | null>(null);

  useEffect(() => {
    checkAuth();
    fetchSummary();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchSummary = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/health-record/summary", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        throw new Error("Failed to fetch health summary");
      }

      const data = await response.json();
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("portal_access_token");
    localStorage.removeItem("portal_refresh_token");
    localStorage.removeItem("portal_user");
    router.push("/portal/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your health dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && !summary) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md w-full">
          <div className="text-center">
            <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Dashboard</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchSummary}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">SIMRS Patient Portal</h1>
            {summary && (
              <p className="text-sm text-gray-600">Welcome, {summary.patient_name}</p>
            )}
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Sign Out
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">{error}</p>
          </div>
        )}

        {summary && (
          <>
            {/* Welcome Card */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 text-white mb-8">
              <h2 className="text-2xl font-bold mb-2">Hello, {summary.patient_name}!</h2>
              <p className="text-indigo-100">MRN: {summary.medical_record_number} • Age: {summary.age} • {summary.gender === "male" ? "Male" : "Female"}</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                label="Allergies"
                value={summary.allergies_count}
                color={summary.has_severe_allergies ? "red" : "green"}
                href="/portal/health-record?section=allergies"
              />
              <StatCard
                label="Chronic Conditions"
                value={summary.chronic_conditions_count}
                color="blue"
                href="/portal/health-record?section=diagnoses"
              />
              <StatCard
                label="Current Medications"
                value={summary.current_medications_count}
                color="purple"
                href="/portal/health-record?section=medications"
              />
              <StatCard
                label="Total Visits"
                value={summary.total_visits}
                color="indigo"
                href="/portal/health-record?section=encounters"
              />
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-md p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <QuickActionButton
                  icon={
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  }
                  label="View Health Records"
                  description="See your complete medical history"
                  href="/portal/health-record"
                />
                <QuickActionButton
                  icon={
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  }
                  label="Appointments"
                  description="Schedule or manage appointments"
                  href="#"
                  disabled
                />
                <QuickActionButton
                  icon={
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  }
                  label="Prescriptions"
                  description="Request refills or view history"
                  href="#"
                  disabled
                />
              </div>
            </div>

            {/* Last Visit */}
            {summary.last_visit_date && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Last Visit</h3>
                <p className="text-gray-600">
                  {new Date(summary.last_visit_date).toLocaleDateString("id-ID", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                  {summary.last_visit_department && ` • ${summary.last_visit_department}`}
                </p>
              </div>
            )}

            {/* Record Completeness */}
            <div className="mt-6 text-center text-sm text-gray-500">
              Record completeness: <span className="font-semibold">{summary.record_completeness}</span> •
              Last updated: {new Date(summary.last_updated).toLocaleDateString("id-ID")}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function StatCard({ label, value, color, href }: { label: string; value: number; color: string; href: string }) {
  const colorClasses = {
    red: "bg-red-50 text-red-700 border-red-200",
    green: "bg-green-50 text-green-700 border-green-200",
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    purple: "bg-purple-50 text-purple-700 border-purple-200",
    indigo: "bg-indigo-50 text-indigo-700 border-indigo-200",
  };

  return (
    <a href={href} className="block">
      <div className={`bg-white rounded-xl shadow-md p-6 border-2 ${colorClasses[color as keyof typeof colorClasses]} hover:shadow-lg transition-shadow`}>
        <p className="text-sm font-medium mb-2">{label}</p>
        <p className="text-3xl font-bold">{value}</p>
      </div>
    </a>
  );
}

function QuickActionButton({
  icon,
  label,
  description,
  href,
  disabled = false,
}: {
  icon: React.ReactNode;
  label: string;
  description: string;
  href: string;
  disabled?: boolean;
}) {
  return (
    <a
      href={disabled ? undefined : href}
      className={`p-4 border rounded-lg ${
        disabled
          ? "bg-gray-50 border-gray-200 cursor-not-allowed opacity-60"
          : "bg-white border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all"
      }`}
    >
      <div className="flex items-start space-x-3">
        <div className={`flex-shrink-0 ${disabled ? "text-gray-400" : "text-indigo-600"}`}>{icon}</div>
        <div>
          <h4 className={`font-semibold ${disabled ? "text-gray-500" : "text-gray-900"}`}>{label}</h4>
          <p className={`text-sm ${disabled ? "text-gray-400" : "text-gray-600"}`}>{description}</p>
          {disabled && <p className="text-xs text-gray-400 mt-1">Coming soon</p>}
        </div>
      </div>
    </a>
  );
}
