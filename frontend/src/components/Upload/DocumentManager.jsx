import React, { useState, useEffect } from 'react';
import { X, UploadCloud, FileText, Trash2, Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';
import { apiService } from '../../services/api';

export default function DocumentManager({ isOpen, onClose, userId, onDocumentsUpdated }) {
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [statusNotice, setStatusNotice] = useState(null); // { type: 'success'|'error', text: string }

  const loadDocuments = async () => {
    if (!userId) return;
    setIsLoading(true);
    try {
      const data = await apiService.getDocuments(userId);
      const docs = Array.isArray(data) ? data : [];
      setDocuments(docs);
      if (onDocumentsUpdated) {
        onDocumentsUpdated(docs.length, docs);
      }
    } catch (err) {
      console.warn('Failed to load documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadDocuments();
    }
  }, [isOpen, userId]);

  const handleFileUpload = async (file) => {
    if (!file) return;
    setIsUploading(true);
    setStatusNotice(null);
    try {
      const res = await apiService.uploadDocument(userId, file);
      const chunkMsg = res.chunk_count ? ` (${res.chunk_count} chunks indexed)` : '';
      setStatusNotice({
        type: 'success',
        text: `Successfully uploaded "${res.filename}"${chunkMsg}`,
      });
      await loadDocuments();
    } catch (err) {
      setStatusNotice({
        type: 'error',
        text: err.message || 'Unable to upload document.',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Delete document "${filename}"?`)) return;
    try {
      await apiService.deleteDocument(docId);
      await loadDocuments();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="panel-overlay" onClick={onClose} />
      <div className="panel-drawer">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">Documents</h3>
            <p className="panel-subtitle">Manage the evidence available to VeriMind.</p>
          </div>
          <button className="panel-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="panel-body">
          {/* Upload Dropzone */}
          <label className="upload-box">
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              style={{ display: 'none' }}
              disabled={isUploading}
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />
            {isUploading ? (
              <div className="upload-state-loading">
                <Loader2 size={24} className="spin-loader text-blue" />
                <span>Indexing Document Evidence...</span>
              </div>
            ) : (
              <div className="upload-state-idle">
                <UploadCloud size={28} className="upload-icon" />
                <span className="upload-main-text">Upload Document Evidence</span>
                <span className="upload-sub-text">Supported formats: PDF, DOCX, TXT</span>
              </div>
            )}
          </label>

          {statusNotice && (
            <div className={`status-notice-box ${statusNotice.type}`}>
              {statusNotice.type === 'success' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
              <span>{statusNotice.text}</span>
            </div>
          )}

          <div className="list-section-header">
            <span>Indexed Documents ({documents.length})</span>
          </div>

          {isLoading ? (
            <div className="panel-loader">
              <Loader2 size={20} className="spin-loader" />
            </div>
          ) : documents.length === 0 ? (
            <div className="empty-panel-state">
              <FileText size={32} className="empty-state-icon" />
              <div className="empty-state-title">No documents yet</div>
              <div className="empty-state-desc">
                Upload documents to give VeriMind additional verified evidence.
              </div>
            </div>
          ) : (
            <div className="documents-grid">
              {documents.map((doc) => (
                <div key={doc.id} className="doc-card">
                  <div className="doc-card-main">
                    <FileText size={18} className="doc-type-icon" />
                    <div className="doc-details">
                      <span className="doc-title">{doc.filename}</span>
                      <div className="doc-tags">
                        <span className="doc-tag">ID: {doc.id}</span>
                        {doc.chunk_count !== undefined && doc.chunk_count !== null && (
                          <span className="doc-tag">{doc.chunk_count} chunks</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <button
                    className="doc-delete-btn"
                    onClick={() => handleDelete(doc.id, doc.filename)}
                    title="Remove document evidence"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
