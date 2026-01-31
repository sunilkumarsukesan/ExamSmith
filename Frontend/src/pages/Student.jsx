import React, { useState } from 'react';
import { generateQuestionPaper } from '../services/api';
import './Student.css';
import { FaSpinner, FaDownload, FaPrint } from 'react-icons/fa';

export default function Student() {
  const [isLoading, setIsLoading] = useState(false);
  const [questions, setQuestions] = useState(null);
  const [error, setError] = useState(null);

  const handleGeneratePaper = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const mockQuestions = [
        {
          id: 1,
          text: 'What is the definition of personification in literature?',
          options: ['A) Giving human qualities to non-human things', 'B) Comparing two things', 'C) Repeating words', 'D) Using metaphors'],
          difficulty: 'easy',
          marks: 2,
        },
        {
          id: 2,
          text: 'Analyze the theme of sacrifice in the novel. Provide examples.',
          difficulty: 'hard',
          marks: 5,
        },
        {
          id: 3,
          text: 'Write a short essay on environmental conservation.',
          difficulty: 'medium',
          marks: 8,
        },
      ];
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      setQuestions(mockQuestions);
    } catch (err) {
      setError('Failed to generate question paper. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="student">
      <div className="student-header">
        <h1>Student Dashboard</h1>
        <p>Generate and practice question papers</p>
      </div>

      <div className="student-container">
        <div className="generator-section">
          <h2>Question Paper Generator</h2>
          <div className="generator-form">
            <div className="form-group">
              <label htmlFor="difficulty">Select Difficulty Level</label>
              <select id="difficulty">
                <option value="easy">Easy</option>
                <option value="medium" selected>Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="marks">Total Marks</label>
              <input type="number" id="marks" value="100" readOnly />
            </div>

            <div className="form-group">
              <label htmlFor="subject">Subject</label>
              <select id="subject">
                <option value="english">English</option>
                <option value="math">Mathematics</option>
                <option value="science">Science</option>
                <option value="history">History</option>
              </select>
            </div>

            <button 
              className="generate-btn" 
              onClick={handleGeneratePaper}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <FaSpinner className="spinner" />
                  Generating...
                </>
              ) : (
                'Generate Question Paper'
              )}
            </button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        {questions && (
          <div className="questions-section">
            <div className="questions-header">
              <h2>Generated Question Paper</h2>
              <div className="action-buttons">
                <button className="action-btn download-btn">
                  <FaDownload /> Download
                </button>
                <button className="action-btn print-btn">
                  <FaPrint /> Print
                </button>
              </div>
            </div>

            <div className="questions-list">
              {questions.map((question, index) => (
                <div key={question.id} className="question-card">
                  <div className="question-header">
                    <span className="question-number">Q{index + 1}</span>
                    <span className="difficulty-badge" data-difficulty={question.difficulty}>
                      {question.difficulty}
                    </span>
                    <span className="marks">{question.marks} marks</span>
                  </div>
                  <p className="question-text">{question.text}</p>
                  {question.options && (
                    <div className="options">
                      {question.options.map((option, idx) => (
                        <div key={idx} className="option">
                          <input type="radio" id={`q${question.id}-o${idx}`} name={`q${question.id}`} />
                          <label htmlFor={`q${question.id}-o${idx}`}>{option}</label>
                        </div>
                      ))}
                    </div>
                  )}
                  {!question.options && (
                    <textarea 
                      placeholder="Write your answer here..." 
                      rows="4"
                      className="answer-input"
                    ></textarea>
                  )}
                </div>
              ))}
            </div>

            <div className="submit-section">
              <button className="submit-btn">Submit Answers</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
