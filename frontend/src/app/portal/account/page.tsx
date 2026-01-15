"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface PatientProfile {
  id: number;
  medical_record_number: string;
  full_name: string;
  phone: string | null;
  email: string | null;
  address: string | null;
  city: string | null;
  province: string | null;
  postal_code: string | null;
  date_of_birth: string;
  gender: string;
}

interface SecurityInfo {
  email_verified: boolean;
  phone_verified: boolean;
  last_login: string | null;
  last_password_change: string | null;
  active_sessions: number;
}

interface NotificationPreferences {
  email_notifications: boolean;
  sms_notifications: boolean;
  appointment_reminders: boolean;
  bill_reminders: boolean;
  lab_results_ready: boolean;
  prescription_ready: boolean;
  marketing_emails: boolean;
  digest_frequency: "immediate" | "daily" | "weekly";
}

interface AppearancePreferences {
  language: "indonesian" | "english";
  theme: "light" | "dark" | "auto";
  font_size: "small" | "medium" | "large";
}

interface PrivacySettings {
  share_data_with_bpjs: boolean;
  allow_family_access: boolean;
  data_retention_days: number;
}

type TabType = "profile" | "security" | "notifications" | "appearance" | "privacy";

export default function AccountSettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("profile");
  const [profile, setProfile] = useState<PatientProfile | null>(null);
  const [securityInfo, setSecurityInfo] = useState<SecurityInfo | null>(null);
  const [notifications, setNotifications] = useState<NotificationPreferences | null>(null);
  const [appearance, setAppearance] = useState<AppearancePreferences | null>(null);
  const [privacy, setPrivacy] = useState<PrivacySettings | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    checkAuth();
    fetchAccountData();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchAccountData = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      // Fetch profile data
      const profileRes = await fetch("/api/v1/portal/account/profile", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (profileRes.status === 401) {
        router.push("/portal/login");
        return;
      }

      if (profileRes.ok) {
        const profileData = await profileRes.json();
        setProfile(profileData);
      }

      // Fetch security info
      const securityRes = await fetch("/api/v1/portal/account/security", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (securityRes.ok) {
        const securityData = await securityRes.json();
        setSecurityInfo(securityData);
      }

      // Fetch notification preferences
      const notifRes = await fetch("/api/v1/portal/account/notifications", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (notifRes.ok) {
        const notifData = await notifRes.json();
        setNotifications(notifData);
      }

      // Fetch appearance preferences
      const appearRes = await fetch("/api/v1/portal/account/appearance", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (appearRes.ok) {
        const appearData = await appearRes.json();
        setAppearance(appearData);
      }

      // Fetch privacy settings
      const privacyRes = await fetch("/api/v1/portal/account/privacy", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (privacyRes.ok) {
        const privacyData = await privacyRes.json();
        setPrivacy(privacyData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load account data");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNotifications = async () => {
    if (!notifications) return;

    setSaving(true);
    setSaveSuccess(false);

    try {
      const token = localStorage.getItem("portal_access_token");
      const response = await fetch("/api/v1/portal/account/notifications", {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(notifications),
      });

      if (response.status === 401) {
        router.push("/portal/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to save notification preferences");
      }

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAppearance = async () => {
    if (!appearance) return;

    setSaving(true);
    setSaveSuccess(false);

    try {
      const token = localStorage.getItem("portal_access_token");
      const response = await fetch("/api/v1/portal/account/appearance", {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(appearance),
      });

      if (response.status === 401) {
        router.push("/portal/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to save appearance preferences");
      }

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const handleSavePrivacy = async () => {
    if (!privacy) return;

    setSaving(true);
    setSaveSuccess(false);

    try {
      const token = localStorage.getItem("portal_access_token");
      const response = await fetch("/api/v1/portal/account/privacy", {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(privacy),
      });

      if (response.status === 401) {
        router.push("/portal/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to save privacy settings");
      }

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading account settings...</p>
        </div>
      </div>
    );
  }

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "profile", label: "Profile", icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
    { id: "security", label: "Security", icon: "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" },
    { id: "notifications", label: "Notifications", icon: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" },
    { id: "appearance", label: "Appearance", icon: "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" },
    { id: "privacy", label: "Privacy", icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link href="/portal/dashboard" className="text-indigo-600 hover:underline text-sm">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">Account Settings</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {saveSuccess && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">Settings saved successfully!</p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex overflow-x-auto">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 whitespace-nowrap ${
                    activeTab === tab.id
                      ? "border-indigo-600 text-indigo-600"
                      : "border-transparent text-gray-500 hover:text-gray-700"
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon} />
                  </svg>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === "profile" && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Personal Information</h2>
                  <p className="text-gray-600 mb-6">Update your personal information and contact details.</p>
                </div>

                {profile && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                      <p className="text-gray-900">{profile.full_name}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Medical Record Number</label>
                      <p className="text-gray-900">{profile.medical_record_number}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                      <p className="text-gray-900">{profile.phone || "Not provided"}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                      <p className="text-gray-900">{profile.email || "Not provided"}</p>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                      <p className="text-gray-900">{profile.address || "Not provided"}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                      <p className="text-gray-900">{profile.city || "Not provided"}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Province</label>
                      <p className="text-gray-900">{profile.province || "Not provided"}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
                      <p className="text-gray-900">{profile.postal_code || "Not provided"}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                      <p className="text-gray-900">
                        {new Date(profile.date_of_birth).toLocaleDateString("id-ID", {
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                        })}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                      <p className="text-gray-900 capitalize">{profile.gender}</p>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <Link
                    href="/portal/account/profile"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 inline-block"
                  >
                    Edit Profile
                  </Link>
                </div>
              </div>
            )}

            {activeTab === "security" && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Security Settings</h2>
                  <p className="text-gray-600 mb-6">Manage your password and security settings.</p>
                </div>

                {securityInfo && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email Verified</label>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${
                        securityInfo.email_verified
                          ? "bg-green-100 text-green-700"
                          : "bg-yellow-100 text-yellow-700"
                      }`}>
                        {securityInfo.email_verified ? "Verified" : "Not Verified"}
                      </span>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone Verified</label>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${
                        securityInfo.phone_verified
                          ? "bg-green-100 text-green-700"
                          : "bg-yellow-100 text-yellow-700"
                      }`}>
                        {securityInfo.phone_verified ? "Verified" : "Not Verified"}
                      </span>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Login</label>
                      <p className="text-gray-900">
                        {securityInfo.last_login
                          ? new Date(securityInfo.last_login).toLocaleDateString("id-ID", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : "Never"}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Password Change</label>
                      <p className="text-gray-900">
                        {securityInfo.last_password_change
                          ? new Date(securityInfo.last_password_change).toLocaleDateString("id-ID", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            })
                          : "Never"}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Active Sessions</label>
                      <p className="text-gray-900">{securityInfo.active_sessions} active session(s)</p>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <Link
                    href="/portal/account/security"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 inline-block"
                  >
                    Change Password
                  </Link>
                </div>
              </div>
            )}

            {activeTab === "notifications" && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Notification Preferences</h2>
                  <p className="text-gray-600 mb-6">Choose how you want to receive notifications.</p>
                </div>

                {notifications && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                        <p className="text-sm text-gray-500">Receive notifications via email</p>
                      </div>
                      <button
                        onClick={() => setNotifications({ ...notifications, email_notifications: !notifications.email_notifications })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          notifications.email_notifications ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            notifications.email_notifications ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">SMS Notifications</h3>
                        <p className="text-sm text-gray-500">Receive notifications via SMS</p>
                      </div>
                      <button
                        onClick={() => setNotifications({ ...notifications, sms_notifications: !notifications.sms_notifications })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          notifications.sms_notifications ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            notifications.sms_notifications ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Appointment Reminders</h3>
                        <p className="text-sm text-gray-500">Get reminded about upcoming appointments</p>
                      </div>
                      <button
                        onClick={() => setNotifications({ ...notifications, appointment_reminders: !notifications.appointment_reminders })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          notifications.appointment_reminders ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            notifications.appointment_reminders ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Bill Reminders</h3>
                        <p className="text-sm text-gray-500">Receive payment due reminders</p>
                      </div>
                      <button
                        onClick={() => setNotifications({ ...notifications, bill_reminders: !notifications.bill_reminders })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          notifications.bill_reminders ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            notifications.bill_reminders ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Lab Results Ready</h3>
                        <p className="text-sm text-gray-500">Get notified when lab results are available</p>
                      </div>
                      <button
                        onClick={() => setNotifications({ ...notifications, lab_results_ready: !notifications.lab_results_ready })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          notifications.lab_results_ready ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            notifications.lab_results_ready ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Prescription Ready</h3>
                        <p className="text-sm text-gray-500">Get notified when prescriptions are ready for pickup</p>
                      </div>
                      <button
                        onClick={() => setNotifications({ ...notifications, prescription_ready: !notifications.prescription_ready })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          notifications.prescription_ready ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            notifications.prescription_ready ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Marketing Emails</h3>
                        <p className="text-sm text-gray-500">Receive news and promotional content</p>
                      </div>
                      <button
                        onClick={() => setNotifications({ ...notifications, marketing_emails: !notifications.marketing_emails })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          notifications.marketing_emails ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            notifications.marketing_emails ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="py-3">
                      <label className="block text-sm font-medium text-gray-900 mb-2">Digest Frequency</label>
                      <select
                        value={notifications.digest_frequency}
                        onChange={(e) => setNotifications({ ...notifications, digest_frequency: e.target.value as any })}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
                      >
                        <option value="immediate">Immediate</option>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                      </select>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <button
                    onClick={handleSaveNotifications}
                    disabled={saving}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {saving ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              </div>
            )}

            {activeTab === "appearance" && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Appearance Preferences</h2>
                  <p className="text-gray-600 mb-6">Customize how the portal looks and feels.</p>
                </div>

                {appearance && (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-900 mb-2">Language</label>
                      <select
                        value={appearance.language}
                        onChange={(e) => setAppearance({ ...appearance, language: e.target.value as any })}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
                      >
                        <option value="indonesian">Indonesian</option>
                        <option value="english">English</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-900 mb-2">Theme</label>
                      <select
                        value={appearance.theme}
                        onChange={(e) => setAppearance({ ...appearance, theme: e.target.value as any })}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
                      >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="auto">Auto</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-900 mb-2">Font Size</label>
                      <select
                        value={appearance.font_size}
                        onChange={(e) => setAppearance({ ...appearance, font_size: e.target.value as any })}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
                      >
                        <option value="small">Small</option>
                        <option value="medium">Medium</option>
                        <option value="large">Large</option>
                      </select>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <button
                    onClick={handleSaveAppearance}
                    disabled={saving}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {saving ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              </div>
            )}

            {activeTab === "privacy" && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Privacy Settings</h2>
                  <p className="text-gray-600 mb-6">Control your data sharing and privacy preferences.</p>
                </div>

                {privacy && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Share Data with BPJS</h3>
                        <p className="text-sm text-gray-500">Allow sharing your medical data with BPJS for claims</p>
                      </div>
                      <button
                        onClick={() => setPrivacy({ ...privacy, share_data_with_bpjs: !privacy.share_data_with_bpjs })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          privacy.share_data_with_bpjs ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            privacy.share_data_with_bpjs ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Allow Family Access</h3>
                        <p className="text-sm text-gray-500">Allow family members to access your health records</p>
                      </div>
                      <button
                        onClick={() => setPrivacy({ ...privacy, allow_family_access: !privacy.allow_family_access })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          privacy.allow_family_access ? "bg-indigo-600" : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            privacy.allow_family_access ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    <div className="py-3">
                      <label className="block text-sm font-medium text-gray-900 mb-2">Data Retention Days</label>
                      <input
                        type="number"
                        value={privacy.data_retention_days}
                        onChange={(e) => setPrivacy({ ...privacy, data_retention_days: parseInt(e.target.value) || 0 })}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        min="0"
                      />
                      <p className="text-sm text-gray-500 mt-1">Number of days to retain your data before archiving</p>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <button
                    onClick={handleSavePrivacy}
                    disabled={saving}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {saving ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
