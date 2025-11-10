import { Moon, Sun } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import Button from './Button';
import Icon from './Icon';

// Note: We use string paths for public assets instead of imports
// Vite copies public/assets/ to dist/assets/ during build
// In production, Electron loads from file:// so we need relative paths

/**
 * Header component for the application.
 * Displays the main title with gradient effect and theme toggle.
 */
const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [iconPath, setIconPath] = useState<string>('');

  useEffect(() => {
    // Determine correct path based on environment
    // Vite copies public/assets/ to dist/assets/ during build
    // In dev: Vite serves from /assets/ (absolute path works)
    // In production: Electron uses file:// protocol, needs proper path resolution

    const isDev =
      window.location.href.includes('localhost') ||
      window.location.href.includes('127.0.0.1');
    const isFileProtocol = window.location.protocol === 'file:';

    // Build correct path using URL constructor for proper resolution
    const getAssetPath = (assetName: string): string => {
      if (isDev) {
        return `/assets/${assetName}`; // Dev: absolute path works with Vite
      } else if (isFileProtocol) {
        // Production: Use URL constructor to build proper relative path
        try {
          const baseUrl = new URL(window.location.href);
          const assetUrl = new URL(`./assets/${assetName}`, baseUrl);
          return assetUrl.href;
        } catch (e) {
          // Fallback to relative path string
          return `./assets/${assetName}`;
        }
      } else {
        return `./assets/${assetName}`;
      }
    };

    // Try icon.svg first, then fallback to PNG
    const pathsToTry = [
      getAssetPath('icon.svg'),
      getAssetPath('icon-256x256.png'),
      'app://assets/icon.svg', // Protocol fallback
      './assets/icon.svg', // Simple relative fallback
      '/assets/icon.svg', // Absolute fallback
    ];

    let currentIndex = 0;
    const tryPath = () => {
      if (currentIndex >= pathsToTry.length) {
        console.warn('[Header] All logo paths failed, using text fallback');
        return;
      }

      const path = pathsToTry[currentIndex];
      const img = new Image();

      img.onload = () => {
        console.log(`[Header] Logo loaded successfully from: ${path}`);
        setIconPath(path);
      };

      img.onerror = () => {
        console.warn(`[Header] Failed to load from: ${path}`);
        currentIndex++;
        tryPath();
      };

      img.src = path;
    };

    tryPath();
  }, []);

  return (
    <header className="relative py-8">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-light-gradientStart/10 dark:from-dark-gradientStart/10 via-transparent to-light-gradientEnd/10 dark:to-dark-gradientEnd/10 pointer-events-none" />

      <div className="relative flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="flex-shrink-0 w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center relative">
            {iconPath && (
              <img
                src={iconPath}
                alt="AiChemist Transmutation Codex Logo"
                className="w-14 h-14 object-contain absolute"
                onError={(e) => {
                  // If image fails to load, hide it and show text fallback
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            )}
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
          <Icon size="md">{theme === 'light' ? <Moon /> : <Sun />}</Icon>
        </Button>
      </div>
    </header>
  );
};

export default Header;
