"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface NotificationChannel {
  email: boolean;
  sms: boolean;
  whatsapp: boolean;
  push: boolean;
  in_app: boolean;
}

interface NotificationTypePreference {
  [key: string]: boolean | NotificationChannel;
}

interface NotificationPreferences {
  channel_preferences: NotificationChannel;
  type_preferences?: NotificationTypePreference;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  timezone?: string;
}

interface NotificationType {
  id: string;
  name: string;
  nameId: string;
  description: string;
  icon: string;
}

const NOTIFICATION_TYPES: NotificationType[] = [
  {
    id: "appointment_reminder",
    name: "Appointment Reminders",
    nameId: "Pengingat Janji Temu",
    description: "Reminders for upcoming appointments",
    icon: "📅",
  },
  {
    id: "appointment_confirmation",
    name: "Appointment Confirmations",
    nameId: "Konfirmasi Janji Temu",
    description: "Confirmations when booking appointments",
    icon: "✅",
  },
  {
    id: "appointment_cancellation",
    name: "Appointment Cancellations",
    nameId: "Pembatalan Janji Temu",
    description: "Notifications when appointments are cancelled",
    icon: "❌",
  },
  {
    id: "appointment_rescheduling",
    name: "Appointment Rescheduling",
    nameId: "Penjadwalan Ulang Janji Temu",
    description: "Notifications when appointments are rescheduled",
    icon: "🔄",
  },
  {
    id: "prescription_ready",
    name: "Prescription Ready",
    nameId: "Resep Siap",
    description: "When your prescription is ready for pickup",
    icon: "💊",
  },
  {
    id: "test_results",
    name: "Test Results",
    nameId: "Hasil Lab",
    description: "When lab or radiology results are available",
    icon: "🔬",
  },
  {
    id: "billing_payment",
    name: "Billing & Payments",
    nameId: "Tagihan & Pembayaran",
    description: "Payment reminders and billing notifications",
    icon: "💳",
  },
  {
    id: "system_alert",
    name: "System Alerts",
    nameId: "Alert Sistem",
    description: "Important system announcements",
    icon: "🔔",
  },
  {
    id: "marketing",
    name: "Marketing",
    nameId: "Pemasaran",
    description: "Health tips and promotional content",
    icon: "📢",
  },
];

const CHANNELS = [
  { id: "email", name: "Email", icon: "📧", description: "Email notifications" },
  { id: "sms", name: "SMS", icon: "💬", description: "Text messages to your phone" },
  { id: "whatsapp", name: "WhatsApp", icon: "📱", description: "WhatsApp messages" },
  { id: "push", name: "Push", icon: "🔔", description: "Browser/app notifications" },
  { id: "in_app", name: "In-App", icon: "📲", description: "Notifications within the portal" },
];

export default function NotificationPreferencesPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [quietHoursEnabled, setQuietHoursEnabled] = useState(false);

  useEffect(() => {
    checkAuth();
    fetchPreferences();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchPreferences = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/v1/notifications/preferences", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.status === 401) {
        router.push("/portal/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch preferences");
      }

      const data = await response.json();

      // Parse preferences from the API response format
      const parsedPreferences: NotificationPreferences = {
        channel_preferences: {
          email: true,
          sms: false,
          whatsapp: true,
          push: true,
          in_app: true,
        },
        type_preferences: {},
        quiet_hours_start: undefined,
        quiet_hours_end: undefined,
        timezone: "Asia/Jakarta",
      };

      // Parse the preferences list into our format
      if (data.preferences && Array.isArray(data.preferences)) {
        data.preferences.forEach((pref: any) => {
          if (pref.setting_key === "channel_preferences") {
            try {
              parsedPreferences.channel_preferences = JSON.parse(pref.setting_value);
            } catch {
              // Use defaults
            }
          } else if (pref.setting_key === "quiet_hours") {
            try {
              const quietHours = JSON.parse(pref.setting_value);
              parsedPreferences.quiet_hours_start = quietHours.start;
              parsedPreferences.quiet_hours_end = quietHours.end;
              setQuietHoursEnabled(!!quietHours.start && !!quietHours.end);
            } catch {
              // No quiet hours set
            }
          } else if (pref.setting_key === "timezone") {
            parsedPreferences.timezone = pref.setting_value;
          } else if (pref.setting_key.startsWith("type_")) {
            const typeId = pref.setting_key.replace("type_", "");
            try {
              parsedPreferences.type_preferences = parsedPreferences.type_preferences || {};
              parsedPreferences.type_preferences[typeId] = JSON.parse(pref.setting_value);
            } catch {
              // Use channel defaults
            }
          }
        });
      }

      setPreferences(parsedPreferences);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load preferences");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!preferences) return;

    setSaving(true);
    setSaveSuccess(false);
    setError(null);

    try {
      const token = localStorage.getItem("portal_access_token");
      if (!token) {
        router.push("/portal/login");
        return;
      }

      // Build the request payload
      const payload: any = {
        channel_preferences: preferences.channel_preferences,
      };

      if (quietHoursEnabled && preferences.quiet_hours_start && preferences.quiet_hours_end) {
        payload.quiet_hours_start = preferences.quiet_hours_start;
        payload.quiet_hours_end = preferences.quiet_hours_end;
      }

      if (preferences.timezone) {
        payload.timezone = preferences.timezone;
      }

      const response = await fetch("/api/v1/notifications/preferences", {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to save preferences");
      }

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  const handleChannelToggle = (channel: keyof NotificationChannel) => {
    if (!preferences) return;
    setPreferences({
      ...preferences,
      channel_preferences: {
        ...preferences.channel_preferences,
        [channel]: !preferences.channel_preferences[channel],
      },
    });
  };

  const handleTypeToggle = (typeId: string) => {
    if (!preferences) return;

    const currentEnabled = preferences.type_preferences?.[typeId];
    const newValue = currentEnabled === false ? true : (currentEnabled === true ? false : true);

    setPreferences({
      ...preferences,
      type_preferences: {
        ...preferences.type_preferences,
        [typeId]: newValue,
      },
    });
  };

  const handleTypeChannelToggle = (typeId: string, channel: keyof NotificationChannel) => {
    if (!preferences || !preferences.type_preferences) return;

    const typePref = preferences.type_preferences[typeId];
    if (typeof typePref === "boolean") {
      // If it's currently a boolean, convert to channel preferences
      setPreferences({
        ...preferences,
        type_preferences: {
          ...preferences.type_preferences,
          [typeId]: {
            email: channel === "email" ? !typePref : typePref,
            sms: channel === "sms" ? !typePref : false,
            whatsapp: channel === "whatsapp" ? !typePref : true,
            push: channel === "push" ? !typePref : true,
            in_app: channel === "in_app" ? !typePref : true,
          },
        },
      });
    } else if (typeof typePref === "object") {
      // Toggle the specific channel
      setPreferences({
        ...preferences,
        type_preferences: {
          ...preferences.type_preferences,
          [typeId]: {
            ...typePref,
            [channel]: !typePref[channel],
          },
        },
      });
    }
  };

  const getTypeChannelEnabled = (typeId: string, channel: keyof NotificationChannel): boolean => {
    if (!preferences?.type_preferences) return false;
    const typePref = preferences.type_preferences[typeId];
    if (typeof typePref === "boolean") {
      return typePref ? preferences.channel_preferences[channel] : false;
    } else if (typeof typePref === "object") {
      return typePref[channel] ?? false;
    }
    return false;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Memuat preferensi notifikasi...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Preferensi Notifikasi</h1>
          <p className="mt-2 text-gray-600">
            Atur bagaimana Anda ingin menerima notifikasi dari kami
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {saveSuccess && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800">✓ Preferensi berhasil disimpan</p>
          </div>
        )}

        {/* Global Channel Preferences */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Pengaturan Channel Global</h2>
            <p className="mt-1 text-sm text-gray-600">
              Atur channel notifikasi default untuk semua tipe
            </p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {CHANNELS.map((channel) => (
                <div key={channel.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                  <div className="flex items-center flex-1">
                    <span className="text-2xl mr-3">{channel.icon}</span>
                    <div>
                      <p className="font-medium text-gray-900">{channel.name}</p>
                      <p className="text-sm text-gray-500">{channel.description}</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences?.channel_preferences[channel.id as keyof NotificationChannel] || false}
                      onChange={() => handleChannelToggle(channel.id as keyof NotificationChannel)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Notification Type Preferences */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Preferensi per Tipe Notifikasi</h2>
            <p className="mt-1 text-sm text-gray-600">
              Atur notifikasi untuk setiap tipe secara spesifik
            </p>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              {NOTIFICATION_TYPES.map((type) => {
                const typePref = preferences?.type_preferences?.[type.id];
                const isEnabled = typePref !== false;

                return (
                  <div key={type.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center flex-1">
                        <span className="text-2xl mr-3">{type.icon}</span>
                        <div>
                          <p className="font-medium text-gray-900">{type.nameId}</p>
                          <p className="text-sm text-gray-500">{type.description}</p>
                        </div>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={isEnabled}
                          onChange={() => handleTypeToggle(type.id)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    {isEnabled && (
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4 pt-4 border-t border-gray-100">
                        {CHANNELS.map((channel) => {
                          const channelEnabled = getTypeChannelEnabled(type.id, channel.id as keyof NotificationChannel);
                          return (
                            <button
                              key={channel.id}
                              onClick={() => handleTypeChannelToggle(type.id, channel.id as keyof NotificationChannel)}
                              className={`
                                flex flex-col items-center justify-center p-3 rounded-lg border-2 transition-all
                                ${channelEnabled
                                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                                  : 'border-gray-200 bg-gray-50 text-gray-400 hover:border-gray-300'
                                }
                              `}
                              title={channel.name}
                            >
                              <span className="text-xl mb-1">{channel.icon}</span>
                              <span className="text-xs font-medium">{channel.name}</span>
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Quiet Hours */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Jam Tenang (Quiet Hours)</h2>
                <p className="mt-1 text-sm text-gray-600">
                  Nonaktifkan notifikasi selama jam tertentu
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={quietHoursEnabled}
                  onChange={(e) => setQuietHoursEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>

          {quietHoursEnabled && (
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Jam Mulai
                  </label>
                  <input
                    type="time"
                    value={preferences?.quiet_hours_start || "22:00"}
                    onChange={(e) => setPreferences({ ...preferences!, quiet_hours_start: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Jam Selesai
                  </label>
                  <input
                    type="time"
                    value={preferences?.quiet_hours_end || "08:00"}
                    onChange={(e) => setPreferences({ ...preferences!, quiet_hours_end: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <p className="mt-4 text-sm text-gray-500">
                Notifikasi akan dipause selama jam ini (Timezone: {preferences?.timezone || "Asia/Jakarta"})
              </p>
            </div>
          )}
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? "Menyimpan..." : "Simpan Preferensi"}
          </button>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Informasi</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Notifikasi penting (seperti alert sistem) tetap akan dikirim meskipun channel dinonaktifkan</li>
            <li>• Anda dapat menyesuaikan preferensi per tipe notifikasi untuk kontrol yang lebih detail</li>
            <li>• Jam tenang akan menonaktifkan semua notifikasi non-urgent selama periode tersebut</li>
            <li>• Perubahan akan diterapkan secara instan setelah disimpan</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
