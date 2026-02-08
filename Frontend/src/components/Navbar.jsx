import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { isAuthenticated, user, logout, isAdmin, isInstructor } = useAuth();
  const navigate = useNavigate();

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const closeMenu = () => {
    setMenuOpen(false);
  };

  const handleLogout = () => {
    logout();
    closeMenu();
    navigate('/');
  };

  // Get dashboard link based on role
  const getDashboardLink = () => {
    if (isAdmin) return '/admin';
    if (isInstructor) return '/teacher';
    return '/student';
  };

  // Get role-specific dashboard label
  const getDashboardLabel = () => {
    if (isAdmin) return 'Admin';
    if (isInstructor) return 'My Papers';
    return 'My Learning';
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={closeMenu}>
          <span className="logo-icon">🎯</span>
          <span className="logo-text">ExamSmith</span>
          <span className="logo-tagline">Learn Smarter</span>
        </Link>

        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-links" onClick={closeMenu}>
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/about" className="nav-links" onClick={closeMenu}>
              About
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/contact" className="nav-links" onClick={closeMenu}>
              Contact
            </Link>
          </li>
          {isAuthenticated && (
            <li className="nav-item">
              <Link to={getDashboardLink()} className="nav-links dashboard-link" onClick={closeMenu}>
                <span className="dashboard-icon">
                  {isAdmin ? '⚙️' : isInstructor ? '📄' : '📊'}
                </span>
                {getDashboardLabel()}
              </Link>
            </li>
          )}
        </ul>

        <div className="nav-auth">
          {isAuthenticated ? (
            <div className="auth-section">
              <div className="user-badge">
                <span className="user-avatar">
                  {user?.name?.charAt(0)?.toUpperCase() || '👤'}
                </span>
                <span className="user-name">{user?.name}</span>
                <span className="user-role">{user?.role}</span>
              </div>
              <button 
                onClick={handleLogout}
                className="logout-btn"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <Link to="/signin" className="nav-links-btn" onClick={closeMenu}>
              <span className="btn-icon">🚀</span> Start Learning
            </Link>
          )}
        </div>

        {/* Mobile Menu Toggle */}
        <button className="menu-toggle" onClick={toggleMenu} aria-label="Toggle menu">
          <span className={`hamburger ${menuOpen ? 'active' : ''}`}></span>
        </button>
      </div>
    </nav>
  );
}
