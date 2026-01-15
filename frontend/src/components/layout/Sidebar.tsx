'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  Calendar,
  FileText,
  Pill,
  Activity,
  Microscope,
  TestTube,
  Settings,
  Shield,
  ChevronRight,
  DollarSign,
  BarChart3,
} from 'lucide-react';
import { NavSection } from './NavSection';
import { NavItem } from './NavItem';
import { UserRole, MenuItem } from '@/types';

interface SidebarProps {
  currentPath?: string;
  userRole: UserRole;
  onClose?: () => void;
}

const menuConfig: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'LayoutDashboard',
    href: '/app/dashboard',
  },
  {
    id: 'patients',
    label: 'Pasien',
    icon: 'Users',
    href: '/app/patients',
  },
  {
    id: 'registration',
    label: 'Pendaftaran',
    icon: 'FileText',
    href: '/app/patients/new',
  },
  {
    id: 'medical-records',
    label: 'Rekam Medis',
    icon: 'FileText',
    children: [
      { id: 'outpatient', label: 'Rawat Jalan', href: '/app/consultation' },
      { id: 'inpatient', label: 'Rawat Inap', href: '/app/admission' },
      { id: 'emergency', label: 'IGD', href: '/app/emergency' },
      { id: 'clinical', label: 'Catatan Medis', href: '/app/clinical' },
    ],
  },
  {
    id: 'pharmacy',
    label: 'Farmasi',
    icon: 'Pill',
    roles: ['admin', 'pharmacist', 'doctor', 'nurse'],
    children: [
      { id: 'prescription', label: 'Resep', href: '/app/prescriptions' },
      { id: 'inventory', label: 'Stok Obat', href: '/app/inventory' },
    ],
  },
  {
    id: 'radiology',
    label: 'Radiologi',
    icon: 'Microscope',
    roles: ['admin', 'radiologist', 'doctor'],
    href: '/app/radiology',
  },
  {
    id: 'laboratory',
    label: 'Laboratorium',
    icon: 'TestTube',
    roles: ['admin', 'lab_tech', 'doctor'],
    href: '/app/lab',
  },
  {
    id: 'appointments',
    label: 'Janji Temu',
    icon: 'Calendar',
    roles: ['admin', 'doctor', 'nurse', 'receptionist'],
    href: '/app/appointments',
  },
  {
    id: 'queue',
    label: 'Antrian',
    icon: 'Activity',
    href: '/app/queue',
  },
  {
    id: 'schedule',
    label: 'Jadwal',
    icon: 'Calendar',
    roles: ['admin', 'doctor', 'nurse', 'receptionist'],
    href: '/app/schedule',
  },
  {
    id: 'billing',
    label: 'Tagihan',
    icon: 'DollarSign',
    href: '/app/billing',
  },
  {
    id: 'reports',
    label: 'Laporan',
    icon: 'BarChart3',
    roles: ['admin'],
    href: '/app/reports',
  },
];

const adminMenuConfig: MenuItem[] = [
  {
    id: 'admin',
    label: 'Admin',
    icon: 'Shield',
    roles: ['admin'],
    children: [
      { id: 'users', label: 'Manajemen User', href: '/app/admin/users' },
      { id: 'roles', label: 'Roles & Permissions', href: '/app/admin/roles' },
      { id: 'settings', label: 'Pengaturan', href: '/app/admin/settings' },
    ],
  },
];

const iconMap: Record<string, React.ComponentType<{ size?: number }>> = {
  LayoutDashboard,
  Users,
  Calendar,
  FileText,
  Pill,
  Activity,
  Microscope,
  TestTube,
  Settings,
  Shield,
  ChevronRight,
  DollarSign,
  BarChart3,
};

export const Sidebar: React.FC<SidebarProps> = ({
  currentPath = '/',
  userRole,
  onClose,
}) => {
  const router = useRouter();
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const toggleExpanded = (itemId: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
      }
      return next;
    });
  };

  const isMenuItemVisible = (item: MenuItem): boolean => {
    if (!item.roles) return true;
    return item.roles.includes(userRole);
  };

  const isActive = (href?: string): boolean => {
    if (!href) return false;
    return currentPath === href || currentPath.startsWith(href + '/');
  };

  const renderMenuItem = (item: MenuItem, isChild = false): React.ReactNode => {
    if (!isMenuItemVisible(item)) return null;

    const Icon = item.icon ? iconMap[item.icon] : Activity;
    const isExpanded = expandedItems.has(item.id);
    const hasChildren = item.children && item.children.length > 0;

    return (
      <NavItem
        key={item.id}
        href={item.href}
        icon={Icon}
        label={item.label}
        active={isActive(item.href)}
        expanded={isExpanded}
        onToggle={() => toggleExpanded(item.id)}
        onClick={() => {
          if (item.href) {
            router.push(item.href);
            onClose?.();
          }
        }}
      >
        {hasChildren &&
          item.children?.map((child) => (
            <div key={child.id} className="mt-1">
              {renderMenuItem(child, true)}
            </div>
          ))}
      </NavItem>
    );
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Link href="/dashboard" className="sidebar-brand" style={{ textDecoration: 'none' }}>
          <div className="sidebar-logo">SM</div>
          <div className="sidebar-brand-name">SIMRS</div>
        </Link>
      </div>

      <nav className="sidebar-nav">
        <NavSection title="Menu Utama">
          {menuConfig.map((item) => renderMenuItem(item))}
        </NavSection>

        <NavSection title="Sistem">
          {adminMenuConfig.map((item) => renderMenuItem(item))}
          <NavItem
            icon={Settings}
            label="Pengaturan"
            href="/app/settings"
            active={isActive('/app/settings')}
            onClick={() => {
              router.push('/app/settings');
              onClose?.();
            }}
          />
        </NavSection>
      </nav>
    </aside>
  );
};
