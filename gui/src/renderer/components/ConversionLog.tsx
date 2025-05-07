import React from 'react';

/**
 * Props for the ConversionLog component.
 */
interface ConversionLogProps {
  /** Array of log messages to display. */
  logs: string[];
  /** Callback function to clear the log. */
  onClearLog: () => void;
}

/**
 * Component for displaying conversion log messages.
 */
const ConversionLog: React.FC<ConversionLogProps> = ({ logs, onClearLog }) => {
  return (
    <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface">
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-2xl font-semibold text-dark-textPrimary">Conversion Log & Progress</h2>
        <button
          onClick={onClearLog}
          className="px-3 py-1 text-sm bg-dark-secondary hover:bg-opacity-80 text-dark-textPrimary border border-dark-border rounded-md shadow-sm transition-colors duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-dark-primary focus:ring-opacity-50"
        >
          Clear Log
        </button>
      </div>
      <div className="h-64 overflow-y-auto p-3 border border-dark-border rounded-md bg-dark-background text-sm font-mono text-dark-textSecondary shadow-inner">
        {logs.length === 0 && <p className="italic text-dark-textSecondary opacity-75">Awaiting conversion actions...</p>}
        {logs.map((log, index) => (
          <p key={index} className="whitespace-pre-wrap break-words text-dark-textSecondary py-0.5">
            {log}
          </p>
        ))}
      </div>
    </section>
  );
};

export default ConversionLog;