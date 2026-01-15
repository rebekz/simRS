"use client";

/**
 * Notification Center Component - EPIC-022: Notification System
 *
 * Centralized notification display and management for staff members including:
 * - Real-time notification list with filtering
 * - Mark as read/unread functionality
 * - Notification type filtering
 * - Delete notifications
 * - Notification count badge
 */

import { useState, useEffect } from "react";
import {
  Bell,
  X,
  Check,
  AlertCircle,
  Info,
  CheckCircle,
  Clock,
  Trash2,
  Filter,
  ChevronDown,
} from "lucide-react";

// Types
export interface Notification {
  id: number;
  user_id: number;
  type: NotificationType;
  channel: NotificationChannel;
  title: string;
  message: string;
  data?: Record<string, any>;
  priority: NotificationPriority;
  status: NotificationStatus;
  created_at: string;
  read_at?: string;
  expires_at?: string;
  action_url?: string;
  action_label?: string;
}

export type NotificationType =
  | "appointment_reminder"
  | "prescription_ready"
  | "lab_result_ready"
  | "radiology_result_ready"
  | "critical_lab_value"
  | "payment_reminder"
  | "system_alert"
  | "system_update"
  | "queue_update"
  | "message"
  | "announcement";

export type NotificationChannel = "email" | "sms" | "whatsapp" | "push" | "in_app";

export type NotificationPriority = "low" | "normal" | "high" | "urgent";

export type NotificationStatus = "pending" | "sent" | "delivered" | "failed" | "read";

interface NotificationCenterProps {
  onNotificationClick?: (notification: Notification) => void;
  className?: string;
}

export function NotificationCenter({
  onNotificationClick,
  className = "",
}: NotificationCenterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "unread" | "urgent">("all");
  const [typeFilter, setTypeFilter] = useState<NotificationType | "all">("all");

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen, filter, typeFilter]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      if (filter !== "all") params.append("status", filter === "unread" ? "unread" : "all");
      if (typeFilter !== "all") params.append("type", typeFilter);

      const response = await fetch(
        `/api/v1/notifications?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.items || []);
      }
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const token = localStorage.getItem("staff_access_token");
      await fetch(`/api/v1/notifications/${notificationId}/read`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notificationId
            ? { ...n, status: "read" as NotificationStatus, read_at: new Date().toISOString() }
            : n
        )
      );
    } catch (error) {
      console.error("Failed to mark as read:", error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const token = localStorage.getItem("staff_access_token");
      await fetch("/api/v1/notifications/mark-all-read", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setNotifications((prev) =>
        prev.map((n) => ({
          ...n,
          status: "read" as NotificationStatus,
          read_at: new Date().toISOString(),
        }))
      );
    } catch (error) {
      console.error("Failed to mark all as read:", error);
    }
  };

  const handleDelete = async (notificationId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const token = localStorage.getItem("staff_access_token");
      await fetch(`/api/v1/notifications/${notificationId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setNotifications((prev) => prev.filter((n) => n.id !== notificationId));
    } catch (error) {
      console.error("Failed to delete notification:", error);
    }
  };

  const unreadCount = notifications.filter((n) => n.status === "pending" || n.status === "sent").length;

  const getPriorityColor = (priority: NotificationPriority) => {
    switch (priority) {
      case "urgent":
        return "bg-red-50 border-red-200 text-red-800";
      case "high":
        return "bg-orange-50 border-orange-200 text-orange-800";
      case "normal":
        return "bg-blue-50 border-blue-200 text-blue-800";
      case "low":
        return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  const getTypeIcon = (type: NotificationType) => {
    switch (type) {
      case "critical_lab_value":
      case "system_alert":
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      case "appointment_reminder":
      case "prescription_ready":
      case "lab_result_ready":
      case "radiology_result_ready":
        return <Clock className="h-5 w-5 text-blue-600" />;
      case "payment_reminder":
        return <Info className="h-5 w-5 text-yellow-600" />;
      default:
        return <Bell className="h-5 w-5 text-gray-600" />;
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000 / 60);

    if (diff < 1) return "Baru saja";
    if (diff < 60) return `${diff} menit yang lalu`;
    if (diff < 1440) return `${Math.floor(diff / 60)} jam yang lalu`;
    if (diff < 10080) return `${Math.floor(diff / 1440)} hari yang lalu`;
    return date.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "short",
      year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    });
  };

  return (
    <div className={`relative ${className}`}>
      {/* Notification Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown Panel */}
          <div className="absolute right-0 top-12 z-50 w-96 bg-white rounded-lg shadow-xl border border-gray-200 max-h-[600px] flex flex-col">
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900">Notifikasi</h3>
                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllAsRead}
                      className="text-sm text-blue-600 hover:text-blue-700"
                    >
                      Tandai semua dibaca
                    </button>
                  )}
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    <X className="h-5 w-5 text-gray-500" />
                  </button>
                </div>
              </div>

              {/* Filters */}
              <div className="flex items-center space-x-2">
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value as any)}
                  className="text-sm border border-gray-300 rounded-md px-2 py-1"
                >
                  <option value="all">Semua</option>
                  <option value="unread">Belum Dibaca</option>
                  <option value="urgent">Urgent</option>
                </select>

                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value as any)}
                  className="text-sm border border-gray-300 rounded-md px-2 py-1"
                >
                  <option value="all">Semua Tipe</option>
                  <option value="appointment_reminder">Janji Temu</option>
                  <option value="critical_lab_value">Lab Kritis</option>
                  <option value="system_alert">Sistem</option>
                  <option value="message">Pesan</option>
                </select>
              </div>
            </div>

            {/* Notifications List */}
            <div className="flex-1 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-gray-500">
                  <Bell className="h-12 w-12 mb-2 text-gray-400" />
                  <p>Tidak ada notifikasi</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {notifications.map((notification) => (
                    <NotificationItem
                      key={notification.id}
                      notification={notification}
                      onMarkAsRead={handleMarkAsRead}
                      onDelete={handleDelete}
                      onClick={() => {
                        if (onNotificationClick) {
                          onNotificationClick(notification);
                        }
                        if (notification.action_url) {
                          window.location.href = notification.action_url;
                        }
                        setIsOpen(false);
                      }}
                      getPriorityColor={getPriorityColor}
                      getTypeIcon={getTypeIcon}
                      formatTime={formatTime}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-gray-200">
              <button
                onClick={() => {
                  window.location.href = "/app/notifications";
                }}
                className="w-full text-center text-sm text-blue-600 hover:text-blue-700"
              >
                Lihat Semua Notifikasi
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Notification Item Component
interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: number, e: React.MouseEvent) => void;
  onDelete: (id: number, e: React.MouseEvent) => void;
  onClick: () => void;
  getPriorityColor: (priority: NotificationPriority) => string;
  getTypeIcon: (type: NotificationType) => React.ReactNode;
  formatTime: (date: string) => string;
}

function NotificationItem({
  notification,
  onMarkAsRead,
  onDelete,
  onClick,
  getPriorityColor,
  getTypeIcon,
  formatTime,
}: NotificationItemProps) {
  const isUnread = notification.status === "pending" || notification.status === "sent";

  return (
    <div
      onClick={onClick}
      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
        isUnread ? "bg-blue-50" : ""
      }`}
    >
      <div className="flex items-start space-x-3">
        {/* Icon */}
        <div className="flex-shrink-0 mt-0.5">{getTypeIcon(notification.type)}</div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p
                className={`text-sm font-medium ${
                  isUnread ? "text-gray-900" : "text-gray-700"
                }`}
              >
                {notification.title}
              </p>
              <p
                className={`text-sm mt-0.5 ${
                  isUnread ? "text-gray-700" : "text-gray-600"
                }`}
              >
                {notification.message}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {formatTime(notification.created_at)}
              </p>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-1 ml-2">
              {isUnread && (
                <button
                  onClick={(e) => onMarkAsRead(notification.id, e)}
                  className="p-1 hover:bg-gray-200 rounded"
                  title="Tandai dibaca"
                >
                  <Check className="h-4 w-4 text-gray-600" />
                </button>
              )}
              <button
                onClick={(e) => onDelete(notification.id, e)}
                className="p-1 hover:bg-red-100 rounded"
                title="Hapus"
              >
                <Trash2 className="h-4 w-4 text-gray-600 hover:text-red-600" />
              </button>
            </div>
          </div>

          {/* Priority Badge */}
          {notification.priority !== "normal" && (
            <span
              className={`inline-block mt-2 px-2 py-0.5 text-xs font-medium rounded ${getPriorityColor(
                notification.priority
              )}`}
            >
              {notification.priority === "urgent" && "⚠️ "}
              {notification.priority.charAt(0).toUpperCase() +
                notification.priority.slice(1)}
            </span>
          )}

          {/* Action Button */}
          {notification.action_label && notification.action_url && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                window.location.href = notification.action_url!;
              }}
              className="mt-2 text-sm text-blue-600 hover:text-blue-700"
            >
              {notification.action_label} →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// Notification List Page Component
export function NotificationListPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "unread" | "read">("all");
  const [typeFilter, setTypeFilter] = useState<NotificationType | "all">("all");

  useEffect(() => {
    fetchNotifications();
  }, [filter, typeFilter]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      if (filter !== "all") params.append("status", filter);
      if (typeFilter !== "all") params.append("type", typeFilter);

      const response = await fetch(
        `/api/v1/notifications?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.items || []);
      }
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      await fetch(`/api/v1/notifications/${notificationId}/read`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notificationId
            ? { ...n, status: "read" as NotificationStatus, read_at: new Date().toISOString() }
            : n
        )
      );
    } catch (error) {
      console.error("Failed to mark as read:", error);
    }
  };

  const handleDelete = async (notificationId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      await fetch(`/api/v1/notifications/${notificationId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setNotifications((prev) => prev.filter((n) => n.id !== notificationId));
    } catch (error) {
      console.error("Failed to delete notification:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Notifikasi</h1>
        <p className="text-sm text-gray-600 mt-1">Kelola notifikasi Anda</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filter:</span>
          </div>

          <div className="flex space-x-2">
            <button
              onClick={() => setFilter("all")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                filter === "all"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Semua
            </button>
            <button
              onClick={() => setFilter("unread")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                filter === "unread"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Belum Dibaca
            </button>
            <button
              onClick={() => setFilter("read")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                filter === "read"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Dibaca
            </button>
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as any)}
            className="ml-auto text-sm border border-gray-300 rounded-md px-3 py-1.5"
          >
            <option value="all">Semua Tipe</option>
            <option value="appointment_reminder">Janji Temu</option>
            <option value="critical_lab_value">Lab Kritis</option>
            <option value="system_alert">Sistem</option>
            <option value="message">Pesan</option>
          </select>
        </div>
      </div>

      {/* Notifications List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : notifications.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Bell className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada notifikasi</h3>
          <p className="text-gray-600">
            {filter === "unread"
              ? "Tidak ada notifikasi yang belum dibaca"
              : "Belum ada notifikasi"}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow divide-y divide-gray-100">
          {notifications.map((notification) => (
            <NotificationListItem
              key={notification.id}
              notification={notification}
              onMarkAsRead={handleMarkAsRead}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Notification List Item Component
function NotificationListItem({
  notification,
  onMarkAsRead,
  onDelete,
}: {
  notification: Notification;
  onMarkAsRead: (id: number) => void;
  onDelete: (id: number) => void;
}) {
  const isUnread = notification.status === "pending" || notification.status === "sent";

  const getPriorityColor = (priority: NotificationPriority) => {
    switch (priority) {
      case "urgent":
        return "bg-red-100 text-red-800";
      case "high":
        return "bg-orange-100 text-orange-800";
      case "normal":
        return "bg-blue-100 text-blue-800";
      case "low":
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className={`p-6 ${isUnread ? "bg-blue-50" : ""}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3
              className={`text-lg font-semibold ${
                isUnread ? "text-gray-900" : "text-gray-700"
              }`}
            >
              {notification.title}
            </h3>
            {notification.priority !== "normal" && (
              <span
                className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(
                  notification.priority
                )}`}
              >
                {notification.priority === "urgent" && "⚠️ "}
                {notification.priority.charAt(0).toUpperCase() +
                  notification.priority.slice(1)}
              </span>
            )}
            {isUnread && (
              <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
                Baru
              </span>
            )}
          </div>

          <p className="text-gray-700 mb-2">{notification.message}</p>

          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <span>{new Date(notification.created_at).toLocaleString("id-ID")}</span>
            <span>•</span>
            <span className="capitalize">{notification.type.replace(/_/g, " ")}</span>
            {notification.read_at && (
              <>
                <span>•</span>
                <span>Dibaca {new Date(notification.read_at).toLocaleString("id-ID")}</span>
              </>
            )}
          </div>

          {notification.action_url && notification.action_label && (
            <button
              onClick={() => (window.location.href = notification.action_url!)}
              className="mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {notification.action_label} →
            </button>
          )}
        </div>

        <div className="flex items-center space-x-2 ml-4">
          {isUnread && (
            <button
              onClick={() => onMarkAsRead(notification.id)}
              className="p-2 hover:bg-gray-100 rounded-lg"
              title="Tandai dibaca"
            >
              <CheckCircle className="h-5 w-5 text-gray-600" />
            </button>
          )}
          <button
            onClick={() => onDelete(notification.id)}
            className="p-2 hover:bg-red-100 rounded-lg"
            title="Hapus"
          >
            <Trash2 className="h-5 w-5 text-gray-600 hover:text-red-600" />
          </button>
        </div>
      </div>
    </div>
  );
}
