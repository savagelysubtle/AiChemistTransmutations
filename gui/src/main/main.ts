import { spawn } from 'child_process';
import {
  app,
  BrowserWindow,
  dialog,
  ipcMain,
  IpcMainInvokeEvent,
  protocol,
} from 'electron';
import fs from 'node:fs';
import path from 'node:path';
// Removed: import { convertMdxToMd } from '../converters/mdxToMd';
// This import was causing React to load in the main process, which crashes Electron

// Set app user model ID BEFORE anything else for Windows taskbar icon
// This must be called before app.whenReady() and before creating windows
if (process.platform === 'win32') {
  app.setAppUserModelId('com.aichemist.transmutationcodex');
}

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

// Prevent multiple instances of the app
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  console.log('Another instance is already running. Exiting...');
  app.quit();
} else {
  // Handle second instance attempts
  app.on('second-instance', () => {
    // Someone tried to run a second instance, focus our window instead
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

let mainWindow: BrowserWindow | null;

/**
 * Get the app icon path for the current environment
 */
function getIconPath(): string | undefined {
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

  if (isDev) {
    // Development: try multiple paths relative to the project root
    // Windows taskbar REQUIRES .ico file, so prioritize that
    const projectRoot = path.resolve(__dirname, '../../..');
    const devIconPaths = process.platform === 'win32'
      ? [
          // Windows: prioritize .ico files for taskbar
          path.join(projectRoot, 'gui/assets/icon.ico'),
          path.join(projectRoot, 'assets/icon.ico'),
          path.join(projectRoot, 'gui/assets/icon.png'),
          path.join(projectRoot, 'assets/icon.png'),
          path.join(projectRoot, 'public/assets/icon.png'),
        ]
      : [
          // Other platforms: .png is fine
          path.join(projectRoot, 'gui/assets/icon.png'),
          path.join(projectRoot, 'assets/icon.png'),
          path.join(projectRoot, 'public/assets/icon.png'),
          path.join(projectRoot, 'gui/assets/icon.ico'),
          path.join(projectRoot, 'assets/icon.ico'),
        ];

    for (const iconPath of devIconPaths) {
      if (fs.existsSync(iconPath)) {
        console.log(`Using icon: ${iconPath}`);
        return iconPath;
      }
    }
    console.warn('No icon file found in development mode. Using default.');
    return undefined;
  } else {
    // Production: use resources path
    const prodIconPath = path.join(process.resourcesPath, 'assets/icon.ico');
    if (fs.existsSync(prodIconPath)) {
      return prodIconPath;
    }
    // Fallback to .png if .ico doesn't exist
    const prodIconPathPng = path.join(process.resourcesPath, 'assets/icon.png');
    if (fs.existsSync(prodIconPathPng)) {
      return prodIconPathPng;
    }
    return undefined;
  }
}

function createWindow() {
  const iconPath = getIconPath();

  // On Windows, the icon must be set in BrowserWindow options for both window and taskbar
  // Windows taskbar uses the same icon as the window, but it's cached by Windows Explorer
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    icon: iconPath, // This sets both window icon and taskbar icon on Windows
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'), // Adjusted path from dist-electron/main to dist-electron/preload
      nodeIntegration: false, // Recommended for security
      contextIsolation: true, // Recommended for security
    },
  });

  // Vite DEV server URL
  const viteDevServerURL = 'http://localhost:3000'; // Ensure this matches your Vite server port

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL(viteDevServerURL);
    mainWindow.webContents.openDevTools(); // Open DevTools automatically in development
  } else {
    // Load the index.html of the app.
    mainWindow.loadFile(path.join(__dirname, '../../dist/index.html')); // Path from dist-electron/main to dist/index.html
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  // Register protocol FIRST, before creating window
  // This ensures app:// protocol is available when assets load
  if (app.isPackaged) {
    // Production mode - register protocol for assets
    protocol.registerFileProtocol('app', (request, callback) => {
      const url = request.url.substr(6); // Remove 'app://' prefix
      // __dirname is dist-electron/main in production
      // dist/ is at dist-electron/main/../../dist/
      const filePath = path.normalize(path.join(__dirname, '../../dist', url));
      console.log(`[Protocol] Serving: app://${url} -> ${filePath}`);

      // Verify file exists
      if (fs.existsSync(filePath)) {
        callback({ path: filePath });
      } else {
        console.error(`[Protocol] File not found: ${filePath}`);
        callback({ error: -6 }); // FILE_NOT_FOUND
      }
    });
    console.log('[Protocol] Registered app:// protocol for production');
  }

  // Get icon path
  const iconPath = getIconPath();

  // On macOS, set dock icon
  if (iconPath && process.platform === 'darwin' && app.dock) {
    app.dock.setIcon(iconPath);
  }

  createWindow();

  app.on('activate', () => {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// --- IPC Handlers --- (Based on project_brief_gui.rst examples)

ipcMain.handle(
  'dialog:openFile',
  async (
    _event,
    options?: { filters?: Array<{ name: string; extensions: string[] }> },
  ) => {
    if (!mainWindow) return [];
    const dialogOptions: Electron.OpenDialogOptions = {
      properties: ['openFile', 'multiSelections'],
    };
    if (options && options.filters) {
      dialogOptions.filters = options.filters;
    }
    const { canceled, filePaths } = await dialog.showOpenDialog(
      mainWindow,
      dialogOptions,
    );
    return canceled ? [] : filePaths;
  },
);

ipcMain.handle('dialog:openDirectory', async () => {
  if (!mainWindow) return null;
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
  });
  return canceled ? null : filePaths[0];
});

interface RunConversionArgs {
  conversionType: string;
  inputFiles: string[];
  outputDir?: string;
  options?: Record<string, any>; // Matches ElectronAPI definition in preload.ts
}

// Handler for running the Python conversion script
ipcMain.handle(
  'run-conversion',
  async (
    _event: IpcMainInvokeEvent,
    { conversionType, inputFiles, outputDir, options }: RunConversionArgs,
  ) => {
    return new Promise((resolve, reject) => {
      // IMPORTANT: Adjust this path if your script is located elsewhere or if your build process changes structure.
      // This path assumes electron_bridge.py is in <project_root>/src/transmutation_codex/adapters/bridges/electron_bridge.py
      // and main.ts (after compilation) is in <project_root>/gui/dist-electron/main/main.js
      const scriptPath = path.resolve(
        app.getAppPath(),
        '../src/transmutation_codex/adapters/bridges/electron_bridge.py',
      );

      // Determine Python executable: prioritize venv if it exists, otherwise use system python
      // This is a basic approach; more robust venv detection might be needed for different OS/setups.
      const venvPythonPathWindows = path.resolve(
        app.getAppPath(),
        '../.venv/Scripts/python.exe',
      ); // Windows
      const venvPythonPathUnix = path.resolve(
        app.getAppPath(),
        '../.venv/bin/python',
      ); // Unix/macOS

      let pythonExecutable = 'python'; // Default to system python
      // Simple check if venv python exists (replace with a more robust check if needed)
      try {
        const venvPath =
          process.platform === 'win32'
            ? venvPythonPathWindows
            : venvPythonPathUnix;
        fs.accessSync(venvPath); // Use imported fs
        pythonExecutable = venvPath;
        console.log('Using venv Python:', pythonExecutable);
      } catch (e) {
        console.log(
          'Venv Python not found or accessible, using system Python.',
        );
      }

      let args: string[] = [
        scriptPath,
        conversionType,
        '--input-files',
        ...inputFiles,
      ];

      if (outputDir) {
        args.push('--output-dir', outputDir);
      }

      if (options) {
        // Check if options is defined
        Object.entries(options).forEach(([key, value]) => {
          if (
            value !== undefined &&
            value !== null &&
            typeof value !== 'object'
          ) {
            const pythonArg = `--${key.replace(
              /[A-Z]/g,
              (letter) => `-${letter.toLowerCase()}`,
            )}`;
            if (typeof value === 'boolean') {
              if (value === true) args.push(pythonArg);
            } else {
              args.push(pythonArg, String(value));
            }
          }
        });
      }

      console.log(
        'Spawning Python script:',
        pythonExecutable,
        'with args:',
        args.join(' '),
      );
      const pyProcess = spawn(pythonExecutable, args);

      let stdoutBuffer = '';
      pyProcess.stdout.on('data', (data: Buffer) => {
        stdoutBuffer += data.toString();
        console.log(`Python stdout chunk: ${data.toString()}`);
        let boundary = stdoutBuffer.indexOf('\n');
        while (boundary !== -1) {
          const message = stdoutBuffer.substring(0, boundary).trim();
          stdoutBuffer = stdoutBuffer.substring(boundary + 1);
          if (message && mainWindow) {
            if (
              message.startsWith('PROGRESS:') ||
              message.startsWith('BATCH_PROGRESS:') ||
              message.startsWith('RESULT:') ||
              message.startsWith('ERROR:') ||
              message.startsWith('SINGLE_RESULT:') ||
              message.startsWith('BATCH_RESULT:')
            ) {
              try {
                const jsonPart = message.substring(message.indexOf(':') + 1);
                const parsedMessage = JSON.parse(jsonPart);
                // Extract error code if present
                const errorCode =
                  parsedMessage.error_code ||
                  parsedMessage.errorCode ||
                  parsedMessage.data?.error_code ||
                  parsedMessage.data?.errorCode;
                if (errorCode) {
                  console.log(
                    `[${errorCode}] ${
                      parsedMessage.message ||
                      JSON.stringify(parsedMessage.data)
                    }`,
                  );
                }
                mainWindow.webContents.send('conversion-event', parsedMessage);
              } catch (e) {
                const errorCode = 'FRONTEND_JSON_PARSE_FAILED';
                console.error(
                  `[${errorCode}] Failed to parse JSON from Python:`,
                  message,
                  e,
                );
                mainWindow.webContents.send('conversion-event', {
                  type: 'raw_error',
                  data: message,
                  error: (e as Error).message,
                  error_code: errorCode,
                });
              }
            } else {
              console.log('Non-JSON Python stdout:', message);
            }
          }
          boundary = stdoutBuffer.indexOf('\n');
        }
      });

      let stderrBuffer = '';
      pyProcess.stderr.on('data', (data: Buffer) => {
        stderrBuffer += data.toString();
        console.error(`Python stderr chunk: ${data.toString()}`);
        // Send stderr data in chunks or after a newline as well
        let errBoundary = stderrBuffer.indexOf('\n');
        while (errBoundary !== -1) {
          const errMsg = stderrBuffer.substring(0, errBoundary).trim();
          stderrBuffer = stderrBuffer.substring(errBoundary + 1);
          if (errMsg && mainWindow) {
            mainWindow.webContents.send('conversion-event', {
              type: 'stderr',
              data: errMsg,
            });
          }
          errBoundary = stderrBuffer.indexOf('\n');
        }
      });

      pyProcess.on('close', (code: number | null) => {
        console.log(`Python script exited with code ${code}`);
        // Send any remaining stderr
        if (stderrBuffer.trim() && mainWindow) {
          mainWindow.webContents.send('conversion-event', {
            type: 'stderr',
            data: stderrBuffer.trim(),
          });
        }
        if (code === 0) {
          console.log('[SUCCESS] Python script finished successfully');
          resolve({
            success: true,
            message: 'Python script finished successfully.',
          });
        } else {
          const errorCode = 'FRONTEND_PYTHON_PROCESS_FAILED';
          console.error(
            `[${errorCode}] Python script exited with code ${code}. Check logs for details.`,
          );
          reject({
            success: false,
            message: `Python script exited with code ${code}. Check logs for details.`,
            error_code: errorCode,
            exitCode: code,
          });
        }
      });

      pyProcess.on('error', (err: Error) => {
        const errorCode = 'FRONTEND_PYTHON_PROCESS_FAILED';
        console.error(`[${errorCode}] Failed to start Python process:`, err);
        reject({
          success: false,
          message: `Failed to start Python process: ${err.message}`,
          error_code: errorCode,
          error: err.message,
        });
      });
    });
  },
);

// IPC Handler for MDX to MD conversion
// Note: MDX conversion requires React, which cannot run in the Electron main process.
// This needs to be either:
// 1. Implemented in the renderer process, or
// 2. Spawned as a separate Node process, or
// 3. Implemented as a Python converter
ipcMain.handle(
  'convert-mdx-to-md',
  async (
    _event: IpcMainInvokeEvent,
    {
      inputFile,
      outputFile: _outputFile,
    }: { inputFile: string; outputFile?: string },
  ) => {
    console.log(`MDX to MD conversion requested for: ${inputFile}`);
    // For now, return an error indicating this needs to be implemented differently
    return {
      success: false,
      error:
        'MDX to MD conversion is not yet implemented. React cannot run in Electron main process. This converter needs to be reimplemented as a spawned process or moved to Python backend.',
    };
  },
);

// Handler for GUI log clear notification
ipcMain.on('log:gui-cleared', () => {
  console.log('======== GUI Log Cleared by User ========');
  // Here you could add more complex logic, like signaling Python to rotate logs,
  // or rotating Electron's own logs if you implement such a feature.
  // For now, just logging a separator to the Electron main log.
});

// --- License Management IPC Handlers ---

// Helper function to run Python licensing commands
async function runLicenseCommand(
  command: string,
  args: string[] = [],
): Promise<any> {
  return new Promise((resolve, reject) => {
    // Detect if running from production build or development
    const isProduction =
      !process.defaultApp && !process.env.NODE_ENV?.includes('dev');
    const appPath = app.getAppPath();

    console.log('='.repeat(80));
    console.log('LICENSE COMMAND EXECUTION START');
    console.log('='.repeat(80));
    console.log('Command:', command);
    console.log('Args count:', args.length);
    console.log(
      'First 50 chars of first arg:',
      args[0]?.substring(0, 50) + '...',
    );
    console.log('Is Production:', isProduction);
    console.log('App Path:', appPath);
    console.log('Platform:', process.platform);
    console.log('Node ENV:', process.env.NODE_ENV);
    console.log('Default App:', process.defaultApp);

    let pythonExecutable: string;
    let fullArgs: string[];

    if (isProduction) {
      // Production: Use bundled Python backend executable
      // Path structure: resources/python-backend/aichemist_transmutation_codex.exe
      const pythonBackendExe = path.join(
        appPath,
        '..',
        'python-backend',
        'aichemist_transmutation_codex.exe',
      );

      // Try to find the license_bridge.py script in the bundle
      // PyInstaller bundles Python files, so we can call them directly
      const licenseBridgeScript = path.join(
        path.dirname(pythonBackendExe),
        'transmutation_codex',
        'adapters',
        'bridges',
        'license_bridge.py',
      );

      // Check if script exists in bundle
      if (fs.existsSync(licenseBridgeScript)) {
        // Call Python executable directly on the script
        pythonExecutable = pythonBackendExe;
        fullArgs = [licenseBridgeScript, command, ...args];
        console.log('  Using direct script execution');
      } else {
        // Fallback: Use Python executable with -m flag
        pythonExecutable = pythonBackendExe;
        fullArgs = [
          '-m',
          'transmutation_codex.adapters.bridges.license_bridge',
          command,
          ...args,
        ];
        console.log('  Using -m flag (script not found in bundle)');
      }

      console.log('✓ Production mode detected');
      console.log('  Python executable:', pythonExecutable);
      console.log('  Checking if executable exists...');

      try {
        fs.accessSync(pythonExecutable, fs.constants.X_OK);
        console.log('  ✓ Executable exists and is accessible');
      } catch (e) {
        const errorCode = 'FRONTEND_PYTHON_PROCESS_FAILED';
        console.error(
          `[${errorCode}] Executable not found or not accessible:`,
          e,
        );
        reject({
          error: `Python backend not found at: ${pythonExecutable}`,
          details: (e as Error).message,
          error_code: errorCode,
        });
        return;
      }
    } else {
      // Development: Use Python script with venv
      const scriptPath = path.resolve(
        appPath,
        '../src/transmutation_codex/adapters/bridges/license_bridge.py',
      );

      console.log('✓ Development mode detected');
      console.log('  Script path:', scriptPath);

      // Determine Python executable
      const venvPythonPathWindows = path.resolve(
        appPath,
        '../.venv/Scripts/python.exe',
      );
      const venvPythonPathUnix = path.resolve(appPath, '../.venv/bin/python');

      pythonExecutable = 'python';
      try {
        const venvPath =
          process.platform === 'win32'
            ? venvPythonPathWindows
            : venvPythonPathUnix;
        fs.accessSync(venvPath);
        pythonExecutable = venvPath;
        console.log('  ✓ Using venv Python:', pythonExecutable);
      } catch (e) {
        console.log('  ⚠ Venv not found, using system Python');
      }

      // Check if script exists
      try {
        fs.accessSync(scriptPath);
        console.log('  ✓ Script exists and is accessible');
      } catch (e) {
        const errorCode = 'FRONTEND_PYTHON_PROCESS_FAILED';
        console.error(`[${errorCode}] Script not found:`, e);
        reject({
          error: `License bridge script not found at: ${scriptPath}`,
          details: (e as Error).message,
          error_code: errorCode,
        });
        return;
      }

      fullArgs = [scriptPath, command, ...args];
    }

    console.log('Final command to execute:');
    console.log('  Executable:', pythonExecutable);
    console.log(
      '  Arguments:',
      fullArgs
        .map((arg, i) =>
          i === fullArgs.length - 1 && arg.length > 100
            ? `${arg.substring(0, 50)}...${arg.substring(arg.length - 20)}`
            : arg,
        )
        .join(' '),
    );
    console.log('-'.repeat(80));

    console.log('Spawning Python process...');

    // Prepare environment variables for Python subprocess
    // Include all current environment variables plus any Supabase config
    const env = {
      ...process.env,
      // Pass through Supabase environment variables if they exist
      ...(process.env.SUPABASE_URL && { SUPABASE_URL: process.env.SUPABASE_URL }),
      ...(process.env.SUPABASE_ANON_KEY && { SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY }),
      ...(process.env.SUPABASE_SERVICE_KEY && { SUPABASE_SERVICE_KEY: process.env.SUPABASE_SERVICE_KEY }),
      // Python path for imports
      PYTHONUNBUFFERED: '1', // Ensure Python output is unbuffered
    };

    // Ensure stderr is available for Python subprocess
    // PyInstaller builds sometimes have issues with stderr, so we need to ensure it's open

    console.log('Environment variables:');
    console.log('  SUPABASE_URL:', process.env.SUPABASE_URL ? '***set***' : 'not set');
    console.log('  SUPABASE_ANON_KEY:', process.env.SUPABASE_ANON_KEY ? '***set***' : 'not set');

    let pyProcess;
    try {
      pyProcess = spawn(pythonExecutable, fullArgs, { env });
      console.log('✓ Process spawned successfully, PID:', pyProcess.pid);
    } catch (spawnError) {
      const errorCode = 'FRONTEND_PYTHON_PROCESS_FAILED';
      console.error(`[${errorCode}] Failed to spawn process:`, spawnError);
      reject({
        error: `Failed to spawn Python process: ${
          (spawnError as Error).message
        }`,
        executable: pythonExecutable,
        args: fullArgs,
        error_code: errorCode,
      });
      return;
    }

    let stdout = '';
    let stderr = '';

    pyProcess.stdout.on('data', (data: Buffer) => {
      const chunk = data.toString();
      stdout += chunk;
      console.log('[PYTHON STDOUT]:', chunk);
      // Send to renderer for DevTools visibility
      if (mainWindow) {
        mainWindow.webContents.send('license-debug', {
          type: 'stdout',
          data: chunk,
        });
      }
    });

    pyProcess.stderr.on('data', (data: Buffer) => {
      const chunk = data.toString();
      stderr += chunk;
      console.error('[PYTHON STDERR]:', chunk);
      // Send to renderer for DevTools visibility
      if (mainWindow) {
        mainWindow.webContents.send('license-debug', {
          type: 'stderr',
          data: chunk,
        });
      }
    });

    pyProcess.on('close', (code: number | null) => {
      const summary = {
        exitCode: code,
        stdoutLength: stdout.length,
        stderrLength: stderr.length,
        stdout,
        stderr,
      };

      console.log('-'.repeat(80));
      console.log('Process exited with code:', code);
      console.log('STDOUT length:', stdout.length);
      console.log('STDERR length:', stderr.length);

      if (stdout) {
        console.log('Full STDOUT:', stdout);
      }
      if (stderr) {
        console.error('Full STDERR:', stderr);
      }
      console.log('='.repeat(80));
      console.log('LICENSE COMMAND EXECUTION END');
      console.log('='.repeat(80));

      // Send summary to renderer for debugging
      if (mainWindow) {
        mainWindow.webContents.send('license-debug', {
          type: 'summary',
          data: summary,
        });
      }

      // Try to parse JSON from stdout regardless of exit code
      // The Python script outputs JSON even on errors before calling sys.exit(1)
      let parsedResult: any = null;
      if (stdout.trim()) {
        try {
          parsedResult = JSON.parse(stdout);
          console.log('✓ Successfully parsed JSON result:', parsedResult);
        } catch (e) {
          console.warn('Could not parse stdout as JSON:', e);
        }
      }

      if (code === 0) {
        if (parsedResult) {
          resolve(parsedResult);
        } else {
          const errorCode = 'FRONTEND_JSON_PARSE_FAILED';
          console.error(`[${errorCode}] No valid JSON output`);
          console.error('Raw stdout:', stdout);
          reject({
            error: 'Failed to parse license command output',
            stdout,
            stderr,
            error_code: errorCode,
          });
        }
      } else {
        const errorCode = 'FRONTEND_LICENSE_ACTIVATION_FAILED';
        console.error(`[${errorCode}] Command failed with non-zero exit code ${code}`);

        // If we have parsed JSON with an error, use that error message
        let errorMessage = `License command failed with code ${code}`;
        if (parsedResult?.error) {
          errorMessage = parsedResult.error;
        } else if (parsedResult?.success === false && parsedResult?.error) {
          errorMessage = parsedResult.error;
        }

        reject({
          error: errorMessage,
          exitCode: code,
          stderr,
          stdout,
          parsedResult,
          error_code: errorCode,
        });
      }
    });

    pyProcess.on('error', (err: Error) => {
      const errorCode = 'FRONTEND_PYTHON_PROCESS_FAILED';
      console.error(`[${errorCode}] Process error event:`, err);
      reject({
        error: `Failed to run license command: ${err.message}`,
        errorName: err.name,
        errorStack: err.stack,
        error_code: errorCode,
      });
    });
  });
}

// Get current license status
ipcMain.handle('license:get-status', async () => {
  try {
    return await runLicenseCommand('get-status');
  } catch (error) {
    console.error('Error getting license status:', error);
    return {
      license_type: 'trial',
      error: (error as any).error || 'Unknown error',
    };
  }
});

// Activate a license key
ipcMain.handle('license:activate', async (_event, licenseKey: string) => {
  console.log('='.repeat(80));
  console.log('LICENSE ACTIVATION REQUESTED');
  console.log('='.repeat(80));
  console.log('License key length:', licenseKey?.length || 0);
  console.log('License key preview:', licenseKey?.substring(0, 50) || 'none');

  // Send initial log to renderer
  if (mainWindow) {
    mainWindow.webContents.send('license-debug', {
      type: 'info',
      data: { message: 'Starting license activation...', licenseKeyLength: licenseKey?.length || 0 },
    });
  }

  try {
    return await runLicenseCommand('activate', [licenseKey]);
  } catch (error: any) {
    console.error('Error activating license:', error);

    // Try to extract the actual error message from stderr or stdout
    let errorMessage = error.error || 'License activation failed';

    // Check if there's JSON output in stdout with an error message
    if (error.stdout) {
      try {
        const stdoutData = JSON.parse(error.stdout);
        if (stdoutData.error) {
          errorMessage = stdoutData.error;
        } else if (stdoutData.success === false && stdoutData.error) {
          errorMessage = stdoutData.error;
        }
      } catch {
        // stdout is not JSON, ignore
      }
    }

    // Extract error from stderr if available (Python logs go to stderr)
    if (error.stderr) {
      // Look for error patterns in stderr
      const stderrLines = error.stderr.split('\n');
      for (const line of stderrLines) {
        // Look for lines like: [LICENSE_BRIDGE] ERROR: ✗ Activation failed: <error>
        if (line.includes('ERROR:') || line.includes('✗')) {
          const match = line.match(/✗\s+(?:Activation failed|Error):\s*(.+)/i);
          if (match) {
            errorMessage = match[1].trim();
            break;
          }
          // Also check for just the error message after ERROR:
          const errorMatch = line.match(/ERROR:\s*(.+)/i);
          if (errorMatch) {
            errorMessage = errorMatch[1].trim();
            break;
          }
        }
      }
    }

    throw new Error(errorMessage);
  }
});

// Deactivate current license
ipcMain.handle('license:deactivate', async () => {
  try {
    return await runLicenseCommand('deactivate');
  } catch (error) {
    console.error('Error deactivating license:', error);
    throw new Error((error as any).error || 'License deactivation failed');
  }
});

// Get trial status
ipcMain.handle('license:get-trial-status', async () => {
  try {
    return await runLicenseCommand('get-trial-status');
  } catch (error) {
    console.error('Error getting trial status:', error);
    return {
      status: 'error',
      error: (error as any).error || 'Unknown error',
    };
  }
});

// --- Telemetry IPC Handlers ---

// Helper function to run Python telemetry commands
async function runTelemetryCommand(
  command: string,
  args: any[] = [],
): Promise<any> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.resolve(
      app.getAppPath(),
      '../src/transmutation_codex/adapters/bridges/telemetry_bridge.py',
    );

    // Determine Python executable
    const venvPythonPathWindows = path.resolve(
      app.getAppPath(),
      '../.venv/Scripts/python.exe',
    );
    const venvPythonPathUnix = path.resolve(
      app.getAppPath(),
      '../.venv/bin/python',
    );

    let pythonExecutable = 'python';
    try {
      const venvPath =
        process.platform === 'win32'
          ? venvPythonPathWindows
          : venvPythonPathUnix;
      fs.accessSync(venvPath);
      pythonExecutable = venvPath;
    } catch (e) {
      console.log('Using system Python for telemetry command');
    }

    const fullArgs = [
      scriptPath,
      command,
      ...args.map((arg) => JSON.stringify(arg)),
    ];
    console.log('Running telemetry command:', command);

    const pyProcess = spawn(pythonExecutable, fullArgs);
    let stdout = '';
    let stderr = '';

    pyProcess.stdout.on('data', (data: Buffer) => {
      stdout += data.toString();
    });

    pyProcess.stderr.on('data', (data: Buffer) => {
      stderr += data.toString();
    });

    pyProcess.on('close', (code: number | null) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          resolve({ success: true }); // If no JSON output, assume success
        }
      } else {
        reject({ error: `Telemetry command failed with code ${code}`, stderr });
      }
    });

    pyProcess.on('error', (err: Error) => {
      reject({ error: `Failed to run telemetry command: ${err.message}` });
    });
  });
}

// Get telemetry consent status
ipcMain.handle('telemetry:get-consent-status', async () => {
  try {
    return await runTelemetryCommand('get-consent-status');
  } catch (error) {
    console.error('Error getting telemetry consent status:', error);
    return {
      has_consent: false,
      can_request: true,
      error: (error as any).error || 'Unknown error',
    };
  }
});

// Grant telemetry consent
ipcMain.handle('telemetry:grant-consent', async () => {
  try {
    return await runTelemetryCommand('grant-consent');
  } catch (error) {
    console.error('Error granting telemetry consent:', error);
    throw new Error((error as any).error || 'Failed to grant consent');
  }
});

// Revoke telemetry consent
ipcMain.handle('telemetry:revoke-consent', async () => {
  try {
    return await runTelemetryCommand('revoke-consent');
  } catch (error) {
    console.error('Error revoking telemetry consent:', error);
    throw new Error((error as any).error || 'Failed to revoke consent');
  }
});

// Open external URL
ipcMain.handle('open-external', async (_event, url: string) => {
  const { shell } = require('electron');
  try {
    await shell.openExternal(url);
    return { success: true };
  } catch (error) {
    console.error('Error opening external URL:', error);
    return { success: false, error: (error as Error).message };
  }
});
