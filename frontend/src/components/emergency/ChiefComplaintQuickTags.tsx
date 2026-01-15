import React from 'react';

export interface ChiefComplaint {
  id: string;
  label: string;
  icon: string;
  priority: 'critical' | 'urgent' | 'normal';
  category: string;
}

/**
 * Common chief complaints for Emergency Department (IGD)
 * Organized by priority and category
 */
export const CHIEF_COMPLAINTS: ChiefComplaint[] = [
  // CRITICAL - Life-threatening complaints
  { id: 'chest_pain', label: 'Nyeri Dada', icon: '💔', priority: 'critical', category: 'Kardiovaskuler' },
  { id: 'shortness_of_breath', label: 'Sesak Napas', icon: '🫁', priority: 'critical', category: 'Pernapasan' },
  { id: 'unconscious', label: 'Pingsan/Sadar Menurun', icon: '😵', priority: 'critical', category: 'Neurologis' },
  { id: 'seizure', label: 'Kejang', icon: '⚡', priority: 'critical', category: 'Neurologis' },
  { id: 'severe_bleeding', label: 'Pendarahan Berat', icon: '🩸', priority: 'critical', category: 'Trauma' },

  // URGENT - Needs immediate attention
  { id: 'abdominal_pain', label: 'Nyeri Perut', icon: '🤢', priority: 'urgent', category: 'Gastrointestinal' },
  { id: 'high_fever', label: 'Demam Tinggi', icon: '🌡️', priority: 'urgent', category: 'Umum' },
  { id: 'severe_headache', label: 'Nyeri Kepala Berat', icon: '🤯', priority: 'urgent', category: 'Neurologis' },
  { id: 'allergy', label: 'Reaksi Alergi', icon: '🔴', priority: 'urgent', category: 'Alergi' },
  { id: 'burns', label: 'Luka Bakar', icon: '🔥', priority: 'urgent', category: 'Trauma' },

  // NORMAL - Can wait briefly
  { id: 'trauma', label: 'Trauma/Luka', icon: '🩹', priority: 'normal', category: 'Trauma' },
  { id: 'vomiting', label: 'Muntah/Mual', icon: '🤮', priority: 'normal', category: 'Gastrointestinal' },
  { id: 'dizziness', label: 'Pusing', icon: '😵‍💫', priority: 'normal', category: 'Neurologis' },
  { id: 'poisoning', label: 'Keracunan', icon: '☠️', priority: 'urgent', category: 'Toksin' },
  { id: 'fracture', label: 'Fraktur/Diduga Patah', icon: '🦴', priority: 'urgent', category: 'Trauma' },
];

export interface ChiefComplaintQuickTagsProps {
  selectedComplaints: string[];
  onToggleComplaint: (complaintId: string) => void;
  maxSelection?: number;
  disabled?: boolean;
}

/**
 * ChiefComplaintQuickTags Component
 *
 * One-tap selection of common IGD chief complaints
 * Organized by priority level with color coding
 */
export const ChiefComplaintQuickTags: React.FC<ChiefComplaintQuickTagsProps> = ({
  selectedComplaints,
  onToggleComplaint,
  maxSelection = 3,
  disabled = false,
}) => {
  const criticalComplaints = CHIEF_COMPLAINTS.filter(c => c.priority === 'critical');
  const urgentComplaints = CHIEF_COMPLAINTS.filter(c => c.priority === 'urgent');
  const normalComplaints = CHIEF_COMPLAINTS.filter(c => c.priority === 'normal');

  const isSelected = (id: string) => selectedComplaints.includes(id);
  const isMaxReached = selectedComplaints.length >= maxSelection;

  const getButtonClass = (complaint: ChiefComplaint) => {
    const selected = isSelected(complaint.id);

    if (disabled) {
      return 'bg-gray-100 text-gray-400 cursor-not-allowed border-gray-200';
    }

    if (selected) {
      switch (complaint.priority) {
        case 'critical':
          return 'bg-red-600 text-white border-red-600 shadow-lg shadow-red-200';
        case 'urgent':
          return 'bg-yellow-500 text-white border-yellow-500 shadow-lg shadow-yellow-200';
        default:
          return 'bg-green-600 text-white border-green-600 shadow-lg shadow-green-200';
      }
    }

    switch (complaint.priority) {
      case 'critical':
        return 'bg-white text-red-700 border-red-300 hover:bg-red-50 hover:border-red-400';
      case 'urgent':
        return 'bg-white text-yellow-700 border-yellow-300 hover:bg-yellow-50 hover:border-yellow-400';
      default:
        return 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400';
    }
  };

  const ComplaintSection = ({
    title,
    complaints,
    bgColor,
  }: {
    title: string;
    complaints: ChiefComplaint[];
    bgColor: string;
  }) => (
    <div className={`${bgColor} rounded-lg p-4`}>
      <h4 className="text-sm font-semibold text-gray-900 mb-3">{title}</h4>
      <div className="flex flex-wrap gap-2">
        {complaints.map((complaint) => {
          const canSelect = !isSelected(complaint.id) && isMaxReached && !disabled;
          return (
            <button
              key={complaint.id}
              type="button"
              onClick={() => !canSelect && onToggleComplaint(complaint.id)}
              disabled={disabled || canSelect}
              className={`
                px-3 py-2 rounded-lg border-2 transition-all duration-200
                flex items-center gap-2 text-sm font-medium
                ${getButtonClass(complaint)}
                ${canSelect ? 'opacity-50 cursor-not-allowed' : ''}
                transform active:scale-95
              `}
              title={complaint.category}
            >
              <span className="text-lg">{complaint.icon}</span>
              <span>{complaint.label}</span>
              {isSelected(complaint.id) && (
                <span className="ml-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Keluhan Utama</h3>
        <span className="text-sm text-gray-600">
          {selectedComplaints.length}/{maxSelection} dipilih
        </span>
      </div>

      <div className="space-y-4">
        {/* Critical Complaints - Red background */}
        <ComplaintSection
          title="🚨 KRITIS - Gawat Darurat"
          complaints={criticalComplaints}
          bgColor="bg-red-50"
        />

        {/* Urgent Complaints - Yellow background */}
        <ComplaintSection
          title="⚠️ URGENT - Perlu Segera"
          complaints={urgentComplaints}
          bgColor="bg-yellow-50"
        />

        {/* Normal Complaints - Gray background */}
        <ComplaintSection
          title="📋 Umum - Dapat Menunggu"
          complaints={normalComplaints}
          bgColor="bg-gray-50"
        />
      </div>

      {/* Custom Complaint Input */}
      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-2">Keluhan Lainnya</h4>
        <input
          type="text"
          placeholder="Tulis keluhan lainnya..."
          disabled={disabled}
          className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
        />
      </div>

      {/* Selection Info */}
      {selectedComplaints.length > 0 && (
        <div className="bg-gray-100 rounded-lg p-3">
          <p className="text-sm text-gray-700">
            <span className="font-medium">Keluhan yang dipilih:</span>{" "}
            {selectedComplaints
              .map(id => CHIEF_COMPLAINTS.find(c => c.id === id)?.label)
              .filter(Boolean)
              .join(', ')}
          </p>
        </div>
      )}
    </div>
  );
};

ChiefComplaintQuickTags.displayName = 'ChiefComplaintQuickTags';
