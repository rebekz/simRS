import React from 'react';
import { NavItem } from './NavItem';

interface NavSectionProps {
  title: string;
  children: React.ReactNode;
}

export const NavSection: React.FC<NavSectionProps> = ({ title, children }) => {
  return (
    <div className="nav-section">
      <div className="nav-section-title">{title}</div>
      {children}
    </div>
  );
};
