"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FileCode,
  Activity,
  ChevronRight,
  Search,
  Clock,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function CasemixDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  const stats = [
    { label: "Klaim Pending", value: 15, icon: Clock, color: "text-orange-600" },
    { label: "Klaim Selesai", value: 120, icon: CheckCircle, color: "text-green-600" },
    { label: "Perlu Review", value: 3, icon: AlertTriangle, color: "text-red-600" },
    { label: "Total Bulan Ini", value: 138, icon: Activity, color: "text-blue-600" },
  ];

  const quickActions = [
    { label: "Coding ICD-10", href: "/app/casemix/coding", desc: "Koding diagnosis dan tindakan" },
    { label: "Klaim BPJS", href: "/app/casemix/bpjs", desc: "Submit dan tracking klaim BPJS" },
    { label: "INA-CBG Grouper", href: "/app/casemix/grouper", desc: "Grouping kasus INA-CBG" },
  ];

  const recentClaims = [
    { id: "CLM-001", patient: "Ahmad Susanto", mrn: "MRN-001", cbg: "A-1-1-I", tarif: 2500000, status: "submitted" },
    { id: "CLM-002", patient: "Siti Rahayu", mrn: "MRN-002", cbg: "B-2-2-II", tarif: 3500000, status: "pending" },
    { id: "CLM-003", patient: "Budi Hartono", mrn: "MRN-003", cbg: "C-3-1-I", tarif: 1800000, status: "verified" },
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
      submitted: "bg-blue-100 text-blue-700",
      verified: "bg-green-100 text-green-700",
    };
    const labels: Record<string, string> = {
      pending: "Pending",
      submitted: "Terkirim",
      verified: "Terverifikasi",
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
          <span className="text-gray-900">Casemix</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <FileCode className="h-6 w-6 mr-2 text-teal-600" />
          Dashboard Casemix
        </h1>
        <p className="text-gray-600 mt-1">Coding, INA-CBG grouping, dan klaim BPJS</p>
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

      {/* Recent Claims */}
      <Card>
        <CardHeader>
          <CardTitle>Klaim Terbaru</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">ID Klaim</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pasien</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">INA-CBG</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Tarif</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody>
                {recentClaims.map((claim) => (
                  <tr key={claim.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{claim.id}</td>
                    <td className="py-3 px-4">
                      <div>
                        <p className="text-gray-900">{claim.patient}</p>
                        <p className="text-sm text-gray-500">{claim.mrn}</p>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono text-gray-600">{claim.cbg}</td>
                    <td className="py-3 px-4 text-right text-gray-600">Rp {claim.tarif.toLocaleString()}</td>
                    <td className="py-3 px-4">{getStatusBadge(claim.status)}</td>
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
