import React from 'react';
import { Card, CardProps } from './Card';
import { BPJSBadge } from './BPJSBadge';

export interface Patient {
  id: string;
  name: string;
  rmNumber: string; // Rekam Medis number
  photoUrl?: string;
  isBPJS?: boolean;
  bpjsNumber?: string;
}

export interface PatientCardProps extends Omit<CardProps, 'children'> {
  patient: Patient;
  onClick?: () => void;
  showBPJS?: boolean;
}

/**
 * PatientCard Component
 *
 * Specialized card component for displaying patient information
 * in a SIMRS (Sistem Informasi Manajemen Rumah Sakit) context.
 *
 * Features:
 * - Patient photo with automatic fallback
 * - Patient name prominently displayed
 * - RM (Rekam Medis) number for medical record identification
 * - Optional BPJS badge for insurance status
 * - Clickable for navigation to patient details
 *
 * Uses enhanced-simrs-components.css classes:
 * - .card: Base card styling
 * - .card-patient: Patient-specific border accent
 * - .card-interactive: Hover effects when clickable
 * - .badge-bpjs: BPJS insurance badge
 *
 * @example
 * <PatientCard
 *   patient={{
 *     id: '1',
 *     name: 'Ahmad Wijaya',
 *     rmNumber: 'RM-001234',
 *     photoUrl: '/photos/ahmad.jpg',
 *     isBPJS: true,
 *     bpjsNumber: '1234567890'
 *   }}
 *   onClick={() => navigate(`/patients/${patient.id}`)}
 * />
 */
export const PatientCard: React.FC<PatientCardProps> = ({
  patient,
  onClick,
  showBPJS = true,
  className = '',
  ...props
}) => {
  const {
    name,
    rmNumber,
    photoUrl,
    isBPJS = false,
    bpjsNumber
  } = patient;

  // Generate initials from name for fallback
  const getInitials = (fullName: string): string => {
    const parts = fullName.trim().split(' ');
    if (parts.length === 1) {
      return parts[0].charAt(0).toUpperCase();
    }
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
  };

  // Avatar styles
  const avatarStyle: React.CSSProperties = {
    width: '64px',
    height: '64px',
    borderRadius: 'var(--radius-lg)',
    objectFit: 'cover',
    backgroundColor: 'var(--simrs-primary-100)',
    color: 'var(--simrs-primary-700)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 'var(--text-xl)',
    fontWeight: 'var(--font-semibold)',
    flexShrink: 0
  };

  const cardClasses = [
    'card',
    'card-patient',
    onClick && 'card-interactive',
    className
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <Card
      className={cardClasses}
      onClick={onClick}
      {...props}
    >
      <div
        className="flex items-center gap-4"
        style={{ padding: 'var(--space-4)' }}
      >
        {/* Patient Photo with Fallback */}
        {photoUrl ? (
          <img
            src={photoUrl}
            alt={name}
            style={avatarStyle}
            onError={(e) => {
              // Fallback to initials on image load error
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              const parent = target.parentElement;
              if (parent && !parent.querySelector('.initials-fallback')) {
                const fallback = document.createElement('div');
                fallback.className = 'initials-fallback';
                fallback.style.cssText = `
                  width: 64px;
                  height: 64px;
                  border-radius: var(--radius-lg);
                  background-color: var(--simrs-primary-100);
                  color: var(--simrs-primary-700);
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  font-size: var(--text-xl);
                  font-weight: var(--font-semibold);
                  flex-shrink: 0;
                `;
                fallback.textContent = getInitials(name);
                parent.insertBefore(fallback, target);
              }
            }}
          />
        ) : (
          <div className="initials-fallback" style={avatarStyle}>
            {getInitials(name)}
          </div>
        )}

        {/* Patient Information */}
        <div className="flex flex-col gap-2" style={{ flex: 1, minWidth: 0 }}>
          {/* Patient Name */}
          <h3
            className="font-semibold text-base"
            style={{
              margin: 0,
              color: 'var(--simrs-gray-800)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {name}
          </h3>

          {/* RM Number */}
          <div
            className="text-sm"
            style={{
              color: 'var(--simrs-gray-500)',
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-sm)'
            }}
          >
            {rmNumber}
          </div>

          {/* BPJS Badge */}
          {showBPJS && isBPJS && (
            <div style={{ marginTop: 'var(--space-1)' }}>
              <BPJSBadge showDot>
                {bpjsNumber ? `BPJS: ${bpjsNumber}` : 'Peserta BPJS'}
              </BPJSBadge>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

PatientCard.displayName = 'PatientCard';
