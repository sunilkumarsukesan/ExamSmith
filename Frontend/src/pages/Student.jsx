import React, { useState, useEffect, useCallback } from 'react';
import './Student.css';
import { 
  FaSpinner, FaDownload, FaPlay, FaClipboardList, 
  FaCheckCircle, FaTimesCircle, FaClock, FaPaperPlane,
  FaChartBar, FaEye, FaComments, FaRobot
} from 'react-icons/fa';
import { 
  getPipelinePapers, 
  getPaperForExam, 
  startExam, 
  submitExam, 
  getMyAttempts,
  getResult,
  downloadPaperPdf 
} from '../services/api';
import Chatbot from '../components/Chatbot';

export default function Student() {
  const [activeTab, setActiveTab] = useState('available'); // available, my-attempts, chat
  const [papers, setPapers] = useState([]);
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Exam state
  const [examMode, setExamMode] = useState(false);
  const [currentPaper, setCurrentPaper] = useState(null);
  const [currentAttempt, setCurrentAttempt] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  
  // Results state
  const [viewingResult, setViewingResult] = useState(null);
  
  // Chatbot state
  const [chatbotOpen, setChatbotOpen] = useState(false);
  const [selectedQuestionsForChat, setSelectedQuestionsForChat] = useState([]);
  const [questionSelections, setQuestionSelections] = useState({});

  // Fetch available papers
  const fetchPapers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getPipelinePapers();
      setPapers(data.papers || []);
    } catch (err) {
      console.error('Error fetching papers:', err);
      setError('Failed to load available exams');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch my attempts
  const fetchAttempts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getMyAttempts();
      setAttempts(data.attempts || []);
    } catch (err) {
      console.error('Error fetching attempts:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'available') {
      fetchPapers();
    } else if (activeTab === 'my-attempts') {
      fetchAttempts();
    }
  }, [activeTab, fetchPapers, fetchAttempts]);

  // Start an exam
  const handleStartExam = async (paper) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Starting exam for paper:', paper.paper_id);
      
      // Start the attempt
      const attemptData = await startExam(paper.paper_id);
      console.log('Attempt created:', attemptData);
      setCurrentAttempt(attemptData);
      
      // Get the paper questions
      const paperData = await getPaperForExam(paper.paper_id);
      console.log('Paper data received:', paperData);
      console.log('Questions count:', paperData.questions?.length);
      setCurrentPaper(paperData);
      
      // Initialize answers
      const initialAnswers = {};
      paperData.questions.forEach(q => {
        initialAnswers[q.question_id] = '';
      });
      setAnswers(initialAnswers);
      
      setExamMode(true);
    } catch (err) {
      console.error('Error starting exam:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to start exam';
      setError(errorMsg);
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // Handle answer change
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  // Submit exam
  const handleSubmitExam = async () => {
    if (!window.confirm('Are you sure you want to submit? You cannot change your answers after submission.')) {
      return;
    }
    
    try {
      setSubmitting(true);
      
      // Format answers for API
      const formattedAnswers = currentPaper.questions.map(q => {
        let student_answer = answers[q.question_id] || '';
        
        // For internal choice, include which option was selected
        if (q.internal_choice || q.question_type === 'INTERNAL_CHOICE') {
          const selectedChoice = answers[`${q.question_id}_choice`] || '';
          if (selectedChoice && student_answer) {
            student_answer = `[Choice ${String.fromCharCode(65 + parseInt(selectedChoice))}] ${student_answer}`;
          }
        }
        
        // Map question types to backend expected values
        let question_type = q.question_type;
        if (question_type === 'INTERNAL_CHOICE') {
          question_type = 'LONG_ANSWER';
        } else if (question_type === 'MEMORY') {
          question_type = 'LONG_ANSWER';
        }
        
        return {
          question_id: q.question_id || `q_${q.question_number}`,
          question_number: parseInt(q.question_number) || 0,
          question_type: question_type,
          student_answer: student_answer
        };
      });
      
      console.log('Submitting answers:', formattedAnswers);
      
      const result = await submitExam(currentAttempt.attempt_id, formattedAnswers);
      
      alert('Exam submitted successfully! Your score is being calculated.');
      
      // Exit exam mode and show results
      setExamMode(false);
      setCurrentPaper(null);
      setCurrentAttempt(null);
      setAnswers({});
      
      // Switch to results tab
      setActiveTab('my-attempts');
      fetchAttempts();
      
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit exam');
    } finally {
      setSubmitting(false);
    }
  };

  // View result details
  const handleViewResult = async (attemptId) => {
    console.log('🎯 handleViewResult called with attemptId:', attemptId);
    try {
      console.log('🎯 Fetching results for attempt:', attemptId);
      setLoading(true);
      setError(null);
      const result = await getResult(attemptId);
      console.log('✅ Result data received:', result);
      console.log('✅ Result summary:', result?.summary);
      console.log('✅ Question results count:', result?.question_results?.length);
      setViewingResult(result);
      console.log('✅ viewingResult state updated');
    } catch (err) {
      console.error('❌ Failed to load results:', err);
      console.error('❌ Error response:', err.response?.data);
      setError('Failed to load results: ' + (err.response?.data?.detail || err.message));
      alert('Failed to load results: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Download PDF
  const handleDownloadPdf = async (paperId, title) => {
    try {
      const blob = await downloadPaperPdf(paperId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${title.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to download PDF');
    }
  };

  // Render exam mode
  if (examMode && currentPaper) {
    // Check if questions exist
    if (!currentPaper.questions || currentPaper.questions.length === 0) {
      return (
        <div className="student exam-mode">
          <div className="exam-header">
            <h1>{currentPaper.title || 'Exam'}</h1>
          </div>
          <div className="exam-container">
            <div className="error-message">
              No questions found in this exam. Please contact your instructor.
            </div>
            <button onClick={() => setExamMode(false)}>Back to Papers</button>
          </div>
        </div>
      );
    }

    return (
      <div className="student exam-mode">
        <div className="exam-header">
          <h1>{currentPaper.title}</h1>
          <div className="exam-info">
            <span><FaClipboardList /> {currentPaper.total_questions} Questions</span>
            <span><FaChartBar /> {currentPaper.total_marks} Marks</span>
            <span><FaClock /> No Time Limit</span>
          </div>
        </div>
        
        <div className="exam-container">
          {currentPaper.instructions && (
            <div className="exam-instructions">
              <strong>Instructions:</strong> {currentPaper.instructions}
            </div>
          )}
          
          <div className="questions-list">
            {currentPaper.questions.map((question, index) => (
              <div key={question.question_id} className="exam-question">
                <div className="question-header">
                  <span className="question-number">Q{question.question_number || index + 1}</span>
                  <span className="question-marks">{question.marks} mark{question.marks > 1 ? 's' : ''}</span>
                  <span className={`question-type type-${question.question_type?.toLowerCase()}`}>
                    {question.question_type}
                  </span>
                </div>
                
                <div className="question-text">
                  {question.question_text}
                </div>
                
                <div className="answer-input">
                  {question.question_type === 'MCQ' && question.options && !question.internal_choice ? (
                    <div className="mcq-options">
                      {question.options.map((option, optIdx) => (
                        <label key={optIdx} className="mcq-option">
                          <input
                            type="radio"
                            name={`question-${question.question_id}`}
                            value={optIdx}
                            checked={answers[question.question_id] === String(optIdx)}
                            onChange={(e) => handleAnswerChange(question.question_id, e.target.value)}
                          />
                          <span className="option-letter">{String.fromCharCode(65 + optIdx)}</span>
                          <span className="option-text">{option}</span>
                        </label>
                      ))}
                    </div>
                  ) : question.internal_choice || question.question_type === 'INTERNAL_CHOICE' ? (
                    <div className="internal-choice-section">
                      <p className="choice-instruction">Choose ONE of the following questions to answer:</p>
                      {question.options && question.options.map((choice, choiceIdx) => (
                        <div key={choiceIdx} className="choice-option">
                          <div className="choice-header">
                            <input
                              type="radio"
                              name={`choice-${question.question_id}`}
                              value={choiceIdx}
                              checked={answers[`${question.question_id}_choice`] === String(choiceIdx)}
                              onChange={(e) => handleAnswerChange(`${question.question_id}_choice`, e.target.value)}
                            />
                            <strong>Option {choice.option_label || String.fromCharCode(65 + choiceIdx)}:</strong>
                          </div>
                          <div className="choice-question">
                            {choice.question_text || choice.text || JSON.stringify(choice)}
                          </div>
                        </div>
                      ))}
                      <textarea
                        className="text-answer"
                        placeholder="Write your answer for the chosen option here..."
                        value={answers[question.question_id] || ''}
                        onChange={(e) => handleAnswerChange(question.question_id, e.target.value)}
                        rows={8}
                      />
                    </div>
                  ) : (
                    <textarea
                      className="text-answer"
                      placeholder="Write your answer here..."
                      value={answers[question.question_id] || ''}
                      onChange={(e) => handleAnswerChange(question.question_id, e.target.value)}
                      rows={question.question_type === 'LONG_ANSWER' ? 8 : 4}
                    />
                  )}
                </div>
              </div>
            ))}
          </div>
          
          <div className="exam-actions">
            <button 
              className="submit-exam-btn"
              onClick={handleSubmitExam}
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <FaSpinner className="spin" /> Submitting...
                </>
              ) : (
                <>
                  <FaPaperPlane /> Submit Exam
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render result view
  if (viewingResult) {
    console.log('📊 Rendering result view with data:', viewingResult);
    return (
      <div className="student result-mode">
        <div className="result-header">
          <h1>Exam Results</h1>
          <button className="back-btn" onClick={() => setViewingResult(null)}>
            ← Back to Attempts
          </button>
        </div>
        
        <div className="result-container">
          <div className="result-summary">
            <h2>{viewingResult.paper_title || 'Exam Results'}</h2>
            <div className="score-card">
              <div className="score-main">
                <span className="score-value">{viewingResult.summary.percentage}%</span>
                <span className="score-label">Overall Score</span>
              </div>
              <div className="score-details">
                <div className="score-item">
                  <span className="label">MCQ Score:</span>
                  <span className="value">{viewingResult.summary.mcq_score} / {viewingResult.summary.mcq_total}</span>
                </div>
                <div className="score-item">
                  <span className="label">Descriptive Score:</span>
                  <span className="value">{viewingResult.summary.descriptive_score} / {viewingResult.summary.descriptive_total}</span>
                </div>
                <div className="score-item">
                  <span className="label">Total:</span>
                  <span className="value">{viewingResult.summary.final_score} / {viewingResult.summary.total_marks}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="question-results">
            <div className="question-results-header">
              <h3>Question-by-Question Analysis</h3>
              <button 
                className="chat-now-btn"
                onClick={() => {
                  const selected = viewingResult.question_results.filter(
                    (_, idx) => questionSelections[idx]
                  );
                  if (selected.length === 0) {
                    // If none selected, open chat without specific questions
                    setSelectedQuestionsForChat([]);
                  } else {
                    setSelectedQuestionsForChat(selected);
                  }
                  setChatbotOpen(true);
                }}
              >
                <FaComments /> {Object.values(questionSelections).filter(Boolean).length > 0 
                  ? `Chat About Selected (${Object.values(questionSelections).filter(Boolean).length})`
                  : 'Ask Tutor'}
              </button>
            </div>
            {viewingResult.question_results.map((qr, idx) => (
              <div key={idx} className={`question-result ${qr.is_correct ? 'correct' : qr.question_type === 'MCQ' ? 'incorrect' : ''}`}>
                <div className="qr-header">
                  <label className="qr-checkbox">
                    <input 
                      type="checkbox"
                      checked={questionSelections[idx] || false}
                      onChange={(e) => {
                        setQuestionSelections(prev => ({
                          ...prev,
                          [idx]: e.target.checked
                        }));
                      }}
                    />
                  </label>
                  <span className="qr-number">Q{qr.question_number}</span>
                  <span className="qr-type">{qr.question_type}</span>
                  <span className="qr-marks">
                    {qr.marks_awarded} / {qr.marks_possible}
                  </span>
                  {qr.question_type === 'MCQ' && (
                    <span className={`qr-status ${qr.is_correct ? 'correct' : 'incorrect'}`}>
                      {qr.is_correct ? <FaCheckCircle /> : <FaTimesCircle />}
                    </span>
                  )}
                </div>
                
                <div className="qr-question">{qr.question_text}</div>
                
                <div className="qr-comparison">
                  <div className="your-answer">
                    <strong>Your Answer:</strong>
                    <p>{qr.student_answer || '(No answer provided)'}</p>
                  </div>
                  <div className="correct-answer">
                    <strong>Correct Answer:</strong>
                    <p>{qr.correct_answer}</p>
                  </div>
                </div>
                
                {qr.feedback && (
                  <div className="qr-feedback">
                    <strong>Feedback:</strong> {qr.feedback}
                  </div>
                )}
                
                {qr.question_type === 'DESCRIPTIVE' && (
                  <div className="semantic-scores">
                    <span>Answer Key Match: {qr.answer_key_similarity}%</span>
                    <span>Textbook Match: {qr.textbook_similarity}%</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        
        {/* Chatbot for results */}
        <Chatbot 
          isOpen={chatbotOpen}
          onClose={() => {
            setChatbotOpen(false);
            setSelectedQuestionsForChat([]);
          }}
          selectedQuestions={selectedQuestionsForChat}
        />
      </div>
    );
  }

  // Main dashboard view
  return (
    <div className="student">
      <div className="student-header">
        <h1>Student Dashboard</h1>
        <p>Take exams and view your results</p>
      </div>

      <div className="student-container">
        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button
            className={`tab-btn ${activeTab === 'available' ? 'active' : ''}`}
            onClick={() => setActiveTab('available')}
          >
            <FaClipboardList /> Available Exams
          </button>
          <button
            className={`tab-btn ${activeTab === 'my-attempts' ? 'active' : ''}`}
            onClick={() => setActiveTab('my-attempts')}
          >
            <FaChartBar /> My Attempts
          </button>
          <button
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <FaRobot /> Ask Tutor
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading-state">
            <FaSpinner className="spin" />
            <p>Loading...</p>
          </div>
        ) : activeTab === 'available' ? (
          <div className="papers-grid">
            {papers.length === 0 ? (
              <div className="empty-state">
                <p>No exams available at the moment. Check back later!</p>
              </div>
            ) : (
              papers.map(paper => (
                <div key={paper.paper_id} className="paper-card">
                  <div className="paper-card-header">
                    <h3>{paper.title}</h3>
                    {paper.already_attempted && (
                      <span className="attempted-badge">Attempted</span>
                    )}
                  </div>
                  <div className="paper-card-body">
                    <p className="paper-description">{paper.description || 'Model question paper'}</p>
                    <div className="paper-meta">
                      <span><FaClipboardList /> {paper.total_questions} Questions</span>
                      <span><FaChartBar /> {paper.total_marks} Marks</span>
                      <span><FaClock /> {paper.duration_minutes ? `${paper.duration_minutes} min` : 'No limit'}</span>
                    </div>
                    <div className="paper-info">
                      <small>Published by: {paper.published_by_name || 'Instructor'}</small>
                    </div>
                  </div>
                  <div className="paper-card-actions">
                    {paper.already_attempted ? (
                      <button className="view-result-btn" onClick={() => {
                        setActiveTab('my-attempts');
                        fetchAttempts();
                      }}>
                        <FaEye /> View Result
                      </button>
                    ) : (
                      <button className="start-exam-btn" onClick={() => handleStartExam(paper)}>
                        <FaPlay /> Start Exam
                      </button>
                    )}
                    <button 
                      className="download-btn" 
                      onClick={() => handleDownloadPdf(paper.paper_id, paper.title)}
                    >
                      <FaDownload />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : activeTab === 'my-attempts' ? (
          <div className="attempts-list">
            {attempts.length === 0 ? (
              <div className="empty-state">
                <p>You haven't attempted any exams yet.</p>
              </div>
            ) : (
              <table className="attempts-table">
                <thead>
                  <tr>
                    <th>Paper</th>
                    <th>Status</th>
                    <th>Started</th>
                    <th>Submitted</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {attempts.map(attempt => (
                    <tr key={attempt.attempt_id}>
                      <td>{attempt.paper_title || attempt.paper_id}</td>
                      <td>
                        <span className={`status-badge status-${attempt.status}`}>
                          {attempt.status}
                        </span>
                      </td>
                      <td>{new Date(attempt.started_at).toLocaleString()}</td>
                      <td>{attempt.submitted_at ? new Date(attempt.submitted_at).toLocaleString() : '-'}</td>
                      <td>
                        {attempt.status === 'evaluated' && (
                          <button 
                            className="view-result-btn"
                            onClick={() => handleViewResult(attempt.attempt_id)}
                          >
                            <FaEye /> View Results
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        ) : activeTab === 'chat' ? (
          <div className="chat-tab-content">
            <div className="chat-intro">
              <div className="chat-intro-icon">
                <FaRobot />
              </div>
              <h2>English Learning Assistant</h2>
              <p>
                Ask me anything about your English textbook! I can help you understand 
                poems, prose, grammar, and answer any questions about your TN SSLC syllabus.
              </p>
              <button 
                className="start-chat-btn"
                onClick={() => {
                  setSelectedQuestionsForChat([]);
                  setChatbotOpen(true);
                }}
              >
                <FaComments /> Start Chatting
              </button>
            </div>
            
            <div className="chat-tips">
              <h3>💡 What can you ask?</h3>
              <ul>
                <li>Explain the meaning of a poem or prose passage</li>
                <li>Help me understand a grammar concept</li>
                <li>Why was my exam answer wrong?</li>
                <li>Give me examples of literary devices</li>
                <li>Summarize a chapter or story</li>
              </ul>
            </div>
          </div>
        ) : null}
      </div>
      
      {/* Chatbot Modal (for general chat from tab) */}
      {activeTab === 'chat' && (
        <Chatbot 
          isOpen={chatbotOpen}
          onClose={() => setChatbotOpen(false)}
          selectedQuestions={selectedQuestionsForChat}
        />
      )}
    </div>
  );
}
