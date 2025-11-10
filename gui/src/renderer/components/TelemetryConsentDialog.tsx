import React, { useState } from 'react';
import Button from './Button';
import Card from './Card';

interface TelemetryConsentDialogProps {
  isOpen: boolean;
  onAccept: () => void;
  onDecline: () => void;
}

/**
 * TelemetryConsentDialog - Modal for requesting user consent for telemetry
 *
 * Displays information about what data is collected and allows user to
 * opt-in or opt-out of anonymous usage tracking.
 */
const TelemetryConsentDialog: React.FC<TelemetryConsentDialogProps> = ({
  isOpen,
  onAccept,
  onDecline,
}) => {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleAccept = async () => {
    setIsProcessing(true);
    try {
      const electronAPI = (window as any).electronAPI;
      if (electronAPI?.grantTelemetryConsent) {
        await electronAPI.grantTelemetryConsent();
      }
      onAccept();
    } catch (error) {
      console.error('Failed to grant telemetry consent:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDecline = async () => {
    setIsProcessing(true);
    try {
      const electronAPI = (window as any).electronAPI;
      if (electronAPI?.revokeTelemetryConsent) {
        await electronAPI.revokeTelemetryConsent();
      }
      onDecline();
    } catch (error) {
      console.error('Failed to revoke telemetry consent:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <Card variant="elevated" className="w-full max-w-2xl mx-4 animate-fade-in">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-br from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd rounded-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-light-textPrimary dark:text-dark-textPrimary">
              Help Us Improve
            </h2>
            <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
              Anonymous usage data helps us make AiChemist better
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-4 mb-6">
          <p className="text-light-textPrimary dark:text-dark-textPrimary">
            We'd like to collect anonymous usage data to help improve AiChemist Transmutation Codex.
            This helps us understand which features are most used, identify bugs, and make informed
            decisions about future improvements.
          </p>

          {/* What we collect */}
          <div className="bg-light-surface dark:bg-dark-surface p-4 rounded-lg border border-light-border dark:border-dark-border">
            <h3 className="font-semibold text-light-textPrimary dark:text-dark-textPrimary mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              What We Collect
            </h3>
            <ul className="space-y-2 text-sm text-light-textSecondary dark:text-dark-textSecondary">
              <li className="flex items-start gap-2">
                <span className="text-green-600 dark:text-green-400 mt-0.5">•</span>
                <span>Feature usage (which converters you use)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 dark:text-green-400 mt-0.5">•</span>
                <span>Conversion success/failure rates</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 dark:text-green-400 mt-0.5">•</span>
                <span>Performance metrics (conversion times, file sizes)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 dark:text-green-400 mt-0.5">•</span>
                <span>Error types (to help us fix bugs)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 dark:text-green-400 mt-0.5">•</span>
                <span>Operating system and app version</span>
              </li>
            </ul>
          </div>

          {/* What we DON'T collect */}
          <div className="bg-light-surface dark:bg-dark-surface p-4 rounded-lg border border-light-border dark:border-dark-border">
            <h3 className="font-semibold text-light-textPrimary dark:text-dark-textPrimary mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
              What We DON'T Collect
            </h3>
            <ul className="space-y-2 text-sm text-light-textSecondary dark:text-dark-textSecondary">
              <li className="flex items-start gap-2">
                <span className="text-red-600 dark:text-red-400 mt-0.5">•</span>
                <span>File contents or document data</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600 dark:text-red-400 mt-0.5">•</span>
                <span>File names or paths</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600 dark:text-red-400 mt-0.5">•</span>
                <span>Personal information (name, email, etc.)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600 dark:text-red-400 mt-0.5">•</span>
                <span>IP addresses or identifying information</span>
              </li>
            </ul>
          </div>

          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-start gap-3 text-sm">
            <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-blue-800 dark:text-blue-200">
              <p className="font-semibold mb-1">Your Privacy Matters</p>
              <p>All data is completely anonymous and is never sold or shared with third parties.
              You can change your mind at any time in Settings.</p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={handleAccept}
            variant="primary"
            className="flex-1"
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Accept & Help Improve'}
          </Button>
          <Button
            onClick={handleDecline}
            variant="secondary"
            className="flex-1"
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'No Thanks'}
          </Button>
        </div>

        {/* Footer links */}
        <div className="mt-6 pt-4 border-t border-light-border dark:border-dark-border text-center text-xs text-light-textMuted dark:text-dark-textMuted">
          <p>
            By accepting, you agree to our{' '}
            <button
              className="text-light-gradientStart dark:text-dark-gradientStart hover:underline"
              onClick={() => {
                const electronAPI = (window as any).electronAPI;
                if (electronAPI?.openExternal) {
                  electronAPI.openExternal('https://aichemist.app/privacy');
                }
              }}
            >
              Privacy Policy
            </button>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default TelemetryConsentDialog;

