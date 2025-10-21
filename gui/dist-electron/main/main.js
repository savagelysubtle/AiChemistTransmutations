"use strict";
const electron = require("electron");
const path = require("node:path");
const fs = require("node:fs");
const child_process = require("child_process");
if (require("electron-squirrel-startup")) {
  electron.app.quit();
}
let mainWindow;
function createWindow() {
  mainWindow = new electron.BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      preload: path.join(__dirname, "../preload/preload.js"),
      // Adjusted path from dist-electron/main to dist-electron/preload
      nodeIntegration: false,
      // Recommended for security
      contextIsolation: true
      // Recommended for security
    }
  });
  const viteDevServerURL = "http://localhost:3000";
  if (process.env.NODE_ENV === "development") {
    mainWindow.loadURL(viteDevServerURL);
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "../../dist/index.html"));
  }
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}
electron.app.whenReady().then(() => {
  createWindow();
  electron.app.on("activate", () => {
    if (electron.BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});
electron.app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    electron.app.quit();
  }
});
electron.ipcMain.handle("dialog:openFile", async (_event, options) => {
  if (!mainWindow) return [];
  const dialogOptions = {
    properties: ["openFile", "multiSelections"]
  };
  if (options && options.filters) {
    dialogOptions.filters = options.filters;
  }
  const { canceled, filePaths } = await electron.dialog.showOpenDialog(mainWindow, dialogOptions);
  return canceled ? [] : filePaths;
});
electron.ipcMain.handle("dialog:openDirectory", async () => {
  if (!mainWindow) return null;
  const { canceled, filePaths } = await electron.dialog.showOpenDialog(mainWindow, {
    properties: ["openDirectory"]
  });
  return canceled ? null : filePaths[0];
});
electron.ipcMain.handle("run-conversion", async (_event, { conversionType, inputFiles, outputDir, options }) => {
  return new Promise((resolve, reject) => {
    const scriptPath = path.resolve(electron.app.getAppPath(), "../src/transmutation_codex/adapters/bridges/electron_bridge.py");
    const venvPythonPathWindows = path.resolve(electron.app.getAppPath(), "../.venv/Scripts/python.exe");
    const venvPythonPathUnix = path.resolve(electron.app.getAppPath(), "../.venv/bin/python");
    let pythonExecutable = "python";
    try {
      const venvPath = process.platform === "win32" ? venvPythonPathWindows : venvPythonPathUnix;
      fs.accessSync(venvPath);
      pythonExecutable = venvPath;
      console.log("Using venv Python:", pythonExecutable);
    } catch (e) {
      console.log("Venv Python not found or accessible, using system Python.");
    }
    let args = [
      scriptPath,
      conversionType,
      "--input-files",
      ...inputFiles
    ];
    if (outputDir) {
      args.push("--output-dir", outputDir);
    }
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== void 0 && value !== null && typeof value !== "object") {
          const pythonArg = `--${key.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`;
          if (typeof value === "boolean") {
            if (value === true) args.push(pythonArg);
          } else {
            args.push(pythonArg, String(value));
          }
        }
      });
    }
    console.log("Spawning Python script:", pythonExecutable, "with args:", args.join(" "));
    const pyProcess = child_process.spawn(pythonExecutable, args);
    let stdoutBuffer = "";
    pyProcess.stdout.on("data", (data) => {
      stdoutBuffer += data.toString();
      console.log(`Python stdout chunk: ${data.toString()}`);
      let boundary = stdoutBuffer.indexOf("\n");
      while (boundary !== -1) {
        const message = stdoutBuffer.substring(0, boundary).trim();
        stdoutBuffer = stdoutBuffer.substring(boundary + 1);
        if (message && mainWindow) {
          if (message.startsWith("PROGRESS:") || message.startsWith("BATCH_PROGRESS:") || message.startsWith("RESULT:") || message.startsWith("ERROR:") || message.startsWith("SINGLE_RESULT:") || message.startsWith("BATCH_RESULT:")) {
            try {
              const jsonPart = message.substring(message.indexOf(":") + 1);
              const parsedMessage = JSON.parse(jsonPart);
              mainWindow.webContents.send("conversion-event", parsedMessage);
            } catch (e) {
              console.error("Failed to parse JSON from Python:", message, e);
              mainWindow.webContents.send("conversion-event", { type: "raw_error", data: message, error: e.message });
            }
          } else {
            console.log("Non-JSON Python stdout:", message);
          }
        }
        boundary = stdoutBuffer.indexOf("\n");
      }
    });
    let stderrBuffer = "";
    pyProcess.stderr.on("data", (data) => {
      stderrBuffer += data.toString();
      console.error(`Python stderr chunk: ${data.toString()}`);
      let errBoundary = stderrBuffer.indexOf("\n");
      while (errBoundary !== -1) {
        const errMsg = stderrBuffer.substring(0, errBoundary).trim();
        stderrBuffer = stderrBuffer.substring(errBoundary + 1);
        if (errMsg && mainWindow) {
          mainWindow.webContents.send("conversion-event", { type: "stderr", data: errMsg });
        }
        errBoundary = stderrBuffer.indexOf("\n");
      }
    });
    pyProcess.on("close", (code) => {
      console.log(`Python script exited with code ${code}`);
      if (stderrBuffer.trim() && mainWindow) {
        mainWindow.webContents.send("conversion-event", { type: "stderr", data: stderrBuffer.trim() });
      }
      if (code === 0) {
        resolve({ success: true, message: "Python script finished successfully." });
      } else {
        reject({ success: false, message: `Python script exited with code ${code}. Check logs for details.` });
      }
    });
    pyProcess.on("error", (err) => {
      console.error("Failed to start Python process:", err);
      reject({ success: false, message: `Failed to start Python process: ${err.message}` });
    });
  });
});
electron.ipcMain.handle("convert-mdx-to-md", async (_event, { inputFile, outputFile: _outputFile }) => {
  console.log(`MDX to MD conversion requested for: ${inputFile}`);
  return {
    success: false,
    error: "MDX to MD conversion is not yet implemented. React cannot run in Electron main process. This converter needs to be reimplemented as a spawned process or moved to Python backend."
  };
});
electron.ipcMain.on("log:gui-cleared", () => {
  console.log("======== GUI Log Cleared by User ========");
});
async function runLicenseCommand(command, args = []) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.resolve(electron.app.getAppPath(), "../src/transmutation_codex/adapters/bridges/license_bridge.py");
    const venvPythonPathWindows = path.resolve(electron.app.getAppPath(), "../.venv/Scripts/python.exe");
    const venvPythonPathUnix = path.resolve(electron.app.getAppPath(), "../.venv/bin/python");
    let pythonExecutable = "python";
    try {
      const venvPath = process.platform === "win32" ? venvPythonPathWindows : venvPythonPathUnix;
      fs.accessSync(venvPath);
      pythonExecutable = venvPath;
    } catch (e) {
      console.log("Using system Python for license command");
    }
    const fullArgs = [scriptPath, command, ...args];
    console.log("Running license command:", command, args);
    const pyProcess = child_process.spawn(pythonExecutable, fullArgs);
    let stdout = "";
    let stderr = "";
    pyProcess.stdout.on("data", (data) => {
      stdout += data.toString();
    });
    pyProcess.stderr.on("data", (data) => {
      stderr += data.toString();
    });
    pyProcess.on("close", (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          reject({ error: "Failed to parse license command output", stdout, stderr });
        }
      } else {
        reject({ error: `License command failed with code ${code}`, stderr });
      }
    });
    pyProcess.on("error", (err) => {
      reject({ error: `Failed to run license command: ${err.message}` });
    });
  });
}
electron.ipcMain.handle("license:get-status", async () => {
  try {
    return await runLicenseCommand("get-status");
  } catch (error) {
    console.error("Error getting license status:", error);
    return {
      license_type: "trial",
      error: error.error || "Unknown error"
    };
  }
});
electron.ipcMain.handle("license:activate", async (_event, licenseKey) => {
  try {
    return await runLicenseCommand("activate", [licenseKey]);
  } catch (error) {
    console.error("Error activating license:", error);
    throw new Error(error.error || "License activation failed");
  }
});
electron.ipcMain.handle("license:deactivate", async () => {
  try {
    return await runLicenseCommand("deactivate");
  } catch (error) {
    console.error("Error deactivating license:", error);
    throw new Error(error.error || "License deactivation failed");
  }
});
electron.ipcMain.handle("license:get-trial-status", async () => {
  try {
    return await runLicenseCommand("get-trial-status");
  } catch (error) {
    console.error("Error getting trial status:", error);
    return {
      status: "error",
      error: error.error || "Unknown error"
    };
  }
});
