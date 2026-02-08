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

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={closeMenu}>
          📚 ExamSmith
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
              Contact Us
            </Link>
          </li>
          {isAuthenticated && (
            <li className="nav-item">
              <Link to={getDashboardLink()} className="nav-links" onClick={closeMenu}>
                Dashboard
              </Link>
            </li>
          )}
        </ul>

        <div className="nav-auth">
          {isAuthenticated ? (
            <>
              <span className="user-info">
                {user?.name}
              </span>
              <button 
                onClick={handleLogout}
                className="nav-links-btn"
              >
                Logout
              </button>
            </>
          ) : (
            <Link to="/signin" className="nav-links-btn" onClick={closeMenu}>
              Sign In
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
