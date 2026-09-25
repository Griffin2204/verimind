const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

async function handleResponse(res) {
  if (!res.ok) {
    let errorData = null;
    try {
      errorData = await res.json();
    } catch (e) {
      // Non-JSON response
    }
    const message = errorData?.detail?.error?.message || errorData?.detail || `Server error (${res.status})`;
    const code = errorData?.detail?.error?.code || `HTTP_${res.status}`;
    const err = new Error(message);
    err.code = code;
    err.status = res.status;
    throw err;
  }
  return await res.json();
}

export const apiService = {
  baseUrl: API_BASE_URL,

  async checkHealth() {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(20000) });
      if (!res.ok) {
        return { status: 'offline', error: `HTTP ${res.status}` };
      }
      const data = await res.json();
      const statusRaw = (data.status || '').toLowerCase();
      const services = data.services || {};
      const serviceValues = Object.values(services);

      const hasUnhealthyService = serviceValues.some((s) => s !== 'healthy');

      if ((statusRaw === 'ok' || statusRaw === 'healthy') && !hasUnhealthyService) {
        return { status: 'healthy', services: data.services };
      } else {
        return { status: 'degraded', services: data.services };
      }
    } catch (err) {
      return { status: 'offline', error: err.message };
    }
  },

  async sendChatMessage(userId, query, conversationId = null) {
    const payload = {
      user_id: parseInt(userId, 10),
      query: query.trim(),
    };
    if (conversationId) {
      payload.conversation_id = conversationId;
    }

    const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await handleResponse(res);
  },

  async uploadDocument(userId, file) {
    const formData = new FormData();
    formData.append('user_id', parseInt(userId, 10));
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/api/v1/documents`, {
      method: 'POST',
      body: formData,
    });
    return await handleResponse(res);
  },

  async getDocuments(userId) {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents?user_id=${parseInt(userId, 10)}`);
    return await handleResponse(res);
  },

  async deleteDocument(documentId) {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}`, {
      method: 'DELETE',
    });
    return await handleResponse(res);
  },

  async getMemories(userId) {
    const res = await fetch(`${API_BASE_URL}/api/v1/memory?user_id=${parseInt(userId, 10)}`);
    return await handleResponse(res);
  },

  async addMemory(userId, text, type = 'preference') {
    const res = await fetch(`${API_BASE_URL}/api/v1/memory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: parseInt(userId, 10), text, type }),
    });
    return await handleResponse(res);
  },

  async confirmMemory(memoryId, confirmed) {
    const res = await fetch(`${API_BASE_URL}/api/v1/memory/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ memory_id: memoryId, confirmed }),
    });
    return await handleResponse(res);
  },

  async deleteMemory(memoryId) {
    const res = await fetch(`${API_BASE_URL}/api/v1/memory/${memoryId}`, {
      method: 'DELETE',
    });
    return await handleResponse(res);
  },

  async submitFeedback(userId, chatMessageId, rating, comment = null) {
    const payload = {
      user_id: parseInt(userId, 10),
      chat_message_id: chatMessageId,
      rating,
      comment,
    };
    const res = await fetch(`${API_BASE_URL}/api/v1/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await handleResponse(res);
  },
};
