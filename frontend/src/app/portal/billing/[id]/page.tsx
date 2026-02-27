"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";

interface InvoiceItem {
  id: number;
  item_type: string;
  item_code: string | null;
  item_name: string;
  description: string | null;
  quantity: string;
  unit_price: string;
  subtotal: string;
  tax_amount: string;
  discount_amount: string;
  total: string;
  doctor_name: string | null;
  service_date: string | null;
  is_bpjs_covered: boolean;
}

interface PaymentRecord {
  id: number;
  payment_date: string;
  payment_method: string;
  amount: string;
  reference_number: string | null;
  bank_name: string | null;
}

interface InvoiceDetail {
  id: number;
  invoice_number: string;
  invoice_date: string;
  invoice_type: string;
  status: string;
  due_date: string | null;
  payer_type: string;
  insurance_company: string | null;
  policy_number: string | null;
  bpjs_membership_number: string | null;
  subtotal: string;
  tax_amount: string;
  discount_amount: string;
  total_amount: string;
  paid_amount: string;
  balance_due: string;
  items: InvoiceItem[];
  payment_history: PaymentRecord[];
  outstanding_balance: string;
  created_at: string;
  approved_at: string | null;
}

interface PaymentMethodConfig {
  method: string;
  name: string;
  is_available: boolean;
  fee_percentage: string | null;
  min_amount: string | null;
  max_amount: string | null;
  description: string | null;
}

export default function InvoiceDetailPage() {
  const router = useRouter();
  const params = useParams();
  const invoiceId = parseInt(params.id as string);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethodConfig[]>([]);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState("");
  const [paymentAmount, setPaymentAmount] = useState("");
  const [processingPayment, setProcessingPayment] = useState(false);

  useEffect(() => {
    checkAuth();
    fetchInvoiceDetail();
    fetchPaymentMethods();
  }, [invoiceId]);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchInvoiceDetail = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/billing/invoices/${invoiceId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        if (response.status === 404) {
          setError("Invoice not found");
          setLoading(false);
          return;
        }
        throw new Error("Failed to fetch invoice details");
      }

      const data = await response.json();
      setInvoice(data);
      // Set default payment amount to outstanding balance
      setPaymentAmount(data.outstanding_balance);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load invoice");
    } finally {
      setLoading(false);
    }
  };

  const fetchPaymentMethods = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/billing/payment-methods", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPaymentMethods(data);
      }
    } catch (err) {
      console.error("Failed to fetch payment methods");
    }
  };

  const handleInitiatePayment = async () => {
    if (!selectedPaymentMethod || !paymentAmount) {
      alert("Please select payment method and amount");
      return;
    }

    setProcessingPayment(true);

    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/billing/payments/initiate", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          invoice_id: invoiceId,
          payment_method: selectedPaymentMethod,
          amount: parseFloat(paymentAmount),
          return_url: `${window.location.origin}/portal/billing/${invoiceId}`,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Payment initiation failed");
      }

      const data = await response.json();

      // In production, this would redirect to payment gateway
      alert(`Payment initiated!\n\nPayment ID: ${data.payment_id}\nAmount: ${formatCurrency(data.amount)}\n\n(This is a demo - payment gateway integration required)`);

      setShowPaymentModal(false);
      // Refresh invoice details
      fetchInvoiceDetail();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to initiate payment");
    } finally {
      setProcessingPayment(false);
    }
  };

  const formatCurrency = (amount: string | number) => {
    const num = typeof amount === "string" ? parseFloat(amount) : amount;
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "N/A";
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading invoice details...</p>
        </div>
      </div>
    );
  }

  if (error || !invoice) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-gray-500 mb-4">{error || "Invoice not found"}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link href="/portal/billing" className="text-indigo-600 hover:underline text-sm">
            ← Back to Billing
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-2">{invoice.invoice_number}</h1>
          <p className="text-sm text-gray-500">Invoice Details</p>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Invoice Summary */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <p className="text-sm text-gray-500">Invoice Date</p>
              <p className="font-medium">{formatDate(invoice.invoice_date)}</p>
            </div>
            {invoice.due_date && (
              <div>
                <p className="text-sm text-gray-500">Due Date</p>
                <p className="font-medium">{formatDate(invoice.due_date)}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-gray-500">Type</p>
              <p className="font-medium capitalize">{invoice.invoice_type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Status</p>
              <p className="font-medium capitalize">{invoice.status.replace("_", " ")}</p>
            </div>
          </div>

          <div className="border-t border-gray-200 pt-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">{formatCurrency(invoice.subtotal)}</span>
            </div>
            {parseFloat(invoice.discount_amount) > 0 && (
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Discount</span>
                <span className="font-medium text-green-600">-{formatCurrency(invoice.discount_amount)}</span>
              </div>
            )}
            {parseFloat(invoice.tax_amount) > 0 && (
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Tax</span>
                <span className="font-medium">{formatCurrency(invoice.tax_amount)}</span>
              </div>
            )}
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-600">Total</span>
              <span className="font-bold text-lg">{formatCurrency(invoice.total_amount)}</span>
            </div>
            {parseFloat(invoice.paid_amount) > 0 && (
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Paid</span>
                <span className="font-medium text-green-600">{formatCurrency(invoice.paid_amount)}</span>
              </div>
            )}
            <div className="flex justify-between items-center pt-2 border-t border-gray-200">
              <span className="text-gray-900 font-semibold">Balance Due</span>
              <span className="font-bold text-xl text-indigo-600">{formatCurrency(invoice.balance_due)}</span>
            </div>
          </div>

          {parseFloat(invoice.balance_due) > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <button
                onClick={() => setShowPaymentModal(true)}
                className="w-full py-3 px-6 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700"
              >
                Pay Now
              </button>
            </div>
          )}
        </div>

        {/* Line Items */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Invoice Items</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Item</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Description</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Qty</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Unit Price</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Total</th>
                </tr>
              </thead>
              <tbody>
                {invoice.items.map((item) => (
                  <tr key={item.id} className="border-b border-gray-100">
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium text-gray-900">{item.item_name}</p>
                        {item.is_bpjs_covered && (
                          <span className="inline-block mt-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                            BPJS
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">{item.description || "-"}</td>
                    <td className="py-3 px-4 text-right text-sm">{item.quantity}</td>
                    <td className="py-3 px-4 text-right text-sm">{formatCurrency(item.unit_price)}</td>
                    <td className="py-3 px-4 text-right text-sm font-medium">{formatCurrency(item.total)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Payment History */}
        {invoice.payment_history.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment History</h2>
            <div className="space-y-3">
              {invoice.payment_history.map((payment) => (
                <div key={payment.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{formatDate(payment.payment_date)}</p>
                    <p className="text-xs text-gray-500 capitalize">{payment.payment_method.replace("_", " ")}</p>
                    {payment.reference_number && (
                      <p className="text-xs text-gray-500">Ref: {payment.reference_number}</p>
                    )}
                  </div>
                  <p className="font-bold text-green-600">{formatCurrency(payment.amount)}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Make Payment</h2>
              <button
                onClick={() => setShowPaymentModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-500">Outstanding Balance</p>
              <p className="text-2xl font-bold text-indigo-600">{formatCurrency(invoice.balance_due)}</p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Payment Amount
              </label>
              <input
                type="number"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                max={parseFloat(invoice.balance_due)}
                min={10000}
                step={1000}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Payment Method
              </label>
              <div className="space-y-2">
                {paymentMethods.map((method) => (
                  method.is_available && (
                    <button
                      key={method.method}
                      onClick={() => setSelectedPaymentMethod(method.method)}
                      className={`w-full p-3 border rounded-lg text-left ${
                        selectedPaymentMethod === method.method
                          ? "border-indigo-500 bg-indigo-50"
                          : "border-gray-300 hover:border-gray-400"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{method.name}</p>
                          <p className="text-xs text-gray-500">{method.description}</p>
                        </div>
                        {method.fee_percentage && (
                          <span className="text-xs text-gray-500">
                            Fee: {(parseFloat(method.fee_percentage) * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </button>
                  )
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleInitiatePayment}
                disabled={processingPayment || !selectedPaymentMethod}
                className="flex-1 py-3 px-6 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processingPayment ? "Processing..." : "Pay Now"}
              </button>
              <button
                onClick={() => setShowPaymentModal(false)}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
