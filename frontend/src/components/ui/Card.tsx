import React from 'react';

export type CardVariant = 'default' | 'interactive' | 'elevated';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  children: React.ReactNode;
}

/**
 * Card Component
 *
 * A versatile container component with multiple variants:
 * - default: Standard card with subtle shadow
 * - interactive: Hover effects with cursor pointer
 * - elevated: Prominent shadow for emphasis
 *
 * Uses enhanced-simrs-components.css classes:
 * - .card: Base card styling
 * - .card-interactive: Hover effects
 * - .card-elevated: Enhanced shadow
 */
export const Card: React.FC<CardProps> = ({
  variant = 'default',
  className = '',
  children,
  ...props
}) => {
  const cardClasses = [
    'card',
    variant === 'interactive' && 'card-interactive',
    variant === 'elevated' && 'card-elevated',
    className
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={cardClasses} {...props}>
      {children}
    </div>
  );
};

/**
 * Card.Header Component
 * Provides a styled header section with optional title
 */
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  className = '',
  children,
  ...props
}) => {
  return (
    <div className={`card-header ${className}`.trim()} {...props}>
      {title ? <h3 className="card-title">{title}</h3> : children}
    </div>
  );
};

/**
 * Card.Body Component
 * Main content area with consistent padding
 */
export interface CardBodyProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardBody: React.FC<CardBodyProps> = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <div className={`card-body ${className}`.trim()} {...props}>
      {children}
    </div>
  );
};

/**
 * Card.Footer Component
 * Bottom section with subtle background
 */
export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardFooter: React.FC<CardFooterProps> = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <div className={`card-footer ${className}`.trim()} {...props}>
      {children}
    </div>
  );
};

// Display names for debugging
Card.displayName = 'Card';
CardHeader.displayName = 'Card.Header';
CardBody.displayName = 'Card.Body';
CardFooter.displayName = 'Card.Footer';
