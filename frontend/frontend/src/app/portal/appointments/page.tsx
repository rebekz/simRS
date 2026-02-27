"use client";

import { useState } from "react";
import Link from "next/link";
import { Calendar, Plus, ChevronRight, Clock, Search } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function PortalAppointmentsPage() {
  const [view, setView] = useState<"upcoming" | "past">("upcoming");

  const appointments = [
    { id: "1", doctor: "Dr. Ahmad Yusuf", date: "2026-03-01", time: "09:00", department: "Poli Umum", status: "confirmed" },
    { id: "2", doctor: "Dr. Siti Rahayu", date: "2026-03-05", time: "14:00", department: "Poli Jantung", status: "confirmed" },
    { id: "3", doctor: "Dr. Budi Santoso", date: "2026-03-10", time: "10:00", department: "Poli Anak", status: "pending" },
    { id: "4", doctor: "Dr. Dewi Lestari", date: "2026-02-15", time: "11:00", department: "Poli Kulit", status: "completed" },
  { id: "5", doctor: "Dr. Ahmad Yusuf", date: "2026-02-20", time: "15:00", department: "Poli Umum", status: "completed" },
  ];

  const filteredAppointments = appointments.filter((a) =>
    view === "upcoming" ? a.status !== "completed" : a.status === "completed"
  );

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/portal/dashboard" className="hover:text-gray-700">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Janji Temu</span>
        </div>
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Janji Temu</h1>
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            Buat Janji Baru
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex space-x-2">
              <button onClick={() => setView("upcoming")} className={"px-4 py-2 rounded-lg font-medium " + (view === "upcoming" ? "bg-teal-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200")}>Mendatang</button>
              <button onClick={() => setView("past")} className={"px-4 py-2 rounded-lg font-medium " + (view === "past" ? "bg-teal-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200")}>Selesai</button>
            </div>
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input type="text" placeholder="Cari janji temu..." className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500" />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {filteredAppointments.map((apt) => (
          <Card key={apt.id}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="p-3 bg-teal-100 rounded-lg">
                    <Calendar className="h-6 w-6 text-teal-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{apt.doctor}</h3>
                    <p className="text-gray-500">{apt.department}</p>
                    <div className="flex items-center mt-2 text-sm text-gray-500">
                      <Clock className="h-4 w-4 mr-1" />
                      {apt.date} at {apt.time}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={"px-2 py-1 text-xs font-medium rounded-full " + (apt.status === "confirmed" ? "bg-green-100 text-green-700" : apt.status === "pending" ? "bg-yellow-100 text-yellow-700" : "bg-gray-100 text-gray-700")}>
                    {apt.status === "confirmed" ? "Terkonfirmasi" : apt.status === "pending" ? "Menunggu" : "Selesai"}
                  </span>
                  <Button variant="secondary" size="sm">Detail</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
