import React from 'react';

function DarkModeToggle({ darkMode, setDarkMode }) {
  return (
    <div className="dark-mode-toggle">
      <label className="switch">
        <input 
          type="checkbox" 
          checked={darkMode}
          onChange={() => setDarkMode(!darkMode)}
        />
        <span className="slider"></span>
      </label>
      <span className="toggle-label">{darkMode ? '🌙' : '☀️'}</span>
    </div>
  );
}

export default DarkModeToggle;