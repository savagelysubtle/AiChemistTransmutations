import React from 'react';
import { FolderOpen, Folder } from 'lucide-react';
import Button from './Button';
import Card from './Card';
import Icon from './Icon';
import Badge from './Badge';

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
    <div className="space-y-4">
      <Button
        onClick={onSelectOutputDirectory}
        variant="secondary"
        size="lg"
        className="w-full"
      >
        <Icon size="sm" className="mr-2">
          <FolderOpen />
        </Icon>
        {buttonText}
      </Button>

      {outputDir && (
        <Card variant="elevated" className="animate-slide-up">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-dark-primary/10 rounded-lg text-dark-primary">
              <Icon size="sm">
                <Folder />
              </Icon>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-medium text-dark-textPrimary text-sm">Output Directory</h3>
                <Badge variant="success" size="sm">Selected</Badge>
              </div>
              <p className="text-xs text-dark-textSecondary truncate" title={outputDir}>
                {outputDir}
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default DirectoryInput;