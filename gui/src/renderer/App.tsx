import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import ConversionPage from './pages/ConversionPage';

/**
 * Main application component.
 * Renders the primary page of the application.
 * Future routing logic could be added here if the application grows to multiple pages.
 */
function App() {
  return (
    <ThemeProvider>
      <ConversionPage />
    </ThemeProvider>
  );
}

export default App;