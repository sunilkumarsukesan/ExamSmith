import React, { useState, useEffect, useCallback } from 'react';
import './Teacher.css';
import { FaEye, FaEdit, FaCheck, FaRocket, FaUndo, FaSpinner, FaDownload, FaBook, FaPlus, FaChartLine, FaUsers, FaClipboardList } from 'react-icons/fa';
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

  // Teacher stats (could be fetched from API in future)
  const [teacherStats] = useState({
    studentsReached: 156,
    avgImprovement: 18,
    papersThisMonth: 8,
    pendingReviews: 3
  });

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
          style={{ background: '#10b981', color: '#ffffff', fontSize: '1rem', fontWeight: 'bold' }}
        >
          ⬇
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
      {/* Productivity-Focused Header */}
      <div className="teacher-header">
        <div className="header-content">
          <div className="header-left">
            <div className="greeting-section">
              <span className="greeting-emoji">👨‍🏫</span>
              <div className="greeting-text">
                <h1>Instructor Command Center</h1>
                <p className="subtitle">Create quality assessments in minutes, not hours</p>
              </div>
            </div>
          </div>
          <div className="header-right">
            <div className="impact-badge">
              <FaUsers className="impact-icon" />
              <span className="impact-count">{teacherStats.studentsReached}</span>
              <span className="impact-label">Students Helped</span>
            </div>
          </div>
        </div>
        
        {/* Productivity Stats Bar */}
        <div className="stats-bar">
          <div className="stat-item">
            <span className="stat-icon">📄</span>
            <span className="stat-value">{totalPapers}</span>
            <span className="stat-label">Total Papers</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">📈</span>
            <span className="stat-value">+{teacherStats.avgImprovement}%</span>
            <span className="stat-label">Avg Improvement</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🚀</span>
            <span className="stat-value">{publishedPapers}</span>
            <span className="stat-label">Published</span>
          </div>
          <div className="stat-item highlight">
            <span className="stat-icon">⏰</span>
            <span className="stat-value">{teacherStats.pendingReviews}</span>
            <span className="stat-label">Pending Review</span>
          </div>
        </div>
      </div>

      <div className="teacher-container">
        {/* Quick Action Card */}
        <div className="quick-action-card">
          <div className="action-content">
            <div className="action-info">
              <h2><FaPlus /> Create New Assessment</h2>
              <p>AI generates curriculum-aligned questions instantly. Review, customize, and publish!</p>
            </div>
            <button 
              className="create-btn" 
              onClick={handleCreatePaper}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <FaSpinner className="spinner-icon spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FaBook /> Generate Paper
                </>
              )}
            </button>
          </div>
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

        {/* Papers Management Section */}
        <div className="papers-management">
          <div className="section-header">
            <h2><FaClipboardList /> Your Assessments</h2>
            <p className="section-subtitle">Manage your question papers through the review pipeline</p>
          </div>

          {/* Tab Navigation */}
          <div className="tab-navigation">
            {['all', 'draft', 'approved', 'published'].map(tab => (
              <button
                key={tab}
                className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab === 'all' && '📋 '}
                {tab === 'draft' && '✏️ '}
                {tab === 'approved' && '✅ '}
                {tab === 'published' && '🚀 '}
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
                <span className="tab-count">
                  {tab === 'all' && totalPapers}
                  {tab === 'draft' && draftPapers}
                  {tab === 'approved' && approvedPapers}
                  {tab === 'published' && publishedPapers}
                </span>
              </button>
            ))}
          </div>

          {/* Papers Table */}
          <div className="papers-section">
            {loading ? (
              <div className="loading-state">
                <FaSpinner className="spin" />
                <p>Loading your assessments...</p>
              </div>
            ) : papers.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📝</span>
                <h3>No assessments yet</h3>
                <p>Generate your first AI-powered question paper!</p>
                <button className="start-now-btn" onClick={handleCreatePaper}>
                  <FaPlus /> Create First Paper
                </button>
              </div>
            ) : (
              <div className="papers-grid">
                {papers.map((paper) => (
                  <div key={paper.paper_id} className={`paper-card status-${paper.status?.toLowerCase()}`}>
                    <div className="paper-card-header">
                      <h3>{paper.title}</h3>
                      <span className={`status-badge ${getStatusBadgeClass(paper.status)}`}>
                        {paper.status === 'DRAFT' && '✏️ '}
                        {paper.status === 'REVISED' && '🔄 '}
                        {paper.status === 'APPROVED' && '✅ '}
                        {paper.status === 'PUBLISHED' && '🚀 '}
                        {paper.status}
                      </span>
                    </div>
                    <div className="paper-card-body">
                      <div className="paper-meta">
                        <span className="meta-item">
                          <FaClipboardList /> {paper.questions?.length || 0} Questions
                        </span>
                        <span className="meta-item">
                          ⭐ {paper.total_marks || 100} Marks
                        </span>
                      </div>
                      <div className="paper-date">
                        Created: {new Date(paper.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="paper-card-actions">
                      {renderActionButtons(paper)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Workflow Guide */}
        <div className="workflow-guide">
          <h3>📋 Assessment Workflow</h3>
          <div className="workflow-steps">
            <div className="workflow-step">
              <span className="step-number">1</span>
              <span className="step-icon">🤖</span>
              <span className="step-label">Generate</span>
              <span className="step-desc">AI creates questions</span>
            </div>
            <div className="workflow-arrow">→</div>
            <div className="workflow-step">
              <span className="step-number">2</span>
              <span className="step-icon">✏️</span>
              <span className="step-label">Review</span>
              <span className="step-desc">Edit & customize</span>
            </div>
            <div className="workflow-arrow">→</div>
            <div className="workflow-step">
              <span className="step-number">3</span>
              <span className="step-icon">✅</span>
              <span className="step-label">Approve</span>
              <span className="step-desc">Mark ready</span>
            </div>
            <div className="workflow-arrow">→</div>
            <div className="workflow-step">
              <span className="step-number">4</span>
              <span className="step-icon">🚀</span>
              <span className="step-label">Publish</span>
              <span className="step-desc">Live for students</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
