import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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

  // If user is logged in, show personalized dashboard redirect
  if (!isLoading && user) {
    return <PersonalizedHome user={user} navigate={navigate} />;
  }

  // If user is not logged in, show landing page
  return <LandingPage />;
}

// ============================================
// PERSONALIZED HOME FOR LOGGED-IN USERS
// ============================================
function PersonalizedHome({ user, navigate }) {
  const roleConfig = {
    student: {
      icon: '🎯',
      greeting: `Welcome back, ${user.name || 'Learner'}!`,
      subtitle: "Ready to continue your learning journey?",
      motivation: "You're making great progress! Keep it up 💪",
      quickStats: [
        { label: 'Practice Sessions', value: '12', icon: '📝' },
        { label: 'Topics Mastered', value: '8', icon: '⭐' },
        { label: 'Day Streak', value: '5', icon: '🔥' }
      ],
      todayFocus: {
        title: "Today's Recommendation",
        description: "Continue practicing Algebra - you're 80% to mastery!",
        action: 'Start Practice',
        path: '/student'
      },
      actions: [
        { label: 'Go to Dashboard', path: '/student', primary: true, icon: '📊' },
        { label: 'Quick Practice', path: '/student', primary: false, icon: '⚡' }
      ]
    },
    teacher: {
      icon: '👨‍🏫',
      greeting: `Welcome back, ${user.name || 'Instructor'}!`,
      subtitle: "Your students are waiting for new challenges",
      motivation: "You've helped 45 students improve this week! 🌟",
      quickStats: [
        { label: 'Papers Created', value: '24', icon: '📄' },
        { label: 'Students Reached', value: '156', icon: '👥' },
        { label: 'Avg. Improvement', value: '+18%', icon: '📈' }
      ],
      todayFocus: {
        title: "Pending Reviews",
        description: "3 papers are waiting for your approval",
        action: 'Review Now',
        path: '/teacher'
      },
      actions: [
        { label: 'Go to Dashboard', path: '/teacher', primary: true, icon: '📊' },
        { label: 'Create Paper', path: '/teacher', primary: false, icon: '✏️' }
      ]
    },
    admin: {
      icon: '⚙️',
      greeting: `Welcome back, Admin!`,
      subtitle: "System overview and management",
      motivation: "Platform is running smoothly 🚀",
      quickStats: [
        { label: 'Active Users', value: '234', icon: '👤' },
        { label: 'Papers Generated', value: '1.2K', icon: '📄' },
        { label: 'System Health', value: '99.9%', icon: '💚' }
      ],
      todayFocus: {
        title: "System Status",
        description: "All systems operational",
        action: 'View Dashboard',
        path: '/admin'
      },
      actions: [
        { label: 'Admin Dashboard', path: '/admin', primary: true, icon: '⚙️' }
      ]
    }
  };

  const config = roleConfig[user.role] || roleConfig.student;

  return (
    <div className="home personalized">
      {/* Hero Section with Greeting */}
      <section className="hero-personalized">
        <div className="hero-content">
          <span className="hero-icon">{config.icon}</span>
          <h1>{config.greeting}</h1>
          <p className="hero-subtitle">{config.subtitle}</p>
          <div className="motivation-badge">
            <span className="motivation-icon">✨</span>
            {config.motivation}
          </div>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="quick-stats-section">
        <div className="container">
          <div className="quick-stats-grid">
            {config.quickStats.map((stat, idx) => (
              <div key={idx} className="quick-stat-card">
                <span className="stat-icon">{stat.icon}</span>
                <span className="stat-value">{stat.value}</span>
                <span className="stat-label">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Today's Focus */}
      <section className="today-focus-section">
        <div className="container">
          <div className="today-focus-card">
            <div className="focus-content">
              <span className="focus-badge">📌 {config.todayFocus.title}</span>
              <p className="focus-description">{config.todayFocus.description}</p>
            </div>
            <button 
              className="focus-action-btn"
              onClick={() => navigate(config.todayFocus.path)}
            >
              {config.todayFocus.action} →
            </button>
          </div>
        </div>
      </section>

      {/* Action Buttons */}
      <section className="actions-section">
        <div className="container">
          <div className="actions-grid">
            {config.actions.map((action, idx) => (
              <button
                key={idx}
                className={`action-btn ${action.primary ? 'primary' : 'secondary'}`}
                onClick={() => navigate(action.path)}
              >
                <span className="action-icon">{action.icon}</span>
                {action.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Profile Info */}
      <section className="profile-section">
        <div className="container">
          <div className="profile-card">
            <p>Logged in as <strong>{user.name}</strong> ({user.role})</p>
            <button
              className="logout-btn"
              onClick={() => {
                localStorage.removeItem('user');
                localStorage.removeItem('token');
                window.location.href = '/signin';
              }}
            >
              Sign Out
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

// ============================================
// LANDING PAGE FOR NEW/LOGGED-OUT USERS
// ============================================
function LandingPage() {
  return (
    <div className="home landing">
      {/* Hero Section - Learning Focused */}
      <section className="hero-landing">
        <div className="hero-content">
          <div className="hero-badge">🎯 AI-Powered Learning Platform</div>
          <h1>Practice Smarter.<br/>Score Higher.</h1>
          <p className="hero-description">
            Your personal AI exam coach that generates smart practice papers, 
            tracks your progress, and helps you master your weak areas — automatically.
          </p>
          <div className="hero-cta-group">
            <Link to="/signin" className="cta-primary">
              <span>🚀</span> Start Practicing Now
            </Link>
            <a href="#how-it-works" className="cta-secondary">
              <span>▶️</span> See How It Works
            </a>
          </div>
          <div className="hero-trust-badges">
            <span className="trust-badge">✓ Syllabus Aligned</span>
            <span className="trust-badge">✓ Exam Pattern Based</span>
            <span className="trust-badge">✓ Bloom's Taxonomy</span>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-mockup">
            <div className="mockup-header">
              <span className="mockup-dot"></span>
              <span className="mockup-dot"></span>
              <span className="mockup-dot"></span>
            </div>
            <div className="mockup-content">
              <div className="mockup-progress">
                <div className="progress-label">Your Progress</div>
                <div className="progress-bar-mock">
                  <div className="progress-fill" style={{width: '72%'}}></div>
                </div>
                <div className="progress-text">72% Mastery</div>
              </div>
              <div className="mockup-stats">
                <div className="mock-stat">
                  <span className="mock-stat-value">🔥 12</span>
                  <span className="mock-stat-label">Day Streak</span>
                </div>
                <div className="mock-stat">
                  <span className="mock-stat-value">📈 +23%</span>
                  <span className="mock-stat-label">Improvement</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pain → Solution Section */}
      <section className="transformation-section">
        <div className="container">
          <h2 className="section-title">Transform Your Exam Preparation</h2>
          <p className="section-subtitle">See how ExamSmith changes your learning experience</p>
          <div className="transformation-grid">
            <TransformCard
              before={{ icon: '😰', title: 'Confusion', description: 'Random study without direction' }}
              after={{ icon: '🎯', title: 'Clarity', description: 'Targeted practice on weak areas' }}
            />
            <TransformCard
              before={{ icon: '📚', title: 'Overwhelmed', description: 'Too many topics, no structure' }}
              after={{ icon: '📊', title: 'Organized', description: 'Step-by-step learning path' }}
            />
            <TransformCard
              before={{ icon: '❓', title: 'No Feedback', description: 'Practice without knowing gaps' }}
              after={{ icon: '💡', title: 'Smart Insights', description: 'Know exactly where to improve' }}
            />
          </div>
        </div>
      </section>

      {/* Learning Journey Section */}
      <section id="how-it-works" className="journey-section">
        <div className="container">
          <h2 className="section-title">Your Learning Journey</h2>
          <p className="section-subtitle">Simple steps to exam success</p>
          <div className="journey-timeline">
            <JourneyStep 
              number="1" 
              icon="📖" 
              title="Choose Your Subject" 
              description="Select your syllabus and exam pattern"
            />
            <JourneyStep 
              number="2" 
              icon="🎯" 
              title="Generate Practice Paper" 
              description="AI creates personalized questions for you"
            />
            <JourneyStep 
              number="3" 
              icon="✍️" 
              title="Practice Daily" 
              description="Build consistency with regular practice"
            />
            <JourneyStep 
              number="4" 
              icon="📊" 
              title="Track Weak Areas" 
              description="See exactly which topics need attention"
            />
            <JourneyStep 
              number="5" 
              icon="🏆" 
              title="Improve Scores" 
              description="Watch your confidence and scores grow"
            />
          </div>
        </div>
      </section>

      {/* Features Section - Learning Focused */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Built for Better Learning</h2>
          <p className="section-subtitle">Every feature designed to help you succeed</p>
          <div className="features-grid">
            <FeatureCard 
              icon="🧠"
              title="Smart Question Generation"
              description="AI generates questions based on your level and weak areas, not random topics"
              highlight="Personalized"
            />
            <FeatureCard 
              icon="📈"
              title="Progress Tracking"
              description="Visual dashboards show your mastery level for each topic"
              highlight="Insightful"
            />
            <FeatureCard 
              icon="🔥"
              title="Streak Motivation"
              description="Build daily practice habits with streaks and achievements"
              highlight="Motivating"
            />
            <FeatureCard 
              icon="🎯"
              title="Weak Area Focus"
              description="Automatically identifies and prioritizes topics you need to work on"
              highlight="Targeted"
            />
            <FeatureCard 
              icon="📝"
              title="Exam Pattern Matching"
              description="Practice with questions that match real exam formats exactly"
              highlight="Realistic"
            />
            <FeatureCard 
              icon="💬"
              title="AI Tutor Chat"
              description="Get instant explanations and help when you're stuck"
              highlight="24/7 Support"
            />
          </div>
        </div>
      </section>

      {/* Progress Preview Section */}
      <section className="preview-section">
        <div className="container">
          <h2 className="section-title">See Your Growth</h2>
          <p className="section-subtitle">Track every step of your improvement journey</p>
          <div className="preview-grid">
            <div className="preview-card mastery">
              <h3>📊 Topic Mastery</h3>
              <div className="mastery-bars">
                <MasteryBar topic="Algebra" percentage={85} level="advanced" />
                <MasteryBar topic="Geometry" percentage={62} level="intermediate" />
                <MasteryBar topic="Statistics" percentage={45} level="beginner" />
                <MasteryBar topic="Calculus" percentage={78} level="intermediate" />
              </div>
            </div>
            <div className="preview-card improvement">
              <h3>📈 Your Improvement</h3>
              <div className="improvement-chart">
                <div className="chart-bars">
                  {[35, 42, 48, 55, 62, 68, 75, 82].map((height, idx) => (
                    <div key={idx} className="chart-bar" style={{height: `${height}%`}}>
                      <span className="chart-value">{height}%</span>
                    </div>
                  ))}
                </div>
                <div className="chart-label">Past 8 weeks → +47% improvement!</div>
              </div>
            </div>
            <div className="preview-card focus">
              <h3>🎯 Focus Areas</h3>
              <div className="focus-list">
                <div className="focus-item weak">
                  <span className="focus-indicator">⚠️</span>
                  <span className="focus-topic">Quadratic Equations</span>
                  <span className="focus-action">Practice Now</span>
                </div>
                <div className="focus-item moderate">
                  <span className="focus-indicator">💪</span>
                  <span className="focus-topic">Linear Graphs</span>
                  <span className="focus-action">Almost there!</span>
                </div>
                <div className="focus-item strong">
                  <span className="focus-indicator">⭐</span>
                  <span className="focus-topic">Basic Operations</span>
                  <span className="focus-action">Mastered!</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Who Is It For Section */}
      <section className="audience-section">
        <div className="container">
          <h2 className="section-title">Who Is ExamSmith For?</h2>
          <div className="audience-grid">
            <AudienceCard 
              icon="🎓"
              title="Students"
              features={[
                'Practice papers tailored to your level',
                'Track progress and weak areas',
                'Build exam confidence daily'
              ]}
              cta="Start Learning"
              path="/signin"
            />
            <AudienceCard 
              icon="👨‍🏫"
              title="Teachers"
              features={[
                'Generate quality assessments quickly',
                'Align with syllabus automatically',
                'Track class performance analytics'
              ]}
              cta="Create Assessments"
              path="/signin"
            />
            <AudienceCard 
              icon="🏫"
              title="Institutions"
              features={[
                'Standardized question generation',
                'Multiple class management',
                'Comprehensive analytics dashboard'
              ]}
              cta="Contact Us"
              path="/contact"
            />
          </div>
        </div>
      </section>

      {/* Trust & Credibility Section */}
      <section className="trust-section">
        <div className="container">
          <h2 className="section-title">Academic Excellence, Guaranteed</h2>
          <div className="trust-grid">
            <div className="trust-card">
              <span className="trust-icon">📚</span>
              <h3>Syllabus Aligned</h3>
              <p>Every question matches your curriculum exactly</p>
            </div>
            <div className="trust-card">
              <span className="trust-icon">🎯</span>
              <h3>Bloom's Taxonomy</h3>
              <p>Questions test all cognitive levels</p>
            </div>
            <div className="trust-card">
              <span className="trust-icon">📝</span>
              <h3>Exam Pattern Based</h3>
              <p>Practice exactly like real exams</p>
            </div>
            <div className="trust-card">
              <span className="trust-icon">🔒</span>
              <h3>Secure & Private</h3>
              <p>Your data is always protected</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="final-cta-section">
        <div className="container">
          <div className="final-cta-content">
            <h2>Ready to Transform Your Learning?</h2>
            <p>Join thousands of students who are practicing smarter and scoring higher.</p>
            <Link to="/signin" className="cta-primary large">
              <span>🚀</span> Start Your Journey Today
            </Link>
            <p className="cta-note">Free to get started • No credit card required</p>
          </div>
        </div>
      </section>
    </div>
  );
}

// ============================================
// REUSABLE COMPONENTS
// ============================================

function TransformCard({ before, after }) {
  return (
    <div className="transform-card">
      <div className="transform-before">
        <span className="transform-icon">{before.icon}</span>
        <h4>{before.title}</h4>
        <p>{before.description}</p>
      </div>
      <div className="transform-arrow">→</div>
      <div className="transform-after">
        <span className="transform-icon">{after.icon}</span>
        <h4>{after.title}</h4>
        <p>{after.description}</p>
      </div>
    </div>
  );
}

function JourneyStep({ number, icon, title, description }) {
  return (
    <div className="journey-step">
      <div className="step-number">{number}</div>
      <div className="step-icon">{icon}</div>
      <h3 className="step-title">{title}</h3>
      <p className="step-description">{description}</p>
    </div>
  );
}

function FeatureCard({ icon, title, description, highlight }) {
  return (
    <div className="feature-card">
      <span className="feature-highlight">{highlight}</span>
      <span className="feature-icon">{icon}</span>
      <h3 className="feature-title">{title}</h3>
      <p className="feature-description">{description}</p>
    </div>
  );
}

function MasteryBar({ topic, percentage, level }) {
  return (
    <div className="mastery-item">
      <div className="mastery-info">
        <span className="mastery-topic">{topic}</span>
        <span className={`mastery-badge ${level}`}>{percentage}%</span>
      </div>
      <div className="mastery-bar-track">
        <div className={`mastery-bar-fill ${level}`} style={{width: `${percentage}%`}}></div>
      </div>
    </div>
  );
}

function AudienceCard({ icon, title, features, cta, path }) {
  return (
    <div className="audience-card">
      <span className="audience-icon">{icon}</span>
      <h3 className="audience-title">{title}</h3>
      <ul className="audience-features">
        {features.map((feature, idx) => (
          <li key={idx}>✓ {feature}</li>
        ))}
      </ul>
      <Link to={path} className="audience-cta">{cta} →</Link>
    </div>
  );
}
