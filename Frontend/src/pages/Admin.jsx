import React, { useState } from 'react';
import './Admin.css';
import { FaUser, FaEdit, FaTrash, FaLock, FaCog } from 'react-icons/fa';

export default function Admin() {
  const [users] = useState([
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'student', status: 'active' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'teacher', status: 'active' },
    { id: 3, name: 'Mike Johnson', email: 'mike@example.com', role: 'student', status: 'inactive' },
    { id: 4, name: 'Sarah Williams', email: 'sarah@example.com', role: 'teacher', status: 'active' },
  ]);

  const [activeTab, setActiveTab] = useState('users');

  return (
    <div className="admin">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <p>Manage users and system configuration</p>
      </div>

      <div className="admin-container">
        <div className="admin-tabs">
          <button 
            className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            <FaUser /> User Management
          </button>
          <button 
            className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <FaCog /> System Settings
          </button>
          <button 
            className={`tab-btn ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            <FaLock /> Security
          </button>
        </div>

        {activeTab === 'users' && (
          <div className="tab-content">
            <div className="section-header">
              <h2>User Management</h2>
              <button className="add-user-btn">+ Add New User</button>
            </div>

            <div className="users-table-wrapper">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="user-name">{user.name}</td>
                      <td>{user.email}</td>
                      <td>
                        <span className={`role-badge role-${user.role}`}>
                          {user.role}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge status-${user.status}`}>
                          {user.status}
                        </span>
                      </td>
                      <td className="actions-cell">
                        <button className="action-icon edit-btn">
                          <FaEdit />
                        </button>
                        <button className="action-icon delete-btn">
                          <FaTrash />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="tab-content">
            <h2>System Settings</h2>
            <div className="settings-grid">
              <div className="setting-item">
                <h3>Platform Name</h3>
                <input type="text" value="ExamSmith" />
              </div>
              <div className="setting-item">
                <h3>Max Questions per Paper</h3>
                <input type="number" value="100" />
              </div>
              <div className="setting-item">
                <h3>Default Language</h3>
                <select>
                  <option>English</option>
                  <option>Spanish</option>
                  <option>French</option>
                </select>
              </div>
              <div className="setting-item">
                <h3>Maintenance Mode</h3>
                <input type="checkbox" />
              </div>
            </div>
            <button className="save-settings-btn">Save Settings</button>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="tab-content">
            <h2>Security Settings</h2>
            <div className="security-items">
              <div className="security-item">
                <h3>Enable Two-Factor Authentication</h3>
                <p>Enhance account security with 2FA</p>
                <input type="checkbox" defaultChecked />
              </div>
              <div className="security-item">
                <h3>Password Policy</h3>
                <p>Enforce strong password requirements</p>
                <input type="checkbox" defaultChecked />
              </div>
              <div className="security-item">
                <h3>Session Timeout (minutes)</h3>
                <input type="number" value="30" />
              </div>
              <div className="security-item">
                <h3>IP Whitelist</h3>
                <textarea placeholder="Enter IP addresses (one per line)" rows="4"></textarea>
              </div>
            </div>
            <button className="save-settings-btn">Save Security Settings</button>
          </div>
        )}

        <div className="stats-section">
          <h2>System Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">4</div>
              <div className="stat-label">Total Users</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">2</div>
              <div className="stat-label">Teachers</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">2</div>
              <div className="stat-label">Students</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">3</div>
              <div className="stat-label">Active Users</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
