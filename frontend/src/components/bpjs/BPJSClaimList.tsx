"""BPJS Claim List Component

Comprehensive BPJS claims list with:
- Filter by status, date, package type
- Status tracking (draft, submitted, verified, approved, rejected)
- Action buttons (submit, validate, respond)
- Deadline indicators
- Claim details modal
"""

import { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  Filter,
  Eye,
  Send,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Download,
  Calendar,
  User,
  Package,
  MoreVertical,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

// Types
type ClaimStatus = 'draft' | 'submitted' | 'verified' | 'approved' | 'rejected';
type PackageType = 'inap' | 'jalan' | 'igd' | 'katarak' | 'klinis';

interface BPJSClaim {
  id: number;
  claim_id: string;
  patient_name: string;
  patient_bpjs_number: string;
  sep_number: string;
  package_code: string;
  package_name: string;
  package_type: PackageType;
  package_rate: number;
  admission_date: string;
  discharge_date: string;
  submit_date: string | null;
  status: ClaimStatus;
  deadline_date: string | null;
  response_deadline: string | null;
  has_queries: boolean;
  query_count: number;
  documents_complete: boolean;
  missing_documents: string[];
}

interface ClaimFilters {
  status: ClaimStatus | 'all';
  package_type: PackageType | 'all';
  date_from: string;
  date_to: string;
  search: string;
}

export function BPJSClaimList() {
  const [claims, setClaims] = useState<BPJSClaim[]>([]);
  const [filteredClaims, setFilteredClaims] = useState<BPJSClaim[]>([]);
  const [filters, setFilters] = useState<ClaimFilters>({
    status: 'all',
    package_type: 'all',
    date_from: '',
    date_to: '',
    search: '',
  });
  const [selectedClaim, setSelectedClaim] = useState<BPJSClaim | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  useEffect(() => {
    loadClaims();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [claims, filters]);

  const loadClaims = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/bpjs/claims', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setClaims(data);
      }
    } catch (error) {
      console.error('Gagal memuat klaim:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...claims];

    // Status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(c => c.status === filters.status);
    }

    // Package type filter
    if (filters.package_type !== 'all') {
      filtered = filtered.filter(c => c.package_type === filters.package_type);
    }

    // Date range filter
    if (filters.date_from) {
      filtered = filtered.filter(c => new Date(c.admission_date) >= new Date(filters.date_from));
    }
    if (filters.date_to) {
      filtered = filtered.filter(c => new Date(c.admission_date) <= new Date(filters.date_to));
    }

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(c =>
        c.patient_name.toLowerCase().includes(searchLower) ||
        c.sep_number.toLowerCase().includes(searchLower) ||
        c.claim_id.toLowerCase().includes(searchLower)
      );
    }

    setFilteredClaims(filtered);
    setCurrentPage(1);
  };

  const getStatusVariant = (status: ClaimStatus) => {
    switch (status) {
      case 'draft':
        return 'neutral';
      case 'submitted':
        return 'info';
      case 'verified':
        return 'warning';
      case 'approved':
        return 'success';
      case 'rejected':
        return 'error';
      default:
        return 'neutral';
    }
  };

  const getStatusLabel = (status: ClaimStatus) => {
    switch (status) {
      case 'draft':
        return 'Draft';
      case 'submitted':
        return 'Submitted';
      case 'verified':
        return 'Verified';
      case 'approved':
        return 'Approved';
      case 'rejected':
        return 'Rejected';
      default:
        return status;
    }
  };

  const getPackageTypeLabel = (type: PackageType) => {
    switch (type) {
      case 'inap':
        return 'Rawat Inap';
      case 'jalan':
        return 'Rawat Jalan';
      case 'igd':
        return 'IGD';
      case 'katarak':
        return 'Katarak';
      case 'klinis':
        return 'Klinis';
      default:
        return type;
    }
  };

  const getDeadlineStatus = (deadline: string | null) => {
    if (!deadline) return null;

    const days = Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (days < 0) return 'expired';
    if (days <= 2) return 'urgent';
    if (days <= 7) return 'warning';
    return 'normal';
  };

  const submitClaim = async (claimId: string) => {
    try {
      const response = await fetch(`/api/v1/bpjs/claims/${claimId}/submit`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        alert('Klaim berhasil disubmit!');
        loadClaims();
      }
    } catch (error) {
      console.error('Gagal submit klaim:', error);
    }
  };

  const viewDetails = (claim: BPJSClaim) => {
    setSelectedClaim(claim);
    setShowDetails(true);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  // Pagination
  const totalPages = Math.ceil(filteredClaims.length / itemsPerPage);
  const paginatedClaims = filteredClaims.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            Daftar Klaim BPJS
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola dan pantau status klaim BPJS
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Filter className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-sm font-medium text-gray-900">Filter</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Cari klaim..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500 w-full"
            />
          </div>

          {/* Status Filter */}
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value as ClaimStatus | 'all' })}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Semua Status</option>
            <option value="draft">Draft</option>
            <option value="submitted">Submitted</option>
            <option value="verified">Verified</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>

          {/* Package Type Filter */}
          <select
            value={filters.package_type}
            onChange={(e) => setFilters({ ...filters, package_type: e.target.value as PackageType | 'all' })}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Semua Tipe Paket</option>
            <option value="inap">Rawat Inap</option>
            <option value="jalan">Rawat Jalan</option>
            <option value="igd">IGD</option>
            <option value="katarak">Katarak</option>
            <option value="klinis">Klinis</option>
          </select>

          {/* Date Range */}
          <input
            type="date"
            value={filters.date_from}
            onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Filter Summary */}
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Menampilkan {filteredClaims.length} dari {claims.length} klaim
          </p>
          {(filters.status !== 'all' || filters.package_type !== 'all' || filters.date_from || filters.search) && (
            <button
              onClick={() => setFilters({ status: 'all', package_type: 'all', date_from: '', date_to: '', search: '' })}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Reset Filter
            </button>
          )}
        </div>
      </div>

      {/* Claims List */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID Klaim</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pasien</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">No. SEP</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Paket</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tanggal</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nilai</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deadline</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aksi</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedClaims.map((claim) => {
                  const deadlineStatus = getDeadlineStatus(claim.response_deadline || claim.deadline_date);
                  return (
                    <tr key={claim.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {claim.claim_id}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <User className="h-4 w-4 text-gray-400 mr-2" />
                          <div className="text-sm text-gray-900">{claim.patient_name}</div>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {claim.sep_number}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Package className="h-4 w-4 text-gray-400 mr-2" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{claim.package_name}</p>
                            <p className="text-xs text-gray-500">{getPackageTypeLabel(claim.package_type)}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                          {formatDate(claim.admission_date)}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(claim.package_rate)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <Badge variant={getStatusVariant(claim.status)}>
                            {getStatusLabel(claim.status)}
                          </Badge>
                          {claim.has_queries && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                              {claim.query_count} Query
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        {deadlineStatus && deadlineStatus !== 'normal' && (
                          <div className={`flex items-center text-xs ${
                            deadlineStatus === 'expired' ? 'text-red-600' :
                            deadlineStatus === 'urgent' ? 'text-orange-600' :
                            'text-yellow-600'
                          }`}>
                            <Clock className="h-3 w-3 mr-1" />
                            {deadlineStatus === 'expired' ? 'Expired' :
                             deadlineStatus === 'urgent' ? 'Urgent' :
                             'Warning'}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => viewDetails(claim)}
                            className="text-blue-600 hover:text-blue-800"
                            title="Lihat Detail"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          {claim.status === 'draft' && (
                            <button
                              onClick={() => submitClaim(claim.claim_id)}
                              className="text-green-600 hover:text-green-800"
                              title="Submit Klaim"
                            >
                              <Send className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {paginatedClaims.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada klaim yang cocok dengan filter</p>
              </div>
            )}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Halaman {currentPage} dari {totalPages}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Prev
                </button>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Claim Details Modal */}
      {showDetails && selectedClaim && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Detail Klaim</h2>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Patient Info */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Informasi Pasien</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-500">Nama Pasien</p>
                        <p className="text-sm font-medium text-gray-900">{selectedClaim.patient_name}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">No. BPJS</p>
                        <p className="text-sm font-medium text-gray-900">{selectedClaim.patient_bpjs_number}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Claim Info */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Informasi Klaim</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-500">ID Klaim</p>
                        <p className="text-sm font-medium text-gray-900">{selectedClaim.claim_id}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">No. SEP</p>
                        <p className="text-sm font-medium text-gray-900">{selectedClaim.sep_number}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Status</p>
                        <div className="mt-1">
                          <Badge variant={getStatusVariant(selectedClaim.status)}>
                            {getStatusLabel(selectedClaim.status)}
                          </Badge>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Tipe Paket</p>
                        <p className="text-sm font-medium text-gray-900">{getPackageTypeLabel(selectedClaim.package_type)}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Package Info */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Paket INA-CBG</h3>
                  <div className="border rounded-lg p-4 bg-blue-50">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-bold text-gray-900">{selectedClaim.package_code}</p>
                        <p className="text-xs text-gray-600 mt-1">{selectedClaim.package_name}</p>
                      </div>
                      <p className="text-lg font-bold text-blue-600">
                        {formatCurrency(selectedClaim.package_rate)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Dates */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Tanggal Penting</h3>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Tanggal Masuk</span>
                      <span className="text-sm font-medium text-gray-900">{formatDate(selectedClaim.admission_date)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Tanggal Keluar</span>
                      <span className="text-sm font-medium text-gray-900">{formatDate(selectedClaim.discharge_date)}</span>
                    </div>
                    {selectedClaim.submit_date && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Tanggal Submit</span>
                        <span className="text-sm font-medium text-gray-900">{formatDate(selectedClaim.submit_date)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Documents Status */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Status Dokumen</h3>
                  <div className={`rounded-lg p-4 ${selectedClaim.documents_complete ? 'bg-green-50' : 'bg-red-50'}`}>
                    {selectedClaim.documents_complete ? (
                      <div className="flex items-center text-green-900">
                        <CheckCircle className="h-5 w-5 mr-2" />
                        <span className="text-sm font-medium">Dokumen Lengkap</span>
                      </div>
                    ) : (
                      <div>
                        <div className="flex items-center text-red-900 mb-2">
                          <XCircle className="h-5 w-5 mr-2" />
                          <span className="text-sm font-medium">Dokumen Tidak Lengkap</span>
                        </div>
                        <div className="space-y-1">
                          {selectedClaim.missing_documents.map((doc, idx) => (
                            <p key={idx} className="text-xs text-red-700 ml-7">- {doc}</p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <button
                    onClick={() => setShowDetails(false)}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Tutup
                  </button>
                  {selectedClaim.status === 'draft' && (
                    <button
                      onClick={() => {
                        submitClaim(selectedClaim.claim_id);
                        setShowDetails(false);
                      }}
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                    >
                      <Send className="h-4 w-4 mr-2" />
                      Submit Klaim
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
