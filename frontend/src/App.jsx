import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar/Sidebar';
import ChatContainer from './components/Chat/ChatContainer';
import ChatInput from './components/Chat/ChatInput';
import DocumentManager from './components/Upload/DocumentManager';
import MemoryManager from './components/Memory/MemoryManager';
import ErrorBanner from './components/common/ErrorBanner';
import { apiService } from './services/api';

export default function App() {
  const [userId, setUserId] = useState(1);
  const [healthStatus, setHealthStatus] = useState('healthy');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // In-memory session-based Recent Chats (without backend modifications)
  const [sessions, setSessions] = useState([
    { id: 'sess_default', title: 'New Conversation', messages: [] }
  ]);
  const [activeSessionId, setActiveSessionId] = useState('sess_default');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDocsOpen, setIsDocsOpen] = useState(false);
  const [isMemoryOpen, setIsMemoryOpen] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [memoryCount, setMemoryCount] = useState(0);

  // Active messages derived from current session
  const currentSession = sessions.find((s) => s.id === activeSessionId) || sessions[0];
  const messages = currentSession ? currentSession.messages : [];

  // Check health periodically against real GET /health
  const checkBackendHealth = useCallback(async () => {
    try {
      const health = await apiService.checkHealth();
      setHealthStatus(health.status || 'offline');
    } catch {
      setHealthStatus('offline');
    }
  }, []);

  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 15000);
    return () => clearInterval(interval);
  }, [checkBackendHealth]);

  // Refresh documents and memories on user switch
  const refreshContextData = useCallback(async () => {
    if (!userId) return;
    try {
      const docs = await apiService.getDocuments(userId);
      setDocuments(Array.isArray(docs) ? docs : []);

      const mems = await apiService.getMemories(userId);
      setMemoryCount(Array.isArray(mems) ? mems.length : 0);
    } catch {
      // Quiet catch if server offline
    }
  }, [userId]);

  useEffect(() => {
    refreshContextData();
  }, [refreshContextData]);

  // Session Management
  const handleNewChat = () => {
    const newId = `sess_${Date.now()}`;
    const newSession = {
      id: newId,
      title: 'New Conversation',
      messages: [],
    };
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newId);
    setError(null);
  };

  const handleSelectSession = (id) => {
    setActiveSessionId(id);
    setError(null);
  };

  const handleDeleteSession = (id) => {
    setSessions((prev) => {
      const updated = prev.filter((s) => s.id !== id);
      if (updated.length === 0) {
        const fallback = { id: `sess_${Date.now()}`, title: 'New Conversation', messages: [] };
        setActiveSessionId(fallback.id);
        return [fallback];
      }
      if (activeSessionId === id) {
        setActiveSessionId(updated[0].id);
      }
      return updated;
    });
  };

  // Helper to update active session messages
  const updateActiveMessages = (updater) => {
    setSessions((prevSessions) =>
      prevSessions.map((s) => {
        if (s.id === activeSessionId) {
          const newMsgs = typeof updater === 'function' ? updater(s.messages) : updater;
          // Dynamically derive thread title from first user prompt
          let newTitle = s.title;
          if (s.title === 'New Conversation' && newMsgs.length > 0) {
            const firstUserMsg = newMsgs.find((m) => m.role === 'user');
            if (firstUserMsg) {
              newTitle = firstUserMsg.content.slice(0, 26) + (firstUserMsg.content.length > 26 ? '...' : '');
            }
          }
          return { ...s, title: newTitle, messages: newMsgs };
        }
        return s;
      })
    );
  };

  // Real Chat Handler
  const handleSendMessage = async (queryText) => {
    if (!queryText.trim() || isLoading) return;

    setError(null);
    const userMsgId = `user_${Date.now()}`;
    const userMessage = {
      id: userMsgId,
      role: 'user',
      content: queryText,
    };

    updateActiveMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await apiService.sendChatMessage(userId, queryText);

      const assistantMessage = {
        id: `asst_${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        answer: response.answer,
        status: response.status, // 'SUPPORTED' | 'UNCERTAIN' | 'CONFLICTING'
        sources: response.sources || [],
        claims: response.claims || [],
        uncertainty_reason: response.uncertainty_reason || null,
      };

      updateActiveMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat query error:', err);

      let errText = 'Something went wrong while processing your request.';
      if (err.message?.includes('Failed to fetch') || healthStatus === 'offline') {
        errText = "VeriMind can't reach the backend. Make sure the FastAPI server is running on port 8000.";
      } else if (err.message) {
        errText = err.message;
      }

      setError(errText);

      const errorMessage = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: `Error: ${errText}`,
        answer: errText,
        status: 'UNCERTAIN',
        uncertainty_reason: errText,
        sources: [],
      };
      updateActiveMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      checkBackendHealth();
    }
  };

  return (
    <div className="verimind-app">
      <Header
        healthStatus={healthStatus}
        userId={userId}
        setUserId={setUserId}
        onOpenDocuments={() => setIsDocsOpen(true)}
        onOpenMemory={() => setIsMemoryOpen(true)}
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        docCount={documents.length}
        memoryCount={memoryCount}
      />

      <div className="app-body">
        <Sidebar
          isOpen={isSidebarOpen}
          onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
          onNewChat={handleNewChat}
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onDeleteSession={handleDeleteSession}
          docCount={documents.length}
          documents={documents}
          onOpenDocuments={() => setIsDocsOpen(true)}
          memoryCount={memoryCount}
          onOpenMemory={() => setIsMemoryOpen(true)}
          userId={userId}
        />

        <main className="chat-viewport">
          <ErrorBanner error={error} onDismiss={() => setError(null)} />

          <ChatContainer
            messages={messages}
            isLoading={isLoading}
            onSampleClick={handleSendMessage}
            userId={userId}
          />

          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            isBackendOffline={healthStatus === 'offline'}
            onOpenUpload={() => setIsDocsOpen(true)}
          />
        </main>
      </div>

      <DocumentManager
        isOpen={isDocsOpen}
        onClose={() => setIsDocsOpen(false)}
        userId={userId}
        onDocumentsUpdated={(count, docsList) => {
          setDocuments(docsList || []);
        }}
      />

      <MemoryManager
        isOpen={isMemoryOpen}
        onClose={() => setIsMemoryOpen(false)}
        userId={userId}
        onMemoriesUpdated={(count) => setMemoryCount(count)}
      />
    </div>
  );
}
