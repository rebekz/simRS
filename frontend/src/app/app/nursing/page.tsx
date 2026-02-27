"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Heart,
  Activity,
  Users,
  ClipboardList,
  ChevronRight,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function NursingDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  const stats = [
    { label: "Pasien Dirawat", value: 25, icon: Users, color: "text-blue-600" },
    { label: "Tugas Hari Ini", value: 48, icon: ClipboardList, color: "text-orange-600" },
    { label: "Tanda Vital Pending", value: 8, icon: Activity, color: "text-red-600" },
    { label: "Shift Aktif", value: 12, icon: Clock, color: "text-green-600" },
  ];

  const tasks = [
    { id: "1", patient: "Ahmad Susanto", room: "A-101", task: "Pemberian Obat", time: "10:00", status: "pending" },
    { id: "2", patient: "Siti Rahayu", room: "B-205", task: "Cek Tanda Vital", time: "10:30", status: "pending" },
    { id: "3", patient: "Budi Hartono", room: "A-103", task: "Infus", time: "11:00", status: "completed" },
    { id: "4", patient: "Dewi Sartika", room: "C-301", task: "Dressing Luka", time: "11:30", status: "pending" },
  ];

  const quickActions = [
    { label: "Tanda Vital", href: "/app/vitals", icon: Activity },
    { label: "Pemberian Obat", href: "/app/nursing/medication", icon: Heart },
    { label: "Catatan Keperawatan", href: "/app/nursing/notes", icon: ClipboardList },
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
      pending: "bg-yellow-100 text-yellow-700",
      completed: "bg-green-100 text-green-700",
    };
    const labels: Record<string, string> = {
      pending: "Menunggu",
      completed: "Selesai",
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
          <span className="text-gray-900">Keperawatan</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Heart className="h-6 w-6 mr-2 text-teal-600" />
          Dashboard Keperawatan
        </h1>
        <p className="text-gray-600 mt-1">Koordinasi dan dokumentasi asuhan keperawatan</p>
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
                <div className="flex items-center space-x-3">
                  <action.icon className="h-5 w-5 text-teal-600" />
                  <span className="font-medium text-gray-900">{action.label}</span>
                </div>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tasks */}
      <Card>
        <CardHeader>
          <CardTitle>Tugas Hari Ini</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Ruangan</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tugas</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Waktu</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{task.patient}</td>
                    <td className="py-3 px-4 text-gray-600">{task.room}</td>
                    <td className="py-3 px-4 text-gray-600">{task.task}</td>
                    <td className="py-3 px-4 text-gray-600">{task.time}</td>
                    <td className="py-3 px-4">{getStatusBadge(task.status)}</td>
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
