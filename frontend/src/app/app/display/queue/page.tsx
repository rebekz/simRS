"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Building, Users, Clock, Volume2, Bell } from "lucide-react";

/**
 * WEB-S-3.4: Digital Queue Display Screens
 *
 * Key Features:
 * - Full-screen TV-optimized layout (16:9 aspect ratio)
 * - Department tabs with auto-rotate every 30 seconds
 * - Current queue number (LARGE, prominent display)
 * - Next 5 patients in queue
 * - Estimated wait time
 * - Hospital branding with SIMRS colors
 * - Auto-refresh every 10 seconds
 * - Marquee for announcements
 * - Audio alert when queue number changes
 * - Responsive to TV aspect ratios
 */

// ============================================================================
// TYPES
// ============================================================================

interface QueuePatient {
  id: string;
  queueNumber: string;
  name: string;
  department: string;
}

interface DepartmentQueue {
  department: string;
  label: string;
  color: string;
  currentQueue: string;
  currentPatient?: string;
  nextPatients: QueuePatient[];
  estimatedWait: string;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const MOCK_DEPARTMENT_QUEUES: DepartmentQueue[] = [
  {
    department: "igd",
    label: "Instalasi Gawat Darurat",
    color: "red",
    currentQueue: "IGD-001",
    currentPatient: "SUTRISNO",
    nextPatients: [
      { id: "2", queueNumber: "IGD-002", name: "MURNIATI", department: "igd" },
      { id: "3", queueNumber: "IGD-003", name: "JOKO SUSILO", department: "igd" },
      { id: "4", queueNumber: "IGD-004", name: "SRI WAHYUNI", department: "igd" },
      { id: "5", queueNumber: "IGD-005", name: "BAMBANG S", department: "igd" },
      { id: "6", queueNumber: "IGD-006", name: "RATNA SARI", department: "igd" },
    ],
    estimatedWait: "5 menit",
  },
  {
    department: "ana",
    label: "Poli Anak",
    color: "blue",
    currentQueue: "ANA-001",
    currentPatient: "AHMAD SUSANTO",
    nextPatients: [
      { id: "8", queueNumber: "ANA-002", name: "SITI RAHAYU", department: "ana" },
      { id: "9", queueNumber: "ANA-003", name: "BUDI SANTOSO", department: "ana" },
      { id: "10", queueNumber: "ANA-004", name: "DEWI LESTARI", department: "ana" },
      { id: "11", queueNumber: "ANA-005", name: "EKO PRASETYO", department: "ana" },
      { id: "12", queueNumber: "ANA-006", name: "RINA WATI", department: "ana" },
    ],
    estimatedWait: "10 menit",
  },
  {
    department: "int",
    label: "Poli Penyakit Dalam",
    color: "green",
    currentQueue: "INT-001",
    currentPatient: "AGUS SETIAWAN",
    nextPatients: [
      { id: "14", queueNumber: "INT-002", name: "LILIS SURYANI", department: "int" },
      { id: "15", queueNumber: "INT-003", name: "DEDI KURNIAWAN", department: "int" },
      { id: "16", queueNumber: "INT-004", name: "YULIATI", department: "int" },
      { id: "17", queueNumber: "INT-005", name: "HENDRO W", department: "int" },
      { id: "18", queueNumber: "INT-006", name: "SUSILO", department: "int" },
    ],
    estimatedWait: "15 menit",
  },
  {
    department: "bed",
    label: "Poli Bedah",
    color: "purple",
    currentQueue: "BED-001",
    currentPatient: "Drs. BAMBANG",
    nextPatients: [
      { id: "20", queueNumber: "BED-002", name: "SRI MULYANI", department: "bed" },
      { id: "21", queueNumber: "BED-003", name: "JOKO WIDODO", department: "bed" },
      { id: "22", queueNumber: "BED-004", name: "MEGA WATI", department: "bed" },
      { id: "23", queueNumber: "BED-005", name: "RUDI HARTONO", department: "bed" },
      { id: "24", queueNumber: "BED-006", name: "DENI K", department: "bed" },
    ],
    estimatedWait: "20 menit",
  },
  {
    department: "obg",
    label: "Poli Kandungan",
    color: "pink",
    currentQueue: "OBG-001",
    currentPatient: "NY. SUTARMI",
    nextPatients: [
      { id: "26", queueNumber: "OBG-002", name: "PUJI ASTUTI", department: "obg" },
      { id: "27", queueNumber: "OBG-003", name: "RINI MARLINA", department: "obg" },
      { id: "28", queueNumber: "OBG-004", name: "DEWI SARTIKA", department: "obg" },
      { id: "29", queueNumber: "OBG-005", name: "TATI S", department: "obg" },
      { id: "30", queueNumber: "OBG-006", name: "MINARNI", department: "obg" },
    ],
    estimatedWait: "12 menit",
  },
  {
    department: "mat",
    label: "Poli Mata",
    color: "teal",
    currentQueue: "MAT-001",
    currentPatient: "IR. SOEKARNO",
    nextPatients: [
      { id: "32", queueNumber: "MAT-002", name: "SRI REJEKI", department: "mat" },
      { id: "33", queueNumber: "MAT-003", name: "JUMADI", department: "mat" },
      { id: "34", queueNumber: "MAT-004", name: "SUKIRMAN", department: "mat" },
      { id: "35", queueNumber: "MAT-005", name: "WARJI", department: "mat" },
      { id: "36", queueNumber: "MAT-006", name:"PARNI", department: "mat" },
    ],
    estimatedWait: "8 menit",
  },
];

const ANNOUNCEMENTS = [
  "Selamat datang di RSUD Sehat Selalu. Mohon datang 15 menit sebelum jadwal pemeriksaan.",
  "Bersedia menunggu jika dokter terlambat karena pemeriksaan darurat.",
  "Jaga kebersihan area ruang tunggu. Buang sampah pada tempatnya.",
  "Mohon menyiapkan kartu berobat dan BPJS saat dipanggil.",
  "Terima kasih atas kepercayaan Anda berobat di RSUD Sehat Selalu.",
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function QueueDisplayPage() {
  const [currentDeptIndex, setCurrentDeptIndex] = useState(0);
  const [queueData, setQueueData] = useState<DepartmentQueue[]>(MOCK_DEPARTMENT_QUEUES);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [previousQueue, setPreviousQueue] = useState<string>("");
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [announcementIndex, setAnnouncementIndex] = useState(0);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const currentDeptQueue = queueData[currentDeptIndex];

  /**
   * AC-3.4.2: Auto-rotate departments every 30 seconds
   */
  useEffect(() => {
    const rotateInterval = setInterval(() => {
      setCurrentDeptIndex((prev) => (prev + 1) % queueData.length);
    }, 30000); // 30 seconds

    return () => clearInterval(rotateInterval);
  }, [queueData.length]);

  /**
   * AC-3.4.7: Auto-refresh every 10 seconds
   */
  useEffect(() => {
    const refreshInterval = setInterval(() => {
      setLastUpdate(new Date());
      // In production, fetch new queue data here
    }, 10000); // 10 seconds

    return () => clearInterval(refreshInterval);
  }, []);

  /**
   * AC-3.4.8: Marquee announcements - rotate every 15 seconds
   */
  useEffect(() => {
    const announcementInterval = setInterval(() => {
      setAnnouncementIndex((prev) => (prev + 1) % ANNOUNCEMENTS.length);
    }, 15000); // 15 seconds per announcement

    return () => clearInterval(announcementInterval);
  }, []);

  /**
   * AC-3.4.9: Audio alert when queue number changes
   */
  useEffect(() => {
    if (!soundEnabled) return;

    if (previousQueue && currentDeptQueue.currentQueue !== previousQueue) {
      // Play notification sound
      playAudioNotification();
      announceQueue(currentDeptQueue.currentQueue, currentDeptQueue.label);
    }

    setPreviousQueue(currentDeptQueue.currentQueue);
  }, [currentDeptQueue.currentQueue, currentDeptQueue.label, soundEnabled, previousQueue]);

  /**
   * Play audio notification
   */
  const playAudioNotification = useCallback(() => {
    if (!soundEnabled) return;

    // Create audio context for notification sound
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800; // 800Hz tone
    oscillator.type = "sine";

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  }, [soundEnabled]);

  /**
   * Text-to-speech announcement
   */
  const announceQueue = useCallback((queueNumber: string, department: string) => {
    if (!soundEnabled || !("speechSynthesis" in window)) return;

    const utterance = new SpeechSynthesisUtterance(
      `Nomor antrian ${queueNumber}, poli ${department}. Mohon menuju ruang pemeriksaan.`
    );

    utterance.lang = "id-ID";
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    window.speechSynthesis.speak(utterance);
  }, [soundEnabled]);

  /**
   * Manual department selection (for touch screens)
   */
  const handleDeptClick = (index: number) => {
    setCurrentDeptIndex(index);
  };

  /**
   * Toggle sound
   */
  const toggleSound = () => {
    setSoundEnabled(!soundEnabled);
  };

  /**
   * Get color classes based on department color
   */
  const getColorClasses = (color: string) => {
    const colorMap: Record<string, { bg: string; text: string; border: string }> = {
      red: {
        bg: "bg-gradient-to-br from-red-500 to-red-600",
        text: "text-white",
        border: "border-red-500",
      },
      blue: {
        bg: "bg-gradient-to-br from-blue-500 to-blue-600",
        text: "text-white",
        border: "border-blue-500",
      },
      green: {
        bg: "bg-gradient-to-br from-green-500 to-green-600",
        text: "text-white",
        border: "border-green-500",
      },
      purple: {
        bg: "bg-gradient-to-br from-purple-500 to-purple-600",
        text: "text-white",
        border: "border-purple-500",
      },
      pink: {
        bg: "bg-gradient-to-br from-pink-500 to-pink-600",
        text: "text-white",
        border: "border-pink-500",
      },
      teal: {
        bg: "bg-gradient-to-br from-teal-500 to-teal-600",
        text: "text-white",
        border: "border-teal-500",
      },
    };

    return colorMap[color] || colorMap.blue;
  };

  const colorClasses = getColorClasses(currentDeptQueue.color);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white flex flex-col overflow-hidden">
      {/* AC-3.4.6: Hospital Branding Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
        <div className="max-w-screen-2xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center shadow-lg">
                <Building className="w-10 h-10 text-blue-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight">RSUD Sehat Selalu</h1>
                <p className="text-blue-100 text-lg">Sistem Informasi Manajemen Rumah Sakit</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-blue-100">Terakhir diperbarui</p>
                <p className="text-lg font-semibold">{lastUpdate.toLocaleTimeString("id-ID")}</p>
              </div>

              {/* Sound Toggle */}
              <button
                type="button"
                onClick={toggleSound}
                className={`p-3 rounded-lg transition-colors ${
                  soundEnabled ? "bg-white bg-opacity-20" : "bg-white bg-opacity-10"
                }`}
                title={soundEnabled ? "Matikan suara" : "Hidupkan suara"}
              >
                {soundEnabled ? (
                  <Volume2 className="w-6 h-6" />
                ) : (
                  <Volume2 className="w-6 h-6 opacity-50" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* AC-3.4.8: Marquee for Announcements */}
      <div className="bg-yellow-100 border-b-4 border-yellow-400 py-3">
        <div className="max-w-screen-2xl mx-auto px-8">
          <div className="flex items-center gap-3">
            <Bell className="w-6 h-6 text-yellow-600 flex-shrink-0 animate-pulse" />
            <p className="text-lg font-medium text-yellow-900">
              {ANNOUNCEMENTS[announcementIndex]}
            </p>
          </div>
        </div>
      </div>

      {/* Department Tabs */}
      <div className="bg-white border-b-2 border-gray-200 shadow-sm">
        <div className="max-w-screen-2xl mx-auto px-8 py-4">
          <div className="flex gap-3 overflow-x-auto">
            {queueData.map((dept, index) => {
              const isActive = index === currentDeptIndex;
              const deptColorClasses = getColorClasses(dept.color);

              return (
                <button
                  key={dept.department}
                  type="button"
                  onClick={() => handleDeptClick(index)}
                  className={`flex-shrink-0 px-6 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 ${
                    isActive
                      ? `${deptColorClasses.bg} ${deptColorClasses.text} shadow-lg`
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {dept.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Queue Display */}
      <div className="flex-1 max-w-screen-2xl mx-auto w-full px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
          {/* Left Column: Current Queue */}
          <div className="lg:col-span-2">
            {/* AC-3.4.3: Current Queue Number (LARGE, Prominent) */}
            <div
              className={`${colorClasses.bg} rounded-3xl shadow-2xl p-12 text-center ${colorClasses.text} relative overflow-hidden`}
            >
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full -translate-y-1/2 translate-x-1/2"></div>
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-white rounded-full translate-y-1/2 -translate-x-1/2"></div>
              </div>

              {/* Content */}
              <div className="relative z-10">
                <p className="text-2xl font-medium mb-4 opacity-90">Sedang Melayani</p>

                {/* AC-3.4.3: LARGE Queue Number */}
                <div className="mb-6">
                  <p className="text-9xl font-black tracking-wider mb-2 drop-shadow-lg">
                    {currentDeptQueue.currentQueue}
                  </p>
                  {currentDeptQueue.currentPatient && (
                    <p className="text-4xl font-semibold opacity-90">
                      {currentDeptQueue.currentPatient}
                    </p>
                  )}
                </div>

                {/* AC-3.4.5: Estimated Wait Time */}
                <div className="flex items-center justify-center gap-3 text-xl">
                  <Clock className="w-8 h-8" />
                  <span className="font-semibold">
                    Estimasi Tunggu: {currentDeptQueue.estimatedWait}
                  </span>
                </div>
              </div>
            </div>

            {/* Progress Bar for Auto-Rotate */}
            <div className="mt-6 bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-full transition-all duration-1000 ease-linear"
                style={{
                  width: `${((30000 - ((lastUpdate.getTime() / 1000) % 30000) * 1000) / 30000) * 100}%`,
                }}
              />
            </div>
            <p className="text-center text-sm text-gray-600 mt-2">
              Rotasi otomatis dalam 30 detik
            </p>
          </div>

          {/* Right Column: Upcoming Queue */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <Users className="w-8 h-8 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Antrian Berikutnya</h2>
            </div>

            {/* AC-3.4.4: Next 5 Patients in Queue */}
            <div className="space-y-3">
              {currentDeptQueue.nextPatients.slice(0, 5).map((patient, index) => (
                <div
                  key={patient.id}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    index === 0
                      ? "bg-blue-50 border-blue-300 shadow-md"
                      : "bg-gray-50 border-gray-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-lg font-bold text-gray-900">{patient.queueNumber}</p>
                      <p className="text-base text-gray-700 mt-1">{patient.name}</p>
                    </div>
                    {index === 0 && (
                      <span className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-semibold">
                        Berikutnya
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Total Waiting */}
            <div className="mt-6 pt-6 border-t-2 border-gray-200">
              <div className="flex items-center justify-between text-lg">
                <span className="font-medium text-gray-700">Total Menunggu:</span>
                <span className="font-bold text-blue-600">{currentDeptQueue.nextPatients.length} pasien</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AC-3.4.10: Footer with 16:9 Optimization Info */}
      <div className="bg-gray-800 text-white py-4">
        <div className="max-w-screen-2xl mx-auto px-8">
          <div className="flex items-center justify-between text-sm">
            <p className="text-gray-300">
              Optimalkan tampilan untuk rasio aspek 16:9 (1920x1080)
            </p>
            <p className="text-gray-400">
              RSUD Sehat Selalu © 2026 • SIMRS v1.0
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
