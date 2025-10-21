import React, { useEffect, useState } from 'react';

interface TrialStatusData {
  status: string;
  used: number;
  limit: number;
  remaining: number;
  error?: string;
}

interface LicenseStatusData {
  license_type: string;
  trial_status?: TrialStatusData;
  email?: string;
  error?: string;
}

/**
 * TrialStatus component - Displays trial information badge
 */
const TrialStatus: React.FC = () => {
  const [licenseStatus, setLicenseStatus] = useState<LicenseStatusData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLicenseStatus();
    // Refresh every 30 seconds
    const interval = setInterval(loadLicenseStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadLicenseStatus = async () => {
    try {
      const electronAPI = (window as any).electronAPI;
      if (!electronAPI?.getLicenseStatus) {
        console.warn('License API not available');
        return;
      }

      const status = await electronAPI.getLicenseStatus();
      setLicenseStatus(status);
    } catch (error) {
      console.error('Error loading license status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !licenseStatus) {
    return null;
  }

  // Don't show anything for paid licenses
  if (licenseStatus.license_type === 'paid') {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full text-sm font-medium border border-green-200 dark:border-green-800">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="width" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Pro License</span>
      </div>
    );
  }

  // Trial status
  const trialStatus = licenseStatus.trial_status;
  if (!trialStatus) {
    return null;
  }

  const isExpired = trialStatus.remaining === 0;
  const isLow = trialStatus.remaining <= 3 && trialStatus.remaining > 0;

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium border ${
        isExpired
          ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 border-red-200 dark:border-red-800'
          : isLow
          ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 border-yellow-200 dark:border-yellow-800'
          : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-800'
      }`}
    >
      {isExpired ? (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <span>Trial Expired</span>
        </>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <span>
            {trialStatus.remaining} conversion{trialStatus.remaining !== 1 ? 's' : ''} left
          </span>
        </>
      )}
    </div>
  );
};

export default TrialStatus;
