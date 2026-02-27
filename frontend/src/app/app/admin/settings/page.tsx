"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Settings,
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  Database,
  Key,
  Save,
  RotateCcw,
  ChevronRight,
  Check,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

interface SettingsSection {
  id: string;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const settingsSections: SettingsSection[] = [
  {
    id: "profile",
    label: "Profil Pengguna",
    icon: <User className="h-5 w-5" />,
    description: "Kelola informasi profil dan akun Anda",
  },
  {
    id: "notifications",
    label: "Notifikasi",
    icon: <Bell className="h-5 w-5" />,
    description: "Atur preferensi notifikasi email dan sistem",
  },
  {
    id: "security",
    label: "Keamanan",
    icon: <Shield className="h-5 w-5" />,
    description: "Password, autentikasi dua faktor, dan sesi",
  },
  {
    id: "appearance",
    label: "Tampilan",
    icon: <Palette className="h-5 w-5" />,
    description: "Tema, bahasa, dan preferensi tampilan",
  },
  {
    id: "localization",
    label: "Lokalisasi",
    icon: <Globe className="h-5 w-5" />,
    description: "Format tanggal, waktu, dan mata uang",
  },
  {
    id: "integrations",
    label: "Integrasi",
    icon: <Database className="h-5 w-5" />,
    description: "Koneksi ke sistem eksternal (BPJS, SATUSEHAT)",
  },
  {
    id: "api-keys",
    label: "API Keys",
    icon: <Key className="h-5 w-5" />,
    description: "Kelola kunci akses API",
  },
];

export default function SettingsPage() {
  const router = useRouter();
  const [activeSection, setActiveSection] = useState("profile");
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  // Profile settings state
  const [profileSettings, setProfileSettings] = useState({
    fullName: "",
    email: "",
    phone: "",
    department: "",
    role: "",
  });

  // Notification settings state
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    smsNotifications: false,
    appointmentReminders: true,
    criticalAlerts: true,
    dailyReports: false,
    weeklyReports: true,
  });

  // Security settings state
  const [securitySettings, setSecuritySettings] = useState({
    twoFactorEnabled: false,
    sessionTimeout: "30",
    passwordExpiry: "90",
    loginNotifications: true,
  });

  // Appearance settings state
  const [appearanceSettings, setAppearanceSettings] = useState({
    theme: "light",
    fontSize: "medium",
    compactMode: false,
    sidebarCollapsed: false,
  });

  // Localization settings state
  const [localizationSettings, setLocalizationSettings] = useState({
    language: "id",
    dateFormat: "DD-MM-YYYY",
    timeFormat: "24h",
    currency: "IDR",
    timezone: "Asia/Jakarta",
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      // Try to fetch settings from API
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/users/me/settings`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        // Apply settings from API
        if (data.profile) setProfileSettings(data.profile);
        if (data.notifications) setNotificationSettings(data.notifications);
        if (data.security) setSecuritySettings(data.security);
        if (data.appearance) setAppearanceSettings(data.appearance);
        if (data.localization) setLocalizationSettings(data.localization);
      } else {
        // Load from localStorage as fallback
        const savedSettings = localStorage.getItem("user_settings");
        if (savedSettings) {
          const parsed = JSON.parse(savedSettings);
          if (parsed.profile) setProfileSettings(parsed.profile);
          if (parsed.notifications) setNotificationSettings(parsed.notifications);
          if (parsed.security) setSecuritySettings(parsed.security);
          if (parsed.appearance) setAppearanceSettings(parsed.appearance);
          if (parsed.localization) setLocalizationSettings(parsed.localization);
        }
      }
    } catch (error) {
      console.error("Failed to load settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setSaved(false);

    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) return;

      const allSettings = {
        profile: profileSettings,
        notifications: notificationSettings,
        security: securitySettings,
        appearance: appearanceSettings,
        localization: localizationSettings,
      };

      // Try API first
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/users/me/settings`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(allSettings),
        }
      );

      if (response.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      } else {
        // Save to localStorage as fallback
        localStorage.setItem("user_settings", JSON.stringify(allSettings));
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch (error) {
      console.error("Failed to save settings:", error);
      // Save to localStorage as fallback
      const allSettings = {
        profile: profileSettings,
        notifications: notificationSettings,
        security: securitySettings,
        appearance: appearanceSettings,
        localization: localizationSettings,
      };
      localStorage.setItem("user_settings", JSON.stringify(allSettings));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (confirm("Apakah Anda yakin ingin mengembalikan semua pengaturan ke default?")) {
      setProfileSettings({
        fullName: "",
        email: "",
        phone: "",
        department: "",
        role: "",
      });
      setNotificationSettings({
        emailNotifications: true,
        pushNotifications: true,
        smsNotifications: false,
        appointmentReminders: true,
        criticalAlerts: true,
        dailyReports: false,
        weeklyReports: true,
      });
      setSecuritySettings({
        twoFactorEnabled: false,
        sessionTimeout: "30",
        passwordExpiry: "90",
        loginNotifications: true,
      });
      setAppearanceSettings({
        theme: "light",
        fontSize: "medium",
        compactMode: false,
        sidebarCollapsed: false,
      });
      setLocalizationSettings({
        language: "id",
        dateFormat: "DD-MM-YYYY",
        timeFormat: "24h",
        currency: "IDR",
        timezone: "Asia/Jakarta",
      });
    }
  };

  const renderSectionContent = () => {
    switch (activeSection) {
      case "profile":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Profil Pengguna</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nama Lengkap
                </label>
                <input
                  type="text"
                  value={profileSettings.fullName}
                  onChange={(e) =>
                    setProfileSettings({ ...profileSettings, fullName: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  placeholder="Nama lengkap Anda"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={profileSettings.email}
                  onChange={(e) =>
                    setProfileSettings({ ...profileSettings, email: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  placeholder="email@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Telepon</label>
                <input
                  type="tel"
                  value={profileSettings.phone}
                  onChange={(e) =>
                    setProfileSettings({ ...profileSettings, phone: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  placeholder="+62 xxx xxxx xxxx"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Departemen</label>
                <input
                  type="text"
                  value={profileSettings.department}
                  onChange={(e) =>
                    setProfileSettings({ ...profileSettings, department: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  placeholder="Departemen"
                />
              </div>
            </div>
          </div>
        );

      case "notifications":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Pengaturan Notifikasi</h3>
            <div className="space-y-4">
              {[
                {
                  key: "emailNotifications",
                  label: "Notifikasi Email",
                  description: "Terima notifikasi melalui email",
                },
                {
                  key: "pushNotifications",
                  label: "Notifikasi Push",
                  description: "Terima notifikasi di browser",
                },
                {
                  key: "smsNotifications",
                  label: "Notifikasi SMS",
                  description: "Terima notifikasi melalui SMS",
                },
                {
                  key: "appointmentReminders",
                  label: "Pengingat Janji Temu",
                  description: "Ingatkan pasien tentang janji temu",
                },
                {
                  key: "criticalAlerts",
                  label: "Alert Kritis",
                  description: "Notifikasi untuk kondisi darurat",
                },
                {
                  key: "dailyReports",
                  label: "Laporan Harian",
                  description: "Terima laporan ringkasan harian",
                },
                {
                  key: "weeklyReports",
                  label: "Laporan Mingguan",
                  description: "Terima laporan ringkasan mingguan",
                },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between py-2">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.label}</p>
                    <p className="text-xs text-gray-500">{item.description}</p>
                  </div>
                  <button
                    onClick={() =>
                      setNotificationSettings({
                        ...notificationSettings,
                        [item.key]: !notificationSettings[item.key as keyof typeof notificationSettings],
                      })
                    }
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      notificationSettings[item.key as keyof typeof notificationSettings]
                        ? "bg-teal-600"
                        : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        notificationSettings[item.key as keyof typeof notificationSettings]
                          ? "translate-x-6"
                          : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>
        );

      case "security":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Keamanan Akun</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Autentikasi Dua Faktor (2FA)
                  </p>
                  <p className="text-xs text-gray-500">
                    Tambah lapisan keamanan ekstra ke akun Anda
                  </p>
                </div>
                <button
                  onClick={() =>
                    setSecuritySettings({
                      ...securitySettings,
                      twoFactorEnabled: !securitySettings.twoFactorEnabled,
                    })
                  }
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    securitySettings.twoFactorEnabled ? "bg-teal-600" : "bg-gray-300"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      securitySettings.twoFactorEnabled ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Waktu Sesi (menit)
                </label>
                <select
                  value={securitySettings.sessionTimeout}
                  onChange={(e) =>
                    setSecuritySettings({ ...securitySettings, sessionTimeout: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="15">15 menit</option>
                  <option value="30">30 menit</option>
                  <option value="60">1 jam</option>
                  <option value="120">2 jam</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Masa Berlaku Password (hari)
                </label>
                <select
                  value={securitySettings.passwordExpiry}
                  onChange={(e) =>
                    setSecuritySettings({ ...securitySettings, passwordExpiry: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="30">30 hari</option>
                  <option value="60">60 hari</option>
                  <option value="90">90 hari</option>
                  <option value="180">180 hari</option>
                </select>
              </div>

              <div className="pt-4 border-t">
                <Button variant="secondary" onClick={() => router.push("/app/change-password")}>
                  <Key className="h-4 w-4 mr-2" />
                  Ubah Password
                </Button>
              </div>
            </div>
          </div>
        );

      case "appearance":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Pengaturan Tampilan</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tema</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: "light", label: "Terang" },
                    { value: "dark", label: "Gelap" },
                    { value: "system", label: "Sistem" },
                  ].map((theme) => (
                    <button
                      key={theme.value}
                      onClick={() => setAppearanceSettings({ ...appearanceSettings, theme: theme.value })}
                      className={`px-4 py-2 rounded-md border ${
                        appearanceSettings.theme === theme.value
                          ? "border-teal-500 bg-teal-50 text-teal-700"
                          : "border-gray-300 hover:border-gray-400"
                      }`}
                    >
                      {theme.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Ukuran Font</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: "small", label: "Kecil" },
                    { value: "medium", label: "Sedang" },
                    { value: "large", label: "Besar" },
                  ].map((size) => (
                    <button
                      key={size.value}
                      onClick={() => setAppearanceSettings({ ...appearanceSettings, fontSize: size.value })}
                      className={`px-4 py-2 rounded-md border ${
                        appearanceSettings.fontSize === size.value
                          ? "border-teal-500 bg-teal-50 text-teal-700"
                          : "border-gray-300 hover:border-gray-400"
                      }`}
                    >
                      {size.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-gray-900">Mode Kompak</p>
                  <p className="text-xs text-gray-500">Tampilkan lebih banyak data di layar</p>
                </div>
                <button
                  onClick={() =>
                    setAppearanceSettings({
                      ...appearanceSettings,
                      compactMode: !appearanceSettings.compactMode,
                    })
                  }
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    appearanceSettings.compactMode ? "bg-teal-600" : "bg-gray-300"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      appearanceSettings.compactMode ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>
        );

      case "localization":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Pengaturan Lokalisasi</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bahasa</label>
                <select
                  value={localizationSettings.language}
                  onChange={(e) =>
                    setLocalizationSettings({ ...localizationSettings, language: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="id">Bahasa Indonesia</option>
                  <option value="en">English</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Format Tanggal</label>
                <select
                  value={localizationSettings.dateFormat}
                  onChange={(e) =>
                    setLocalizationSettings({ ...localizationSettings, dateFormat: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="DD-MM-YYYY">DD-MM-YYYY</option>
                  <option value="MM-DD-YYYY">MM-DD-YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Format Waktu</label>
                <select
                  value={localizationSettings.timeFormat}
                  onChange={(e) =>
                    setLocalizationSettings({ ...localizationSettings, timeFormat: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="24h">24 jam</option>
                  <option value="12h">12 jam (AM/PM)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Mata Uang</label>
                <select
                  value={localizationSettings.currency}
                  onChange={(e) =>
                    setLocalizationSettings({ ...localizationSettings, currency: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="IDR">IDR - Rupiah Indonesia</option>
                  <option value="USD">USD - US Dollar</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Zona Waktu</label>
                <select
                  value={localizationSettings.timezone}
                  onChange={(e) =>
                    setLocalizationSettings({ ...localizationSettings, timezone: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="Asia/Jakarta">WIB (Jakarta)</option>
                  <option value="Asia/Makassar">WITA (Makassar)</option>
                  <option value="Asia/Jayapura">WIT (Jayapura)</option>
                </select>
              </div>
            </div>
          </div>
        );

      case "integrations":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Integrasi Sistem</h3>
            <div className="space-y-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <span className="text-blue-600 font-bold text-sm">BPJS</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">BPJS VClaim</p>
                      <p className="text-xs text-gray-500">Integrasi dengan BPJS Kesehatan</p>
                    </div>
                  </div>
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                    Terhubung
                  </span>
                </div>
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 bg-cyan-100 rounded-lg flex items-center justify-center">
                      <span className="text-cyan-600 font-bold text-xs">SS</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">SATUSEHAT</p>
                      <p className="text-xs text-gray-500">Platform Kemenkes</p>
                    </div>
                  </div>
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                    Konfigurasi
                  </span>
                </div>
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <span className="text-purple-600 font-bold text-xs">SI</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">SIRANAP</p>
                      <p className="text-xs text-gray-500">Ketersediaan Tempat Tidur</p>
                    </div>
                  </div>
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                    Tidak Aktif
                  </span>
                </div>
              </div>
            </div>
          </div>
        );

      case "api-keys":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Kunci API</h3>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">Perhatian</p>
                  <p className="text-xs text-yellow-700 mt-1">
                    API keys bersifat sensitif. Jangan bagikan kepada pihak yang tidak berwenang.
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Production Key</p>
                    <p className="text-xs text-gray-500">Dibuat: 2024-01-15</p>
                  </div>
                  <code className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">
                    sk_live_••••••••••••
                  </code>
                </div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Test Key</p>
                    <p className="text-xs text-gray-500">Dibuat: 2024-01-15</p>
                  </div>
                  <code className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">
                    sk_test_••••••••••••
                  </code>
                </div>
              </div>
            </div>
            <Button variant="secondary">
              <Key className="h-4 w-4 mr-2" />
              Buat Kunci Baru
            </Button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
            <Link href="/app/dashboard" className="hover:text-gray-700">
              Dashboard
            </Link>
            <ChevronRight className="h-4 w-4" />
            <span className="text-gray-900">Pengaturan</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Settings className="h-7 w-7 mr-2 text-gray-600" />
            Pengaturan
          </h1>
          <p className="text-gray-600 mt-1">Kelola preferensi dan pengaturan akun Anda</p>
        </div>

        {/* Saved notification */}
        {saved && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center">
            <Check className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-green-800">Pengaturan berhasil disimpan</span>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Card className="p-2">
              <nav className="space-y-1">
                {settingsSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-md text-left transition-colors ${
                      activeSection === section.id
                        ? "bg-teal-50 text-teal-700"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                  >
                    <span className={activeSection === section.id ? "text-teal-600" : "text-gray-400"}>
                      {section.icon}
                    </span>
                    <span className="text-sm font-medium">{section.label}</span>
                  </button>
                ))}
              </nav>
            </Card>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <Card className="p-6">
              {loading ? (
                <div className="flex items-center justify-center h-48">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
                </div>
              ) : (
                renderSectionContent()
              )}

              {/* Action Buttons */}
              <div className="mt-8 pt-6 border-t flex items-center justify-end space-x-3">
                <Button variant="secondary" onClick={handleReset}>
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button variant="primary" onClick={handleSave} disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  Simpan
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
