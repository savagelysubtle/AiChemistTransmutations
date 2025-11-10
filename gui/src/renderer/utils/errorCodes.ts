/**
 * Frontend Error Codes
 *
 * These error codes correspond to backend error codes where applicable,
 * and include frontend-specific error codes for UI and Electron communication issues.
 */

export enum ErrorCode {
  // Frontend/Electron Errors (20000-20099)
  FRONTEND_ELECTRON_API_UNAVAILABLE = "FRONTEND_001",
  FRONTEND_FILE_DIALOG_FAILED = "FRONTEND_002",
  FRONTEND_DIRECTORY_DIALOG_FAILED = "FRONTEND_003",
  FRONTEND_CONVERSION_START_FAILED = "FRONTEND_004",
  FRONTEND_INVALID_INPUT = "FRONTEND_005",
  FRONTEND_NO_FILES_SELECTED = "FRONTEND_006",
  FRONTEND_INVALID_CONVERSION_TYPE = "FRONTEND_007",
  FRONTEND_PYTHON_PROCESS_FAILED = "FRONTEND_008",
  FRONTEND_JSON_PARSE_FAILED = "FRONTEND_009",
  FRONTEND_LICENSE_ACTIVATION_FAILED = "FRONTEND_010",
  FRONTEND_LICENSE_STATUS_FAILED = "FRONTEND_011",
  FRONTEND_TELEMETRY_FAILED = "FRONTEND_012",
  FRONTEND_EXTERNAL_URL_FAILED = "FRONTEND_013",

  // Backend Error Codes (mapped from Python backend)
  // Validation Errors (1000-1999)
  VALIDATION_FILE_NOT_FOUND = "VALIDATION_001",
  VALIDATION_INVALID_FORMAT = "VALIDATION_002",
  VALIDATION_FILE_TOO_LARGE = "VALIDATION_003",
  VALIDATION_INVALID_PATH = "VALIDATION_004",

  // Conversion Errors (2000-2999)
  CONVERSION_FAILED = "CONVERSION_001",
  CONVERSION_TIMEOUT = "CONVERSION_002",
  CONVERSION_DEPENDENCY_MISSING = "CONVERSION_003",

  // File Operation Errors (3000-3999)
  FILE_OPERATION_FAILED = "FILE_OPERATION_001",
  FILE_OPERATION_PERMISSION_DENIED = "FILE_OPERATION_002",
  FILE_OPERATION_NOT_FOUND = "FILE_OPERATION_003",

  // Security Errors (4000-4999)
  SECURITY_PATH_TRAVERSAL = "SECURITY_001",
  SECURITY_DANGEROUS_FILE_TYPE = "SECURITY_002",

  // Bridge Errors (11000-11099)
  BRIDGE_INVALID_ARGUMENTS = "BRIDGE_001",
  BRIDGE_PLUGIN_LOAD_FAILED = "BRIDGE_002",
  BRIDGE_CONVERTER_NOT_FOUND = "BRIDGE_003",
  BRIDGE_CONVERSION_EXECUTION_FAILED = "BRIDGE_004",
  BRIDGE_BATCH_EXECUTION_FAILED = "BRIDGE_005",
  BRIDGE_MERGE_EXECUTION_FAILED = "BRIDGE_006",
  BRIDGE_JSON_SERIALIZATION_FAILED = "BRIDGE_007",
  BRIDGE_INVALID_MODE = "BRIDGE_008",
  BRIDGE_VALIDATION_FAILED = "BRIDGE_009",
  BRIDGE_OUTPUT_DIRECTORY_INVALID = "BRIDGE_010",

  // Service Errors (12000-12099)
  SERVICE_BATCH_INVALID_CONVERSION_TYPE = "SERVICE_BATCH_001",
  SERVICE_BATCH_CONVERTER_NOT_FOUND = "SERVICE_BATCH_002",
  SERVICE_BATCH_FILE_PROCESSING_FAILED = "SERVICE_BATCH_003",
  SERVICE_MERGE_INVALID_INPUT = "SERVICE_MERGE_001",
  SERVICE_MERGE_PDF_READ_FAILED = "SERVICE_MERGE_002",
  SERVICE_MERGE_PDF_WRITE_FAILED = "SERVICE_MERGE_003",
  SERVICE_MERGE_PDF_CORRUPTED = "SERVICE_MERGE_004",
}

/**
 * Get a human-readable error message for an error code
 */
export function getErrorMessage(errorCode: string, context?: Record<string, any>): string {
  const messages: Record<string, string> = {
    // Frontend errors
    [ErrorCode.FRONTEND_ELECTRON_API_UNAVAILABLE]: "Electron API is not available. Ensure preload script is working.",
    [ErrorCode.FRONTEND_FILE_DIALOG_FAILED]: "Failed to open file dialog.",
    [ErrorCode.FRONTEND_DIRECTORY_DIALOG_FAILED]: "Failed to open directory dialog.",
    [ErrorCode.FRONTEND_CONVERSION_START_FAILED]: "Failed to start conversion process.",
    [ErrorCode.FRONTEND_INVALID_INPUT]: "Invalid input provided.",
    [ErrorCode.FRONTEND_NO_FILES_SELECTED]: "No input files selected.",
    [ErrorCode.FRONTEND_INVALID_CONVERSION_TYPE]: "Invalid conversion type specified.",
    [ErrorCode.FRONTEND_PYTHON_PROCESS_FAILED]: "Python process failed to start or execute.",
    [ErrorCode.FRONTEND_JSON_PARSE_FAILED]: "Failed to parse JSON response from backend.",
    [ErrorCode.FRONTEND_LICENSE_ACTIVATION_FAILED]: "License activation failed.",
    [ErrorCode.FRONTEND_LICENSE_STATUS_FAILED]: "Failed to retrieve license status.",
    [ErrorCode.FRONTEND_TELEMETRY_FAILED]: "Telemetry operation failed.",
    [ErrorCode.FRONTEND_EXTERNAL_URL_FAILED]: "Failed to open external URL.",

    // Backend errors
    [ErrorCode.VALIDATION_FILE_NOT_FOUND]: "File not found.",
    [ErrorCode.VALIDATION_INVALID_FORMAT]: "Invalid file format.",
    [ErrorCode.VALIDATION_FILE_TOO_LARGE]: "File size exceeds maximum limit.",
    [ErrorCode.CONVERSION_FAILED]: "Conversion process failed.",
    [ErrorCode.CONVERSION_TIMEOUT]: "Conversion process timed out.",
    [ErrorCode.BRIDGE_CONVERSION_EXECUTION_FAILED]: "Backend conversion execution failed.",
    [ErrorCode.SERVICE_MERGE_INVALID_INPUT]: "Invalid input for PDF merge operation.",
  };

  let message = messages[errorCode] || `Error: ${errorCode}`;

  if (context) {
    if (context.file) message += ` File: ${context.file}`;
    if (context.path) message += ` Path: ${context.path}`;
    if (context.details) message += ` Details: ${context.details}`;
  }

  return message;
}

/**
 * Extract error code from error message or object
 */
export function extractErrorCode(error: any): string | null {
  if (typeof error === 'string') {
    // Check if error message contains an error code pattern [CODE]
    const match = error.match(/\[([A-Z_]+\d+)\]/);
    if (match) return match[1];

    // Check if error is already an error code
    if (Object.values(ErrorCode).includes(error as ErrorCode)) {
      return error;
    }
  }

  if (error && typeof error === 'object') {
    if (error.error_code) return error.error_code;
    if (error.code) return error.code;
    if (error.errorCode) return error.errorCode;
  }

  return null;
}



















