"use client";

import React, { useState, useEffect } from 'react';
import { Users, Clock, AlertCircle, Volume2, VolumeX, RefreshCw, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

// Types
interface QueuePatient {
  id: string;
  queue_number: string;
  patient_name: string;
  department: string;
  doctor_name: string;
  status: 'waiting' | 'called' | 'serving' | 'completed' | 'skipped';
  check_in_time: string;
  queue_position: number;
  people_ahead: number;
  estimated_wait_minutes?: number;
  serving_counter?: number;
}

interface QueueStats {
  total_waiting: number;
  total_called: number;
  total_completed: number;
  average_wait_minutes: number;
  fastest_wait_minutes: number;
  longest_wait_minutes: number;
}

interface QueueDisplayProps {
  department: string;
  doctorId?: string;
  refreshInterval?: number; // seconds
  autoRefresh?: boolean;
  soundEnabled?: boolean;
  digitalMode?: boolean; // For large screen displays
}

export default function QueueDisplay({
  department,
  doctorId,
  refreshInterval = 10,
  autoRefresh = true,
  soundEnabled = false,
  digitalMode = false,
}: QueueDisplayProps) {
  const [queue, setQueue] = useState<QueuePatient[]>([]);
  const [currentServing, setCurrentServing] = useState<QueuePatient | null>(null);
  const [lastCalled, setLastCalled] = useState<QueuePatient | null>(null);
  const [stats, setStats] = useState<QueueStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [soundOn, setSoundOn] = useState(soundEnabled);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    fetchQueue();
    if (autoRefresh) {
      const interval = setInterval(fetchQueue, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [department, doctorId, refreshInterval, autoRefresh]);

  // Update current time every second for digital display
  useEffect(() => {
    const timeInterval = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timeInterval);
  }, []);

  async function fetchQueue() {
    setRefreshing(true);
    try {
      const params = new URLSearchParams();
      if (doctorId) params.append('doctor_id', doctorId);

      const response = await fetch(`/api/v1/appointments/queue/${department}?${params}`);
      const data = await response.json();

      setQueue(data.queue || []);
      setCurrentServing(data.current_serving || null);
      setLastCalled(data.last_called || null);
      setStats(data.stats || null);
    } catch (error) {
      console.error('Failed to fetch queue:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  function handleManualRefresh() {
    fetchQueue();
  }

  function toggleSound() {
    setSoundOn(!soundOn);
    // In real implementation, would trigger sound playback
  }

  function getDepartmentName(dept: string): string {
    const names: Record<string, string> = {
      'umum': 'Poli Umum',
      'anak': 'Poli Anak',
      'gigi': 'Poli Gigi',
      'kandungan': 'Poli Kandungan',
      'penyakit-dalam': 'Poli Penyakit Dalam',
      'farmasi': 'Farmasi',
      'lab': 'Laboratorium',
      'radiologi': 'Radiologi',
    };
    return names[dept] || dept;
  }

  function getStatusColor(status: QueuePatient['status']): string {
    switch (status) {
      case 'waiting':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'called':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'serving':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'completed':
        return 'bg-gray-100 text-gray-600 border-gray-300';
      case 'skipped':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  }

  function getStatusLabel(status: QueuePatient['status']): string {
    const labels: Record<string, string> = {
      waiting: 'Menunggu',
      called: 'Dipanggil',
      serving: 'Dilayani',
      completed: 'Selesai',
      skipped: 'Dilewati',
    };
    return labels[status] || status;
  }

  // Digital display mode for large screens
  if (digitalMode) {
    return (
      <div className="bg-gradient-to-br from-blue-700 via-blue-600 to-blue-800 rounded-2xl shadow-2xl p-8 text-white min-h-screen">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">{getDepartmentName(department)}</h1>
            <p className="text-blue-200 text-lg">Sistem Antrian Terpadu</p>
          </div>

          <div className="text-right">
            <div className="text-6xl font-bold">{queue.length}</div>
            <div className="text-blue-200 text-xl">Pasien Menunggu</div>
          </div>
        </div>

        {/* Clock */}
        <div className="text-center mb-8">
          <div className="text-7xl font-bold font-mono">
            {currentTime.toLocaleTimeString('id-ID', {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            })}
          </div>
          <div className="text-blue-200 text-xl mt-2">
            {currentTime.toLocaleDateString('id-ID', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </div>
        </div>

        {/* Current Serving */}
        {currentServing && (
          <div className="bg-white/10 backdrop-blur-sm border-4 border-yellow-400 rounded-2xl p-8 mb-8">
            <div className="text-center">
              <div className="text-yellow-300 text-3xl mb-4 font-semibold">SEKARANG MELAYANI</div>
              <div className="text-9xl font-bold mb-6 text-yellow-300">
                {currentServing.queue_number}
              </div>
              <div className="text-4xl font-semibold mb-2">{currentServing.patient_name}</div>
              {currentServing.serving_counter && (
                <div className="text-2xl text-blue-200 mt-4">
                  Loket {currentServing.serving_counter}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Last Called */}
        {lastCalled && lastCalled.id !== currentServing?.id && (
          <div className="bg-white/10 backdrop-blur-sm border-2 border-blue-300 rounded-2xl p-6 mb-8">
            <div className="text-center">
              <div className="text-blue-200 text-2xl mb-2">TERAKHIR DIPANGGIL</div>
              <div className="text-5xl font-bold mb-2">{lastCalled.queue_number}</div>
              <div className="text-2xl">{lastCalled.patient_name}</div>
            </div>
          </div>
        )}

        {/* Queue List */}
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
          <h2 className="text-2xl font-bold mb-6">Antrian Menunggu</h2>

          {loading ? (
            <div className="text-center py-12">
              <Loader2 className="w-16 h-16 animate-spin mx-auto mb-4" />
              <p>Memuat antrian...</p>
            </div>
          ) : queue.filter(q => q.status === 'waiting').length === 0 ? (
            <div className="text-center py-12 text-blue-200 text-2xl">
              Tidak ada antrian saat ini
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {queue
                .filter(q => q.status === 'waiting')
                .slice(0, 10)
                .map(patient => (
                  <div
                    key={patient.id}
                    className="bg-white rounded-xl p-6 text-gray-800 shadow-lg"
                  >
                    <div className="text-4xl font-bold text-blue-600 mb-3">
                      {patient.queue_number}
                    </div>
                    <div className="font-semibold text-lg mb-2 truncate">
                      {patient.patient_name}
                    </div>
                    <div className="text-sm text-gray-600">
                      Antrian #{patient.queue_position}
                    </div>
                    {patient.estimated_wait_minutes && (
                      <div className="text-sm text-gray-600 mt-2">
                        ~{patient.estimated_wait_minutes} menit
                      </div>
                    )}
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-blue-200 text-lg">
          <p>Last Update: {currentTime.toLocaleTimeString('id-ID')}</p>
        </div>
      </div>
    );
  }

  // Standard display mode
  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{getDepartmentName(department)}</h2>
              <p className="text-gray-600 mt-1">Antrian Pasien</p>
            </div>

            <div className="flex items-center gap-2">
              {/* Sound Toggle */}
              <button
                onClick={toggleSound}
                className={cn(
                  'p-2 rounded-lg border transition-colors',
                  soundOn
                    ? 'bg-blue-50 border-blue-300 text-blue-600'
                    : 'bg-gray-50 border-gray-300 text-gray-600'
                )}
              >
                {soundOn ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>

              {/* Refresh Button */}
              <button
                onClick={handleManualRefresh}
                className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-600 transition-colors"
                disabled={refreshing}
              >
                <RefreshCw className={cn('w-5 h-5', refreshing && 'animate-spin')} />
              </button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card variant="elevated">
            <CardBody className="text-center">
              <div className="text-3xl font-bold text-blue-600">{stats.total_waiting}</div>
              <div className="text-sm text-gray-600 mt-1">Menunggu</div>
            </CardBody>
          </Card>

          <Card variant="elevated">
            <CardBody className="text-center">
              <div className="text-3xl font-bold text-yellow-600">{stats.total_called}</div>
              <div className="text-sm text-gray-600 mt-1">Dipanggil</div>
            </CardBody>
          </Card>

          <Card variant="elevated">
            <CardBody className="text-center">
              <div className="text-3xl font-bold text-green-600">{stats.total_completed}</div>
              <div className="text-sm text-gray-600 mt-1">Selesai</div>
            </CardBody>
          </Card>

          <Card variant="elevated">
            <CardBody className="text-center">
              <div className="text-3xl font-bold text-gray-600">
                {stats.average_wait_minutes}
              </div>
              <div className="text-sm text-gray-600 mt-1">Menit Rata-rata</div>
            </CardBody>
          </Card>
        </div>
      )}

      {/* Current Serving */}
      {currentServing && (
        <Card variant="elevated" className="border-2 border-yellow-400">
          <CardBody>
            <div className="text-center">
              <div className="text-sm font-semibold text-yellow-600 mb-2">SEKARANG MELAYANI</div>
              <div className="text-6xl font-bold text-yellow-600 mb-3">
                {currentServing.queue_number}
              </div>
              <div className="text-xl font-semibold text-gray-900 mb-1">
                {currentServing.patient_name}
              </div>
              <div className="text-gray-600">
                {currentServing.doctor_name}
              </div>
              {currentServing.serving_counter && (
                <div className="text-sm text-gray-600 mt-2">
                  Loket {currentServing.serving_counter}
                </div>
              )}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Queue List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-600" />
              Daftar Antrian
            </h3>
            <div className="text-sm text-gray-600">
              {queue.filter(q => q.status === 'waiting').length} menunggu
            </div>
          </div>
        </CardHeader>

        <CardBody>
          {loading ? (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-3" />
              <p className="text-gray-600">Memuat antrian...</p>
            </div>
          ) : queue.length === 0 ? (
            <div className="text-center py-12">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Tidak ada antrian saat ini</p>
            </div>
          ) : (
            <div className="space-y-3">
              {queue.map((patient, index) => (
                <div
                  key={patient.id}
                  className={cn(
                    'flex items-center justify-between p-4 rounded-lg border-2 transition-all',
                    patient.status === 'serving' && 'border-green-400 bg-green-50',
                    patient.status === 'called' && 'border-yellow-400 bg-yellow-50',
                    patient.status === 'waiting' && 'border-gray-200 bg-white hover:border-blue-200',
                    patient.status === 'skipped' && 'border-red-200 bg-red-50 opacity-60',
                    patient.status === 'completed' && 'border-gray-200 bg-gray-50 opacity-50'
                  )}
                >
                  {/* Queue Number and Position */}
                  <div className="flex items-center gap-4">
                    <div
                      className={cn(
                        'w-16 h-16 rounded-lg flex items-center justify-center font-bold text-xl flex-shrink-0',
                        patient.status === 'serving' && 'bg-green-600 text-white',
                        patient.status === 'called' && 'bg-yellow-500 text-white',
                        patient.status === 'waiting' && 'bg-blue-100 text-blue-700',
                        patient.status === 'skipped' && 'bg-red-100 text-red-700',
                        patient.status === 'completed' && 'bg-gray-200 text-gray-600'
                      )}
                    >
                      {patient.queue_number}
                    </div>

                    <div>
                      <div className="font-semibold text-gray-900">
                        {patient.patient_name}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        {patient.doctor_name}
                      </div>
                      <div className="flex items-center gap-3 mt-2 text-sm">
                        <span className="text-gray-500">
                          Antrian ke-{patient.queue_position}
                        </span>
                        {patient.estimated_wait_minutes && (
                          <span className="flex items-center gap-1 text-gray-600">
                            <Clock className="w-4 h-4" />
                            ~{patient.estimated_wait_minutes} menit
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <span
                    className={cn(
                      'px-3 py-1 rounded-full text-sm font-medium border',
                      getStatusColor(patient.status)
                    )}
                  >
                    {getStatusLabel(patient.status)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
