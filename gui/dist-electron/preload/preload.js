"use strict";
const electron = require("electron");
const electronAPI = {
  openFileDialog: () => electron.ipcRenderer.invoke("dialog:openFile"),
  openDirectoryDialog: () => electron.ipcRenderer.invoke("dialog:openDirectory"),
  runConversion: (args) => electron.ipcRenderer.invoke("run-conversion", args),
  onConversionEvent: (callback) => {
    const listener = (_event, eventData) => callback(eventData);
    electron.ipcRenderer.on("conversion-event", listener);
    return () => {
      electron.ipcRenderer.removeListener("conversion-event", listener);
    };
  },
  // Implementation for the new method
  convertMdxToMd: (args) => electron.ipcRenderer.invoke("convert-mdx-to-md", args),
  // Optional: Notify main process that GUI log was cleared
  notifyLogCleared: () => electron.ipcRenderer.send("log:gui-cleared")
};
electron.contextBridge.exposeInMainWorld("electronAPI", electronAPI);
