'use client';

import React, { useState } from 'react';
import { Bell, Menu, X } from 'lucide-react';
import { SearchBar } from './SearchBar';
import { UserAvatar } from './UserAvatar';
import { NotificationCenter } from '@/components/notifications/NotificationCenter';
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
  const [showNotificationCenter, setShowNotificationCenter] = useState(false);

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
        <NotificationCenter />

        <UserAvatar user={user} onLogout={onLogout} />
      </div>

      {showNotificationCenter && (
        <div className="fixed inset-0 z-50" onClick={() => setShowNotificationCenter(false)}>
          <div className="fixed right-4 top-16 z-50" onClick={(e) => e.stopPropagation()}>
            <NotificationCenter />
          </div>
        </div>
      )}
    </header>
  );
};
