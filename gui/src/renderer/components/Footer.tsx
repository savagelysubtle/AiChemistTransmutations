import React from 'react';
import { Github, Heart, Code } from 'lucide-react';
import Icon from './Icon';
import Badge from './Badge';

/**
 * Footer component for the application.
 * Displays version information and links.
 */
const Footer: React.FC = () => {
  return (
    <footer className="border-t border-light-border dark:border-dark-border py-6">
      <div className="flex flex-col items-center gap-4">
        {/* Version and Status */}
        <div className="flex items-center gap-3">
          <Badge variant="info" size="sm">v0.1.0</Badge>
          <Badge variant="success" size="sm">Beta</Badge>
        </div>

        {/* Description */}
        <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary text-center max-w-md">
          A versatile document conversion toolkit powered by Python and Electron
        </p>

        {/* Links */}
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/savagelysubtle"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-light-textSecondary dark:text-dark-textSecondary hover:text-light-primary dark:hover:text-dark-primary transition-colors duration-200"
          >
            <Icon size="sm">
              <Github />
            </Icon>
            <span className="text-sm">GitHub</span>
          </a>

          <div className="flex items-center gap-1 text-light-textMuted dark:text-dark-textMuted">
            <Icon size="xs">
              <Heart />
            </Icon>
            <span className="text-xs">Made with</span>
          </div>

          <div className="flex items-center gap-1 text-light-textMuted dark:text-dark-textMuted">
            <Icon size="xs">
              <Code />
            </Icon>
            <span className="text-xs">TypeScript & Python</span>
          </div>
        </div>

        {/* Copyright */}
        <p className="text-xs text-light-textMuted dark:text-dark-textMuted">
          © 2024 AiChemist Codex. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer;