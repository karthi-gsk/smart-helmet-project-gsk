const defaultHost = typeof window !== 'undefined' && window.location.hostname ? window.location.hostname : '127.0.0.1';
const rawBase = import.meta.env.VITE_API_BASE_URL || `http://${defaultHost}:8080`;
const cleanBase = rawBase.replace(/\/+$/, '');
const API_BASE_URL = cleanBase.endsWith('/api') ? cleanBase : `${cleanBase}/api`;

export const fetchLiveData = async () => {
  const response = await fetch(`${API_BASE_URL}/live-data`);
  if (!response.ok) {
    throw new Error('Failed to fetch live sensor data');
  }
  return response.json();
};

export const fetchAlert = async () => {
  const response = await fetch(`${API_BASE_URL}/alert`);
  if (!response.ok) {
    throw new Error('Failed to fetch emergency alert details');
  }
  return response.json();
};

export const setDemoMode = async (mode) => {
  const response = await fetch(`${API_BASE_URL}/demo-mode`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ mode }),
  });
  if (!response.ok) {
    throw new Error(`Failed to set demo mode to ${mode}`);
  }
  return response.json();
};

export const resetAlert = async () => {
  const response = await fetch(`${API_BASE_URL}/reset-alert`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to reset alert state');
  }
  return response.json();
};
