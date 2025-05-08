import { contextBridge, ipcRenderer, IpcRendererEvent } from 'electron';

// Define the API that will be exposed to the renderer process
export interface ElectronAPI {
  openFileDialog: (options?: { filters?: Array<{ name: string; extensions: string[] }> }) => Promise<string[]>;
  openDirectoryDialog: () => Promise<string | null>;
  runConversion: (args: {
    conversionType: string;
    inputFiles: string[];
    outputDir?: string;
    options?: Record<string, any>;
  }) => Promise<{ success: boolean; message: string; data?: any }>;
  onConversionEvent: (callback: (eventData: any) => void) => () => void; // Returns a cleanup function
  // Added new method for MDX to MD conversion
  convertMdxToMd: (args: {
    inputFile: string;
    outputFile?: string;
  }) => Promise<{ success: boolean; outputPath?: string; error?: string }>;
  notifyLogCleared?: () => void; // Optional: To inform main process
}

const electronAPI: ElectronAPI = {
  openFileDialog: (options) => ipcRenderer.invoke('dialog:openFile', options),
  openDirectoryDialog: () => ipcRenderer.invoke('dialog:openDirectory'),
  runConversion: (args) => ipcRenderer.invoke('run-conversion', args),
  onConversionEvent: (callback) => {
    const listener = (_event: IpcRendererEvent, eventData: any) => callback(eventData);
    ipcRenderer.on('conversion-event', listener);
    // Return a cleanup function to remove the listener
    return () => {
      ipcRenderer.removeListener('conversion-event', listener);
    };
  },
  // Implementation for the new method
  convertMdxToMd: (args) => ipcRenderer.invoke('convert-mdx-to-md', args),
  // Optional: Notify main process that GUI log was cleared
  notifyLogCleared: () => ipcRenderer.send('log:gui-cleared'),
};

// Expose the API to the renderer process under window.electronAPI
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// It's good practice to also type this on the window object in your renderer's d.ts file
// e.g., in a global.d.ts or similar:
/*
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
*/