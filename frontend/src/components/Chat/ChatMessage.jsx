import React, { useState } from 'react';
import { CheckCircle2, HelpCircle, AlertOctagon, Sparkles, FileText, ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, ShieldCheck, User } from 'lucide-react';
import { apiService } from '../../services/api';

export default function ChatMessage({ message, userId }) {
  const isUser = message.role === 'user';
  const [expandedSources, setExpandedSources] = useState({});
  const [feedbackState, setFeedbackState] = useState(null); // 'positive' | 'negative'

  const toggleProvenanceDetails = (sourceKey) => {
    setExpandedSources((prev) => ({
      ...prev,
      [sourceKey]: !prev[sourceKey],
    }));
  };

  const handleFeedback = async (rating) => {
    const newState = rating === 1 ? 'positive' : 'negative';
    setFeedbackState(newState);
    try {
      await apiService.submitFeedback(userId, message.id || null, rating, null);
    } catch (err) {
      console.warn('Feedback submission failed:', err);
    }
  };

  if (isUser) {
    return (
      <div className="message-row user">
        <div className="message-bubble user-bubble">
          {message.content}
        </div>
        <div className="message-avatar user-avatar">
          <User size={16} />
        </div>
      </div>
    );
  }

  const { status, answer, sources = [], uncertainty_reason, claims = [] } = message;

  // Render Status Badges
  const renderStatusBadge = () => {
    if (!status) return null;
    switch (status) {
      case 'SUPPORTED':
        return (
          <div className="policy-badge status-supported" title="Answer supported by retrieved document evidence">
            <CheckCircle2 size={14} />
            <span>✓ Verified</span>
            <span className="badge-sub font-mono">Evidence-Backed</span>
          </div>
        );
      case 'UNCERTAIN':
        return (
          <div className="policy-badge status-uncertain" title="Not enough verified evidence in uploaded documents">
            <HelpCircle size={14} />
            <span>? Uncertain</span>
            <span className="badge-sub">Insufficient Evidence</span>
          </div>
        );
      case 'CONFLICTING':
        return (
          <div className="policy-badge status-conflicting" title="Available document sources disagree">
            <AlertOctagon size={14} />
            <span>⚠ Conflicting Evidence</span>
            <span className="badge-sub">Contradiction</span>
          </div>
        );
      case 'GENERAL_KNOWLEDGE':
        return (
          <div className="policy-badge status-general" title="Generated from model knowledge — no uploaded evidence used">
            <Sparkles size={14} />
            <span>✦ General Knowledge</span>
            <span className="badge-sub">Model Only</span>
          </div>
        );
      default:
        return null;
    }
  };

  // Extract source pairs for conflict visualizer if status is CONFLICTING
  const renderConflictVisualizer = () => {
    if (status !== 'CONFLICTING' || sources.length < 2) return null;

    const sourceA = sources[0];
    const sourceB = sources[1];

    return (
      <div className="conflict-comparison-card">
        <div className="conflict-header">
          <AlertOctagon size={16} className="conflict-icon" />
          <span>Contradictory Evidence Discovered</span>
        </div>
        <div className="conflict-grid">
          <div className="conflict-side side-a">
            <div className="conflict-source-label">Source A</div>
            <div className="conflict-filename">
              <FileText size={13} />
              <span>{sourceA.filename}</span>
            </div>
            <div className="conflict-page">Page {sourceA.page || 1}</div>
            <div className="conflict-snippet">"{sourceA.snippet}"</div>
          </div>

          <div className="conflict-vs-badge">VS</div>

          <div className="conflict-side side-b">
            <div className="conflict-source-label">Source B</div>
            <div className="conflict-filename">
              <FileText size={13} />
              <span>{sourceB.filename}</span>
            </div>
            <div className="conflict-page">Page {sourceB.page || 1}</div>
            <div className="conflict-snippet">"{sourceB.snippet}"</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="message-row assistant">
      <div className="message-avatar assistant-avatar">
        <ShieldCheck size={18} />
      </div>
      <div className="message-bubble assistant-bubble">
        {renderStatusBadge()}

        <div className="assistant-answer-text">
          {answer}
        </div>

        {/* Uncertainty Callout */}
        {status === 'UNCERTAIN' && uncertainty_reason && (
          <div className="callout-box uncertain-callout">
            <HelpCircle size={15} className="callout-icon" />
            <div className="callout-text">
              <strong>Verification Note:</strong> {uncertainty_reason}
            </div>
          </div>
        )}

        {/* Conflict Comparison Card */}
        {renderConflictVisualizer()}

        {/* Sources & Provenance Cards */}
        {sources.length > 0 && (
          <div className="sources-container">
            <div className="sources-header-title">
              <FileText size={14} />
              <span>Verified Evidence ({sources.length})</span>
            </div>
            <div className="source-cards-list">
              {sources.map((src, idx) => {
                const sKey = src.source_id || `src_${idx}`;
                const isExpanded = !!expandedSources[sKey];

                return (
                  <div key={sKey} className="evidence-card">
                    <div className="evidence-card-top">
                      <div className="evidence-file">
                        <FileText size={14} className="file-icon" />
                        <span className="file-name">{src.filename}</span>
                      </div>
                      <span className="file-page-tag">Page {src.page || 1}</span>
                    </div>

                    <div className="evidence-snippet">
                      "{src.snippet}"
                    </div>

                    <button
                      className="provenance-toggle-btn"
                      onClick={() => toggleProvenanceDetails(sKey)}
                    >
                      <span>{isExpanded ? 'Hide provenance' : 'View provenance →'}</span>
                      {isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                    </button>

                    {isExpanded && (
                      <div className="provenance-details-panel">
                        <div className="prov-row"><span className="prov-key">Source ID:</span> <span className="prov-val">{src.source_id}</span></div>
                        <div className="prov-row"><span className="prov-key">Document ID:</span> <span className="prov-val">{src.document_id}</span></div>
                        <div className="prov-row"><span className="prov-key">Chunk ID:</span> <span className="prov-val">{src.chunk_id}</span></div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Feedback Actions */}
        <div className="assistant-feedback-bar">
          <span className="feedback-label">Was this answer helpful?</span>
          <button
            className={`feedback-chip ${feedbackState === 'positive' ? 'positive-active' : ''}`}
            onClick={() => handleFeedback(1)}
            title="Mark response as accurate & helpful"
          >
            <ThumbsUp size={13} /> Helpful
          </button>
          <button
            className={`feedback-chip ${feedbackState === 'negative' ? 'negative-active' : ''}`}
            onClick={() => handleFeedback(-1)}
            title="Mark response as unhelpful or ungrounded"
          >
            <ThumbsDown size={13} /> Unhelpful
          </button>
        </div>
      </div>
    </div>
  );
}
