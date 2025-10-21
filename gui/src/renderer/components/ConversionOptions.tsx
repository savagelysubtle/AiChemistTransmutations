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

  /** Options for TXT to PDF conversion. */
  txtToPdfOptions?: {
    fontName: string;
    fontSize: number;
  };
  /** Callback function when TXT to PDF options change. */
  onTxtToPdfOptionsChange?: React.Dispatch<React.SetStateAction<{
    fontName: string;
    fontSize: number;
  }>>;

  /** Options for Excel/CSV conversions. */
  excelOptions?: {
    sheetName?: string;
    includeCharts: boolean;
    preserveFormatting: boolean;
  };
  /** Callback function when Excel options change. */

  /** Options for OCR layer conversion. */
  ocrOptions?: {
    language: string;
    dpi: number;
    preprocess: string;
    confidenceThreshold: number;
    pageRange: string;
    preserveLayout: boolean;
  };
  /** Callback function when OCR options change. */
  onOcrOptionsChange?: React.Dispatch<React.SetStateAction<{
    language: string;
    dpi: number;
    preprocess: string;
    confidenceThreshold: number;
    pageRange: string;
    preserveLayout: boolean;
  }>>;
  onExcelOptionsChange?: React.Dispatch<React.SetStateAction<{
    sheetName?: string;
    includeCharts: boolean;
    preserveFormatting: boolean;
  }>>;

  /** Options for PowerPoint conversions. */
  pptxOptions?: {
    slideRange?: string;
    includeNotes: boolean;
    imageQuality: number;
  };
  /** Callback function when PowerPoint options change. */
  onPptxOptionsChange?: React.Dispatch<React.SetStateAction<{
    slideRange?: string;
    includeNotes: boolean;
    imageQuality: number;
  }>>;

  /** Options for image conversions. */
  imageOptions?: {
    imageFormat?: string;
    imageQuality: number;
    resize?: string;
    crop?: string;
  };
  /** Callback function when image options change. */
  onImageOptionsChange?: React.Dispatch<React.SetStateAction<{
    imageFormat?: string;
    imageQuality: number;
    resize?: string;
    crop?: string;
  }>>;

  /** Options for advanced PDF operations. */
  advancedPdfOptions?: {
    compressionLevel: number;
    userPassword?: string;
    ownerPassword?: string;
    watermarkText?: string;
    watermarkImage?: string;
    pageRange?: string;
    rotate?: number;
    removePages?: string;
  };
  /** Callback function when advanced PDF options change. */
  onAdvancedPdfOptionsChange?: React.Dispatch<React.SetStateAction<{
    compressionLevel: number;
    userPassword?: string;
    ownerPassword?: string;
    watermarkText?: string;
    watermarkImage?: string;
    pageRange?: string;
    rotate?: number;
    removePages?: string;
  }>>;

  /** Options for EPUB conversions. */
  epubOptions?: {
    epubTitle?: string;
    epubAuthor?: string;
    epubLanguage?: string;
    includeImages: boolean;
    tocDepth: number;
  };
  /** Callback function when EPUB options change. */
  onEpubOptionsChange?: React.Dispatch<React.SetStateAction<{
    epubTitle?: string;
    epubAuthor?: string;
    epubLanguage?: string;
    includeImages: boolean;
    tocDepth: number;
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
  txtToPdfOptions,
  onTxtToPdfOptionsChange,
  excelOptions,
  onExcelOptionsChange,
  pptxOptions,
  onPptxOptionsChange,
  imageOptions,
  onImageOptionsChange,
  advancedPdfOptions,
  onAdvancedPdfOptionsChange,
  epubOptions,
  onEpubOptionsChange,
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

  if (conversionType === 'txt2pdf') {
    const handleOptionChange = <K extends keyof NonNullable<ConversionOptionsProps['txtToPdfOptions']>>(
      optionKey: K,
      value: NonNullable<ConversionOptionsProps['txtToPdfOptions']>[K]
    ) => {
      if (onTxtToPdfOptionsChange && txtToPdfOptions) {
        onTxtToPdfOptionsChange({
          ...txtToPdfOptions,
          [optionKey]: value,
        });
      }
    };

    return (
      <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
        <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">TXT to PDF Options</h2>
        <div className="space-y-2">
          <label htmlFor="txtFontName" className="block text-sm font-medium text-dark-textSecondary">
            Font Name
          </label>
          <input
            type="text"
            id="txtFontName"
            name="txtFontName"
            value={txtToPdfOptions?.fontName || 'Helvetica'}
            onChange={(e) => handleOptionChange('fontName', e.target.value)}
            placeholder="e.g., Helvetica, Times-Roman"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="txtFontSize" className="block text-sm font-medium text-dark-textSecondary">
            Font Size
          </label>
          <input
            type="number"
            id="txtFontSize"
            name="txtFontSize"
            value={txtToPdfOptions?.fontSize || 10}
            onChange={(e) => handleOptionChange('fontSize', parseInt(e.target.value, 10) || 10)}
            min="1"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>
      </section>
    );
  }

  // Excel/CSV conversion options
  if (['xlsx2pdf', 'xlsx2html', 'xlsx2md', 'csv2xlsx', 'csv2pdf', 'pdf2xlsx', 'xlsx2csv'].includes(conversionType)) {
    const handleExcelOptionChange = <K extends keyof NonNullable<ConversionOptionsProps['excelOptions']>>(
      optionKey: K,
      value: NonNullable<ConversionOptionsProps['excelOptions']>[K]
    ) => {
      if (onExcelOptionsChange && excelOptions) {
        onExcelOptionsChange({
          ...excelOptions,
          [optionKey]: value,
        });
      }
    };

    return (
      <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
        <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">Excel/CSV Options</h2>

        <div className="space-y-2">
          <label htmlFor="sheetName" className="block text-sm font-medium text-dark-textSecondary">
            Sheet Name (optional)
          </label>
          <input
            type="text"
            id="sheetName"
            name="sheetName"
            value={excelOptions?.sheetName || ''}
            onChange={(e) => handleExcelOptionChange('sheetName', e.target.value)}
            placeholder="Leave empty for all sheets"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        <div className="flex items-center">
          <input
            id="includeCharts"
            name="includeCharts"
            type="checkbox"
            checked={excelOptions?.includeCharts || false}
            onChange={(e) => handleExcelOptionChange('includeCharts', e.target.checked)}
            className="h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background"
          />
          <label htmlFor="includeCharts" className="ml-2 block text-sm text-dark-textSecondary">
            Include Charts
          </label>
        </div>

        <div className="flex items-center">
          <input
            id="preserveFormatting"
            name="preserveFormatting"
            type="checkbox"
            checked={excelOptions?.preserveFormatting || false}
            onChange={(e) => handleExcelOptionChange('preserveFormatting', e.target.checked)}
            className="h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background"
          />
          <label htmlFor="preserveFormatting" className="ml-2 block text-sm text-dark-textSecondary">
            Preserve Formatting
          </label>
        </div>
      </section>
    );
  }

  // PowerPoint conversion options
  if (['pptx2pdf', 'pptx2html', 'pptx2md', 'pptx2images'].includes(conversionType)) {
    const handlePptxOptionChange = <K extends keyof NonNullable<ConversionOptionsProps['pptxOptions']>>(
      optionKey: K,
      value: NonNullable<ConversionOptionsProps['pptxOptions']>[K]
    ) => {
      if (onPptxOptionsChange && pptxOptions) {
        onPptxOptionsChange({
          ...pptxOptions,
          [optionKey]: value,
        });
      }
    };

    return (
      <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
        <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">PowerPoint Options</h2>

        <div className="space-y-2">
          <label htmlFor="slideRange" className="block text-sm font-medium text-dark-textSecondary">
            Slide Range (optional)
          </label>
          <input
            type="text"
            id="slideRange"
            name="slideRange"
            value={pptxOptions?.slideRange || ''}
            onChange={(e) => handlePptxOptionChange('slideRange', e.target.value)}
            placeholder="e.g., 1-5 or 1,3,5"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        <div className="flex items-center">
          <input
            id="includeNotes"
            name="includeNotes"
            type="checkbox"
            checked={pptxOptions?.includeNotes || false}
            onChange={(e) => handlePptxOptionChange('includeNotes', e.target.checked)}
            className="h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background"
          />
          <label htmlFor="includeNotes" className="ml-2 block text-sm text-dark-textSecondary">
            Include Speaker Notes
          </label>
        </div>

        <div className="space-y-2">
          <label htmlFor="pptxImageQuality" className="block text-sm font-medium text-dark-textSecondary">
            Image Quality (1-100)
          </label>
          <input
            type="number"
            id="pptxImageQuality"
            name="pptxImageQuality"
            value={pptxOptions?.imageQuality || 90}
            onChange={(e) => handlePptxOptionChange('imageQuality', parseInt(e.target.value, 10) || 90)}
            min="1"
            max="100"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>
      </section>
    );
  }

  // Image conversion options
  if (['image2pdf', 'image2text', 'image2image', 'pdf2images'].includes(conversionType)) {
    const handleImageOptionChange = <K extends keyof NonNullable<ConversionOptionsProps['imageOptions']>>(
      optionKey: K,
      value: NonNullable<ConversionOptionsProps['imageOptions']>[K]
    ) => {
      if (onImageOptionsChange && imageOptions) {
        onImageOptionsChange({
          ...imageOptions,
          [optionKey]: value,
        });
      }
    };

    return (
      <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
        <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">Image Options</h2>

        <div className="space-y-2">
          <label htmlFor="imageFormat" className="block text-sm font-medium text-dark-textSecondary">
            Output Format
          </label>
          <select
            id="imageFormat"
            name="imageFormat"
            value={imageOptions?.imageFormat || 'png'}
            onChange={(e) => handleImageOptionChange('imageFormat', e.target.value)}
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none appearance-none"
          >
            <option value="png" className="bg-dark-surface text-dark-textPrimary">PNG</option>
            <option value="jpg" className="bg-dark-surface text-dark-textPrimary">JPEG</option>
            <option value="tiff" className="bg-dark-surface text-dark-textPrimary">TIFF</option>
            <option value="bmp" className="bg-dark-surface text-dark-textPrimary">BMP</option>
            <option value="webp" className="bg-dark-surface text-dark-textPrimary">WebP</option>
          </select>
        </div>

        <div className="space-y-2">
          <label htmlFor="imageQuality" className="block text-sm font-medium text-dark-textSecondary">
            Image Quality (1-100)
          </label>
          <input
            type="number"
            id="imageQuality"
            name="imageQuality"
            value={imageOptions?.imageQuality || 90}
            onChange={(e) => handleImageOptionChange('imageQuality', parseInt(e.target.value, 10) || 90)}
            min="1"
            max="100"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="resize" className="block text-sm font-medium text-dark-textSecondary">
            Resize (optional)
          </label>
          <input
            type="text"
            id="resize"
            name="resize"
            value={imageOptions?.resize || ''}
            onChange={(e) => handleImageOptionChange('resize', e.target.value)}
            placeholder="e.g., 800x600"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="crop" className="block text-sm font-medium text-dark-textSecondary">
            Crop (optional)
          </label>
          <input
            type="text"
            id="crop"
            name="crop"
            value={imageOptions?.crop || ''}
            onChange={(e) => handleImageOptionChange('crop', e.target.value)}
            placeholder="e.g., 100,100,400,300"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>
      </section>
    );
  }

  // Advanced PDF operations options
  if (['pdf2split', 'pdf2compress', 'pdf2encrypt', 'pdf2watermark', 'pdf2pages', 'pdf2ocr_layer'].includes(conversionType)) {
    const handleAdvancedPdfOptionChange = <K extends keyof NonNullable<ConversionOptionsProps['advancedPdfOptions']>>(
      optionKey: K,
      value: NonNullable<ConversionOptionsProps['advancedPdfOptions']>[K]
    ) => {
      if (onAdvancedPdfOptionsChange && advancedPdfOptions) {
        onAdvancedPdfOptionsChange({
          ...advancedPdfOptions,
          [optionKey]: value,
        });
      }
    };

    return (
      <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
        <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">Advanced PDF Options</h2>

        {conversionType === 'pdf2compress' && (
          <div className="space-y-2">
            <label htmlFor="compressionLevel" className="block text-sm font-medium text-dark-textSecondary">
              Compression Level (0-9)
            </label>
            <input
              type="number"
              id="compressionLevel"
              name="compressionLevel"
              value={advancedPdfOptions?.compressionLevel || 6}
              onChange={(e) => handleAdvancedPdfOptionChange('compressionLevel', parseInt(e.target.value, 10) || 6)}
              min="0"
              max="9"
              className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
            />
          </div>
        )}

        {conversionType === 'pdf2encrypt' && (
          <>
            <div className="space-y-2">
              <label htmlFor="userPassword" className="block text-sm font-medium text-dark-textSecondary">
                User Password (optional)
              </label>
              <input
                type="password"
                id="userPassword"
                name="userPassword"
                value={advancedPdfOptions?.userPassword || ''}
                onChange={(e) => handleAdvancedPdfOptionChange('userPassword', e.target.value)}
                placeholder="Password for opening PDF"
                className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="ownerPassword" className="block text-sm font-medium text-dark-textSecondary">
                Owner Password (optional)
              </label>
              <input
                type="password"
                id="ownerPassword"
                name="ownerPassword"
                value={advancedPdfOptions?.ownerPassword || ''}
                onChange={(e) => handleAdvancedPdfOptionChange('ownerPassword', e.target.value)}
                placeholder="Password for editing PDF"
                className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
              />
            </div>
          </>
        )}

        {conversionType === 'pdf2watermark' && (
          <>
            <div className="space-y-2">
              <label htmlFor="watermarkText" className="block text-sm font-medium text-dark-textSecondary">
                Watermark Text (optional)
              </label>
              <input
                type="text"
                id="watermarkText"
                name="watermarkText"
                value={advancedPdfOptions?.watermarkText || ''}
                onChange={(e) => handleAdvancedPdfOptionChange('watermarkText', e.target.value)}
                placeholder="Text to watermark"
                className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="watermarkImage" className="block text-sm font-medium text-dark-textSecondary">
                Watermark Image (optional)
              </label>
              <input
                type="text"
                id="watermarkImage"
                name="watermarkImage"
                value={advancedPdfOptions?.watermarkImage || ''}
                onChange={(e) => handleAdvancedPdfOptionChange('watermarkImage', e.target.value)}
                placeholder="Path to watermark image"
                className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
              />
            </div>
          </>
        )}

        {(conversionType === 'pdf2pages' || conversionType === 'pdf2split') && (
          <div className="space-y-2">
            <label htmlFor="pageRange" className="block text-sm font-medium text-dark-textSecondary">
              Page Range (optional)
            </label>
            <input
              type="text"
              id="pageRange"
              name="pageRange"
              value={advancedPdfOptions?.pageRange || ''}
              onChange={(e) => handleAdvancedPdfOptionChange('pageRange', e.target.value)}
              placeholder="e.g., 1-5 or 1,3,5"
              className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
            />
          </div>
        )}

        {conversionType === 'pdf2pages' && (
          <>
            <div className="space-y-2">
              <label htmlFor="rotate" className="block text-sm font-medium text-dark-textSecondary">
                Rotate Pages (degrees)
              </label>
              <select
                id="rotate"
                name="rotate"
                value={advancedPdfOptions?.rotate || 0}
                onChange={(e) => handleAdvancedPdfOptionChange('rotate', parseInt(e.target.value, 10) || 0)}
                className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none appearance-none"
              >
                <option value="0" className="bg-dark-surface text-dark-textPrimary">No rotation</option>
                <option value="90" className="bg-dark-surface text-dark-textPrimary">90° clockwise</option>
                <option value="180" className="bg-dark-surface text-dark-textPrimary">180°</option>
                <option value="270" className="bg-dark-surface text-dark-textPrimary">90° counter-clockwise</option>
              </select>
            </div>

            <div className="space-y-2">
              <label htmlFor="removePages" className="block text-sm font-medium text-dark-textSecondary">
                Remove Pages (optional)
              </label>
              <input
                type="text"
                id="removePages"
                name="removePages"
                value={advancedPdfOptions?.removePages || ''}
                onChange={(e) => handleAdvancedPdfOptionChange('removePages', e.target.value)}
                placeholder="e.g., 1,3,5"
                className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
              />
            </div>
          </>
        )}
      </section>
    );
  }

  // OCR layer conversion options
  if (conversionType === 'pdf2ocr_layer') {
    const handleOcrOptionChange = <K extends keyof NonNullable<ConversionOptionsProps['ocrOptions']>>(
      optionKey: K,
      value: NonNullable<ConversionOptionsProps['ocrOptions']>[K]
    ) => {
      if (onOcrOptionsChange && ocrOptions) {
        onOcrOptionsChange({
          ...ocrOptions,
          [optionKey]: value,
        });
      }
    };

    return (
      <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
        <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">OCR Layer Options</h2>

        <div className="space-y-2">
          <label htmlFor="language" className="block text-sm font-medium text-dark-textSecondary">
            OCR Language
          </label>
          <select
            id="language"
            name="language"
            value={ocrOptions?.language || 'eng'}
            onChange={(e) => handleOcrOptionChange('language', e.target.value)}
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm appearance-none"
          >
            <option value="eng" className="bg-dark-surface text-dark-textPrimary">English</option>
            <option value="spa" className="bg-dark-surface text-dark-textPrimary">Spanish</option>
            <option value="fra" className="bg-dark-surface text-dark-textPrimary">French</option>
            <option value="deu" className="bg-dark-surface text-dark-textPrimary">German</option>
            <option value="ita" className="bg-dark-surface text-dark-textPrimary">Italian</option>
            <option value="por" className="bg-dark-surface text-dark-textPrimary">Portuguese</option>
            <option value="rus" className="bg-dark-surface text-dark-textPrimary">Russian</option>
            <option value="chi_sim" className="bg-dark-surface text-dark-textPrimary">Chinese (Simplified)</option>
            <option value="jpn" className="bg-dark-surface text-dark-textPrimary">Japanese</option>
            <option value="kor" className="bg-dark-surface text-dark-textPrimary">Korean</option>
          </select>
        </div>

        <div className="space-y-2">
          <label htmlFor="dpi" className="block text-sm font-medium text-dark-textSecondary">
            DPI (Image Quality)
          </label>
          <input
            type="number"
            id="dpi"
            name="dpi"
            value={ocrOptions?.dpi || 300}
            onChange={(e) => handleOcrOptionChange('dpi', parseInt(e.target.value, 10) || 300)}
            min="50"
            max="1200"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
          <p className="text-xs text-dark-textSecondary">Higher DPI = better quality but slower processing</p>
        </div>

        <div className="space-y-2">
          <label htmlFor="preprocess" className="block text-sm font-medium text-dark-textSecondary">
            Image Preprocessing
          </label>
          <select
            id="preprocess"
            name="preprocess"
            value={ocrOptions?.preprocess || 'grayscale'}
            onChange={(e) => handleOcrOptionChange('preprocess', e.target.value)}
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm appearance-none"
          >
            <option value="none" className="bg-dark-surface text-dark-textPrimary">None</option>
            <option value="grayscale" className="bg-dark-surface text-dark-textPrimary">Grayscale</option>
            <option value="threshold" className="bg-dark-surface text-dark-textPrimary">Threshold</option>
          </select>
        </div>

        <div className="space-y-2">
          <label htmlFor="confidenceThreshold" className="block text-sm font-medium text-dark-textSecondary">
            Confidence Threshold
          </label>
          <input
            type="number"
            id="confidenceThreshold"
            name="confidenceThreshold"
            value={ocrOptions?.confidenceThreshold || 0}
            onChange={(e) => handleOcrOptionChange('confidenceThreshold', parseInt(e.target.value, 10) || 0)}
            min="0"
            max="100"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
          <p className="text-xs text-dark-textSecondary">Minimum confidence for text extraction (0-100)</p>
        </div>

        <div className="space-y-2">
          <label htmlFor="pageRange" className="block text-sm font-medium text-dark-textSecondary">
            Page Range (optional)
          </label>
          <input
            type="text"
            id="pageRange"
            name="pageRange"
            value={ocrOptions?.pageRange || 'all'}
            onChange={(e) => handleOcrOptionChange('pageRange', e.target.value)}
            placeholder="e.g., all, 1-5, or 1,3,5"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        <div className="space-y-2">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={ocrOptions?.preserveLayout || true}
              onChange={(e) => handleOcrOptionChange('preserveLayout', e.target.checked)}
              className="rounded border-dark-border bg-dark-input text-dark-primary focus:ring-dark-primary focus:ring-offset-0"
            />
            <span className="text-sm text-dark-textSecondary">Preserve text layout</span>
          </label>
        </div>
      </section>
    );
  }

  // EPUB conversion options
  if (['epub2pdf', 'epub2html', 'epub2md', 'md2epub', 'docx2epub', 'html2epub'].includes(conversionType)) {
    const handleEpubOptionChange = <K extends keyof NonNullable<ConversionOptionsProps['epubOptions']>>(
      optionKey: K,
      value: NonNullable<ConversionOptionsProps['epubOptions']>[K]
    ) => {
      if (onEpubOptionsChange && epubOptions) {
        onEpubOptionsChange({
          ...epubOptions,
          [optionKey]: value,
        });
      }
    };

    return (
      <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
        <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">EPUB Options</h2>

        <div className="space-y-2">
          <label htmlFor="epubTitle" className="block text-sm font-medium text-dark-textSecondary">
            Title (optional)
          </label>
          <input
            type="text"
            id="epubTitle"
            name="epubTitle"
            value={epubOptions?.epubTitle || ''}
            onChange={(e) => handleEpubOptionChange('epubTitle', e.target.value)}
            placeholder="Book title"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="epubAuthor" className="block text-sm font-medium text-dark-textSecondary">
            Author (optional)
          </label>
          <input
            type="text"
            id="epubAuthor"
            name="epubAuthor"
            value={epubOptions?.epubAuthor || ''}
            onChange={(e) => handleEpubOptionChange('epubAuthor', e.target.value)}
            placeholder="Author name"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="epubLanguage" className="block text-sm font-medium text-dark-textSecondary">
            Language (optional)
          </label>
          <input
            type="text"
            id="epubLanguage"
            name="epubLanguage"
            value={epubOptions?.epubLanguage || 'en'}
            onChange={(e) => handleEpubOptionChange('epubLanguage', e.target.value)}
            placeholder="e.g., en, fr, de"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
        </div>

        <div className="flex items-center">
          <input
            id="includeImages"
            name="includeImages"
            type="checkbox"
            checked={epubOptions?.includeImages || false}
            onChange={(e) => handleEpubOptionChange('includeImages', e.target.checked)}
            className="h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background"
          />
          <label htmlFor="includeImages" className="ml-2 block text-sm text-dark-textSecondary">
            Include Images
          </label>
        </div>

        <div className="space-y-2">
          <label htmlFor="tocDepth" className="block text-sm font-medium text-dark-textSecondary">
            Table of Contents Depth
          </label>
          <input
            type="number"
            id="tocDepth"
            name="tocDepth"
            value={epubOptions?.tocDepth || 3}
            onChange={(e) => handleEpubOptionChange('tocDepth', parseInt(e.target.value, 10) || 3)}
            min="1"
            max="6"
            className="block w-full p-2.5 bg-dark-input border border-dark-border text-dark-textPrimary rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          />
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