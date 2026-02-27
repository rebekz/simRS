"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  UserPlus,
  Search,
  ChevronRight,
  Plus,
  Clock,
  CheckCircle,
  Users,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function RegistrationDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  const stats = [
    { label: "Registrasi Hari Ini", value: 45, icon: UserPlus, color: "text-teal-600" },
    { label: "Menunggu", value: 8, icon: Clock, color: "text-orange-600" },
    { label: "Selesai", value: 37, icon: CheckCircle, color: "text-green-600" },
    { label: "Total Pasien", value: 1250, icon: Users, color: "text-blue-600" },
  ];

  const quickActions = [
    { label: "Pasien Baru", href: "/app/registration/new-patient", desc: "Daftarkan pasien baru" },
    { label: "Pasien Lama", href: "/app/registration/existing", desc: "Cari pasien terdaftar" },
    { label: "Antrian", href: "/app/queue", desc: "Lihat antrian pasien" },
  ];

  const recentRegistrations = [
    { id: "REG-001", patientName: "Ahmad Susanto", mrn: "MRN-001", type: "Rawat Jalan", time: "10:30", status: "completed" },
    { id: "REG-002", patientName: "Siti Rahayu", mrn: "MRN-002", type: "IGD", time: "10:15", status: "in_progress" },
    { id: "REG-003", patientName: "Budi Hartono", mrn: "MRN-003", type: "Rawat Inap", time: "09:45", status: "completed" },
    { id: "REG-004", patientName: "Dewi Sartika", mrn: "MRN-004", type: "Rawat Jalan", time: "09:30", status: "completed" },
  ];

  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
      return;
    }
    setLoading(false);
  }, [router]);

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      completed: "bg-green-100 text-green-700",
      in_progress: "bg-blue-100 text-blue-700",
    };
    const labels: Record<string, string> = {
      completed: "Selesai",
      in_progress: "Proses",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Registrasi</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <UserPlus className="h-6 w-6 mr-2 text-teal-600" />
          Dashboard Registrasi
        </h1>
        <p className="text-gray-600 mt-1">Pendaftaran pasien baru dan lama</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <stat.icon className={`h-8 w-8 ${stat.color}`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Aksi Cepat</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action) => (
              <Link
                key={action.href}
                href={action.href}
                className="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:border-teal-500 hover:bg-teal-50 transition-colors"
              >
                <div>
                  <p className="font-medium text-gray-900">{action.label}</p>
                  <p className="text-sm text-gray-500">{action.desc}</p>
                </div>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Registrations */}
      <Card>
        <CardHeader>
          <CardTitle>Registrasi Terbaru</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">ID</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tipe</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Waktu</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody>
                {recentRegistrations.map((reg) => (
                  <tr key={reg.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{reg.id}</td>
                    <td className="py-3 px-4">
                      <div>
                        <p className="text-gray-900">{reg.patientName}</p>
                        <p className="text-sm text-gray-500">{reg.mrn}</p>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-600">{reg.type}</td>
                    <td className="py-3 px-4 text-gray-600">{reg.time}</td>
                    <td className="py-3 px-4">{getStatusBadge(reg.status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
