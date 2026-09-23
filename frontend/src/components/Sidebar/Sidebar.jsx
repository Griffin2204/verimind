import React from 'react';
import { Shield, Plus, MessageSquare, FileText, Brain, Trash2, ChevronLeft, ChevronRight, UploadCloud, X } from 'lucide-react';

export default function Sidebar({
  isOpen,
  onToggleSidebar,
  onNewChat,
  sessions = [],
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  docCount = 0,
  documents = [],
  onOpenDocuments,
  onDeleteDocument,
  memoryCount = 0,
  onOpenMemory,
  userId
}) {
  return (
    <>
      {/* Mobile Drawer Overlay */}
      {isOpen && <div className="sidebar-mobile-overlay" onClick={onToggleSidebar} />}

      <aside className={`app-sidebar ${isOpen ? 'open' : 'collapsed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="logo-icon-wrapper">
              <Shield size={20} className="logo-shield" />
            </div>
            {isOpen && (
              <div className="brand-text-container">
                <span className="brand-name">VeriMind</span>
                <span className="brand-sub">Evidence AI</span>
              </div>
            )}
          </div>
          <button
            className="sidebar-toggle-btn"
            onClick={onToggleSidebar}
            title={isOpen ? "Collapse Sidebar" : "Expand Sidebar"}
          >
            {isOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
          </button>
        </div>

        {/* New Chat Button */}
        <div className="sidebar-action-container">
          <button className="btn-new-chat" onClick={onNewChat} title="Start New Conversation">
            <Plus size={18} />
            {isOpen && <span>New Chat</span>}
          </button>
        </div>

        <div className="sidebar-scroll-content">
          {/* Recent Conversations Section */}
          <div className="sidebar-section">
            {isOpen && <div className="section-label">Recent Chats</div>}
            <div className="session-list">
              {sessions.length === 0 ? (
                isOpen && <div className="empty-sidebar-note">No recent sessions</div>
              ) : (
                sessions.map((sess) => {
                  const isActive = sess.id === activeSessionId;
                  const title = sess.title || 'Conversation';
                  return (
                    <div
                      key={sess.id}
                      className={`session-item ${isActive ? 'active' : ''}`}
                      onClick={() => onSelectSession(sess.id)}
                      title={title}
                    >
                      <MessageSquare size={16} className="session-icon" />
                      {isOpen && (
                        <>
                          <span className="session-title">{title}</span>
                          {sessions.length > 1 && (
                            <button
                              className="session-delete-btn"
                              onClick={(e) => {
                                e.stopPropagation();
                                onDeleteSession(sess.id);
                              }}
                              title="Delete Session"
                            >
                              <X size={14} />
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Documents Section */}
          <div className="sidebar-section">
            {isOpen && (
              <div className="section-label-header">
                <span className="section-label">Documents ({docCount})</span>
                <button className="section-action-btn" onClick={onOpenDocuments} title="Manage Documents">
                  <UploadCloud size={14} />
                </button>
              </div>
            )}
            <div className="compact-doc-list">
              {documents.length === 0 ? (
                isOpen && <div className="empty-sidebar-note">No documents uploaded</div>
              ) : (
                documents.slice(0, 5).map((doc) => (
                  <div key={doc.id} className="compact-doc-item" onClick={onOpenDocuments} title={doc.filename}>
                    <FileText size={15} className="doc-icon" />
                    {isOpen && (
                      <div className="compact-doc-info">
                        <span className="compact-doc-name">{doc.filename}</span>
                        {doc.chunk_count && <span className="compact-doc-meta">{doc.chunk_count} chunks</span>}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Memory Section */}
          <div className="sidebar-section">
            {isOpen && (
              <div className="section-label-header">
                <span className="section-label">User Memory ({memoryCount})</span>
                <button className="section-action-btn" onClick={onOpenMemory} title="Manage Memory">
                  <Brain size={14} />
                </button>
              </div>
            )}
            <button className="compact-memory-card" onClick={onOpenMemory} title="Open Persistent Memory Manager">
              <Brain size={16} className="memory-icon" />
              {isOpen && (
                <div className="memory-card-text">
                  <span className="memory-title">Memory Manager</span>
                  <span className="memory-sub">User {userId} Context</span>
                </div>
              )}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
