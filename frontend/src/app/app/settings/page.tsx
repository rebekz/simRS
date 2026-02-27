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
  Key,
  Save,
  RotateCcw,
  ChevronRight,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export default function UserSettingsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("profile");
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  // Profile settings state
  const [profileSettings, setProfileSettings] = useState({
    fullName: "",
    email: "",
    phone: "",
    department: "",
  });

  // Notification settings state
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    appointmentReminders: true,
    criticalAlerts: true,
  });

  // Appearance settings state
  const [appearanceSettings, setAppearanceSettings] = useState({
    theme: "light",
    language: "id",
    compactMode: false,
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

      // Load from localStorage as fallback
      const savedSettings = localStorage.getItem("user_settings");
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        if (parsed.profile) setProfileSettings(parsed.profile);
        if (parsed.notifications) setNotificationSettings(parsed.notifications);
        if (parsed.appearance) setAppearanceSettings(parsed.appearance);
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
      const allSettings = {
        profile: profileSettings,
        notifications: notificationSettings,
        appearance: appearanceSettings,
      };

      localStorage.setItem("user_settings", JSON.stringify(allSettings));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error("Failed to save settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (confirm("Apakah Anda yakin ingin mengembalikan semua pengaturan ke default?")) {
      setProfileSettings({ fullName: "", email: "", phone: "", department: "" });
      setNotificationSettings({
        emailNotifications: true,
        pushNotifications: true,
        appointmentReminders: true,
        criticalAlerts: true,
      });
      setAppearanceSettings({ theme: "light", language: "id", compactMode: false });
    }
  };

  const tabs = [
    { id: "profile", label: "Profil", icon: <User className="h-4 w-4" /> },
    { id: "notifications", label: "Notifikasi", icon: <Bell className="h-4 w-4" /> },
    { id: "appearance", label: "Tampilan", icon: <Palette className="h-4 w-4" /> },
    { id: "security", label: "Keamanan", icon: <Shield className="h-4 w-4" /> },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
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
            <div className="space-y-3">
              {[
                { key: "emailNotifications", label: "Notifikasi Email", desc: "Terima notifikasi melalui email" },
                { key: "pushNotifications", label: "Notifikasi Push", desc: "Terima notifikasi di browser" },
                { key: "appointmentReminders", label: "Pengingat Janji Temu", desc: "Ingatkan pasien tentang janji temu" },
                { key: "criticalAlerts", label: "Alert Kritis", desc: "Notifikasi untuk kondisi darurat" },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.label}</p>
                    <p className="text-xs text-gray-500">{item.desc}</p>
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
                      className={`px-4 py-2 rounded-md border text-sm ${
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
                <label className="block text-sm font-medium text-gray-700 mb-2">Bahasa</label>
                <select
                  value={appearanceSettings.language}
                  onChange={(e) => setAppearanceSettings({ ...appearanceSettings, language: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                >
                  <option value="id">Bahasa Indonesia</option>
                  <option value="en">English</option>
                </select>
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

      case "security":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Keamanan Akun</h3>
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Password</p>
                    <p className="text-xs text-gray-500">Terakhir diubah: 30 hari yang lalu</p>
                  </div>
                  <Button variant="secondary" size="sm">
                    <Key className="h-4 w-4 mr-1" />
                    Ubah Password
                  </Button>
                </div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Autentikasi Dua Faktor</p>
                    <p className="text-xs text-gray-500">Tambah lapisan keamanan ekstra</p>
                  </div>
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                    Tidak Aktif
                  </span>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">
            Dashboard
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Pengaturan</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Settings className="h-6 w-6 mr-2 text-gray-600" />
          Pengaturan
        </h1>
        <p className="text-gray-600 mt-1">Kelola preferensi dan pengaturan akun Anda</p>
      </div>

      {/* Saved notification */}
      {saved && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center">
          <Check className="h-5 w-5 text-green-600 mr-2" />
          <span className="text-green-800">Pengaturan berhasil disimpan</span>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? "border-teal-500 text-teal-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <Card className="p-6">
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
          </div>
        ) : (
          renderTabContent()
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
  );
}
