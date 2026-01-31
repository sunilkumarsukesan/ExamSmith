import React, { useState } from 'react';
import './SignIn.css';
import { FaUser, FaLock, FaArrowRight } from 'react-icons/fa';

export default function SignIn() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    role: 'student',
  });

  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Sign in data:', formData);
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setFormData({ email: '', password: '', role: 'student' });
    }, 2000);
  };

  return (
    <div className="signin">
      <div className="signin-container">
        <form className="signin-form" onSubmit={handleSubmit}>
          <h1>Welcome Back</h1>
          <p className="signin-subtitle">Sign in to your ExamSmith account</p>

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <div className="input-wrapper">
              <FaUser className="input-icon" />
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Enter your email"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <div className="input-wrapper">
              <FaLock className="input-icon" />
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="role">Role *</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <button type="submit" className="signin-btn">
            Sign In <FaArrowRight />
          </button>

          {submitted && (
            <div className="success-message">
              ✓ Sign in successful! Redirecting...
            </div>
          )}

          <div className="signin-footer">
            <a href="#forgot">Forgot password?</a>
            <span>•</span>
            <a href="#signup">Create account</a>
          </div>
        </form>

        <div className="signin-visual">
          <h2>ExamSmith</h2>
          <p>AI-Powered Question Paper Generation</p>
          <div className="visual-content">
            <div className="visual-item">📚 Learn Smarter</div>
            <div className="visual-item">🎯 Practice Better</div>
            <div className="visual-item">✨ Succeed Together</div>
          </div>
        </div>
      </div>
    </div>
  );
}
