import React from 'react';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItemProps {
  href?: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  active?: boolean;
  badge?: string | number;
  onClick?: () => void;
  children?: React.ReactNode;
  expanded?: boolean;
  onToggle?: () => void;
}

export const NavItem: React.FC<NavItemProps> = ({
  href,
  icon: Icon,
  label,
  active = false,
  badge,
  onClick,
  children,
  expanded = false,
  onToggle,
}) => {
  const baseClasses = 'nav-item';
  const activeClasses = active ? 'active' : '';

  const content = (
    <>
      <Icon className="nav-icon" size={20} />
      <span className="nav-label">{label}</span>
      {badge && <span className="nav-badge">{badge}</span>}
      {children && (
        <ChevronRight
          size={16}
          className={cn('transition-transform', expanded && 'rotate-90')}
        />
      )}
    </>
  );

  if (children) {
    return (
      <div>
        <button
          onClick={onToggle}
          className={cn(baseClasses, activeClasses, 'w-full')}
          style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
        >
          {content}
        </button>
        {expanded && <div className="ml-6 mt-1 space-y-1">{children}</div>}
      </div>
    );
  }

  if (href) {
    return (
      <Link href={href} className={cn(baseClasses, activeClasses)} onClick={onClick}>
        {content}
      </Link>
    );
  }

  return (
    <button
      onClick={onClick}
      className={cn(baseClasses, activeClasses)}
      style={{ background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left' }}
    >
      {content}
    </button>
  );
};
