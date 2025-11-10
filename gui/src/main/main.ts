import { spawn } from 'child_process';
import {
  app,
  BrowserWindow,
  dialog,
  ipcMain,
  IpcMainInvokeEvent,
} from 'electron';
import fs from 'node:fs';
import path from 'node:path';
// Removed: import { convertMdxToMd } from '../converters/mdxToMd';
// This import was causing React to load in the main process, which crashes Electron

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

let mainWindow: BrowserWindow | null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
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
                mainWindow.webContents.send('conversion-event', parsedMessage);
              } catch (e) {
                console.error('Failed to parse JSON from Python:', message, e);
                mainWindow.webContents.send('conversion-event', {
                  type: 'raw_error',
                  data: message,
                  error: (e as Error).message,
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
          resolve({
            success: true,
            message: 'Python script finished successfully.',
          });
        } else {
          reject({
            success: false,
            message: `Python script exited with code ${code}. Check logs for details.`,
          });
        }
      });

      pyProcess.on('error', (err: Error) => {
        console.error('Failed to start Python process:', err);
        reject({
          success: false,
          message: `Failed to start Python process: ${err.message}`,
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

      pythonExecutable = pythonBackendExe;
      // The bundled exe can run Python modules with -m flag
      fullArgs = [
        '-m',
        'transmutation_codex.adapters.bridges.license_bridge',
        command,
        ...args,
      ];

      console.log(
        'Production mode - using bundled Python backend:',
        pythonExecutable,
      );
    } else {
      // Development: Use Python script with venv
      const scriptPath = path.resolve(
        appPath,
        '../src/transmutation_codex/adapters/bridges/license_bridge.py',
      );

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
      } catch (e) {
        console.log('Using system Python for license command');
      }

      fullArgs = [scriptPath, command, ...args];
      console.log('Development mode - using Python script');
    }

    console.log('Running license command:', command, args);

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
          reject({
            error: 'Failed to parse license command output',
            stdout,
            stderr,
          });
        }
      } else {
        reject({ error: `License command failed with code ${code}`, stderr });
      }
    });

    pyProcess.on('error', (err: Error) => {
      reject({ error: `Failed to run license command: ${err.message}` });
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
  try {
    return await runLicenseCommand('activate', [licenseKey]);
  } catch (error) {
    console.error('Error activating license:', error);
    throw new Error((error as any).error || 'License activation failed');
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
