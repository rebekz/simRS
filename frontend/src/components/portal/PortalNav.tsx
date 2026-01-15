"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { ReactNode } from "react";

interface PortalLayoutProps {
  children: ReactNode;
}

interface NavItem {
  label: string;
  labelId: string;
  href: string;
  icon: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", labelId: "Beranda", href: "/portal/dashboard", icon: "🏠" },
  { label: "Health Records", labelId: "Rekam Medis", href: "/portal/health-record", icon: "📋" },
  { label: "Appointments", labelId: "Janji Temu", href: "/portal/appointments", icon: "📅" },
  { label: "Prescriptions", labelId: "Resep", href: "/portal/prescriptions", icon: "💊" },
  { label: "Lab Results", labelId: "Hasil Lab", href: "/portal/lab-results", icon: "🔬" },
  { label: "Radiology", labelId: "Radiologi", href: "/portal/radiology", icon: "📷" },
  { label: "Billing", labelId: "Tagihan", href: "/portal/billing", icon: "💳" },
  { label: "Messages", labelId: "Pesan", href: "/portal/messages", icon: "✉️" },
  { label: "Medical Records", labelId: "Dokumen Medis", href: "/portal/medical-records", icon: "📁" },
  { label: "Vaccinations", labelId: "Vaksinasi", href: "/portal/vaccinations", icon: "💉" },
  { label: "Account", labelId: "Akun", href: "/portal/account", icon: "⚙️" },
  { label: "Notifications", labelId: "Notifikasi", href: "/portal/notifications/preferences", icon: "🔔" },
];

export default function PortalNav() {
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    localStorage.removeItem("portal_access_token");
    localStorage.removeItem("portal_refresh_token");
    localStorage.removeItem("portal_user");
    router.push("/portal/login");
  };

  const isActive = (href: string) => {
    if (href === "/portal/dashboard") {
      return pathname === "/portal/dashboard";
    }
    return pathname.startsWith(href);
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/portal/dashboard" className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold text-indigo-600">SIMRS</span>
              <span className="ml-2 text-sm text-gray-600 hidden sm:inline">Patient Portal</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-1">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={
                  isActive(item.href)
                    ? "inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors bg-indigo-50 text-indigo-700"
                    : "inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                }
                title={item.labelId}
              >
                <span className="mr-1">{item.icon}</span>
                <span className="hidden lg:inline">{item.label}</span>
              </Link>
            ))}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <button
              onClick={handleLogout}
              className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden pb-3">
          <div className="flex overflow-x-auto space-x-1 py-2">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={
                  isActive(item.href)
                    ? "inline-flex items-center px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors bg-indigo-50 text-indigo-700"
                    : "inline-flex items-center px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors text-gray-700 hover:bg-gray-50"
                }
              >
                <span className="mr-1">{item.icon}</span>
                <span>{item.labelId}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
