import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';
import './FormattedContent.css';
import FormattedContent from './FormattedContent';
import { FaPaperPlane, FaTimes, FaSpinner, FaRobot, FaUser, FaInfoCircle } from 'react-icons/fa';

/**
 * Chatbot Component for Student Learning Assistant
 * Supports real-time streaming responses via SSE
 */
export default function Chatbot({ 
  isOpen, 
  onClose, 
  selectedQuestions = [], 
  initialSessionId = null 
}) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(initialSessionId);
  const [remainingQuota, setRemainingQuota] = useState(null);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
      fetchQuota();
    }
    return () => {
      // Abort any ongoing stream when closing
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [isOpen]);

  // Add welcome message when questions are selected
  useEffect(() => {
    if (isOpen && selectedQuestions.length > 0 && messages.length === 0) {
      const questionList = selectedQuestions
        .map(q => `• Q${q.question_number}: ${q.question_text?.substring(0, 50)}...`)
        .join('\n');
      
      setMessages([{
        role: 'assistant',
        content: `👋 Hey there, learning champ! 🌟\n\nI see you've got ${selectedQuestions.length} question(s) you want to explore:\n\n${questionList}\n\n💡 What would you like to understand better?\n\n✏️ You can ask me:\n• "Why was my answer wrong?"\n• "Explain this concept"\n• "Give me tips to remember this"\n\nLet's learn together! 💪`
      }]);
    } else if (isOpen && selectedQuestions.length === 0 && messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: `👋 Hey there! I'm your friendly English tutor for TN SSLC! 📚\n\n🎯 I can help you with:\n• 🎭 Poetry - meanings, themes & literary devices\n• 📖 Prose - story analysis & character study\n• ✍️ Grammar - rules & examples\n• 📝 Vocabulary - words & their usage\n\n💡 Just type your question and let's start learning! 💪`
      }]);
    }
  }, [isOpen, selectedQuestions]);

  const fetchQuota = async () => {
    try {
      const token = localStorage.getItem('examsmith_token');
      const apiUrl = `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'}`;
      
      console.log('Fetching quota from:', `${apiUrl}/student/chat/quota`);
      
      const response = await fetch(
        `${apiUrl}/student/chat/quota`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setRemainingQuota(data.remaining);
        console.log('Quota fetched:', data.remaining);
      } else {
        console.error('Quota fetch failed:', response.status);
      }
    } catch (err) {
      console.error('Failed to fetch quota:', err.message);
      // Don't set error here - just log it
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);
    setStreamingMessage('');
    
    try {
      const token = localStorage.getItem('examsmith_token');
      const apiUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/student/chat/stream`;
      
      console.log('Sending chat request to:', apiUrl);
      console.log('Auth token:', token ? 'Present' : 'Missing');
      console.log('Selected questions:', selectedQuestions);
      
      if (!token) {
        setError('Session expired. Please log in again.');
        setIsLoading(false);
        return;
      }
      
      abortControllerRef.current = new AbortController();
      
      const requestBody = {
        query: userMessage,
        selected_questions: selectedQuestions.map(q => ({
          question_number: q.question_number,
          question_text: q.question_text,
          student_answer: q.student_answer,
          correct_answer: q.correct_answer,
          is_correct: q.is_correct,
          source_unit: q.source_unit,
          unit_name: q.unit_name
        })),
        session_id: sessionId,
        chat_history: messages.slice(-10).map(m => ({
          role: m.role,
          content: m.content
        }))
      };
      
      console.log('Request body:', requestBody);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody),
        signal: abortControllerRef.current.signal
      });
      
      console.log('Response status:', response.status);
      
      if (response.status === 429) {
        const errorData = await response.json();
        setError(`Daily limit reached (${errorData.detail?.message || 'Try again tomorrow'})`);
        setIsLoading(false);
        return;
      }
      
      if (!response.ok) {
        console.error('Response error:', response.statusText);
        const errorText = await response.text();
        console.error('Error response body:', errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is empty');
      }
      
      // Read SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullMessage = '';
      let sources = [];
      let buffer = '';
      
      while (true) {
        try {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          
          // Keep the last incomplete line in the buffer
          buffer = lines[lines.length - 1];
          
          for (let i = 0; i < lines.length - 1; i++) {
            const line = lines[i];
            
            // Match SSE format: "event: TYPE\ndata: JSON"
            if (line.startsWith('event:')) {
              const eventType = line.substring(6).trim();
              const dataLine = lines[i + 1];
              
              if (dataLine && dataLine.startsWith('data:')) {
                const jsonStr = dataLine.substring(5).trim();
                
                try {
                  const data = JSON.parse(jsonStr);
                  
                  if (eventType === 'meta') {
                    if (data.session_id) {
                      setSessionId(data.session_id);
                    }
                    if (data.remaining_quota !== undefined) {
                      setRemainingQuota(data.remaining_quota);
                    }
                  }
                  
                  if (eventType === 'token' && data.token) {
                    fullMessage += data.token;
                    setStreamingMessage(fullMessage);
                  }
                  
                  if (eventType === 'done') {
                    if (data.sources) {
                      sources = data.sources;
                    }
                    if (data.remaining_quota !== undefined) {
                      setRemainingQuota(data.remaining_quota);
                    }
                  }
                  
                  if (eventType === 'error' && data.error) {
                    setError(data.error);
                  }
                } catch (parseErr) {
                  console.warn('JSON parse warning:', parseErr, 'data:', jsonStr);
                }
              }
              i++; // Skip the data line since we processed it
            }
          }
        } catch (readErr) {
          console.error('Stream read error:', readErr);
          break;
        }
      }
      
      // Process any remaining buffer
      if (buffer.trim()) {
        const lines = buffer.split('\n');
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          if (line.startsWith('event:')) {
            const eventType = line.substring(6).trim();
            const dataLine = lines[i + 1];
            if (dataLine && dataLine.startsWith('data:')) {
              const jsonStr = dataLine.substring(5).trim();
              try {
                const data = JSON.parse(jsonStr);
                if (eventType === 'token' && data.token) {
                  fullMessage += data.token;
                  setStreamingMessage(fullMessage);
                }
              } catch (e) {
                // ignore
              }
            }
          }
        }
      }
      
      // Add final assistant message
      if (fullMessage) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: fullMessage,
          sources: sources
        }]);
      } else if (!error) {
        setError('No response received from tutor');
      }
      setStreamingMessage('');
      
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Request aborted');
      } else {
        console.error('Chat error:', err);
        
        // Provide helpful error messages
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          setError('Cannot reach the server. Please ensure backend is running and try again.');
        } else if (err.message.includes('Unauthorized')) {
          setError('Session expired. Please log in again.');
        } else {
          setError(`Error: ${err.message || 'Unable to send message.'}`);
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="chatbot-side-panel">
      {/* Header */}
      <div className="chatbot-header">
        <div className="chatbot-title">
          <span className="tutor-emoji">🎓</span>
          <span>Your Study Buddy</span>
        </div>
        <button className="close-btn" onClick={onClose} title="Close chat">
          <FaTimes />
        </button>
      </div>
      
      {/* Quota Badge - Separate Row */}
      {remainingQuota !== null && (
        <div className="quota-bar">
          <span className="quota-badge">💬 {remainingQuota} messages left today</span>
        </div>
      )}
      
      {/* Selected Questions Info */}
      {selectedQuestions.length > 0 && (
        <div className="selected-questions-bar">
          <FaInfoCircle />
          <span>{selectedQuestions.length} question(s)</span>
        </div>
      )}
      
      {/* Messages Area */}
      <div className="chatbot-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-icon">
              {msg.role === 'user' ? <FaUser /> : <FaRobot />}
            </div>
            <div className="message-content">
              <div className="message-text">
                {msg.role === 'assistant' ? (
                  <FormattedContent content={msg.content} />
                ) : (
                  msg.content
                )}
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="message-sources">
                  <small>Sources: {msg.sources.map(s => s.lesson_name || 'Textbook').join(', ')}</small>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* Streaming message */}
        {streamingMessage && (
          <div className="message assistant">
            <div className="message-icon">
              <FaRobot />
            </div>
            <div className="message-content">
              <div className="message-text">
                <FormattedContent content={streamingMessage} />
              </div>
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        
        {/* Loading indicator */}
        {isLoading && !streamingMessage && (
          <div className="message assistant">
            <div className="message-icon">
              <FaRobot />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        
        {/* Error message */}
        {error && (
          <div className="message error">
            <div className="message-content">
              <div className="message-text">{error}</div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div className="chatbot-input">
        <textarea
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything! 💭"
          disabled={isLoading || remainingQuota === 0}
          rows={1}
        />
        <button 
          className="send-btn"
          onClick={handleSend}
          disabled={isLoading || !inputValue.trim() || remainingQuota === 0}
          title="Send message"
        >
          {isLoading ? <FaSpinner className="spin" /> : <FaPaperPlane />}
        </button>
      </div>
      
      {remainingQuota === 0 && (
        <div className="quota-exhausted">
          ⏰ You've used all your questions for today! Come back tomorrow for more learning! 🌟
        </div>
      )}
    </div>
  );
}
