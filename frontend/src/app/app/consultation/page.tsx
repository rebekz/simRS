"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Stethoscope,
  Search,
  Filter,
  Clock,
  User,
  AlertTriangle,
  Play,
  Eye,
  Calendar,
  ChevronRight,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/Button";

interface WaitingPatient {
  id: number;
  queue_number: string;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  age: number;
  gender: string;
  chief_complaint: string;
  queue_time: string;
  priority: "normal" | "urgent" | "emergency";
  status: "waiting" | "in_progress" | "completed";
  department?: string;
  appointment_id?: number;
}

function ConsultationPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const department = searchParams.get("department") || "all";

  const [loading, setLoading] = useState(true);
  const [patients, setPatients] = useState<WaitingPatient[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("waiting");

  useEffect(() => {
    checkAuth();
    fetchWaitingPatients();
  }, [department, filterStatus]);

  const checkAuth = () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  };

  const fetchWaitingPatients = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) return;

      const params = new URLSearchParams();
      if (department !== "all") params.append("department", department);
      if (filterStatus !== "all") params.append("status", filterStatus);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/queue/consultation?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPatients(data.items || data || []);
      } else {
        // If API not available, show demo data
        setPatients(getDemoData());
      }
    } catch (error) {
      console.error("Failed to fetch waiting patients:", error);
      // Show demo data on error
      setPatients(getDemoData());
    } finally {
      setLoading(false);
    }
  };

  const getDemoData = (): WaitingPatient[] => [
    {
      id: 1,
      queue_number: "A001",
      patient_id: 101,
      patient_name: "Ahmad Sudirman",
      medical_record_number: "RM-2024-001234",
      age: 45,
      gender: "male",
      chief_complaint: "Sakit kepala dan demam sejak 3 hari",
      queue_time: "08:30",
      priority: "normal",
      status: "waiting",
      department: "Poli Umum",
    },
    {
      id: 2,
      queue_number: "A002",
      patient_id: 102,
      patient_name: "Siti Rahayu",
      medical_record_number: "RM-2024-001235",
      age: 32,
      gender: "female",
      chief_complaint: "Batuk dan sesak napas",
      queue_time: "08:45",
      priority: "normal",
      status: "waiting",
      department: "Poli Umum",
    },
    {
      id: 3,
      queue_number: "A003",
      patient_id: 103,
      patient_name: "Budi Santoso",
      medical_record_number: "RM-2024-001236",
      age: 58,
      gender: "male",
      chief_complaint: "Nyeri dada dan keringat dingin",
      queue_time: "09:00",
      priority: "urgent",
      status: "waiting",
      department: "Poli Jantung",
    },
    {
      id: 4,
      queue_number: "A004",
      patient_id: 104,
      patient_name: "Dewi Lestari",
      medical_record_number: "RM-2024-001237",
      age: 28,
      gender: "female",
      chief_complaint: "Kontrol kehamilan 32 minggu",
      queue_time: "09:15",
      priority: "normal",
      status: "in_progress",
      department: "Poli KIA",
    },
    {
      id: 5,
      queue_number: "C001",
      patient_id: 105,
      patient_name: "Anak Putra",
      medical_record_number: "RM-2024-001238",
      age: 5,
      gender: "male",
      chief_complaint: "Demam tinggi dan kejang",
      queue_time: "09:20",
      priority: "emergency",
      status: "waiting",
      department: "Poli Anak",
    },
  ];

  const handleStartConsultation = (patient: WaitingPatient) => {
    router.push(`/app/consultation/room/${patient.id}?patient_id=${patient.patient_id}`);
  };

  const handleViewPatient = (patient: WaitingPatient) => {
    router.push(`/app/patients/${patient.patient_id}`);
  };

  const filteredPatients = patients.filter((patient) => {
    const matchesSearch =
      patient.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.medical_record_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.queue_number.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesPriority = filterPriority === "all" || patient.priority === filterPriority;

    return matchesSearch && matchesPriority;
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "emergency":
        return "bg-red-100 text-red-800 border-red-200";
      case "urgent":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "in_progress":
        return "bg-blue-100 text-blue-800";
      case "completed":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-600";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "in_progress":
        return "Sedang Diperiksa";
      case "completed":
        return "Selesai";
      default:
        return "Menunggu";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Stethoscope className="h-7 w-7 mr-2 text-blue-600" />
            Konsultasi Rawat Jalan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Daftar pasien yang menunggu konsultasi
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Link
            href="/app/consultation/notes"
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Eye className="h-4 w-4 mr-2" />
            Lihat Catatan
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Menunggu</p>
              <p className="text-2xl font-bold text-gray-900">
                {patients.filter((p) => p.status === "waiting").length}
              </p>
            </div>
            <Clock className="h-8 w-8 text-yellow-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Sedang Diperiksa</p>
              <p className="text-2xl font-bold text-blue-600">
                {patients.filter((p) => p.status === "in_progress").length}
              </p>
            </div>
            <Activity className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Prioritas Tinggi</p>
              <p className="text-2xl font-bold text-red-600">
                {patients.filter((p) => p.priority === "urgent" || p.priority === "emergency").length}
              </p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Hari Ini</p>
              <p className="text-2xl font-bold text-gray-900">{patients.length}</p>
            </div>
            <User className="h-8 w-8 text-gray-500" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Cari nama, No. RM, atau nomor antrian..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">Semua Prioritas</option>
                <option value="emergency">Darurat</option>
                <option value="urgent">Urgent</option>
                <option value="normal">Normal</option>
              </select>
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="waiting">Menunggu</option>
              <option value="in_progress">Sedang Diperiksa</option>
              <option value="all">Semua Status</option>
            </select>
          </div>
        </div>
      </div>

      {/* Patient List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredPatients.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Stethoscope className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak Ada Pasien</h3>
          <p className="text-gray-500">
            {searchQuery || filterPriority !== "all"
              ? "Tidak ada pasien yang cocok dengan filter Anda"
              : "Tidak ada pasien yang menunggu konsultasi saat ini"}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Antrian
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pasien
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Keluhan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Waktu
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Aksi
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPatients.map((patient) => (
                <tr
                  key={patient.id}
                  className={`hover:bg-gray-50 ${
                    patient.priority === "emergency" ? "bg-red-50" : ""
                  }`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-lg font-bold text-blue-600">
                        {patient.queue_number}
                      </span>
                      <span
                        className={`ml-2 px-2 py-1 text-xs rounded-full border ${getPriorityColor(
                          patient.priority
                        )}`}
                      >
                        {patient.priority === "emergency"
                          ? "DARURAT"
                          : patient.priority === "urgent"
                          ? "URGENT"
                          : "Normal"}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                        <User className="h-5 w-5 text-gray-500" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {patient.patient_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {patient.medical_record_number} | {patient.age} th,{" "}
                          {patient.gender === "male" ? "L" : "P"}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate">
                      {patient.chief_complaint}
                    </div>
                    {patient.department && (
                      <div className="text-xs text-gray-500">{patient.department}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{patient.queue_time}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                        patient.status
                      )}`}
                    >
                      {getStatusLabel(patient.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => handleViewPatient(patient)}
                        className="text-gray-600 hover:text-gray-900 px-2 py-1 rounded hover:bg-gray-100"
                        title="Lihat Detail Pasien"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      {patient.status === "waiting" && (
                        <Button
                          onClick={() => handleStartConsultation(patient)}
                          variant="primary"
                          className="inline-flex items-center"
                        >
                          <Play className="h-4 w-4 mr-1" />
                          Mulai
                        </Button>
                      )}
                      {patient.status === "in_progress" && (
                        <Button
                          onClick={() => handleStartConsultation(patient)}
                          variant="secondary"
                          className="inline-flex items-center"
                        >
                          <ChevronRight className="h-4 w-4 mr-1" />
                          Lanjutkan
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Quick Links */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Akses Cepat</h3>
        <div className="flex flex-wrap gap-2">
          <Link
            href="/app/patients"
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 flex items-center"
          >
            <Users className="h-4 w-4 mr-2" />
            Daftar Pasien
          </Link>
          <Link
            href="/app/queue"
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 flex items-center"
          >
            <Activity className="h-4 w-4 mr-2" />
            Manajemen Antrian
          </Link>
          <Link
            href="/app/appointments"
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 flex items-center"
          >
            <Calendar className="h-4 w-4 mr-2" />
            Janji Temu
          </Link>
          <Link
            href="/app/lab"
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 flex items-center"
          >
            <TestTube className="h-4 w-4 mr-2" />
            Laboratorium
          </Link>
        </div>
      </div>
    </div>
  );
}

// Import missing icons
import { TestTube, Users } from "lucide-react";

export default function ConsultationPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      }
    >
      <ConsultationPageContent />
    </Suspense>
  );
}
