import React from 'react';
import { ChevronUp, ChevronDown, XCircle } from 'lucide-react'; // Using lucide-react for icons

/**
 * Interface for the props of the MergeOptions component.
 * This defines what data and functions the component expects to receive from its parent.
 */
interface MergeOptionsProps {
  /** An array of full file paths that have been selected for merging. */
  orderedFilePaths: string[];
  /**
   * Callback function to be called when the order of files is changed by the user.
   * It receives the new array of ordered file paths.
   */
  onOrderChange: (newOrderedPaths: string[]) => void;
  /** The current desired name for the output merged PDF file. */
  outputFileName: string;
  /**
   * Callback function to be called when the user changes the output file name.
   * It receives the new file name string.
   */
  onOutputFileNameChange: (fileName: string) => void;
  /**
   * Optional: A default file name to suggest if the outputFileName is empty.
   * For example, "merged_document.pdf".
   */
  defaultFileName?: string;
  /**
   * Callback function to remove a specific file from the merge list.
   * It receives the file path to be removed.
   */
  onRemoveFile: (filePathToRemove: string) => void;
}

/**
 * MergeOptions Component
 *
 * This React functional component provides UI elements for users to manage
 * options related to merging PDF files. Specifically, it allows:
 * 1. Reordering the selected PDF files using "Move Up" and "Move Down" buttons.
 * 2. Specifying a custom file name for the final merged PDF.
 * 3. Removing individual files from the merge list.
 *
 * It's built using React with TypeScript for type safety and styled with Tailwind CSS.
 * Lucide-react is used for icons.
 */
const MergeOptions: React.FC<MergeOptionsProps> = ({
  orderedFilePaths,
  onOrderChange,
  outputFileName,
  onOutputFileNameChange,
  defaultFileName = "merged_output.pdf", // Sets a default if none provided
  onRemoveFile,
}) => {

  /**
   * Handles moving a file up in the merge order.
   * @param index The current index of the file to move.
   */
  const handleMoveUp = (index: number) => {
    // Cannot move up if it's the first item or list is too short
    if (index === 0 || orderedFilePaths.length <= 1) return;

    // Create a new array to avoid directly mutating the prop (React best practice)
    const newOrder = [...orderedFilePaths];
    // Simple array swap:
    // Store the element to move
    const itemToMove = newOrder[index];
    // Remove it from its current position
    newOrder.splice(index, 1);
    // Insert it one position earlier
    newOrder.splice(index - 1, 0, itemToMove);

    // Call the callback provided by the parent component to update the state there
    onOrderChange(newOrder);
  };

  /**
   * Handles moving a file down in the merge order.
   * @param index The current index of the file to move.
   */
  const handleMoveDown = (index: number) => {
    // Cannot move down if it's the last item or list is too short
    if (index === orderedFilePaths.length - 1 || orderedFilePaths.length <= 1) return;

    const newOrder = [...orderedFilePaths];
    const itemToMove = newOrder[index];
    newOrder.splice(index, 1); // Remove from current position
    newOrder.splice(index + 1, 0, itemToMove); // Insert one position later
    onOrderChange(newOrder);
  };

  /**
   * Handles changes to the output file name input field.
   * @param event The React change event from the input field.
   */
  const handleFileNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onOutputFileNameChange(event.target.value);
  };

  // If there are no files, don't render anything for reordering or filename.
  // The parent component (`ConversionPage`) will decide whether to show this component at all.
  if (orderedFilePaths.length === 0) {
    return null;
  }

  return (
    // Main container for the merge options section
    // Styled with Tailwind CSS for padding, border, rounded corners, shadow, background, and spacing
    <div className="p-6 border border-dark-border rounded-lg shadow-lg bg-dark-surface space-y-4">
      {/* Section Title */}
      <h3 className="text-xl font-semibold text-dark-textPrimary">Merge Options</h3>

      {/* Subsection for File Reordering */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-dark-textSecondary">
          Order of PDF files for merging (Top is first):
        </label>
        {/* Unordered list to display the files */}
        <ul className="space-y-1.5 p-2 border border-dark-border rounded-md max-h-60 overflow-y-auto bg-dark-input">
          {/*
            Map over the 'orderedFilePaths' array to create a list item for each file.
            'filePath' is the path string, 'index' is its position in the array.
          */}
          {orderedFilePaths.map((filePath, index) => (
            <li
              key={filePath} // React needs a unique 'key' for list items for efficient updates
              className="flex items-center justify-between p-2 bg-dark-background border border-dark-border rounded shadow-sm hover:bg-dark-surface-hover"
            >
              {/* Display the file name (extracted from the full path) */}
              <span className="truncate text-dark-textPrimary text-sm" title={filePath}>
                {index + 1}. {filePath.split(/[\\/]/).pop() || filePath}
              </span>

              {/* Container for action buttons (Remove, Move Up, Move Down) */}
              <div className="flex items-center space-x-1.5">
                {/* Remove File Button */}
                <button
                  onClick={() => onRemoveFile(filePath)}
                  title="Remove this file from merge list"
                  className="p-1 text-dark-danger hover:text-red-500 transition-colors duration-150 focus:outline-none"
                  aria-label={`Remove ${filePath.split(/[\\/]/).pop()}`}
                >
                  <XCircle size={18} />
                </button>

                {/* Move Up Button: Disabled if it's the first item */}
                <button
                  onClick={() => handleMoveUp(index)}
                  disabled={index === 0}
                  title="Move file up"
                  className="p-1 text-dark-textSecondary hover:text-dark-textPrimary disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-150 focus:outline-none"
                  aria-label={`Move ${filePath.split(/[\\/]/).pop()} up`}
                >
                  <ChevronUp size={20} />
                </button>

                {/* Move Down Button: Disabled if it's the last item */}
                <button
                  onClick={() => handleMoveDown(index)}
                  disabled={index === orderedFilePaths.length - 1}
                  title="Move file down"
                  className="p-1 text-dark-textSecondary hover:text-dark-textPrimary disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-150 focus:outline-none"
                  aria-label={`Move ${filePath.split(/[\\/]/).pop()} down`}
                >
                  <ChevronDown size={20} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Subsection for Output File Name */}
      <div className="space-y-1">
        <label htmlFor="outputFileName" className="block text-sm font-medium text-dark-textSecondary">
          Output file name for merged PDF:
        </label>
        <input
          type="text"
          id="outputFileName"
          name="outputFileName"
          value={outputFileName}
          onChange={handleFileNameChange}
          placeholder={defaultFileName} // Show default as placeholder
          // Styling for the input field using Tailwind CSS
          className="block w-full p-2.5 bg-gray-900 text-gray-100 placeholder-gray-500 border border-dark-border rounded-md shadow-sm focus:ring-dark-primary focus:border-dark-primary sm:text-sm focus:outline-none"
          // Basic validation: ensure it's not empty and suggest .pdf extension
          onBlur={(e) => {
            let currentName = e.target.value.trim();
            if (currentName === "") {
              // If empty, parent might set it to default or handle it.
              // Or, we could force defaultFileName here: onOutputFileNameChange(defaultFileName);
            } else if (!currentName.toLowerCase().endsWith('.pdf')) {
              onOutputFileNameChange(currentName + '.pdf');
            }
          }}
        />
        {/* Helper text or validation message area */}
        {!outputFileName.toLowerCase().endsWith('.pdf') && outputFileName.length > 0 && (
            <p className="text-xs text-dark-warning mt-1">
                It's recommended that the filename ends with ".pdf".
            </p>
        )}
        {outputFileName.trim() === "" && (
             <p className="text-xs text-dark-textSecondary mt-1">
                Using default: {defaultFileName} if left empty.
            </p>
        )}
      </div>
    </div>
  );
};

export default MergeOptions;

// Explanation of React/TypeScript concepts used:
//
// React.FC:
//   - Stands for React Functional Component. It's a type provided by React that
//     allows you to define components as JavaScript functions.
//   - When used with TypeScript (e.g., React.FC<MergeOptionsProps>), it provides
//     type checking for props and can implicitly type 'children' prop if needed.
//
// interface MergeOptionsProps:
//   - In TypeScript, an 'interface' is a way to define the "shape" of an object.
//   - Here, it specifies what props the MergeOptions component expects (e.g., 'orderedFilePaths'
//     must be an array of strings, 'onOrderChange' must be a function with a specific signature).
//   - This helps catch errors early if you try to use the component with incorrect props.
//
// useState (not used directly in this component, but relevant for its parent):
//   - A React Hook that lets you add state to functional components.
//   - Example: const [count, setCount] = useState(0);
//   - 'count' is the state variable, 'setCount' is the function to update it.
//
// Props (e.g., orderedFilePaths, onOrderChange):
//   - Data and functions passed from a parent component to a child component.
//   - They are read-only in the child component. If a child needs to change data
//     owned by the parent, the parent passes down a callback function (like 'onOrderChange')
//     that the child can call.
//
// Callbacks (e.g., onOrderChange):
//   - Functions passed as props to child components. The child can execute these
//     functions to communicate back to the parent, often to signal an event or
//     request a state change in the parent.
//
// Array.prototype.map():
//   - A standard JavaScript method used to iterate over an array and create a new
//     array by applying a function to each element.
//   - In React, it's commonly used to render lists of elements:
//     `myArray.map(item => <li key={item.id}>{item.name}</li>)`
//
// Key prop in lists:
//   - When rendering a list of elements using `map()`, React needs a unique `key` prop
//     for each list item (e.g., `<li key={filePath}>`).
//   - Keys help React identify which items have changed, are added, or are removed,
//     allowing for more efficient updates to the DOM. File paths are unique here.
//
// Spreading an array ([...orderedFilePaths]):
//   - This is JavaScript's spread syntax. `[...someArray]` creates a new shallow copy
//     of `someArray`.
//   - It's important in React when updating state that is an array or object because
//     React relies on immutable updates. You should create a new array/object
//     instead of modifying the existing one directly to ensure React detects the change.
//
// Event Handlers (e.g., onClick, onChange):
//   - Props on HTML-like elements (JSX) that specify functions to be called when
//     certain events occur (like a button click or an input field's value changing).
//   - Example: `<button onClick={() => console.log('Clicked!')}>Click Me</button>`
//
// Tailwind CSS classes (e.g., "p-6", "border-dark-border", "rounded-lg"):
//   - Utility classes provided by the Tailwind CSS framework. Each class applies a
//     specific style (e.g., "p-6" means padding of 6 units, "rounded-lg" means
//     large rounded corners).
//   - This approach allows for rapidly building custom designs directly in the HTML/JSX
//     without writing separate CSS files for many common styles.
//
// Lucide-react icons (<ChevronUp />, <ChevronDown />):
//  - A library of simply designed SVG icons, imported as React components.
//  - They are easily customizable with size and color props.
//
// Conditional Rendering (if (orderedFilePaths.length === 0) return null;):
//  - A common pattern in React where you decide whether to render a piece of UI
//    based on certain conditions. If the condition is met to not render,
//    returning `null` tells React to render nothing for that part.
//
// Input onBlur event:
//  - This event fires when an input element loses focus (e.g., user clicks away).
//  - Used here for a simple auto-correction (adding .pdf if missing).