import React, { useState } from 'react';
import Button from './Button';
import Card from './Card';

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

  const handleActivate = async () => {
    if (!licenseKey.trim()) {
      setError('Please enter a license key');
      return;
    }

    setIsActivating(true);
    setError('');
    setSuccess(false);

    try {
      const electronAPI = (window as any).electronAPI;
      if (!electronAPI?.activateLicense) {
        throw new Error('License activation not available');
      }

      const result = await electronAPI.activateLicense(licenseKey.trim());

      if (result.success) {
        setSuccess(true);
        setLicenseKey('');
        setTimeout(() => {
          onActivated?.();
          onClose();
        }, 2000);
      } else {
        setError(result.error || 'License activation failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to activate license');
    } finally {
      setIsActivating(false);
    }
  };

  const handleBuyLicense = () => {
    // Open Gumroad/purchase page
    const purchaseUrl = 'https://gumroad.com/l/aichemist-codex'; // TODO: Update with actual URL
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
            </div>
          </>
        )}
      </Card>
    </div>
  );
};

export default LicenseDialog;
