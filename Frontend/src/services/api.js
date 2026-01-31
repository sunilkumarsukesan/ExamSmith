import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for paper generation
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export default apiClient;
