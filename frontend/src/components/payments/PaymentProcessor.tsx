/**
 * Payment Processor Component
 *
Payment processing system with:
- Invoice lookup by number or patient
- Amount calculation with change for cash
- Payment method selection (cash, card, transfer, VA, gateway)
- Payment gateway integration
- Receipt generation
- Change calculation for cash payments

 */

import { useState, useEffect } from 'react';
import {
  CreditCard,
  DollarSign,
  Smartphone,
  Building,
  QrCode,
  Printer,
  Mail,
  AlertCircle,
  RefreshCw,
  FileText,
  Search,
  User,
  CheckCircle,
  ArrowRight,
} from 'lucide-react';

// Types
interface Invoice {
  id: number;
  invoice_number: string;
  patient_name: string;
  patient_id: number;
  total_amount: number;
  paid_amount: number;
  balance_due: number;
  status: string;
  due_date: string;
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
  va_number: string;
  gateway_transaction_id: string;
  notes: string;
}

interface Receipt {
  receipt_number: string;
  payment_date: string;
  patient_name: string;
  invoice_number: string;
  payment_method: string;
  amount: number;
  change_amount: number;
  reference_number: string;
  received_by: string;
}

interface VirtualAccount {
  bank_name: string;
  va_number: string;
  expiration_date: string;
}

interface GatewayResponse {
  transaction_id: string;
  payment_url: string;
  qr_code: string;
  expiration: string;
}

export function PaymentProcessor() {
  const [step, setStep] = useState<'search' | 'process' | 'gateway' | 'receipt'>('search');
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [paymentForm, setPaymentForm] = useState<PaymentForm>({
    payment_method: 'cash',
    amount: 0,
    reference_number: '',
    approval_code: '',
    cardholder_name: '',
    bank_name: '',
    va_number: '',
    gateway_transaction_id: '',
    notes: '',
  });
  const [receipt, setReceipt] = useState<Receipt | null>(null);
  const [gatewayResponse, setGatewayResponse] = useState<GatewayResponse | null>(null);
  const [virtualAccount, setVirtualAccount] = useState<VirtualAccount | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchType, setSearchType] = useState<'invoice' | 'patient'>('invoice');
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
      id: 'va',
      name: 'Virtual Account',
      name_id: 'Virtual Account',
      icon: CreditCard,
      requires_reference: true,
      reference_label: 'Nomor VA',
      requires_approval: false,
    },
    {
      id: 'gateway',
      name: 'Payment Gateway',
      name_id: 'Payment Gateway',
      icon: QrCode,
      requires_reference: false,
      reference_label: '',
      requires_approval: false,
    },
  ];

  const searchInvoices = async () => {
    if (!searchTerm.trim()) {
      setSearchError('Masukkan kata pencarian');
      return;
    }

    setIsLoading(true);
    setSearchError('');
    try {
      const endpoint = searchType === 'invoice'
        ? `/api/v1/payments/invoices/search?number=${searchTerm}`
        : `/api/v1/payments/invoices/search?patient=${searchTerm}`;

      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          setInvoices(data);
        } else {
          setInvoices([]);
          setSearchError('Tidak ada faktur ditemukan');
        }
      } else {
        setSearchError('Gagal mencari faktur');
      }
    } catch (error) {
      console.error('Failed to search invoices:', error);
      setSearchError('Gagal mencari faktur');
    } finally {
      setIsLoading(false);
    }
  };

  const selectInvoice = (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    setPaymentForm({
      ...paymentForm,
      amount: invoice.balance_due,
    });
    setStep('process');
  };

  const generateVA = async () => {
    if (!selectedInvoice) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/payments/virtual-account`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          invoice_id: selectedInvoice.id,
          bank_name: paymentForm.bank_name,
          amount: paymentForm.amount,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setVirtualAccount(data);
        setPaymentForm({
          ...paymentForm,
          va_number: data.va_number,
          reference_number: data.va_number,
        });
      }
    } catch (error) {
      console.error('Failed to generate VA:', error);
      alert('Gagal membuat Virtual Account');
    } finally {
      setIsLoading(false);
    }
  };

  const initiateGatewayPayment = async () => {
    if (!selectedInvoice) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/payments/gateway/initiate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          invoice_id: selectedInvoice.id,
          amount: paymentForm.amount,
          payment_method: 'qris',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGatewayResponse(data);
        setPaymentForm({
          ...paymentForm,
          gateway_transaction_id: data.transaction_id,
        });
        setStep('gateway');
      }
    } catch (error) {
      console.error('Failed to initiate gateway payment:', error);
      alert('Gagal memulai pembayaran gateway');
    } finally {
      setIsLoading(false);
    }
  };

  const checkGatewayStatus = async () => {
    if (!gatewayResponse) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/payments/gateway/status/${gatewayResponse.transaction_id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.status === 'paid') {
          completePayment();
        } else {
          alert('Pembayaran belum diterima. Silakan coba lagi.');
        }
      }
    } catch (error) {
      console.error('Failed to check gateway status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const processPayment = async () => {
    if (!selectedInvoice) return;

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
      const response = await fetch(`/api/v1/payments/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          invoice_id: selectedInvoice.id,
          ...paymentForm,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setReceipt(data);
        setStep('receipt');
      } else {
        alert('Gagal memproses pembayaran');
      }
    } catch (error) {
      console.error('Failed to process payment:', error);
      alert('Gagal memproses pembayaran');
    } finally {
      setIsLoading(false);
    }
  };

  const completePayment = async () => {
    if (!selectedInvoice || !gatewayResponse) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/payments/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          invoice_id: selectedInvoice.id,
          transaction_id: gatewayResponse.transaction_id,
          amount: paymentForm.amount,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setReceipt(data);
        setStep('receipt');
      }
    } catch (error) {
      console.error('Failed to complete payment:', error);
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
            .change { margin-top: 10px; color: #16a34a; }
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
              <span>TOTAL BAYAR</span>
              <span>${formatCurrency(receipt.amount)}</span>
            </div>
            ${receipt.change_amount > 0 ? `
              <div class="change info-row">
                <span>KEMBALIAN</span>
                <span>${formatCurrency(receipt.change_amount)}</span>
              </div>
            ` : ''}
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
      const response = await fetch(`/api/v1/payments/receipts/${receipt.receipt_number}/email`, {
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
    setStep('search');
    setSelectedInvoice(null);
    setInvoices([]);
    setPaymentForm({
      payment_method: 'cash',
      amount: 0,
      reference_number: '',
      approval_code: '',
      cardholder_name: '',
      bank_name: '',
      va_number: '',
      gateway_transaction_id: '',
      notes: '',
    });
    setReceipt(null);
    setGatewayResponse(null);
    setVirtualAccount(null);
    setSearchTerm('');
    setSearchError('');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const calculateChange = () => {
    if (paymentForm.payment_method === 'cash' && selectedInvoice) {
      const change = paymentForm.amount - selectedInvoice.balance_due;
      return change > 0 ? change : 0;
    }
    return 0;
  };

  const selectedPaymentMethod = paymentMethods.find(m => m.id === paymentForm.payment_method);
  const PaymentIcon = selectedPaymentMethod?.icon || DollarSign;
  const changeAmount = calculateChange();

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

      {/* Step 1: Search Invoice */}
      {step === 'search' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Cari Faktur</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="flex gap-2">
              <button
                onClick={() => setSearchType('invoice')}
                className={`flex-1 px-4 py-2 rounded-md text-sm font-medium ${
                  searchType === 'invoice'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                No. Faktur
              </button>
              <button
                onClick={() => setSearchType('patient')}
                className={`flex-1 px-4 py-2 rounded-md text-sm font-medium ${
                  searchType === 'patient'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Nama Pasien
              </button>
            </div>
            <div className="md:col-span-2 flex gap-2">
              <div className="flex-1 relative">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchInvoices()}
                  placeholder={searchType === 'invoice' ? 'Masukkan nomor faktur...' : 'Masukkan nama pasien...'}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <button
                onClick={searchInvoices}
                disabled={isLoading}
                className="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Cari
                  </>
                )}
              </button>
            </div>
          </div>

          {searchError && (
            <div className="mb-4 flex items-center text-sm text-red-600">
              <AlertCircle className="h-4 w-4 mr-2" />
              {searchError}
            </div>
          )}

          {invoices.length > 0 && (
            <div className="border rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">No. Faktur</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pasien</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Sisa</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aksi</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                        {invoice.invoice_number}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {invoice.patient_name}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {formatCurrency(invoice.total_amount)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right font-medium text-red-600">
                        {formatCurrency(invoice.balance_due)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          invoice.balance_due === 0 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {invoice.balance_due === 0 ? 'Lunas' : 'Belum Lunas'}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => selectInvoice(invoice)}
                          disabled={invoice.balance_due === 0}
                          className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                        >
                          Pilih
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Process Payment */}
      {step === 'process' && selectedInvoice && (
        <div className="space-y-6">
          {/* Invoice Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-blue-900">Ringkasan Faktur</h3>
              <button
                onClick={() => setStep('search')}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Cari Faktur Lain
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-blue-700">No. Faktur</p>
                <p className="text-sm font-medium text-blue-900">{selectedInvoice.invoice_number}</p>
              </div>
              <div>
                <p className="text-xs text-blue-700">Pasien</p>
                <p className="text-sm font-medium text-blue-900 flex items-center">
                  <User className="h-4 w-4 mr-1" />
                  {selectedInvoice.patient_name}
                </p>
              </div>
              <div>
                <p className="text-xs text-blue-700">Total Tagihan</p>
                <p className="text-sm font-medium text-blue-900">{formatCurrency(selectedInvoice.total_amount)}</p>
              </div>
              <div>
                <p className="text-xs text-blue-700">Sisa Tagihan</p>
                <p className="text-lg font-bold text-blue-900">{formatCurrency(selectedInvoice.balance_due)}</p>
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
                  Sisa tagihan: {formatCurrency(selectedInvoice.balance_due)}
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

              {/* Bank Selection for VA */}
              {paymentForm.payment_method === 'va' && (
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
                    <option value="permata">Permata</option>
                    <option value="cimb">CIMB Niaga</option>
                  </select>
                  {virtualAccount && (
                    <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
                      <p className="text-sm font-medium text-green-900">Nomor VA: {virtualAccount.va_number}</p>
                      <p className="text-xs text-green-700">Berlaku sampai: {virtualAccount.expiration_date}</p>
                    </div>
                  )}
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

          {/* Change Calculation for Cash */}
          {paymentForm.payment_method === 'cash' && changeAmount > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-900">Kembalian</p>
                  <p className="text-2xl font-bold text-green-600">
                    {formatCurrency(changeAmount)}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
            </div>
          )}

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
              onClick={() => setStep('search')}
              className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Batal
            </button>
            {paymentForm.payment_method === 'gateway' ? (
              <button
                onClick={initiateGatewayPayment}
                disabled={isLoading || paymentForm.amount <= 0}
                className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Memproses...
                  </>
                ) : (
                  <>
                    <QrCode className="h-4 w-4 mr-2" />
                    Lanjut ke Pembayaran Gateway
                  </>
                )}
              </button>
            ) : (
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
            )}
          </div>
        </div>
      )}

      {/* Step 3: Gateway Payment */}
      {step === 'gateway' && gatewayResponse && selectedInvoice && (
        <div className="max-w-2xl mx-auto">
          <div className="bg-white shadow rounded-lg p-8">
            <div className="text-center mb-6">
              <QrCode className="h-16 w-16 mx-auto text-purple-600 mb-4" />
              <h2 className="text-2xl font-bold text-gray-900">Pembayaran Gateway</h2>
              <p className="text-gray-600 mt-2">Scan QRIS atau transfer ke Virtual Account</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <div className="text-center mb-4">
                <p className="text-sm text-gray-600">Nomor Transaksi</p>
                <p className="text-lg font-bold text-gray-900">{gatewayResponse.transaction_id}</p>
              </div>

              <div className="text-center mb-4">
                <p className="text-sm text-gray-600">Jumlah yang Harus Dibayar</p>
                <p className="text-3xl font-bold text-blue-600">{formatCurrency(paymentForm.amount)}</p>
              </div>

              {gatewayResponse.qr_code && (
                <div className="text-center mb-4">
                  <img src={gatewayResponse.qr_code} alt="QRIS" className="mx-auto" />
                  <p className="text-xs text-gray-500 mt-2">Scan QRIS dengan e-wallet atau mobile banking</p>
                </div>
              )}

              <div className="text-center">
                <p className="text-xs text-gray-500">Berlaku sampai: {gatewayResponse.expiration}</p>
              </div>
            </div>

            <div className="flex justify-center gap-3">
              <button
                onClick={() => setStep('process')}
                className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Kembali
              </button>
              <button
                onClick={checkGatewayStatus}
                disabled={isLoading}
                className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Mengecek...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Cek Status Pembayaran
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Receipt */}
      {step === 'receipt' && receipt && (
        <div className="bg-white shadow rounded-lg p-8 max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Pembayaran Berhasil!</h2>
            <p className="text-gray-600 mt-2">Kuitansi pembayaran telah dibuat</p>
          </div>

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
                  <span className="text-gray-900">TOTAL BAYAR</span>
                  <span className="text-green-600">{formatCurrency(receipt.amount)}</span>
                </div>
              </div>
              {receipt.change_amount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>KEMBALIAN</span>
                  <span className="font-medium">{formatCurrency(receipt.change_amount)}</span>
                </div>
              )}
            </div>
          </div>

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
              onClick={resetForm}
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
