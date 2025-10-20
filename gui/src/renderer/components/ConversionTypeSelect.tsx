import React from 'react';
import {
  FileText,
  FileImage,
  FileCode,
  FileType,
  FileDown,
  FileUp,
  Merge,
  Edit3,
  Globe,
  Type,
  ChevronRight
} from 'lucide-react';
import Card from './Card';
import Icon from './Icon';
import { cn } from '../utils/cn';

/**
 * Props for the ConversionTypeSelect component.
 */
interface ConversionTypeSelectProps {
  /** The currently selected conversion type. */
  conversionType: string;
  /** Callback function when the conversion type changes. */
  onConversionTypeChange: (newType: string) => void;
}

interface ConversionOption {
  value: string;
  label: string;
  icon: React.ReactNode;
  description: string;
}

interface ConversionCategory {
  title: string;
  options: ConversionOption[];
}

const conversionCategories: ConversionCategory[] = [
  {
    title: 'PDF Conversions',
    options: [
      {
        value: 'pdf2md',
        label: 'PDF to Markdown',
        icon: <FileText />,
        description: 'Extract text from PDF files'
      },
      {
        value: 'pdf2html',
        label: 'PDF to HTML',
        icon: <Globe />,
        description: 'Convert PDF to web format'
      },
      {
        value: 'pdf2editable',
        label: 'PDF to Editable PDF',
        icon: <Edit3 />,
        description: 'Make PDFs editable with OCR'
      }
    ]
  },
  {
    title: 'Markdown Conversions',
    options: [
      {
        value: 'md2pdf',
        label: 'Markdown to PDF',
        icon: <FileDown />,
        description: 'Convert Markdown to PDF'
      },
      {
        value: 'md2html',
        label: 'Markdown to HTML',
        icon: <Globe />,
        description: 'Convert Markdown to web format'
      },
      {
        value: 'md2docx',
        label: 'Markdown to DOCX',
        icon: <FileType />,
        description: 'Convert Markdown to Word document'
      },
      {
        value: 'mdx2md',
        label: 'MDX to Markdown',
        icon: <FileCode />,
        description: 'Convert MDX to standard Markdown'
      }
    ]
  },
  {
    title: 'Document Conversions',
    options: [
      {
        value: 'docx2md',
        label: 'DOCX to Markdown',
        icon: <FileText />,
        description: 'Convert Word documents to Markdown'
      },
      {
        value: 'docx2pdf',
        label: 'DOCX to PDF',
        icon: <FileDown />,
        description: 'Convert Word documents to PDF'
      },
      {
        value: 'html2pdf',
        label: 'HTML to PDF',
        icon: <FileDown />,
        description: 'Convert web pages to PDF'
      },
      {
        value: 'txt2pdf',
        label: 'TXT to PDF',
        icon: <Type />,
        description: 'Convert text files to PDF'
      }
    ]
  },
  {
    title: 'Utilities',
    options: [
      {
        value: 'merge_to_pdf',
        label: 'Merge PDFs',
        icon: <Merge />,
        description: 'Combine multiple PDFs into one'
      }
    ]
  }
];

/**
 * Component for selecting the conversion type from categorized cards.
 */
const ConversionTypeSelect: React.FC<ConversionTypeSelectProps> = ({ conversionType, onConversionTypeChange }) => {
  return (
    <Card variant="elevated" className="animate-fade-in">
      <div className="flex items-center gap-2 mb-6">
        <div className="w-8 h-8 bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd rounded-lg flex items-center justify-center text-white font-bold">
          1
        </div>
        <h2 className="text-2xl font-semibold text-light-textPrimary dark:text-dark-textPrimary">Select Conversion Type</h2>
      </div>

      <div className="space-y-6">
        {conversionCategories.map((category, categoryIndex) => (
          <div key={category.title} className="space-y-3">
            <h3 className="text-lg font-medium text-light-textSecondary dark:text-dark-textSecondary flex items-center gap-2">
              <ChevronRight className="w-4 h-4" />
              {category.title}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {category.options.map((option) => (
                <button
                  key={option.value}
                  onClick={() => onConversionTypeChange(option.value)}
                  className={cn(
                    'p-4 rounded-lg border-2 transition-all duration-200 text-left group hover:scale-105 focus:outline-none focus:ring-2 focus:ring-light-primary dark:focus:ring-dark-primary focus:ring-offset-2',
                    conversionType === option.value
                      ? 'border-light-primary dark:border-dark-primary bg-light-primary/10 dark:bg-dark-primary/10 shadow-lg shadow-light-primary/20 dark:shadow-dark-primary/20'
                      : 'border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface hover:border-light-primary/50 dark:hover:border-dark-primary/50 hover:bg-light-surfaceElevated dark:hover:bg-dark-surfaceElevated'
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className={cn(
                      'p-2 rounded-lg transition-colors duration-200',
                      conversionType === option.value
                        ? 'bg-light-primary dark:bg-dark-primary text-white'
                        : 'bg-light-surfaceElevated dark:bg-dark-surfaceElevated text-light-textSecondary dark:text-dark-textSecondary group-hover:bg-light-primary dark:group-hover:bg-dark-primary group-hover:text-white'
                    )}>
                      <Icon size="md">{option.icon}</Icon>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-light-textPrimary dark:text-dark-textPrimary text-sm mb-1">
                        {option.label}
                      </h4>
                      <p className="text-xs text-light-textSecondary dark:text-dark-textSecondary leading-relaxed">
                        {option.description}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default ConversionTypeSelect;