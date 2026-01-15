"use client";

/**
 * WEB-S-4.1: Split-View Patient Context Demo
 *
 * Demo page showcasing the split-view consultation workspace with:
 * - Patient context panel (left, always visible)
 * - Consultation working area (right)
 * - Patient alerts, vitals, and quick actions
 */

import { ConsultationWorkspace } from "@/components/consultation/ConsultationWorkspace";

export default function ConsultationDemoPage() {
  // Mock patient data
  const patientData = {
    patient_id: 1,
    medical_record_number: "RM2024001",
    full_name: "AHMAD SUSANTO",
    date_of_birth: "1979-05-15",
    age: 45,
    gender: "Laki-laki",
    phone: "081234567890",
    blood_type: "A+",
    last_visit_date: "2026-01-10",
    chronic_problems: ["Diabetes Mellitus T2", "Hipertensi"],
    active_allergies: ["Penisilin - Anafilaksis"],
    current_medications: ["Metformin 500mg", "Amlodipine 10mg", "Captopril 25mg"],
  };

  return (
    <div className="h-screen">
      <ConsultationWorkspace
        patientId={patientData.patient_id}
        encounterId={12345}
      />
    </div>
  );
}
