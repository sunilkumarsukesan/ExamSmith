import React, { useState, useEffect, useCallback } from 'react';
import './Teacher.css';
import { FaEye, FaEdit, FaCheck, FaRocket, FaUndo, FaSpinner, FaDownload, FaBook } from 'react-icons/fa';
import { 
  generateQuestionPaper, 
  getInstructorPapers, 
  savePaper,
  approvePaper, 
  publishPaper, 
  unpublishPaper,
  downloadPaperPdf 
} from '../services/api';
import QuestionPaper from '../components/QuestionPaper';

export default function Teacher() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPaper, setGeneratedPaper] = useState(null);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(null); // paper_id being acted upon
  const [activeTab, setActiveTab] = useState('all'); // all, draft, approved, published

  // Fetch papers on mount
  const fetchPapers = useCallback(async () => {
    try {
      setLoading(true);
      const statusFilter = activeTab === 'all' ? null : activeTab.toUpperCase();
      const data = await getInstructorPapers(statusFilter);
      setPapers(data.papers || []);
    } catch (err) {
      console.error('Error fetching papers:', err);
      setError('Failed to load papers');
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchPapers();
  }, [fetchPapers]);

  const handleCreatePaper = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      console.log('Generating question paper...');
      const response = await generateQuestionPaper({});
      console.log('Generated paper:', response);
      
      // Save the generated paper
      const savedPaper = await savePaper(response);
      console.log('Saved paper:', savedPaper);
      
      setGeneratedPaper(response);
      
      // Refresh papers list
      fetchPapers();
    } catch (err) {
      console.error('Error generating paper:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to generate question paper');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClosePaper = () => {
    setGeneratedPaper(null);
  };

  const handleViewPaper = async (paper) => {
    // TODO: Fetch full paper details and show in modal
    console.log('View paper:', paper);
    setGeneratedPaper({
      paper_id: paper.paper_id,
      title: paper.title,
      questions: paper.questions || [],
      total_marks: paper.total_marks,
      status: paper.status
    });
  };

  const handleApprovePaper = async (paperId) => {
    try {
      setActionLoading(paperId);
      await approvePaper(paperId);
      fetchPapers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to approve paper');
    } finally {
      setActionLoading(null);
    }
  };

  const handlePublishPaper = async (paperId) => {
    try {
      setActionLoading(paperId);
      await publishPaper(paperId);
      alert('Paper published to student pipeline!');
      fetchPapers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to publish paper');
    } finally {
      setActionLoading(null);
    }
  };

  const handleUnpublishPaper = async (paperId) => {
    try {
      setActionLoading(paperId);
      await unpublishPaper(paperId);
      fetchPapers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to unpublish paper');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDownloadPdf = async (paperId, title) => {
    try {
      setActionLoading(paperId);
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
    } finally {
      setActionLoading(null);
    }
  };

  const handleQuestionRevised = (questionNumber, revisedQuestion) => {
    if (!generatedPaper || !generatedPaper.questions) return;
    
    const updatedQuestions = generatedPaper.questions.map(q => {
      if (q.question_number === questionNumber) {
        return { ...revisedQuestion, is_revised: true };
      }
      return q;
    });
    
    setGeneratedPaper({
      ...generatedPaper,
      questions: updatedQuestions
    });
  };

  const getStatusBadgeClass = (status) => {
    switch (status?.toUpperCase()) {
      case 'DRAFT': return 'status-draft';
      case 'REVISED': return 'status-revised';
      case 'APPROVED': return 'status-approved';
      case 'PUBLISHED': return 'status-published';
      default: return 'status-draft';
    }
  };

  const renderActionButtons = (paper) => {
    const status = paper.status?.toUpperCase();
    const isLoading = actionLoading === paper.paper_id;

    return (
      <div className="action-buttons">
        <button 
          className="action-icon view-btn" 
          title="View"
          onClick={() => handleViewPaper(paper)}
          disabled={isLoading}
        >
          <FaEye />
        </button>

        {/* Download PDF */}
        <button 
          className="action-icon download-btn" 
          title="Download PDF"
          onClick={() => handleDownloadPdf(paper.paper_id, paper.title)}
          disabled={isLoading}
        >
          <FaDownload />
        </button>

        {/* Approve Button - for DRAFT/REVISED papers */}
        {(status === 'DRAFT' || status === 'REVISED') && (
          <button 
            className="action-icon approve-btn" 
            title="Approve Paper"
            onClick={() => handleApprovePaper(paper.paper_id)}
            disabled={isLoading}
          >
            {isLoading ? <FaSpinner className="spin" /> : <FaCheck />}
          </button>
        )}

        {/* Publish Button - for APPROVED papers */}
        {status === 'APPROVED' && (
          <button 
            className="action-icon publish-btn" 
            title="Publish to Pipeline"
            onClick={() => handlePublishPaper(paper.paper_id)}
            disabled={isLoading}
          >
            {isLoading ? <FaSpinner className="spin" /> : <FaRocket />}
          </button>
        )}

        {/* Unpublish Button - for PUBLISHED papers */}
        {status === 'PUBLISHED' && (
          <button 
            className="action-icon unpublish-btn" 
            title="Unpublish"
            onClick={() => handleUnpublishPaper(paper.paper_id)}
            disabled={isLoading}
          >
            {isLoading ? <FaSpinner className="spin" /> : <FaUndo />}
          </button>
        )}
      </div>
    );
  };

  // Calculate stats
  const totalPapers = papers.length;
  const draftPapers = papers.filter(p => p.status === 'DRAFT' || p.status === 'REVISED').length;
  const approvedPapers = papers.filter(p => p.status === 'APPROVED').length;
  const publishedPapers = papers.filter(p => p.status === 'PUBLISHED').length;

  return (
    <div className="teacher">
      <div className="teacher-header">
        <h1>Instructor Dashboard</h1>
        <p>Create, review, and publish question papers for your students</p>
      </div>

      <div className="teacher-container">
        {/* Action Bar */}
        <div className="teacher-actions">
          <button 
            className="create-btn" 
            onClick={handleCreatePaper}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <FaSpinner className="spinner-icon spin" />
                Generating Paper...
              </>
            ) : (
              <>
                <FaBook /> Generate New Paper
              </>
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

        {/* Tab Navigation */}
        <div className="tab-navigation">
          {['all', 'draft', 'approved', 'published'].map(tab => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {tab === 'all' && ` (${totalPapers})`}
              {tab === 'draft' && ` (${draftPapers})`}
              {tab === 'approved' && ` (${approvedPapers})`}
              {tab === 'published' && ` (${publishedPapers})`}
            </button>
          ))}
        </div>

        {/* Papers Table */}
        <div className="papers-section">
          <h2>Your Question Papers</h2>
          
          {loading ? (
            <div className="loading-state">
              <FaSpinner className="spin" />
              <p>Loading papers...</p>
            </div>
          ) : papers.length === 0 ? (
            <div className="empty-state">
              <p>No papers found. Generate your first question paper!</p>
            </div>
          ) : (
            <div className="papers-table-wrapper">
              <table className="papers-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Questions</th>
                    <th>Marks</th>
                    <th>Created</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {papers.map((paper) => (
                    <tr key={paper.paper_id}>
                      <td className="paper-title">{paper.title}</td>
                      <td>{paper.questions?.length || 0}</td>
                      <td>{paper.total_marks || 100}</td>
                      <td>{new Date(paper.created_at).toLocaleDateString()}</td>
                      <td>
                        <span className={`status-badge ${getStatusBadgeClass(paper.status)}`}>
                          {paper.status}
                        </span>
                      </td>
                      <td className="actions-cell">
                        {renderActionButtons(paper)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Stats Section */}
        <div className="stats-section">
          <h2>Paper Pipeline</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{totalPapers}</div>
              <div className="stat-label">Total Papers</div>
            </div>
            <div className="stat-card draft">
              <div className="stat-value">{draftPapers}</div>
              <div className="stat-label">Drafts/Revised</div>
            </div>
            <div className="stat-card approved">
              <div className="stat-value">{approvedPapers}</div>
              <div className="stat-label">Approved</div>
            </div>
            <div className="stat-card published">
              <div className="stat-value">{publishedPapers}</div>
              <div className="stat-label">Published</div>
            </div>
          </div>
        </div>

        {/* Workflow Guide */}
        <div className="workflow-guide">
          <h3>Paper Workflow</h3>
          <div className="workflow-steps">
            <div className="workflow-step">
              <span className="step-number">1</span>
              <span className="step-label">Generate</span>
              <span className="step-desc">Create AI-generated paper</span>
            </div>
            <div className="workflow-arrow">→</div>
            <div className="workflow-step">
              <span className="step-number">2</span>
              <span className="step-label">Revise</span>
              <span className="step-desc">Edit questions (HITL)</span>
            </div>
            <div className="workflow-arrow">→</div>
            <div className="workflow-step">
              <span className="step-number">3</span>
              <span className="step-label">Approve</span>
              <span className="step-desc">Mark as ready</span>
            </div>
            <div className="workflow-arrow">→</div>
            <div className="workflow-step">
              <span className="step-number">4</span>
              <span className="step-label">Publish</span>
              <span className="step-desc">Available to students</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
