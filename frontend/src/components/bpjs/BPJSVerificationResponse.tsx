"""BPJS Verification Response Component

Comprehensive BPJS verification response management with:
- Query list
- Response editor
- Document attachment
- Response history
- Status tracking
"""

import { useState, useEffect } from 'react';
import {
  MessageSquare,
  Send,
  Paperclip,
  Clock,
  CheckCircle,
  AlertCircle,
  FileText,
  Download,
  Eye,
  User,
  Calendar,
  RefreshCw,
  XCircle,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

// Types
interface Query {
  id: number;
  claim_id: string;
  query_code: string;
  query_type: 'admin' | 'medical' | 'document' | 'tariff';
  question: string;
  category: string;
  asked_date: string;
  deadline_date: string;
  status: 'pending' | 'responded' | 'closed';
  responses: QueryResponse[];
  attachments: QueryAttachment[];
}

interface QueryResponse {
  id: number;
  query_id: number;
  response_text: string;
  responded_by: string;
  responded_date: string;
  attachments: string[];
  status: 'draft' | 'submitted' | 'verified' | 'rejected';
  verification_notes?: string;
}

interface QueryAttachment {
  id: number;
  query_id: number;
  file_name: string;
  file_url: string;
  file_size: number;
  upload_date: string;
}

interface ClaimQuerySummary {
  claim_id: string;
  patient_name: string;
  sep_number: string;
  total_queries: number;
  pending_queries: number;
  urgent_queries: number;
  deadline_date: string | null;
}

export function BPJSVerificationResponse({ claimId }: { claimId?: string }) {
  const [claimSummary, setClaimSummary] = useState<ClaimQuerySummary | null>(null);
  const [queries, setQueries] = useState<Query[]>([]);
  const [selectedQuery, setSelectedQuery] = useState<Query | null>(null);
  const [responseText, setResponseText] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showResponseHistory, setShowResponseHistory] = useState(false);

  useEffect(() => {
    if (claimId) {
      loadClaimQueries(claimId);
    }
  }, [claimId]);

  const loadClaimQueries = async (claimId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/bpjs/claims/${claimId}/queries`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setClaimSummary(data.summary);
        setQueries(data.queries);
      }
    } catch (error) {
      console.error('Gagal memuat query:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const submitResponse = async () => {
    if (!selectedQuery || !responseText.trim()) return;

    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('query_id', selectedQuery.id.toString());
      formData.append('response_text', responseText);

      attachments.forEach((file, idx) => {
        formData.append(`attachment_${idx}`, file);
      });

      const response = await fetch('/api/v1/bpjs/queries/respond', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        setResponseText('');
        setAttachments([]);
        if (claimId) {
          loadClaimQueries(claimId);
        }
        alert('Jawaban berhasil dikirim!');
      }
    } catch (error) {
      console.error('Gagal submit jawaban:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const downloadAttachment = async (attachment: QueryAttachment) => {
    try {
      const response = await fetch(attachment.file_url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = attachment.file_name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Gagal download lampiran:', error);
    }
  };

  const getQueryTypeLabel = (type: Query['query_type']) => {
    switch (type) {
      case 'admin':
        return 'Administrasi';
      case 'medical':
        return 'Medis';
      case 'document':
        return 'Dokumen';
      case 'tariff':
        return 'Tarif';
      default:
        return type;
    }
  };

  const getQueryTypeBadge = (type: Query['query_type']) => {
    switch (type) {
      case 'admin':
        return <Badge variant="info">Administrasi</Badge>;
      case 'medical':
        return <Badge variant="warning">Medis</Badge>;
      case 'document':
        return <Badge variant="neutral">Dokumen</Badge>;
      case 'tariff':
        return <Badge variant="error">Tarif</Badge>;
      default:
        return <Badge variant="neutral">{type}</Badge>;
    }
  };

  const getStatusBadge = (status: Query['status']) => {
    switch (status) {
      case 'pending':
        return <Badge variant="warning" dot>Pending</Badge>;
      case 'responded':
        return <Badge variant="info">Responded</Badge>;
      case 'closed':
        return <Badge variant="success">Closed</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const getDeadlineStatus = (deadline: string) => {
    const days = Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (days < 0) return 'expired';
    if (days <= 2) return 'urgent';
    if (days <= 7) return 'warning';
    return 'normal';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (!claimId) {
    return (
      <div className="bg-white shadow rounded-lg p-6 text-center">
        <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-500">Pilih klaim untuk melihat query verifikasi</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <MessageSquare className="h-6 w-6 mr-2" />
            Respon Verifikasi Klaim
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola respon query dari verifikator BPJS
          </p>
        </div>
        <button
          onClick={() => claimId && loadClaimQueries(claimId)}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Claim Summary */}
      {claimSummary && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-gray-500">Nama Pasien</p>
              <p className="text-sm font-medium text-gray-900">{claimSummary.patient_name}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">No. SEP</p>
              <p className="text-sm font-medium text-gray-900">{claimSummary.sep_number}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Total Query</p>
              <p className="text-sm font-medium text-gray-900">{claimSummary.total_queries}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Pending</p>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-orange-600">{claimSummary.pending_queries}</span>
                {claimSummary.urgent_queries > 0 && (
                  <Badge variant="error" dot>Urgent</Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Query List */}
      <div className="bg-white shadow rounded-lg">
        <div className="p-4 border-b">
          <h2 className="text-lg font-medium text-gray-900">Daftar Query</h2>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : queries.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Tidak ada query untuk klaim ini</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {queries.map((query) => {
              const deadlineStatus = getDeadlineStatus(query.deadline_date);
              return (
                <div key={query.id} className="p-4 hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedQuery(query)}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-medium text-gray-900">{query.query_code}</span>
                        {getQueryTypeBadge(query.query_type)}
                        {getStatusBadge(query.status)}
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{query.question}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div className="flex items-center">
                          <Calendar className="h-3 w-3 mr-1" />
                          {formatDate(query.asked_date)}
                        </div>
                        <div className={`flex items-center ${
                          deadlineStatus === 'expired' ? 'text-red-600' :
                          deadlineStatus === 'urgent' ? 'text-orange-600' :
                          deadlineStatus === 'warning' ? 'text-yellow-600' :
                          'text-gray-500'
                        }`}>
                          <Clock className="h-3 w-3 mr-1" />
                          Deadline: {formatDate(query.deadline_date)}
                        </div>
                        {query.attachments.length > 0 && (
                          <div className="flex items-center">
                            <Paperclip className="h-3 w-3 mr-1" />
                            {query.attachments.length} lampiran
                          </div>
                        )}
                      </div>
                    </div>
                    <Eye className="h-5 w-5 text-gray-400" />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Query Detail & Response */}
      {selectedQuery && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-medium text-gray-900">Detail Query</h2>
            <button
              onClick={() => setSelectedQuery(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              <XCircle className="h-6 w-6" />
            </button>
          </div>

          <div className="space-y-6">
            {/* Query Info */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">{selectedQuery.query_code}</span>
                  {getQueryTypeBadge(selectedQuery.query_type)}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Status:</span>
                  {getStatusBadge(selectedQuery.status)}
                </div>
              </div>
              <p className="text-sm text-gray-700 mb-3">{selectedQuery.question}</p>
              <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                <div className="flex items-center">
                  <Calendar className="h-3 w-3 mr-1" />
                  Ditanyakan: {formatDate(selectedQuery.asked_date)}
                </div>
                <div className={`flex items-center ${
                  getDeadlineStatus(selectedQuery.deadline_date) === 'expired' ? 'text-red-600' :
                  getDeadlineStatus(selectedQuery.deadline_date) === 'urgent' ? 'text-orange-600' :
                  'text-gray-500'
                }`}>
                  <Clock className="h-3 w-3 mr-1" />
                  Deadline: {formatDate(selectedQuery.deadline_date)}
                </div>
              </div>
            </div>

            {/* Attachments */}
            {selectedQuery.attachments.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Lampiran</h3>
                <div className="space-y-2">
                  {selectedQuery.attachments.map((attachment) => (
                    <div key={attachment.id} className="flex items-center justify-between border rounded-lg p-3 bg-gray-50">
                      <div className="flex items-center">
                        <FileText className="h-4 w-4 text-gray-400 mr-2" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{attachment.file_name}</p>
                          <p className="text-xs text-gray-500">{formatFileSize(attachment.file_size)}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => downloadAttachment(attachment)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Response History */}
            {selectedQuery.responses.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-gray-900">Riwayat Respon</h3>
                  <button
                    onClick={() => setShowResponseHistory(!showResponseHistory)}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    {showResponseHistory ? 'Sembunyikan' : 'Tampilkan'}
                  </button>
                </div>

                {showResponseHistory && (
                  <div className="space-y-3">
                    {selectedQuery.responses.map((response) => (
                      <div key={response.id} className="border rounded-lg p-4 bg-blue-50">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4 text-gray-400" />
                            <span className="text-sm font-medium text-gray-900">{response.responded_by}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">{formatDate(response.responded_date)}</span>
                            {response.status === 'verified' ? (
                              <Badge variant="success">Verified</Badge>
                            ) : response.status === 'rejected' ? (
                              <Badge variant="error">Rejected</Badge>
                            ) : (
                              <Badge variant="info">Submitted</Badge>
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">{response.response_text}</p>
                        {response.verification_notes && (
                          <p className="text-xs text-gray-600 italic">{response.verification_notes}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Response Form */}
            {selectedQuery.status === 'pending' && (
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Buat Respon</h3>
                <div className="space-y-4">
                  <div>
                    <textarea
                      value={responseText}
                      onChange={(e) => setResponseText(e.target.value)}
                      placeholder="Tulis jawaban Anda..."
                      rows={5}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  {/* File Attachments */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Lampiran Dokumen (Opsional)
                    </label>
                    <input
                      type="file"
                      multiple
                      onChange={(e) => {
                        if (e.target.files) {
                          setAttachments(Array.from(e.target.files));
                        }
                      }}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                    {attachments.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {attachments.map((file, idx) => (
                          <p key={idx} className="text-xs text-gray-600">
                            <Paperclip className="h-3 w-3 inline mr-1" />
                            {file.name} ({formatFileSize(file.size)})
                          </p>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Submit Button */}
                  <div className="flex justify-end">
                    <button
                      onClick={submitResponse}
                      disabled={!responseText.trim() || isSubmitting}
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Sending...
                        </>
                      ) : (
                        <>
                          <Send className="h-4 w-4 mr-2" />
                          Kirim Respon
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
