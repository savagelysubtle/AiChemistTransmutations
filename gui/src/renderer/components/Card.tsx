import React from 'react';
import { cn } from '../utils/cn';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'glass';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = 'default',
  padding = 'md',
}) => {
  const baseClasses = 'rounded-lg border transition-all duration-200';

  const variantClasses = {
    default: 'bg-light-surface dark:bg-dark-surface border-light-border dark:border-dark-border shadow-lg',
    elevated: 'bg-light-surfaceElevated dark:bg-dark-surfaceElevated border-light-border dark:border-dark-border shadow-xl',
    glass: 'bg-light-surface/80 dark:bg-dark-surface/80 backdrop-blur-sm border-light-border/50 dark:border-dark-border/50 shadow-lg',
  };

  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        paddingClasses[padding],
        className
      )}
    >
      {children}
    </div>
  );
};

export default Card;
