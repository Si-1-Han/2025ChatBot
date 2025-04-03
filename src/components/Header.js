import React from 'react';
import './Header.css';

function Header() {
  const refreshPage = () => {
    window.location.reload();
  };

  return (
    <header className="header">
      <div className="header-center" onClick={refreshPage} style={{ cursor: 'pointer' }}>
        Chat Bot
      </div>
    </header>
  );
}

export default Header;