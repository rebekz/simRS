/**
 * Billing Rules Admin Component for STORY-028
 *
Billing rules management system with:
- Rule builder interface
- Condition editor (patient type, service, payer, etc.)
- Action configuration (discount, surcharge, waiver)
- Priority management
- Testing interface to validate rules

 */

import { useState, useEffect } from 'react';
import {
  Settings,
  Plus,
  Edit,
  Trash2,
  Play,
  Save,
  X,
  ChevronUp,
  ChevronDown,
  TestTube,
  AlertCircle,
  CheckCircle,
  RefreshCw,
} from 'lucide-react';

// Types
interface BillingRule {
  id?: number;
  name: string;
  description: string;
  rule_type: 'discount' | 'surcharge' | 'waiver';
  conditions: RuleCondition[];
  actions: RuleAction[];
  priority: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

interface RuleCondition {
  id: string;
  field: string;
  operator: string;
  value: string | number | boolean;
}

interface RuleAction {
  id: string;
  type: 'percentage' | 'fixed' | 'waive';
  target: string;
  value: number;
}

interface RuleTestResult {
  rule_id: number;
  rule_name: string;
  is_match: boolean;
  result_amount: number;
  original_amount: number;
  difference: number;
  message: string;
}

interface TestScenario {
  patient_type: string;
  payer_type: string;
  service_code: string;
  amount: number;
}

export function BillingRulesAdmin() {
  const [rules, setRules] = useState<BillingRule[]>([]);
  const [selectedRule, setSelectedRule] = useState<BillingRule | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState<RuleTestResult[]>([]);
  const [testScenario, setTestScenario] = useState<TestScenario>({
    patient_type: 'outpatient',
    payer_type: 'cash',
    service_code: '',
    amount: 100000,
  });

  // New rule form
  const [ruleForm, setRuleForm] = useState<BillingRule>({
    name: '',
    description: '',
    rule_type: 'discount',
    conditions: [],
    actions: [],
    priority: 0,
    is_active: true,
  });

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/billing/rules', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setRules(data);
      }
    } catch (error) {
      console.error('Failed to load billing rules:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveRule = async () => {
    setIsLoading(true);
    try {
      const url = ruleForm.id
        ? `/api/v1/billing/rules/${ruleForm.id}`
        : '/api/v1/billing/rules';

      const method = ruleForm.id ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(ruleForm),
      });

      if (response.ok) {
        alert('Aturan berhasil disimpan');
        loadRules();
        setIsEditing(false);
        setRuleForm({
          name: '',
          description: '',
          rule_type: 'discount',
          conditions: [],
          actions: [],
          priority: 0,
          is_active: true,
        });
      }
    } catch (error) {
      console.error('Failed to save rule:', error);
      alert('Gagal menyimpan aturan');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteRule = async (ruleId: number) => {
    if (!confirm('Apakah Anda yakin ingin menghapus aturan ini?')) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/billing/rules/${ruleId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        alert('Aturan berhasil dihapus');
        loadRules();
      }
    } catch (error) {
      console.error('Failed to delete rule:', error);
      alert('Gagal menghapus aturan');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRuleStatus = async (ruleId: number, isActive: boolean) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/billing/rules/${ruleId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ is_active: !isActive }),
      });

      if (response.ok) {
        loadRules();
      }
    } catch (error) {
      console.error('Failed to toggle rule status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addCondition = () => {
    setRuleForm({
      ...ruleForm,
      conditions: [
        ...ruleForm.conditions,
        {
          id: Math.random().toString(36).substr(2, 9),
          field: 'patient_type',
          operator: 'equals',
          value: 'outpatient',
        },
      ],
    });
  };

  const updateCondition = (conditionId: string, updates: Partial<RuleCondition>) => {
    setRuleForm({
      ...ruleForm,
      conditions: ruleForm.conditions.map(c =>
        c.id === conditionId ? { ...c, ...updates } : c
      ),
    });
  };

  const removeCondition = (conditionId: string) => {
    setRuleForm({
      ...ruleForm,
      conditions: ruleForm.conditions.filter(c => c.id !== conditionId),
    });
  };

  const addAction = () => {
    setRuleForm({
      ...ruleForm,
      actions: [
        ...ruleForm.actions,
        {
          id: Math.random().toString(36).substr(2, 9),
          type: 'percentage',
          target: 'total',
          value: 10,
        },
      ],
    });
  };

  const updateAction = (actionId: string, updates: Partial<RuleAction>) => {
    setRuleForm({
      ...ruleForm,
      actions: ruleForm.actions.map(a =>
        a.id === actionId ? { ...a, ...updates } : a
      ),
    });
  };

  const removeAction = (actionId: string) => {
    setRuleForm({
      ...ruleForm,
      actions: ruleForm.actions.filter(a => a.id !== actionId),
    });
  };

  const testRule = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/billing/rules/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(testScenario),
      });

      if (response.ok) {
        const data = await response.json();
        setTestResults(data);
      }
    } catch (error) {
      console.error('Failed to test rule:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const editRule = (rule: BillingRule) => {
    setRuleForm(rule);
    setIsEditing(true);
  };

  const newRule = () => {
    setRuleForm({
      name: '',
      description: '',
      rule_type: 'discount',
      conditions: [],
      actions: [],
      priority: 0,
      is_active: true,
    });
    setIsEditing(true);
  };

  const cancelEdit = () => {
    setIsEditing(false);
    setRuleForm({
      name: '',
      description: '',
      rule_type: 'discount',
      conditions: [],
      actions: [],
      priority: 0,
      is_active: true,
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const conditionFields = [
    { value: 'patient_type', label: 'Tipe Pasien' },
    { value: 'payer_type', label: 'Tipe Penanggung' },
    { value: 'service_code', label: 'Kode Layanan' },
    { value: 'service_category', label: 'Kategori Layanan' },
    { value: 'amount', label: 'Jumlah' },
    { value: 'age', label: 'Usia' },
    { value: 'gender', label: 'Jenis Kelamin' },
    { value: 'insurance_type', label: 'Tipe Asuransi' },
  ];

  const conditionOperators = [
    { value: 'equals', label: 'Sama dengan' },
    { value: 'not_equals', label: 'Tidak sama dengan' },
    { value: 'contains', label: 'Mengandung' },
    { value: 'greater_than', label: 'Lebih besar dari' },
    { value: 'less_than', label: 'Lebih kecil dari' },
    { value: 'between', label: 'Antara' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Settings className="h-6 w-6 mr-2" />
            Administrasi Aturan Penagihan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola diskon, biaya tambahan, dan pengecualian penagihan
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowTestModal(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <TestTube className="h-4 w-4 mr-2" />
            Uji Aturan
          </button>
          {!isEditing && (
            <button
              onClick={newRule}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Aturan Baru
            </button>
          )}
        </div>
      </div>

      {/* Rule Editor */}
      {isEditing && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">
              {ruleForm.id ? 'Edit Aturan' : 'Aturan Baru'}
            </h2>
            <button
              onClick={cancelEdit}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nama Aturan *
                </label>
                <input
                  type="text"
                  value={ruleForm.name}
                  onChange={(e) => setRuleForm({ ...ruleForm, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Contoh: Diskon Pasien Lansia"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipe Aturan *
                </label>
                <select
                  value={ruleForm.rule_type}
                  onChange={(e) => setRuleForm({
                    ...ruleForm,
                    rule_type: e.target.value as any
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="discount">Diskon</option>
                  <option value="surcharge">Biaya Tambahan</option>
                  <option value="waiver">Pengecualian</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Deskripsi
              </label>
              <textarea
                value={ruleForm.description}
                onChange={(e) => setRuleForm({ ...ruleForm, description: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Jelaskan kapan aturan ini diterapkan..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Prioritas
                </label>
                <input
                  type="number"
                  value={ruleForm.priority}
                  onChange={(e) => setRuleForm({
                    ...ruleForm,
                    priority: parseInt(e.target.value) || 0
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0 = prioritas tertinggi"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Angka lebih kecil = prioritas lebih tinggi
                </p>
              </div>
              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={ruleForm.is_active}
                    onChange={(e) => setRuleForm({
                      ...ruleForm,
                      is_active: e.target.checked
                    })}
                    className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">Aktif</span>
                </label>
              </div>
            </div>

            {/* Conditions */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-900">Kondisi</h3>
                <button
                  onClick={addCondition}
                  className="inline-flex items-center px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Tambah Kondisi
                </button>
              </div>

              <div className="space-y-3">
                {ruleForm.conditions.map((condition, index) => (
                  <div key={condition.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-500 font-medium">{index + 1}.</span>
                    <select
                      value={condition.field}
                      onChange={(e) => updateCondition(condition.id, {
                        field: e.target.value,
                        value: ''
                      })}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      {conditionFields.map(field => (
                        <option key={field.value} value={field.value}>
                          {field.label}
                        </option>
                      ))}
                    </select>
                    <select
                      value={condition.operator}
                      onChange={(e) => updateCondition(condition.id, {
                        operator: e.target.value
                      })}
                      className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      {conditionOperators.map(op => (
                        <option key={op.value} value={op.value}>
                          {op.label}
                        </option>
                      ))}
                    </select>
                    <input
                      type="text"
                      value={String(condition.value ?? '')}
                      onChange={(e) => updateCondition(condition.id, {
                        value: e.target.value
                      })}
                      className="w-40 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Nilai"
                    />
                    <button
                      onClick={() => removeCondition(condition.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>

              {ruleForm.conditions.length === 0 && (
                <div className="text-center py-4 text-sm text-gray-500 bg-gray-50 rounded-lg">
                  Belum ada kondisi. Klik "Tambah Kondisi" untuk memulai.
                </div>
              )}
            </div>

            {/* Actions */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-900">Aksi</h3>
                <button
                  onClick={addAction}
                  className="inline-flex items-center px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Tambah Aksi
                </button>
              </div>

              <div className="space-y-3">
                {ruleForm.actions.map((action, index) => (
                  <div key={action.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-500 font-medium">{index + 1}.</span>
                    <select
                      value={action.type}
                      onChange={(e) => updateAction(action.id, {
                        type: e.target.value as any
                      })}
                      className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="percentage">Persentase</option>
                      <option value="fixed">Jumlah Tetap</option>
                      <option value="waive">Bebaskan Biaya</option>
                    </select>
                    {action.type !== 'waive' && (
                      <>
                        <select
                          value={action.target}
                          onChange={(e) => updateAction(action.id, {
                            target: e.target.value
                          })}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="total">Total</option>
                          <option value="subtotal">Subtotal</option>
                          <option value="service">Layanan</option>
                        </select>
                        <input
                          type="number"
                          value={action.value}
                          onChange={(e) => updateAction(action.id, {
                            value: parseFloat(e.target.value) || 0
                          })}
                          className="w-32 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                          placeholder={action.type === 'percentage' ? '0-100' : '0'}
                        />
                        <span className="text-sm text-gray-500">
                          {action.type === 'percentage' ? '%' : 'Rp'}
                        </span>
                      </>
                    )}
                    <button
                      onClick={() => removeAction(action.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>

              {ruleForm.actions.length === 0 && (
                <div className="text-center py-4 text-sm text-gray-500 bg-gray-50 rounded-lg">
                  Belum ada aksi. Klik "Tambah Aksi" untuk memulai.
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-3 pt-4 border-t">
              <button
                onClick={cancelEdit}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={saveRule}
                disabled={!ruleForm.name || isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                <Save className="h-4 w-4 mr-2" />
                Simpan Aturan
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Rules List */}
      {!isEditing && (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prioritas</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nama</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipe</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kondisi</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aksi</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aksi</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rules
                  .sort((a, b) => a.priority - b.priority)
                  .map((rule) => (
                    <tr key={rule.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {rule.priority}
                      </td>
                      <td className="px-4 py-4 text-sm">
                        <div>
                          <p className="font-medium text-gray-900">{rule.name}</p>
                          {rule.description && (
                            <p className="text-xs text-gray-500 mt-1">{rule.description}</p>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          rule.rule_type === 'discount' ? 'bg-green-100 text-green-800' :
                          rule.rule_type === 'surcharge' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {rule.rule_type === 'discount' ? 'Diskon' :
                           rule.rule_type === 'surcharge' ? 'Biaya Tambahan' : 'Pengecualian'}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-900">
                        {rule.conditions.length} kondisi
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-900">
                        {rule.actions.length} aksi
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <button
                          onClick={() => toggleRuleStatus(rule.id!, rule.is_active)}
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            rule.is_active
                              ? 'bg-green-100 text-green-800 hover:bg-green-200'
                              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                          }`}
                        >
                          {rule.is_active ? 'Aktif' : 'Nonaktif'}
                        </button>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => editRule(rule)}
                            className="text-blue-600 hover:text-blue-800"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => deleteRule(rule.id!)}
                            className="text-red-600 hover:text-red-800"
                            title="Hapus"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {rules.length === 0 && !isLoading && (
            <div className="text-center py-8 text-gray-500">
              <Settings className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Belum ada aturan penagihan</p>
            </div>
          )}
        </div>
      )}

      {/* Test Modal */}
      {showTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Uji Aturan Penagihan</h2>
              <button
                onClick={() => setShowTestModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Test Scenario */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-4">Skenario Pengujian</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tipe Pasien
                    </label>
                    <select
                      value={testScenario.patient_type}
                      onChange={(e) => setTestScenario({
                        ...testScenario,
                        patient_type: e.target.value
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="outpatient">Rawat Jalan</option>
                      <option value="inpatient">Rawat Inap</option>
                      <option value="emergency">IGD</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tipe Penanggung
                    </label>
                    <select
                      value={testScenario.payer_type}
                      onChange={(e) => setTestScenario({
                        ...testScenario,
                        payer_type: e.target.value
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="cash">Tunai</option>
                      <option value="bpjs">BPJS</option>
                      <option value="insurance">Asuransi</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Kode Layanan
                    </label>
                    <input
                      type="text"
                      value={testScenario.service_code}
                      onChange={(e) => setTestScenario({
                        ...testScenario,
                        service_code: e.target.value
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Contoh: KONSUL-001"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Jumlah Tagihan
                    </label>
                    <input
                      type="number"
                      value={testScenario.amount}
                      onChange={(e) => setTestScenario({
                        ...testScenario,
                        amount: parseFloat(e.target.value) || 0
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0"
                    />
                  </div>
                </div>
              </div>

              {/* Test Button */}
              <div className="flex justify-end">
                <button
                  onClick={testRule}
                  disabled={isLoading}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Jalankan Pengujian
                </button>
              </div>

              {/* Test Results */}
              {testResults.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-4">Hasil Pengujian</h3>
                  <div className="space-y-3">
                    {testResults.map((result) => (
                      <div
                        key={result.rule_id}
                        className={`border-l-4 p-4 rounded-md ${
                          result.is_match
                            ? 'border-green-500 bg-green-50'
                            : 'border-gray-300 bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <p className="text-sm font-medium text-gray-900">
                                {result.rule_name}
                              </p>
                              {result.is_match ? (
                                <CheckCircle className="h-4 w-4 text-green-600" />
                              ) : (
                                <AlertCircle className="h-4 w-4 text-gray-400" />
                              )}
                            </div>
                            <p className="text-xs text-gray-600 mt-1">{result.message}</p>
                            {result.is_match && (
                              <div className="mt-2 text-sm">
                                <div className="flex items-center gap-4">
                                  <span className="text-gray-600">
                                    Asli: {formatCurrency(result.original_amount)}
                                  </span>
                                  <span className="text-green-600 font-medium">
                                    Hasil: {formatCurrency(result.result_amount)}
                                  </span>
                                  <span className={`font-medium ${
                                    result.difference < 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {result.difference < 0 ? '-' : '+'}
                                    {formatCurrency(Math.abs(result.difference))}
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
