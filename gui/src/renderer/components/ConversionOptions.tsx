import React from 'react';

/**
 * Props for the ConversionOptions component.
 */
interface ConversionOptionsProps {
  /** The currently selected conversion type, to determine which options to display. */
  conversionType: string;
  /** The currently selected OCR language. */
  ocrLang?: string;
  /** Callback function when the OCR language changes. */
  onOcrLangChange?: (newLang: string) => void;

  /** Options for PDF to Editable PDF conversion. */
  pdfToEditableOptions?: {
    forceOcr: boolean;
    redoOcr: boolean;
    clean: boolean;
    deskew: boolean;
    outputType: string;
    pdfRenderer: string;
  };
  /** Callback function when PDF to Editable PDF options change. */
  onPdfToEditableOptionsChange?: React.Dispatch<React.SetStateAction<{
    forceOcr: boolean;
    redoOcr: boolean;
    clean: boolean;
    deskew: boolean;
    outputType: string;
    pdfRenderer: string;
  }>>;
}

// Component for displaying dynamic conversion options.
// It renders specific options for 'pdf2editable', nothing for 'pdf2md',
// and a placeholder for other types.
const ConversionOptions: React.FC<ConversionOptionsProps> = ({
  conversionType,
  ocrLang,
  onOcrLangChange,
  pdfToEditableOptions,
  onPdfToEditableOptionsChange,
}) => {
  if (conversionType === 'pdf2md') {
    // No specific options for pdf2md currently shown in UI, can add if needed
    return null;
  }

  if (conversionType === 'pdf2editable') {
    const handleOptionChange = <K extends keyof NonNullable<ConversionOptionsProps['pdfToEditableOptions']>>(
      optionKey: K,
      value: NonNullable<ConversionOptionsProps['pdfToEditableOptions']>[K]
    ) => {
      if (onPdfToEditableOptionsChange && pdfToEditableOptions) {
        onPdfToEditableOptionsChange({
          ...pdfToEditableOptions,
          [optionKey]: value,
        });
      }
    };

    return (
      <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
        <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">PDF to Editable PDF Options</h2>
        <div className="space-y-2">
          <label htmlFor="ocrLang" className="block text-sm font-medium text-dark-textSecondary">
            OCR Language
          </label>
          <input
            type="text"
            id="ocrLang"
            name="ocrLang"
            value={ocrLang || 'eng'} // Default to 'eng' if undefined
            onChange={(e) => onOcrLangChange && onOcrLangChange(e.target.value)}
            placeholder="e.g., eng, fra, deu"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        {/* Force OCR Checkbox */}
        <div className="flex items-center">
          <input
            id="forceOcr"
            name="forceOcr"
            type="checkbox"
            checked={pdfToEditableOptions?.forceOcr || false}
            onChange={(e) => handleOptionChange('forceOcr', e.target.checked)}
            className="h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background"
          />
          <label htmlFor="forceOcr" className="ml-2 block text-sm text-dark-textSecondary">
            Force OCR (Rasterize all pages and re-OCR)
          </label>
        </div>

        {/* Redo OCR Checkbox (disable if Force OCR is on) */}
        <div className="flex items-center">
          <input
            id="redoOcr"
            name="redoOcr"
            type="checkbox"
            checked={!pdfToEditableOptions?.forceOcr && (pdfToEditableOptions?.redoOcr || false)}
            disabled={pdfToEditableOptions?.forceOcr}
            onChange={(e) => handleOptionChange('redoOcr', e.target.checked)}
            className="h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background disabled:opacity-50"
          />
          <label htmlFor="redoOcr" className={`ml-2 block text-sm text-dark-textSecondary ${pdfToEditableOptions?.forceOcr ? 'opacity-50' : ''}`}>
            Redo OCR (Attempt to preserve visible text, re-OCR images/scans. Disabled if Force OCR is on.)
          </label>
        </div>

        {/* Clean Image Checkbox */}
        <div className="flex items-center">
          <input
            id="cleanImage"
            name="cleanImage"
            type="checkbox"
            checked={pdfToEditableOptions?.clean || false}
            onChange={(e) => handleOptionChange('clean', e.target.checked)}
            className="h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background"
          />
          <label htmlFor="cleanImage" className="ml-2 block text-sm text-dark-textSecondary">
            Clean Image (via unpaper, before OCR)
          </label>
        </div>

        {/* Deskew Image Checkbox */}
        <div className="flex items-center">
          <input
            id="deskewImage"
            name="deskewImage"
            type="checkbox"
            checked={pdfToEditableOptions?.deskew || false}
            onChange={(e) => handleOptionChange('deskew', e.target.checked)}
            className="h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background"
          />
          <label htmlFor="deskewImage" className="ml-2 block text-sm text-dark-textSecondary">
            Deskew Image (Straighten pages before OCR)
          </label>
        </div>

        {/* Output Type Dropdown */}
        <div className="space-y-1">
          <label htmlFor="outputType" className="block text-sm font-medium text-dark-textSecondary">
            Output PDF Type
          </label>
          <select
            id="outputType"
            name="outputType"
            value={pdfToEditableOptions?.outputType || 'pdf'}
            onChange={(e) => handleOptionChange('outputType', e.target.value)}
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none appearance-none"
          >
            <option value="pdf" className="bg-dark-surface text-dark-textPrimary">Standard PDF (less strict)</option>
            <option value="pdfa" className="bg-dark-surface text-dark-textPrimary">PDF/A (archival, stricter)</option>
          </select>
        </div>

        {/* PDF Renderer Dropdown */}
        <div className="space-y-1">
          <label htmlFor="pdfRenderer" className="block text-sm font-medium text-dark-textSecondary">
            PDF Text Renderer
          </label>
          <select
            id="pdfRenderer"
            name="pdfRenderer"
            value={pdfToEditableOptions?.pdfRenderer || 'auto'}
            onChange={(e) => handleOptionChange('pdfRenderer', e.target.value)}
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none appearance-none"
          >
            <option value="auto" className="bg-dark-surface text-dark-textPrimary">Auto (OCRmyPDF default)</option>
            <option value="hocr" className="bg-dark-surface text-dark-textPrimary">hOCR (Recommended)</option>
            <option value="sandwich" className="bg-dark-surface text-dark-textPrimary">Sandwich (Legacy)</option>
          </select>
        </div>

      </section>
    );
  }

  // Placeholder for other conversion types or a general message
  return (
    <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
      <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">Conversion Options</h2>
      <p className="text-sm text-dark-textSecondary">No specific options for this conversion type yet.</p>
    </section>
  );
};

export default ConversionOptions;