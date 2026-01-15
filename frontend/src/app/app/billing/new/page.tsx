"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type {
  InvoicePatient,
  InvoiceEncounter,
  FormLineItem,
  LineItemType,
  PaymentMethod,
  PayerType,
  VisitType,
  BillingCatalogItem,
} from "@/types/invoice";
import {
  PAYMENT_METHOD_OPTIONS,
  PAYER_TYPE_OPTIONS,
  LINE_ITEM_TYPE_OPTIONS,
  VISIT_TYPES,
  DEFAULT_INVOICE_FORM_VALUES,
  DEFAULT_LINE_ITEM_VALUES,
  formatCurrency,
  calculateLineItemSubtotal,
  calculateDiscountAmount,
  calculateTaxAmount,
  calculateLineItemTotal,
  calculateInvoiceTotals,
} from "@/constants/invoice";

export default function NewInvoicePage() {
  const router = useRouter();

  // Form state
  const [selectedPatient, setSelectedPatient] = useState<InvoicePatient | null>(null);
  const [selectedEncounter, setSelectedEncounter] = useState<InvoiceEncounter | null>(null);
  const [lineItems, setLineItems] = useState<FormLineItem[]>([]);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("cash");
  const [payerType, setPayerType] = useState<PayerType>("patient");
  const [notes, setNotes] = useState("");
  const [discountType, setDiscountType] = useState<"percentage" | "fixed" | "none">("none");
  const [discountValue, setDiscountValue] = useState(0);
  const [taxRate, setTaxRate] = useState(11);

  // UI state
  const [loading, setLoading] = useState(false);
  const [searchingPatient, setSearchingPatient] = useState(false);
  const [patientSearchQuery, setPatientSearchQuery] = useState("");
  const [patientSearchResults, setPatientSearchResults] = useState<InvoicePatient[]>([]);
  const [showPatientResults, setShowPatientResults] = useState(false);
  const [encounters, setEncounters] = useState<InvoiceEncounter[]>([]);
  const [loadingEncounters, setLoadingEncounters] = useState(false);
  const [showAddItemModal, setShowAddItemModal] = useState(false);
  const [addItemType, setAddItemType] = useState<LineItemType>("service");
  const [catalogItems, setCatalogItems] = useState<BillingCatalogItem[]>([]);
  const [loadingCatalog, setLoadingCatalog] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  }, [router]);

  // Calculate totals
  const totals = calculateInvoiceTotals(
    lineItems,
    discountType,
    discountValue,
    taxRate
  );

  // Search patients
  const searchPatients = async (query: string) => {
    if (!query || query.length < 2) {
      setPatientSearchResults([]);
      setShowPatientResults(false);
      return;
    }

    setSearchingPatient(true);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch(
        `/api/v1/patients/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Gagal mencari pasien");
      }

      const data = await response.json();
      setPatientSearchResults(data.patients || []);
      setShowPatientResults(true);
    } catch (err) {
      console.error("Error searching patients:", err);
      setPatientSearchResults([]);
    } finally {
      setSearchingPatient(false);
    }
  };

  // Debounced patient search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchPatients(patientSearchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [patientSearchQuery]);

  // Fetch patient encounters
  const fetchPatientEncounters = async (patientId: number) => {
    setLoadingEncounters(true);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch(
        `/api/v1/patients/${patientId}/encounters?unbilled=true`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Gagal mengambil data kunjungan");
      }

      const data = await response.json();
      setEncounters(data.encounters || []);
    } catch (err) {
      console.error("Error fetching encounters:", err);
      setError(err instanceof Error ? err.message : "Gagal mengambil data kunjungan");
    } finally {
      setLoadingEncounters(false);
    }
  };

  // Fetch catalog items
  const fetchCatalogItems = async (itemType: LineItemType) => {
    setLoadingCatalog(true);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch(
        `/api/v1/billing/catalog?category=${itemType}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Gagal mengambil data katalog");
      }

      const data = await response.json();
      setCatalogItems(data.items || []);
    } catch (err) {
      console.error("Error fetching catalog:", err);
      setError(err instanceof Error ? err.message : "Gagal mengambil data katalog");
    } finally {
      setLoadingCatalog(false);
    }
  };

  // Select patient
  const handleSelectPatient = (patient: InvoicePatient) => {
    setSelectedPatient(patient);
    setShowPatientResults(false);
    setPatientSearchQuery("");
    fetchPatientEncounters(patient.id);
  };

  // Select encounter
  const handleSelectEncounter = (encounter: InvoiceEncounter) => {
    setSelectedEncounter(encounter);
  };

  // Add line item
  const handleAddLineItem = (catalogItem: BillingCatalogItem) => {
    const newItem: FormLineItem = {
      ...DEFAULT_LINE_ITEM_VALUES,
      temp_id: `temp-${Date.now()}`,
      item_type: catalogItem.category,
      item_code: catalogItem.code,
      item_name: catalogItem.name,
      description: catalogItem.description,
      unit: catalogItem.unit,
      unit_price: catalogItem.standard_price,
      quantity: 1,
      subtotal: catalogItem.standard_price,
      bpjs_tariff: catalogItem.bpjs_tariff,
      bpjs_code: catalogItem.bpjs_code,
      is_covered_by_bpjs: catalogItem.is_bpjs_covered && selectedPatient?.bpjs_status === "active",
      is_new: true,
      is_modified: false,
      is_deleted: false,
    };

    // Calculate totals
    newItem.subtotal = calculateLineItemSubtotal(newItem.quantity, newItem.unit_price);
    newItem.discount_amount = calculateDiscountAmount(
      newItem.subtotal,
      newItem.discount_type,
      newItem.discount_value
    );
    newItem.tax_amount = calculateTaxAmount(newItem.subtotal, newItem.discount_amount, newItem.tax_rate);
    newItem.total = calculateLineItemTotal(
      newItem.quantity,
      newItem.unit_price,
      newItem.discount_type,
      newItem.discount_value,
      newItem.tax_rate
    );

    // Set BPJS coverage if applicable
    if (newItem.is_covered_by_bpjs && newItem.bpjs_tariff) {
      newItem.bpjs_coverage_amount = Math.min(newItem.total, newItem.bpjs_tariff);
    }

    setLineItems([...lineItems, newItem]);
    setShowAddItemModal(false);
    setCatalogItems([]);
  };

  // Remove line item
  const handleRemoveLineItem = (tempId: string) => {
    setLineItems(lineItems.filter((item) => item.temp_id !== tempId));
  };

  // Update line item quantity
  const handleUpdateQuantity = (tempId: string, quantity: number) => {
    setLineItems(
      lineItems.map((item) => {
        if (item.temp_id === tempId) {
          const updatedItem = { ...item, quantity };
          updatedItem.subtotal = calculateLineItemSubtotal(quantity, updatedItem.unit_price);
          updatedItem.discount_amount = calculateDiscountAmount(
            updatedItem.subtotal,
            updatedItem.discount_type,
            updatedItem.discount_value
          );
          updatedItem.tax_amount = calculateTaxAmount(
            updatedItem.subtotal,
            updatedItem.discount_amount,
            updatedItem.tax_rate
          );
          updatedItem.total = calculateLineItemTotal(
            quantity,
            updatedItem.unit_price,
            updatedItem.discount_type,
            updatedItem.discount_value,
            updatedItem.tax_rate
          );

          // Update BPJS coverage
          if (updatedItem.is_covered_by_bpjs && updatedItem.bpjs_tariff) {
            updatedItem.bpjs_coverage_amount = Math.min(updatedItem.total, updatedItem.bpjs_tariff);
          }

          return updatedItem;
        }
        return item;
      })
    );
  };

  // Save invoice as draft
  const handleSaveDraft = async () => {
    if (!selectedPatient) {
      setError("Pilih pasien terlebih dahulu");
      return;
    }

    if (lineItems.length === 0) {
      setError("Tambahkan minimal satu item tagihan");
      return;
    }

    setLoading(true);
    setError(null);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch("/api/v1/billing/invoices", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_id: selectedPatient.id,
          encounter_id: selectedEncounter?.id,
          visit_type: selectedEncounter?.visit_type || "outpatient",
          department_id: selectedEncounter?.department_id || 1,
          invoice_date: new Date().toISOString().split("T")[0],
          due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
          discount_type: discountType,
          discount_value: discountValue,
          tax_rate: taxRate,
          payer_type: payerType,
          payment_method: paymentMethod,
          bpjs_number: selectedPatient.bpjs_number,
          items: lineItems.map(({ temp_id, is_new, is_modified, is_deleted, ...item }) => item),
          notes: notes,
          status: "draft",
        }),
      });

      if (!response.ok) {
        throw new Error("Gagal menyimpan draft tagihan");
      }

      const data = await response.json();
      setSuccessMessage("Draft tagihan berhasil disimpan");
      setTimeout(() => {
        router.push(`/app/billing/${data.id}`);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan draft tagihan");
    } finally {
      setLoading(false);
    }
  };

  // Submit invoice for approval
  const handleSubmitForApproval = async () => {
    if (!selectedPatient) {
      setError("Pilih pasien terlebih dahulu");
      return;
    }

    if (lineItems.length === 0) {
      setError("Tambahkan minimal satu item tagihan");
      return;
    }

    setLoading(true);
    setError(null);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch("/api/v1/billing/invoices", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_id: selectedPatient.id,
          encounter_id: selectedEncounter?.id,
          visit_type: selectedEncounter?.visit_type || "outpatient",
          department_id: selectedEncounter?.department_id || 1,
          invoice_date: new Date().toISOString().split("T")[0],
          due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
          discount_type: discountType,
          discount_value: discountValue,
          tax_rate: taxRate,
          payer_type: payerType,
          payment_method: paymentMethod,
          bpjs_number: selectedPatient.bpjs_number,
          items: lineItems.map(({ temp_id, is_new, is_modified, is_deleted, ...item }) => item),
          notes: notes,
          status: "pending",
        }),
      });

      if (!response.ok) {
        throw new Error("Gagal mengirim tagihan untuk persetujuan");
      }

      const data = await response.json();
      setSuccessMessage("Tagihan berhasil diajukan untuk persetujuan");
      setTimeout(() => {
        router.push(`/app/billing/${data.id}`);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal mengirim tagihan untuk persetujuan");
    } finally {
      setLoading(false);
    }
  };

  // Open add item modal
  const handleOpenAddItemModal = (itemType: LineItemType) => {
    setAddItemType(itemType);
    setShowAddItemModal(true);
    fetchCatalogItems(itemType);
  };

  // Calculate patient age
  const calculateAge = (dateOfBirth: string): number => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Buat Tagihan Baru</h1>
          <p className="text-gray-600 mt-1">Buat tagihan baru untuk pasien</p>
        </div>
        <button
          onClick={() => router.push("/app/billing")}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Kembali
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <p className="text-green-800">{successMessage}</p>
        </div>
      )}

      {/* Patient Selection Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Pilih Pasien</h2>

        <div className="relative">
          <input
            type="text"
            placeholder="Cari berdasarkan No RM, nama, atau nomor BPJS..."
            value={patientSearchQuery}
            onChange={(e) => setPatientSearchQuery(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            disabled={!!selectedPatient}
          />
          {searchingPatient && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
            </div>
          )}
        </div>

        {/* Patient Search Results */}
        {showPatientResults && patientSearchResults.length > 0 && (
          <div className="mt-4 border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-64 overflow-y-auto">
            {patientSearchResults.map((patient) => (
              <button
                key={patient.id}
                onClick={() => handleSelectPatient(patient)}
                className="w-full px-4 py-3 hover:bg-gray-50 text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{patient.name}</p>
                    <p className="text-sm text-gray-600">
                      {patient.medical_record_number} • {calculateAge(patient.date_of_birth)} tahun •{" "}
                      {patient.gender === "male" ? "Laki-laki" : "Perempuan"}
                    </p>
                  </div>
                  {patient.bpjs_number && (
                    <div className="text-right">
                      <p className="text-xs text-gray-500">BPJS</p>
                      <p className="text-sm font-medium text-gray-900">{patient.bpjs_number}</p>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Selected Patient Card */}
        {selectedPatient && (
          <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{selectedPatient.name}</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {selectedPatient.medical_record_number} • {calculateAge(selectedPatient.date_of_birth)} tahun •{" "}
                  {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}
                </p>
                {selectedPatient.bpjs_number && (
                  <div className="mt-2">
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                        selectedPatient.bpjs_status === "active"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      BPJS: {selectedPatient.bpjs_number} •{" "}
                      {selectedPatient.bpjs_status === "active" ? "Aktif" : "Tidak Aktif"}
                    </span>
                  </div>
                )}
                {selectedPatient.insurance_number && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-700">
                      Asuransi: {selectedPatient.insurance_provider} - {selectedPatient.insurance_number}
                    </span>
                  </div>
                )}
                {selectedPatient.corporate_name && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-700">
                      Korporat: {selectedPatient.corporate_name}
                    </span>
                  </div>
                )}
              </div>
              <button
                onClick={() => {
                  setSelectedPatient(null);
                  setSelectedEncounter(null);
                  setLineItems([]);
                }}
                className="text-gray-400 hover:text-red-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Encounter Selection Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Pilih Kunjungan</h2>

          {loadingEncounters ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : encounters.length > 0 ? (
            <div className="space-y-3">
              {encounters.map((encounter) => (
                <label
                  key={encounter.id}
                  className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedEncounter?.id === encounter.id
                      ? "border-indigo-500 bg-indigo-50"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <input
                    type="radio"
                    name="encounter"
                    value={encounter.id}
                    checked={selectedEncounter?.id === encounter.id}
                    onChange={() => handleSelectEncounter(encounter)}
                    className="mr-4"
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">{VISIT_TYPES[encounter.visit_type]?.icon || "🏥"}</span>
                      <div>
                        <p className="font-medium text-gray-900">
                          {VISIT_TYPES[encounter.visit_type]?.label || encounter.visit_type}
                        </p>
                        <p className="text-sm text-gray-600">{encounter.department}</p>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-500">
                      {encounter.admission_date && (
                        <span>Masuk: {new Date(encounter.admission_date).toLocaleDateString("id-ID")}</span>
                      )}
                      {encounter.discharge_date && (
                        <span className="ml-4">
                          Keluar: {new Date(encounter.discharge_date).toLocaleDateString("id-ID")}
                        </span>
                      )}
                    </div>
                  </div>
                  {encounter.room_number && (
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Kamar</p>
                      <p className="text-sm font-medium text-gray-900">
                        {encounter.room_number} {encounter.bed_number && `(${encounter.bed_number})`}
                      </p>
                    </div>
                  )}
                </label>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Tidak ada kunjungan yang belum ditagih</p>
              <p className="text-sm mt-1">Anda dapat membuat tagihan tanpa mengaitkan ke kunjungan tertentu</p>
            </div>
          )}
        </div>
      )}

      {/* Line Items Management Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Item Tagihan</h2>

          {/* Add Line Item Buttons */}
          <div className="flex flex-wrap gap-2 mb-4">
            {LINE_ITEM_TYPE_OPTIONS.map((type) => (
              <button
                key={type.value}
                onClick={() => handleOpenAddItemModal(type.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
              >
                <span>{type.icon}</span>
                <span className="text-sm">Tambah {type.label}</span>
              </button>
            ))}
          </div>

          {/* Line Items Table */}
          {lineItems.length > 0 ? (
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Qty</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Harga</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Diskon</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Subtotal</th>
                    {(selectedPatient?.bpjs_number || selectedPatient?.insurance_number) && (
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        {selectedPatient?.bpjs_number ? "Tarif BPJS" : "Jaminan"}
                      </th>
                    )}
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {lineItems.map((item) => (
                    <tr key={item.temp_id} className="text-sm">
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          <span>{LINE_ITEM_TYPES[item.item_type]?.icon}</span>
                          <div>
                            <p className="font-medium text-gray-900">{item.item_name}</p>
                            <p className="text-xs text-gray-500">{item.item_code}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <input
                          type="number"
                          min="1"
                          value={item.quantity}
                          onChange={(e) => handleUpdateQuantity(item.temp_id!, parseInt(e.target.value) || 1)}
                          className="w-16 px-2 py-1 border border-gray-300 rounded text-center"
                        />
                      </td>
                      <td className="px-4 py-3 text-right">{formatCurrency(item.unit_price)}</td>
                      <td className="px-4 py-3 text-right text-red-600">
                        {item.discount_amount > 0 ? `- ${formatCurrency(item.discount_amount)}` : "-"}
                      </td>
                      <td className="px-4 py-3 text-right font-medium">{formatCurrency(item.subtotal)}</td>
                      {(selectedPatient?.bpjs_number || selectedPatient?.insurance_number) && (
                        <td className="px-4 py-3 text-right">
                          {selectedPatient?.bpjs_number ? (
                            <span className={item.is_covered_by_bpjs ? "text-green-600" : "text-gray-400"}>
                              {item.bpjs_tariff ? formatCurrency(item.bpjs_tariff) : "-"}
                            </span>
                          ) : (
                            <span className={item.is_covered_by_insurance ? "text-blue-600" : "text-gray-400"}>
                              {item.is_covered_by_insurance ? "Covered" : "-"}
                            </span>
                          )}
                        </td>
                      )}
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() => handleRemoveLineItem(item.temp_id!)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-200 rounded-lg">
              <p>Belum ada item tagihan</p>
              <p className="text-sm mt-1">Klik tombol di atas untuk menambahkan item</p>
            </div>
          )}
        </div>
      )}

      {/* Payment Information Section */}
      {selectedPatient && lineItems.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Pembayaran</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Metode Pembayaran</label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value as PaymentMethod)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {PAYMENT_METHOD_OPTIONS.map((method) => (
                  <option key={method.value} value={method.value}>
                    {method.icon} {method.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Penanggung</label>
              <select
                value={payerType}
                onChange={(e) => setPayerType(e.target.value as PayerType)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {PAYER_TYPE_OPTIONS.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.icon} {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipe Diskon</label>
              <select
                value={discountType}
                onChange={(e) => setDiscountType(e.target.value as "percentage" | "fixed" | "none")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="none">Tidak Ada</option>
                <option value="percentage">Persentase</option>
                <option value="fixed">Nominal Tetap</option>
              </select>
            </div>

            {discountType !== "none" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nilai Diskon {discountType === "percentage" ? "(%)" : "(Rp)"}
                </label>
                <input
                  type="number"
                  min="0"
                  max={discountType === "percentage" ? 100 : undefined}
                  value={discountValue}
                  onChange={(e) => setDiscountValue(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            )}

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Catatan</label>
              <textarea
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Tambahkan catatan untuk tagihan ini..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Summary Section */}
      {lineItems.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Ringkasan Tagihan</h2>

          <div className="max-w-md ml-auto space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">{formatCurrency(totals.subtotal)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Diskon</span>
              <span className="font-medium text-red-600">-{formatCurrency(totals.discount_amount)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Pajak (11%)</span>
              <span className="font-medium">{formatCurrency(totals.tax_amount)}</span>
            </div>
            <div className="flex justify-between text-lg font-bold border-t pt-3">
              <span>Total</span>
              <span className="text-indigo-600">{formatCurrency(totals.total_amount)}</span>
            </div>

            {(selectedPatient?.bpjs_number || selectedPatient?.insurance_number) && (
              <>
                <div className="border-t pt-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">
                      {selectedPatient?.bpjs_number ? "Jaminan BPJS" : "Jaminan Asuransi"}
                    </span>
                    <span className="font-medium text-green-600">
                      {formatCurrency(
                        lineItems.reduce((sum, item) => sum + (item.bpjs_coverage_amount || 0), 0)
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between text-base font-semibold mt-2">
                    <span>Tanggungan Pasien</span>
                    <span className="text-gray-900">
                      {formatCurrency(
                        totals.total_amount -
                          lineItems.reduce((sum, item) => sum + (item.bpjs_coverage_amount || 0), 0)
                      )}
                    </span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {selectedPatient && lineItems.length > 0 && (
        <div className="flex flex-wrap gap-3 justify-end">
          <button
            onClick={() => router.push("/app/billing")}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Batal
          </button>
          <button
            onClick={handleSaveDraft}
            disabled={loading}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            {loading ? "Menyimpan..." : "Simpan Draft"}
          </button>
          <button
            onClick={() => window.print()}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Print Preview
          </button>
          <button
            onClick={handleSubmitForApproval}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? "Mengirim..." : "Ajukan untuk Persetujuan"}
          </button>
        </div>
      )}

      {/* Add Item Modal */}
      {showAddItemModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">
                Tambah {LINE_ITEM_TYPES[addItemType]?.label}
              </h3>
              <button
                onClick={() => {
                  setShowAddItemModal(false);
                  setCatalogItems([]);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {loadingCatalog ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
              ) : catalogItems.length > 0 ? (
                <div className="space-y-2">
                  {catalogItems.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handleAddLineItem(item)}
                      className="w-full p-3 border border-gray-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-300 text-left"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{item.name}</p>
                          <p className="text-sm text-gray-500">{item.code} • {item.description}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium text-gray-900">{formatCurrency(item.standard_price)}</p>
                          {item.bpjs_tariff && (
                            <p className="text-xs text-green-600">BPJS: {formatCurrency(item.bpjs_tariff)}</p>
                          )}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  Tidak ada item tersedia untuk kategori ini
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
