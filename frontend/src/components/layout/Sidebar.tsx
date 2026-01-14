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
    href: '/dashboard',
  },
  {
    id: 'patients',
    label: 'Pasien',
    icon: 'Users',
    href: '/patients',
  },
  {
    id: 'registration',
    label: 'Pendaftaran',
    icon: 'FileText',
    href: '/registration',
  },
  {
    id: 'medical-records',
    label: 'Rekam Medis',
    icon: 'FileText',
    children: [
      { id: 'outpatient', label: 'Rawat Jalan', href: '/medical-records/outpatient' },
      { id: 'inpatient', label: 'Rawat Inap', href: '/medical-records/inpatient' },
      { id: 'emergency', label: 'IGD', href: '/medical-records/emergency' },
    ],
  },
  {
    id: 'pharmacy',
    label: 'Farmasi',
    icon: 'Pill',
    roles: ['admin', 'pharmacist', 'doctor', 'nurse'],
    children: [
      { id: 'prescription', label: 'Resep', href: '/pharmacy/prescription' },
      { id: 'inventory', label: 'Stok Obat', href: '/pharmacy/inventory' },
    ],
  },
  {
    id: 'radiology',
    label: 'Radiologi',
    icon: 'Microscope',
    roles: ['admin', 'radiologist', 'doctor'],
    href: '/radiology',
  },
  {
    id: 'laboratory',
    label: 'Laboratorium',
    icon: 'TestTube',
    roles: ['admin', 'lab_tech', 'doctor'],
    href: '/laboratory',
  },
  {
    id: 'schedule',
    label: 'Jadwal Dokter',
    icon: 'Calendar',
    roles: ['admin', 'doctor', 'nurse', 'receptionist'],
    href: '/schedule',
  },
];

const adminMenuConfig: MenuItem[] = [
  {
    id: 'admin',
    label: 'Admin',
    icon: 'Shield',
    roles: ['admin'],
    children: [
      { id: 'users', label: 'Manajemen User', href: '/admin/users' },
      { id: 'roles', label: 'Roles & Permissions', href: '/admin/roles' },
      { id: 'settings', label: 'Pengaturan', href: '/admin/settings' },
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
            href="/settings"
            active={isActive('/settings')}
            onClick={() => {
              router.push('/settings');
              onClose?.();
            }}
          />
        </NavSection>
      </nav>
    </aside>
  );
};
