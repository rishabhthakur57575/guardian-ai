import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // System Health
  getHealth: async () => {
    const res = await api.get('/health');
    return res.data;
  },

  // Events
  getEvents: async (sessionId = null, limit = 50) => {
    const params = { limit };
    if (sessionId) params.session_id = sessionId;
    const res = await api.get('/events', { params });
    return res.data;
  },

  postEvent: async (eventData) => {
    const res = await api.post('/events', eventData);
    return res.data;
  },

  // Risk Score
  getRiskScore: async (sessionId, events = null) => {
    const res = await api.post('/risk-score', {
      session_id: sessionId,
      events: events,
    });
    return res.data;
  },

  // Sessions
  getSession: async (sessionId) => {
    const res = await api.get(`/session/${sessionId}`);
    return res.data;
  },

  getSessions: async () => {
    const res = await api.get('/sessions');
    return res.data;
  },

  // Interventions
  postIntervention: async (interventionData) => {
    const res = await api.post('/intervention', interventionData);
    return res.data;
  },

  // Analytics
  getAnalytics: async () => {
    const res = await api.get('/analytics');
    return res.data;
  },

  // Simulator Endpoints
  simulatorStep: async (sessionId = 'demo-session-live') => {
    const res = await api.post('/simulator/step', null, {
      params: { session_id: sessionId }
    });
    return res.data;
  },

  simulatorReset: async (sessionId = 'demo-session-live') => {
    const res = await api.post('/simulator/reset', null, {
      params: { session_id: sessionId }
    });
    return res.data;
  },

  getSimulatorState: async (sessionId = 'demo-session-live') => {
    const res = await api.get('/simulator/state', {
      params: { session_id: sessionId }
    });
    return res.data;
  }
};

export default apiService;
