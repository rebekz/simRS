"use client";

import { useState } from "react";
import Link from "next/link";
import { CreditCard, ChevronRight, Search, Download, Eye } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function PortalBillingPage() {
  const [statusFilter, setStatusFilter] = useState("all");

  const invoices = [
    { id: "INV-001", date: "2026-02-27", total: 250000, paid: 250000, status: "paid", items: 5 },
    { id: "INV-002", date: "2026-02-15", total: 1800000, paid: 500000, status: "partial", items: 12 },
    { id: "INV-003", date: "2026-01-20", total: 750000, paid: 0, status: "unpaid", items: 8 },
  ];

  const filteredInvoices = invoices.filter((inv) => statusFilter === "all" || inv.status === statusFilter);

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      paid: "bg-green-100 text-green-700",
      partial: "bg-yellow-100 text-yellow-700",
      unpaid: "bg-red-100 text-red-700",
    };
    const labels: Record<string, string> = { paid: "Lunas", partial: "Sebagian", unpaid: "Belum Bayar" };
    return <span className={"px-2 py-1 text-xs font-medium rounded-full " + styles[status]}>{labels[status]}</span>;
  };

  const totalDue = invoices.reduce((sum, inv) => sum + (inv.total - inv.paid), 0);

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/portal/dashboard">Dashboard</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Tagihan</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Tagihan</h1>
      </div>

      <Card className="bg-gradient-to-r from-red-500 to-red-600 text-white">
        <CardContent className="p-6">
          <p className="text-red-100">Total Tunggakan</p>
          <p className="text-3xl font-bold">Rp {totalDue.toLocaleString()}</p>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="all">Semua Status</option>
            <option value="unpaid">Belum Bayar</option>
            <option value="partial">Sebagian</option>
            <option value="paid">Lunas</option>
          </select>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {filteredInvoices.map((inv) => (
          <Card key={inv.id}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-semibold">{inv.id}</h3>
                    {getStatusBadge(inv.status)}
                  </div>
                  <p className="text-sm text-gray-500">{inv.date}</p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold">Rp {inv.total.toLocaleString()}</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t flex justify-end space-x-2">
                <Button variant="secondary" size="sm"><Eye className="h-4 w-4 mr-1" />Detail</Button>
                <Button variant="secondary" size="sm"><Download className="h-4 w-4 mr-1" />PDF</Button>
                {inv.status !== "paid" && <Button variant="primary" size="sm">Bayar</Button>}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
