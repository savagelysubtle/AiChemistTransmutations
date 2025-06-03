import React, { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import ConversionTypeSelect from '../components/ConversionTypeSelect';
import FileInput from '../components/FileInput';
import DirectoryInput from '../components/DirectoryInput';
import ConversionOptions from '../components/ConversionOptions';
import ConversionLog from '../components/ConversionLog';
import MergeOptions from '../components/MergeOptions';

// Updated PlaceholderElectronAPI
interface PlaceholderElectronAPI {
  openFileDialog: (options?: { filters?: Array<{ name: string; extensions: string[] }> }) => Promise<string[]>;
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

  // State for PDF Merge Options
  const [mergeOrderedFiles, setMergeOrderedFiles] = useState<string[]>([]);
  const [mergeOutputFileName, setMergeOutputFileName] = useState<string>('merged_document.pdf');

  // New state for TXT to PDF options
  const [txtToPdfOptions, setTxtToPdfOptions] = useState({
    fontName: 'Helvetica',
    fontSize: 10,
  });

  const electronAPI = getElectronAPI();

  // Effect to synchronize mergeOrderedFiles with selectedFiles when conversionType is merge_to_pdf
  useEffect(() => {
    if (conversionType === 'merge_to_pdf') {
      // This ensures that mergeOrderedFiles reflects selectedFiles when switching to merge mode
      // or when selectedFiles change while in merge mode.
      // A more sophisticated sync might be needed if preserving order across deselection/reselection is desired.
      setMergeOrderedFiles(selectedFiles);
      if (selectedFiles.length === 0) {
        setMergeOutputFileName('merged_document.pdf'); // Reset if no files
      }
    } else {
      // Clear merge specific states if not in merge mode to avoid confusion
      setMergeOrderedFiles([]);
      // setMergeOutputFileName('merged_document.pdf'); // Optionally reset filename
    }
  }, [selectedFiles, conversionType]);

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
      let dialogOptions: { filters?: Array<{ name: string; extensions: string[] }> } = {};
      if (conversionType === 'merge_to_pdf') {
        dialogOptions.filters = [{ name: 'PDF Documents', extensions: ['pdf'] }];
      }
      // For other conversion types, you might want to set specific filters too, e.g.:
      else if (conversionType === 'md2pdf') {
        dialogOptions.filters = [{ name: 'Markdown Files', extensions: ['md', 'markdown'] }];
      }
      else if (conversionType === 'txt2pdf') { // Added filter for txt2pdf
        dialogOptions.filters = [{ name: 'Text Files', extensions: ['txt'] }];
      }

      const files = await electronAPI.openFileDialog(dialogOptions);
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

  // Specific handler for removing a file from the merge list (called by MergeOptions component)
  const handleRemoveFileFromMerge = (filePathToRemove: string) => {
    // This updates both selectedFiles and mergeOrderedFiles to keep them in sync
    const updatedSelectedFiles = selectedFiles.filter(file => file !== filePathToRemove);
    setSelectedFiles(updatedSelectedFiles);
    // mergeOrderedFiles will be updated by the useEffect hook watching selectedFiles
    setConversionLog(prev => [...prev, `Removed ${filePathToRemove.split(/[\\/]/).pop()} from merge list.`]);
  };

  const handleClearSelection = () => {
    if (selectedFiles.length > 0) {
        setConversionLog(prev => [...prev, "Cleared all selected files."]);
    }
    setSelectedFiles([]);
    // mergeOrderedFiles will be cleared by the useEffect hook
    setMergeOutputFileName('merged_document.pdf'); // Reset merge output name as well
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
    if (!electronAPI) {
      setConversionLog(prev => [...prev, 'Error: API not available.']);
      return;
    }

    // Use mergeOrderedFiles for input if in merge_to_pdf mode, otherwise use selectedFiles
    const currentInputFiles = conversionType === 'merge_to_pdf' ? mergeOrderedFiles : selectedFiles;

    if (currentInputFiles.length === 0) {
      setConversionLog(prev => [...prev, 'Error: No input files selected.']);
      return;
    }

    // Specific handling for PDF Merging
    if (conversionType === 'merge_to_pdf') {
      if (currentInputFiles.length < 2) {
        setConversionLog(prev => [...prev, 'Error: PDF Merging requires at least two input files.']);
        return;
      }
      if (!outputDir) {
        setConversionLog(prev => [...prev, 'Error: An output directory must be selected for PDF Merging.']);
        return;
      }
      if (!mergeOutputFileName || mergeOutputFileName.trim() === '') {
        setConversionLog(prev => [...prev, 'Error: An output file name must be specified for the merged PDF.']);
        // Optionally, you could force a default name here if you prefer
        // setMergeOutputFileName('merged_output.pdf'); // and then proceed
        return;
      }
      setConversionLog(prev => [
        ...prev,
        `Starting PDF Merge for ${currentInputFiles.length} files: ${currentInputFiles.join(', ')}... Output to: ${outputDir}/${mergeOutputFileName}`,
      ]);
      try {
        const result = await electronAPI.runConversion({
          conversionType: 'merge_to_pdf',
          inputFiles: currentInputFiles, // Use the (potentially reordered) mergeOrderedFiles
          outputDir: outputDir,
          options: { outputFileName: mergeOutputFileName }, // Pass the desired output filename
        });
        setConversionLog(prev => [...prev, `Merge process ended: ${result.message}`]);
        if (result.success) {
          // Optionally clear selection on success
          // setSelectedFiles([]); // This would also clear mergeOrderedFiles via useEffect
        }
      } catch (error) {
        console.error('Error running PDF merge conversion:', error);
        const errorMessage = (error as any)?.message || JSON.stringify(error);
        setConversionLog(prev => [...prev, `Error during PDF merge: ${errorMessage}`]);
      }
      return; // End here for merge_to_pdf
    }

    // Existing MDX to MD conversion (client-side handled differently)
    setConversionLog(prev => [...prev, `Starting ${conversionType} conversion for ${currentInputFiles.length} file(s): ${currentInputFiles.join(', ')}...`]);

    if (conversionType === 'mdx2md') {
      if (!electronAPI.convertMdxToMd) {
        setConversionLog(prev => [...prev, 'ERROR: MDX to MD conversion function is not available on electronAPI.']);
        return;
      }
      if (currentInputFiles.length > 1) {
          setConversionLog(prev => [...prev, 'Note: MDX to MD conversion will be processed one file at a time for multiple selections.']);
      }
      // Loop through selected files for MDX to MD conversion
      for (const inputFile of currentInputFiles) { // Use currentInputFiles here too
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
      // Existing logic for Python-based conversions (excluding merge_to_pdf which is handled above)
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
        } else if (conversionType === 'txt2pdf') { // Added options for txt2pdf
          options.fontName = txtToPdfOptions.fontName;
          options.fontSize = txtToPdfOptions.fontSize;
        }
        // Add other conversion-specific options here as needed

        const result = await electronAPI.runConversion({
          conversionType,
          inputFiles: currentInputFiles, // Use currentInputFiles
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
          onConversionTypeChange={(newType) => {
            setConversionType(newType);
            // If switching away from merge_to_pdf, selectedFiles remains, but merge options might hide.
            // If switching TO merge_to_pdf, useEffect will handle mergeOrderedFiles.
            // Reset output filename for merge if user switches type then switches back with files already selected.
            if (newType === 'merge_to_pdf' && selectedFiles.length > 0) {
                setMergeOutputFileName('merged_document.pdf');
            } else if (newType !== 'merge_to_pdf') {
                // Optionally clear merge-specific states if desired when switching away
                // setMergeOrderedFiles([]); // Already handled by useEffect
                // setMergeOutputFileName('merged_document.pdf');
            }
          }}
        />

        <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
          <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">2. Select Files & Output</h2>
          <FileInput
            selectedFiles={selectedFiles}
            onSelectFilesClick={handleSelectFilesClick}
            onSelectedFilesChange={handleSelectedFilesChange}
            onClearSelection={handleClearSelection}
            buttonText={
              conversionType === 'merge_to_pdf'
                ? "Select PDFs to Merge (Min. 2)"
                : "Select Input File(s)"
            }
            instructions={
              conversionType === 'merge_to_pdf'
                ? "Select two or more PDF files to combine. Order and output name can be set below."
                : undefined
            }
            accept={conversionType === 'merge_to_pdf' ? ".pdf" : undefined}
            allowMultiple={true} // Always allow multiple for FileInput, merge logic will check count
          />
          <DirectoryInput
            outputDir={outputDir}
            onSelectOutputDirectory={handleSelectOutputDir}
            buttonText={
              conversionType === 'merge_to_pdf'
                ? "Select Output Directory (Required for Merge)"
                : "Select Output Directory (Optional)"
            }
          />
        </section>

        {/* Conditionally render MergeOptions only for 'merge_to_pdf' and if files are selected */}
        {conversionType === 'merge_to_pdf' && selectedFiles.length > 0 && (
          <MergeOptions
            orderedFilePaths={mergeOrderedFiles} // Pass the ordered list
            onOrderChange={setMergeOrderedFiles} // Pass the setter for order changes
            outputFileName={mergeOutputFileName} // Pass current output filename
            onOutputFileNameChange={setMergeOutputFileName} // Pass setter for filename changes
            onRemoveFile={handleRemoveFileFromMerge} // Pass the remove handler
            defaultFileName="merged_document.pdf"
          />
        )}

        <ConversionOptions
          conversionType={conversionType}
          ocrLang={ocrLang}
          onOcrLangChange={setOcrLang}
          pdfToEditableOptions={pdfToEditableOptions}
          onPdfToEditableOptionsChange={setPdfToEditableOptions}
          txtToPdfOptions={txtToPdfOptions}
          onTxtToPdfOptionsChange={setTxtToPdfOptions}
        />

        <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface">
          <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">3. Start Conversion</h2>
          <button
            onClick={handleRunConversion}
            disabled={selectedFiles.length === 0 || !electronAPI || (conversionType === 'merge_to_pdf' && (mergeOrderedFiles.length < 2 || !outputDir || !mergeOutputFileName))}
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