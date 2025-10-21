import React from 'react';
import { cn } from '../utils/cn';
import LoadingSpinner from './LoadingSpinner';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  className,
  children,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50';

  const variantClasses = {
    primary: 'bg-dark-primary dark:bg-dark-primary hover:bg-dark-primaryHover dark:hover:bg-dark-primaryHover active:bg-dark-primaryPressed dark:active:bg-dark-primaryPressed text-white focus:ring-dark-primary dark:focus:ring-dark-primary shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95',
    secondary: 'bg-light-surface dark:bg-dark-surfaceElevated hover:bg-light-border dark:hover:bg-dark-border text-light-textPrimary dark:text-dark-textPrimary border border-light-border dark:border-dark-border focus:ring-light-primary dark:focus:ring-dark-primary shadow-md hover:shadow-lg',
    danger: 'bg-light-error dark:bg-dark-error hover:bg-red-600 text-white focus:ring-light-error dark:focus:ring-dark-error shadow-lg hover:shadow-xl',
    ghost: 'bg-transparent hover:bg-light-surfaceElevated dark:hover:bg-dark-surfaceElevated text-light-textPrimary dark:text-dark-textPrimary focus:ring-light-primary dark:focus:ring-dark-primary',
    outline: 'bg-transparent border-2 border-light-primary dark:border-dark-primary text-light-primary dark:text-dark-primary hover:bg-light-primary dark:hover:bg-dark-primary hover:text-white focus:ring-light-primary dark:focus:ring-dark-primary',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const isDisabled = disabled || loading;

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        loading && 'cursor-wait',
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading && (
        <LoadingSpinner size="sm" className="mr-2" />
      )}
      {children}
    </button>
  );
};

export default Button;
