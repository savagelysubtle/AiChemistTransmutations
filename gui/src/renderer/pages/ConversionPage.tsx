import React, { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import ConversionTypeSelect from '../components/ConversionTypeSelect';
import FileInput from '../components/FileInput';
import DirectoryInput from '../components/DirectoryInput';
import ConversionOptions from '../components/ConversionOptions';
import ConversionLog from '../components/ConversionLog';
import MergeOptions from '../components/MergeOptions';
import Card from '../components/Card';
import Button from '../components/Button';
import TrialStatus from '../components/TrialStatus';
import LicenseDialog from '../components/LicenseDialog';
import { logger, logError, logErrorFromException, logInfo, logWarn } from '../utils/logger';
import { ErrorCode } from '../utils/errorCodes';

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

  // State for Excel/CSV options
  const [excelOptions, setExcelOptions] = useState({
    sheetName: '',
    includeCharts: false,
    preserveFormatting: false,
  });

  // State for PowerPoint options
  const [pptxOptions, setPptxOptions] = useState({
    slideRange: '',
    includeNotes: false,
    imageQuality: 90,
  });

  // State for image options
  const [imageOptions, setImageOptions] = useState({
    imageFormat: 'png',
    imageQuality: 90,
    resize: '',
    crop: '',
  });

  // State for advanced PDF options
  const [advancedPdfOptions, setAdvancedPdfOptions] = useState({
    compressionLevel: 6,
    userPassword: '',
    ownerPassword: '',
    watermarkText: '',
    watermarkImage: '',
    pageRange: '',
    rotate: 0,
    removePages: '',
  });

  // State for EPUB options
  const [epubOptions, setEpubOptions] = useState({
    epubTitle: '',
    epubAuthor: '',
    epubLanguage: 'en',
    includeImages: false,
    tocDepth: 3,
  });

  // State for OCR options
  const [ocrOptions, setOcrOptions] = useState({
    language: 'eng',
    dpi: 300,
    preprocess: 'grayscale',
    confidenceThreshold: 0,
    pageRange: 'all',
    preserveLayout: true,
  });

  // License dialog state
  const [showLicenseDialog, setShowLicenseDialog] = useState(false);

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
      const errorMsg = "Error: Electron API is not available. Ensure preload script is working.";
      logError(errorMsg, ErrorCode.FRONTEND_ELECTRON_API_UNAVAILABLE, {});
      setConversionLog(prev => [...prev, `[${ErrorCode.FRONTEND_ELECTRON_API_UNAVAILABLE}] ${errorMsg}`]);
      return;
    }

    logger.info('Electron API available, setting up conversion event listener');

    const removeListener = electronAPI.onConversionEvent((eventData) => {
      logger.debug('Conversion Event received', { type: eventData.type, data: eventData.data });

      // Extract error code if present
      const errorCode = eventData.error_code || eventData.errorCode ||
                       (eventData.data?.error_code) || (eventData.data?.errorCode);

      let logMessage = `[${eventData.type || 'EVENT'}] `;
      if (errorCode) {
        logMessage += `[${errorCode}] `;
      }

      if (eventData.message) {
        logMessage += eventData.message;
      } else if (typeof eventData.data === 'string') {
        logMessage += eventData.data;
      } else if (eventData.data) {
        logMessage += JSON.stringify(eventData.data);
      } else {
        logMessage += JSON.stringify(eventData);
      }

      // Log based on event type
      if (eventData.type === 'error' || eventData.type === 'ERROR') {
        logError(
          eventData.message || logMessage,
          errorCode || ErrorCode.BRIDGE_CONVERSION_EXECUTION_FAILED,
          { eventData }
        );
      } else if (eventData.type === 'success' || eventData.type === 'SUCCESS') {
        logger.info(eventData.message || logMessage, { eventData });
      } else {
        logger.debug(eventData.message || logMessage, { eventData });
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
      // Excel/CSV filters
      else if (['xlsx2pdf', 'xlsx2html', 'xlsx2md', 'xlsx2csv'].includes(conversionType)) {
        dialogOptions.filters = [{ name: 'Excel Files', extensions: ['xlsx', 'xls'] }];
      }
      else if (['csv2xlsx', 'csv2pdf'].includes(conversionType)) {
        dialogOptions.filters = [{ name: 'CSV Files', extensions: ['csv'] }];
      }
      else if (conversionType === 'pdf2xlsx') {
        dialogOptions.filters = [{ name: 'PDF Files', extensions: ['pdf'] }];
      }
      // PowerPoint filters
      else if (['pptx2pdf', 'pptx2html', 'pptx2md', 'pptx2images'].includes(conversionType)) {
        dialogOptions.filters = [{ name: 'PowerPoint Files', extensions: ['pptx', 'ppt'] }];
      }
      // Image filters
      else if (['image2pdf', 'image2text', 'image2image'].includes(conversionType)) {
        dialogOptions.filters = [{ name: 'Image Files', extensions: ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'] }];
      }
      else if (conversionType === 'pdf2images') {
        dialogOptions.filters = [{ name: 'PDF Files', extensions: ['pdf'] }];
      }
      // EPUB filters
      else if (['epub2pdf', 'epub2html', 'epub2md'].includes(conversionType)) {
        dialogOptions.filters = [{ name: 'EPUB Files', extensions: ['epub'] }];
      }
      else if (['md2epub', 'docx2epub', 'html2epub'].includes(conversionType)) {
        if (conversionType === 'md2epub') {
          dialogOptions.filters = [{ name: 'Markdown Files', extensions: ['md', 'markdown'] }];
        } else if (conversionType === 'docx2epub') {
          dialogOptions.filters = [{ name: 'Word Documents', extensions: ['docx', 'doc'] }];
        } else if (conversionType === 'html2epub') {
          dialogOptions.filters = [{ name: 'HTML Files', extensions: ['html', 'htm'] }];
        }
      }
      // Advanced PDF operations filters
      else if (['pdf2split', 'pdf2compress', 'pdf2encrypt', 'pdf2watermark', 'pdf2pages', 'pdf2ocr_layer'].includes(conversionType)) {
        dialogOptions.filters = [{ name: 'PDF Files', extensions: ['pdf'] }];
      }

      logger.debug('Opening file dialog', { conversionType, dialogOptions });
      const files = await electronAPI.openFileDialog(dialogOptions);
      if (files.length > 0) {
        logger.info(`File dialog returned ${files.length} file(s)`, { files });
        // Add new files, preventing duplicates
        setSelectedFiles(prevFiles => {
          const newFiles = files.filter(f => !prevFiles.includes(f));
          if (newFiles.length > 0) {
            const logMsg = `Added input files: ${newFiles.join(', ')}`;
            logger.info(logMsg, { newFiles });
            setConversionLog(prev => [...prev, logMsg]);
            return [...prevFiles, ...newFiles];
          }
          return prevFiles;
        });
      } else {
        logger.debug('File dialog canceled or no files selected');
      }
    } catch (error) {
      logErrorFromException(error, ErrorCode.FRONTEND_FILE_DIALOG_FAILED, { conversionType });
      const errorMsg = `Error opening file dialog: ${(error as Error).message}`;
      setConversionLog(prev => [...prev, `[${ErrorCode.FRONTEND_FILE_DIALOG_FAILED}] ${errorMsg}`]);
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
    if (!electronAPI) {
      logWarn('Electron API not available for directory dialog', ErrorCode.FRONTEND_ELECTRON_API_UNAVAILABLE);
      return;
    }
    try {
      logger.debug('Opening directory dialog');
      const dir = await electronAPI.openDirectoryDialog();
      if (dir) {
        logger.info('Output directory selected', { dir });
        setOutputDir(dir);
        setConversionLog(prev => [...prev, `Selected output directory: ${dir}`]);
      } else {
        logger.debug('Directory dialog canceled');
      }
    } catch (error) {
      logErrorFromException(error, ErrorCode.FRONTEND_DIRECTORY_DIALOG_FAILED);
      const errorMsg = `Error opening directory dialog: ${(error as Error).message}`;
      setConversionLog(prev => [...prev, `[${ErrorCode.FRONTEND_DIRECTORY_DIALOG_FAILED}] ${errorMsg}`]);
    }
  };

  const handleRunConversion = async () => {
    if (!electronAPI) {
      const errorMsg = 'Error: API not available.';
      logError(errorMsg, ErrorCode.FRONTEND_ELECTRON_API_UNAVAILABLE, {});
      setConversionLog(prev => [...prev, `[${ErrorCode.FRONTEND_ELECTRON_API_UNAVAILABLE}] ${errorMsg}`]);
      return;
    }

    // Use mergeOrderedFiles for input if in merge_to_pdf mode, otherwise use selectedFiles
    const currentInputFiles = conversionType === 'merge_to_pdf' ? mergeOrderedFiles : selectedFiles;

    logger.info('Starting conversion', { conversionType, fileCount: currentInputFiles.length });

    if (currentInputFiles.length === 0) {
      const errorMsg = 'Error: No input files selected.';
      logError(errorMsg, ErrorCode.FRONTEND_NO_FILES_SELECTED, { conversionType });
      setConversionLog(prev => [...prev, `[${ErrorCode.FRONTEND_NO_FILES_SELECTED}] ${errorMsg}`]);
      return;
    }

    // Specific handling for PDF Merging
    if (conversionType === 'merge_to_pdf') {
      if (currentInputFiles.length < 2) {
        const errorMsg = 'Error: PDF Merging requires at least two input files.';
        logError(errorMsg, ErrorCode.SERVICE_MERGE_INVALID_INPUT, { fileCount: currentInputFiles.length });
        setConversionLog(prev => [...prev, `[${ErrorCode.SERVICE_MERGE_INVALID_INPUT}] ${errorMsg}`]);
        return;
      }
      if (!outputDir) {
        const errorMsg = 'Error: An output directory must be selected for PDF Merging.';
        logError(errorMsg, ErrorCode.BRIDGE_OUTPUT_DIRECTORY_INVALID, {});
        setConversionLog(prev => [...prev, `[${ErrorCode.BRIDGE_OUTPUT_DIRECTORY_INVALID}] ${errorMsg}`]);
        return;
      }
      if (!mergeOutputFileName || mergeOutputFileName.trim() === '') {
        const errorMsg = 'Error: An output file name must be specified for the merged PDF.';
        logError(errorMsg, ErrorCode.BRIDGE_OUTPUT_DIRECTORY_INVALID, {});
        setConversionLog(prev => [...prev, `[${ErrorCode.BRIDGE_OUTPUT_DIRECTORY_INVALID}] ${errorMsg}`]);
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
        logErrorFromException(error, ErrorCode.SERVICE_MERGE_PDF_WRITE_FAILED, {
          fileCount: currentInputFiles.length,
          outputDir,
          outputFileName: mergeOutputFileName
        });
        const errorMessage = (error as any)?.message || JSON.stringify(error);
        setConversionLog(prev => [...prev, `[${ErrorCode.SERVICE_MERGE_PDF_WRITE_FAILED}] Error during PDF merge: ${errorMessage}`]);
      }
      return; // End here for merge_to_pdf
    }

    // Existing MDX to MD conversion (client-side handled differently)
    setConversionLog(prev => [...prev, `Starting ${conversionType} conversion for ${currentInputFiles.length} file(s): ${currentInputFiles.join(', ')}...`]);

    if (conversionType === 'mdx2md') {
      if (!electronAPI.convertMdxToMd) {
        const errorMsg = 'ERROR: MDX to MD conversion function is not available on electronAPI.';
        logError(errorMsg, ErrorCode.FRONTEND_INVALID_CONVERSION_TYPE, { conversionType });
        setConversionLog(prev => [...prev, `[${ErrorCode.FRONTEND_INVALID_CONVERSION_TYPE}] ${errorMsg}`]);
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
        } else if (conversionType === 'docx2pdf') {
          // Maximum quality settings for DOCX to PDF conversion
          // These options are passed to the LibreOffice converter (v1.1)
          options.imageQuality = 95; // Maximum JPEG quality (0-100)
          options.useLosslessCompression = true; // No image quality loss
          options.reduceImageResolution = false; // Keep original resolution
          options.exportBookmarks = true; // Preserve document structure
          options.exportNotes = false; // Don't export comments
          options.timeout = 120; // Allow up to 2 minutes for conversion
          // For archival documents, users could enable PDF/A compliance:
          // options.pdfa = true;
        } else if (conversionType === 'pptx2pdf') {
          // Maximum quality settings for PPTX to PDF conversion
          // These options are passed to the LibreOffice converter
          options.imageQuality = 95; // Maximum JPEG quality (0-100)
          options.useLosslessCompression = true; // No image quality loss
          options.reduceImageResolution = false; // Keep original resolution
          options.exportBookmarks = true; // Preserve slide structure
          options.exportNotes = false; // Don't export speaker notes
          options.timeout = 120; // Allow up to 2 minutes for conversion
        } else if (conversionType === 'xlsx2pdf') {
          // Maximum quality settings for XLSX to PDF conversion
          // These options are passed to the LibreOffice converter
          options.imageQuality = 95; // Maximum JPEG quality (0-100)
          options.useLosslessCompression = true; // No image quality loss
          options.reduceImageResolution = false; // Keep original resolution
          options.exportBookmarks = true; // Preserve sheet structure
          options.exportNotes = false; // Don't export cell comments
          options.timeout = 120; // Allow up to 2 minutes for conversion
        } else if (conversionType === 'epub2pdf') {
          // Maximum quality settings for EPUB to PDF conversion
          // These options are passed to the LibreOffice converter
          options.imageQuality = 95; // Maximum JPEG quality (0-100)
          options.useLosslessCompression = true; // No image quality loss
          options.reduceImageResolution = false; // Keep original resolution
          options.exportBookmarks = true; // Preserve chapter structure
          options.exportNotes = false; // Don't export annotations
          options.timeout = 120; // Allow up to 2 minutes for conversion
        }
        // Excel/CSV options
        else if (['xlsx2pdf', 'xlsx2html', 'xlsx2md', 'csv2xlsx', 'csv2pdf', 'pdf2xlsx', 'xlsx2csv'].includes(conversionType)) {
          if (excelOptions.sheetName) options.sheetName = excelOptions.sheetName;
          options.includeCharts = excelOptions.includeCharts;
          options.preserveFormatting = excelOptions.preserveFormatting;
        }
        // PowerPoint options
        else if (['pptx2pdf', 'pptx2html', 'pptx2md', 'pptx2images'].includes(conversionType)) {
          if (pptxOptions.slideRange) options.slideRange = pptxOptions.slideRange;
          options.includeNotes = pptxOptions.includeNotes;
          options.imageQuality = pptxOptions.imageQuality;
        }
        // Image options
        else if (['image2pdf', 'image2text', 'image2image', 'pdf2images'].includes(conversionType)) {
          if (imageOptions.imageFormat) options.imageFormat = imageOptions.imageFormat;
          options.imageQuality = imageOptions.imageQuality;
          if (imageOptions.resize) options.resize = imageOptions.resize;
          if (imageOptions.crop) options.crop = imageOptions.crop;
        }
        // Advanced PDF options
        else if (['pdf2split', 'pdf2compress', 'pdf2encrypt', 'pdf2watermark', 'pdf2pages', 'pdf2ocr_layer'].includes(conversionType)) {
          options.compressionLevel = advancedPdfOptions.compressionLevel;
          if (advancedPdfOptions.userPassword) options.userPassword = advancedPdfOptions.userPassword;
          if (advancedPdfOptions.ownerPassword) options.ownerPassword = advancedPdfOptions.ownerPassword;
          if (advancedPdfOptions.watermarkText) options.watermarkText = advancedPdfOptions.watermarkText;
          if (advancedPdfOptions.watermarkImage) options.watermarkImage = advancedPdfOptions.watermarkImage;
          if (advancedPdfOptions.pageRange) options.pageRange = advancedPdfOptions.pageRange;
          if (advancedPdfOptions.rotate) options.rotate = advancedPdfOptions.rotate;
          if (advancedPdfOptions.removePages) options.removePages = advancedPdfOptions.removePages;
        }
        // EPUB options
        else if (['epub2pdf', 'epub2html', 'epub2md', 'md2epub', 'docx2epub', 'html2epub'].includes(conversionType)) {
          if (epubOptions.epubTitle) options.epubTitle = epubOptions.epubTitle;
          if (epubOptions.epubAuthor) options.epubAuthor = epubOptions.epubAuthor;
          if (epubOptions.epubLanguage) options.epubLanguage = epubOptions.epubLanguage;
          options.includeImages = epubOptions.includeImages;
          options.tocDepth = epubOptions.tocDepth;
        }
        else if (conversionType === 'pdf2ocr_layer') {
          options.language = ocrOptions.language;
          options.dpi = ocrOptions.dpi;
          options.preprocess = ocrOptions.preprocess;
          options.confidenceThreshold = ocrOptions.confidenceThreshold;
          options.pageRange = ocrOptions.pageRange;
          options.preserveLayout = ocrOptions.preserveLayout;
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
        logErrorFromException(error, ErrorCode.BRIDGE_CONVERSION_EXECUTION_FAILED, {
          conversionType,
          fileCount: currentInputFiles.length,
          outputDir: outputDir || undefined
        });
        const errorMessage = (error as any)?.message || JSON.stringify(error);
        setConversionLog(prev => [...prev, `[${ErrorCode.BRIDGE_CONVERSION_EXECUTION_FAILED}] Error during Python-based conversion: ${errorMessage}`]);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-light-background via-light-surface to-light-background dark:from-dark-background dark:via-dark-surface dark:to-dark-background">
      <div className="container mx-auto px-6 py-8 max-w-6xl">
        <Header />

        {/* Trial Status Bar */}
        <div className="flex items-center justify-between mt-6 p-4 bg-light-surface dark:bg-dark-surface rounded-lg border border-light-border dark:border-dark-border">
          <TrialStatus />
          <button
            onClick={() => setShowLicenseDialog(true)}
            className="px-4 py-2 bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd text-white font-medium rounded-lg hover:opacity-90 transition-opacity"
          >
            Activate License
          </button>
        </div>

        {/* License Dialog */}
        <LicenseDialog
          isOpen={showLicenseDialog}
          onClose={() => setShowLicenseDialog(false)}
          onActivated={() => {
            setConversionLog(prev => [...prev, '✅ License activated successfully! All features unlocked.']);
          }}
        />

        <main className="space-y-8 mt-8">
          {/* Progress Stepper */}
          <div className="flex items-center justify-center mb-8">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd rounded-full flex items-center justify-center text-white font-bold shadow-lg">
                  1
                </div>
                <div className="w-16 h-1 bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd mx-2 rounded-full"></div>
              </div>
              <div className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold shadow-lg transition-all duration-300 ${
                  selectedFiles.length > 0
                    ? 'bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd text-white'
                    : 'bg-light-surfaceElevated dark:bg-dark-surfaceElevated text-light-textMuted dark:text-dark-textMuted border-2 border-light-border dark:border-dark-border'
                }`}>
                  2
                </div>
                <div className={`w-16 h-1 mx-2 rounded-full transition-all duration-300 ${
                  selectedFiles.length > 0
                    ? 'bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd'
                    : 'bg-light-border dark:bg-dark-border'
                }`}></div>
              </div>
              <div className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold shadow-lg transition-all duration-300 ${
                  selectedFiles.length > 0 && conversionType !== 'merge_to_pdf' ||
                  (conversionType === 'merge_to_pdf' && selectedFiles.length >= 2 && outputDir)
                    ? 'bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd text-white'
                    : 'bg-light-surfaceElevated dark:bg-dark-surfaceElevated text-light-textMuted dark:text-dark-textMuted border-2 border-light-border dark:border-dark-border'
                }`}>
                  3
                </div>
              </div>
            </div>
          </div>

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

        <Card variant="elevated" className="animate-fade-in">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd rounded-lg flex items-center justify-center text-white font-bold">
              2
            </div>
            <h2 className="text-2xl font-semibold text-light-textPrimary dark:text-dark-textPrimary">Select Files & Output</h2>
          </div>
          <div className="space-y-4">
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
          </div>
        </Card>

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
          excelOptions={excelOptions}
          onExcelOptionsChange={setExcelOptions}
          pptxOptions={pptxOptions}
          onPptxOptionsChange={setPptxOptions}
          imageOptions={imageOptions}
          onImageOptionsChange={setImageOptions}
          advancedPdfOptions={advancedPdfOptions}
          onAdvancedPdfOptionsChange={setAdvancedPdfOptions}
          epubOptions={epubOptions}
          onEpubOptionsChange={setEpubOptions}
          ocrOptions={ocrOptions}
          onOcrOptionsChange={setOcrOptions}
        />

        <Card variant="elevated" className="animate-fade-in">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd rounded-lg flex items-center justify-center text-white font-bold">
              3
            </div>
            <h2 className="text-2xl font-semibold text-light-textPrimary dark:text-dark-textPrimary">Start Conversion</h2>
          </div>
          <Button
            onClick={handleRunConversion}
            variant="primary"
            size="lg"
            className="w-full"
            disabled={selectedFiles.length === 0 || !electronAPI || (conversionType === 'merge_to_pdf' && (mergeOrderedFiles.length < 2 || !outputDir || !mergeOutputFileName))}
          >
            Run Conversion
          </Button>
        </Card>

          <ConversionLog logs={conversionLog} onClearLog={handleClearLog} />
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default ConversionPage;