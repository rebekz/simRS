"use client";

/**
 * New Prescription Page for STORY-017
 *
 * Standalone prescription writing interface accessible from:
 * - Patient menu
 * - Quick actions
 * - Pharmacy workflow
 */

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Prescription } from "lucide-react";
import { PrescriptionWriter } from "@/components/prescriptions/PrescriptionWriter";

export default function NewPrescriptionPage() {
  const router = useRouter();
  const params = useParams();
  const patientId = params.id ? parseInt(params.id as string) : 0;

  const [savedPrescription, setSavedPrescription] = useState<any>(null);

  const handleSavePrescription = (prescription: any) => {
    setSavedPrescription(prescription);
    // Optionally redirect to prescription details
    // router.push(`/app/prescriptions/${prescription.id}`);
  };

  const handleCancel = () => {
    if (savedPrescription) {
      router.push(`/app/patients/${patientId}`);
    } else {
      router.back();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href={`/app/patients/${patientId}`}
                className="text-gray-400 hover:text-gray-600"
              >
                <ArrowLeft className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                  <Prescription className="h-6 w-6 mr-2" />
                  New Prescription
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  Patient ID: {patientId}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <PrescriptionWriter
          patientId={patientId}
          onSave={handleSavePrescription}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
}
