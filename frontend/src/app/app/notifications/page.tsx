"use client";

/**
 * Staff Notifications Page - EPIC-022: Notification System
 *
 * Full-page notification management for staff members
 */

import { NotificationCenter } from "@/components/notifications/NotificationCenter";

export default function NotificationsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifikasi</h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola notifikasi Anda
          </p>
        </div>
      </div>

      {/* Notifications will be rendered here */}
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">
          Fitur notifikasi lengkap akan ditampilkan di sini.
        </p>
      </div>
    </div>
  );
}
