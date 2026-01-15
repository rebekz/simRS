"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Layout } from "@/components/layout/Layout";
import { NotificationCenter } from "@/components/notifications/NotificationCenter";
import { User } from "@/types";

export default function StaffLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem("staff_access_token");
    if (!token && pathname !== "/app/login") {
      router.push("/app/login");
      setIsLoading(false);
    } else if (token) {
      // Fetch user info
      fetchUserInfo();
    } else {
      setIsLoading(false);
    }
  }, [pathname, router]);

  const fetchUserInfo = async () => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch("/api/v1/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser({
          id: userData.id || "",
          name: userData.first_name || userData.username || "User",
          email: userData.email || "",
          role: userData.role || "staff",
          avatar: userData.avatar,
          permissions: userData.permissions,
        });
      } else {
        // Token invalid, redirect to login
        localStorage.removeItem("staff_access_token");
        localStorage.removeItem("staff_refresh_token");
        router.push("/app/login");
      }
    } catch (error) {
      console.error("Failed to fetch user info:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem("staff_access_token");
      await fetch("/api/v1/auth/logout", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem("staff_access_token");
      localStorage.removeItem("staff_refresh_token");
      router.push("/app/login");
    }
  };

  // Don't show layout on login page
  if (pathname === "/app/login") {
    return <>{children}</>;
  }

  // Show loading state
  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Memuat...</p>
        </div>
      </div>
    );
  }

  // Use the Layout component for authenticated pages
  return <Layout user={user}>{children}</Layout>;
}
