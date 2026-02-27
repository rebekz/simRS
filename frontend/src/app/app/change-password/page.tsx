"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Alert } from "@/components/ui/Alert";
import { Loader2, KeyRound, CheckCircle2 } from "lucide-react";

export default function ChangePasswordPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const validateForm = () => {
    if (!formData.current_password) {
      setError("Current password is required");
      return false;
    }
    if (!formData.new_password) {
      setError("New password is required");
      return false;
    }
    if (formData.new_password.length < 8) {
      setError("New password must be at least 8 characters");
      return false;
    }
    if (formData.new_password !== formData.confirm_password) {
      setError("Passwords do not match");
      return false;
    }
    if (formData.current_password === formData.new_password) {
      setError("New password must be different from current password");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("staff_access_token");

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/change-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            current_password: formData.current_password,
            new_password: formData.new_password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to change password");
      }

      setSuccess(true);

      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        router.push("/app/dashboard");
      }, 2000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    router.push("/app/dashboard");
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
        <Card className="w-full max-w-md p-6">
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="rounded-full bg-green-100 p-3">
              <CheckCircle2 className="h-8 w-8 text-green-600" />
            </div>
            <h2 className="text-xl font-semibold text-center">
              Password Changed Successfully
            </h2>
            <p className="text-gray-500 text-center">
              Your password has been updated. Redirecting to dashboard...
            </p>
            <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <Card className="w-full max-w-md">
        <div className="p-6 space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="rounded-full bg-blue-100 p-3">
              <KeyRound className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-center">
            Change Password
          </h2>
          <p className="text-gray-500 text-center">
            Please update your password to continue
          </p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="px-6 pb-4 space-y-4">
            {error && (
              <Alert variant="error">
                {error}
              </Alert>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="current_password">
                Current Password
              </label>
              <input
                id="current_password"
                name="current_password"
                type="password"
                value={formData.current_password}
                onChange={handleChange}
                placeholder="Enter current password"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="new_password">
                New Password
              </label>
              <input
                id="new_password"
                name="new_password"
                type="password"
                value={formData.new_password}
                onChange={handleChange}
                placeholder="Enter new password"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <p className="text-xs text-gray-500">
                Password must be at least 8 characters
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="confirm_password">
                Confirm New Password
              </label>
              <input
                id="confirm_password"
                name="confirm_password"
                type="password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="Confirm new password"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>
          <div className="p-6 pt-2 flex flex-col space-y-3">
            <Button type="submit" variant="primary" className="w-full" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Change Password
            </Button>
            <Button
              type="button"
              variant="secondary"
              className="w-full"
              onClick={handleSkip}
            >
              Skip for now
            </Button>
            <Link
              href="/app/login"
              className="text-sm text-gray-500 hover:text-blue-600 text-center"
            >
              Back to login
            </Link>
          </div>
        </form>
      </Card>
    </div>
  );
}
