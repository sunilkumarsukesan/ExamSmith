import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaArrowRight } from 'react-icons/fa';
import './RoleCard.css';

export default function RoleCard({ icon: Icon, title, description, path, highlight, badge }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(path);
  };

  // Learning-focused labels based on role
  const getCtaText = () => {
    if (title.toLowerCase().includes('student')) return 'Start Learning';
    if (title.toLowerCase().includes('teacher') || title.toLowerCase().includes('instructor')) return 'Create Papers';
    if (title.toLowerCase().includes('admin')) return 'Manage Platform';
    return 'Get Started';
  };

  const getAccent = () => {
    if (title.toLowerCase().includes('student')) return 'student';
    if (title.toLowerCase().includes('teacher') || title.toLowerCase().includes('instructor')) return 'teacher';
    if (title.toLowerCase().includes('admin')) return 'admin';
    return 'default';
  };

  return (
    <div 
      className={`role-card role-card--${getAccent()} ${highlight ? 'role-card--highlight' : ''}`}
      onClick={handleClick}
    >
      {badge && <span className="role-badge">{badge}</span>}
      
      <div className="role-card-icon-wrapper">
        <Icon className="role-card-icon" />
      </div>
      
      <h3 className="role-card-title">{title}</h3>
      
      <p className="role-card-description">{description}</p>
      
      <button className="role-card-button">
        <span>{getCtaText()}</span>
        <FaArrowRight className="btn-arrow" />
      </button>
    </div>
  );
}
