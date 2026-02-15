import React from 'react';
import './About.css';

export default function About() {
  return (
    <div className="about">
      <div className="about-hero">
        <h1>About ExamSmith</h1>
        <p>Revolutionizing Education with AI</p>
      </div>

      <div className="about-container">
        <section className="about-section">
          <h2>Our Mission</h2>
          <p>
            ExamSmith is dedicated to transforming the way students prepare for exams and how teachers create assessments. 
            Using advanced artificial intelligence, we generate high-quality, relevant question papers that adapt to individual learning needs.
          </p>
        </section>

        <section className="about-section">
          <h2>Why ExamSmith?</h2>
          <ul className="about-list">
            <li><strong>AI-Based Question Generation:</strong> Intelligent algorithms create unique and challenging questions</li>
            <li><strong>Personalized Learning:</strong> Adaptive question sets tailored to your level and goals</li>
            <li><strong>Time-Saving:</strong> Generate complete papers in seconds instead of hours</li>
            <li><strong>Comprehensive Analysis:</strong> Detailed performance metrics and insights</li>
            <li><strong>Teacher Support:</strong> Advanced tools for creating assessments and tracking student progress</li>
            <li><strong>Admin Controls:</strong> Centralized management of users and system configuration</li>
          </ul>
        </section>

        <section className="about-section">
          <h2>How It Works</h2>
          <div className="how-it-works">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Select Your Role</h3>
              <p>Choose whether you're a student, teacher, or administrator</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>Configure Parameters</h3>
              <p>Set difficulty level, topics, and question types</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Generate Questions</h3>
              <p>AI generates relevant and challenging questions instantly</p>
            </div>
            <div className="step">
              <div className="step-number">4</div>
              <h3>Practice & Improve</h3>
              <p>Practice with generated papers and track your progress</p>
            </div>
          </div>
        </section>

        <section className="about-section">
          <h2>Our Technology</h2>
          <p>
            ExamSmith leverages state-of-the-art machine learning models and natural language processing to understand 
            curriculum requirements, generate contextually relevant questions, and evaluate student responses with precision. 
            Our platform is built with scalability and security in mind.
          </p>
        </section>
      </div>
    </div>
  );
}
