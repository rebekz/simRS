"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface RefillItem {
  prescription_id: number;
  prescription_item_id: number;
  drug_id: number;
  drug_name: string;
  quantity_requested?: number;
  reason_for_refill?: string;
}

interface RefillRequest {
  items: RefillItem[];
  notes?: string;
  preferred_pickup_date?: string;
}

export default function PrescriptionRefillPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [refillItems, setRefillItems] = useState<RefillItem[]>([]);
  const [formData, setFormData] = useState<RefillRequest>({
    items: [],
    notes: "",
    preferred_pickup_date: "",
  });

  useEffect(() => {
    checkAuth();
    loadRefillItems();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const loadRefillItems = () => {
    const stored = sessionStorage.getItem("refillItems");
    if (!stored) {
      router.push("/portal/prescriptions");
      return;
    }

    const items: RefillItem[] = JSON.parse(stored);
    setRefillItems(items);
    setFormData((prev) => ({
      ...prev,
      items: items.map(item => ({
        ...item,
        quantity_requested: item.quantity_requested || 30,
        reason_for_refill: "",
      })),
    }));
  };

  const updateItem = (index: number, field: keyof RefillItem, value: string | number) => {
    setFormData((prev) => ({
      ...prev,
      items: prev.items.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      ),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate all items have reasons
    const invalidItems = formData.items.filter(item => !item.reason_for_refill || item.reason_for_refill.length < 5);
    if (invalidItems.length > 0) {
      setError("Please provide a reason for refill (at least 5 characters) for all medications");
      return;
    }

    setSubmitting(true);

    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
      return;
    }

    try {
      const response = await fetch("/api/v1/portal/prescriptions/refill-requests", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to submit refill request");
      }

      setSuccess(true);
      sessionStorage.removeItem("refillItems");

      // Redirect to prescriptions after 3 seconds
      setTimeout(() => {
        router.push("/portal/prescriptions");
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit refill request");
    } finally {
      setSubmitting(false);
    }
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split("T")[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 30);
    return maxDate.toISOString().split("T")[0];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md text-center">
          <svg className="w-16 h-16 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Refill Request Submitted!</h2>
          <p className="text-gray-600 mb-4">
            Your refill request has been submitted successfully. You will be notified when it is reviewed.
          </p>
          <p className="text-sm text-gray-500">Redirecting to prescriptions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <a href="/portal/prescriptions" className="text-indigo-600 hover:underline text-sm">
            ← Back to My Prescriptions
          </a>
          <h1 className="text-2xl font-bold text-gray-900 mt-2">Request Prescription Refill</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-medium text-blue-900 mb-2">Important Information</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Refill requests are typically processed within 1-2 business days</li>
            <li>• You will receive a notification when your request is approved</li>
            <li>• Please ensure you have refills remaining on your prescription</li>
            <li>• Controlled substances may require additional processing time</li>
          </ul>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
          {/* Medications to Refill */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Medications to Refill</h3>
            <div className="space-y-4">
              {formData.items.map((item, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-medium text-gray-900">{item.drug_name}</p>
                      <p className="text-sm text-gray-600">Prescription #{item.prescription_id}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        const newItems = formData.items.filter((_, i) => i !== index);
                        setFormData({ ...formData, items: newItems });
                      }}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Quantity Requested <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        min={1}
                        max={365}
                        value={item.quantity_requested || 30}
                        onChange={(e) => updateItem(index, "quantity_requested", parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        required
                      />
                    </div>
                  </div>

                  <div className="mt-3">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Reason for Refill <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., Running low on medication"
                      value={item.reason_for_refill || ""}
                      onChange={(e) => updateItem(index, "reason_for_refill", e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      minLength={5}
                      maxLength={500}
                      required
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {formData.items.length === 0 && (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-500 mb-4">No medications selected for refill</p>
              <button
                type="button"
                onClick={() => router.push("/portal/prescriptions")}
                className="text-indigo-600 hover:underline"
              >
                ← Back to Prescriptions
              </button>
            </div>
          )}

          {/* Additional Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Notes (Optional)
            </label>
            <textarea
              value={formData.notes || ""}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="Any additional information for the pharmacist..."
              maxLength={500}
            />
          </div>

          {/* Preferred Pickup Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Pickup Date (Optional)
            </label>
            <input
              type="date"
              value={formData.preferred_pickup_date || ""}
              onChange={(e) => setFormData({ ...formData, preferred_pickup_date: e.target.value })}
              min={getMinDate()}
              max={getMaxDate()}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-gray-500 mt-1">Select a date within the next 30 days</p>
          </div>

          {/* Submit */}
          {formData.items.length > 0 && (
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 py-3 px-6 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? "Submitting..." : "Submit Refill Request"}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          )}
        </form>
      </main>
    </div>
  );
}
