import React from 'react';
import { Link } from 'react-router-dom';
import { FaGraduationCap, FaHeart, FaTwitter, FaLinkedin, FaGithub, FaEnvelope, FaChartLine, FaBook, FaRobot, FaUserGraduate, FaChalkboardTeacher, FaShieldAlt, FaCheckCircle } from 'react-icons/fa';
import './Footer.css';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      {/* Trust Bar */}
      <div className="trust-bar">
        <div className="trust-bar-content">
          <div className="trust-item">
            <FaCheckCircle className="trust-icon" />
            <span>10,000+ Questions Practiced</span>
          </div>
          <div className="trust-item">
            <FaUserGraduate className="trust-icon" />
            <span>500+ Happy Students</span>
          </div>
          <div className="trust-item">
            <FaChalkboardTeacher className="trust-icon" />
            <span>Trusted by Teachers</span>
          </div>
          <div className="trust-item">
            <FaShieldAlt className="trust-icon" />
            <span>Curriculum Aligned</span>
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="footer-main">
        <div className="footer-container">
          {/* Brand Section */}
          <div className="footer-section footer-brand">
            <div className="footer-logo">
              <span className="logo-icon">🎯</span>
              <span className="logo-text">ExamSmith</span>
            </div>
            <p className="footer-tagline">
              Practice smarter. Score higher. Your personal learning companion for exam success.
            </p>
            <div className="footer-mission">
              <span className="mission-icon">💚</span>
              <span>Built with love for learners</span>
            </div>
          </div>

          {/* For Students */}
          <div className="footer-section">
            <h4 className="footer-heading">
              <FaUserGraduate className="heading-icon" />
              For Students
            </h4>
            <ul className="footer-links">
              <li><Link to="/student">Start Practicing</Link></li>
              <li><Link to="/student">Track Progress</Link></li>
              <li><Link to="/student">AI Tutor Help</Link></li>
              <li><a href="#">Study Tips</a></li>
            </ul>
          </div>

          {/* For Teachers */}
          <div className="footer-section">
            <h4 className="footer-heading">
              <FaChalkboardTeacher className="heading-icon" />
              For Teachers
            </h4>
            <ul className="footer-links">
              <li><Link to="/teacher">Generate Papers</Link></li>
              <li><a href="#">Review Questions</a></li>
              <li><a href="#">Class Analytics</a></li>
              <li><a href="#">Teacher Resources</a></li>
            </ul>
          </div>

          {/* Features */}
          <div className="footer-section">
            <h4 className="footer-heading">
              <FaChartLine className="heading-icon" />
              Features
            </h4>
            <ul className="footer-links">
              <li><a href="#">AI-Powered Practice</a></li>
              <li><a href="#">Progress Tracking</a></li>
              <li><a href="#">Instant Explanations</a></li>
              <li><a href="#">Personalized Learning</a></li>
            </ul>
          </div>

          {/* Connect */}
          <div className="footer-section footer-connect">
            <h4 className="footer-heading">
              <FaHeart className="heading-icon" />
              Stay Connected
            </h4>
            <p className="connect-text">Join our learning community!</p>
            <div className="social-icons">
              <a href="#" className="social-link" aria-label="Twitter">
                <FaTwitter />
              </a>
              <a href="#" className="social-link" aria-label="LinkedIn">
                <FaLinkedin />
              </a>
              <a href="#" className="social-link" aria-label="GitHub">
                <FaGithub />
              </a>
              <a href="#" className="social-link" aria-label="Email">
                <FaEnvelope />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Bottom */}
      <div className="footer-bottom">
        <div className="footer-bottom-content">
          <p className="copyright">
            &copy; {currentYear} ExamSmith. Crafted with <FaHeart className="heart-icon" /> for learners everywhere.
          </p>
          <div className="footer-bottom-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Contact Us</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
