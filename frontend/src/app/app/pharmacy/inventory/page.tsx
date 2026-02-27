"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Package,
  Search,
  Plus,
  ChevronRight,
  Edit,
  AlertTriangle,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface InventoryItem {
  id: string;
  name: string;
  category: string;
  unit: string;
  stock: number;
  minStock: number;
  price: number;
  expiryDate: string;
  supplier: string;
}

export default function PharmacyInventoryPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");

  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      if (!token) {
        router.push("/app/login");
        return;
      }

      setItems([
        { id: "1", name: "Paracetamol 500mg", category: "Analgesik", unit: "tablet", stock: 5000, minStock: 1000, price: 500, expiryDate: "2027-06-30", supplier: "PT Kimia Farma" },
        { id: "2", name: "Amoxicillin 500mg", category: "Antibiotik", unit: "kapsul", stock: 2500, minStock: 500, price: 2500, expiryDate: "2027-03-15", supplier: "PT Dexa Medica" },
        { id: "3", name: "Omeprazole 20mg", category: "Maag", unit: "kapsul", stock: 1200, minStock: 300, price: 3500, expiryDate: "2027-08-20", supplier: "PT Sanbe" },
        { id: "4", name: "Vitamin C 1000mg", category: "Vitamin", unit: "tablet", stock: 800, minStock: 500, price: 1500, expiryDate: "2027-12-01", supplier: "PT Kalbe" },
        { id: "5", name: "Cetirizine 10mg", category: "Antihistamin", unit: "tablet", stock: 150, minStock: 200, price: 800, expiryDate: "2027-05-10", supplier: "PT Kimia Farma" },
        { id: "6", name: "Metformin 500mg", category: "Diabetes", unit: "tablet", stock: 3000, minStock: 1000, price: 600, expiryDate: "2027-09-25", supplier: "PT Dexa Medica" },
        { id: "7", name: "Amlodipine 5mg", category: "Hipertensi", unit: "tablet", stock: 80, minStock: 300, price: 1200, expiryDate: "2027-04-12", supplier: "PT Sanbe" },
        { id: "8", name: "Salbutamol Inhaler", category: "Asma", unit: "inhaler", stock: 45, minStock: 50, price: 45000, expiryDate: "2027-07-30", supplier: "PT Kalbe" },
      ]);
    } catch (error) {
      console.error("Failed to load inventory:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredItems = items.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === "all" || item.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const getStockStatus = (stock: number, minStock: number) => {
    if (stock === 0) return { label: "Habis", color: "bg-red-100 text-red-700" };
    if (stock < minStock) return { label: "Rendah", color: "bg-yellow-100 text-yellow-700" };
    return { label: "Aman", color: "bg-green-100 text-green-700" };
  };

  const categories = [...new Set(items.map((item) => item.category))];

  const stats = [
    { label: "Total Item", value: items.length, icon: Package },
    { label: "Stok Rendah", value: items.filter((i) => i.stock < i.minStock).length, icon: TrendingDown },
    { label: "Stok Aman", value: items.filter((i) => i.stock >= i.minStock).length, icon: TrendingUp },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <Link href="/app/dashboard" className="hover:text-gray-700">
            Dashboard
          </Link>
          <ChevronRight className="h-4 w-4" />
          <Link href="/app/pharmacy" className="hover:text-gray-700">
            Farmasi
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Inventori</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Package className="h-6 w-6 mr-2 text-teal-600" />
              Inventori Obat
            </h1>
            <p className="text-gray-600 mt-1">Kelola stok dan data obat</p>
          </div>
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            Tambah Obat
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <stat.icon className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari nama obat..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">Semua Kategori</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Inventory Table */}
      <Card>
        <CardHeader>
          <CardTitle>Daftar Obat ({filteredItems.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Nama Obat</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Kategori</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Stok</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Harga</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Kadaluarsa</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredItems.map((item) => {
                    const stockStatus = getStockStatus(item.stock, item.minStock);
                    return (
                      <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <div>
                            <p className="font-medium text-gray-900">{item.name}</p>
                            <p className="text-sm text-gray-500">{item.supplier}</p>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-gray-600">{item.category}</td>
                        <td className="py-3 px-4">
                          <div>
                            <p className="font-medium text-gray-900">{item.stock} {item.unit}</p>
                            <p className="text-sm text-gray-500">Min: {item.minStock}</p>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${stockStatus.color}`}>
                            {stockStatus.label}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-600">Rp {item.price.toLocaleString()}</td>
                        <td className="py-3 px-4 text-sm text-gray-500">{item.expiryDate}</td>
                        <td className="py-3 px-4 text-right">
                          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                            <Edit className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
