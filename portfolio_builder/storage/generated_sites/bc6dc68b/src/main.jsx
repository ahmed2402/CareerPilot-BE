import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

function RootApp() {
  return (
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

export default RootApp;

ReactDOM.createRoot(document.getElementById('root')).render(<RootApp />);