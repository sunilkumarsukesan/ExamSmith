import React, { useState } from 'react';
import './Teacher.css';
import { FaEye, FaEdit, FaTrash } from 'react-icons/fa';

export default function Teacher() {
  const [papers] = useState([
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

  return (
    <div className="teacher">
      <div className="teacher-header">
        <h1>Teacher Dashboard</h1>
        <p>Create and review question papers for your classes</p>
      </div>

      <div className="teacher-container">
        <div className="teacher-actions">
          <button className="create-btn">+ Create New Paper</button>
        </div>

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
