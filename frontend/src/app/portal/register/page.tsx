"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function PatientPortalRegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState<"email" | "verify" | "phone" | "complete">("email");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    phone: "",
    nik: "",
    mrn: "",
    bpjsCard: "",
    acceptTerms: false,
    acceptPrivacy: false,
  });

  // Verification state
  const [emailCode, setEmailCode] = useState("");
  const [phoneCode, setPhoneCode] = useState("");
  const [portalUserId, setPortalUserId] = useState<number | null>(null);

  const updateForm = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const validateEmailStep = (): boolean => {
    if (!formData.email) {
      setError("Email is required");
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError("Invalid email format");
      return false;
    }
    if (!formData.password) {
      setError("Password is required");
      return false;
    }
    if (formData.password.length < 12) {
      setError("Password must be at least 12 characters");
      return false;
    }
    if (!/[A-Z]/.test(formData.password)) {
      setError("Password must contain at least one uppercase letter");
      return false;
    }
    if (!/[a-z]/.test(formData.password)) {
      setError("Password must contain at least one lowercase letter");
      return false;
    }
    if (!/[0-9]/.test(formData.password)) {
      setError("Password must contain at least one number");
      return false;
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(formData.password)) {
      setError("Password must contain at least one special character");
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    if (!formData.phone) {
      setError("Phone number is required");
      return false;
    }
    if (!/^(\+62|62|0)8[1-9][0-9]{6,11}$/.test(formData.phone.replace(/[\s-]/g, ""))) {
      setError("Invalid Indonesian phone number");
      return false;
    }
    if (!formData.acceptTerms || !formData.acceptPrivacy) {
      setError("You must accept the terms and privacy policy");
      return false;
    }
    return true;
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateEmailStep()) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/v1/portal/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          phone: formData.phone,
          nik: formData.nik || undefined,
          mrn: formData.mrn || undefined,
          bpjs_card_number: formData.bpjsCard || undefined,
          accept_terms: formData.acceptTerms,
          accept_privacy: formData.acceptPrivacy,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Registration failed");
      }

      setPortalUserId(data.portal_user_id);
      setSuccess("Registration successful! Please enter the verification code sent to your email.");
      setStep("verify");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch("/api/v1/portal/register/verify-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          verification_code: emailCode,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || "Verification failed");
      }

      if (!data.success) {
        throw new Error(data.message || "Verification failed");
      }

      setSuccess("Email verified successfully! Now let's verify your phone number.");
      setStep("phone");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSendPhoneVerification = async () => {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch("/api/v1/portal/register/send-phone-verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: formData.phone,
          portal_user_id: portalUserId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || "Failed to send SMS");
      }

      setSuccess("Verification code sent to your phone!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send SMS");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyPhone = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch("/api/v1/portal/register/verify-phone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: formData.phone,
          verification_code: phoneCode,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.message || "Verification failed");
      }

      // Activate account
      await handleActivateAccount();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleActivateAccount = async () => {
    if (!portalUserId) return;

    try {
      const response = await fetch("/api/v1/portal/register/activate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          portal_user_id: portalUserId,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.message || "Activation failed");
      }

      setStep("complete");
      setSuccess("Account activated successfully! Redirecting to login...");
      setTimeout(() => {
        router.push("/portal/login");
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Activation failed");
    }
  };

  const handleResendCode = async (type: "email" | "phone") => {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch("/api/v1/portal/register/resend-verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          verification_type: type,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || "Failed to resend");
      }

      setSuccess(data.message || "Code resent successfully!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to resend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              SIMRS Patient Portal
            </h1>
            <p className="text-gray-600 mt-2">
              {step === "email" && "Create your account"}
              {step === "verify" && "Verify your email"}
              {step === "phone" && "Verify your phone"}
              {step === "complete" && "Registration complete!"}
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-4">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                step === "email" || step === "verify" || step === "phone" || step === "complete"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-200 text-gray-600"
              }`}>
                {step === "verify" || step === "phone" || step === "complete" ? "✓" : "1"}
              </div>
              <div className={`h-1 w-12 ${
                step === "verify" || step === "phone" || step === "complete" ? "bg-indigo-600" : "bg-gray-200"
              }`}></div>
              <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                step === "verify" || step === "phone" || step === "complete"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-200 text-gray-600"
              }`}>
                {step === "phone" || step === "complete" ? "✓" : "2"}
              </div>
              <div className={`h-1 w-12 ${
                step === "phone" || step === "complete" ? "bg-indigo-600" : "bg-gray-200"
              }`}></div>
              <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                step === "complete" ? "bg-indigo-600 text-white" : "bg-gray-200 text-gray-600"
              }`}>
                {step === "complete" ? "✓" : "3"}
              </div>
            </div>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
              {success}
            </div>
          )}

          {/* Step 1: Email & Password Registration */}
          {step === "email" && (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => updateForm("email", e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="your@email.com"
                  required
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => updateForm("password", e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Min. 12 characters with uppercase, lowercase, number, special character"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">
                  Must be 12+ characters with uppercase, lowercase, number, and special character
                </p>
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => updateForm("confirmPassword", e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Re-enter password"
                  required
                />
              </div>

              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => updateForm("phone", e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="+6281234567890"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">Indonesian mobile number (e.g., +6281234567890)</p>
              </div>

              <div className="pt-2">
                <div className="flex items-start mb-3">
                  <input
                    id="acceptTerms"
                    type="checkbox"
                    checked={formData.acceptTerms}
                    onChange={(e) => updateForm("acceptTerms", e.target.checked)}
                    className="mt-1 w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                    required
                  />
                  <label htmlFor="acceptTerms" className="ml-2 text-sm text-gray-600">
                    I accept the <a href="/terms" className="text-indigo-600 hover:underline">Terms of Service</a>
                  </label>
                </div>

                <div className="flex items-start">
                  <input
                    id="acceptPrivacy"
                    type="checkbox"
                    checked={formData.acceptPrivacy}
                    onChange={(e) => updateForm("acceptPrivacy", e.target.checked)}
                    className="mt-1 w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                    required
                  />
                  <label htmlFor="acceptPrivacy" className="ml-2 text-sm text-gray-600">
                    I accept the <a href="/privacy" className="text-indigo-600 hover:underline">Privacy Policy</a>
                  </label>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? "Creating account..." : "Create Account"}
              </button>
            </form>
          )}

          {/* Step 2: Email Verification */}
          {step === "verify" && (
            <form onSubmit={handleVerifyEmail} className="space-y-4">
              <div className="text-center mb-4">
                <p className="text-gray-600">
                  We've sent a 6-digit verification code to <strong>{formData.email}</strong>
                </p>
              </div>

              <div>
                <label htmlFor="emailCode" className="block text-sm font-medium text-gray-700 mb-1">
                  Verification Code
                </label>
                <input
                  id="emailCode"
                  type="text"
                  value={emailCode}
                  onChange={(e) => setEmailCode(e.target.value.replace(/[^0-9]/g, "").slice(0, 6))}
                  className="w-full px-4 py-3 text-center text-2xl tracking-widest border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="000000"
                  maxLength={6}
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading || emailCode.length !== 6}
                className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? "Verifying..." : "Verify Email"}
              </button>

              <button
                type="button"
                onClick={() => handleResendCode("email")}
                disabled={loading}
                className="w-full py-3 px-4 border border-indigo-600 text-indigo-600 font-semibold rounded-lg hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Resend Code
              </button>
            </form>
          )}

          {/* Step 3: Phone Verification */}
          {step === "phone" && (
            <form onSubmit={handleVerifyPhone} className="space-y-4">
              <div className="text-center mb-4">
                <p className="text-gray-600">
                  Verify your phone: <strong>{formData.phone}</strong>
                </p>
              </div>

              {!phoneCode && (
                <button
                  type="button"
                  onClick={handleSendPhoneVerification}
                  disabled={loading}
                  className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? "Sending..." : "Send SMS Code"}
                </button>
              )}

              {phoneCode && (
                <>
                  <div>
                    <label htmlFor="phoneCode" className="block text-sm font-medium text-gray-700 mb-1">
                      SMS Verification Code
                    </label>
                    <input
                      id="phoneCode"
                      type="text"
                      value={phoneCode}
                      onChange={(e) => setPhoneCode(e.target.value.replace(/[^0-9]/g, "").slice(0, 6))}
                      className="w-full px-4 py-3 text-center text-2xl tracking-widest border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="000000"
                      maxLength={6}
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading || phoneCode.length !== 6}
                    className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {loading ? "Verifying..." : "Complete Registration"}
                  </button>

                  <button
                    type="button"
                    onClick={() => handleResendCode("phone")}
                    disabled={loading}
                    className="w-full py-3 px-4 border border-indigo-600 text-indigo-600 font-semibold rounded-lg hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    Resend SMS
                  </button>
                </>
              )}
            </form>
          )}

          {/* Complete */}
          {step === "complete" && (
            <div className="text-center">
              <div className="mb-6">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900">Registration Complete!</h3>
                <p className="text-gray-600 mt-2">Your account has been created and verified.</p>
              </div>

              <button
                onClick={() => router.push("/portal/login")}
                className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all"
              >
                Go to Login
              </button>
            </div>
          )}

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{" "}
              <a href="/portal/login" className="text-indigo-600 hover:underline font-medium">
                Sign in
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
