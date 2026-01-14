'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { User, Settings, LogOut, ChevronDown } from 'lucide-react';
import { User as UserType } from '@/types';
import { cn } from '@/lib/utils';

interface UserAvatarProps {
  user: UserType;
  onLogout?: () => void;
}

export const UserAvatar: React.FC<UserAvatarProps> = ({ user, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleLabel = (role: string) => {
    const roleLabels: Record<string, string> = {
      admin: 'Administrator',
      doctor: 'Dokter',
      nurse: 'Perawat',
      pharmacist: 'Apoteker',
      receptionist: 'Resepsionis',
      radiologist: 'Radiolog',
      lab_tech: 'Teknisi Lab',
    };
    return roleLabels[role] || role;
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
        style={{ border: 'none', background: 'transparent', cursor: 'pointer' }}
      >
        <div className="topbar-avatar">
          {user.avatar ? (
            <img
              src={user.avatar}
              alt={user.name}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            <span className="text-sm font-semibold">{getInitials(user.name)}</span>
          )}
        </div>
        <div className="hidden md:block text-left">
          <div className="text-sm font-medium text-gray-800">{user.name}</div>
          <div className="text-xs text-gray-500">{getRoleLabel(user.role)}</div>
        </div>
        <ChevronDown size={16} className="text-gray-400 hidden md:block" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
          <div className="px-4 py-3 border-b border-gray-200">
            <p className="text-sm font-medium text-gray-800">{user.name}</p>
            <p className="text-xs text-gray-500 mt-1">{user.email}</p>
            <span className="inline-block mt-2 text-xs px-2 py-1 bg-teal-50 text-teal-700 rounded-full">
              {getRoleLabel(user.role)}
            </span>
          </div>

          <div className="py-2">
            <Link
              href="/profile"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              style={{ textDecoration: 'none' }}
            >
              <User size={18} />
              Profile
            </Link>
            <Link
              href="/settings"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              style={{ textDecoration: 'none' }}
            >
              <Settings size={18} />
              Settings
            </Link>
          </div>

          <div className="border-t border-gray-200 pt-2">
            <button
              onClick={() => {
                onLogout?.();
                setIsOpen(false);
              }}
              className="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              style={{ border: 'none', background: 'transparent', cursor: 'pointer', textAlign: 'left' }}
            >
              <LogOut size={18} />
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
