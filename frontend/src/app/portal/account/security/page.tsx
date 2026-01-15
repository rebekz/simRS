"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface PasswordChangeForm {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface SecurityInfo {
  email_verified: boolean;
  phone_verified: boolean;
  last_login: string | null;
  last_password_change: string | null;
  active_sessions: number;
  mfa_enabled: boolean;
}

export default function SecuritySettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [changingPassword, setChangingPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [securityInfo, setSecurityInfo] = useState<SecurityInfo | null>(null);
  const [passwordForm, setPasswordForm] = useState<PasswordChangeForm>({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string>>({});
  const [passwordStrength, setPasswordStrength] = useState<"weak" | "medium" | "strong" | null>(null);

  useEffect(() => {
    checkAuth();
    fetchSecurityInfo();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchSecurityInfo = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/account/security", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.status === 401) {
        router.push("/portal/login");
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setSecurityInfo(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load security information");
    } finally {
      setLoading(false);
    }
  };

  const checkPasswordStrength = (password: string): "weak" | "medium" | "strong" => {
    if (password.length < 8) return "weak";
    
    let score = 0;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 2) return "weak";
    if (score <= 3) return "medium";
    return "strong";
  };

  const handlePasswordChange = (field: keyof PasswordChangeForm, value: string) => {
    setPasswordForm((prev) => ({ ...prev, [field]: value }));
    
    // Clear error for this field
    if (passwordErrors[field]) {
      setPasswordErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }

    // Update password strength indicator
    if (field === "new_password") {
      setPasswordStrength(checkPasswordStrength(value));
    }
  };

  const validatePasswordForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!passwordForm.current_password) {
      errors.current_password = "Current password is required";
    }

    if (!passwordForm.new_password) {
      errors.new_password = "New password is required";
    } else if (passwordForm.new_password.length < 12) {
      errors.new_password = "Password must be at least 12 characters";
    } else if (passwordForm.new_password === passwordForm.current_password) {
      errors.new_password = "New password must be different from current password";
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:'\\|,.<>?])/.test(passwordForm.new_password)) {
      errors.new_password = "Password must contain uppercase, lowercase, number, and special character";
    }

    if (!passwordForm.confirm_password) {
      errors.confirm_password = "Please confirm your new password";
    } else if (passwordForm.new_password !== passwordForm.confirm_password) {
      errors.confirm_password = "Passwords do not match";
    }

    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmitPasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage(null);

    if (!validatePasswordForm()) {
      return;
    }

    setChangingPassword(true);
    setError(null);

    try {
      const token = localStorage.getItem("portal_access_token");
      const response = await fetch("/api/v1/portal/account/change-password", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password,
        }),
      });

      if (response.status === 401) {
        setError("Current password is incorrect");
        setPasswordErrors({ current_password: "Incorrect password" });
        return;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to change password" }));
        throw new Error(errorData.detail || "Failed to change password");
      }

      // Clear form
      setPasswordForm({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
      setPasswordStrength(null);
      setSuccessMessage("Password changed successfully!");
      
      // Refresh security info
      await fetchSecurityInfo();
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to change password");
    } finally {
      setChangingPassword(false);
    }
  };

  const getPasswordStrengthColor = () => {
    switch (passwordStrength) {
      case "weak": return "bg-red-500";
      case "medium": return "bg-yellow-500";
      case "strong": return "bg-green-500";
      default: return "bg-gray-200";
    }
  };

  const getPasswordStrengthText = () => {
    switch (passwordStrength) {
      case "weak": return "Weak";
      case "medium": return "Medium";
      case "strong": return "Strong";
      default: return "";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading security settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link href="/portal/account" className="text-indigo-600 hover:underline text-sm">
            ← Back to Account Settings
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">Security Settings</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex">
              <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-green-800">{successMessage}</p>
            </div>
          </div>
        )}

        {/* Security Overview */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Security Overview</h2>
          </div>
          <div className="p-6">
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center justify-between py-2">
                <dt className="text-sm font-medium text-gray-500">Email Verified</dt>
                <dd className="mt-1">
                  {securityInfo?.email_verified ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l3.293-3.293a1 1 0 011.414 1.414l-4 4z" clipRule="evenodd" />
                      </svg>
                      Verified
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      Not Verified
                    </span>
                  )}
                </dd>
              </div>

              <div className="flex items-center justify-between py-2">
                <dt className="text-sm font-medium text-gray-500">Phone Verified</dt>
                <dd className="mt-1">
                  {securityInfo?.phone_verified ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l3.293-3.293a1 1 0 011.414 1.414l-4 4z" clipRule="evenodd" />
                      </svg>
                      Verified
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      Not Verified
                    </span>
                  )}
                </dd>
              </div>

              <div className="flex items-center justify-between py-2">
                <dt className="text-sm font-medium text-gray-500">Two-Factor Authentication</dt>
                <dd className="mt-1">
                  {securityInfo?.mfa_enabled ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Enabled
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      Disabled
                    </span>
                  )}
                </dd>
              </div>

              <div className="flex items-center justify-between py-2">
                <dt className="text-sm font-medium text-gray-500">Active Sessions</dt>
                <dd className="mt-1 text-sm text-gray-900">{securityInfo?.active_sessions || 0}</dd>
              </div>

              <div className="flex items-center justify-between py-2">
                <dt className="text-sm font-medium text-gray-500">Last Login</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {securityInfo?.last_login
                    ? new Date(securityInfo.last_login).toLocaleString("id-ID")
                    : "Never"}
                </dd>
              </div>

              <div className="flex items-center justify-between py-2">
                <dt className="text-sm font-medium text-gray-500">Last Password Change</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {securityInfo?.last_password_change
                    ? new Date(securityInfo.last_password_change).toLocaleDateString("id-ID")
                    : "Never"}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Change Password Form */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Change Password</h2>
            <p className="text-sm text-gray-600 mt-1">
              Password must be at least 12 characters with uppercase, lowercase, number, and special character.
            </p>
          </div>

          <form onSubmit={handleSubmitPasswordChange} className="p-6 space-y-4">
            <div>
              <label htmlFor="current_password" className="block text-sm font-medium text-gray-700 mb-1">
                Current Password <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                id="current_password"
                value={passwordForm.current_password}
                onChange={(e) => handlePasswordChange("current_password", e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                  passwordErrors.current_password ? "border-red-300" : "border-gray-300"
                }`}
                placeholder="Enter your current password"
              />
              {passwordErrors.current_password && (
                <p className="mt-1 text-sm text-red-600">{passwordErrors.current_password}</p>
              )}
            </div>

            <div>
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-1">
                New Password <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                id="new_password"
                value={passwordForm.new_password}
                onChange={(e) => handlePasswordChange("new_password", e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                  passwordErrors.new_password ? "border-red-300" : "border-gray-300"
                }`}
                placeholder="Enter your new password"
              />
              {passwordErrors.new_password && (
                <p className="mt-1 text-sm text-red-600">{passwordErrors.new_password}</p>
              )}
              
              {passwordForm.new_password && passwordStrength && (
                <div className="mt-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">Password strength:</span>
                    <span className={`text-xs font-medium ${
                      passwordStrength === "weak" ? "text-red-600" :
                      passwordStrength === "medium" ? "text-yellow-600" :
                      "text-green-600"
                    }`}>
                      {getPasswordStrengthText()}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getPasswordStrengthColor()}`}
                      style={{
                        width: passwordStrength === "weak" ? "33%" :
                               passwordStrength === "medium" ? "66%" :
                               passwordStrength === "strong" ? "100%" : "0%"
                      }}
                    ></div>
                  </div>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                id="confirm_password"
                value={passwordForm.confirm_password}
                onChange={(e) => handlePasswordChange("confirm_password", e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                  passwordErrors.confirm_password ? "border-red-300" : "border-gray-300"
                }`}
                placeholder="Confirm your new password"
              />
              {passwordErrors.confirm_password && (
                <p className="mt-1 text-sm text-red-600">{passwordErrors.confirm_password}</p>
              )}
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={changingPassword || !passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password}
                className="w-full px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {changingPassword ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Changing Password...
                  </span>
                ) : (
                  "Change Password"
                )}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
