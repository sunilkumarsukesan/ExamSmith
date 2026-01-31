import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister, getCurrentUser, refreshToken } from '../services/api';

// Auth Context
const AuthContext = createContext(null);

// Token storage keys
const TOKEN_KEY = 'examsmith_token';
const USER_KEY = 'examsmith_user';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);
    
    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        // Verify token is still valid
        verifyToken(storedToken);
      } catch (e) {
        console.error('Error parsing stored user:', e);
        logout();
      }
    }
    setLoading(false);
  }, []);

  // Verify token on mount
  const verifyToken = async (tokenToVerify) => {
    try {
      const userData = await getCurrentUser(tokenToVerify);
      setUser(userData);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
    } catch (e) {
      console.error('Token verification failed:', e);
      logout();
    }
  };

  // Login
  const login = async (email, password) => {
    setError(null);
    try {
      const response = await apiLogin(email, password);
      const { user: userData, token: tokenData } = response;
      
      setToken(tokenData.access_token);
      setUser(userData);
      
      localStorage.setItem(TOKEN_KEY, tokenData.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
      
      return { success: true, user: userData };
    } catch (e) {
      const errorMessage = e.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Register
  const register = async (name, email, password) => {
    setError(null);
    try {
      const userData = await apiRegister(name, email, password);
      return { success: true, user: userData };
    } catch (e) {
      const errorMessage = e.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Logout
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  // Check role
  const hasRole = (requiredRoles) => {
    if (!user) return false;
    if (typeof requiredRoles === 'string') {
      return user.role === requiredRoles;
    }
    return requiredRoles.includes(user.role);
  };

  // Check if authenticated
  const isAuthenticated = !!token && !!user;

  // Check specific roles
  const isAdmin = user?.role === 'ADMIN';
  const isInstructor = user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN';
  const isStudent = !!user; // Any authenticated user can access student features

  const value = {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isInstructor,
    isStudent,
    login,
    register,
    logout,
    hasRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Protected Route Component
export function ProtectedRoute({ children, requiredRoles = null }) {
  const { isAuthenticated, hasRole, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!isAuthenticated) {
    // Redirect to login
    window.location.href = '/signin';
    return null;
  }

  if (requiredRoles && !hasRole(requiredRoles)) {
    return (
      <div className="access-denied">
        <h2>Access Denied</h2>
        <p>You don't have permission to access this page.</p>
      </div>
    );
  }

  return children;
}

export default AuthContext;
