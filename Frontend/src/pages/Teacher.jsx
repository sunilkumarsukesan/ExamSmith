import React, { useState } from 'react';
import './Teacher.css';
import { FaEye, FaEdit, FaTrash, FaSpinner } from 'react-icons/fa';
import { generateQuestionPaper } from '../services/api';
import QuestionPaper from '../components/QuestionPaper';

export default function Teacher() {
  const [papers, setPapers] = useState([
    {
      id: 1,
      title: 'English Mid-term Exam',
      subject: 'English',
      createdDate: '2025-01-15',
      totalQuestions: 15,
      totalMarks: 100,
      status: 'published',
    },
    {
      id: 2,
      title: 'Science Quiz',
      subject: 'Science',
      createdDate: '2025-01-18',
      totalQuestions: 20,
      totalMarks: 50,
      status: 'draft',
    },
    {
      id: 3,
      title: 'Math Finals',
      subject: 'Mathematics',
      createdDate: '2025-01-10',
      totalQuestions: 25,
      totalMarks: 100,
      status: 'published',
    },
  ]);

  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPaper, setGeneratedPaper] = useState(null);
  const [error, setError] = useState(null);

  const handleCreatePaper = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      console.log('Calling generateQuestionPaper API...');
      const response = await generateQuestionPaper({});
      console.log('API Response:', response);
      console.log('Response type:', typeof response);
      console.log('Has questions?', response?.questions);
      
      setGeneratedPaper(response);
      
      // Add to papers list
      const newPaper = {
        id: response.paper_id,
        title: `TN SSLC English Paper`,
        subject: 'English',
        createdDate: new Date().toISOString().split('T')[0],
        totalQuestions: response.questions?.length || 0,
        totalMarks: response.total_marks || 100,
        status: 'generated',
      };
      setPapers((prev) => [newPaper, ...prev]);
      console.log('Paper state updated successfully');
    } catch (err) {
      console.error('Error in handleCreatePaper:', err);
      console.error('Error response:', err.response);
      console.error('Error message:', err.message);
      setError(err.response?.data?.detail || err.message || 'Failed to generate question paper. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClosePaper = () => {
    setGeneratedPaper(null);
  };

  // Handler for when a question is revised (Human-in-the-Loop)
  const handleQuestionRevised = (questionNumber, revisedQuestion) => {
    console.log('=== handleQuestionRevised called ===');
    console.log('Question number:', questionNumber);
    console.log('Revised question:', revisedQuestion);
    console.log('Has image_url:', revisedQuestion?.image_url);
    console.log('Image topic:', revisedQuestion?.image_topic);
    
    if (!generatedPaper || !generatedPaper.questions) {
      console.log('No generated paper or questions!');
      return;
    }
    
    // Update the question in the generated paper
    const updatedQuestions = generatedPaper.questions.map(q => {
      if (q.question_number === questionNumber) {
        console.log('Found matching question, replacing with revised version');
        return { ...revisedQuestion, is_revised: true };
      }
      return q;
    });
    
    const newPaper = {
      ...generatedPaper,
      questions: updatedQuestions
    };
    
    console.log('Setting new paper state');
    console.log('Updated question 42:', updatedQuestions.find(q => q.question_number === 42));
    
    setGeneratedPaper(newPaper);
    
    console.log('Paper updated with revised question');
  };

  return (
    <div className="teacher">
      <div className="teacher-header">
        <h1>Teacher Dashboard</h1>
        <p>Create and review question papers for your classes</p>
      </div>

      <div className="teacher-container">
        <div className="teacher-actions">
          <button 
            className="create-btn" 
            onClick={handleCreatePaper}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <FaSpinner className="spinner-icon" />
                Generating Paper...
              </>
            ) : (
              '+ Create New Paper'
            )}
          </button>
          {error && <div className="error-message">{error}</div>}
        </div>

        {/* Question Paper Modal */}
        {generatedPaper && (
          <QuestionPaper 
            paper={generatedPaper} 
            onClose={handleClosePaper}
            onQuestionRevised={handleQuestionRevised}
          />
        )}

        <div className="papers-section">
          <h2>Your Question Papers</h2>
          <div className="papers-table-wrapper">
            <table className="papers-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Subject</th>
                  <th>Questions</th>
                  <th>Marks</th>
                  <th>Created Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {papers.map((paper) => (
                  <tr key={paper.id}>
                    <td className="paper-title">{paper.title}</td>
                    <td>{paper.subject}</td>
                    <td>{paper.totalQuestions}</td>
                    <td>{paper.totalMarks}</td>
                    <td>{new Date(paper.createdDate).toLocaleDateString()}</td>
                    <td>
                      <span className={`status-badge status-${paper.status}`}>
                        {paper.status}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <button className="action-icon view-btn" title="View">
                        <FaEye />
                      </button>
                      <button className="action-icon edit-btn" title="Edit">
                        <FaEdit />
                      </button>
                      <button className="action-icon delete-btn" title="Delete">
                        <FaTrash />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="stats-section">
          <h2>Quick Stats</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">3</div>
              <div className="stat-label">Total Papers</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">2</div>
              <div className="stat-label">Published</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">1</div>
              <div className="stat-label">Draft</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">60</div>
              <div className="stat-label">Total Questions</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
