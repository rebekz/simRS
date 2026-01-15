/**
 * Payment Processor Component for STORY-028
 *
Payment processing system with:
- Payment method selection (cash, card, transfer, BPJS, insurance)
- Amount entry and validation
- Reference number capture
- Receipt generation
- Payment confirmation

 */

import { useState, useEffect } from 'react';
import {
  CreditCard,
  DollarSign,
  Smartphone,
  Building,
  Shield,
  CheckCircle,
  Printer,
  Mail,
  AlertCircle,
  RefreshCw,
  FileText,
  Search,
} from 'lucide-react';

// Types
interface PaymentRequest {
  invoice_id: number;
  invoice_number: string;
  patient_name: string;
  patient_bpjs_number: string | null;
  total_amount: number;
  paid_amount: number;
  balance_due: number;
  status: string;
}

interface PaymentMethod {
  id: string;
  name: string;
  name_id: string;
  icon: any;
  requires_reference: boolean;
  reference_label: string;
  requires_approval: boolean;
}

interface PaymentForm {
  payment_method: string;
  amount: number;
  reference_number: string;
  approval_code: string;
  cardholder_name: string;
  bank_name: string;
  notes: string;
}

interface Receipt {
  receipt_number: string;
  payment_date: string;
  patient_name: string;
  invoice_number: string;
  payment_method: string;
  amount: number;
  reference_number: string;
  received_by: string;
}

export function PaymentProcessor() {
  const [paymentRequest, setPaymentRequest] = useState<PaymentRequest | null>(null);
  const [paymentForm, setPaymentForm] = useState<PaymentForm>({
    payment_method: 'cash',
    amount: 0,
    reference_number: '',
    approval_code: '',
    cardholder_name: '',
    bank_name: '',
    notes: '',
  });
  const [receipt, setReceipt] = useState<Receipt | null>(null);
  const [showReceipt, setShowReceipt] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [invoiceNumber, setInvoiceNumber] = useState('');
  const [searchError, setSearchError] = useState('');

  const paymentMethods: PaymentMethod[] = [
    {
      id: 'cash',
      name: 'Cash',
      name_id: 'Tunai',
      icon: DollarSign,
      requires_reference: false,
      reference_label: '',
      requires_approval: false,
    },
    {
      id: 'card',
      name: 'Card',
      name_id: 'Kartu Debit/Kredit',
      icon: CreditCard,
      requires_reference: true,
      reference_label: 'Nomor Kartu (4 digit terakhir)',
      requires_approval: true,
    },
    {
      id: 'transfer',
      name: 'Transfer',
      name_id: 'Transfer Bank',
      icon: Building,
      requires_reference: true,
      reference_label: 'Nomor Referensi Transfer',
      requires_approval: false,
    },
    {
      id: 'bpjs',
      name: 'BPJS',
      name_id: 'BPJS Kesehatan',
      icon: Shield,
      requires_reference: true,
      reference_label: 'Nomor SEP',
      requires_approval: false,
    },
    {
      id: 'insurance',
      name: 'Insurance',
      name_id: 'Asuransi',
      icon: Smartphone,
      requires_reference: true,
      reference_label: 'Nomor Klaim',
      requires_approval: false,
    },
  ];

  const searchInvoice = async () => {
    if (!invoiceNumber.trim()) {
      setSearchError('Masukkan nomor faktur');
      return;
    }

    setIsLoading(true);
    setSearchError('');
    try {
      const response = await fetch(`/api/v1/billing/invoices/${invoiceNumber}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPaymentRequest(data);
        setPaymentForm({
          ...paymentForm,
          amount: data.balance_due,
        });
      } else {
        setSearchError('Faktur tidak ditemukan');
      }
    } catch (error) {
      console.error('Failed to search invoice:', error);
      setSearchError('Gagal mencari faktur');
    } finally {
      setIsLoading(false);
    }
  };

  const processPayment = async () => {
    if (!paymentRequest) return;

    if (paymentForm.amount <= 0) {
      alert('Masukkan jumlah pembayaran yang valid');
      return;
    }

    const selectedMethod = paymentMethods.find(m => m.id === paymentForm.payment_method);
    if (selectedMethod?.requires_reference && !paymentForm.reference_number.trim()) {
      alert(`Masukkan ${selectedMethod.reference_label}`);
      return;
    }

    if (paymentForm.payment_method === 'card' && !paymentForm.approval_code.trim()) {
      alert('Masukkan kode approval transaksi');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/billing/invoices/${paymentRequest.invoice_id}/payments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(paymentForm),
      });

      if (response.ok) {
        const data = await response.json();
        setReceipt(data);
        setShowReceipt(true);
        resetForm();
      }
    } catch (error) {
      console.error('Failed to process payment:', error);
      alert('Gagal memproses pembayaran');
    } finally {
      setIsLoading(false);
    }
  };

  const printReceipt = () => {
    if (!receipt) return;

    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    printWindow.document.write(`
      <html>
        <head>
          <title>Kuitansi Pembayaran - ${receipt.receipt_number}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .header { text-align: center; margin-bottom: 20px; }
            .header h1 { margin: 0; }
            .info { margin-bottom: 20px; }
            .info-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
            .total { border-top: 2px solid #000; padding-top: 10px; margin-top: 20px; }
            .total-row { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; }
            .footer { margin-top: 40px; text-align: center; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>SIMRS - Kuitansi Pembayaran</h1>
            <p>${receipt.receipt_number}</p>
          </div>
          <div class="info">
            <div class="info-row"><span>Tanggal:</span><span>${receipt.payment_date}</span></div>
            <div class="info-row"><span>No. Faktur:</span><span>${receipt.invoice_number}</span></div>
            <div class="info-row"><span>Pasien:</span><span>${receipt.patient_name}</span></div>
            <div class="info-row"><span>Metode:</span><span>${receipt.payment_method}</span></div>
            ${receipt.reference_number ? `<div class="info-row"><span>Referensi:</span><span>${receipt.reference_number}</span></div>` : ''}
          </div>
          <div class="total">
            <div class="total-row">
              <span>TOTAL</span>
              <span>${formatCurrency(receipt.amount)}</span>
            </div>
          </div>
          <div class="footer">
            <p>Diterima oleh: ${receipt.received_by}</p>
            <p>Terima kasih atas pembayaran Anda</p>
          </div>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const emailReceipt = async () => {
    if (!receipt) return;

    try {
      const response = await fetch(`/api/v1/billing/payments/${receipt.receipt_number}/email`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        alert('Kuitansi berhasil dikirim ke email pasien');
      }
    } catch (error) {
      console.error('Failed to email receipt:', error);
    }
  };

  const resetForm = () => {
    setPaymentRequest(null);
    setPaymentForm({
      payment_method: 'cash',
      amount: 0,
      reference_number: '',
      approval_code: '',
      cardholder_name: '',
      bank_name: '',
      notes: '',
    });
    setInvoiceNumber('');
    setSearchError('');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const selectedPaymentMethod = paymentMethods.find(m => m.id === paymentForm.payment_method);
  const PaymentIcon = selectedPaymentMethod?.icon || DollarSign;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <CreditCard className="h-6 w-6 mr-2" />
            Pemrosesan Pembayaran
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Terima dan catat pembayaran tagihan pasien
          </p>
        </div>
      </div>

      {!showReceipt ? (
        <>
          {/* Invoice Search */}
          {!paymentRequest && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Cari Faktur</h3>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={invoiceNumber}
                  onChange={(e) => setInvoiceNumber(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchInvoice()}
                  placeholder="Masukkan nomor faktur..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  onClick={searchInvoice}
                  disabled={isLoading}
                  className="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </button>
              </div>
              {searchError && (
                <div className="mt-3 flex items-center text-sm text-red-600">
                  <AlertCircle className="h-4 w-4 mr-2" />
                  {searchError}
                </div>
              )}
            </div>
          )}

          {/* Payment Form */}
          {paymentRequest && (
            <div className="space-y-6">
              {/* Invoice Summary */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-blue-900">Ringkasan Faktur</h3>
                  <button
                    onClick={resetForm}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Cari Faktur Lain
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-blue-700">No. Faktur</p>
                    <p className="text-sm font-medium text-blue-900">{paymentRequest.invoice_number}</p>
                  </div>
                  <div>
                    <p className="text-xs text-blue-700">Pasien</p>
                    <p className="text-sm font-medium text-blue-900">{paymentRequest.patient_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-blue-700">Total Tagihan</p>
                    <p className="text-sm font-medium text-blue-900">{formatCurrency(paymentRequest.total_amount)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-blue-700">Sisa Tagihan</p>
                    <p className="text-lg font-bold text-blue-900">{formatCurrency(paymentRequest.balance_due)}</p>
                  </div>
                </div>
              </div>

              {/* Payment Method Selection */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Metode Pembayaran</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {paymentMethods.map((method) => {
                    const Icon = method.icon;
                    return (
                      <button
                        key={method.id}
                        onClick={() => setPaymentForm({
                          ...paymentForm,
                          payment_method: method.id,
                        })}
                        className={`p-4 border-2 rounded-lg transition-all ${
                          paymentForm.payment_method === method.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex flex-col items-center">
                          <Icon className={`h-8 w-8 mb-2 ${
                            paymentForm.payment_method === method.id
                              ? 'text-blue-600'
                              : 'text-gray-400'
                          }`} />
                          <span className="text-sm font-medium text-gray-900">{method.name_id}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Payment Details */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Detail Pembayaran</h3>
                <div className="space-y-4">
                  {/* Amount */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Jumlah Pembayaran
                    </label>
                    <div className="relative">
                      <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 font-medium">
                        Rp
                      </span>
                      <input
                        type="number"
                        value={paymentForm.amount}
                        onChange={(e) => setPaymentForm({
                          ...paymentForm,
                          amount: parseFloat(e.target.value) || 0,
                        })}
                        className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-md text-lg font-medium focus:ring-blue-500 focus:border-blue-500"
                        placeholder="0"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Sisa tagihan: {formatCurrency(paymentRequest.balance_due)}
                    </p>
                  </div>

                  {/* Reference Number */}
                  {selectedPaymentMethod?.requires_reference && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {selectedPaymentMethod.reference_label}
                      </label>
                      <input
                        type="text"
                        value={paymentForm.reference_number}
                        onChange={(e) => setPaymentForm({
                          ...paymentForm,
                          reference_number: e.target.value,
                        })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        placeholder={selectedPaymentMethod.reference_label}
                      />
                    </div>
                  )}

                  {/* Card Details */}
                  {paymentForm.payment_method === 'card' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Nama Pemegang Kartu
                        </label>
                        <input
                          type="text"
                          value={paymentForm.cardholder_name}
                          onChange={(e) => setPaymentForm({
                            ...paymentForm,
                            cardholder_name: e.target.value,
                          })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Nama sesuai kartu"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Kode Approval
                        </label>
                        <input
                          type="text"
                          value={paymentForm.approval_code}
                          onChange={(e) => setPaymentForm({
                            ...paymentForm,
                            approval_code: e.target.value,
                          })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Kode approval dari EDC"
                          required
                        />
                      </div>
                    </>
                  )}

                  {/* Bank Details for Transfer */}
                  {paymentForm.payment_method === 'transfer' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Bank Tujuan
                      </label>
                      <select
                        value={paymentForm.bank_name}
                        onChange={(e) => setPaymentForm({
                          ...paymentForm,
                          bank_name: e.target.value,
                        })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Pilih Bank</option>
                        <option value="bca">BCA</option>
                        <option value="mandiri">Mandiri</option>
                        <option value="bni">BNI</option>
                        <option value="bri">BRI</option>
                        <option value="cimb">CIMB Niaga</option>
                        <option value="other">Lainnya</option>
                      </select>
                    </div>
                  )}

                  {/* Notes */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Catatan (Opsional)
                    </label>
                    <textarea
                      value={paymentForm.notes}
                      onChange={(e) => setPaymentForm({
                        ...paymentForm,
                        notes: e.target.value,
                      })}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Catatan tambahan untuk pembayaran ini"
                    />
                  </div>
                </div>
              </div>

              {/* Payment Summary */}
              <div className="bg-gray-50 border rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Metode Pembayaran</p>
                    <p className="text-lg font-medium text-gray-900 flex items-center">
                      <PaymentIcon className="h-5 w-5 mr-2" />
                      {selectedPaymentMethod?.name_id}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Jumlah</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {formatCurrency(paymentForm.amount)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end gap-3">
                <button
                  onClick={resetForm}
                  className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Batal
                </button>
                <button
                  onClick={processPayment}
                  disabled={isLoading || paymentForm.amount <= 0}
                  className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Memproses...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Proses Pembayaran
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        /* Receipt Display */
        <div className="bg-white shadow rounded-lg p-8 max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Pembayaran Berhasil!</h2>
            <p className="text-gray-600 mt-2">Kuitansi pembayaran telah dibuat</p>
          </div>

          {receipt && (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 mb-6">
              <div className="text-center mb-6">
                <h3 className="text-lg font-bold text-gray-900">KUITANSI PEMBAYARAN</h3>
                <p className="text-sm text-gray-600">{receipt.receipt_number}</p>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Tanggal:</span>
                  <span className="font-medium text-gray-900">{receipt.payment_date}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">No. Faktur:</span>
                  <span className="font-medium text-gray-900">{receipt.invoice_number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Pasien:</span>
                  <span className="font-medium text-gray-900">{receipt.patient_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Metode:</span>
                  <span className="font-medium text-gray-900 capitalize">{receipt.payment_method}</span>
                </div>
                {receipt.reference_number && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Referensi:</span>
                    <span className="font-medium text-gray-900">{receipt.reference_number}</span>
                  </div>
                )}
                <div className="border-t pt-3 mt-3">
                  <div className="flex justify-between text-lg font-bold">
                    <span className="text-gray-900">TOTAL</span>
                    <span className="text-green-600">{formatCurrency(receipt.amount)}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-center gap-3">
            <button
              onClick={printReceipt}
              className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Printer className="h-4 w-4 mr-2" />
              Cetak Kuitansi
            </button>
            <button
              onClick={emailReceipt}
              className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Mail className="h-4 w-4 mr-2" />
              Email Kuitansi
            </button>
            <button
              onClick={() => {
                setShowReceipt(false);
                resetForm();
              }}
              className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <FileText className="h-4 w-4 mr-2" />
              Transaksi Baru
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
