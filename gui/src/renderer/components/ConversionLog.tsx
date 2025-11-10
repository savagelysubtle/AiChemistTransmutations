import React from 'react';
import { Scrollbars } from 'react-custom-scrollbars-2';
import { Download, Trash2, Clock, CheckCircle, AlertCircle, Info, XCircle } from 'lucide-react';
import Button from './Button';
import Badge from './Badge';
import Icon from './Icon';
import Card from './Card';
import { cn } from '../utils/cn';

/**
 * Props for the ConversionLog component.
 */
interface ConversionLogProps {
  /** Array of log messages to display. */
  logs: string[];
  /** Callback function to clear the log. */
  onClearLog: () => void;
}

interface LogEntry {
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  raw: string;
}

/**
 * Component for displaying conversion log messages with enhanced styling.
 */
const ConversionLog: React.FC<ConversionLogProps> = ({ logs, onClearLog }) => {
  const parseLogEntry = (log: string): LogEntry => {
    const timestamp = new Date().toLocaleTimeString();

    // Extract error code if present (format: [CODE])
    const errorCodeMatch = log.match(/\[([A-Z_]+\d+)\]/);
    const errorCode = errorCodeMatch ? errorCodeMatch[1] : undefined;

    // Determine log level based on content and error code
    let level: LogEntry['level'] = 'info';
    if (log.includes('ERROR') || log.includes('Error') || log.includes('Failed') || errorCode) {
      // Check if error code indicates an error
      if (errorCode && (
        errorCode.startsWith('FRONTEND_') ||
        errorCode.startsWith('BRIDGE_') ||
        errorCode.startsWith('SERVICE_') ||
        errorCode.startsWith('CONVERSION_') ||
        errorCode.startsWith('VALIDATION_') ||
        errorCode.startsWith('FILE_OPERATION_') ||
        errorCode.startsWith('SECURITY_')
      )) {
        level = 'error';
      } else if (log.includes('ERROR') || log.includes('Error') || log.includes('Failed')) {
        level = 'error';
      }
    } else if (log.includes('SUCCESS') || log.includes('Success') || log.includes('Completed')) {
      level = 'success';
    } else if (log.includes('Warning') || log.includes('WARN')) {
      level = 'warning';
    }

    return {
      timestamp,
      level,
      message: log,
      raw: log,
    };
  };

  const getLogIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-dark-success" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-dark-warning" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-dark-error" />;
      default:
        return <Info className="w-4 h-4 text-dark-info" />;
    }
  };

  const getLogBadgeVariant = (level: LogEntry['level']) => {
    switch (level) {
      case 'success':
        return 'success' as const;
      case 'warning':
        return 'warning' as const;
      case 'error':
        return 'error' as const;
      default:
        return 'info' as const;
    }
  };

  const exportLogs = () => {
    const logContent = logs.join('\n');
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversion-log-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const parsedLogs = logs.map(parseLogEntry);

  return (
    <Card variant="elevated" className="animate-fade-in">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-dark-textPrimary">Conversion Log & Progress</h2>
          {logs.length > 0 && (
            <Badge variant="info" size="sm">{logs.length}</Badge>
          )}
        </div>
        <div className="flex gap-2">
          {logs.length > 0 && (
            <Button
              onClick={exportLogs}
              variant="outline"
              size="sm"
            >
              <Icon size="sm" className="mr-1">
                <Download />
              </Icon>
              Export
            </Button>
          )}
          <Button
            onClick={onClearLog}
            variant="outline"
            size="sm"
            disabled={logs.length === 0}
          >
            <Icon size="sm" className="mr-1">
              <Trash2 />
            </Icon>
            Clear
          </Button>
        </div>
      </div>

      <Scrollbars
        autoHeight
        autoHeightMax={300}
        className="border border-dark-border rounded-lg bg-dark-background"
      >
        <div className="p-4 space-y-2">
          {logs.length === 0 ? (
            <div className="text-center py-8">
              <Icon size="lg" className="text-dark-textMuted mb-2">
                <Clock />
              </Icon>
              <p className="text-dark-textSecondary italic">Awaiting conversion actions...</p>
            </div>
          ) : (
            parsedLogs.map((entry, index) => (
              <div
                key={index}
                className={cn(
                  'flex items-start gap-3 p-3 rounded-lg border transition-colors duration-200',
                  entry.level === 'error' && 'bg-dark-errorBg border-dark-error/20',
                  entry.level === 'warning' && 'bg-dark-warningBg border-dark-warning/20',
                  entry.level === 'success' && 'bg-dark-successBg border-dark-success/20',
                  entry.level === 'info' && 'bg-dark-surfaceElevated border-dark-border'
                )}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getLogIcon(entry.level)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={getLogBadgeVariant(entry.level)} size="sm">
                      {entry.level.toUpperCase()}
                    </Badge>
                    <span className="text-xs text-dark-textMuted font-mono">
                      {entry.timestamp}
                    </span>
                  </div>
                  <p className="text-sm text-dark-textPrimary font-mono whitespace-pre-wrap break-words">
                    {entry.message}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </Scrollbars>
    </Card>
  );
};

export default ConversionLog;