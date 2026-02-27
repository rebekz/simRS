"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Pill,
  Search,
  ChevronRight,
  CheckCircle,
  Clock,
  AlertTriangle,
  User,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface MedicationTask {
  id: string;
  patientName: string;
  mrn: string;
  room: string;
  medication: string;
  dosage: string;
  route: string;
  scheduledTime: string;
  status: "pending" | "administered" | "missed" | "delayed";
  nurse: string | null;
  administeredAt: string | null;
  notes: string | null;
}

export default function NursingMedicationPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState<MedicationTask[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    loadMedications();
  }, []);

  const loadMedications = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setTasks([
        { id: "MED-001", patientName: "Ahmad Susanto", mrn: "MRN-001", room: "A-101", medication: "Paracetamol", dosage: "500mg", route: "Oral", scheduledTime: "08:00", status: "administered", nurse: "Siti N.", administeredAt: "08:05", notes: null },
        { id: "MED-002", patientName: "Siti Rahayu", mrn: "MRN-002", room: "B-205", medication: "Amoxicillin", dosage: "500mg", route: "IV", scheduledTime: "09:00", status: "pending", nurse: null, administeredAt: null, notes: null },
        { id: "MED-003", patientName: "Budi Hartono", mrn: "MRN-003", room: "A-103", medication: "Insulin Novorapid", dosage: "10 units", route: "SC", scheduledTime: "07:30", status: "delayed", nurse: null, administeredAt: null, notes: "Menunggu hasil lab gula darah" },
        { id: "MED-004", patientName: "Dewi Sartika", mrn: "MRN-004", room: "C-301", medication: "Metformin", dosage: "500mg", route: "Oral", scheduledTime: "07:00", status: "missed", nurse: null, administeredAt: null, notes: "Pasien menolak" },
        { id: "MED-005", patientName: "Eko Prasetyo", mrn: "MRN-005", room: "B-210", medication: "Omeprazole", dosage: "40mg", route: "IV", scheduledTime: "10:00", status: "pending", nurse: null, administeredAt: null, notes: null },
      ]);
    } catch (error) {
      console.error("Failed to load medications:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = tasks.filter((t) => {
    const matchesSearch = t.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.medication.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || t.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-700",
      administered: "bg-green-100 text-green-700",
      missed: "bg-red-100 text-red-700",
      delayed: "bg-orange-100 text-orange-700",
    };
    const labels: Record<string, string> = {
      pending: "Menunggu",
      administered: "Diberikan",
      missed: "Terlewat",
      delayed: "Tertunda",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const handleAdminister = (taskId: string) => {
    setTasks(tasks.map((t) =>
      t.id === taskId
        ? { ...t, status: "administered" as const, nurse: "Current Nurse", administeredAt: new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }) }
        : t
    ));
  };

  const stats = [
    { label: "Menunggu", value: tasks.filter((t) => t.status === "pending").length, color: "text-yellow-600" },
    { label: "Diberikan", value: tasks.filter((t) => t.status === "administered").length, color: "text-green-600" },
    { label: "Tertunda", value: tasks.filter((t) => t.status === "delayed").length, color: "text-orange-600" },
    { label: "Terlewat", value: tasks.filter((t) => t.status === "missed").length, color: "text-red-600" },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/nursing" className="hover:text-gray-700">Keperawatan</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Pemberian Obat</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Pill className="h-6 w-6 mr-2 text-teal-600" />
          Pemberian Obat
        </h1>
        <p className="text-gray-600 mt-1">Kelola jadwal dan dokumentasi pemberian obat</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">{stat.label}</p>
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari pasien atau obat..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">Semua Status</option>
              <option value="pending">Menunggu</option>
              <option value="administered">Diberikan</option>
              <option value="delayed">Tertunda</option>
              <option value="missed">Terlewat</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Medication List */}
      <Card>
        <CardHeader>
          <CardTitle>Jadwal Pemberian Obat ({filteredTasks.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Ruangan</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Obat</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Dosis/Route</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Jadwal</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTasks.map((task) => (
                    <tr key={task.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="h-8 w-8 rounded-full bg-teal-100 flex items-center justify-center">
                            <User className="h-4 w-4 text-teal-600" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{task.patientName}</p>
                            <p className="text-sm text-gray-500">{task.mrn}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600">{task.room}</td>
                      <td className="py-3 px-4 font-medium text-gray-900">{task.medication}</td>
                      <td className="py-3 px-4 text-gray-600">{task.dosage} / {task.route}</td>
                      <td className="py-3 px-4 text-gray-600">{task.scheduledTime}</td>
                      <td className="py-3 px-4">{getStatusBadge(task.status)}</td>
                      <td className="py-3 px-4 text-right">
                        {task.status === "pending" || task.status === "delayed" ? (
                          <Button variant="primary" size="sm" onClick={() => handleAdminister(task.id)}>
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Berikan
                          </Button>
                        ) : task.status === "administered" ? (
                          <span className="text-sm text-gray-500">
                            {task.nurse} @ {task.administeredAt}
                          </span>
                        ) : (
                          <span className="text-sm text-gray-500">{task.notes}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
