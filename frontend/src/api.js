import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('Request headers:', config.headers); // DEBUG
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh token if available
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('token', access_token);
          
          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refreshToken', response.data.access_token); // Use same token as refresh for simplicity
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/auth/me', profileData);
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },
};

// Tracking API
export const trackingAPI = {
  logData: async (trackingData) => {
    const response = await api.post('/tracking/log', trackingData);
    return response.data;
  },

  getHistory: async (days = 30) => {
    const response = await api.get(`/tracking/history?days=${days}`);
    return response.data;
  },

  getGoals: async () => {
    const response = await api.get('/tracking/goals');
    return response.data;
  },
};

// Health Prediction APIs
export const predictionAPI = {
  predict: async (healthData) => {
    const response = await api.post('/predict', healthData);
    return response.data;
  },

  getHistory: async (limit = 10) => {
    const response = await api.get(`/predictions/history?limit=${limit}`);
    return response.data;
  },

  getWhatIf: async (scenario, currentValues) => {
    const response = await api.post('/what-if', {
      scenario,
      current_values: currentValues,
    });
    return response.data;
  },  
    downloadPDF: async (healthData) => {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/predict/current-pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(healthData)
      });
      
      if (!response.ok) throw new Error('Failed to download PDF');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `health_report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
  },
};


// Dashboard APIs
export const dashboardAPI = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
};

// Recommendations APIs
export const recommendationsAPI = {
  getGeneral: async () => {
    const response = await api.get('/recommendations');
    return response.data;
  },
};

// Food Database APIs
export const foodAPI = {
  search: async (query) => {
    const response = await api.get(`/food-database/search?query=${query}`);
    return response.data;
  },
};

// Health Q&A APIs (only for fresh assessments)
export const healthQA = {
  askQuestion: async (question, healthData = null) => {
    const response = await api.post('/health/ask-question', {
      question,
      health_data: healthData
    });
    return response.data;
  }
};

// Recent Assessments APIs
export const recentAssessments = {
  getRecent: async (limit = 10) => {
    const response = await api.get(`/assessments/recent?limit=${limit}`);
    return response.data;
  }
};

// Health Check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;