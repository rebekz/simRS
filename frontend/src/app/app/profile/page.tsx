"use client";

/**
 * Staff Profile Page - EPIC-020: Staff Portal
 *
 * Self-service profile management for staff members including:
 * - View and update personal information
 * - Update contact details and emergency contacts
 * - Manage professional credentials
 * - Configure notification preferences
 * - Change password
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  User,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  Calendar,
  Shield,
  Bell,
  Key,
  Camera,
  Save,
  X,
  Check,
  AlertCircle,
} from "lucide-react";

interface StaffProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
  phone?: string;
  address?: string;
  city?: string;
  province?: string;
  postal_code?: string;
  date_of_birth?: string;
  gender?: string;
  blood_type?: string;
  employee_id?: string;
  position?: string;
  department?: string;
  hire_date?: string;
  license_number?: string;
  specialization?: string;
  education?: string;
  profile_image_url?: string;
  notification_preferences: {
    email: boolean;
    sms: boolean;
    in_app: boolean;
    appointment_reminders: boolean;
    system_updates: boolean;
  };
  emergency_contact?: {
    name: string;
    relationship: string;
    phone: string;
  };
}

interface UpdateProfileRequest {
  full_name?: string;
  phone?: string;
  address?: string;
  city?: string;
  province?: string;
  postal_code?: string;
  emergency_contact_name?: string;
  emergency_contact_relationship?: string;
  emergency_contact_phone?: string;
}

export default function StaffProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<StaffProfile | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [activeTab, setActiveTab] = useState<"personal" | "professional" | "notifications" | "security">("personal");

  // Form state
  const [formData, setFormData] = useState<UpdateProfileRequest>({});

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch("/api/v1/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setFormData({
          full_name: data.full_name,
          phone: data.phone,
          address: data.address,
          city: data.city,
          province: data.province,
          postal_code: data.postal_code,
          emergency_contact_name: data.emergency_contact?.name,
          emergency_contact_relationship: data.emergency_contact?.relationship,
          emergency_contact_phone: data.emergency_contact?.phone,
        });
      }
    } catch (error) {
      console.error("Failed to fetch profile:", error);
      setErrorMessage("Gagal memuat profil");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch("/api/v1/staff/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setSuccessMessage("Profil berhasil diperbarui");
        setEditMode(false);
        fetchProfile(); // Refresh data
      } else {
        const error = await response.json();
        setErrorMessage(error.detail || "Gagal memperbarui profil");
      }
    } catch (error) {
      console.error("Failed to update profile:", error);
      setErrorMessage("Terjadi kesalahan saat memperbarui profil");
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditMode(false);
    setFormData({
      full_name: profile?.full_name,
      phone: profile?.phone,
      address: profile?.address,
      city: profile?.city,
      province: profile?.province,
      postal_code: profile?.postal_code,
      emergency_contact_name: profile?.emergency_contact?.name,
      emergency_contact_relationship: profile?.emergency_contact?.relationship,
      emergency_contact_phone: profile?.emergency_contact?.phone,
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-gray-500">Profil tidak ditemukan</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profil Saya</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola informasi profil Anda</p>
        </div>
        {!editMode ? (
          <button
            onClick={() => setEditMode(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <User className="h-4 w-4 mr-2" />
            Edit Profil
          </button>
        ) : (
          <div className="flex space-x-3">
            <button
              onClick={handleCancel}
              disabled={saving}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
            >
              <X className="h-4 w-4 mr-2" />
              Batal
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center disabled:opacity-50"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Menyimpan...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Simpan
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center">
          <Check className="h-5 w-5 text-green-600 mr-2" />
          <p className="text-sm text-green-800">{successMessage}</p>
        </div>
      )}

      {errorMessage && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
          <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
          <p className="text-sm text-red-800">{errorMessage}</p>
        </div>
      )}

      {/* Profile Card */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {/* Profile Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 h-32 relative">
          <div className="absolute -bottom-12 left-8">
            <div className="relative">
              <div className="w-24 h-24 bg-gray-300 rounded-full border-4 border-white flex items-center justify-center">
                {profile.profile_image_url ? (
                  <img
                    src={profile.profile_image_url}
                    alt={profile.full_name}
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <User className="w-12 h-12 text-gray-500" />
                )}
              </div>
              {editMode && (
                <button className="absolute bottom-0 right-0 bg-blue-600 text-white p-1.5 rounded-full hover:bg-blue-700">
                  <Camera className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="pt-16 pb-6 px-8">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{profile.full_name}</h2>
              <p className="text-gray-600 mt-1">
                {profile.position} • {profile.department}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Employee ID: {profile.employee_id || "N/A"}
              </p>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-8 border-b border-gray-200">
            <nav className="flex space-x-8">
              <button
                onClick={() => setActiveTab("personal")}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === "personal"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <User className="w-4 h-4 mr-2" />
                Informasi Pribadi
              </button>
              <button
                onClick={() => setActiveTab("professional")}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === "professional"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <Briefcase className="w-4 h-4 mr-2" />
                Informasi Profesional
              </button>
              <button
                onClick={() => setActiveTab("notifications")}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === "notifications"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <Bell className="w-4 h-4 mr-2" />
                Notifikasi
              </button>
              <button
                onClick={() => setActiveTab("security")}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === "security"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <Shield className="w-4 h-4 mr-2" />
                Keamanan
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="mt-6">
            {activeTab === "personal" && (
              <PersonalInfoTab
                profile={profile}
                formData={formData}
                editMode={editMode}
                onChange={setFormData}
              />
            )}

            {activeTab === "professional" && (
              <ProfessionalInfoTab profile={profile} />
            )}

            {activeTab === "notifications" && (
              <NotificationsTab
                profile={profile}
                editMode={editMode}
                onUpdate={(prefs) => {
                  setProfile({ ...profile, notification_preferences: prefs });
                }}
              />
            )}

            {activeTab === "security" && (
              <SecurityTab profile={profile} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Personal Info Tab Component
function PersonalInfoTab({
  profile,
  formData,
  editMode,
  onChange,
}: {
  profile: StaffProfile;
  formData: UpdateProfileRequest;
  editMode: boolean;
  onChange: (data: UpdateProfileRequest) => void;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Contact Information */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Mail className="w-5 h-5 mr-2" />
          Informasi Kontak
        </h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={profile.email}
            disabled
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
          />
          <p className="text-xs text-gray-500 mt-1">Email tidak dapat diubah</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nama Lengkap
          </label>
          <input
            type="text"
            value={formData.full_name || ""}
            onChange={(e) => onChange({ ...formData, full_name: e.target.value })}
            disabled={!editMode}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            No. Telepon
          </label>
          <input
            type="tel"
            value={formData.phone || ""}
            onChange={(e) => onChange({ ...formData, phone: e.target.value })}
            disabled={!editMode}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
          />
        </div>
      </div>

      {/* Address Information */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <MapPin className="w-5 h-5 mr-2" />
          Alamat
        </h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Alamat Lengkap
          </label>
          <textarea
            value={formData.address || ""}
            onChange={(e) => onChange({ ...formData, address: e.target.value })}
            disabled={!editMode}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kota
            </label>
            <input
              type="text"
              value={formData.city || ""}
              onChange={(e) => onChange({ ...formData, city: e.target.value })}
              disabled={!editMode}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Provinsi
            </label>
            <input
              type="text"
              value={formData.province || ""}
              onChange={(e) => onChange({ ...formData, province: e.target.value })}
              disabled={!editMode}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Kode Pos
          </label>
          <input
            type="text"
            value={formData.postal_code || ""}
            onChange={(e) => onChange({ ...formData, postal_code: e.target.value })}
            disabled={!editMode}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
          />
        </div>
      </div>

      {/* Emergency Contact */}
      <div className="md:col-span-2 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Phone className="w-5 h-5 mr-2" />
          Kontak Darurat
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nama Kontak
            </label>
            <input
              type="text"
              value={formData.emergency_contact_name || ""}
              onChange={(e) => onChange({ ...formData, emergency_contact_name: e.target.value })}
              disabled={!editMode}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hubungan
            </label>
            <input
              type="text"
              value={formData.emergency_contact_relationship || ""}
              onChange={(e) => onChange({ ...formData, emergency_contact_relationship: e.target.value })}
              disabled={!editMode}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              No. Telepon
            </label>
            <input
              type="tel"
              value={formData.emergency_contact_phone || ""}
              onChange={(e) => onChange({ ...formData, emergency_contact_phone: e.target.value })}
              disabled={!editMode}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Professional Info Tab Component
function ProfessionalInfoTab({ profile }: { profile: StaffProfile }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Informasi Pekerjaan</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Employee ID
            </label>
            <input
              type="text"
              value={profile.employee_id || "N/A"}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Jabatan
            </label>
            <input
              type="text"
              value={profile.position || "N/A"}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Departemen
          </label>
          <input
            type="text"
            value={profile.department || "N/A"}
            disabled
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tanggal Bergabung
          </label>
          <input
            type="text"
            value={profile.hire_date ? new Date(profile.hire_date).toLocaleDateString("id-ID", {
              year: "numeric",
              month: "long",
              day: "numeric",
            }) : "N/A"}
            disabled
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
          />
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Kredensial Profesional</h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            No. SIP/STR
          </label>
          <input
            type="text"
            value={profile.license_number || "N/A"}
            disabled
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Spesialisasi
          </label>
          <input
            type="text"
            value={profile.specialization || "N/A"}
            disabled
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Pendidikan Terakhir
          </label>
          <input
            type="text"
            value={profile.education || "N/A"}
            disabled
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
          />
        </div>
      </div>
    </div>
  );
}

// Notifications Tab Component
function NotificationsTab({
  profile,
  editMode,
  onUpdate,
}: {
  profile: StaffProfile;
  editMode: boolean;
  onUpdate: (prefs: StaffProfile["notification_preferences"]) => void;
}) {
  const [localPrefs, setLocalPrefs] = useState(profile.notification_preferences);

  const handleToggle = (key: keyof StaffProfile["notification_preferences"]) => {
    const updated = { ...localPrefs, [key]: !localPrefs[key] };
    setLocalPrefs(updated);
    if (!editMode) {
      onUpdate(updated);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Preferensi Notifikasi</h3>
        <div className="space-y-4">
          <NotificationToggle
            label="Notifikasi Email"
            description="Terima notifikasi melalui email"
            checked={localPrefs.email}
            onChange={() => handleToggle("email")}
          />

          <NotificationToggle
            label="Notifikasi SMS"
            description="Terima notifikasi melalui SMS"
            checked={localPrefs.sms}
            onChange={() => handleToggle("sms")}
          />

          <NotificationToggle
            label="Notifikasi In-App"
            description="Terima notifikasi di dalam aplikasi"
            checked={localPrefs.in_app}
            onChange={() => handleToggle("in_app")}
          />
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Jenis Notifikasi</h3>
        <div className="space-y-4">
          <NotificationToggle
            label="Pengingat Janji Temu"
            description="Terima pengingat untuk janji temu yang akan datang"
            checked={localPrefs.appointment_reminders}
            onChange={() => handleToggle("appointment_reminders")}
          />

          <NotificationToggle
            label="Update Sistem"
            description="Terima informasi tentang update dan pemeliharaan sistem"
            checked={localPrefs.system_updates}
            onChange={() => handleToggle("system_updates")}
          />
        </div>
      </div>
    </div>
  );
}

function NotificationToggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
      <div>
        <p className="font-medium text-gray-900">{label}</p>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
      <button
        onClick={onChange}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          checked ? "bg-blue-600" : "bg-gray-200"
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );
}

// Security Tab Component
function SecurityTab({ profile }: { profile: StaffProfile }) {
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleChangePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage("Password baru tidak cocok");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch("/api/v1/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password,
        }),
      });

      if (response.ok) {
        setMessage("Password berhasil diubah");
        setPasswordData({ current_password: "", new_password: "", confirm_password: "" });
        setShowPasswordForm(false);
      } else {
        const error = await response.json();
        setMessage(error.detail || "Gagal mengubah password");
      }
    } catch (error) {
      setMessage("Terjadi kesalahan saat mengubah password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Keamanan Akun</h3>

        <div className="space-y-4">
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Password</p>
                <p className="text-sm text-gray-600">Terakhir diubah: Tidak diketahui</p>
              </div>
              <button
                onClick={() => setShowPasswordForm(!showPasswordForm)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
              >
                <Key className="w-4 h-4 mr-2" />
                Ganti Password
              </button>
            </div>

            {showPasswordForm && (
              <div className="mt-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password Saat Ini
                  </label>
                  <input
                    type="password"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password Baru
                  </label>
                  <input
                    type="password"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Konfirmasi Password Baru
                  </label>
                  <input
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                {message && (
                  <p className={`text-sm ${message.includes("berhasil") ? "text-green-600" : "text-red-600"}`}>
                    {message}
                  </p>
                )}

                <div className="flex space-x-3">
                  <button
                    onClick={handleChangePassword}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? "Menyimpan..." : "Simpan"}
                  </button>
                  <button
                    onClick={() => {
                      setShowPasswordForm(false);
                      setPasswordData({ current_password: "", new_password: "", confirm_password: "" });
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Batal
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Autentikasi Dua Faktor (2FA)</p>
                <p className="text-sm text-gray-600">Tambahkan lapisan keamanan ekstra</p>
              </div>
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                Aktifkan 2FA
              </button>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Riwayat Login</h3>
        <div className="p-4 border border-gray-200 rounded-lg">
          <p className="text-sm text-gray-600">Riwayat login akan ditampilkan di sini</p>
        </div>
      </div>
    </div>
  );
}
