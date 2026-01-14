'use client';

import React, { useState } from 'react';
import { Bell, Menu, X } from 'lucide-react';
import { SearchBar } from './SearchBar';
import { UserAvatar } from './UserAvatar';
import { User } from '@/types';
import { cn } from '@/lib/utils';

interface TopbarProps {
  user: User;
  onMobileMenuToggle?: () => void;
  isMobileMenuOpen?: boolean;
  notificationCount?: number;
  onLogout?: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  user,
  onMobileMenuToggle,
  isMobileMenuOpen = false,
  notificationCount = 0,
  onLogout,
}) => {
  return (
    <header className="topbar">
      <div className="flex items-center gap-4">
        <button
          onClick={onMobileMenuToggle}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
          style={{ border: 'none', background: 'transparent', cursor: 'pointer' }}
          aria-label="Toggle menu"
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        <SearchBar />
      </div>

      <div className="flex items-center gap-3">
        <button
          className="relative btn-icon"
          aria-label="Notifications"
          style={{ border: 'none', background: 'transparent', cursor: 'pointer' }}
        >
          <Bell size={20} />
          {notificationCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {notificationCount > 9 ? '9+' : notificationCount}
            </span>
          )}
        </button>

        <UserAvatar user={user} onLogout={onLogout} />
      </div>
    </header>
  );
};
