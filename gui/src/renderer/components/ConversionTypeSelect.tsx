import React from 'react';

/**
 * Props for the ConversionTypeSelect component.
 */
interface ConversionTypeSelectProps {
  /** The currently selected conversion type. */
  conversionType: string;
  /** Callback function when the conversion type changes. */
  onConversionTypeChange: (newType: string) => void;
}

/**
 * Component for selecting the conversion type from a dropdown menu.
 */
const ConversionTypeSelect: React.FC<ConversionTypeSelectProps> = ({ conversionType, onConversionTypeChange }) => {
  return (
    <section className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface">
      <h2 className="text-2xl font-semibold mb-3 text-dark-textPrimary">1. Select Conversion Type</h2>
      <select
        value={conversionType}
        onChange={(e) => onConversionTypeChange(e.target.value)}
        className="p-3 border border-dark-border rounded-md w-full bg-dark-surface text-dark-textPrimary focus:ring-2 focus:ring-dark-primary focus:border-dark-primary appearance-none focus:outline-none"
      >
        {/* Options sorted alphabetically by display text */}
        <option value="docx2md" className="bg-dark-surface text-dark-textPrimary">DOCX to Markdown</option>
        <option value="docx2pdf" className="bg-dark-surface text-dark-textPrimary">DOCX to PDF</option>
        <option value="html2pdf" className="bg-dark-surface text-dark-textPrimary">HTML to PDF</option>
        <option value="md2docx" className="bg-dark-surface text-dark-textPrimary">Markdown to DOCX</option>
        <option value="md2html" className="bg-dark-surface text-dark-textPrimary">Markdown to HTML</option>
        <option value="md2pdf" className="bg-dark-surface text-dark-textPrimary">Markdown to PDF</option>
        <option value="mdx2md" className="bg-dark-surface text-dark-textPrimary">MDX to Markdown</option>
        <option value="merge_to_pdf" className="bg-dark-surface text-dark-textPrimary">Merge PDFs to Single PDF</option>
        <option value="pdf2editable" className="bg-dark-surface text-dark-textPrimary">PDF to Editable PDF</option>
        <option value="pdf2html" className="bg-dark-surface text-dark-textPrimary">PDF to HTML</option>
        <option value="pdf2md" className="bg-dark-surface text-dark-textPrimary">PDF to Markdown</option>
        {/* Add other conversion types as needed, maintaining alphabetical order */}
      </select>
    </section>
  );
};

export default ConversionTypeSelect;