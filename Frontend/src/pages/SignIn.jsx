import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './SignIn.css';
import { FaUser, FaLock, FaArrowRight, FaEnvelope } from 'react-icons/fa';

export default function SignIn() {
  const navigate = useNavigate();
  const { login, register, error: authError } = useAuth();
  
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (isLogin) {
        // Login
        const result = await login(formData.email, formData.password);
        
        if (result.success) {
          setSuccess('Login successful! Redirecting...');
          // Redirect based on role
          const role = result.user.role;
          setTimeout(() => {
            if (role === 'ADMIN') {
              navigate('/admin');
            } else if (role === 'INSTRUCTOR') {
              navigate('/teacher');
            } else {
              navigate('/student');
            }
          }, 1000);
        } else {
          setError(result.error || 'Login failed');
        }
      } else {
        // Register
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }

        if (formData.password.length < 8) {
          setError('Password must be at least 8 characters');
          setLoading(false);
          return;
        }

        const result = await register(formData.name, formData.email, formData.password);
        
        if (result.success) {
          setSuccess('Registration successful! Please sign in.');
          setIsLogin(true);
          setFormData({ ...formData, password: '', confirmPassword: '' });
        } else {
          setError(result.error || 'Registration failed');
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="signin">
      <div className="signin-container">
        {/* Left Side - Visual/Branding */}
        <div className="signin-visual">
          <h2>ExamSmith</h2>
          <p>AI-Powered Question Paper Generation</p>
          <div className="visual-content">
            <div className="visual-item">📚 Learn Smarter</div>
            <div className="visual-item">🎯 Practice Better</div>
            <div className="visual-item">✨ Succeed Together</div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="signin-form-wrapper">
          <form className="signin-form" onSubmit={handleSubmit}>
            <h1>{isLogin ? 'Welcome Back' : 'Create Account'}</h1>
            <p className="signin-subtitle">
              {isLogin ? 'Sign in to your ExamSmith account' : 'Register for a new student account'}
            </p>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required={!isLogin}
                  placeholder="Enter your full name"
                  disabled={loading}
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Enter your email"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
                minLength={isLogin ? undefined : 8}
                disabled={loading}
              />
            </div>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password *</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required={!isLogin}
                  placeholder="Confirm your password"
                  disabled={loading}
                />
              </div>
            )}

            {error && (
              <div className="error-message">
                ✗ {error}
              </div>
            )}

            {success && (
              <div className="success-message">
                ✓ {success}
              </div>
            )}

            <button type="submit" className="signin-btn" disabled={loading}>
              {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
              {!loading && <FaArrowRight />}
            </button>

            <div className="signin-footer">
              {isLogin ? (
                <>
                  <a href="#forgot">Forgot password?</a>
                  <span>•</span>
                  <button type="button" className="link-btn" onClick={toggleMode}>
                    Create account
                  </button>
                </>
              ) : (
                <>
                  <span>Already have an account?</span>
                  <button type="button" className="link-btn" onClick={toggleMode}>
                    Sign in
                  </button>
                </>
              )}
            </div>

            {!isLogin && (
              <p className="register-note">
                Note: Self-registration is for students only. Instructors and admins must be created by an administrator.
              </p>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
