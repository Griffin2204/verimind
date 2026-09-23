import React from 'react';
import { AlertCircle, X } from 'lucide-react';

export default function ErrorBanner({ error, onDismiss }) {
  if (!error) return null;

  return (
    <div className="error-banner">
      <div className="error-banner-content">
        <AlertCircle size={18} className="error-icon" />
        <span className="error-text">{error}</span>
      </div>
      {onDismiss && (
        <button className="error-dismiss-btn" onClick={onDismiss} title="Dismiss notice">
          <X size={15} />
        </button>
      )}
    </div>
  );
}
