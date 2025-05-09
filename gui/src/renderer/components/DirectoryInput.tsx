import React from 'react';

/**
 * Props for the DirectoryInput component.
 */
interface DirectoryInputProps {
  /** The currently selected output directory path, or null if none selected. */
  outputDir: string | null;
  /** Callback function triggered when an output directory is selected. */
  onSelectOutputDirectory: () => Promise<void>; // Matches the original handler's signature
  /** Optional: Custom text for the directory selection button. */
  buttonText?: string;
}

/**
 * Component for selecting the output directory.
 * It includes a button to open the directory dialog and displays the selected path.
 */
const DirectoryInput: React.FC<DirectoryInputProps> = ({
  outputDir,
  onSelectOutputDirectory,
  buttonText = "Select Output Directory (Optional)" // Default button text
}) => {
  return (
    <div className="space-y-2">
      <button
        onClick={onSelectOutputDirectory}
        className="w-full bg-dark-primary hover:bg-dark-hoverPrimary text-white font-semibold py-2.5 px-4 rounded-lg shadow-md transition duration-150 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-dark-primary focus:ring-opacity-50"
      >
        {buttonText}
      </button>
      {outputDir && (
        <div className="mt-2 p-3 border border-dark-border rounded-md bg-dark-surface text-sm shadow">
          <p className="font-medium text-dark-textPrimary">
            Output Directory: <span className="text-dark-textSecondary font-normal ml-1">{outputDir}</span>
          </p>
        </div>
      )}
    </div>
  );
};

export default DirectoryInput;