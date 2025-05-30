import React from 'react';
// import CustomScrollbar from './CustomScrollbar';
import { Scrollbars } from 'react-custom-scrollbars-2';

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

  return (
    <div className="space-y-3">
      <button
        onClick={onSelectFilesClick}
        className="w-full bg-dark-primary hover:bg-dark-hoverPrimary text-white font-semibold py-2.5 px-4 rounded-lg shadow-md transition duration-150 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-dark-primary focus:ring-opacity-50"
      >
        {buttonText}
      </button>
      {instructions && (
        <p className="text-xs text-center text-dark-textSecondary mt-1">
          {instructions}
        </p>
      )}

      {selectedFiles.length > 0 && (
        <div className="mt-3 p-3 border border-dark-border rounded-md bg-dark-surface text-sm shadow">
          <div className="flex justify-between items-center mb-2">
            <p className="font-medium text-dark-textPrimary">Selected Files ({selectedFiles.length}):</p>
            <button
              onClick={onClearSelection}
              className="text-xs bg-dark-surface hover:bg-opacity-75 text-dark-secondaryAccent border border-dark-secondaryAccent font-semibold py-1 px-2 rounded shadow-sm transition duration-150 ease-in-out focus:outline-none focus:ring-1 focus:ring-dark-secondaryAccent"
            >
              Clear Selection
            </button>
          </div>
          <Scrollbars
            autoHeight
            autoHeightMax={128} // max-h-32 (8rem = 128px)
            className="rounded" // Applies to the outer div of Scrollbars
            // The ul below already has p-1, which is the content padding.
          >
            <ul className="space-y-1 p-1">
              {selectedFiles.map((file, index) => (
                <li key={index} className="flex items-center justify-between p-1.5 bg-dark-background border border-dark-border rounded hover:bg-opacity-50 hover:bg-dark-border text-dark-textSecondary">
                  <label htmlFor={`file-checkbox-${index}`} className="flex items-center space-x-2 cursor-pointer flex-grow min-w-0">
                    <input
                      type="checkbox"
                      id={`file-checkbox-${index}`}
                      checked={true}
                      onChange={(e) => handleFileCheckboxChange(file, e.target.checked)}
                      className="form-checkbox h-4 w-4 text-dark-primary bg-dark-surface border-dark-border rounded focus:ring-dark-primary focus:ring-offset-dark-background"
                    />
                    <span className="truncate text-dark-textPrimary" title={file}>
                      {file.split(/[\\/]/).pop() || file}
                    </span>
                  </label>
                </li>
              ))}
            </ul>
          </Scrollbars>
        </div>
      )}
    </div>
  );
};

export default FileInput;