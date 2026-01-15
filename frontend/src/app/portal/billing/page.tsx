"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface InvoiceListItem {
  id: number;
  invoice_number: string;
  invoice_date: string;
  invoice_type: string;
  status: string;
  total_amount: string;
  paid_amount: string;
  balance_due: string;
  due_date: string | null;
  is_overdue: boolean;
  payer_type: string;
}

interface InvoiceListResponse {
  invoices: InvoiceListItem[];
  total: number;
  outstanding_balance: string;
  overdue_count: number;
  overdue_amount: string;
}

export default function BillingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [invoices, setInvoices] = useState<InvoiceListResponse | null>(null);
  const [statusFilter, setStatusFilter] = useState<"all" | "unpaid" | "overdue">("all");

  useEffect(() => {
    checkAuth();
    fetchInvoices();
  }, [statusFilter]);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchInvoices = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const statusParam = statusFilter === "all" ? "" : `?status=${statusFilter}`;
      const response = await fetch(`/api/v1/portal/billing/invoices${statusParam}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        throw new Error("Failed to fetch invoices");
      }

      const data = await response.json();
      setInvoices(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load invoices");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "paid": return "bg-green-100 text-green-700";
      case "partial_paid": return "bg-blue-100 text-blue-700";
      case "approved": return "bg-yellow-100 text-yellow-700";
      case "cancelled": return "bg-red-100 text-red-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const formatCurrency = (amount: string) => {
    const num = parseFloat(amount);
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
          <p className="mt-4 text-gray-600">Loading billing information...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <a href="/portal/dashboard" className="text-indigo-600 hover:underline text-sm">
            ← Back to Dashboard
          </a>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">Billing & Payments</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {invoices && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Outstanding Balance</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(invoices.outstanding_balance)}</p>
                  </div>
                  <svg className="w-8 h-8 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
              </div>

              {invoices.overdue_count > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg shadow p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-red-600">Overdue</p>
                      <p className="text-2xl font-bold text-red-700">{invoices.overdue_count} invoices</p>
                      <p className="text-xs text-red-600 mt-1">{formatCurrency(invoices.overdue_amount)}</p>
                    </div>
                    <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
              )}

              <div className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Invoices</p>
                    <p className="text-2xl font-bold text-gray-900">{invoices.total}</p>
                  </div>
                  <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="bg-white rounded-lg shadow-md mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  <button
                    onClick={() => setStatusFilter("all")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      statusFilter === "all"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    All ({invoices.total})
                  </button>
                  <button
                    onClick={() => setStatusFilter("unpaid")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      statusFilter === "unpaid"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Unpaid
                  </button>
                  <button
                    onClick={() => setStatusFilter("overdue")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      statusFilter === "overdue"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Overdue
                  </button>
                </nav>
              </div>
            </div>

            {/* Invoices List */}
            <div className="space-y-4">
              {invoices.invoices.length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-gray-500">No invoices found</p>
                </div>
              ) : (
                invoices.invoices.map((invoice) => (
                  <InvoiceCard key={invoice.id} invoice={invoice} />
                ))
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

interface InvoiceCardProps {
  invoice: InvoiceListItem;
}

function InvoiceCard({ invoice }: InvoiceCardProps) {
  const formatCurrency = (amount: string) => {
    const num = parseFloat(amount);
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case "paid": return "bg-green-100 text-green-700";
      case "partial_paid": return "bg-blue-100 text-blue-700";
      case "approved": return "bg-yellow-100 text-yellow-700";
      case "cancelled": return "bg-red-100 text-red-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${invoice.is_overdue ? "border-l-4 border-red-500" : ""}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="text-lg font-semibold text-gray-900">{invoice.invoice_number}</h3>
            <span className={`px-2 py-1 text-xs font-medium rounded capitalize ${getStatusColor(invoice.status)}`}>
              {invoice.status.replace("_", " ")}
            </span>
            {invoice.is_overdue && (
              <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-700">
                Overdue
              </span>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Invoice Date</p>
              <p className="font-medium">{formatDate(invoice.invoice_date)}</p>
            </div>
            {invoice.due_date && (
              <div>
                <p className="text-gray-500">Due Date</p>
                <p className={`font-medium ${invoice.is_overdue ? "text-red-600" : ""}`}>
                  {formatDate(invoice.due_date)}
                </p>
              </div>
            )}
            <div>
              <p className="text-gray-500">Type</p>
              <p className="font-medium capitalize">{invoice.invoice_type}</p>
            </div>
            <div>
              <p className="text-gray-500">Payer</p>
              <p className="font-medium capitalize">{invoice.payer_type.replace("_", " ")}</p>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-500">Total</p>
                <p className="text-lg font-bold text-gray-900">{formatCurrency(invoice.total_amount)}</p>
              </div>
              {parseFloat(invoice.paid_amount) > 0 && (
                <div className="text-right">
                  <p className="text-sm text-gray-500">Paid</p>
                  <p className="font-medium text-green-600">{formatCurrency(invoice.paid_amount)}</p>
                </div>
              )}
              {parseFloat(invoice.balance_due) > 0 && (
                <div className="text-right">
                  <p className="text-sm text-gray-500">Balance Due</p>
                  <p className={`text-lg font-bold ${invoice.is_overdue ? "text-red-600" : "text-indigo-600"}`}>
                    {formatCurrency(invoice.balance_due)}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="ml-4 flex flex-col gap-2">
          {parseFloat(invoice.balance_due) > 0 && (
            <a
              href={`/portal/billing/${invoice.id}`}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm text-center"
            >
              {invoice.is_overdue ? "Pay Now" : "View/Pay"}
            </a>
          )}
          <a
            href={`/portal/billing/${invoice.id}`}
            className="text-sm text-indigo-600 hover:underline text-center"
          >
            View Details
          </a>
        </div>
      </div>
    </div>
  );
}
