\
.. _project_brief_gui:

#########################
Project Brief: MDtoPDF Converter GUI
#########################

:Date: |today|
:Version: 1.0.0
:Status: Proposed

.. |today| date::

Introduction
============

This document outlines the project brief for developing a Graphical User Interface (GUI) for the MDtoPDF Converter application. The current application consists of Python scripts capable of various file conversions (e.g., PDF to Markdown, Markdown to PDF). The GUI aims to provide a user-friendly desktop experience, leveraging a Python backend through an existing Electron bridge (`electron_bridge.py`).

The frontend will be built using modern web technologies, packaged in a desktop application framework. Development of the GUI will adhere to the guidelines specified in the **`810-gui-development-guidelines.mdc`** rule, which details component structure, state management, and backend communication patterns.

Project Goals
=============

The primary goals for this GUI project are:

1.  **User-Friendly Interface**: To provide an intuitive and accessible interface for users to perform file conversions without needing to use the command line.
2.  **Seamless Backend Integration**: To effectively communicate with the existing Python conversion scripts via `electron_bridge.py`.
3.  **Progress and Feedback**: To offer clear, real-time feedback to the user, including progress indicators for ongoing conversions and status messages (success, error).
4.  **Batch Processing Support**: To allow users to convert multiple files at once, with aggregated and individual progress.
5.  **Configuration Options**: To expose relevant conversion options (e.g., OCR language, engine choice) to the user through the GUI where applicable.
6.  **Cross-Platform Compatibility**: To aim for a consistent experience on major desktop operating systems, facilitated by the chosen desktop framework.

Target Audience
===============

The MDtoPDF Converter GUI is intended for:

*   Users who need to convert documents between supported formats (Markdown, PDF, HTML, DOCX) regularly.
*   Individuals who prefer a graphical interface over command-line tools.
*   Users who may not have advanced technical skills but require reliable conversion utilities.
*   Content creators, writers, students, and professionals who work with various document formats.

Core Functionality (Supported Conversions)
==========================================

The GUI will support all conversion types currently handled by `electron_bridge.py`:

*   PDF to Markdown (`pdf2md`)
*   Markdown to PDF (`md2pdf`)
*   HTML to PDF (`html2pdf`)
*   Markdown to HTML (`md2html`)
*   PDF to HTML (`pdf2html`)
*   DOCX to Markdown (`docx2md`)

Key GUI Features
================

The GUI will include the following features, largely orchestrated by the `ConversionPage.tsx` component:

1.  **File Selection**:
    *   Ability to select one or more input files using a native file dialog (invoked via `window.electronAPI`).
    *   Drag-and-drop support for adding input files.
    *   Display of selected files, potentially managed by a dedicated component like `FileInput.tsx`.

2.  **Conversion Type Selection**:
    *   A clear way for the user to choose the desired conversion type (e.g., from a dropdown menu).
    *   The list of available output formats should dynamically update based on the input file type(s) and selected conversion, managed within `ConversionPage.tsx`.

3.  **Output Configuration**:
    *   Option to select an output directory for converted files (invoked via `window.electronAPI`).
    *   Default output to the source file's directory or a pre-defined "output" subfolder, with option to change.

4.  **Conversion Options**:
    *   Dynamically display relevant options based on the selected conversion type. These options are defined in `electron_bridge.py` and rendered by `ConversionPage.tsx`.
    *   User-friendly controls for these options (e.g., dropdowns, checkboxes, text inputs using Shadcn/UI components).

5.  **Conversion Control**:
    *   "Start Conversion" button to initiate the process, triggering a call to the backend via `window.electronAPI`.
    *   Ability to cancel an ongoing batch conversion (if feasible through the Python bridge and exposed via `window.electronAPI`).

6.  **Progress and Status Display**:
    *   **Single File Conversion**:
        *   Overall progress bar (e.g., Shadcn/UI `Progress` component).
        *   Textual status updates, potentially displayed in a `ConversionLog.tsx` component.
    *   **Batch Conversion**:
        *   Overall progress bar for the entire batch.
        *   A list displaying each file, its individual status (e.g., pending, processing, success, failed), processing time, and any error messages, likely managed within `ConversionPage.tsx` and using components like `ConversionLog.tsx`.
        *   Counters for successful and failed conversions in the batch.
    *   Progress updates are received from the backend via `window.electronAPI` event listeners.

7.  **Results Display**:
    *   Notification upon completion of conversions.
    *   Option to open the output directory or individual converted files.

8.  **Error Handling and Reporting**:
    *   Clear display of errors received from the Python backend via `window.electronAPI`.
    *   Guidance for users on how to resolve common errors if possible.

9.  **Settings/Preferences (Optional - Future Consideration)**:
    *   Basic application settings (e.g., default output directory, theme).

Technology Stack
================

The GUI will be developed using the following technologies, as per your project's core guidelines. For detailed GUI development practices, refer to the **`810-gui-development-guidelines.mdc`** rule.

*   **Desktop Application Framework**:
    *   **Electron**: Allows building cross-platform desktop apps with web technologies. The `gui/src/main/main.ts` script will handle main process logic, including IPC setup and invoking the Python backend. The `gui/src/preload/preload.ts` script will securely expose specific IPC channels to the renderer process via the `window.electronAPI` object.
    *   (Note: The "Gemini (NodeGUI/NWG wrapper)" mentioned in earlier custom instructions seems to be superseded by the more concrete Electron setup described in the `810-gui-development-guidelines.mdc` rule and observed file structure. We will proceed with standard Electron architecture.)

*   **Frontend Framework**: **React**
    *   Used for building a component-based user interface.
    *   Components are developed as TypeScript React Functional Components (`React.FC`).
    *   Props are defined using interfaces (e.g., `ComponentNameProps`).
    *   Page-level components (e.g., `gui/src/renderer/pages/ConversionPage.tsx`) manage their relevant state using `useState` and `useEffect` hooks, passing data and callbacks to reusable child components (in `gui/src/renderer/components/`) via props.
    *   The main React application entry point is `gui/src/renderer/main.tsx`, rendering `gui/src/renderer/App.tsx`.

*   **Language**: **TypeScript**
    *   TypeScript is a superset of JavaScript that adds static typing. This helps catch errors early in development and makes the code easier to understand and maintain, especially for larger projects. Since you're familiar with Python's type hints, you'll find similarities.

*   **Build Tool**: **Vite**
    *   Vite is a very fast build tool for modern web projects. It will handle compiling your React and TypeScript code, providing a fast development server with Hot Module Replacement (HMR), which means changes in your code can appear in the running app almost instantly without a full reload.

*   **Styling**:
    *   **TailwindCSS**: A utility-first CSS framework. Instead of writing custom CSS rules, you use pre-defined utility classes directly in your HTML (or JSX in React). This speeds up UI development and helps maintain consistency.
    *   **Shadcn/UI**: A collection of beautifully designed UI components built with Radix UI and Tailwind CSS. These are not traditional UI components you install as a library, but rather code snippets you can copy, paste, and customize. This gives a great starting point for a professional look and feel.

Interaction with Python Backend
===============================

The GUI (Frontend - Renderer Process) will interact with your Python conversion scripts (Backend) via the Electron Main Process, which in turn uses `electron_bridge.py`.

1.  **Initiating Conversions & Actions**:
    *   The React UI (e.g., `ConversionPage.tsx`) will gather user inputs.
    *   To perform actions like opening file dialogs or starting a conversion, it will call asynchronous functions on the `window.electronAPI` object (exposed by `gui/src/preload/preload.ts`). These functions typically use `ipcRenderer.invoke()` to send a message to the Electron main process.
    *   The Electron main process (`gui/src/main/main.ts`) listens for these IPC messages and then invokes the `electron_bridge.py` script as a separate child process, passing the necessary arguments.

2.  **Receiving Progress and Data**:
    *   `electron_bridge.py` sends JSON formatted messages to `stdout` (e.g., `PROGRESS:`, `BATCH_PROGRESS:`, `RESULT:`, `ERROR:`).
    *   The Electron main process captures this `stdout`.
    *   The main process then uses `webContents.send()` to forward these messages to the renderer process via specific event channels (e.g., `conversion-progress`, `conversion-result`, `conversion-error`).
    *   React components (e.g., `ConversionPage.tsx`) subscribe to these events using `window.electronAPI.onEventName(callback)` (which uses `ipcRenderer.on()`). The callback updates the React state, causing the UI to re-render with new progress information or results, often displayed in components like `ConversionLog.tsx`.
    *   Cleanup functions for event listeners are used to prevent memory leaks when components unmount.

3.  **Handling Errors**:
    *   Errors from the Python script (e.g., file not found, conversion errors) will also be sent as JSON messages and displayed appropriately in the GUI.

This separation allows the Python backend to focus on the conversion logic, while the frontend handles user interaction and presentation.

+Implementation Ideas and Snippets
+==================================
+
+This section provides high-level ideas and potential snippets to guide the implementation of key GUI features. For more specific implementation patterns within the GUI codebase, refer to the **`810-gui-development-guidelines.mdc`** rule and existing components like `ConversionPage.tsx`.
+
+1.  **Communicating with Python (Electron Main Process - `gui/src/main/main.ts`)**:
+    *   The Electron main process will use Node.js's `child_process.spawn` to run your `electron_bridge.py` script.
+    *   It will listen to `stdout` for JSON messages (progress, results) and `stderr` for errors, then forward them to the renderer via `webContents.send()`.
+
+    .. code-block::typescript
+       :caption: Example: Spawning Python script in Electron's main.ts
+
+       import { spawn } from 'child_process';
+       import path from 'path';
+       import { BrowserWindow } from 'electron'; // Assuming mainWindow is available
+
+       export function runConversion(
+         mainWindow: BrowserWindow | null, // To send messages to renderer
+         conversionType: string,
+         inputFiles: string[],
+         outputDir: string | null,
+         options: any
+       ) {
+         // Path to electron_bridge.py, assuming main.ts is in gui/src/main
+         // and electron_bridge.py is in project_root/src/mdtopdf/
+         const scriptPath = path.join(process.cwd(), 'src', 'mdtopdf', 'electron_bridge.py');
+         const pythonExecutable = 'python'; // Or path to your venv python
+
+         let args = [
+           scriptPath,
+           conversionType,
+           '--input-files', ...inputFiles,
+         ];
+         if (outputDir) {
+           args.push('--output-dir', outputDir);
+         }
+         // Example: if (options.lang) args.push('--lang', options.lang);
+         // Add other converter_options from your electron_bridge.py
+
+         const pyProcess = spawn(pythonExecutable, args);
+
+         pyProcess.stdout.on('data', (data) => {
+           const message = data.toString();
+           // Split messages if multiple are received in one chunk
+           message.split('\n').forEach(line => {
+             if (line.trim() === '') return;
+             // A more robust parsing might be needed depending on actual output
+             // Example: send every line that seems to be JSON-like or prefixed
+             if (mainWindow) {
+               // Determine channel based on prefix (PROGRESS:, RESULT:, BATCH_PROGRESS:, ERROR:)
+               // This logic should be robust
+               if (line.startsWith("PROGRESS:") || line.startsWith("BATCH_PROGRESS:") || line.startsWith("RESULT:") || line.startsWith("ERROR:")) {
+                  mainWindow.webContents.send('conversion-event', line);
+               }
+             }
+             console.log(`Python stdout: ${line}`);
+           });
+         });
+
+         pyProcess.stderr.on('data', (data) => {
+           const errorMessage = data.toString();
+           console.error(`Python stderr: ${errorMessage}`);
+           if (mainWindow) {
+             // Send as a specific error event or part of the general 'conversion-event'
+             mainWindow.webContents.send('conversion-event', `ERROR: ${JSON.stringify({ type: 'stderr', message: errorMessage })}`);
+           }
+         });
+
+         pyProcess.on('close', (code) => {
+           console.log(`Python script exited with code ${code}`);
+           if (mainWindow) {
+            const resultMessage = code === 0
+                ? `SUCCESS: ${JSON.stringify({ type: 'script_exit', code, message: 'Conversion process completed.'})}`
+                : `ERROR: ${JSON.stringify({ type: 'script_exit', code, message: 'Conversion process failed.'})}`;
+            mainWindow.webContents.send('conversion-event', resultMessage);
+           }
+         });
+       }
+
+2.  **Triggering File Dialogs (Electron Main & Renderer - as per `810-gui-development-guidelines.mdc`)**:
+    *   The React component (renderer process, e.g., `ConversionPage.tsx`) requests a file dialog via `window.electronAPI.openFileDialog()` or `window.electronAPI.openDirectoryDialog()`.
+    *   The main process (`gui/src/main/main.ts`) handles this using `ipcMain.handle` and `dialog.showOpenDialog`.
+    *   The `gui/src/preload/preload.ts` script exposes these handlers to the renderer.
+
+    .. code-block::typescript
+       :caption: Example: IPC Handler in gui/src/main/main.ts
+
+       import { ipcMain, dialog } from 'electron';
+
+       ipcMain.handle('dialog:openFile', async () => {
+         const { canceled, filePaths } = await dialog.showOpenDialog({
+           properties: ['openFile', 'multiSelections'],
+         });
+         return canceled ? [] : filePaths;
+       });
+
+       ipcMain.handle('dialog:openDirectory', async () => {
+         const { canceled, filePaths } = await dialog.showOpenDialog({
+           properties: ['openDirectory'],
+         });
+         return canceled ? null : filePaths[0];
+       });
+
+    .. code-block::typescript
+       :caption: Example: Exposing API in gui/src/preload/preload.ts
+
+       import { contextBridge, ipcRenderer } from 'electron';
+
+       contextBridge.exposeInMainWorld('electronAPI', {
+         openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
+         openDirectoryDialog: () => ipcRenderer.invoke('dialog:openDirectory'),
+         // For receiving events from main to renderer
+         onConversionEvent: (callback) => {
+           const handler = (_event, value) => callback(value);
+           ipcRenderer.on('conversion-event', handler);
+           return () => ipcRenderer.removeListener('conversion-event', handler); // Cleanup
+         },
+         // Add a function to send conversion commands
+         runConversion: (conversionType: string, inputFiles: string[], outputDir: string | null, options: any) =>
+           ipcRenderer.invoke('run-conversion', conversionType, inputFiles, outputDir, options),
+       });
+
+    .. code-block::typescript
+       :caption: Ensure global.d.ts in renderer is updated
+
+       // gui/src/renderer/global.d.ts
+       export interface IElectronAPI {
+         openFileDialog: () => Promise<string[]>;
+         openDirectoryDialog: () => Promise<string | null>;
+         onConversionEvent: (callback: (eventData: string) => void) => () => void; // Returns a cleanup function
+         runConversion: (
+            conversionType: string,
+            inputFiles: string[],
+            outputDir: string | null,
+            options: any
+         ) => Promise<any>; // Define expected return type more accurately
+       }
+
+       declare global {
+         interface Window {
+           electronAPI: IElectronAPI;
+         }
+       }
+
+3.  **Drag and Drop Files (React Component - e.g., `FileInput.tsx`)**:
+    *   Use standard HTML5 drag-and-drop events (`onDragOver`, `onDrop`) in your React component.
+    *   Access `event.dataTransfer.files` to get the list of dropped files.
+
+    .. code-block::tsx
+       :caption: Example: React Drag and Drop Area
+
+       import React, { useState, DragEvent } from 'react';
+
+       const FileDropArea: React.FC = () => {
+         const [droppedFiles, setDroppedFiles] = useState<File[]>([]);
+
+         const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
+           event.preventDefault(); // Necessary to allow dropping
+         };
+
+         const handleDrop = (event: DragEvent<HTMLDivElement>) => {
+           event.preventDefault();
+           const files = Array.from(event.dataTransfer.files);
+           console.log('Dropped files:', files.map(f => f.path)); // f.path is available in Electron
+           setDroppedFiles(prevFiles => [...prevFiles, ...files]);
+           // You'd likely want to use file.path for Electron to pass to Python
+         };
+
+         return (
+           <div
+             onDragOver={handleDragOver}
+             onDrop={handleDrop}
+             style={{ border: '2px dashed #ccc', padding: '20px', textAlign: 'center' }}
+           >
+             <p>Drag and drop files here</p>
+             {/* Display list of dropped files */}
+           </div>
+         );
+       };
+
+4.  **Progress Display (Shadcn/UI in React - e.g., `ConversionPage.tsx`, `ConversionLog.tsx`)**:
+    *   Use the `Progress` component from Shadcn/UI within `ConversionPage.tsx` or a dedicated progress component.
+    *   Update its `value` and status messages based on parsed data from the `conversion-event` listener.
+    *   The `ConversionLog.tsx` can display detailed messages.
+
+    .. code-block::tsx
+       :caption: Example: React Progress Bar logic in ConversionPage.tsx
+
+       // ... imports ...
+       // import { Progress } from '@/components/ui/progress';
+       // import ConversionLog from '@/components/ConversionLog';
+
+       const ConversionPage: React.FC = () => {
+         const [progress, setProgress] = useState(0);
+         const [statusMessage, setStatusMessage] = useState('');
+         const [logMessages, setLogMessages] = useState<string[]>([]);
+
+         useEffect(() => {
+           const cleanup = window.electronAPI.onConversionEvent((eventData: string) => {
+             setLogMessages(prev => [...prev, eventData]); // Add raw event to log
+             try {
+                // Attempt to parse based on prefix
+                if (eventData.startsWith("PROGRESS:")) {
+                    const jsonData = JSON.parse(eventData.substring("PROGRESS:".length));
+                    setProgress(jsonData.progress);
+                    setStatusMessage(jsonData.message);
+                } else if (eventData.startsWith("BATCH_PROGRESS:")) {
+                    const jsonData = JSON.parse(eventData.substring("BATCH_PROGRESS:".length));
+                    setProgress(jsonData.overallProgress);
+                    setStatusMessage(`File ${jsonData.fileName}: ${jsonData.status}`);
+                } else if (eventData.startsWith("RESULT:")) {
+                    // Handle result
+                    setStatusMessage("Conversion successful!");
+                    setProgress(100);
+                } else if (eventData.startsWith("ERROR:")) {
+                     const errorJson = JSON.parse(eventData.substring("ERROR:".length));
+                     setStatusMessage(`Error: ${errorJson.message}`);
+                     setProgress(100); // Or reset, or show error state
+                } else if (eventData.startsWith("SUCCESS:")) { // From python script exit
+                    const jsonData = JSON.parse(eventData.substring("SUCCESS:".length));
+                    if(jsonData.type === 'script_exit' && jsonData.code === 0){
+                        setStatusMessage("Process completed.");
+                        //setProgress(100); // Might already be 100 from RESULT
+                    }
+                }
+             } catch (e) {
+                console.error("Failed to parse message from backend:", eventData, e);
+                // setStatusMessage("Received unparseable message from backend.");
+             }
+           });
+           return cleanup; // Cleanup listener on component unmount
+         }, []);
+
+         // ... other component logic ...
+
+         // Example of how to call the conversion:
+         // const handleStartConversion = async () => {
+         //   setStatusMessage('Starting conversion...');
+         //   setProgress(0);
+         //   setLogMessages([]);
+         //   try {
+         //     await window.electronAPI.runConversion(conversionType, selectedFiles, outputDir, {/* conversion options */});
+         //   } catch (error) {
+         //     setStatusMessage(`Failed to start conversion: ${error}`);
+         //     setLogMessages(prev => [...prev, `Frontend Error: ${error}`]);
+         //   }
+         // };
+
+         return (
+           <div>
+             {/* ... other UI elements ... */}
+             {/* <Progress value={progress} /> */}
+             {/* <p>{statusMessage}</p> */}
+             {/* <ConversionLog messages={logMessages} /> */}
+           </div>
+         );
+       };
+
+5.  **Dynamic Conversion Options (React - in `ConversionPage.tsx`)**:
+    *   `ConversionPage.tsx` will maintain state for the selected `conversionType`.
+    *   It will conditionally render form elements for specific options (e.g., OCR language for PDF to Markdown) based on this state, likely using Shadcn/UI input components.
+
+    .. code-block::tsx
+       :caption: Example: React Dynamic Form Section (Conceptual within ConversionPage.tsx)
+
+       // ... inside ConversionPage.tsx ...
+       // const [conversionType, setConversionType] = useState<string>('');
+       // const [ocrLang, setOcrLang] = useState('eng');
+
+       // return (
+       //   ...
+       //   {/* Select for conversionType */}
+       //
+       //   {conversionType === 'pdf2md' && (
+       //     <div>
+       //       {/* <Label htmlFor="ocrLang">OCR Language</Label> */}
+       //       {/* <Input id="ocrLang" value={ocrLang} onChange={(e) => setOcrLang(e.target.value)} /> */}
+       //       <p>PDF to Markdown specific options here</p>
+       //     </div>
+       //   )}
+       //   ...
+       // );
+
Future Considerations (Optional)
================================

*   Advanced settings panel for power users.
*   Plugin system for new conversion types (if the Python backend is designed for extensibility).
*   Theming options for the GUI.
*   Automatic update functionality for the application.

+Performance Considerations
+==========================
+
+Building a performant Electron application is crucial for a good user experience. The following considerations, largely based on Electron's official performance guidelines, should be kept in mind throughout the development lifecycle.
+
+*   **Measure and Profile Regularly**:
+    *   The most effective way to improve performance is to profile the application to identify bottlenecks. Use tools like Chrome Developer Tools (Performance and Memory tabs) to analyze runtime behavior and memory usage.
+    *   *Reference*: `Analyze runtime performance <https://developer.chrome.com/docs/devtools/performance/>`_
+
+*   **Minimize Module Impact (Main & Renderer Processes)**:
+    *   Before adding dependencies (Node.js modules or frontend libraries), evaluate their size and performance overhead (load time, memory usage).
+    *   Prefer lean modules and consider if functionality can be achieved with built-in APIs or smaller libraries.
+    *   *Reference*: `Carelessly including modules <https://www.electronjs.org/docs/latest/tutorial/performance#1-carelessly-including-modules>`_
+
+*   **Optimize Loading and Execution Time**:
+    *   Avoid running expensive operations immediately at startup or when a window loads if they are not immediately necessary.
+    *   Utilize techniques like lazy loading for React components or features that are not initially visible to the user.
+    *   *Reference*: `Loading and running code too soon <https://www.electronjs.org/docs/latest/tutorial/performance#2-loading-and-running-code-too-soon>`_
+
+*   **Keep Processes Non-Blocking**:
+    *   **Main Process**: Avoid synchronous IPC and blocking I/O operations. Use asynchronous APIs (e.g., `async`/`await`, Promises) for file system access or other potentially long tasks.
+    *   **Renderer Process (UI)**: Ensure the UI thread remains responsive. For CPU-intensive tasks within the renderer (if any), consider Web Workers. For deferrable, non-critical tasks, `requestIdleCallback` can be used.
+    *   *Reference*: `Blocking the main process <https://www.electronjs.org/docs/latest/tutorial/performance#3-blocking-the-main-process>`_ and `Blocking the renderer process <https://www.electronjs.org/docs/latest/tutorial/performance#4-blocking-the-renderer-process>`_
+
+*   **Bundle Assets Locally**:
+    *   Avoid fetching rarely changing resources (fonts, images, icons) from the internet. Bundle them directly with the application.
+    *   Vite will handle bundling for the React frontend. Ensure any assets used by the main process are also managed efficiently.
+    *   *Reference*: `Unnecessary or blocking network requests <https://www.electronjs.org/docs/latest/tutorial/performance#6-unnecessary-or-blocking-network-requests>`_
+
+*   **Efficient Code Bundling**:
+    *   Vite, as specified in the technology stack, will bundle the frontend (renderer) code. This is crucial for reducing the overhead of `require()` or `import` statements and improving load times.
+    *   If the main process JavaScript becomes complex with many files, consider bundling it as well.
+    *   *Reference*: `Bundle your code <https://www.electronjs.org/docs/latest/tutorial/performance#7-bundle-your-code>`_
+
+*   **Avoid Unnecessary Polyfills**:
+    *   Electron uses a modern version of Chromium. Ensure your build process (e.g., TypeScript or Babel configuration if customized beyond Vite defaults) targets a modern JavaScript version to avoid including polyfills for features already present in Electron.
+    *   *Reference*: `Unnecessary polyfills <https://www.electronjs.org/docs/latest/tutorial/performance#5-unnecessary-polyfills>`_
+
+*   **Optimize Application Menu**:
+    *   If a default application menu is not needed or a custom one is built, call `Menu.setApplicationMenu(null)` early in the main process (before `app.on("ready")`) to prevent Electron from setting up a default menu, which can save a small amount of startup time.
+    *   *Reference*: `Call Menu.setApplicationMenu(null) <https://www.electronjs.org/docs/latest/tutorial/performance#8-call-menusetapplicationmenunull-when-you-do-not-need-a-default-menu>`_
+
+Adhering to these practices will contribute to a faster, more responsive, and resource-efficient GUI for the MDtoPDF Converter.