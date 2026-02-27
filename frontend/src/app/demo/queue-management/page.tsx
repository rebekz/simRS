"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight, CheckCircle } from 'lucide-react';
import {
  QueueDashboard,
  type QueuePatient,
  type Department,
  type QueueStatus,
} from '@/components/queue';

export default function QueueManagementDemoPage() {
  const [lastAction, setLastAction] = useState<string | null>(null);

  const departments: Department[] = [
    { value: 'igd', label: 'IGD', color: 'red', priority: true },
    { value: 'ana', label: 'Poli Anak', color: 'blue', priority: false },
    { value: 'int', label: 'Penyakit Dalam', color: 'green', priority: false },
    { value: 'bed', label: 'Poli Bedah', color: 'purple', priority: false },
    { value: 'obg', label: 'Poli Kandungan', color: 'pink', priority: false },
    { value: 'mat', label: 'Poli Mata', color: 'teal', priority: false },
  ];

  const mockPatients: QueuePatient[] = [
    // Poli Anak (Children)
    {
      id: '1',
      rmNumber: 'RM2024001',
      name: 'AHMAD SUSANTO',
      queueNumber: 'ANA-001',
      department: 'ana',
      status: 'in-service',
      checkInTime: '08:15',
      waitTime: '15 menit',
      age: 8,
      priorities: [],
      phone: '081234567890',
    },
    {
      id: '2',
      rmNumber: 'RM2024002',
      name: 'SITI RAHAYU',
      queueNumber: 'ANA-002',
      department: 'ana',
      status: 'waiting',
      checkInTime: '08:30',
      waitTime: '0 menit',
      age: 5,
      priorities: [],
      phone: '081234567891',
    },
    {
      id: '3',
      rmNumber: 'RM2024003',
      name: 'BUDI SANTOSO',
      queueNumber: 'ANA-003',
      department: 'ana',
      status: 'waiting',
      checkInTime: '08:45',
      waitTime: '0 menit',
      age: 12,
      priorities: ['disabled'],
      phone: '081234567892',
    },
    {
      id: '4',
      rmNumber: 'RM2024004',
      name: 'DEWI LESTARI',
      queueNumber: 'ANA-004',
      department: 'ana',
      status: 'completed',
      checkInTime: '07:45',
      waitTime: '45 menit',
      age: 6,
      priorities: [],
      phone: '081234567893',
    },
    {
      id: '5',
      rmNumber: 'RM2024005',
      name: 'EKO PRASETYO',
      queueNumber: 'ANA-005',
      department: 'ana',
      status: 'waiting',
      checkInTime: '08:50',
      waitTime: '0 menit',
      age: 10,
      priorities: [],
      phone: '081234567894',
    },

    // Poli Penyakit Dalam (Internal Medicine)
    {
      id: '6',
      rmNumber: 'RM2024006',
      name: 'RINA WATI',
      queueNumber: 'INT-001',
      department: 'int',
      status: 'in-service',
      checkInTime: '08:00',
      waitTime: '30 menit',
      age: 45,
      priorities: ['elderly'],
      phone: '081234567895',
    },
    {
      id: '7',
      rmNumber: 'RM2024007',
      name: 'AGUS SETIAWAN',
      queueNumber: 'INT-002',
      department: 'int',
      status: 'waiting',
      checkInTime: '08:20',
      waitTime: '10 menit',
      age: 52,
      priorities: ['elderly'],
      phone: '081234567896',
    },
    {
      id: '8',
      rmNumber: 'RM2024008',
      name: 'LILIS SURYANI',
      queueNumber: 'INT-003',
      department: 'int',
      status: 'waiting',
      checkInTime: '08:35',
      waitTime: '0 menit',
      age: 38,
      priorities: ['pregnant'],
      phone: '081234567897',
    },
    {
      id: '9',
      rmNumber: 'RM2024009',
      name: 'DEDI KURNIAWAN',
      queueNumber: 'INT-004',
      department: 'int',
      status: 'completed',
      checkInTime: '07:30',
      waitTime: '1 jam',
      age: 48,
      priorities: [],
      phone: '081234567898',
    },

    // IGD (Emergency)
    {
      id: '10',
      rmNumber: 'RM2024010',
      name: 'SUTRISNO',
      queueNumber: 'IGD-001',
      department: 'igd',
      status: 'in-service',
      checkInTime: '08:10',
      waitTime: '5 menit',
      age: 55,
      priorities: ['emergency'],
      triageLevel: 'merah',
      phone: '081234567899',
    },
    {
      id: '11',
      rmNumber: 'RM2024011',
      name: 'MURNIATI',
      queueNumber: 'IGD-002',
      department: 'igd',
      status: 'waiting',
      checkInTime: '08:25',
      waitTime: '0 menit',
      age: 62,
      priorities: ['emergency', 'elderly'],
      triageLevel: 'kuning',
      phone: '081234567900',
    },
    {
      id: '12',
      rmNumber: 'RM2024012',
      name: 'JOKO SUSILO',
      queueNumber: 'IGD-003',
      department: 'igd',
      status: 'waiting',
      checkInTime: '08:40',
      waitTime: '0 menit',
      age: 35,
      priorities: ['emergency'],
      triageLevel: 'hijau',
      phone: '081234567901',
    },

    // Poli Bedah
    {
      id: '13',
      rmNumber: 'RM2024013',
      name: 'WAHYU HIDAYAT',
      queueNumber: 'BED-001',
      department: 'bed',
      status: 'waiting',
      checkInTime: '08:30',
      waitTime: '0 menit',
      age: 40,
      priorities: [],
      phone: '081234567902',
    },
    {
      id: '14',
      rmNumber: 'RM2024014',
      name: 'SRI MULYANI',
      queueNumber: 'BED-002',
      department: 'bed',
      status: 'in-service',
      checkInTime: '08:00',
      waitTime: '20 menit',
      age: 55,
      priorities: ['elderly'],
      phone: '081234567903',
    },

    // Poli Kandungan
    {
      id: '15',
      rmNumber: 'RM2024015',
      name: 'RATNA DEWI',
      queueNumber: 'OBG-001',
      department: 'obg',
      status: 'waiting',
      checkInTime: '08:45',
      waitTime: '0 menit',
      age: 28,
      priorities: ['pregnant'],
      phone: '081234567904',
    },

    // Poli Mata
    {
      id: '16',
      rmNumber: 'RM2024016',
      name: 'SUHARTONO',
      queueNumber: 'MAT-001',
      department: 'mat',
      status: 'waiting',
      checkInTime: '09:00',
      waitTime: '0 menit',
      age: 65,
      priorities: ['elderly'],
      phone: '081234567905',
    },
  ];

  const handleCallNext = (patient: QueuePatient) => {
    console.log('Calling patient:', patient);
    setLastAction(`Called: ${patient.name} (${patient.queueNumber})`);
  };

  const handleUpdateStatus = (patientId: string, status: QueueStatus) => {
    console.log('Updating status:', patientId, status);
    const patient = mockPatients.find(p => p.id === patientId);
    if (patient) {
      setLastAction(`Updated ${patient.name} to: ${status}`);
    }
  };

  const handleRefresh = () => {
    console.log('Refreshing queue data...');
    setLastAction('Queue data refreshed');
  };

  const handleExportPDF = () => {
    alert('PDF export functionality will be implemented with backend integration');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Demo Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto">
          {/* Breadcrumb */}
          <div className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
            <Link href="/demo" className="hover:text-gray-700">Demo</Link>
            <ChevronRight className="h-4 w-4" />
            <span className="text-gray-900">Queue Management Dashboard</span>
          </div>

          {/* Page Header */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              WEB-S-3.3: Queue Management Dashboard
            </h1>
            <p className="text-gray-600 mt-2">
              Real-time queue monitoring and patient flow management.
            </p>
          </div>

          {/* Acceptance Criteria */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="text-lg font-bold text-blue-900 mb-3">Acceptance Criteria</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">AC-3.3.1: Queue list by department</span>
                </label>
                <label className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">AC-3.3.2: Patient details (name, RM, queue, wait)</span>
                </label>
                <label className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">AC-3.3.3: Status badges (waiting/in-service/completed)</span>
                </label>
                <label className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">AC-3.3.4: Priority indicators (elderly/pregnant/disabled)</span>
                </label>
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">AC-3.3.5: Emergency queue (IGD) with triage levels</span>
                </label>
                <label className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">AC-3.3.6: Queue statistics</span>
                </label>
                <label className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">AC-3.3.7: Call next patient button</span>
                </label>
                <label className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">AC-3.3.8: Move to completed status</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Queue Dashboard */}
      <QueueDashboard
        patients={mockPatients}
        departments={departments}
        onCallNext={handleCallNext}
        onUpdateStatus={handleUpdateStatus}
        onRefresh={handleRefresh}
        onExportPDF={handleExportPDF}
        defaultDepartment="igd"
      />

      {/* Last Action Info */}
      {lastAction && (
        <div className="fixed bottom-4 right-4 bg-gray-900 rounded-lg p-4 shadow-lg max-w-sm">
          <h3 className="text-sm font-semibold text-gray-400 mb-1">Last Action:</h3>
          <p className="text-green-400 text-sm">{lastAction}</p>
        </div>
      )}

      {/* Demo Hint */}
      <div className="bg-amber-50 border-t border-amber-200 p-4">
        <div className="max-w-7xl mx-auto">
          <h3 className="font-medium text-amber-800 mb-2">Demo Hints</h3>
          <ul className="text-sm text-amber-700 space-y-1">
            <li>• Click department tabs to switch between polyclinics</li>
            <li>• Use "Panggil Berikutnya" to call the next waiting patient</li>
            <li>• IGD shows triage levels (Merah/Kuning/Hijau) for emergency prioritization</li>
            <li>• Priority badges show elderly (Lansia), pregnant (Hamil), disabled (Disabilitas)</li>
            <li>• Queue auto-refreshes every 30 seconds (simulated)</li>
          </ul>
        </div>
      </div>

      {/* Integration Example */}
      <div className="bg-gray-100 p-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Integration Example</h2>
          <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto">
{`import { QueueDashboard, type QueuePatient, type Department } from '@/components/queue';

const departments: Department[] = [
  { value: 'igd', label: 'IGD', color: 'red', priority: true },
  { value: 'ana', label: 'Poli Anak', color: 'blue' },
  // ...
];

// In admin queue page
<QueueDashboard
  patients={queuePatients}
  departments={departments}
  onCallNext={(patient) => {
    // Announce in waiting room
    announceQueue(patient.queueNumber);
    // Update status in database
    updatePatientStatus(patient.id, 'in-service');
  }}
  onUpdateStatus={(patientId, status) => {
    updatePatientStatus(patientId, status);
  }}
  onRefresh={() => refetchQueue()}
  onExportPDF={() => generateQueueReport()}
  defaultDepartment="igd"
/>`}
          </pre>
        </div>
      </div>
    </div>
  );
}
