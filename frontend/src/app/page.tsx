'use client';

import React, { useState, useEffect, useRef } from 'react';

// API Base configuration
const API_BASE = 'http://localhost:8000/api';

interface EvidenceItem {
  id: number;
  source: string;
  claim: string;
  confidence: number;
}

interface Argument {
  id: number;
  side: 'Pro' | 'Con';
  claim: string;
  evidence: string;
  impact: string;
  score: number;
}

interface Rebuttal {
  id: number;
  target_argument_id: number;
  side: 'Pro' | 'Con';
  claim: string;
  question: string;
}

interface Fallacy {
  id: number;
  argument_id?: number;
  type: string;
  severity: number;
  explanation: string;
}

interface Verification {
  id: number;
  claim: string;
  evidence_used: string;
  status: 'supported' | 'partially supported' | 'unsupported';
  reasoning: string;
}

interface Debate {
  id: number;
  topic: string;
  created_at: string;
  winner: string | null;
  scope: string | null;
  status: string;
  error_message: string | null;
  pro_opening: string | null;
  con_opening: string | null;
  pro_score: number | null;
  con_score: number | null;
  decision_reasoning: string | null;
  report: string | null;
  evidence_items?: EvidenceItem[];
  arguments?: Argument[];
  rebuttals?: Rebuttal[];
  fallacies?: Fallacy[];
  verifications?: Verification[];
}

export default function Home() {
  const [debates, setDebates] = useState<Debate[]>([]);
  const [selectedDebate, setSelectedDebate] = useState<Debate | null>(null);
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'transcript' | 'crossexam' | 'audit' | 'report'>('overview');
  
  // Track running debate ID for polling
  const [runningDebateId, setRunningDebateId] = useState<number | null>(null);
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Load debates on mount
  useEffect(() => {
    fetchDebates();
    return () => stopPolling();
  }, []);

  const fetchDebates = async () => {
    try {
      const res = await fetch(`${API_BASE}/debates`);
      if (res.ok) {
        const data = await res.json();
        setDebates(data);
      }
    } catch (err) {
      console.error('Failed to fetch debates:', err);
    }
  };

  const fetchDebateDetails = async (id: number) => {
    try {
      const res = await fetch(`${API_BASE}/debates/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedDebate(data);
      }
    } catch (err) {
      console.error('Failed to fetch debate details:', err);
    }
  };

  const startPolling = (id: number) => {
    stopPolling();
    setRunningDebateId(id);
    
    pollTimerRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/debates/${id}/status`);
        if (!res.ok) return;
        
        const data = await res.json();
        
        // Refresh details
        await fetchDebateDetails(id);
        
        // If done/failed, stop polling and refresh list
        if (['completed', 'failed'].includes(data.status)) {
          stopPolling();
          fetchDebates();
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2500);
  };

  const stopPolling = () => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    setRunningDebateId(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanTopic = topic.trim();
    if (!cleanTopic) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/debates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: cleanTopic })
      });
      
      if (res.ok) {
        const data = await res.json();
        setTopic('');
        setSelectedDebate(data);
        setActiveTab('overview');
        // Start polling for updates
        startPolling(data.id);
        fetchDebates();
      } else {
        alert('Failed to launch debate');
      }
    } catch (err) {
      console.error('Error starting debate:', err);
      alert('Error connecting to backend API');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this debate?')) return;
    
    try {
      const res = await fetch(`${API_BASE}/debates/${id}`, { method: 'DELETE' });
      if (res.ok) {
        if (selectedDebate?.id === id) {
          setSelectedDebate(null);
        }
        if (runningDebateId === id) {
          stopPolling();
        }
        fetchDebates();
      }
    } catch (err) {
      console.error('Failed to delete debate:', err);
    }
  };

  const getStepNumber = (status: string) => {
    const steps = [
      'pending',
      'orchestrating',
      'researching',
      'pro_arguing',
      'con_arguing',
      'cross_examining',
      'detecting_fallacies',
      'verifying_evidence',
      'judging',
      'generating_report',
      'completed'
    ];
    return steps.indexOf(status);
  };

  const renderAgentProgress = (status: string) => {
    const currentStep = getStepNumber(status);
    const agents = [
      { name: 'Orchestrator', step: 1, label: 'Structuring scope' },
      { name: 'Research Analyst', step: 2, label: 'Retrieving evidence' },
      { name: 'Pro Debater', step: 3, label: 'Formulating arguments' },
      { name: 'Con Debater', step: 4, label: 'Formulating counters' },
      { name: 'Cross-Examiner', step: 5, label: 'Generating rebuttals' },
      { name: 'Logic Auditor', step: 6, label: 'Detecting fallacies' },
      { name: 'Evidence Verifier', step: 7, label: 'Checking citations' },
      { name: 'Judge Agent', step: 8, label: 'Determining winner' },
      { name: 'Report Generator', step: 9, label: 'Compiling files' }
    ];

    return (
      <div style={{ marginTop: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--text-primary)' }}>
          Multi-Agent Reasoning Pipeline
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {agents.map((agent) => {
            const isCompleted = currentStep > agent.step;
            const isActive = currentStep === agent.step;
            
            let statusColor = 'var(--text-muted)';
            let bgColor = 'rgba(255, 255, 255, 0.02)';
            let borderColor = 'var(--border-color)';
            let pulseClass = '';

            if (isCompleted) {
              statusColor = 'var(--color-success)';
              borderColor = 'rgba(16, 185, 129, 0.3)';
              bgColor = 'rgba(16, 185, 129, 0.03)';
            } else if (isActive) {
              statusColor = 'var(--color-accent)';
              borderColor = 'var(--color-accent)';
              bgColor = 'rgba(139, 92, 246, 0.05)';
              pulseClass = 'active-agent-glow';
            }

            return (
              <div 
                key={agent.name} 
                className={pulseClass}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: '1px solid',
                  borderColor,
                  backgroundColor: bgColor,
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    backgroundColor: isCompleted ? 'var(--color-success)' : isActive ? 'var(--color-accent)' : 'transparent',
                    border: isCompleted || isActive ? 'none' : '1px solid var(--text-muted)',
                    color: isCompleted ? '#070a13' : 'white'
                  }}>
                    {isCompleted ? '✓' : agent.step}
                  </div>
                  <div>
                    <div style={{ fontWeight: '600', fontSize: '0.95rem', color: isActive ? 'var(--color-accent)' : 'var(--text-primary)' }}>
                      {agent.name}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{agent.label}</div>
                  </div>
                </div>
                <span style={{ fontSize: '0.8rem', fontWeight: '500', color: statusColor }}>
                  {isCompleted ? 'Completed' : isActive ? 'Processing...' : 'Queued'}
                </span>
              </div>
            );
          })}
        </div>
        
        <style jsx global>{`
          @keyframes glow {
            0% { box-shadow: 0 0 5px rgba(139, 92, 246, 0.2); }
            50% { box-shadow: 0 0 15px rgba(139, 92, 246, 0.4); }
            100% { box-shadow: 0 0 5px rgba(139, 92, 246, 0.2); }
          }
          .active-agent-glow {
            animation: glow 2s infinite;
          }
        `}</style>
      </div>
    );
  };

  const getStatusBadge = (statusStr: string) => {
    let color = 'var(--text-muted)';
    let text = statusStr;
    
    switch(statusStr) {
      case 'completed':
        color = 'var(--color-success)';
        text = 'Completed';
        break;
      case 'failed':
        color = 'var(--color-error)';
        text = 'Failed';
        break;
      case 'pending':
        text = 'Pending';
        break;
      default:
        color = 'var(--color-accent)';
        text = 'Processing...';
    }

    return (
      <span style={{ 
        fontSize: '0.75rem', 
        padding: '3px 8px', 
        borderRadius: '20px', 
        backgroundColor: `rgba(255,255,255,0.02)`,
        border: `1px solid ${color}`,
        color: color,
        fontWeight: '600'
      }}>
        {text}
      </span>
    );
  };

  const renderMarkdown = (text: string | null) => {
    if (!text) return <p style={{ color: 'var(--text-muted)' }}>No content available.</p>;

    // Simple markdown renderer for headers, bullet points, tables, bold text
    const lines = text.split('\n');
    let inTable = false;
    let tableHeaders: string[] = [];
    let tableRows: string[][] = [];

    const elements = lines.map((line, idx) => {
      const trimmed = line.trim();

      // Table parsing
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        inTable = true;
        const cells = trimmed.split('|').map(c => c.trim()).filter((_, i, arr) => i > 0 && i < arr.length - 1);
        
        if (trimmed.includes('---')) {
          // Alignment separator, skip rendering
          return null;
        }
        
        if (tableHeaders.length === 0) {
          tableHeaders = cells;
          return null;
        } else {
          tableRows.push(cells);
          return null;
        }
      } else if (inTable) {
        inTable = false;
        const headers = [...tableHeaders];
        const rows = [...tableRows];
        tableHeaders = [];
        tableRows = [];
        
        return (
          <div key={`table-${idx}`} style={{ overflowX: 'auto', margin: '20px 0' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-secondary)', borderBottom: '2px solid var(--border-color)' }}>
                  {headers.map((h, i) => (
                    <th key={i} style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold', border: '1px solid var(--border-color)' }}>
                      {h.replace(/\*\*/g, '')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, ri) => (
                  <tr key={ri} style={{ borderBottom: '1px solid var(--border-color)', background: ri % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)' }}>
                    {row.map((cell, ci) => (
                      <td key={ci} style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                        {cell.startsWith('**') && cell.endsWith('**') ? <strong>{cell.replace(/\*\*/g, '')}</strong> : cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }

      // Headers
      if (trimmed.startsWith('# ')) {
        return <h1 key={idx} style={{ fontSize: '1.75rem', fontWeight: '800', margin: '24px 0 16px 0', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>{trimmed.slice(2)}</h1>;
      }
      if (trimmed.startsWith('## ')) {
        return <h2 key={idx} style={{ fontSize: '1.35rem', fontWeight: '700', margin: '20px 0 12px 0', color: 'var(--color-accent)' }}>{trimmed.slice(3)}</h2>;
      }
      if (trimmed.startsWith('### ')) {
        return <h3 key={idx} style={{ fontSize: '1.1rem', fontWeight: '600', margin: '16px 0 8px 0' }}>{trimmed.slice(4)}</h3>;
      }

      // Horizontal Rule
      if (trimmed === '---') {
        return <hr key={idx} style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: '24px 0' }} />;
      }

      // Bullet points
      if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
        const boldMatch = trimmed.slice(2).match(/^\*\*(.*?)\*\*:(.*)/);
        if (boldMatch) {
          return (
            <li key={idx} style={{ marginLeft: '20px', marginBottom: '8px', listStyleType: 'square' }}>
              <strong>{boldMatch[1]}</strong>: {boldMatch[2]}
            </li>
          );
        }
        return <li key={idx} style={{ marginLeft: '20px', marginBottom: '6px' }}>{trimmed.slice(2)}</li>;
      }

      // Skip empty lines
      if (!trimmed) return <div key={idx} style={{ height: '12px' }} />;

      // Fallback: normal paragraph, replace inline bolding
      const renderInlineBolding = (txt: string) => {
        const parts = txt.split('**');
        return parts.map((part, i) => i % 2 === 1 ? <strong key={i} style={{ color: 'var(--text-primary)' }}>{part}</strong> : part);
      };

      return <p key={idx} style={{ marginBottom: '12px', lineHeight: '1.6', color: 'var(--text-secondary)' }}>{renderInlineBolding(trimmed)}</p>;
    });

    return <div>{elements}</div>;
  };

  const getWinnerColor = (w: string | null) => {
    if (w === 'Pro') return 'var(--color-pro)';
    if (w === 'Con') return 'var(--color-con)';
    return 'var(--text-muted)';
  };

  return (
    <div className="container" style={{ padding: '32px 24px', display: 'grid', gridTemplateColumns: '320px 1fr', gap: '32px', flex: '1' }}>
      
      {/* LEFT COLUMN: Controls & History */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* New Debate Form */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.15rem', marginBottom: '16px', fontWeight: '700' }}>Create Debate</h2>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label htmlFor="topic-input" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: '500' }}>Debate Topic</label>
              <textarea
                id="topic-input"
                placeholder="e.g., Should AI replace university exams?"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                required
                disabled={loading}
                style={{
                  minHeight: '80px',
                  padding: '12px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--bg-input)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                  resize: 'vertical',
                  fontFamily: 'var(--font-sans)',
                  outline: 'none'
                }}
              />
            </div>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading || !topic.trim()}
              style={{ width: '100%', padding: '12px' }}
            >
              {loading ? 'Starting...' : 'Launch Agents'}
            </button>
          </form>
        </div>

        {/* History List */}
        <div className="glass-card" style={{ padding: '24px', flex: '1', display: 'flex', flexDirection: 'column', minHeight: '350px' }}>
          <h2 style={{ fontSize: '1.15rem', marginBottom: '16px', fontWeight: '700' }}>Debates History</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto', flex: '1', maxHeight: '500px' }}>
            {debates.length === 0 ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '20px' }}>
                No debates generated yet. Enter a topic above to initiate.
              </div>
            ) : (
              debates.map((deb) => {
                const isSelected = selectedDebate?.id === deb.id;
                
                return (
                  <div
                    key={deb.id}
                    onClick={() => {
                      setSelectedDebate(deb);
                      fetchDebateDetails(deb.id);
                      if (['pending', 'orchestrating', 'researching', 'pro_arguing', 'con_arguing', 'cross_examining', 'detecting_fallacies', 'verifying_evidence', 'judging', 'generating_report'].includes(deb.status)) {
                        startPolling(deb.id);
                      } else {
                        stopPolling();
                      }
                      setActiveTab('overview');
                    }}
                    style={{
                      padding: '14px',
                      borderRadius: '8px',
                      backgroundColor: isSelected ? 'rgba(255, 255, 255, 0.04)' : 'rgba(255, 255, 255, 0.01)',
                      border: isSelected ? '1px solid var(--color-accent)' : '1px solid var(--border-color)',
                      cursor: 'pointer',
                      transition: 'all var(--transition-fast)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
                      <span style={{ fontSize: '0.9rem', fontWeight: '600', lineHeight: '1.3', color: isSelected ? 'var(--color-accent)' : 'var(--text-primary)' }}>
                        {deb.topic}
                      </span>
                      <button 
                        onClick={(e) => handleDelete(deb.id, e)}
                        style={{ background: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', opacity: 0.6 }}
                        title="Delete Debate"
                      >
                        ×
                      </button>
                    </div>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem' }}>
                      {getStatusBadge(deb.status)}
                      {deb.winner && (
                        <span style={{ 
                          fontWeight: '700', 
                          color: getWinnerColor(deb.winner),
                          backgroundColor: 'rgba(255, 255, 255, 0.02)',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          border: `1px solid ${getWinnerColor(deb.winner)}`
                        }}>
                          {deb.winner === 'Tie' ? 'Tie' : `${deb.winner} Won`}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

      </div>

      {/* RIGHT COLUMN: Active Arena */}
      <div className="glass-card" style={{ padding: '32px', display: 'flex', flexDirection: 'column', minHeight: '600px' }}>
        
        {!selectedDebate ? (
          /* Landing State */
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', flex: '1', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
            <div style={{ 
              width: '64px', 
              height: '64px', 
              borderRadius: '16px', 
              background: 'linear-gradient(135deg, var(--color-accent) 0%, var(--color-pro) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2rem',
              boxShadow: 'var(--shadow-neon-accent)',
              marginBottom: '24px'
            }}>
              🧠
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: '800', marginBottom: '12px' }}>AI Debate Arena</h1>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', fontSize: '0.95rem' }}>
              Launch a multi-agent reasoning simulation. Watch the Orchestrator frame a topic, the Research Analyst extract evidence, the Pro/Con debaters construct arguments, and the Logic Auditor identify fallacies. An automated Judge will evaluate the debate and generate a full scorecard.
            </p>
            <div style={{ display: 'flex', gap: '16px', marginTop: '32px', flexWrap: 'wrap', justifyContent: 'center' }}>
              <div className="glass-card" style={{ padding: '16px', width: '220px', textAlign: 'left' }}>
                <div style={{ fontSize: '1.25rem', marginBottom: '8px' }}>🕵️‍♂️ RAG Retrieval</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Fetches live studies, experts and statistics before generating debate claims.</div>
              </div>
              <div className="glass-card" style={{ padding: '16px', width: '220px', textAlign: 'left' }}>
                <div style={{ fontSize: '1.25rem', marginBottom: '8px' }}>⚖️ Logic & Citation Audit</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Flags slippery slopes, hasty generalizations, and checks citation alignment.</div>
              </div>
            </div>
          </div>
        ) : (
          /* Debate Details State */
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%', flex: '1' }}>
            
            {/* Header info */}
            <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '20px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
                <div style={{ flex: '1' }}>
                  <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--color-accent)', fontWeight: '600' }}>
                    Active Motion
                  </span>
                  <h1 style={{ fontSize: '1.6rem', fontWeight: '800', marginTop: '4px', marginBottom: '8px', lineHeight: '1.2' }}>
                    {selectedDebate.topic}
                  </h1>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {getStatusBadge(selectedDebate.status)}
                </div>
              </div>
              
              {/* Show Winner Scorecard if completed */}
              {selectedDebate.status === 'completed' && (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '24px', 
                  marginTop: '16px',
                  padding: '16px',
                  borderRadius: '8px',
                  backgroundColor: 'rgba(255, 255, 255, 0.01)',
                  border: '1px solid var(--border-color)',
                  width: 'fit-content'
                }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Debate Verdict</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: '800', color: getWinnerColor(selectedDebate.winner) }}>
                      {selectedDebate.winner === 'Tie' ? 'Round Declared Tie' : `${selectedDebate.winner?.toUpperCase()} WINS`}
                    </div>
                  </div>
                  <div style={{ width: '1px', height: '36px', backgroundColor: 'var(--border-color)' }} />
                  <div style={{ display: 'flex', gap: '16px', textAlign: 'center' }}>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--color-pro)', fontWeight: '600' }}>PRO SCORE</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: '800', color: 'var(--color-pro)' }}>{selectedDebate.pro_score ?? 85}</div>
                    </div>
                    <div style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>:</div>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--color-con)', fontWeight: '600' }}>CON SCORE</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: '800', color: 'var(--color-con)' }}>{selectedDebate.con_score ?? 85}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {selectedDebate.status === 'failed' ? (
              /* Error State */
              <div style={{ padding: '24px', borderRadius: '8px', border: '1px solid var(--color-error)', backgroundColor: 'rgba(239, 68, 68, 0.05)', color: 'var(--text-primary)', margin: 'auto 0' }}>
                <h3 style={{ fontWeight: '700', marginBottom: '8px' }}>Debate Execution Failed</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  An error occurred while compiling the LangGraph agents.
                </p>
                <code style={{ fontSize: '0.8rem', whiteSpace: 'pre-wrap', display: 'block', backgroundColor: 'black', padding: '12px', borderRadius: '6px', overflowX: 'auto', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
                  {selectedDebate.error_message || 'Unknown graph process execution exception.'}
                </code>
              </div>
            ) : ['pending', 'orchestrating', 'researching', 'pro_arguing', 'con_arguing', 'cross_examining', 'detecting_fallacies', 'verifying_evidence', 'judging', 'generating_report'].includes(selectedDebate.status) ? (
              /* Polling / Running State */
              <div style={{ margin: 'auto 0', padding: '20px 0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                  <div className="spinner" style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    border: '3px solid rgba(139, 92, 246, 0.1)',
                    borderTopColor: 'var(--color-accent)',
                    animation: 'spin 1s linear infinite'
                  }} />
                  <div>
                    <h2 style={{ fontSize: '1.15rem', fontWeight: '700' }}>Agents are debating...</h2>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Polling server for active step transcripts. This takes ~15-20 seconds.</p>
                  </div>
                </div>
                {renderAgentProgress(selectedDebate.status)}
                
                <style jsx global>{`
                  @keyframes spin {
                    to { transform: rotate(360deg); }
                  }
                `}</style>
              </div>
            ) : (
              /* Completed State - Tabs & Transcripts */
              <div style={{ display: 'flex', flexDirection: 'column', flex: '1' }}>
                
                {/* Tabs */}
                <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '24px', gap: '8px', overflowX: 'auto' }}>
                  {[
                    { id: 'overview', label: 'Overview' },
                    { id: 'transcript', label: 'Debate Transcript' },
                    { id: 'crossexam', label: 'Cross-Examination' },
                    { id: 'audit', label: 'Fallacies & Citations' },
                    { id: 'report', label: 'Judge Report' }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      style={{
                        padding: '10px 16px',
                        fontSize: '0.9rem',
                        fontWeight: '600',
                        color: activeTab === tab.id ? 'var(--color-accent)' : 'var(--text-secondary)',
                        borderBottom: '2px solid',
                        borderColor: activeTab === tab.id ? 'var(--color-accent)' : 'transparent',
                        background: 'none',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                        transition: 'all var(--transition-fast)'
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Tab Contents */}
                <div style={{ flex: '1' }}>
                  
                  {/* OVERVIEW TAB */}
                  {activeTab === 'overview' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                      <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid var(--color-accent)' }}>
                        <h3 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--color-accent)', textTransform: 'uppercase', marginBottom: '8px' }}>Neutral Framing</h3>
                        <p style={{ fontSize: '0.95rem', lineHeight: '1.6', color: 'var(--text-secondary)' }}>
                          {selectedDebate.report?.split('\n').find(l => l.includes('The debate centers on') || l.includes('This debate examines'))?.replace(/^\*/, '').replace(/\*$/, '') || 
                           `Structured evaluation framing for: "${selectedDebate.topic}".`}
                        </p>
                      </div>

                      {/* Scope Tags */}
                      <div>
                        <h3 style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '10px' }}>Debate Dimensions</h3>
                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                          {selectedDebate.scope?.split(',').map((tag) => (
                            <span key={tag} style={{ fontSize: '0.8rem', padding: '6px 12px', borderRadius: '6px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                              🌐 {tag.trim()}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Evidence Pool */}
                      <div>
                        <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '12px' }}>Retrieved Evidence Pool (RAG)</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                          {selectedDebate.evidence_items?.map((ev) => (
                            <div key={ev.id} className="glass-card" style={{ padding: '16px', background: 'rgba(255,255,255,0.01)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                                <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--color-accent)' }}>{ev.source}</span>
                                <span style={{ 
                                  fontSize: '0.75rem', 
                                  padding: '2px 6px', 
                                  borderRadius: '4px', 
                                  backgroundColor: 'rgba(16, 185, 129, 0.05)', 
                                  border: '1px solid rgba(16, 185, 129, 0.2)',
                                  color: 'var(--color-success)'
                                }}>
                                  Confidence: {Math.round(ev.confidence * 100)}%
                                </span>
                              </div>
                              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>"{ev.claim}"</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TRANSCRIPT TAB */}
                  {activeTab === 'transcript' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                      
                      {/* PRO COLUMN */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '2px solid var(--color-pro)', paddingBottom: '8px' }}>
                          <span style={{ fontSize: '1.2rem' }}>🔵</span>
                          <h2 style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--color-pro)', textTransform: 'uppercase' }}>Pro arguments</h2>
                        </div>

                        {selectedDebate.pro_opening && (
                          <div className="glass-card" style={{ padding: '16px', background: 'rgba(0, 242, 254, 0.01)', borderLeft: '3px solid var(--color-pro)' }}>
                            <h4 style={{ fontSize: '0.8rem', color: 'var(--color-pro)', textTransform: 'uppercase', marginBottom: '6px', fontWeight: '700' }}>Opening Statement</h4>
                            <p style={{ fontSize: '0.85rem', lineHeight: '1.5', color: 'var(--text-secondary)' }}>"{selectedDebate.pro_opening}"</p>
                          </div>
                        )}

                        {selectedDebate.arguments?.filter(a => a.side === 'Pro').map((arg) => (
                          <div key={arg.id} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <h3 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-primary)' }}>{arg.claim}</h3>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                              <strong style={{ color: 'var(--color-pro)' }}>Evidence:</strong> {arg.evidence}
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                              <strong style={{ color: 'var(--color-pro)' }}>Impact:</strong> {arg.impact}
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* CON COLUMN */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '2px solid var(--color-con)', paddingBottom: '8px' }}>
                          <span style={{ fontSize: '1.2rem' }}>🔴</span>
                          <h2 style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--color-con)', textTransform: 'uppercase' }}>Con arguments</h2>
                        </div>

                        {selectedDebate.con_opening && (
                          <div className="glass-card" style={{ padding: '16px', background: 'rgba(255, 8, 68, 0.01)', borderLeft: '3px solid var(--color-con)' }}>
                            <h4 style={{ fontSize: '0.8rem', color: 'var(--color-con)', textTransform: 'uppercase', marginBottom: '6px', fontWeight: '700' }}>Opening Statement</h4>
                            <p style={{ fontSize: '0.85rem', lineHeight: '1.5', color: 'var(--text-secondary)' }}>"{selectedDebate.con_opening}"</p>
                          </div>
                        )}

                        {selectedDebate.arguments?.filter(a => a.side === 'Con').map((arg) => (
                          <div key={arg.id} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <h3 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-primary)' }}>{arg.claim}</h3>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                              <strong style={{ color: 'var(--color-con)' }}>Evidence:</strong> {arg.evidence}
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                              <strong style={{ color: 'var(--color-con)' }}>Impact:</strong> {arg.impact}
                            </div>
                          </div>
                        ))}
                      </div>

                    </div>
                  )}

                  {/* CROSS EXAMINATION TAB */}
                  {activeTab === 'crossexam' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {selectedDebate.rebuttals?.map((reb) => (
                        <div 
                          key={reb.id} 
                          className="glass-card" 
                          style={{ 
                            padding: '20px', 
                            borderLeft: '4px solid',
                            borderColor: reb.side === 'Pro' ? 'var(--color-pro)' : 'var(--color-con)',
                            background: reb.side === 'Pro' ? 'rgba(0, 242, 254, 0.005)' : 'rgba(255, 8, 68, 0.005)'
                          }}
                        >
                          <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: reb.side === 'Pro' ? 'var(--color-pro)' : 'var(--color-con)', marginBottom: '8px' }}>
                            {reb.side === 'Pro' ? 'Pro Cross-Examiner' : 'Con Cross-Examiner'} Rebuttal
                          </div>
                          
                          <div style={{ marginBottom: '12px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                            Target Claim: <span style={{ fontStyle: 'italic' }}>"{
                              selectedDebate.arguments?.find(a => a.id === reb.target_argument_id)?.claim || 'Opposing Argument'
                            }"</span>
                          </div>
                          
                          <div style={{ marginBottom: '8px', fontSize: '0.95rem', fontWeight: '600' }}>
                            {reb.claim}
                          </div>
                          
                          <div style={{ 
                            fontSize: '0.9rem', 
                            color: reb.side === 'Pro' ? 'var(--color-pro)' : 'var(--color-con)', 
                            fontWeight: '600',
                            padding: '8px 12px',
                            backgroundColor: 'rgba(255, 255, 255, 0.01)',
                            borderRadius: '4px',
                            border: '1px solid rgba(255, 255, 255, 0.03)',
                            marginTop: '12px'
                          }}>
                            Question: {reb.question}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* AUDIT TAB (FALLACIES & VERIFICATIONS) */}
                  {activeTab === 'audit' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                      
                      {/* FALLACIES SECTION */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        <h2 style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--color-warning)', textTransform: 'uppercase', borderBottom: '2px solid var(--color-warning)', paddingBottom: '8px' }}>
                          ⚠️ Logic Auditor
                        </h2>
                        
                        {selectedDebate.fallacies?.length === 0 ? (
                          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No logical fallacies detected. Excellent logical integrity.</p>
                        ) : (
                          selectedDebate.fallacies?.map((f) => {
                            const arg = selectedDebate.arguments?.find(a => a.id === f.argument_id);
                            return (
                              <div key={f.id} className="glass-card" style={{ padding: '20px', borderLeft: '3px solid var(--color-warning)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                  <span style={{ fontWeight: '700', fontSize: '0.95rem', color: 'var(--color-warning)' }}>{f.type}</span>
                                  <span style={{ 
                                    fontSize: '0.75rem', 
                                    padding: '2px 6px', 
                                    borderRadius: '4px', 
                                    backgroundColor: `rgba(245, 158, 11, 0.05)`, 
                                    border: `1px solid rgba(245, 158, 11, 0.2)`,
                                    color: 'var(--color-warning)',
                                    fontWeight: '600'
                                  }}>
                                    Severity: {Math.round(f.severity * 100)}%
                                  </span>
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                                  Target Argument: "{arg ? arg.claim : 'Unknown claim'}"
                                </div>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>{f.explanation}</p>
                              </div>
                            );
                          })
                        )}
                      </div>

                      {/* VERIFICATIONS SECTION */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        <h2 style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--color-success)', textTransform: 'uppercase', borderBottom: '2px solid var(--color-success)', paddingBottom: '8px' }}>
                          ✓ Citation Verifier
                        </h2>
                        
                        {selectedDebate.verifications?.length === 0 ? (
                          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No citations audited in this round.</p>
                        ) : (
                          selectedDebate.verifications?.map((v) => {
                            const isSupported = v.status === 'supported';
                            const isPartial = v.status === 'partially supported';
                            
                            const statusColor = isSupported ? 'var(--color-success)' : isPartial ? 'var(--color-warning)' : 'var(--color-error)';
                            const statusBg = isSupported ? 'rgba(16, 185, 129, 0.05)' : isPartial ? 'rgba(245, 158, 11, 0.05)' : 'rgba(239, 68, 68, 0.05)';
                            
                            return (
                              <div key={v.id} className="glass-card" style={{ padding: '20px', borderLeft: `3px solid ${statusColor}` }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '600' }}>Citation Audit</span>
                                  <span style={{ 
                                    fontSize: '0.75rem', 
                                    padding: '2px 6px', 
                                    borderRadius: '4px', 
                                    backgroundColor: statusBg,
                                    border: `1px solid ${statusColor}`,
                                    color: statusColor,
                                    fontWeight: '700',
                                    textTransform: 'uppercase'
                                  }}>
                                    {v.status}
                                  </span>
                                </div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: '600', marginBottom: '6px' }}>
                                  Claim: "{v.claim}"
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                                  Evidence: <span style={{ fontStyle: 'italic' }}>"{v.evidence_used}"</span>
                                </div>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>{v.reasoning}</p>
                              </div>
                            );
                          })
                        )}
                      </div>

                    </div>
                  )}

                  {/* REPORT TAB */}
                  {activeTab === 'report' && (
                    <div className="glass-card" style={{ padding: '32px', backgroundColor: 'var(--bg-secondary)', overflowY: 'auto', maxHeight: '700px' }}>
                      {renderMarkdown(selectedDebate.report)}
                    </div>
                  )}

                </div>
              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
}
