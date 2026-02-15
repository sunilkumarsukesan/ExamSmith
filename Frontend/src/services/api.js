import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for paper generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token storage key
const TOKEN_KEY = 'examsmith_token';

// Add auth token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem('examsmith_user');
      // Optionally redirect to login
      if (window.location.pathname !== '/signin') {
        window.location.href = '/signin';
      }
    }
    return Promise.reject(error);
  }
);

// ===== Authentication APIs =====

/**
 * Login with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Object} - { user, token, message }
 */
export const login = async (email, password) => {
  const response = await apiClient.post('/auth/login', { email, password });
  return response.data;
};

/**
 * Register a new student account
 * @param {string} name - User's full name
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Object} - User data
 */
export const register = async (name, email, password) => {
  const response = await apiClient.post('/auth/register', {
    name,
    email,
    password,
    role: 'STUDENT', // Only students can self-register
  });
  return response.data;
};

/**
 * Get current user profile
 * @returns {Object} - User data
 */
export const getCurrentUser = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};

/**
 * Refresh access token
 * @returns {Object} - New token data
 */
export const refreshToken = async () => {
  const response = await apiClient.post('/auth/refresh');
  return response.data;
};

// ===== Student APIs =====

/**
 * Get published papers for students
 * @returns {Object} - { papers, total }
 */
export const getPipelinePapers = async (skip = 0, limit = 20) => {
  const response = await apiClient.get('/student/pipeline-papers', {
    params: { skip, limit },
  });
  return response.data;
};

/**
 * Get a paper for taking exam (without answers)
 * @param {string} paperId - Paper ID
 * @returns {Object} - Paper data without answer keys
 */
export const getPaperForExam = async (paperId) => {
  const response = await apiClient.get(`/student/papers/${paperId}`);
  return response.data;
};

/**
 * Start an exam attempt
 * @param {string} paperId - Paper ID
 * @returns {Object} - Attempt data
 */
export const startExam = async (paperId) => {
  const response = await apiClient.post('/student/start-exam', { paper_id: paperId });
  return response.data;
};

/**
 * Submit exam answers
 * @param {string} attemptId - Attempt ID
 * @param {Array} answers - Array of answer objects
 * @returns {Object} - Submission result
 */
export const submitExam = async (attemptId, answers) => {
  const response = await apiClient.post(`/student/submit-paper?attempt_id=${attemptId}`, {
    answers,
  });
  return response.data;
};

/**
 * Get student's exam attempts
 * @returns {Object} - { attempts, total }
 */
export const getMyAttempts = async () => {
  const response = await apiClient.get('/student/my-attempts');
  return response.data;
};

/**
 * Get evaluation result for an attempt
 * @param {string} attemptId - Attempt ID
 * @returns {Object} - Evaluation data
 */
export const getResult = async (attemptId) => {
  const response = await apiClient.get(`/student/results/${attemptId}`);
  return response.data;
};

// ===== Instructor APIs =====

/**
 * Get instructor's papers
 * @param {string} status - Optional status filter
 * @returns {Object} - { papers, total }
 */
export const getInstructorPapers = async (status = null) => {
  const params = status ? { status } : {};
  const response = await apiClient.get('/instructor/papers', { params });
  return response.data;
};

/**
 * Save a generated paper
 * @param {Object} paperData - Paper data from generate-paper API
 * @returns {Object} - Saved paper data
 */
export const savePaper = async (paperData) => {
  const response = await apiClient.post('/instructor/save-paper', paperData);
  return response.data;
};

/**
 * Approve a paper
 * @param {string} paperId - Paper ID
 * @param {string} comments - Optional comments
 * @returns {Object} - Approval result
 */
export const approvePaper = async (paperId, comments = null) => {
  const response = await apiClient.post(`/instructor/approve-paper/${paperId}`, {
    comments,
  });
  return response.data;
};

/**
 * Publish a paper to student pipeline
 * @param {string} paperId - Paper ID
 * @param {string} notes - Optional notes
 * @returns {Object} - Publish result
 */
export const publishPaper = async (paperId, notes = null) => {
  const response = await apiClient.post(`/instructor/publish-to-pipeline/${paperId}`, {
    notes,
  });
  return response.data;
};

/**
 * Unpublish a paper
 * @param {string} paperId - Paper ID
 * @returns {Object} - Unpublish result
 */
export const unpublishPaper = async (paperId) => {
  const response = await apiClient.post(`/instructor/unpublish/${paperId}`);
  return response.data;
};

// ===== Admin APIs =====

/**
 * Create a new user (admin only)
 * @param {Object} userData - { email, password, name, role }
 * @returns {Object} - Created user data
 */
export const createUser = async (userData) => {
  const response = await apiClient.post('/admin/create-user', userData);
  return response.data;
};

/**
 * List all users (admin only)
 * @param {Object} filters - { role, status }
 * @returns {Array} - List of users
 */
export const listUsers = async (filters = {}) => {
  const response = await apiClient.get('/admin/list-users', { params: filters });
  return response.data;
};

/**
 * Disable a user (admin only)
 * @param {string} userId - User ID
 * @returns {Object} - Updated user data
 */
export const disableUser = async (userId) => {
  const response = await apiClient.put(`/admin/disable-user/${userId}`);
  return response.data;
};

/**
 * Enable a user (admin only)
 * @param {string} userId - User ID
 * @returns {Object} - Updated user data
 */
export const enableUser = async (userId) => {
  const response = await apiClient.put(`/admin/enable-user/${userId}`);
  return response.data;
};

// ===== PDF Download =====

/**
 * Download paper as PDF
 * @param {string} paperId - Paper ID
 * @returns {Blob} - PDF file blob
 */
export const downloadPaperPdf = async (paperId) => {
  const response = await apiClient.get(`/papers/${paperId}/download-pdf`, {
    responseType: 'blob',
  });
  return response.data;
};

// ===== Existing APIs (unchanged) =====

// Question Paper Generation
export const generateQuestionPaper = async (params) => {

  try {
    const response = await apiClient.post('/generate-paper', params);
    return response.data;
  } catch (error) {
    console.error('Error generating question paper:', error);
    throw error;
  }
};

// Ask a Question
export const askQuestion = async (question, hybridSearch = {}) => {
  try {
    const response = await apiClient.post('/ask', {
      question,
      hybrid_search: hybridSearch,
    });
    return response.data;
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
};

// Find Similar Questions
export const findSimilarQuestions = async (questionText, topK = 5, difficulty = null) => {
  try {
    const response = await apiClient.post('/similar-questions', {
      question_text: questionText,
      top_k: topK,
      difficulty,
    });
    return response.data;
  } catch (error) {
    console.error('Error finding similar questions:', error);
    throw error;
  }
};

// Evaluate Answer
export const evaluateAnswer = async (questionText, studentAnswer, questionId = null) => {
  try {
    const response = await apiClient.post('/evaluate-answer', {
      question_text: questionText,
      student_answer: studentAnswer,
      question_id: questionId,
    });
    return response.data;
  } catch (error) {
    console.error('Error evaluating answer:', error);
    throw error;
  }
};

// Health Check
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

// ===== Human-in-the-Loop: Question Revision APIs =====

/**
 * Revise a single question based on teacher feedback
 * @param {Object} data - { original_question, teacher_feedback, paper_id }
 * @returns {Object} - { success, revised_question, message }
 */
export const reviseQuestion = async (data) => {
  try {
    const response = await apiClient.post('/revise-question', data);
    return response.data;
  } catch (error) {
    console.error('Error revising question:', error);
    throw error;
  }
};

/**
 * Get revision history for a paper
 * @param {string} paperId - The paper ID
 * @param {number|null} questionNumber - Optional question number to filter
 * @returns {Object} - { paper_id, revisions, total_revisions }
 */
export const getRevisionHistory = async (paperId, questionNumber = null) => {
  try {
    let url = `/revision-history/${paperId}`;
    if (questionNumber !== null) {
      url += `?question_number=${questionNumber}`;
    }
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    console.error('Error getting revision history:', error);
    return { revisions: [], total_revisions: 0 };
  }
};

/**
 * Regenerate all questions with global feedback
 * @param {Object} data - { paper_id, questions, teacher_feedback }
 * @returns {Object} - { success, questions, message }
 */
export const regenerateAllQuestions = async (data) => {
  try {
    const response = await apiClient.post('/regenerate-all', data);
    return response.data;
  } catch (error) {
    console.error('Error regenerating all questions:', error);
    throw error;
  }
};

// ===== Chat APIs =====

/**
 * Get chat quota for current user
 * @returns {Object} - { remaining, limit, reset_date }
 */
export const getChatQuota = async () => {
  const response = await apiClient.get('/student/chat/quota');
  return response.data;
};

/**
 * Get chat sessions for current user
 * @returns {Object} - { sessions, total }
 */
export const getChatSessions = async (skip = 0, limit = 20) => {
  const response = await apiClient.get('/student/chat/sessions', {
    params: { skip, limit }
  });
  return response.data;
};

/**
 * Get messages for a chat session
 * @param {string} sessionId - Session ID
 * @returns {Object} - { session_id, title, messages }
 */
export const getChatSessionMessages = async (sessionId) => {
  const response = await apiClient.get(`/student/chat/sessions/${sessionId}/messages`);
  return response.data;
};

// ===== DeepEval Quality Testing APIs =====

const DEEPEVAL_URL = import.meta.env.VITE_DEEPEVAL_URL || 'http://localhost:8001';

/**
 * Evaluate using DeepEval metric
 * @param {Object} payload - Evaluation payload with metric, query, context, output, etc.
 * @returns {Object} - Evaluation result with score, explanation
 */
export const evaluateMetric = async (payload) => {
  try {
    const response = await fetch(`${DEEPEVAL_URL}/eval-only`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('DeepEval metric evaluation error:', error);
    throw error;
  }
};

/**
 * Run sample evaluation for paper generation or chatbot
 * @param {string} testType - 'paper_generation' or 'chatbot'
 * @param {string} metric - Metric to evaluate (faithfulness, answer_relevancy, etc.)
 * @returns {Object} - Evaluation result
 */
export const runSampleEvaluation = async (testType, metric) => {
  // Sample test data for quick evaluation
  const sampleData = {
    paper_generation: {
      query: "Generate a question about photosynthesis for 10th grade biology",
      context: [
        "Photosynthesis is the process by which green plants use sunlight to synthesize nutrients from carbon dioxide and water.",
        "Chlorophyll is the green pigment in plants that absorbs sunlight for photosynthesis.",
        "The process of photosynthesis produces glucose and releases oxygen as a byproduct."
      ],
      output: "What is the role of chlorophyll in the process of photosynthesis? Explain how plants convert sunlight into energy.",
      expected_output: "Chlorophyll absorbs sunlight which is used to convert carbon dioxide and water into glucose and oxygen."
    },
    chatbot: {
      query: "What is the formula for calculating area of a circle?",
      context: [
        "The area of a circle is calculated using the formula A = πr², where r is the radius of the circle.",
        "Pi (π) is a mathematical constant approximately equal to 3.14159.",
        "The radius is the distance from the center of the circle to any point on its circumference."
      ],
      output: "The area of a circle can be calculated using the formula A = πr², where 'A' represents the area, 'π' (pi) is approximately 3.14159, and 'r' is the radius of the circle.",
      expected_output: "The area of a circle is A = πr², where r is the radius of the circle."
    }
  };

  const testData = sampleData[testType] || sampleData.paper_generation;
  
  const payload = {
    metric,
    query: testData.query,
    context: testData.context,
    output: testData.output,
    expected_output: testData.expected_output,
    retrieval_context: testData.context
  };

  return evaluateMetric(payload);
};

// ===== Quality Evaluation APIs =====

/**
 * Get latest paper evaluation results
 * @returns {Object} - Latest paper evaluation result with aggregate scores
 */
export const getLatestPaperEvaluation = async () => {
  const response = await apiClient.get('/evaluation/latest-paper-results');
  return response.data;
};

/**
 * Get latest chatbot evaluation results
 * @returns {Object} - Latest chatbot evaluation result with metric scores
 */
export const getLatestChatbotEvaluation = async () => {
  const response = await apiClient.get('/evaluation/latest-chatbot-results');
  return response.data;
};

/**
 * Run paper evaluation - generates full paper (47 questions) and evaluates selected parts
 * @param {Array} parts - Array of parts to evaluate (e.g., ['I', 'II', 'III', 'IV'])
 * @returns {Object} - Evaluation result with sampled questions and aggregate scores
 */
export const runPaperEvaluation = async (parts = ['I', 'II', 'III', 'IV']) => {
  const response = await apiClient.post('/evaluation/evaluate-paper', { parts }, {
    timeout: 1800000 // 30 minutes for full paper generation + evaluation
  });
  return response.data;
};

/**
 * Run chatbot evaluation with a query
 * @param {string} query - Query to test chatbot with
 * @returns {Object} - Evaluation result with metric scores
 */
export const runChatbotEvaluation = async (query) => {
  const response = await apiClient.post('/evaluation/evaluate-chatbot', { query }, {
    timeout: 300000 // 5 minutes
  });
  return response.data;
};

/**
 * Get all evaluation results history
 * @returns {Object} - All paper and chatbot evaluation history
 */
export const getAllEvaluationResults = async () => {
  const response = await apiClient.get('/evaluation/all-results');
  return response.data;
};

export default apiClient;
