import React, { useState, useEffect } from 'react';
import { X, Brain, Plus, Trash2, CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { apiService } from '../../services/api';

export default function MemoryManager({ isOpen, onClose, userId, onMemoriesUpdated }) {
  const [memories, setMemories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [newText, setNewText] = useState('');
  const [newType, setNewType] = useState('preference');
  const [isAdding, setIsAdding] = useState(false);

  const loadMemories = async () => {
    if (!userId) return;
    setIsLoading(true);
    try {
      const data = await apiService.getMemories(userId);
      const mems = Array.isArray(data) ? data : [];
      setMemories(mems);
      if (onMemoriesUpdated) {
        onMemoriesUpdated(mems.length);
      }
    } catch (err) {
      console.warn('Failed to load memories:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadMemories();
    }
  }, [isOpen, userId]);

  const handleAddMemory = async (e) => {
    e.preventDefault();
    if (!newText.trim() || isAdding) return;
    setIsAdding(true);
    try {
      await apiService.addMemory(userId, newText.trim(), newType);
      setNewText('');
      await loadMemories();
    } catch (err) {
      alert(`Failed to save memory: ${err.message}`);
    } finally {
      setIsAdding(false);
    }
  };

  const handleToggleConfirm = async (mem) => {
    try {
      await apiService.confirmMemory(mem.id, !mem.is_confirmed);
      await loadMemories();
    } catch (err) {
      alert(`Failed to update memory status: ${err.message}`);
    }
  };

  const handleDelete = async (memId) => {
    try {
      await apiService.deleteMemory(memId);
      await loadMemories();
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
            <h3 className="panel-title">Memory</h3>
            <p className="panel-subtitle">Information VeriMind has learned and validated.</p>
          </div>
          <button className="panel-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="panel-body">
          {/* Add Memory Form */}
          <form onSubmit={handleAddMemory} className="memory-add-form">
            <input
              type="text"
              placeholder="Add user memory (e.g. 'I prefer 230V AC devices')"
              value={newText}
              onChange={(e) => setNewText(e.target.value)}
              className="memory-text-input"
            />
            <div className="memory-form-row">
              <select
                value={newType}
                onChange={(e) => setNewType(e.target.value)}
                className="memory-type-select"
              >
                <option value="preference">Preference</option>
                <option value="fact">Fact</option>
              </select>
              <button className="btn-add-memory" type="submit" disabled={!newText.trim() || isAdding}>
                {isAdding ? <Loader2 size={14} className="spin-loader" /> : <Plus size={14} />}
                <span>Add Memory</span>
              </button>
            </div>
          </form>

          <div className="list-section-header">
            <span>Saved Memory Items ({memories.length})</span>
          </div>

          {isLoading ? (
            <div className="panel-loader">
              <Loader2 size={20} className="spin-loader" />
            </div>
          ) : memories.length === 0 ? (
            <div className="empty-panel-state">
              <Brain size={32} className="empty-state-icon" />
              <div className="empty-state-title">No memory records</div>
              <div className="empty-state-desc">
                Add preferences or facts to personalize VeriMind's grounded answers.
              </div>
            </div>
          ) : (
            <div className="memories-list">
              {memories.map((mem) => (
                <div key={mem.id} className="memory-card">
                  <div className="mem-card-top">
                    <span className="mem-text">{mem.text}</span>
                    <button
                      className="mem-delete-btn"
                      onClick={() => handleDelete(mem.id)}
                      title="Delete memory"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                  <div className="mem-card-bottom">
                    <span className="mem-type-badge">{mem.type}</span>
                    <button
                      className={`mem-status-toggle ${mem.is_confirmed ? 'confirmed' : 'pending'}`}
                      onClick={() => handleToggleConfirm(mem)}
                      title={mem.is_confirmed ? 'Click to unconfirm' : 'Click to confirm'}
                    >
                      {mem.is_confirmed ? <CheckCircle2 size={13} /> : <Circle size={13} />}
                      <span>{mem.is_confirmed ? 'Confirmed' : 'Pending'}</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
