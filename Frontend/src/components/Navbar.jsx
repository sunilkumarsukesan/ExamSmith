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
    <nav style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', height: '80px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '1.2rem', position: 'sticky', top: 0, zIndex: 999, boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', maxWidth: '1200px', padding: '0 50px' }}>
        <Link to="/" style={{ color: '#fff', cursor: 'pointer', textDecoration: 'none', fontSize: '2.2rem', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 'bold' }} onClick={closeMenu}>
          📚 ExamSmith
        </Link>

        <div style={{ display: 'none', color: '#fff', fontSize: '1.8rem', cursor: 'pointer' }} onClick={toggleMenu}>
          Menu
        </div>

        <ul style={{ display: 'flex', listStyle: 'none', textAlign: 'center', margin: 0, padding: 0, gap: '1rem' }}>
          <li style={{ height: '80px', lineHeight: '80px', margin: 0 }}>
            <Link to="/" style={{ color: '#fff', textDecoration: 'none', padding: '0.5rem 1rem', height: '100%', display: 'flex', alignItems: 'center', transition: 'all 0.3s ease', borderRadius: '4px' }} onClick={closeMenu}>
              Home
            </Link>
          </li>
          <li style={{ height: '80px', lineHeight: '80px', margin: 0 }}>
            <Link to="/about" style={{ color: '#fff', textDecoration: 'none', padding: '0.5rem 1rem', height: '100%', display: 'flex', alignItems: 'center', transition: 'all 0.3s ease', borderRadius: '4px' }} onClick={closeMenu}>
              About
            </Link>
          </li>
          <li style={{ height: '80px', lineHeight: '80px', margin: 0 }}>
            <Link to="/contact" style={{ color: '#fff', textDecoration: 'none', padding: '0.5rem 1rem', height: '100%', display: 'flex', alignItems: 'center', transition: 'all 0.3s ease', borderRadius: '4px' }} onClick={closeMenu}>
              Contact Us
            </Link>
          </li>
          {isAuthenticated && (
            <li style={{ height: '80px', lineHeight: '80px', margin: 0 }}>
              <Link to={getDashboardLink()} style={{ color: '#fff', textDecoration: 'none', padding: '0.5rem 1rem', height: '100%', display: 'flex', alignItems: 'center', transition: 'all 0.3s ease', borderRadius: '4px' }} onClick={closeMenu}>
                Dashboard
              </Link>
            </li>
          )}
        </ul>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {isAuthenticated ? (
            <>
              <span style={{ color: '#fff', fontSize: '0.9rem' }}>
                {user?.name} ({user?.role})
              </span>
              <button 
                onClick={handleLogout}
                style={{ padding: '8px 20px', borderRadius: '4px', border: 'none', outline: 'none', background: '#fff', color: '#667eea', fontSize: '1rem', cursor: 'pointer', transition: 'all 0.3s ease', fontWeight: '600' }}
              >
                Logout
              </button>
            </>
          ) : (
            <Link to="/signin" style={{ padding: '8px 20px', borderRadius: '4px', border: 'none', outline: 'none', background: '#fff', color: '#667eea', fontSize: '1rem', cursor: 'pointer', transition: 'all 0.3s ease', textDecoration: 'none', fontWeight: '600' }} onClick={closeMenu}>
              Sign In
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
