import React, { useState, useEffect } from 'react';
import { 
  FaFlask, FaSpinner, FaPlay, FaInfoCircle, FaSync, FaFileAlt, FaRobot,
  FaShieldAlt, FaCheckCircle, FaBullseye, FaSearchPlus, FaUserShield,
  FaBrain, FaChartLine, FaClock, FaStar, FaArrowUp, FaArrowDown, FaMinus
} from 'react-icons/fa';
import { 
  getLatestPaperEvaluation, 
  getLatestChatbotEvaluation, 
  runPaperEvaluation, 
  runChatbotEvaluation 
} from '../services/api';
import './QualityTesting.css';

/* ── Animated SVG circular gauge ────────────────────────────── */
function CircularGauge({ score, size = 120, strokeWidth = 10, label, animate = true }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const safeScore = score ?? 0;
  const pct = Math.round(safeScore * 100);
  const offset = circumference - safeScore * circumference;

  const getColor = (s) => {
    if (s >= 0.7) return { main: '#10b981', bg: '#d1fae5', glow: 'rgba(16,185,129,0.25)' };
    if (s >= 0.4) return { main: '#f59e0b', bg: '#fef3c7', glow: 'rgba(245,158,11,0.25)' };
    return { main: '#ef4444', bg: '#fee2e2', glow: 'rgba(239,68,68,0.25)' };
  };
  const c = getColor(safeScore);

  return (
    <div className="circular-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <defs>
          <filter id={`glow-${label}`}>
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {/* background track */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={c.bg} strokeWidth={strokeWidth}
        />
        {/* score arc */}
        <circle
          className={animate ? 'gauge-arc' : ''}
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={c.main} strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          filter={`url(#glow-${label})`}
          style={{ transition: animate ? 'stroke-dashoffset 1.2s ease-out' : 'none' }}
        />
      </svg>
      <div className="gauge-label">
        <span className="gauge-pct" style={{ color: c.main }}>{pct}%</span>
      </div>
    </div>
  );
}

/* ── Metric metadata (icon, description, ideal direction) ──── */
const METRIC_META = {
  faithfulness: {
    icon: <FaShieldAlt />,
    desc: 'Measures how factually consistent the output is with the provided context.',
    ideal: 'higher',
  },
  contextual_recall: {
    icon: <FaSearchPlus />,
    desc: 'How well the retrieved context covers the expected answer.',
    ideal: 'higher',
  },
  contextual_precision: {
    icon: <FaBullseye />,
    desc: 'How relevant each retrieved context chunk is to the query.',
    ideal: 'higher',
  },
  hallucination: {
    icon: <FaBrain />,
    desc: 'Detects fabricated information not present in the context.',
    ideal: 'lower',
  },
  answer_relevancy: {
    icon: <FaCheckCircle />,
    desc: 'Measures how relevant the chatbot answer is to the question asked.',
    ideal: 'higher',
  },
  pii_leakage: {
    icon: <FaUserShield />,
    desc: 'Checks if personally identifiable information is exposed in the response.',
    ideal: 'lower',
  },
};

const defaultMeta = { icon: <FaChartLine />, desc: '', ideal: 'higher' };

/* ── Helpers ────────────────────────────────────────────────── */
function getGrade(score) {
  if (score >= 0.9) return { letter: 'A+', cls: 'grade-a-plus' };
  if (score >= 0.8) return { letter: 'A', cls: 'grade-a' };
  if (score >= 0.7) return { letter: 'B', cls: 'grade-b' };
  if (score >= 0.5) return { letter: 'C', cls: 'grade-c' };
  if (score >= 0.3) return { letter: 'D', cls: 'grade-d' };
  return { letter: 'F', cls: 'grade-f' };
}

function overallAverage(scores) {
  const vals = Object.values(scores || {}).filter(v => v !== null && v !== undefined);
  if (!vals.length) return null;
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

function TrendArrow({ score }) {
  if (score >= 0.7) return <FaArrowUp className="trend-icon trend-up" />;
  if (score >= 0.4) return <FaMinus className="trend-icon trend-flat" />;
  return <FaArrowDown className="trend-icon trend-down" />;
}

/* ══════════════════════════════════════════════════════════════
   MAIN COMPONENT
   ══════════════════════════════════════════════════════════════ */
export default function QualityTesting() {
  const [paperEvaluation, setPaperEvaluation] = useState(null);
  const [chatbotEvaluation, setChatbotEvaluation] = useState(null);
  const [loadingPaper, setLoadingPaper] = useState(true);
  const [loadingChatbot, setLoadingChatbot] = useState(true);
  const [runningPaper, setRunningPaper] = useState(false);
  const [runningChatbot, setRunningChatbot] = useState(false);
  const [paperError, setPaperError] = useState(null);
  const [chatbotError, setChatbotError] = useState(null);
  const [chatbotQuery, setChatbotQuery] = useState('Explain the process of photosynthesis in plants.');
  const [selectedParts, setSelectedParts] = useState(['I', 'II', 'III', 'IV']); // All parts selected by default

  useEffect(() => { loadLatestEvaluations(); }, []);

  /* ── data loaders ─────────────────────────────────────────── */
  const loadLatestEvaluations = async () => {
    setLoadingPaper(true);  setPaperError(null);
    setLoadingChatbot(true); setChatbotError(null);
    try {
      const paperData = await getLatestPaperEvaluation();
      if (paperData && !paperData.error) setPaperEvaluation(paperData);
      else if (paperData?.error) setPaperError(paperData.message || 'No paper evaluation available');
    } catch { setPaperError('No paper evaluation available. Run an evaluation to see results.'); }
    finally { setLoadingPaper(false); }

    try {
      const chatbotData = await getLatestChatbotEvaluation();
      if (chatbotData && !chatbotData.error) setChatbotEvaluation(chatbotData);
      else if (chatbotData?.error) setChatbotError(chatbotData.message || 'No chatbot evaluation available');
    } catch { setChatbotError('No chatbot evaluation available. Run an evaluation to see results.'); }
    finally { setLoadingChatbot(false); }
  };

  const handleRunPaperEvaluation = async () => {
    if (selectedParts.length === 0) {
      setPaperError('Please select at least one part to evaluate');
      return;
    }
    setRunningPaper(true); setPaperError(null);
    try {
      const result = await runPaperEvaluation(selectedParts);
      if (result && !result.error) setPaperEvaluation(result);
      else setPaperError(result?.message || 'Failed to run paper evaluation');
    } catch (err) { 
      const errMsg = err.message || 'Failed to run paper evaluation';
      // Provide helpful message for timeout
      if (errMsg.includes('timeout') || errMsg.includes('ECONNABORTED')) {
        setPaperError('Evaluation timed out - this may take up to 30 minutes for full paper evaluation');
      } else {
        setPaperError(errMsg);
      }
    }
    finally { setRunningPaper(false); }
  };

  const togglePart = (part) => {
    setSelectedParts(prev => 
      prev.includes(part) ? prev.filter(p => p !== part) : [...prev, part]
    );
  };

  const toggleAllParts = () => {
    setSelectedParts(prev => 
      prev.length === 4 ? [] : ['I', 'II', 'III', 'IV']
    );
  };

  const handleRunChatbotEvaluation = async () => {
    if (!chatbotQuery.trim()) { setChatbotError('Please enter a query for the chatbot'); return; }
    setRunningChatbot(true); setChatbotError(null);
    try {
      const result = await runChatbotEvaluation(chatbotQuery);
      if (result && !result.error) setChatbotEvaluation(result);
      else setChatbotError(result?.message || 'Failed to run chatbot evaluation');
    } catch (err) { setChatbotError(err.message || 'Failed to run chatbot evaluation'); }
    finally { setRunningChatbot(false); }
  };

  /* ── score helpers ────────────────────────────────────────── */
  const getScoreColor = (s) => { if (s >= 0.7) return '#10b981'; if (s >= 0.4) return '#f59e0b'; return '#ef4444'; };
  const getScoreClass = (s) => { if (s >= 0.7) return 'high'; if (s >= 0.4) return 'medium'; return 'low'; };
  const formatScore = (s) => (s === null || s === undefined) ? 'N/A' : `${(s * 100).toFixed(1)}%`;
  const formatError = (err) => {
    if (!err) return '';
    if (typeof err === 'string' && err.includes('Rate limit')) return 'Rate limit exceeded - try again later';
    if (typeof err === 'string' && err.includes('429')) return 'API rate limit';
    return (typeof err === 'string' && err.length > 80) ? err.substring(0, 80) + '...' : err || '';
  };
  const formatDate = (d) => d ? new Date(d).toLocaleString() : '';

  /* ── Overall score for a paper evaluation ─────────────────── */
  const paperOverall = paperEvaluation ? overallAverage(paperEvaluation.aggregate_scores) : null;
  const paperGrade = paperOverall !== null ? getGrade(paperOverall) : null;

  /* ── Overall score for a chatbot evaluation ───────────────── */
  const chatbotOverall = chatbotEvaluation
    ? overallAverage(
        Object.fromEntries(
          Object.entries(chatbotEvaluation.metrics || {}).map(([k, v]) => [k, v?.score])
        )
      )
    : null;
  const chatbotGrade = chatbotOverall !== null ? getGrade(chatbotOverall) : null;

  /* ══════════════════════════════════════════════════════════ */
  return (
    <div className="quality-testing">

      {/* ── Header ─────────────────────────────────────────── */}
      <div className="quality-header">
        <div className="header-icon-wrap"><FaFlask /></div>
        <h2>RAG Quality Evaluation</h2>
        <p>Evaluate question paper generation &amp; chatbot responses with DeepEval metrics</p>
        <button className="refresh-btn" onClick={loadLatestEvaluations} disabled={loadingPaper || loadingChatbot}>
          <FaSync className={loadingPaper || loadingChatbot ? 'spin' : ''} /> Refresh Results
        </button>
      </div>

      {/* ═══════════════════════════════════════════════════════
          PAPER GENERATION EVALUATION
          ═══════════════════════════════════════════════════════ */}
      <div className="eval-section paper-section">
        <div className="section-banner paper-banner">
          <div className="banner-left">
            <span className="banner-icon"><FaFileAlt /></span>
            <div>
              <h3>Question Paper Evaluation</h3>
              <span className="banner-sub">Faithfulness · Contextual Recall · Contextual Precision · Hallucination</span>
            </div>
          </div>
          <div className="part-selection-controls">
            <div className="part-selection-title">Select Parts to Evaluate:</div>
            <div className="part-checkboxes">
              <label className="part-checkbox">
                <input 
                  type="checkbox" 
                  checked={selectedParts.length === 4}
                  onChange={toggleAllParts}
                />
                <span>All Parts</span>
              </label>
              {['I', 'II', 'III', 'IV'].map(part => (
                <label key={part} className="part-checkbox">
                  <input 
                    type="checkbox" 
                    checked={selectedParts.includes(part)}
                    onChange={() => togglePart(part)}
                  />
                  <span>Part {part}</span>
                </label>
              ))}
            </div>
            <button className="run-btn" onClick={handleRunPaperEvaluation} disabled={runningPaper || selectedParts.length === 0}>
              {runningPaper
                ? <><FaSpinner className="spin" /> Evaluating {selectedParts.join(', ')}…</>
                : <><FaPlay /> Run Evaluation ({selectedParts.length === 4 ? 'All Parts' : selectedParts.join(', ')})</>}
            </button>
          </div>
        </div>

        {loadingPaper ? (
          <div className="state-msg"><FaSpinner className="spin" /><span>Loading paper evaluation…</span></div>
        ) : paperError ? (
          <div className="state-msg warn"><FaInfoCircle /><span>{paperError}</span></div>
        ) : paperEvaluation ? (
          <div className="eval-body">
            {/* top strip: overall + timestamp */}
            <div className="eval-topstrip">
              {paperGrade && (
                <div className={`overall-badge ${paperGrade.cls}`}>
                  <span className="grade-letter">{paperGrade.letter}</span>
                  <span className="grade-pct">{Math.round(paperOverall * 100)}% overall</span>
                </div>
              )}
              <div className="eval-meta">
                <FaClock /> {formatDate(paperEvaluation.timestamp)}
                <span className="meta-sep">|</span>
                <FaStar /> {paperEvaluation.samples?.length || 0} samples
              </div>
            </div>

            {/* gauge cards */}
            <div className="gauge-grid">
              {Object.entries(paperEvaluation.aggregate_scores || {}).map(([metric, score]) => {
                const meta = METRIC_META[metric] || defaultMeta;
                return (
                  <div key={metric} className={`gauge-card ${getScoreClass(score)}-border`}>
                    <div className="gauge-card-top">
                      <span className="gauge-metric-icon" style={{ color: getScoreColor(score) }}>{meta.icon}</span>
                      <span className="gauge-metric-name">{metric.replace(/_/g, ' ')}</span>
                      <TrendArrow score={score} />
                    </div>
                    <CircularGauge score={score} size={85} strokeWidth={8} label={metric} />
                    <div className="gauge-card-bar">
                      <div className="bar-track">
                        <div className="bar-fill" style={{ width: `${(score || 0) * 100}%`, background: getScoreColor(score) }} />
                      </div>
                    </div>
                    {meta.desc && <p className="gauge-desc">{meta.desc}</p>}
                  </div>
                );
              })}
            </div>

            {/* sample details */}
            <div className="samples-section">
              <h4><FaSearchPlus /> Evaluated Questions <span className="h4-sub">({paperEvaluation.samples?.length || 0} total questions)</span></h4>
              <div className="samples-grid">
                {(paperEvaluation.samples || []).slice(0, 10).map((sample, idx) => (
                  <div key={idx} className="sample-card">
                    <div className="sample-top">
                      <span className="part-pill">Part {sample.part}</span>
                      <span className="q-num">Q{sample.question_number}</span>
                    </div>
                    <p className="sample-q">{sample.question?.substring(0, 180)}{sample.question?.length > 180 && '…'}</p>
                    <div className="mini-scores">
                      {Object.entries(sample.metrics || {}).map(([m, d]) => {
                        const mc = getScoreColor(d?.score);
                        return (
                          <div key={m} className="mini-chip" style={{ borderColor: mc }}>
                            <span className="mini-label">{m.replace(/_/g, ' ')}</span>
                            <span className="mini-val" style={{ color: mc }}>{formatScore(d?.score)}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
              {paperEvaluation.samples?.length > 10 && (
                <p className="samples-note">
                  <FaInfoCircle /> Showing first 10 of {paperEvaluation.total_questions_evaluated || paperEvaluation.samples.length} evaluated questions 
                  (from {paperEvaluation.total_questions_generated || 'N/A'} generated)
                </p>
              )}
              {paperEvaluation.samples?.length <= 10 && paperEvaluation.total_questions_generated && (
                <p className="samples-note">
                  <FaInfoCircle /> Evaluated {paperEvaluation.total_questions_evaluated || paperEvaluation.samples.length} of {paperEvaluation.total_questions_generated} generated questions
                </p>
              )}
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <FaFileAlt className="empty-icon" />
            <p>No paper evaluation yet</p>
            <p className="empty-sub">Click <strong>Run Evaluation</strong> to evaluate question paper quality</p>
          </div>
        )}
      </div>

      {/* ═══════════════════════════════════════════════════════
          CHATBOT EVALUATION
          ═══════════════════════════════════════════════════════ */}
      <div className="eval-section chatbot-section">
        <div className="section-banner chatbot-banner">
          <div className="banner-left">
            <span className="banner-icon"><FaRobot /></span>
            <div>
              <h3>Chatbot Response Evaluation</h3>
              <span className="banner-sub">Answer Relevancy · PII Leakage</span>
            </div>
          </div>
        </div>

        {/* query input */}
        <div className="chat-input-row">
          <div className="chat-input-wrap">
            <label>Test Query</label>
            <input
              type="text" value={chatbotQuery}
              onChange={(e) => setChatbotQuery(e.target.value)}
              placeholder="Enter a question to test the chatbot…"
            />
          </div>
          <button className="run-btn" onClick={handleRunChatbotEvaluation} disabled={runningChatbot}>
            {runningChatbot
              ? <><FaSpinner className="spin" /> Evaluating…</>
              : <><FaPlay /> Run Evaluation</>}
          </button>
        </div>

        {loadingChatbot ? (
          <div className="state-msg"><FaSpinner className="spin" /><span>Loading chatbot evaluation…</span></div>
        ) : chatbotError ? (
          <div className="state-msg warn"><FaInfoCircle /><span>{chatbotError}</span></div>
        ) : chatbotEvaluation ? (
          <div className="eval-body">
            {/* top strip */}
            <div className="eval-topstrip">
              {chatbotGrade && (
                <div className={`overall-badge ${chatbotGrade.cls}`}>
                  <span className="grade-letter">{chatbotGrade.letter}</span>
                  <span className="grade-pct">{Math.round(chatbotOverall * 100)}% overall</span>
                </div>
              )}
              <div className="eval-meta">
                <FaClock /> {formatDate(chatbotEvaluation.timestamp)}
              </div>
            </div>

            {/* Q & A card */}
            <div className="chat-qa-card">
              <div className="qa-row">
                <span className="qa-badge q-badge">Q</span>
                <p>{chatbotEvaluation.query}</p>
              </div>
              <div className="qa-row">
                <span className="qa-badge a-badge">A</span>
                <p>{chatbotEvaluation.response?.substring(0, 500)}{chatbotEvaluation.response?.length > 500 && '…'}</p>
              </div>
              <div className="qa-meta">
                <span>📚 {chatbotEvaluation.context_count || 0} context documents used</span>
              </div>
            </div>

            {/* metric gauges */}
            <div className="gauge-grid chatbot-gauge-grid">
              {Object.entries(chatbotEvaluation.metrics || {}).map(([metric, data]) => {
                const meta = METRIC_META[metric] || defaultMeta;
                const score = data?.score;
                return (
                  <div key={metric} className={`gauge-card ${getScoreClass(score)}-border`}>
                    <div className="gauge-card-top">
                      <span className="gauge-metric-icon" style={{ color: getScoreColor(score) }}>{meta.icon}</span>
                      <span className="gauge-metric-name">{metric.replace(/_/g, ' ')}</span>
                      <TrendArrow score={score} />
                    </div>
                    <CircularGauge score={score} size={85} strokeWidth={8} label={metric} />
                    <div className="gauge-card-bar">
                      <div className="bar-track">
                        <div className="bar-fill" style={{ width: `${(score || 0) * 100}%`, background: getScoreColor(score) }} />
                      </div>
                    </div>
                    {meta.desc && <p className="gauge-desc">{meta.desc}</p>}
                    {data?.explanation && <p className="gauge-explanation">{data.explanation}</p>}
                    {data?.error && <p className="gauge-error">{formatError(data.error)}</p>}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <FaRobot className="empty-icon" />
            <p>No chatbot evaluation yet</p>
            <p className="empty-sub">Enter a query and click <strong>Run Evaluation</strong></p>
          </div>
        )}
      </div>

      {/* ── Footer ─────────────────────────────────────────── */}
      <div className="server-info">
        <FaInfoCircle />
        <span>
          DeepEval server: <code>http://localhost:8001</code>
          &nbsp;|&nbsp; Backend API: <code>http://localhost:8000</code>
        </span>
      </div>
    </div>
  );
}
