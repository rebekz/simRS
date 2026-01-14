'use client';

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { User, UserRole } from '@/types';
import { cn } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
  user: User;
}

export const Layout: React.FC<LayoutProps> = ({ children, user }) => {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [notificationCount] = useState(3);

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  const handleLogout = () => {
    // TODO: Implement logout logic
    console.log('Logout clicked');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar - Desktop */}
      <div className="hidden lg:block">
        <Sidebar currentPath={pathname} userRole={user.role as UserRole} />
      </div>

      {/* Sidebar - Mobile */}
      <div
        className={cn(
          'lg:hidden fixed inset-0 z-40',
          isMobileMenuOpen && 'bg-black/50'
        )}
        onClick={() => setIsMobileMenuOpen(false)}
      >
        <div
          className={cn(
            'sidebar',
            'transition-transform duration-300 ease-in-out',
            isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
          )}
          onClick={(e) => e.stopPropagation()}
        >
          <Sidebar
            currentPath={pathname}
            userRole={user.role as UserRole}
            onClose={() => setIsMobileMenuOpen(false)}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:ml-[280px]">
        <Topbar
          user={user}
          isMobileMenuOpen={isMobileMenuOpen}
          onMobileMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          notificationCount={notificationCount}
          onLogout={handleLogout}
        />

        <main className="p-6">{children}</main>
      </div>
    </div>
  );
};
