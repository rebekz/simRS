"use client";

import React, { useState, useEffect } from 'react';

// Types
interface QueueTicket {
  id: number;
  ticket_number: string;
  patient_name: string;
  department: string;
  priority: 'normal' | 'priority' | 'emergency';
  status: 'waiting' | 'called' | 'served' | 'skipped' | 'cancelled';
  queue_position?: number;
  people_ahead: number;
  estimated_wait_minutes?: number;
  serving_counter?: number;
  issued_at: string;
}

interface QueueDisplayProps {
  department: 'poli' | 'farmasi' | 'lab' | 'radiologi' | 'kasir';
  refreshInterval?: number;  // seconds
}

const DEPARTMENT_NAMES: Record<string, string> = {
  'poli': 'Poli Rawat Jalan',
  'farmasi': 'Farmasi',
  'lab': 'Laboratorium',
  'radiologi': 'Radiologi',
  'kasir': 'Kasir',
};

export default function QueueDisplay({ department, refreshInterval = 10 }: QueueDisplayProps) {
  const [tickets, setTickets] = useState<QueueTicket[]>([]);
  const [currentTicket, setCurrentTicket] = useState<QueueTicket | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQueue();
    const interval = setInterval(fetchQueue, refreshInterval * 1000);
    return () => clearInterval(interval);
  }, [department, refreshInterval]);

  async function fetchQueue() {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/queue/${department}/tickets?status=waiting&page_size=20`);
      const data = await response.json();
      setTickets(data.waiting || []);

      // Get currently serving ticket
      const calledResponse = await fetch(`/api/v1/queue/${department}/tickets?status=called&page_size=1`);
      const calledData = await calledResponse.json();
      if (calledData.waiting && calledData.waiting.length > 0) {
        setCurrentTicket(calledData.waiting[0]);
      } else {
        setCurrentTicket(null);
      }
    } catch (error) {
      console.error('Failed to fetch queue:', error);
    } finally {
      setLoading(false);
    }
  }

  function getPriorityColor(priority: string): string {
    switch (priority) {
      case 'emergency':
        return 'bg-red-500 text-white';
      case 'priority':
        return 'bg-orange-500 text-white';
      default:
        return 'bg-blue-500 text-white';
    }
  }

  function getPriorityLabel(priority: string): string {
    switch (priority) {
      case 'emergency':
        return 'DARURAT';
      case 'priority':
        return 'PRIORITAS';
      default:
        return '';
    }
  }

  return (
    <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg shadow-2xl p-6 text-white">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">{DEPARTMENT_NAMES[department]}</h1>
          <p className="text-blue-200">Sistem Antrian Terpadu</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-blue-200">Total Menunggu</div>
          <div className="text-4xl font-bold">{tickets.length}</div>
        </div>
      </div>

      {/* Currently Serving */}
      {currentTicket && (
        <div className="bg-white bg-opacity-20 backdrop-blur rounded-xl p-6 mb-6 border-2 border-yellow-400">
          <div className="text-center">
            <div className="text-yellow-300 text-lg mb-2">SEKARANG MELAYANI</div>
            <div className="text-7xl font-bold mb-2">{currentTicket.ticket_number}</div>
            <div className="text-2xl mb-1">{currentTicket.patient_name}</div>
            {currentTicket.serving_counter && (
              <div className="text-xl text-blue-200">Loket {currentTicket.serving_counter}</div>
            )}
          </div>
        </div>
      )}

      {/* Queue List */}
      <div className="bg-white bg-opacity-10 backdrop-blur rounded-xl p-6">
        <h2 className="text-xl font-semibold mb-4">Antrian Menunggu</h2>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          </div>
        ) : tickets.length === 0 ? (
          <div className="text-center py-8 text-blue-200">
            Tidak ada antrian saat ini
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {tickets.map((ticket, index) => (
              <div
                key={ticket.id}
                className="bg-white rounded-lg p-4 text-gray-800 shadow-lg"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="text-3xl font-bold text-blue-600">
                    {ticket.ticket_number}
                  </div>
                  {ticket.priority !== 'normal' && (
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getPriorityColor(ticket.priority)}`}>
                      {getPriorityLabel(ticket.priority)}
                    </span>
                  )}
                </div>
                <div className="font-semibold text-gray-900 mb-1 truncate">
                  {ticket.patient_name}
                </div>
                <div className="text-sm text-gray-600">
                  {ticket.queue_position && (
                    <span>Antrian #{ticket.queue_position}</span>
                  )}
                </div>
                {ticket.estimated_wait_minutes && (
                  <div className="text-sm text-gray-600 mt-1">
                    Estimasi: ~{ticket.estimated_wait_minutes} menit
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-6 text-center text-blue-200 text-sm">
        <p>Last updated: {new Date().toLocaleTimeString('id-ID')}</p>
      </div>
    </div>
  );
}
