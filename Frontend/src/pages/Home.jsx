import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RoleCard from '../components/RoleCard';
import './Home.css';

export default function Home() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Error parsing user:', e);
      }
    }
    setIsLoading(false);
  }, []);

  // If user is logged in, show personalized content
  if (!isLoading && user) {
    return <PersonalizedHome user={user} navigate={navigate} />;
  }

  // If user is not logged in, show role selection
  return <RoleSelectionHome />;
}

function PersonalizedHome({ user, navigate }) {
  const roleConfig = {
    student: {
      icon: '🎓',
      title: 'Student Dashboard',
      greeting: `Welcome back, ${user.name || 'Student'}!`,
      subtitle: 'Practice and master your exams',
      features: [
        {
          icon: '📝',
          title: 'Practice Papers',
          description: 'Generate and attempt question papers tailored to your level'
        },
        {
          icon: '📊',
          title: 'Your Results',
          description: 'Review your performance and track your progress'
        },
        {
          icon: '💬',
          title: 'Ask AI Tutor',
          description: 'Get help with concepts and questions from our AI tutor'
        },
        {
          icon: '🎯',
          title: 'Weak Areas',
          description: 'Identify and focus on topics where you need improvement'
        }
      ],
      actions: [
        { label: 'Go to Dashboard', path: '/student', primary: true }
      ]
    },
    teacher: {
      icon: '👨‍🏫',
      title: 'Teacher Dashboard',
      greeting: `Welcome back, ${user.name || 'Teacher'}!`,
      subtitle: 'Create and manage quality assessments',
      features: [
        {
          icon: '✏️',
          title: 'Create Papers',
          description: 'Design custom question papers for your classes'
        },
        {
          icon: '👥',
          title: 'Manage Classes',
          description: 'Organize and manage your student groups'
        },
        {
          icon: '📈',
          title: 'View Analytics',
          description: 'Analyze student performance and identify learning gaps'
        },
        {
          icon: '🔄',
          title: 'Review Answers',
          description: 'Evaluate and provide feedback on student responses'
        }
      ],
      actions: [
        { label: 'Go to Dashboard', path: '/teacher', primary: true }
      ]
    },
    admin: {
      icon: '⚙️',
      title: 'Admin Dashboard',
      greeting: `Welcome back, Admin ${user.name || ''}!`,
      subtitle: 'System management and configuration',
      features: [
        {
          icon: '👤',
          title: 'User Management',
          description: 'Manage users, roles, and permissions'
        },
        {
          icon: '📚',
          title: 'Content Management',
          description: 'Manage curriculum and question bank'
        },
        {
          icon: '🔐',
          title: 'System Security',
          description: 'Configure security settings and access controls'
        },
        {
          icon: '📊',
          title: 'System Reports',
          description: 'View comprehensive system analytics'
        }
      ],
      actions: [
        { label: 'Go to Dashboard', path: '/admin', primary: true }
      ]
    }
  };

  const config = roleConfig[user.role] || roleConfig.student;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-cream)' }}>
      {/* Hero Section */}
      <section style={{
        background: `linear-gradient(135deg, var(--color-sage) 0%, var(--color-sage-dark) 100%)`,
        color: 'white',
        padding: '4rem 2rem',
        textAlign: 'center',
        marginBottom: '3rem'
      }}>
        <div>
          <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>{config.icon}</div>
          <h1 style={{ fontSize: '2.8rem', marginBottom: '0.5rem', fontWeight: '700' }}>{config.greeting}</h1>
          <p style={{ fontSize: '1.3rem', opacity: '0.95' }}>{config.subtitle}</p>
        </div>
      </section>

      {/* Quick Actions */}
      <section style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto 3rem' }}>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '2rem' }}>
          {config.actions.map((action, idx) => (
            <button
              key={idx}
              onClick={() => window.location.href = action.path}
              style={{
                padding: '0.75rem 2rem',
                background: action.primary ? 'linear-gradient(135deg, var(--color-sage) 0%, var(--color-sage-dark) 100%)' : 'var(--color-white)',
                color: action.primary ? 'white' : 'var(--color-sage)',
                border: `2px solid var(--color-sage)`,
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '600',
                transition: 'all 0.3s ease',
              }}
              onMouseOver={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 4px 12px rgba(95, 113, 97, 0.3)';
              }}
              onMouseOut={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = 'none';
              }}
            >
              {action.label}
            </button>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section style={{ padding: '3rem 2rem', maxWidth: '1200px', margin: '0 auto 3rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '3rem', color: 'var(--color-charcoal)' }}>What You Can Do</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          {config.features.map((feature, idx) => (
            <div
              key={idx}
              style={{
                background: 'white',
                padding: '1.5rem',
                borderRadius: '0.75rem',
                border: '1px solid var(--color-gray-200)',
                transition: 'all 0.3s ease',
                cursor: 'pointer'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 8px 16px rgba(95, 113, 97, 0.15)';
                e.currentTarget.style.borderColor = 'var(--color-sage)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = 'var(--color-gray-200)';
              }}
            >
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{feature.icon}</div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: 'var(--color-charcoal)', fontWeight: '600' }}>{feature.title}</h3>
              <p style={{ color: 'var(--color-gray-600)', lineHeight: '1.5', fontSize: '0.9rem' }}>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Profile Section */}
      <section style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', textAlign: 'center' }}>
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '0.75rem',
          border: '1px solid var(--color-gray-200)'
        }}>
          <p style={{ color: 'var(--color-gray-600)', marginBottom: '1rem' }}>Logged in as <strong>{user.name}</strong> ({user.role})</p>
          <button
            onClick={() => {
              localStorage.removeItem('user');
              localStorage.removeItem('token');
              window.location.href = '/signin';
            }}
            style={{
              padding: '0.5rem 1.5rem',
              background: 'var(--color-error)',
              color: 'white',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: '600'
            }}
          >
            Sign Out
          </button>
        </div>
      </section>
    </div>
  );
}

function RoleSelectionHome() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-cream)' }}>
      <section style={{
        background: `linear-gradient(135deg, var(--color-sage) 0%, var(--color-sage-dark) 100%)`,
        color: 'white',
        padding: '5rem 2rem',
        textAlign: 'center',
        marginBottom: '3rem'
      }}>
        <div>
          <h1 style={{ fontSize: '3.5rem', marginBottom: '1rem', fontWeight: '700' }}>Welcome to ExamSmith</h1>
          <p style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>AI-Powered Question Paper Generation Platform</p>
          <p style={{ fontSize: '1.1rem', opacity: '0.9' }}>
            Create, practice, and master exam papers with intelligent question generation
          </p>
        </div>
      </section>

      <section style={{ padding: '3rem 2rem', backgroundColor: 'white', maxWidth: '1200px', margin: '2rem auto' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '3rem', color: 'var(--color-charcoal)' }}>Why Choose ExamSmith?</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
          <div style={{ background: 'linear-gradient(135deg, var(--color-cream-light) 0%, var(--color-cream) 100%)', padding: '2rem', borderRadius: '0.75rem', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--color-charcoal)' }}>🤖 AI-Powered</h3>
            <p style={{ color: 'var(--color-gray-600)', lineHeight: '1.6' }}>Intelligent algorithms generate relevant and challenging questions</p>
          </div>
          <div style={{ background: 'linear-gradient(135deg, var(--color-cream-light) 0%, var(--color-cream) 100%)', padding: '2rem', borderRadius: '0.75rem', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--color-charcoal)' }}>⚡ Instant Generation</h3>
            <p style={{ color: 'var(--color-gray-600)', lineHeight: '1.6' }}>Create complete question papers in seconds</p>
          </div>
          <div style={{ background: 'linear-gradient(135deg, var(--color-cream-light) 0%, var(--color-cream) 100%)', padding: '2rem', borderRadius: '0.75rem', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--color-charcoal)' }}>📊 Smart Analytics</h3>
            <p style={{ color: 'var(--color-gray-600)', lineHeight: '1.6' }}>Track performance and identify areas for improvement</p>
          </div>
          <div style={{ background: 'linear-gradient(135deg, var(--color-cream-light) 0%, var(--color-cream) 100%)', padding: '2rem', borderRadius: '0.75rem', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--color-charcoal)' }}>🎯 Adaptive Learning</h3>
            <p style={{ color: 'var(--color-gray-600)', lineHeight: '1.6' }}>Personalized question sets based on your level</p>
          </div>
        </div>
      </section>

      <section style={{ padding: '3rem 2rem', backgroundColor: 'var(--color-cream)', marginBottom: '3rem', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem', color: 'var(--color-charcoal)' }}>Ready to Get Started?</h2>
        <p style={{ fontSize: '1.1rem', color: 'var(--color-gray-600)', marginBottom: '2rem' }}>Sign in to your account to access your personalized dashboard</p>
        <a href="/signin" style={{
          display: 'inline-block',
          padding: '0.75rem 2rem',
          background: 'linear-gradient(135deg, var(--color-sage) 0%, var(--color-sage-dark) 100%)',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '0.5rem',
          fontWeight: '600',
          transition: 'all 0.3s ease'
        }}>
          Sign In
        </a>
      </section>
    </div>
  );
}
