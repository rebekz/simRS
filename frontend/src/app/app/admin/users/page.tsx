"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Users,
  Search,
  Plus,
  Edit,
  Trash2,
  ChevronRight,
  MoreVertical,
  Shield,
  Mail,
  Phone,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface User {
  id: string;
  username: string;
  fullName: string;
  email: string;
  phone: string;
  role: string;
  department: string;
  status: "active" | "inactive" | "suspended";
  lastLogin: string;
}

export default function UserManagementPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      // Simulate loading users
      setUsers([
        {
          id: "1",
          username: "admin",
          fullName: "Administrator",
          email: "admin@simrs.local",
          phone: "+62 812-0000-0001",
          role: "admin",
          department: "IT",
          status: "active",
          lastLogin: "2026-02-27 10:30:00",
        },
        {
          id: "2",
          username: "doctor1",
          fullName: "Dr. Ahmad Susanto",
          email: "doctor1@simrs.local",
          phone: "+62 812-0000-0002",
          role: "doctor",
          department: "Poli Umum",
          status: "active",
          lastLogin: "2026-02-27 09:15:00",
        },
        {
          id: "3",
          username: "nurse1",
          fullName: "Siti Nurhaliza",
          email: "nurse1@simrs.local",
          phone: "+62 812-0000-0003",
          role: "nurse",
          department: "IGD",
          status: "active",
          lastLogin: "2026-02-27 08:00:00",
        },
        {
          id: "4",
          username: "pharmacist1",
          fullName: "Budi Santoso",
          email: "pharmacist1@simrs.local",
          phone: "+62 812-0000-0004",
          role: "pharmacist",
          department: "Farmasi",
          status: "active",
          lastLogin: "2026-02-26 16:30:00",
        },
        {
          id: "5",
          username: "billing1",
          fullName: "Dewi Lestari",
          email: "billing1@simrs.local",
          phone: "+62 812-0000-0005",
          role: "billing",
          department: "Kasir",
          status: "active",
          lastLogin: "2026-02-27 07:45:00",
        },
      ]);
    } catch (error) {
      console.error("Failed to load users:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === "all" || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const getRoleBadge = (role: string) => {
    const roleStyles: Record<string, string> = {
      admin: "bg-purple-100 text-purple-700",
      doctor: "bg-blue-100 text-blue-700",
      nurse: "bg-green-100 text-green-700",
      pharmacist: "bg-orange-100 text-orange-700",
      billing: "bg-yellow-100 text-yellow-700",
      lab: "bg-pink-100 text-pink-700",
      radiology: "bg-indigo-100 text-indigo-700",
    };
    const roleLabels: Record<string, string> = {
      admin: "Admin",
      doctor: "Dokter",
      nurse: "Perawat",
      pharmacist: "Farmasis",
      billing: "Kasir",
      lab: "Lab",
      radiology: "Radiologi",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${roleStyles[role] || "bg-gray-100 text-gray-700"}`}>
        {roleLabels[role] || role}
      </span>
    );
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      active: "bg-green-100 text-green-700",
      inactive: "bg-gray-100 text-gray-700",
      suspended: "bg-red-100 text-red-700",
    };
    const labels: Record<string, string> = {
      active: "Aktif",
      inactive: "Tidak Aktif",
      suspended: "Ditangguhkan",
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">
            Dashboard
          </Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/admin/dashboard" className="hover:text-gray-700">
            Admin
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Manajemen Pengguna</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Manajemen Pengguna</h1>
            <p className="text-gray-600 mt-1">Kelola pengguna dan hak akses sistem</p>
          </div>
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            Tambah Pengguna
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari nama, username, atau email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">Semua Role</option>
              <option value="admin">Admin</option>
              <option value="doctor">Dokter</option>
              <option value="nurse">Perawat</option>
              <option value="pharmacist">Farmasis</option>
              <option value="billing">Kasir</option>
              <option value="lab">Lab</option>
              <option value="radiology">Radiologi</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="h-5 w-5 mr-2" />
            Daftar Pengguna ({filteredUsers.length})
          </CardTitle>
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
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Pengguna</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Role</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Departemen</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Login Terakhir</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="h-10 w-10 rounded-full bg-teal-100 flex items-center justify-center">
                            <span className="text-teal-700 font-medium">
                              {user.fullName.charAt(0)}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{user.fullName}</p>
                            <p className="text-sm text-gray-500">@{user.username}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">{getRoleBadge(user.role)}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{user.department}</td>
                      <td className="py-3 px-4">{getStatusBadge(user.status)}</td>
                      <td className="py-3 px-4 text-sm text-gray-500">{user.lastLogin}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Edit className="h-4 w-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-red-600 rounded-md hover:bg-red-50">
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
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
