import React, { useState } from 'react';
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
  ChevronRight,
  ChevronDown
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
    title: 'To PDF',
    options: [
      {
        value: 'md2pdf',
        label: 'Markdown to PDF',
        icon: <FileDown />,
        description: 'Convert Markdown to PDF'
      },
      {
        value: 'html2pdf',
        label: 'HTML to PDF',
        icon: <FileDown />,
        description: 'Convert web pages to PDF'
      },
      {
        value: 'docx2pdf',
        label: 'DOCX to PDF',
        icon: <FileDown />,
        description: 'Convert Word documents to PDF'
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
    title: 'To DOCX',
    options: [
      {
        value: 'md2docx',
        label: 'Markdown to DOCX',
        icon: <FileType />,
        description: 'Convert Markdown to Word document'
      }
    ]
  },
  {
    title: 'To Markdown',
    options: [
      {
        value: 'pdf2md',
        label: 'PDF to Markdown',
        icon: <FileText />,
        description: 'Extract text from PDF files'
      },
      {
        value: 'docx2md',
        label: 'DOCX to Markdown',
        icon: <FileText />,
        description: 'Convert Word documents to Markdown'
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
    title: 'To HTML',
    options: [
      {
        value: 'md2html',
        label: 'Markdown to HTML',
        icon: <Globe />,
        description: 'Convert Markdown to web format'
      },
      {
        value: 'pdf2html',
        label: 'PDF to HTML',
        icon: <Globe />,
        description: 'Convert PDF to web format'
      }
    ]
  },
  {
    title: 'PDF Enhancement',
    options: [
      {
        value: 'pdf2editable',
        label: 'PDF to Editable PDF',
        icon: <Edit3 />,
        description: 'Make PDFs editable with OCR'
      }
    ]
  },
  {
    title: 'Merge',
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
  // State to track which categories are expanded (default: all expanded)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(conversionCategories.map(cat => cat.title))
  );

  const toggleCategory = (categoryTitle: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(categoryTitle)) {
        newSet.delete(categoryTitle);
      } else {
        newSet.add(categoryTitle);
      }
      return newSet;
    });
  };

  return (
    <Card variant="elevated" className="animate-fade-in">
      <div className="flex items-center gap-2 mb-6">
        <div className="w-8 h-8 bg-gradient-to-r from-light-gradientStart to-light-gradientEnd dark:from-dark-gradientStart dark:to-dark-gradientEnd rounded-lg flex items-center justify-center text-white font-bold">
          1
        </div>
        <h2 className="text-2xl font-semibold text-light-textPrimary dark:text-dark-textPrimary">Select Conversion Type</h2>
      </div>

      <div className="space-y-6">
        {/* Categories 1-2: Side by side on larger screens */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {conversionCategories.slice(0, 2).map((category) => {
            const isExpanded = expandedCategories.has(category.title);
            return (
              <div key={category.title} className="space-y-3">
                <button
                  onClick={() => toggleCategory(category.title)}
                  className="w-full text-left text-lg font-medium text-light-textSecondary dark:text-dark-textSecondary flex items-center gap-2 hover:text-light-textPrimary dark:hover:text-dark-textPrimary transition-colors duration-200 focus:outline-none"
                >
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 transition-transform duration-200" />
                  ) : (
                    <ChevronRight className="w-4 h-4 transition-transform duration-200" />
                  )}
                  {category.title}
                </button>
                {isExpanded && (
                  <div className="grid grid-cols-1 gap-3 animate-fade-in">
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
                )}
              </div>
            );
          })}
        </div>

        {/* Categories 3+: Full width stacked */}
        {conversionCategories.slice(2).map((category) => {
          const isExpanded = expandedCategories.has(category.title);
          return (
            <div key={category.title} className="space-y-3">
              <button
                onClick={() => toggleCategory(category.title)}
                className="w-full text-left text-lg font-medium text-light-textSecondary dark:text-dark-textSecondary flex items-center gap-2 hover:text-light-textPrimary dark:hover:text-dark-textPrimary transition-colors duration-200 focus:outline-none"
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4 transition-transform duration-200" />
                ) : (
                  <ChevronRight className="w-4 h-4 transition-transform duration-200" />
                )}
                {category.title}
              </button>
              {isExpanded && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 animate-fade-in">
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
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default ConversionTypeSelect;