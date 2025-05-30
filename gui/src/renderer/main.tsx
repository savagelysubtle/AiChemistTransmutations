import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css'; // Import global styles including Tailwind
// import './styles/customScrollbar.css'; // Import custom scrollbar styles

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);