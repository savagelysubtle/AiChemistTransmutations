/**
 * Frontend Logger Utility
 *
 * Provides structured logging with error codes for the frontend application.
 */

import { ErrorCode, extractErrorCode, getErrorMessage } from './errorCodes';

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  errorCode?: string;
  context?: Record<string, any>;
  error?: Error;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // Maximum number of logs to keep in memory
  private listeners: Array<(entry: LogEntry) => void> = [];

  /**
   * Add a listener for log entries
   */
  addListener(listener: (entry: LogEntry) => void): () => void {
    this.listeners.push(listener);
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  /**
   * Get all logs
   */
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * Clear all logs
   */
  clearLogs(): void {
    this.logs = [];
  }

  /**
   * Internal method to add a log entry
   */
  private addLog(level: LogLevel, message: string, errorCode?: string, context?: Record<string, any>, error?: Error): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      errorCode,
      context,
      error,
    };

    this.logs.push(entry);

    // Keep only the most recent logs
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // Notify listeners
    this.listeners.forEach(listener => {
      try {
        listener(entry);
      } catch (e) {
        console.error('Error in log listener:', e);
      }
    });

    // Also log to console in development
    if (process.env.NODE_ENV === 'development') {
      const logMessage = errorCode
        ? `[${errorCode}] ${message}`
        : message;

      switch (level) {
        case LogLevel.DEBUG:
          console.debug(logMessage, context || '');
          break;
        case LogLevel.INFO:
          console.info(logMessage, context || '');
          break;
        case LogLevel.WARN:
          console.warn(logMessage, context || '');
          break;
        case LogLevel.ERROR:
          console.error(logMessage, context || '', error || '');
          break;
      }
    }
  }

  /**
   * Log a debug message
   */
  debug(message: string, context?: Record<string, any>): void {
    this.addLog(LogLevel.DEBUG, message, undefined, context);
  }

  /**
   * Log an info message
   */
  info(message: string, context?: Record<string, any>): void {
    this.addLog(LogLevel.INFO, message, undefined, context);
  }

  /**
   * Log a warning message
   */
  warn(message: string, errorCode?: string, context?: Record<string, any>): void {
    this.addLog(LogLevel.WARN, message, errorCode, context);
  }

  /**
   * Log an error message with error code
   */
  error(message: string, errorCode: string, context?: Record<string, any>, error?: Error): void {
    const fullMessage = getErrorMessage(errorCode, { ...context, details: message });
    this.addLog(LogLevel.ERROR, fullMessage, errorCode, context, error);
  }

  /**
   * Log an error from an error object, extracting error code if available
   */
  errorFromException(error: any, defaultCode: string = ErrorCode.FRONTEND_CONVERSION_START_FAILED, context?: Record<string, any>): void {
    const errorCode = extractErrorCode(error) || defaultCode;
    const message = error?.message || error?.error || String(error);
    this.error(message, errorCode, context, error instanceof Error ? error : undefined);
  }
}

// Export singleton instance
export const logger = new Logger();

// Export convenience functions
export const logDebug = (message: string, context?: Record<string, any>) => logger.debug(message, context);
export const logInfo = (message: string, context?: Record<string, any>) => logger.info(message, context);
export const logWarn = (message: string, errorCode?: string, context?: Record<string, any>) => logger.warn(message, errorCode, context);
export const logError = (message: string, errorCode: string, context?: Record<string, any>, error?: Error) => logger.error(message, errorCode, context, error);
export const logErrorFromException = (error: any, defaultCode?: string, context?: Record<string, any>) => logger.errorFromException(error, defaultCode, context);



















