import React, { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import ConversionTypeSelect from '../components/ConversionTypeSelect';
import FileInput from '../components/FileInput';
import DirectoryInput from '../components/DirectoryInput';
import ConversionOptions from '../components/ConversionOptions';
import ConversionLog from '../components/ConversionLog';

// Updated PlaceholderElectronAPI
interface PlaceholderElectronAPI {
  openFileDialog: () => Promise<string[]>;
  openDirectoryDialog: () => Promise<string | null>;
  runConversion: (args: {
    conversionType: string;
    inputFiles: string[];
    outputDir?: string;
    options?: Record<string, any>;
  }) => Promise<{ success: boolean; message: string; data?: any }>;
  onConversionEvent: (callback: (eventData: any) => void) => () => void;
  // Updated to match preload.ts definition
  convertMdxToMd: (args: {
    inputFile: string;
    outputFile?: string
  }) => Promise<{ success: boolean; outputPath?: string; error?: string }>;
  notifyLogCleared?: () => void;
}

const getElectronAPI = (): PlaceholderElectronAPI | undefined => {
  return (window as any).electronAPI;
};

/**
 * Main page for handling file conversions.
 * This page integrates all conversion-related components and logic.
 */
const ConversionPage: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [outputDir, setOutputDir] = useState<string | null>(null);
  const [conversionLog, setConversionLog] = useState<string[]>([]);
  const [conversionType, setConversionType] = useState<string>('pdf2md'); // Default conversion type
  const [ocrLang, setOcrLang] = useState<string>('eng'); // Added state for OCR language
  // TODO: Add state for dynamic conversion options
  // const [currentOptions, setCurrentOptions] = useState<Record<string, any>>({});

  // New state for PDF to Editable PDF options
  const [pdfToEditableOptions, setPdfToEditableOptions] = useState({
    forceOcr: false,
    redoOcr: false, // Default to false, let user decide
    clean: false,
    deskew: false,
    outputType: 'pdf', // Default to 'pdf' as it seemed to help with Adobe editability
    pdfRenderer: 'auto',
  });

  const electronAPI = getElectronAPI();

  const handleClearLog = () => {
    setConversionLog([]);
    if (electronAPI && electronAPI.notifyLogCleared) { // Check if the new method exists
      electronAPI.notifyLogCleared();
    }
  };

  useEffect(() => {
    if (!electronAPI) {
      setConversionLog(prev => [...prev, "Error: Electron API is not available. Ensure preload script is working."]);
      return;
    }

    const removeListener = electronAPI.onConversionEvent((eventData) => {
      console.log('Conversion Event:', eventData);
      let logMessage = `[${eventData.type || 'EVENT'}] `;
      if (eventData.message) {
        logMessage += eventData.message;
      } else if (typeof eventData.data === 'string') {
        logMessage += eventData.data;
      } else if (eventData.data) {
        logMessage += JSON.stringify(eventData.data);
      } else {
        logMessage += JSON.stringify(eventData);
      }
      setConversionLog(prevLog => [
        ...prevLog,
        logMessage
      ]);
    });

    return () => {
      removeListener();
    };
  }, [electronAPI]);

  const handleSelectFilesClick = async () => {
    if (!electronAPI) return;
    try {
      const files = await electronAPI.openFileDialog();
      if (files.length > 0) {
        // Add new files, preventing duplicates
        setSelectedFiles(prevFiles => {
          const newFiles = files.filter(f => !prevFiles.includes(f));
          if (newFiles.length > 0) {
            setConversionLog(prev => [...prev, `Added input files: ${newFiles.join(', ')}`]);
            return [...prevFiles, ...newFiles];
          }
          return prevFiles;
        });
      }
    } catch (error) {
      console.error('Error opening file dialog:', error);
      setConversionLog(prev => [...prev, `Error opening file dialog: ${(error as Error).message}`]);
    }
  };

  const handleSelectedFilesChange = (updatedFiles: string[]) => {
    const deselectedCount = selectedFiles.length - updatedFiles.length;
    if (deselectedCount > 0) {
        setConversionLog(prev => [...prev, `Deselected ${deselectedCount} file(s).`]);
    }
    setSelectedFiles(updatedFiles);
  };

  const handleClearSelection = () => {
    if (selectedFiles.length > 0) {
        setConversionLog(prev => [...prev, "Cleared all selected files."]);
    }
    setSelectedFiles([]);
  };

  const handleSelectOutputDir = async () => {
    if (!electronAPI) return;
    try {
      const dir = await electronAPI.openDirectoryDialog();
      if (dir) {
        setOutputDir(dir);
        setConversionLog(prev => [...prev, `Selected output directory: ${dir}`]);
      }
    } catch (error) {
      console.error('Error opening directory dialog:', error);
      setConversionLog(prev => [...prev, `Error opening directory dialog: ${(error as Error).message}`]);
    }
  };

  const handleRunConversion = async () => {
    if (!electronAPI || selectedFiles.length === 0) {
      setConversionLog(prev => [...prev, 'Error: No input files selected or API not available.']);
      return;
    }

    setConversionLog(prev => [...prev, `Starting ${conversionType} conversion for ${selectedFiles.length} file(s): ${selectedFiles.join(', ')}...`]);

    if (conversionType === 'mdx2md') {
      if (!electronAPI.convertMdxToMd) {
        setConversionLog(prev => [...prev, 'ERROR: MDX to MD conversion function is not available on electronAPI.']);
        return;
      }
      if (selectedFiles.length > 1) {
          setConversionLog(prev => [...prev, 'Note: MDX to MD conversion will be processed one file at a time for multiple selections.']);
      }
      // Loop through selected files for MDX to MD conversion
      for (const inputFile of selectedFiles) {
        try {
          setConversionLog(prev => [...prev, `Converting ${inputFile} (MDX to MD)...`]);
          let targetOutputFile;
          if (outputDir) {
            const fileName = inputFile.split(/[\\/]/).pop()?.replace(/\.mdx$/i, '.md') || 'output.md';
            targetOutputFile = `${outputDir}/${fileName}`.replace(/\\/g, '/');
          }

          const result = await electronAPI.convertMdxToMd({
            inputFile,
            outputFile: targetOutputFile
          });

          if (result.success && result.outputPath) {
            setConversionLog(prev => [...prev, `SUCCESS: Converted ${inputFile} to ${result.outputPath}`]);
          } else {
            setConversionLog(prev => [...prev, `ERROR converting ${inputFile}: ${result.error || 'Unknown error'}`]);
          }
        } catch (error) {
          const errorMessage = (error as Error)?.message || JSON.stringify(error);
          setConversionLog(prev => [...prev, `ERROR processing ${inputFile} (MDX to MD): ${errorMessage}`]);
        }
      }
    } else {
      // Existing logic for Python-based conversions
      if (!electronAPI.runConversion) {
        setConversionLog(prev => [...prev, 'ERROR: Standard runConversion function is not available on electronAPI.']);
        return;
      }
      try {
        // Construct options based on conversion type
        let options: Record<string, any> = {};
        if (conversionType === 'pdf2md') { // Keep existing specific options for pdf2md if any
          options.lang = ocrLang;
          options.dpi = 300; // Example, manage this properly if DPI is configurable
        } else if (conversionType === 'pdf2editable') {
          options.lang = ocrLang; // Common OCR language option
          // Pass the new detailed options for pdf2editable
          // Note: main.ts will convert these camelCase keys to kebab-case for CLI args
          options.forceOcr = pdfToEditableOptions.forceOcr;
          options.redoOcr = pdfToEditableOptions.redoOcr;
          options.clean = pdfToEditableOptions.clean;
          options.deskew = pdfToEditableOptions.deskew;
          options.outputType = pdfToEditableOptions.outputType;
          options.pdfRenderer = pdfToEditableOptions.pdfRenderer;
        }
        // Add other conversion-specific options here as needed

        const result = await electronAPI.runConversion({
          conversionType,
          inputFiles: selectedFiles,
          outputDir: outputDir || undefined,
          options, // Pass the dynamically constructed options
        });
        setConversionLog(prev => [...prev, `Conversion process ended for Python script: ${result.message}`]);
        if (result.success) {
          // setSelectedFiles([]); // Optionally clear files on success
        }
      } catch (error) {
        console.error('Error running Python-based conversion:', error);
        const errorMessage = (error as any)?.message || JSON.stringify(error);
        setConversionLog(prev => [...prev, `Error during Python-based conversion: ${errorMessage}`]);
      }
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-4 flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow space-y-6">
        <ConversionTypeSelect
          conversionType={conversionType}
          onConversionTypeChange={setConversionType}
        />

        <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
          <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">2. Select Files & Output</h2>
          <FileInput
            selectedFiles={selectedFiles}
            onSelectFilesClick={handleSelectFilesClick}
            onSelectedFilesChange={handleSelectedFilesChange}
            onClearSelection={handleClearSelection}
          />
          <DirectoryInput outputDir={outputDir} onSelectOutputDirectory={handleSelectOutputDir} />
        </section>

        <ConversionOptions
          conversionType={conversionType}
          ocrLang={ocrLang}
          onOcrLangChange={setOcrLang}
          // Pass pdfToEditableOptions and its setter
          pdfToEditableOptions={pdfToEditableOptions}
          onPdfToEditableOptionsChange={setPdfToEditableOptions}
        />

        <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface">
          <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">3. Start Conversion</h2>
          <button
            onClick={handleRunConversion}
            disabled={selectedFiles.length === 0 || !electronAPI}
            className="w-full bg-dark-primary hover:bg-dark-hoverPrimary text-white font-bold py-3 px-4 rounded-lg shadow-lg transition duration-150 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-dark-primary focus:ring-opacity-50"
          >
            Run Conversion
          </button>
        </section>

        <ConversionLog logs={conversionLog} onClearLog={handleClearLog} />
      </main>
      <Footer />
    </div>
  );
};

export default ConversionPage;