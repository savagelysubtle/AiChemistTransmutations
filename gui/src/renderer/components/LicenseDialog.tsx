import React, { useState, useEffect } from 'react';
import Button from './Button';
import Card from './Card';
import { logError, logErrorFromException, logInfo } from '../utils/logger';
import { ErrorCode } from '../utils/errorCodes';

interface LicenseDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onActivated?: () => void;
}

/**
 * LicenseDialog - Modal for entering and activating license keys
 */
const LicenseDialog: React.FC<LicenseDialogProps> = ({ isOpen, onClose, onActivated }) => {
  const [licenseKey, setLicenseKey] = useState('');
  const [isActivating, setIsActivating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Listen for license debug messages from main process
  useEffect(() => {
    if (!isOpen) return;

    const handleLicenseDebug = (data: { type: string; data: any }) => {
      if (data.type === 'info') {
        console.log('[LICENSE DEBUG]:', data.data);
      } else if (data.type === 'stdout') {
        console.log('[PYTHON STDOUT]:', data.data);
      } else if (data.type === 'stderr') {
        console.error('[PYTHON STDERR]:', data.data);
      } else if (data.type === 'summary') {
        console.group('🔍 License Command Summary');
        console.log('Exit Code:', data.data.exitCode);
        console.log('STDOUT Length:', data.data.stdoutLength);
        console.log('STDERR Length:', data.data.stderrLength);
        if (data.data.stdout) {
          console.log('Full STDOUT:', data.data.stdout);
        }
        if (data.data.stderr) {
          console.error('Full STDERR:', data.data.stderr);
        }
        console.groupEnd();
      }
    };

    // Listen for license-debug IPC messages via electronAPI
    const electronAPI = (window as any).electronAPI;
    if (electronAPI?.onLicenseDebug) {
      const cleanup = electronAPI.onLicenseDebug(handleLicenseDebug);
      return cleanup;
    }
  }, [isOpen]);

  const handleActivate = async () => {
    if (!licenseKey.trim()) {
      setError('Please enter a license key');
      return;
    }

    setIsActivating(true);
    setError('');
    setSuccess(false);

    try {
      logInfo('Starting license activation', { licenseKeyLength: licenseKey.trim().length });
      const electronAPI = (window as any).electronAPI;
      if (!electronAPI?.activateLicense) {
        const errorMsg = 'License activation not available';
        logError(errorMsg, ErrorCode.FRONTEND_LICENSE_ACTIVATION_FAILED, {});
        throw new Error(errorMsg);
      }

      const result = await electronAPI.activateLicense(licenseKey.trim());

      if (result.success) {
        logInfo('License activated successfully', {});
        setSuccess(true);
        setLicenseKey('');
        setTimeout(() => {
          onActivated?.();
          onClose();
        }, 2000);
      } else {
        const errorMsg = result.error || 'License activation failed';
        logError(errorMsg, ErrorCode.FRONTEND_LICENSE_ACTIVATION_FAILED, { result });
        setError(errorMsg);
      }
    } catch (err: any) {
      logErrorFromException(err, ErrorCode.FRONTEND_LICENSE_ACTIVATION_FAILED, {});
      setError(err.message || 'Failed to activate license');
    } finally {
      setIsActivating(false);
    }
  };

  const handleBuyLicense = () => {
    // Open Gumroad/purchase page
    const purchaseUrl = 'https://aichemist.gumroad.com/l/transmutation-codex';
    if ((window as any).electronAPI?.openExternal) {
      (window as any).electronAPI.openExternal(purchaseUrl);
    } else {
      window.open(purchaseUrl, '_blank');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <Card variant="elevated" className="w-full max-w-md mx-4 animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-light-textPrimary dark:text-dark-textPrimary">
            Activate License
          </h2>
          <button
            onClick={onClose}
            className="text-light-textSecondary dark:text-dark-textSecondary hover:text-light-textPrimary dark:hover:text-dark-textPrimary transition-colors"
            disabled={isActivating}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {success ? (
          <div className="p-4 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-lg mb-6 flex items-start gap-3">
            <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-semibold">License Activated Successfully!</p>
              <p className="text-sm mt-1">All premium features are now unlocked.</p>
            </div>
          </div>
        ) : (
          <>
            <p className="text-light-textSecondary dark:text-dark-textSecondary mb-4">
              Enter your license key to unlock all premium features including unlimited conversions, all formats, and no file size limits.
            </p>

            <div className="mb-4">
              <label className="block text-sm font-medium text-light-textPrimary dark:text-dark-textPrimary mb-2">
                License Key
              </label>
              <input
                type="text"
                value={licenseKey}
                onChange={(e) => setLicenseKey(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleActivate()}
                placeholder="AICHEMIST-XXXXX-XXXXX-XXXXX"
                className="w-full px-4 py-2 border border-light-border dark:border-dark-border rounded-lg bg-light-surface dark:bg-dark-surface text-light-textPrimary dark:text-dark-textPrimary placeholder-light-textMuted dark:placeholder-dark-textMuted focus:outline-none focus:ring-2 focus:ring-light-gradientStart dark:focus:ring-dark-gradientStart"
                disabled={isActivating}
              />
            </div>

            {error && (
              <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded-lg mb-4 text-sm flex items-start gap-2">
                <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            <div className="flex gap-3">
              <Button
                onClick={handleActivate}
                variant="primary"
                className="flex-1"
                disabled={isActivating || !licenseKey.trim()}
              >
                {isActivating ? 'Activating...' : 'Activate License'}
              </Button>
              <Button
                onClick={onClose}
                variant="secondary"
                disabled={isActivating}
              >
                Cancel
              </Button>
            </div>

            <div className="mt-6 pt-6 border-t border-light-border dark:border-dark-border">
              <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary mb-3 text-center">
                Don't have a license yet?
              </p>
              <Button
                onClick={handleBuyLicense}
                variant="secondary"
                size="sm"
                className="w-full"
              >
                Purchase License
              </Button>

              {/* Legal and privacy links */}
              <div className="mt-4 text-center text-xs text-light-textMuted dark:text-dark-textMuted">
                <button
                  className="hover:text-light-gradientStart dark:hover:text-dark-gradientStart hover:underline"
                  onClick={() => {
                    const electronAPI = (window as any).electronAPI;
                    if (electronAPI?.openExternal) {
                      electronAPI.openExternal('https://aichemist.app/privacy');
                    }
                  }}
                >
                  Privacy Policy
                </button>
                {' • '}
                <button
                  className="hover:text-light-gradientStart dark:hover:text-dark-gradientStart hover:underline"
                  onClick={() => {
                    const electronAPI = (window as any).electronAPI;
                    if (electronAPI?.openExternal) {
                      electronAPI.openExternal('https://aichemist.app/terms');
                    }
                  }}
                >
                  Terms of Service
                </button>
                {' • '}
                <button
                  className="hover:text-light-gradientStart dark:hover:text-dark-gradientStart hover:underline"
                  onClick={() => {
                    const electronAPI = (window as any).electronAPI;
                    if (electronAPI?.openExternal) {
                      electronAPI.openExternal('https://aichemist.app/support');
                    }
                  }}
                >
                  Support
                </button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  );
};

export default LicenseDialog;
