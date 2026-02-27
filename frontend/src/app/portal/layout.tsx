"use client";

import { ReactNode } from "react";
import Link from "next/link";
import {
  Home,
  Calendar,
  FileText,
  CreditCard,
  User,
  Bell,
  Settings,
  LogOut,
} from "lucide-react";
import { usePathname } from "next/navigation";

export default function PortalLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const navigation = [
    { name: "Dashboard", href: "/portal/dashboard", icon: Home },
    { name: "Appointments", href: "/portal/appointments", icon: Calendar },
    { name: "Medical Records", href: "/portal/medical-records", icon: FileText },
    { name: "Billing", href: "/portal/billing", icon: CreditCard },
    { name: "Profile", href: "/portal/profile", icon: User },
    { name: "Settings", href: "/portal/settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg">
        <div className="p-6">
          <h1 className="text-xl font-bold text-teal-600">Patient Portal</h1>
          <p className="text-sm text-gray-500">SIMRS</p>
        </div>

        <nav className="mt-6 px-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors ${
                  isActive
                    ? "bg-teal-100 text-teal-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <item.icon className="h-5 w-5" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto px-4">
          <button className="flex items-center space-x-2 px-4 py-2 w-full text-red-600 hover:bg-red-50 rounded-lg transition-colors">
            <LogOut className="h-5 w-5" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 overflow-auto">
        {children}
      </main>
    </div>
  );
}
