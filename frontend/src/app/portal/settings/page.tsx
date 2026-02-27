"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Settings,
  Bell,
  Lock,
  ChevronRight,
  Save,
} from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function PortalSettingsPage() {
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [settings, setSettings] = useState({
    emailNotifications: true,
    smsNotifications: false,
    appointmentReminders: true,
    billingReminders: true,
    language: "id",
  });

  const handleSave = async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setLoading(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/portal/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Pengaturan</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Settings className="h-6 w-6 mr-2 text-gray-600" />
          Pengaturan
        </h1>
        <p className="text-gray-600">Kelola preferensi akun Anda</p>
      </div>

      {saved && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          Pengaturan berhasil disimpan
        </div>
      )}

      {/* Notifications */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold flex items-center">
            <Bell className="h-5 w-5 mr-2" />
            Notifikasi
          </h2>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { key: "emailNotifications", label: "Notifikasi Email", desc: "Terima pembaruan melalui email" },
            { key: "smsNotifications", label: "Notifikasi SMS", desc: "Terima pengingat melalui SMS" },
            { key: "appointmentReminders", label: "Pengingat Janji Temu", desc: "Ingatkan jadwal konsultasi" },
            { key: "billingReminders", label: "Pengingat Tagihan", desc: "Ingatkan tagihan yang belum dibayar" },
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between py-2">
              <div>
                <p className="font-medium text-gray-900">{item.label}</p>
                <p className="text-sm text-gray-500">{item.desc}</p>
              </div>
              <button
                onClick={() => setSettings({ ...settings, [item.key]: !settings[item.key as keyof typeof settings] })}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  settings[item.key as keyof typeof settings] ? "bg-teal-600" : "bg-gray-300"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    settings[item.key as keyof typeof settings] ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Language */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">Bahasa</h2>
        </CardHeader>
        <CardContent>
          <select
            value={settings.language}
            onChange={(e) => setSettings({ ...settings, language: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
          >
            <option value="id">Bahasa Indonesia</option>
            <option value="en">English</option>
          </select>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold flex items-center">
            <Lock className="h-5 w-5 mr-2" />
            Keamanan
          </h2>
        </CardHeader>
        <CardContent>
          <Button variant="secondary" className="w-full">
            Ubah Password
          </Button>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button variant="primary" onClick={handleSave} disabled={loading}>
          <Save className="h-4 w-4 mr-2" />
          {loading ? "Menyimpan..." : "Simpan Pengaturan"}
        </Button>
      </div>
    </div>
  );
}
