import React, { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import { Shield, Sparkles, FileSearch, Scale, Code } from 'lucide-react';

export default function ChatContainer({ messages, isLoading, onSampleClick, userId }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const samplePrompts = [
    {
      title: "Operating Voltage Query",
      prompt: "What is the operating voltage of the Aurora X1?",
      icon: Sparkles,
      tag: "Verification"
    },
    {
      title: "Document Summary",
      prompt: "Summarize my uploaded document.",
      icon: FileSearch,
      tag: "Ingestion"
    },
    {
      title: "Contradiction Check",
      prompt: "Find conflicting information in my documents.",
      icon: Scale,
      tag: "Conflict"
    },
    {
      title: "General Knowledge",
      prompt: "What is polymorphism in Java?",
      icon: Code,
      tag: "Knowledge"
    }
  ];

  if (messages.length === 0) {
    return (
      <div className="chat-container empty-container">
        <div className="verimind-landing-hero">
          <div className="landing-shield-wrapper">
            <Shield size={36} className="landing-shield-icon" />
          </div>
          <h1 className="landing-title">VeriMind</h1>
          <div className="landing-subtitle">Evidence-Grounded AI Assistant</div>
          <p className="landing-tagline">
            Ask questions. Get evidence. Know when the answer isn't certain.
          </p>

          <div className="sample-prompts-grid">
            {samplePrompts.map((item, idx) => {
              const IconComp = item.icon;
              return (
                <div
                  key={idx}
                  className="sample-prompt-card"
                  onClick={() => onSampleClick(item.prompt)}
                >
                  <div className="card-top-row">
                    <IconComp size={18} className="card-icon" />
                    <span className="card-tag">{item.tag}</span>
                  </div>
                  <div className="card-prompt-text">"{item.prompt}"</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="messages-flow">
        {messages.map((msg, index) => (
          <ChatMessage key={msg.id || index} message={msg} userId={userId} />
        ))}

        {isLoading && (
          <div className="message-row assistant">
            <div className="message-avatar assistant-avatar pulse-avatar">
              <Shield size={18} />
            </div>
            <div className="message-bubble assistant-bubble loading-bubble">
              <div className="thinking-container">
                <span className="pulse-dot" />
                <span className="thinking-text">VeriMind is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
