import React from 'react';
import { cn } from '../utils/cn';

export interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  size = 'md',
  children,
  className,
}) => {
  const baseClasses = 'inline-flex items-center font-medium rounded-full';

  const variantClasses = {
    default: 'bg-light-surfaceElevated dark:bg-dark-surfaceElevated text-light-textPrimary dark:text-dark-textPrimary border border-light-border dark:border-dark-border',
    success: 'bg-light-successBg dark:bg-dark-successBg text-light-success dark:text-dark-success border border-light-success/20 dark:border-dark-success/20',
    warning: 'bg-light-warningBg dark:bg-dark-warningBg text-light-warning dark:text-dark-warning border border-light-warning/20 dark:border-dark-warning/20',
    error: 'bg-light-errorBg dark:bg-dark-errorBg text-light-error dark:text-dark-error border border-light-error/20 dark:border-dark-error/20',
    info: 'bg-light-infoBg dark:bg-dark-infoBg text-light-info dark:text-dark-info border border-light-info/20 dark:border-dark-info/20',
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  return (
    <span
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
};

export default Badge;
