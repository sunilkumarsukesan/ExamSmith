import React from 'react';
import RoleCard from '../components/RoleCard';
import './Home.css';

export default function Home() {
  const roles = [
    {
      icon: () => <span style={{ fontSize: '4rem' }}>🎓</span>,
      title: 'Student',
      description: 'Generate and practice question papers with AI-powered content tailored to your level',
      path: '/student',
    },
    {
      icon: () => <span style={{ fontSize: '4rem' }}>👨‍🏫</span>,
      title: 'Teacher',
      description: 'Create and review question papers for your classes with advanced customization',
      path: '/teacher',
    },
    {
      icon: () => <span style={{ fontSize: '4rem' }}>⚙️</span>,
      title: 'Admin',
      description: 'Manage users and system configuration with comprehensive admin controls',
      path: '/admin',
    },
  ];

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <section style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '5rem 2rem', textAlign: 'center', marginBottom: '3rem' }}>
        <div>
          <h1 style={{ fontSize: '3.5rem', marginBottom: '1rem', fontWeight: '700' }}>Welcome to ExamSmith</h1>
          <p style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>AI-Powered Question Paper Generation Platform</p>
          <p style={{ fontSize: '1.1rem', opacity: '0.9' }}>
            Create, practice, and master exam papers with intelligent question generation
          </p>
        </div>
      </section>

      <section style={{ padding: '3rem 2rem', backgroundColor: '#f9fafb', marginBottom: '3rem' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '3rem', color: '#1a1a2e' }}>Select Your Role</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
            {roles.map((role, index) => (
              <RoleCard
                key={index}
                icon={role.icon}
                title={role.title}
                description={role.description}
                path={role.path}
              />
            ))}
          </div>
        </div>
      </section>

      <section style={{ padding: '3rem 2rem', backgroundColor: 'white', maxWidth: '1200px', margin: '2rem auto' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '3rem', color: '#1a1a2e' }}>Why Choose ExamSmith?</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
          <div style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', padding: '2rem', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#1a1a2e' }}>🤖 AI-Powered</h3>
            <p style={{ color: '#555', lineHeight: '1.6' }}>Intelligent algorithms generate relevant and challenging questions</p>
          </div>
          <div style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', padding: '2rem', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#1a1a2e' }}>⚡ Instant Generation</h3>
            <p style={{ color: '#555', lineHeight: '1.6' }}>Create complete question papers in seconds</p>
          </div>
          <div style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', padding: '2rem', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#1a1a2e' }}>📊 Smart Analytics</h3>
            <p style={{ color: '#555', lineHeight: '1.6' }}>Track performance and identify areas for improvement</p>
          </div>
          <div style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', padding: '2rem', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#1a1a2e' }}>🎯 Adaptive Learning</h3>
            <p style={{ color: '#555', lineHeight: '1.6' }}>Personalized question sets based on your level</p>
          </div>
        </div>
      </section>
    </div>
  );
}
