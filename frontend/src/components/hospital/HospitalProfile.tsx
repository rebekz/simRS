"use client";

import React, { useState, useEffect } from 'react';

// Types
interface HospitalProfile {
  id: number;
  name: string;
  name_alias?: string;
  license_number: string;
  address_line: string;
  address_city: string;
  address_province: string;
  address_postal_code: string;
  country: string;
  phone: string;
  phone_alternate?: string;
  email: string;
  website?: string;
  bpjs_ppk_code: string;
  bpjs_pcare_code?: string;
  bpjs_antrian_code?: string;
  hospital_class?: string;
  hospital_type?: string;
  ownership?: string;
  logo_url?: string;
  created_at: string;
  updated_at: string;
}

interface ConfigurationSummary {
  hospital_profile: HospitalProfile;
  total_departments: number;
  departments_by_type: Record<string, number>;
  total_staff: number;
  staff_by_role: Record<string, number>;
  total_shifts: number;
  branding_configured: boolean;
  configuration_completion: number;
  missing_configurations: string[];
}

const DEPARTMENT_TYPE_NAMES: Record<string, string> = {
  'ward': 'Ruang Rawat Inap',
  'poli': 'Poli Rawat Jalan',
  'unit': 'Unit Penunjang',
  'icu': 'ICU',
  'er': 'UGD',
  'or': 'Ruang Operasi',
};

const STAFF_ROLE_NAMES: Record<string, string> = {
  'doctor': 'Dokter',
  'nurse': 'Perawat',
  'midwife': 'Bidan',
  'pharmacist': 'Apoteker',
  'lab_technician': 'Teknisi Lab',
  'radiologist': 'Radiografer',
  'administrator': 'Administrator',
  'receptionist': 'Resepsionis',
  'security': 'Satpam',
  'cleaning': 'Kebersihan',
  'other': 'Lainnya',
};

export default function HospitalProfile() {
  const [summary, setSummary] = useState<ConfigurationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSummary();
  }, []);

  async function fetchSummary() {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/hospital/configuration-summary');
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error('Failed to fetch configuration summary:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    try {
      // TODO: Implement save functionality
      await fetchSummary();
      setEditing(false);
    } catch (error) {
      console.error('Failed to save hospital profile:', error);
    } finally {
      setSaving(false);
    }
  }

  if (loading || !summary) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const completion = summary.configuration_completion;
  const isComplete = completion === 100;

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Konfigurasi Rumah Sakit</h1>
          <p className="text-gray-600">Pengaturan profil dan informasi rumah sakit</p>
        </div>
        {!editing && (
          <button
            onClick={() => setEditing(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Edit Profil
          </button>
        )}
      </div>

      {/* Configuration Completion Banner */}
      <div className={`mb-6 p-4 rounded-lg border-2 ${
        isComplete
          ? 'bg-green-50 border-green-300'
          : 'bg-yellow-50 border-yellow-300'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className={`font-semibold ${isComplete ? 'text-green-900' : 'text-yellow-900'}`}>
              {isComplete ? 'Konfigurasi Lengkap' : 'Konfigurasi Belum Lengkap'}
            </h3>
            <p className={`text-sm ${isComplete ? 'text-green-700' : 'text-yellow-700'}`}>
              {isComplete
                ? 'Semua pengaturan rumah sakit telah dikonfigurasi dengan lengkap.'
                : `${completion}% selesai. ${summary.missing_configurations.length} item perlu dikonfigurasi.`}
            </p>
            {!isComplete && summary.missing_configurations.length > 0 && (
              <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside">
                {summary.missing_configurations.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            )}
          </div>
          <div className={`text-3xl font-bold ${isComplete ? 'text-green-600' : 'text-yellow-600'}`}>
            {completion.toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Departemen</div>
          <div className="text-3xl font-bold text-gray-900">{summary.total_departments}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Staf Medis</div>
          <div className="text-3xl font-bold text-gray-900">{summary.total_staff}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Dokter</div>
          <div className="text-3xl font-bold text-blue-600">{summary.staff_by_role['doctor'] || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Shift Kerja</div>
          <div className="text-3xl font-bold text-gray-900">{summary.total_shifts}</div>
        </div>
      </div>

      {/* Hospital Profile */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Profil Rumah Sakit</h2>
          {summary.hospital_profile.logo_url && (
            <img
              src={summary.hospital_profile.logo_url}
              alt="Logo"
              className="h-16 w-auto"
            />
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Informasi Dasar</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Nama Rumah Sakit:</span>
                <span className="font-medium">{summary.hospital_profile.name}</span>
              </div>
              {summary.hospital_profile.name_alias && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Singkatan:</span>
                  <span className="font-medium">{summary.hospital_profile.name_alias}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">No. Izin:</span>
                <span className="font-medium">{summary.hospital_profile.license_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Kelas:</span>
                <span className="font-medium">{summary.hospital_profile.hospital_class || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tipe:</span>
                <span className="font-medium">{summary.hospital_profile.hospital_type || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Kepemilikan:</span>
                <span className="font-medium">{summary.hospital_profile.ownership || '-'}</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Alamat & Kontak</h3>
            <div className="space-y-2">
              <div>
                <span className="text-gray-600">Alamat:</span>
                <p className="font-medium">{summary.hospital_profile.address_line}</p>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Kota/Kab:</span>
                <span className="font-medium">{summary.hospital_profile.address_city}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Provinsi:</span>
                <span className="font-medium">{summary.hospital_profile.address_province}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Kode Pos:</span>
                <span className="font-medium">{summary.hospital_profile.address_postal_code}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Telepon:</span>
                <span className="font-medium">{summary.hospital_profile.phone}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Email:</span>
                <span className="font-medium">{summary.hospital_profile.email}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="font-semibold text-gray-900 mb-3">Informasi BPJS</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-sm text-blue-700">Kode PPK</div>
              <div className="font-semibold text-blue-900">{summary.hospital_profile.bpjs_ppk_code}</div>
            </div>
            {summary.hospital_profile.bpjs_pcare_code && (
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="text-sm text-blue-700">Kode PCare</div>
                <div className="font-semibold text-blue-900">{summary.hospital_profile.bpjs_pcare_code}</div>
              </div>
            )}
            {summary.hospital_profile.bpjs_antrian_code && (
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="text-sm text-blue-700">Kode Antrean</div>
                <div className="font-semibold text-blue-900">{summary.hospital_profile.bpjs_antrian_code}</div>
              </div>
            )}
          </div>
        </div>

        {editing && (
          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              {saving ? 'Menyimpan...' : 'Simpan Perubahan'}
            </button>
            <button
              onClick={() => setEditing(false)}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Batal
            </button>
          </div>
        )}
      </div>

      {/* Department Breakdown */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Departemen per Tipe</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(summary.departments_by_type).map(([type, count]) => (
            <div key={type} className="p-4 bg-gray-50 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">{count}</div>
              <div className="text-sm text-gray-600">{DEPARTMENT_TYPE_NAMES[type] || type}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Staff Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Staf per Peran</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {Object.entries(summary.staff_by_role).map(([role, count]) => (
            <div key={role} className="p-4 bg-gray-50 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">{count}</div>
              <div className="text-sm text-gray-600">{STAFF_ROLE_NAMES[role] || role}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
