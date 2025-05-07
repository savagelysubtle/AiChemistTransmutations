import React from 'react';

/**
 * Header component for the application.
 * Displays the main title of the application.
 */
const Header: React.FC = () => {
  return (
    <header className="text-center py-6">
      <h1 className="text-4xl font-bold text-dark-textPrimary">MDtoPDF Converter</h1>
    </header>
  );
};

export default Header;