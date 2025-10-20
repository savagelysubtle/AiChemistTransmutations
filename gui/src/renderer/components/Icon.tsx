import React from 'react';
import { cn } from '../utils/cn';

export interface IconProps {
  children: React.ReactNode;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const Icon: React.FC<IconProps> = ({
  children,
  size = 'md',
  className,
}) => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center',
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
};

export default Icon;
