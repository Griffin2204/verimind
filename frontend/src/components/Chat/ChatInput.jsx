import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Paperclip, Loader2 } from 'lucide-react';

export default function ChatInput({ onSendMessage, isLoading, isBackendOffline, onOpenUpload }) {
  const [query, setQuery] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [query]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!query.trim() || isLoading || isBackendOffline) return;
    onSendMessage(query);
    setQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-input-wrapper">
      <form className="input-box-form" onSubmit={handleSubmit}>
        <div className="textarea-container">
          <button
            type="button"
            className="input-attach-btn"
            onClick={onOpenUpload}
            title="Upload Document Evidence"
            disabled={isLoading || isBackendOffline}
          >
            <Paperclip size={18} />
          </button>

          <textarea
            ref={textareaRef}
            className="input-textarea"
            placeholder={
              isBackendOffline
                ? 'VeriMind can\'t reach the backend on port 8000...'
                : 'Ask VeriMind anything...'
            }
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading || isBackendOffline}
            rows={1}
          />

          <button
            type="submit"
            className="input-send-btn"
            disabled={!query.trim() || isLoading || isBackendOffline}
            title="Send Message (Enter)"
          >
            {isLoading ? <Loader2 size={16} className="spin-loader" /> : <ArrowUp size={18} />}
          </button>
        </div>
        <div className="input-disclaimer">
          VeriMind verifies claims against uploaded document evidence. Shift + Enter for line break.
        </div>
      </form>
    </div>
  );
}
