import React from 'react';
import { Shield, FileText, Brain, Menu, Plus } from 'lucide-react';

export default function Header({
  healthStatus,
  userId,
  setUserId,
  onOpenDocuments,
  onOpenMemory,
  onToggleSidebar,
  docCount = 0,
  memoryCount = 0
}) {
  const getHealthDetails = () => {
    if (healthStatus === 'healthy' || healthStatus === 'ok') {
      return { text: 'Online', class: 'healthy' };
    }
    if (healthStatus === 'degraded') {
      return { text: 'Degraded', class: 'degraded' };
    }
    return { text: 'Offline', class: 'offline' };
  };

  const health = getHealthDetails();

  return (
    <header className="app-header">
      <div className="header-left">
        <button className="mobile-menu-btn" onClick={onToggleSidebar} title="Toggle Navigation Sidebar">
          <Menu size={20} />
        </button>

        <div className="header-brand">
          <div className="header-logo-badge">
            <Shield size={18} className="brand-logo-icon" />
          </div>
          <div className="header-titles">
            <span className="brand-name">VeriMind</span>
            <span className="brand-tagline">Evidence-Grounded AI Assistant</span>
          </div>
        </div>
      </div>

      <div className="header-right">
        {/* Real Backend Status Indicator */}
        <div className={`health-indicator ${health.class}`} title={`Backend Status: ${health.text}`}>
          <span className={`status-dot ${health.class}`} />
          <span className="health-label">{health.text}</span>
        </div>

        {/* User Switcher */}
        <div className="user-id-badge" title="User ID for isolated documents & memory context">
          <span className="user-label">User:</span>
          <input
            type="number"
            min="1"
            max="999"
            value={userId}
            onChange={(e) => setUserId(Math.max(1, parseInt(e.target.value, 10) || 1))}
            className="user-id-input"
          />
        </div>

        {/* Quick Drawer Action Triggers */}
        <button className="header-btn" onClick={onOpenDocuments} title="Manage Documents">
          <FileText size={16} />
          <span className="btn-label">Docs</span>
          {docCount > 0 && <span className="header-counter-badge">{docCount}</span>}
        </button>

        <button className="header-btn" onClick={onOpenMemory} title="Manage Memory">
          <Brain size={16} />
          <span className="btn-label">Memory</span>
          {memoryCount > 0 && <span className="header-counter-badge">{memoryCount}</span>}
        </button>
      </div>
    </header>
  );
}
