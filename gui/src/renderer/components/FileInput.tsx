import React from 'react';
import { Scrollbars } from 'react-custom-scrollbars-2';
import { X, FileText, FileImage, FileCode, FileType, FileDown, FileUp, Merge, Edit3, Globe, Type } from 'lucide-react';
import Button from './Button';
import Badge from './Badge';
import Icon from './Icon';
import Card from './Card';
import { cn } from '../utils/cn';

/**
 * Props for the FileInput component.
 */
interface FileInputProps {
  /** Array of currently selected file paths. */
  selectedFiles: string[];
  /** Callback function triggered when the user initiates file selection (e.g., clicks "Select Files" button). */
  onSelectFilesClick: () => Promise<void>;
  /** Callback function triggered when the list of selected files changes (e.g., a file is deselected). */
  onSelectedFilesChange: (updatedFiles: string[]) => void;
  /** Callback function triggered when the user clicks "Clear Selection". */
  onClearSelection: () => void;
  /** Optional: File types to accept (e.g., '.pdf,.md'). Passed to file dialog if supported. */
  accept?: string;
  /** Optional: Custom text for the main file selection button. */
  buttonText?: string;
  /** Optional: Instructional text displayed below the selection button. */
  instructions?: string;
  /** Optional: Hint for allowing multiple file selections. */
  allowMultiple?: boolean;
}

/**
 * Component for selecting input files.
 * It includes:
 * - A button to open the file dialog.
 * - A list of selected files with checkboxes to deselect individual files.
 * - A button to clear the entire selection.
 */
const FileInput: React.FC<FileInputProps> = ({
  selectedFiles,
  onSelectFilesClick,
  onSelectedFilesChange,
  onClearSelection,
  buttonText = "Select Input File(s)", // Default button text
  instructions,
  // 'accept' and 'allowMultiple' are not directly used in this component's rendering
  // but are part of props for the parent to manage dialog options.
}) => {

  const handleFileCheckboxChange = (filePath: string, isChecked: boolean) => {
    if (isChecked) {
      // This case should ideally not happen if a file is already in selectedFiles and its checkbox is checked
      // But as a safeguard, add it if it's not there (though UI implies it's for deselection)
      if (!selectedFiles.includes(filePath)) {
        onSelectedFilesChange([...selectedFiles, filePath]);
      }
    } else {
      // Remove the file from the selection
      onSelectedFilesChange(selectedFiles.filter(file => file !== filePath));
    }
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf':
        return <FileText />;
      case 'md':
      case 'markdown':
        return <FileCode />;
      case 'mdx':
        return <FileCode />;
      case 'docx':
        return <FileType />;
      case 'html':
      case 'htm':
        return <Globe />;
      case 'txt':
        return <Type />;
      default:
        return <FileText />;
    }
  };

  const getFileTypeBadge = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf':
        return <Badge variant="error" size="sm">PDF</Badge>;
      case 'md':
      case 'markdown':
        return <Badge variant="info" size="sm">MD</Badge>;
      case 'mdx':
        return <Badge variant="info" size="sm">MDX</Badge>;
      case 'docx':
        return <Badge variant="warning" size="sm">DOCX</Badge>;
      case 'html':
      case 'htm':
        return <Badge variant="success" size="sm">HTML</Badge>;
      case 'txt':
        return <Badge variant="default" size="sm">TXT</Badge>;
      default:
        return <Badge variant="default" size="sm">{ext?.toUpperCase()}</Badge>;
    }
  };

  return (
    <div className="space-y-4">
      <Button
        onClick={onSelectFilesClick}
        variant="primary"
        size="lg"
        className="w-full"
      >
        {buttonText}
      </Button>

      {instructions && (
        <p className="text-sm text-center text-dark-textSecondary px-4">
          {instructions}
        </p>
      )}

      {selectedFiles.length > 0 && (
        <Card variant="elevated" className="animate-slide-up">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-dark-textPrimary">Selected Files</h3>
              <Badge variant="info" size="sm">{selectedFiles.length}</Badge>
            </div>
            <Button
              onClick={onClearSelection}
              variant="outline"
              size="sm"
            >
              Clear All
            </Button>
          </div>

          <Scrollbars
            autoHeight
            autoHeightMax={200}
            className="rounded-lg"
          >
            <div className="space-y-2 p-2">
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 bg-dark-background border border-dark-border rounded-lg hover:bg-dark-surfaceElevated transition-colors duration-200 group"
                >
                  <div className="p-2 bg-dark-surfaceElevated rounded-lg text-dark-textSecondary group-hover:text-dark-primary transition-colors duration-200">
                    <Icon size="sm">{getFileIcon(file)}</Icon>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-dark-textPrimary text-sm truncate" title={file}>
                        {file.split(/[\\/]/).pop() || file}
                      </span>
                      {getFileTypeBadge(file)}
                    </div>
                    <p className="text-xs text-dark-textSecondary truncate" title={file}>
                      {file}
                    </p>
                  </div>

                  <button
                    onClick={() => handleFileCheckboxChange(file, false)}
                    className="p-1.5 text-dark-textSecondary hover:text-dark-error hover:bg-dark-errorBg rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-dark-error focus:ring-offset-2"
                    title="Remove file"
                  >
                    <Icon size="sm"><X /></Icon>
                  </button>
                </div>
              ))}
            </div>
          </Scrollbars>
        </Card>
      )}
    </div>
  );
};

export default FileInput;