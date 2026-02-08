import React from 'react';

export default function Footer() {
  return (
    <footer style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', color: '#fff', padding: '3rem 0 0', marginTop: '5rem' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
        <div>
          <h3 style={{ marginBottom: '1rem', color: '#06B6D4' }}>ExamSmith</h3>
          <p style={{ color: '#ccc', lineHeight: '1.6' }}>AI-powered question paper generation platform for students and teachers.</p>
        </div>

        <div>
          <h4 style={{ marginBottom: '1rem', color: '#06B6D4' }}>Quick Links</h4>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ margin: '0.5rem 0' }}><a href="/" style={{ color: '#ccc', textDecoration: 'none' }}>Home</a></li>
            <li style={{ margin: '0.5rem 0' }}><a href="/about" style={{ color: '#ccc', textDecoration: 'none' }}>About</a></li>
            <li style={{ margin: '0.5rem 0' }}><a href="/contact" style={{ color: '#ccc', textDecoration: 'none' }}>Contact</a></li>
          </ul>
        </div>

        <div>
          <h4 style={{ marginBottom: '1rem', color: '#06B6D4' }}>Follow Us</h4>
          <div style={{ display: 'flex', gap: '1.5rem', fontSize: '1.5rem' }}>
            <a href="#" style={{ color: '#ccc', textDecoration: 'none' }}>f</a>
            <a href="#" style={{ color: '#ccc', textDecoration: 'none' }}>T</a>
            <a href="#" style={{ color: '#ccc', textDecoration: 'none' }}>in</a>
            <a href="#" style={{ color: '#ccc', textDecoration: 'none' }}>gh</a>
          </div>
        </div>
      </div>

      <div style={{ backgroundColor: 'rgba(0, 0, 0, 0.2)', padding: '1.5rem', textAlign: 'center', borderTop: '1px solid rgba(6, 182, 212, 0.3)' }}>
        <p style={{ color: '#999', margin: 0 }}>&copy; 2026 ExamSmith. All rights reserved.</p>
      </div>
    </footer>
  );
}
