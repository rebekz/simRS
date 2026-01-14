"""BPJS Document Manager Component

Comprehensive BPJS document management with:
- Required documents list
- Document upload (SEP, resume, DPJP, invoice)
- Document verification status
- Bulk upload
- Missing documents alert
"""

import { useState, useEffect, useRef } from 'react';
import {
  FileText,
  Upload,
  CheckCircle,
  XCircle,
  AlertCircle,
  Download,
  Trash2,
  Eye,
  File,
  FileCheck,
  Plus,
  RefreshCw,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

// Types
interface Document {
  id: number;
  claim_id: string;
  document_type: DocumentType;
  file_name: string;
  file_url: string;
  file_size: number;
  upload_date: string;
  verification_status: 'pending' | 'verified' | 'rejected';
  verified_by?: string;
  verified_date?: string;
  rejection_reason?: string;
}

type DocumentType = 'sep' | 'resume_medis' | 'dpjp' | 'invoice' | 'billing' | 'laboratorium' | 'radiologi' | 'obat' | 'lainnya';

interface DocumentRequirement {
  type: DocumentType;
  name: string;
  description: string;
  required: boolean;
  file_types: string[];
  max_size_mb: number;
}

interface ClaimDocuments {
  claim_id: string;
  patient_name: string;
  sep_number: string;
  status: string;
  documents: Document[];
  missing_required: DocumentType[];
}

export function BPJSDocumentManager({ claimId }: { claimId?: string }) {
  const [claimDocuments, setClaimDocuments] = useState<ClaimDocuments | null>(null);
  const [uploading, setUploading] = useState<DocumentType | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [showBulkUpload, setShowBulkUpload] = useState(false);
  const [bulkFiles, setBulkFiles] = useState<Map<DocumentType, File>>(new Map());
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const documentRequirements: DocumentRequirement[] = [
    {
      type: 'sep',
      name: 'Surat Eligibilitas Peserta (SEP)',
      description: 'Surat jaminan dari BPJS',
      required: true,
      file_types: ['pdf'],
      max_size_mb: 5,
    },
    {
      type: 'resume_medis',
      name: 'Resume Medis',
      description: 'Ringkasan medis pasien saat rawat inap',
      required: true,
      file_types: ['pdf'],
      max_size_mb: 10,
    },
    {
      type: 'dpjp',
      name: 'Surat DPJP',
      description: 'Surat Dokter Pemberi Pelayanan',
      required: true,
      file_types: ['pdf'],
      max_size_mb: 5,
    },
    {
      type: 'invoice',
      name: 'Faktur Rumah Sakit',
      description: 'Faktur tagihan pelayanan',
      required: true,
      file_types: ['pdf'],
      max_size_mb: 5,
    },
    {
      type: 'billing',
      name: 'Billing',
      description: 'Detail biaya per layanan',
      required: true,
      file_types: ['pdf', 'xlsx'],
      max_size_mb: 5,
    },
    {
      type: 'laboratorium',
      name: 'Hasil Laboratorium',
      description: 'Hasil pemeriksaan lab (jika ada)',
      required: false,
      file_types: ['pdf'],
      max_size_mb: 10,
    },
    {
      type: 'radiologi',
      name: 'Hasil Radiologi',
      description: 'Hasil pemeriksaan radiologi (jika ada)',
      required: false,
      file_types: ['pdf'],
      max_size_mb: 10,
    },
    {
      type: 'obat',
      name: 'Resep Obat',
      description: 'Daftar obat yang diberikan (jika ada)',
      required: false,
      file_types: ['pdf'],
      max_size_mb: 5,
    },
    {
      type: 'lainnya',
      name: 'Dokumen Lainnya',
      description: 'Dokumen pendukung lain',
      required: false,
      file_types: ['pdf'],
      max_size_mb: 10,
    },
  ];

  useEffect(() => {
    if (claimId) {
      loadClaimDocuments(claimId);
    }
  }, [claimId]);

  const loadClaimDocuments = async (claimId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/bpjs/claims/${claimId}/documents`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setClaimDocuments(data);
      }
    } catch (error) {
      console.error('Gagal memuat dokumen:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const uploadDocument = async (docType: DocumentType) => {
    if (!selectedFile || !claimDocuments) return;

    setUploading(docType);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('document_type', docType);
      formData.append('claim_id', claimDocuments.claim_id);

      const response = await fetch('/api/v1/bpjs/documents/upload', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        setSelectedFile(null);
        loadClaimDocuments(claimDocuments.claim_id);
      } else {
        const error = await response.json();
        alert(`Gagal upload: ${error.message}`);
      }
    } catch (error) {
      console.error('Gagal upload dokumen:', error);
    } finally {
      setUploading(null);
    }
  };

  const deleteDocument = async (documentId: number) => {
    if (!confirm('Apakah Anda yakin ingin menghapus dokumen ini?')) return;

    try {
      const response = await fetch(`/api/v1/bpjs/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok && claimDocuments) {
        loadClaimDocuments(claimDocuments.claim_id);
      }
    } catch (error) {
      console.error('Gagal menghapus dokumen:', error);
    }
  };

  const downloadDocument = async (document: Document) => {
    try {
      const response = await fetch(document.file_url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = document.file_name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Gagal download dokumen:', error);
    }
  };

  const previewDocument = (document: Document) => {
    setPreviewUrl(document.file_url);
  };

  const handleBulkFileSelect = (docType: DocumentType, file: File) => {
    const newBulkFiles = new Map(bulkFiles);
    newBulkFiles.set(docType, file);
    setBulkFiles(newBulkFiles);
  };

  const uploadBulkDocuments = async () => {
    if (!claimDocuments || bulkFiles.size === 0) return;

    setUploading('lainnya');
    try {
      const formData = new FormData();
      formData.append('claim_id', claimDocuments.claim_id);

      bulkFiles.forEach((file, docType) => {
        formData.append(`files_${docType}`, file);
      });

      const response = await fetch('/api/v1/bpjs/documents/bulk-upload', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        setBulkFiles(new Map());
        setShowBulkUpload(false);
        loadClaimDocuments(claimDocuments.claim_id);
      }
    } catch (error) {
      console.error('Gagal upload bulk:', error);
    } finally {
      setUploading(null);
    }
  };

  const getDocumentByType = (docType: DocumentType): Document | undefined => {
    return claimDocuments?.documents.find(d => d.document_type === docType);
  };

  const getStatusIcon = (status: Document['verification_status']) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: Document['verification_status']) => {
    switch (status) {
      case 'verified':
        return <Badge variant="success">Terverifikasi</Badge>;
      case 'rejected':
        return <Badge variant="error">Ditolak</Badge>;
      default:
        return <Badge variant="warning">Pending</Badge>;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
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

  if (!claimDocuments && !claimId) {
    return (
      <div className="bg-white shadow rounded-lg p-6 text-center">
        <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-500">Pilih klaim untuk mengelola dokumen</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            Manager Dokumen Klaim
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola dokumen pendukung klaim BPJS
          </p>
        </div>
        <button
          onClick={() => claimDocuments && loadClaimDocuments(claimDocuments.claim_id)}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Claim Info */}
      {claimDocuments && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-blue-700">Nama Pasien</p>
              <p className="text-sm font-medium text-blue-900">{claimDocuments.patient_name}</p>
            </div>
            <div>
              <p className="text-xs text-blue-700">No. SEP</p>
              <p className="text-sm font-medium text-blue-900">{claimDocuments.sep_number}</p>
            </div>
            <div>
              <p className="text-xs text-blue-700">ID Klaim</p>
              <p className="text-sm font-medium text-blue-900">{claimDocuments.claim_id}</p>
            </div>
          </div>
        </div>
      )}

      {/* Missing Documents Alert */}
      {claimDocuments && claimDocuments.missing_required.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-900">Dokumen Wajib Belum Lengkap</p>
              <p className="text-xs text-red-700 mt-1">Dokumen berikut masih belum diupload:</p>
              <ul className="mt-2 space-y-1">
                {claimDocuments.missing_required.map((docType) => {
                  const req = documentRequirements.find(r => r.type === docType);
                  return req ? (
                    <li key={docType} className="text-xs text-red-700 ml-4">- {req.name}</li>
                  ) : null;
                })}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Document List */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {documentRequirements.map((requirement) => {
            const document = getDocumentByType(requirement.type);
            const isSelected = selectedFile !== null;

            return (
              <div key={requirement.type} className="bg-white shadow rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <File className="h-5 w-5 text-gray-400" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">{requirement.name}</h3>
                        <p className="text-xs text-gray-500">{requirement.description}</p>
                      </div>
                      {requirement.required && (
                        <Badge variant="error" dot>Wajib</Badge>
                      )}
                    </div>

                    {document ? (
                      // Document exists
                      <div className="mt-3 border rounded-lg p-3 bg-gray-50">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            {getStatusIcon(document.verification_status)}
                            <div>
                              <p className="text-sm font-medium text-gray-900">{document.file_name}</p>
                              <p className="text-xs text-gray-500">
                                {formatFileSize(document.file_size)} • {formatDate(document.upload_date)}
                              </p>
                              {document.verification_status === 'rejected' && document.rejection_reason && (
                                <p className="text-xs text-red-600 mt-1">{document.rejection_reason}</p>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {getStatusBadge(document.verification_status)}
                            <div className="flex gap-1 ml-2">
                              <button
                                onClick={() => previewDocument(document)}
                                className="p-1 text-blue-600 hover:text-blue-800"
                                title="Preview"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => downloadDocument(document)}
                                className="p-1 text-gray-600 hover:text-gray-800"
                                title="Download"
                              >
                                <Download className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => deleteDocument(document.id)}
                                className="p-1 text-red-600 hover:text-red-800"
                                title="Hapus"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      // No document - show upload area
                      <div
                        className={`mt-3 border-2 border-dashed rounded-lg p-6 transition-colors ${
                          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                        }`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <input
                              ref={fileInputRef}
                              type="file"
                              accept={requirement.file_types.map(t => `.${t}`).join(',')}
                              onChange={handleFileSelect}
                              className="hidden"
                            />
                            {isSelected ? (
                              <div>
                                <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                                <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
                              </div>
                            ) : (
                              <div className="text-center">
                                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                                <p className="text-sm text-gray-600">
                                  Drag & drop atau{' '}
                                  <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="text-blue-600 hover:text-blue-800"
                                  >
                                    browse
                                  </button>
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                  {requirement.file_types.map(t => t.toUpperCase()).join(', ')} (max {requirement.max_size_mb}MB)
                                </p>
                              </div>
                            )}
                          </div>
                          {isSelected && (
                            <button
                              onClick={() => uploadDocument(requirement.type)}
                              disabled={uploading === requirement.type}
                              className="ml-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300"
                            >
                              {uploading === requirement.type ? (
                                <>
                                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                  Uploading...
                                </>
                              ) : (
                                <>
                                  <Upload className="h-4 w-4 mr-2" />
                                  Upload
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Bulk Upload Button */}
      {claimDocuments && (
        <div className="flex justify-end">
          <button
            onClick={() => setShowBulkUpload(!showBulkUpload)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Plus className="h-4 w-4 mr-2" />
            Upload Bulk
          </button>
        </div>
      )}

      {/* Bulk Upload Modal */}
      {showBulkUpload && claimDocuments && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Upload Bulk Dokumen</h2>
                <button
                  onClick={() => setShowBulkUpload(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                {documentRequirements.map((requirement) => {
                  const file = bulkFiles.get(requirement.type);
                  return (
                    <div key={requirement.type} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{requirement.name}</p>
                          <p className="text-xs text-gray-500">{requirement.file_types.map(t => t.toUpperCase()).join(', ')}</p>
                        </div>
                        <input
                          type="file"
                          accept={requirement.file_types.map(t => `.${t}`).join(',')}
                          onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                              handleBulkFileSelect(requirement.type, e.target.files[0]);
                            }
                          }}
                          className="text-sm"
                        />
                      </div>
                      {file && (
                        <p className="text-xs text-green-600 mt-2">
                          <CheckCircle className="h-3 w-3 inline mr-1" />
                          {file.name} ({formatFileSize(file.size)})
                        </p>
                      )}
                    </div>
                  );
                })}

                <div className="flex justify-end gap-3 pt-4 border-t">
                  <button
                    onClick={() => setShowBulkUpload(false)}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Batal
                  </button>
                  <button
                    onClick={uploadBulkDocuments}
                    disabled={bulkFiles.size === 0 || uploading === 'lainnya'}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300"
                  >
                    {uploading === 'lainnya' ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        Upload {bulkFiles.size} Dokumen
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Document Preview Modal */}
      {previewUrl && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Preview Dokumen</h3>
              <button
                onClick={() => setPreviewUrl(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>
            <div className="p-4" style={{ height: 'calc(90vh - 80px)' }}>
              <iframe
                src={previewUrl}
                className="w-full h-full border-0"
                title="Document Preview"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
