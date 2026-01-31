import React, { useState, useEffect } from 'react';
import './Admin.css';
import { FaUser, FaEdit, FaTrash, FaLock, FaCog, FaTimes, FaCheck } from 'react-icons/fa';
import { listUsers, createUser, disableUser, enableUser } from '../services/api';

export default function Admin() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('users');
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState(null);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    password: '',
    role: 'STUDENT'
  });

  // Fetch users on mount
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listUsers();
      setUsers(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setModalLoading(true);
    setModalError(null);

    try {
      await createUser(newUser);
      setShowModal(false);
      setNewUser({ name: '', email: '', password: '', role: 'STUDENT' });
      fetchUsers(); // Refresh list
    } catch (err) {
      setModalError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setModalLoading(false);
    }
  };

  const handleToggleUserStatus = async (user) => {
    try {
      if (user.status === 'ACTIVE') {
        await disableUser(user.user_id);
      } else {
        await enableUser(user.user_id);
      }
      fetchUsers(); // Refresh list
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update user status');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewUser({ ...newUser, [name]: value });
  };

  // Calculate stats
  const totalUsers = users.length;
  const instructors = users.filter(u => u.role === 'INSTRUCTOR').length;
  const students = users.filter(u => u.role === 'STUDENT').length;
  const admins = users.filter(u => u.role === 'ADMIN').length;
  const activeUsers = users.filter(u => u.status === 'ACTIVE').length;

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
              <button className="add-user-btn" onClick={() => setShowModal(true)}>
                + Add New User
              </button>
            </div>

            {error && (
              <div className="error-banner">
                {error}
                <button onClick={fetchUsers}>Retry</button>
              </div>
            )}

            {loading ? (
              <div className="loading-state">Loading users...</div>
            ) : (
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
                    {users.length === 0 ? (
                      <tr>
                        <td colSpan="5" style={{ textAlign: 'center', padding: '2rem' }}>
                          No users found
                        </td>
                      </tr>
                    ) : (
                      users.map((user) => (
                        <tr key={user.user_id}>
                          <td className="user-name">{user.name}</td>
                          <td>{user.email}</td>
                          <td>
                            <span className={`role-badge role-${user.role.toLowerCase()}`}>
                              {user.role}
                            </span>
                          </td>
                          <td>
                            <span className={`status-badge status-${user.status.toLowerCase()}`}>
                              {user.status}
                            </span>
                          </td>
                          <td className="actions-cell">
                            <button 
                              className={`action-icon ${user.status === 'ACTIVE' ? 'delete-btn' : 'edit-btn'}`}
                              onClick={() => handleToggleUserStatus(user)}
                              title={user.status === 'ACTIVE' ? 'Disable User' : 'Enable User'}
                            >
                              {user.status === 'ACTIVE' ? <FaLock /> : <FaCheck />}
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="tab-content">
            <h2>System Settings</h2>
            <div className="settings-grid">
              <div className="setting-item">
                <h3>Platform Name</h3>
                <input type="text" defaultValue="ExamSmith" />
              </div>
              <div className="setting-item">
                <h3>Max Questions per Paper</h3>
                <input type="number" defaultValue="100" />
              </div>
              <div className="setting-item">
                <h3>Default Language</h3>
                <select defaultValue="English">
                  <option>English</option>
                  <option>Tamil</option>
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
                <input type="number" defaultValue="30" />
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
              <div className="stat-value">{totalUsers}</div>
              <div className="stat-label">Total Users</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{admins}</div>
              <div className="stat-label">Admins</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{instructors}</div>
              <div className="stat-label">Instructors</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{students}</div>
              <div className="stat-label">Students</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{activeUsers}</div>
              <div className="stat-label">Active Users</div>
            </div>
          </div>
        </div>
      </div>

      {/* Add User Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add New User</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <FaTimes />
              </button>
            </div>
            
            <form onSubmit={handleCreateUser}>
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={newUser.name}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter full name"
                  disabled={modalLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={newUser.email}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter email address"
                  disabled={modalLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password *</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={newUser.password}
                  onChange={handleInputChange}
                  required
                  minLength={8}
                  placeholder="Enter password (min 8 characters)"
                  disabled={modalLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="role">Role *</label>
                <select
                  id="role"
                  name="role"
                  value={newUser.role}
                  onChange={handleInputChange}
                  required
                  disabled={modalLoading}
                >
                  <option value="STUDENT">Student</option>
                  <option value="INSTRUCTOR">Instructor</option>
                  <option value="ADMIN">Admin</option>
                </select>
              </div>

              {modalError && (
                <div className="modal-error">
                  {modalError}
                </div>
              )}

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="cancel-btn"
                  onClick={() => setShowModal(false)}
                  disabled={modalLoading}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="submit-btn"
                  disabled={modalLoading}
                >
                  {modalLoading ? 'Creating...' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
