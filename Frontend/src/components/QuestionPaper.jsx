import React, { useState, useEffect } from 'react';
import './QuestionPaper.css';
import { reviseQuestion, getRevisionHistory, regenerateAllQuestions } from '../services/api';

/**
 * QuestionPaper Component
 * Renders a generated question paper in the TN SSLC English format
 * Includes Human-in-the-Loop revision capabilities
 */
export default function QuestionPaper({ paper, onClose, onQuestionRevised }) {
  const [revisionModal, setRevisionModal] = useState({ open: false, question: null });
  const [feedback, setFeedback] = useState('');
  const [isRevising, setIsRevising] = useState(false);
  const [revisionHistory, setRevisionHistory] = useState({});
  const [showHistory, setShowHistory] = useState({});
  const [regenerateModal, setRegenerateModal] = useState(false);
  const [regenerateFeedback, setRegenerateFeedback] = useState('');
  const [isRegeneratingAll, setIsRegeneratingAll] = useState(false);

  // Debug logging
  console.log('=== QuestionPaper Component Mount ===');
  console.log('Paper prop:', paper);

  // Load revision history on mount
  useEffect(() => {
    if (paper?.paper_id) {
      loadRevisionHistory();
    }
  }, [paper?.paper_id]);

  const loadRevisionHistory = async () => {
    try {
      const response = await getRevisionHistory(paper.paper_id);
      if (response.revisions) {
        // Group by question number
        const historyByQuestion = {};
        response.revisions.forEach(rev => {
          const qNum = rev.question_number;
          if (!historyByQuestion[qNum]) {
            historyByQuestion[qNum] = [];
          }
          historyByQuestion[qNum].push(rev);
        });
        setRevisionHistory(historyByQuestion);
      }
    } catch (error) {
      console.error("Error loading revision history:", error);
    }
  };

  if (!paper) {
    console.log('Paper is null/undefined, returning null');
    return null;
  }

  // Safely get questions array
  const questions = paper.questions || [];
  
  console.log('Questions count:', questions.length);

  // Handle empty questions
  if (questions.length === 0) {
    return (
      <div className="question-paper-overlay">
        <div className="question-paper-container">
          <div className="paper-header">
            <button className="close-btn" onClick={onClose}>×</button>
            <div className="paper-title-section">
              <h1>Question Paper Generated</h1>
              <h2>Paper ID: {paper.paper_id}</h2>
            </div>
          </div>
          <div className="paper-body" style={{ padding: '2rem', textAlign: 'center' }}>
            <p>No questions were returned from the API.</p>
            <p>Status: {paper.status}</p>
            <pre style={{ textAlign: 'left', background: '#f5f5f5', padding: '1rem', borderRadius: '8px', overflow: 'auto' }}>
              {JSON.stringify(paper, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    );
  }

  // Handle opening revision modal
  const handleReviseClick = (question) => {
    setRevisionModal({ open: true, question });
    setFeedback('');
  };

  // Handle submitting revision
  const handleReviseSubmit = async () => {
    if (!feedback.trim()) return;
    
    setIsRevising(true);
    try {
      console.log('=== Submitting revision ===');
      console.log('Original question:', revisionModal.question);
      console.log('Feedback:', feedback);
      console.log('Paper ID:', paper.paper_id);
      
      const response = await reviseQuestion({
        original_question: revisionModal.question,
        teacher_feedback: feedback,
        paper_id: paper.paper_id
      });

      console.log('=== Revision response ===');
      console.log('Full response:', response);
      console.log('Success:', response.success);
      console.log('Revised question:', response.revised_question);
      console.log('Has image_url:', response.revised_question?.image_url);

      if (response.success && response.revised_question) {
        // Notify parent to update the question
        if (onQuestionRevised) {
          console.log('Calling onQuestionRevised with:', revisionModal.question.question_number, response.revised_question);
          onQuestionRevised(revisionModal.question.question_number, response.revised_question);
        }
        // Reload history
        await loadRevisionHistory();
        setRevisionModal({ open: false, question: null });
        setFeedback('');
      } else {
        alert(response.message || "Failed to revise question");
      }
    } catch (error) {
      console.error("Error revising question:", error);
      alert("Error revising question. Please try again.");
    } finally {
      setIsRevising(false);
    }
  };

  // Handle regenerate all
  const handleRegenerateAll = async () => {
    if (!regenerateFeedback.trim()) return;
    
    setIsRegeneratingAll(true);
    try {
      const response = await regenerateAllQuestions({
        paper_id: paper.paper_id,
        questions: questions,
        teacher_feedback: regenerateFeedback
      });

      if (response.success && response.questions) {
        // Notify parent to update all questions
        if (onQuestionRevised) {
          response.questions.forEach(q => {
            onQuestionRevised(q.question_number, q);
          });
        }
        await loadRevisionHistory();
        setRegenerateModal(false);
        setRegenerateFeedback('');
        alert(`Successfully regenerated ${response.questions.length} questions!`);
      } else {
        alert(response.message || "Failed to regenerate questions");
      }
    } catch (error) {
      console.error("Error regenerating all:", error);
      alert("Error regenerating questions. Please try again.");
    } finally {
      setIsRegeneratingAll(false);
    }
  };

  // Toggle history for a question
  const toggleHistory = (questionNumber) => {
    setShowHistory(prev => ({
      ...prev,
      [questionNumber]: !prev[questionNumber]
    }));
  };

  // Group questions by part and section
  const groupedQuestions = {};
  try {
    questions.forEach((q) => {
      if (!q || !q.part) {
        console.warn('Question missing part field:', q);
        return;
      }
      const partKey = `Part ${q.part}`;
      if (!groupedQuestions[partKey]) {
        groupedQuestions[partKey] = {};
      }
      const sectionKey = q.section || 'General';
      if (!groupedQuestions[partKey][sectionKey]) {
        groupedQuestions[partKey][sectionKey] = [];
      }
      groupedQuestions[partKey][sectionKey].push(q);
    });
    console.log('Grouped questions:', groupedQuestions);
  } catch (err) {
    console.error('Error grouping questions:', err);
  }

  // Part metadata for display
  const partMeta = {
    'Part I': {
      title: 'PART – I',
      marks: '(14 × 1 = 14 marks)',
      description: 'Objective Type – Multiple Choice Questions',
      note: 'Answer all questions (1 to 14)',
    },
    'Part II': {
      title: 'PART – II',
      marks: '(10 × 2 = 20 marks)',
      description: 'Short Answer Questions',
      note: 'Answer any THREE out of FOUR questions in each section',
    },
    'Part III': {
      title: 'PART – III',
      marks: '(10 × 5 = 50 marks)',
      description: 'Paragraph / Detailed Answer Questions',
      note: 'Answer as per instructions in each section',
    },
    'Part IV': {
      title: 'PART – IV',
      marks: '(2 × 8 = 16 marks)',
      description: 'Comprehension / Developing Hints',
      note: 'Internal choice available',
    },
  };

  // Render options (handles both string and object formats)
  const renderOptions = (options) => {
    if (!options || !Array.isArray(options) || options.length === 0) return null;
    
    return (
      <div className="question-options">
        {options.map((opt, optIdx) => (
          <div key={optIdx} className="option-item">
            {typeof opt === 'string' 
              ? opt 
              : opt.option_label 
                ? `${opt.option_label}) ${opt.question_text || opt.text || ''}` 
                : JSON.stringify(opt)
            }
          </div>
        ))}
      </div>
    );
  };

  // Render internal choice
  const renderInternalChoice = (choice) => {
    if (!choice) return null;
    
    if (choice === true || typeof choice === 'boolean') {
      return <div className="internal-choice-badge">OR (Internal Choice)</div>;
    }
    
    if (typeof choice === 'object') {
      if (Array.isArray(choice)) {
        return (
          <div className="internal-choice-section">
            <div className="choice-label">OR</div>
            {choice.map((opt, idx) => (
              <div key={idx} className="choice-option">
                <strong>{opt.option_label || String.fromCharCode(65 + idx)})</strong> {opt.question_text || ''}
                {opt.lesson_type && <span className="lesson-tag"> ({opt.lesson_type})</span>}
              </div>
            ))}
          </div>
        );
      } else {
        return (
          <div className="internal-choice-section">
            <div className="choice-label">OR</div>
            <div className="choice-option">
              <strong>{choice.option_label})</strong> {choice.question_text || ''}
            </div>
          </div>
        );
      }
    }
    
    return null;
  };

  return (
    <div className="question-paper-overlay">
      <div className="question-paper-container">
        {/* Header */}
        <div className="paper-header">
          <div className="header-actions">
            <button 
              className="regenerate-all-btn"
              onClick={() => setRegenerateModal(true)}
              title="Regenerate all questions with feedback"
            >
              🔄 Regenerate All
            </button>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          <div className="paper-title-section">
            <h1>TN SSLC ENGLISH LANGUAGE – PAPER I</h1>
            <h2>Model Question Paper</h2>
            <div className="paper-meta">
              <span>Paper ID: {paper.paper_id?.substring(0, 8)}...</span>
              <span>Total Marks: {paper.total_marks || 100}</span>
              <span>Time: {paper.estimated_time_minutes || 180} minutes</span>
            </div>
          </div>
          <div className="paper-instructions">
            <h3>General Instructions:</h3>
            <ul>
              <li>Answer all the questions as per instructions given in each part.</li>
              <li>Write the correct option for objective type questions.</li>
              <li>Click "✏️ Revise" on any question to provide feedback and regenerate it.</li>
            </ul>
          </div>
        </div>

        {/* Paper Body */}
        <div className="paper-body">
          {Object.entries(groupedQuestions).map(([partName, sections]) => {
            const meta = partMeta[partName] || { title: partName, marks: '', description: '', note: '' };
            
            return (
              <div key={partName} className="paper-part">
                <div className="part-header">
                  <h2>{meta.title} {meta.marks}</h2>
                  <p className="part-description">{meta.description}</p>
                  <p className="part-note">{meta.note}</p>
                </div>

                {Object.entries(sections).map(([sectionName, sectionQuestions]) => (
                  <div key={sectionName} className="paper-section">
                    <div className="section-header">
                      <h3>SECTION: {sectionName.toUpperCase()}</h3>
                    </div>

                    <div className="questions-list">
                      {sectionQuestions.map((q, idx) => (
                        <div key={idx} className={`question-item ${q.is_revised ? 'revised' : ''}`}>
                          <div className="question-header">
                            <span className="question-number">Q{q.question_number}.</span>
                            <span className="question-marks">({q.marks} {q.marks === 1 ? 'mark' : 'marks'})</span>
                            
                            {/* Revise button */}
                            <button 
                              className="revise-btn"
                              onClick={() => handleReviseClick(q)}
                              title="Revise this question"
                            >
                              ✏️ Revise
                            </button>
                            
                            {/* History toggle */}
                            {revisionHistory[q.question_number]?.length > 0 && (
                              <button 
                                className="history-btn"
                                onClick={() => toggleHistory(q.question_number)}
                                title="View revision history"
                              >
                                📜 History ({revisionHistory[q.question_number].length})
                              </button>
                            )}
                            
                            {q.is_revised && (
                              <span className="revised-badge">Revised</span>
                            )}
                          </div>
                          
                          <div className="question-text">{q.question_text}</div>
                          
                          {/* Image for picture-based questions (Q42) */}
                          {q.image_url && (
                            <div className="question-image-container">
                              <img 
                                src={q.image_url} 
                                alt={q.image_description || "Question image"} 
                                className="question-image"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.nextSibling.style.display = 'block';
                                }}
                              />
                              <div className="image-fallback" style={{ display: 'none' }}>
                                <p>📷 [Image: {q.image_topic || 'Educational topic'}]</p>
                                <p className="image-description">{q.image_description}</p>
                              </div>
                              {q.image_topic && (
                                <div className="image-caption">
                                  <span className="topic-badge">🖼️ Topic: {q.image_topic}</span>
                                </div>
                              )}
                            </div>
                          )}
                          
                          {renderOptions(q.options)}
                          {renderInternalChoice(q.internal_choice)}

                          {/* Unit/Lesson info */}
                          {q.unit_name && (
                            <div className="question-meta">
                              <span className="unit-tag">{q.unit_name}</span>
                              {q.lesson_type && <span className="lesson-tag">{q.lesson_type}</span>}
                            </div>
                          )}
                          
                          {/* Revision History Panel */}
                          {showHistory[q.question_number] && revisionHistory[q.question_number] && (
                            <div className="revision-history-panel">
                              <h5>📜 Revision History</h5>
                              {revisionHistory[q.question_number].map((rev, revIdx) => (
                                <div key={rev.revision_id || revIdx} className="revision-item">
                                  <div className="revision-meta">
                                    <span className="revision-time">
                                      {new Date(rev.timestamp).toLocaleString()}
                                    </span>
                                    <span className="revision-feedback">
                                      Feedback: "{rev.teacher_feedback}"
                                    </span>
                                  </div>
                                  <div className="revision-comparison">
                                    <div className="original">
                                      <strong>Original:</strong>
                                      <p>{rev.original_question?.question_text}</p>
                                    </div>
                                    <div className="revised">
                                      <strong>Revised:</strong>
                                      <p>{rev.revised_question?.question_text}</p>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="paper-footer">
          <p>— End of Question Paper —</p>
          <div className="paper-actions">
            <button className="print-btn" onClick={() => window.print()}>🖨️ Print Paper</button>
            <button className="download-btn" onClick={() => alert('Download PDF coming soon!')}>📥 Download PDF</button>
          </div>
        </div>
      </div>

      {/* Revision Modal */}
      {revisionModal.open && (
        <div className="revision-modal-overlay" onClick={() => !isRevising && setRevisionModal({ open: false, question: null })}>
          <div className="revision-modal" onClick={e => e.stopPropagation()}>
            <h3>✏️ Revise Question {revisionModal.question?.question_number}</h3>
            
            <div className="current-question">
              <h4>Current Question:</h4>
              <p>{revisionModal.question?.question_text}</p>
              <div className="question-meta-modal">
                <span>Part: {revisionModal.question?.part}</span>
                <span>Section: {revisionModal.question?.section}</span>
                <span>Unit: {revisionModal.question?.unit_name || 'Not specified'}</span>
                <span>Marks: {revisionModal.question?.marks}</span>
              </div>
            </div>
            
            <div className="feedback-section">
              <label>Your Feedback / Instructions:</label>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Examples:
• 'Make this question easier'
• 'Use Unit 3 content instead'
• 'Focus on grammar rules'
• 'Generate from a different poem'
• 'Make it more challenging'
• 'Use vocabulary from prose lesson 2'"
                rows={5}
                disabled={isRevising}
              />
            </div>
            
            <div className="modal-actions">
              <button 
                className="cancel-btn"
                onClick={() => setRevisionModal({ open: false, question: null })}
                disabled={isRevising}
              >
                Cancel
              </button>
              <button 
                className="submit-btn"
                onClick={handleReviseSubmit}
                disabled={isRevising || !feedback.trim()}
              >
                {isRevising ? '🔄 Revising...' : '✨ Revise Question'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Regenerate All Modal */}
      {regenerateModal && (
        <div className="revision-modal-overlay" onClick={() => !isRegeneratingAll && setRegenerateModal(false)}>
          <div className="revision-modal" onClick={e => e.stopPropagation()}>
            <h3>🔄 Regenerate All Questions</h3>
            
            <p className="warning-text">
              ⚠️ This will regenerate all {questions.length} questions based on your feedback.
              This operation may take several minutes.
            </p>
            
            <div className="feedback-section">
              <label>Global Feedback / Instructions:</label>
              <textarea
                value={regenerateFeedback}
                onChange={(e) => setRegenerateFeedback(e.target.value)}
                placeholder="Examples:
• 'Make all questions slightly harder'
• 'Focus more on poetry sections'
• 'Include more grammar-based questions'
• 'Use content from Units 5-7 more'
• 'Reduce difficulty for slow learners'"
                rows={5}
                disabled={isRegeneratingAll}
              />
            </div>
            
            <div className="modal-actions">
              <button 
                className="cancel-btn"
                onClick={() => setRegenerateModal(false)}
                disabled={isRegeneratingAll}
              >
                Cancel
              </button>
              <button 
                className="submit-btn warning"
                onClick={handleRegenerateAll}
                disabled={isRegeneratingAll || !regenerateFeedback.trim()}
              >
                {isRegeneratingAll ? '🔄 Regenerating All...' : '✨ Regenerate All Questions'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
