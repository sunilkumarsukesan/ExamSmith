import React from 'react';
import { useNavigate } from 'react-router-dom';
import './RoleCard.css';

export default function RoleCard({ icon: Icon, title, description, path }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(path);
  };

  return (
    <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', textAlign: 'center', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', transition: 'all 0.3s ease', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '350px' }} onClick={handleClick} onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-10px)'; e.currentTarget.style.boxShadow = '0 12px 24px rgba(102, 126, 234, 0.3)'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)'; }}>
      <div style={{ fontSize: '4rem', marginBottom: '1rem', color: '#667eea', transition: 'transform 0.3s ease' }}>
        <Icon />
      </div>
      <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: '#1a1a2e', fontWeight: '600' }}>{title}</h3>
      <p style={{ fontSize: '1rem', color: '#666', marginBottom: '1.5rem', lineHeight: '1.6', flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{description}</p>
      <button style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none', padding: '10px 30px', borderRadius: '25px', fontSize: '1rem', cursor: 'pointer', fontWeight: '600', transition: 'all 0.3s ease', marginTop: 'auto' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.05)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = 'none'; }}>Get Started</button>
    </div>
  );
}
