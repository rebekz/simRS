"use client";

import { useState } from "react";
import { TriageCard, TriageTicket, TriageDisplay } from "@/components/emergency/TriageCard";
import { Printer } from "lucide-react";

/**
 * WEB-S-5.4: Triage Result Display - Demo/Showcase Page
 *
 * This page demonstrates the TriageCard component with all triage levels.
 */

type TriageLevel = "merah" | "kuning" | "hijau";

export default function TriageDemoPage() {
  const [selectedLevel, setSelectedLevel] = useState<TriageLevel | null>(null);
  const [showTicket, setShowTicket] = useState(false);

  const handleAction = (action: string) => {
    alert(`Action triggered: ${action}`);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            WEB-S-5.4: Triage Result Display
          </h1>
          <p className="text-gray-600">
            Demonstration of color-coded triage cards for emergency department
          </p>
        </div>

        {/* All Triage Levels Display */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Semua Level Triage
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <TriageCard
              level="merah"
              patientName="Budi Santoso"
              queueNumber="A001"
              onAction={handleAction}
            />
            <TriageCard
              level="kuning"
              patientName="Siti Aminah"
              queueNumber="B002"
            />
            <TriageCard
              level="hijau"
              patientName="Ahmad Wijaya"
              queueNumber="C003"
            />
          </div>
        </div>

        {/* Size Variants */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Variasi Ukuran
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            <TriageCard level="merah" size="small" />
            <TriageCard level="kuning" size="medium" />
            <TriageCard level="hijau" size="large" />
          </div>
        </div>

        {/* Interactive Demo */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Demo Interaktif
          </h2>
          <div className="bg-white rounded-lg p-6 shadow-md">
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pilih Level Triage:
              </label>
              <div className="flex gap-3">
                {(["merah", "kuning", "hijau"] as TriageLevel[]).map((level) => (
                  <button
                    key={level}
                    onClick={() => {
                      setSelectedLevel(level);
                      setShowTicket(false);
                    }}
                    className={`px-4 py-2 rounded-lg font-medium ${
                      selectedLevel === level
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                    }`}
                  >
                    {level.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {selectedLevel && (
              <div className="space-y-6">
                <TriageDisplay
                  triageLevel={selectedLevel}
                  patientName="Pasien Demo"
                  queueNumber="D001"
                  showTicket={showTicket}
                  onAction={handleAction}
                />

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowTicket(!showTicket)}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium flex items-center gap-2"
                  >
                    <Printer className="w-4 h-4" />
                    {showTicket ? "Sembunyikan Tiket" : "Tampilkan Tiket"}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Standalone Ticket */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Tiket Triage (Standalone)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <TriageTicket
              hospitalName="RS SIMRS"
              triageLevel="merah"
              patientName="Pasien Gawat Darurat"
              queueNumber="A001"
            />
            <TriageTicket
              hospitalName="RS SIMRS"
              triageLevel="kuning"
              patientName="Pasien Urgent"
              queueNumber="B002"
            />
            <TriageTicket
              hospitalName="RS SIMRS"
              triageLevel="hijau"
              patientName="Pasien Stabil"
              queueNumber="C003"
            />
          </div>
        </div>

        {/* Acceptance Criteria Checklist */}
        <div className="bg-white rounded-lg p-6 shadow-md">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Status Kriteria Penerimaan (Acceptance Criteria)
          </h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span className="text-gray-700">
                AC-5.4.1: Large, color-coded triage card
              </span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span className="text-gray-700">
                AC-5.4.2: Action recommendations per triage level
              </span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span className="text-gray-700">
                AC-5.4.3: Estimated wait time per triage level
              </span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span className="text-gray-700">
                AC-5.4.4: Quick action buttons (Kode Biru for MERAH)
              </span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span className="text-gray-700">
                AC-5.4.5: Print triage ticket with barcode
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
