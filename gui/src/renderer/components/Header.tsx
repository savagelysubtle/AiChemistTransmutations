import React from 'react';
import { Sun, Moon, FileText } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import Button from './Button';
import Icon from './Icon';

/**
 * Header component for the application.
 * Displays the main title with gradient effect and theme toggle.
 */
const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="relative py-8">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-light-gradientStart/10 dark:from-dark-gradientStart/10 via-transparent to-light-gradientEnd/10 dark:to-dark-gradientEnd/10 pointer-events-none" />

      <div className="relative flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd rounded-xl shadow-lg">
            <Icon size="lg" className="text-white">
              <FileText />
            </Icon>
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd bg-clip-text text-transparent">
              AiChemist Transmutation
            </h1>
            <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary font-medium">
              Document Conversion Suite
            </p>
          </div>
        </div>

        {/* Theme Toggle */}
        <Button
          onClick={toggleTheme}
          variant="ghost"
          size="md"
          className="p-3"
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
        >
          <Icon size="md">
            {theme === 'light' ? <Moon /> : <Sun />}
          </Icon>
        </Button>
      </div>
    </header>
  );
};

export default Header;