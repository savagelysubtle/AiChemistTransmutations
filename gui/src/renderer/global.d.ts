import { ElectronAPI } from '../main/preload'; // Adjust path if necessary

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}