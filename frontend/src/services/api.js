import axios from 'axios';

// Create axios instance with base configuration
export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add request ID for tracking
    config.headers['X-Request-ID'] = `web-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common error cases
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// API service functions
export const authAPI = {
  login: (email, name) => apiClient.post('/api/auth/mock-login', { email, name }),
  logout: () => apiClient.post('/api/auth/logout'),
  me: () => apiClient.get('/api/auth/me'),
  validate: () => apiClient.get('/api/auth/validate'),
};

export const organizationsAPI = {
  getAll: (params = {}) => apiClient.get('/api/organizations', { params }),
  getById: (id) => apiClient.get(`/api/organizations/${id}`),
  create: (data) => apiClient.post('/api/organizations', data),
  update: (id, data) => apiClient.put(`/api/organizations/${id}`, data),
  delete: (id) => apiClient.delete(`/api/organizations/${id}`),
  getStats: (id) => apiClient.get(`/api/organizations/${id}/stats`),
};

export const reportsAPI = {
  getAll: (params = {}) => apiClient.get('/api/reports', { params }),
  getById: (id) => apiClient.get(`/api/reports/${id}`),
  create: (data) => apiClient.post('/api/reports', data),
  update: (id, data) => apiClient.put(`/api/reports/${id}`, data),
  delete: (id) => apiClient.delete(`/api/reports/${id}`),
  upload: (formData) => apiClient.post('/api/reports/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  fetchFromUrl: (data) => apiClient.post('/api/reports/fetch', data),
  getChunks: (id, params = {}) => apiClient.get(`/api/reports/${id}/chunks`, { params }),
};

export const ingestionAPI = {
  getJobs: (params = {}) => apiClient.get('/api/ingestion/jobs', { params }),
  getJob: (id) => apiClient.get(`/api/ingestion/jobs/${id}`),
  createJob: (data) => apiClient.post('/api/ingestion/jobs', data),
  runJob: (id) => apiClient.post(`/api/ingestion/jobs/${id}/run`),
  deleteJob: (id) => apiClient.delete(`/api/ingestion/jobs/${id}`),
  getJobStatus: (id) => apiClient.get(`/api/ingestion/jobs/${id}/status`),
  extractKPIs: (reportId) => apiClient.post(`/api/ingestion/extract/${reportId}`),
};

export const kpisAPI = {
  getDefinitions: (params = {}) => apiClient.get('/api/kpis', { params }),
  getDefinition: (id) => apiClient.get(`/api/kpis/${id}`),
  createDefinition: (data) => apiClient.post('/api/kpis', data),
  getValues: (params = {}) => apiClient.get('/api/kpis/values', { params }),
  createValue: (data) => apiClient.post('/api/kpis/values', data),
  getCategories: () => apiClient.get('/api/kpis/categories'),
  getKPIValues: (kpiId, params = {}) => apiClient.get(`/api/kpis/${kpiId}/values`, { params }),
  getKPIStats: (kpiId, params = {}) => apiClient.get(`/api/kpis/${kpiId}/stats`, { params }),
  deleteValue: (valueId) => apiClient.delete(`/api/kpis/values/${valueId}`),
};

export const benchmarksAPI = {
  createSnapshot: (data) => apiClient.post('/api/benchmarks/snapshot', data),
  getOrganizationPercentile: (orgId, params) => apiClient.get(`/api/benchmarks/organization/${orgId}/percentile`, { params }),
  getTopPerformers: (params) => apiClient.get('/api/benchmarks/top-performers', { params }),
  compareOrganizations: (data) => apiClient.post('/api/benchmarks/compare', data),
  getPeerGroups: (params = {}) => apiClient.get('/api/benchmarks/peer-groups', { params }),
  createPeerGroup: (data) => apiClient.post('/api/benchmarks/peer-groups', data),
  getPeerGroup: (id) => apiClient.get(`/api/benchmarks/peer-groups/${id}`),
  deletePeerGroup: (id) => apiClient.delete(`/api/benchmarks/peer-groups/${id}`),
  getSnapshots: (params = {}) => apiClient.get('/api/benchmarks/snapshots', { params }),
};

export const recommendationsAPI = {
  getAll: (params = {}) => apiClient.get('/api/recommendations', { params }),
  getById: (id) => apiClient.get(`/api/recommendations/${id}`),
  create: (data) => apiClient.post('/api/recommendations', data),
  generate: (data) => apiClient.post('/api/recommendations/generate', data),
  generateComprehensive: (data) => apiClient.post('/api/recommendations/comprehensive', data),
  updateStatus: (id, data) => apiClient.put(`/api/recommendations/${id}/status`, data),
  delete: (id) => apiClient.delete(`/api/recommendations/${id}`),
  getSummary: (orgId) => apiClient.get(`/api/recommendations/organization/${orgId}/summary`),
};

export const searchAPI = {
  search: (params) => apiClient.get('/api/search', { params }),
  searchPost: (data) => apiClient.post('/api/search', data),
  findSimilar: (embeddingId, params = {}) => apiClient.get(`/api/search/similar/${embeddingId}`, { params }),
  getSuggestions: (params) => apiClient.get('/api/search/suggestions', { params }),
  getStats: () => apiClient.get('/api/search/stats'),
};

export const healthAPI = {
  check: () => apiClient.get('/health'),
};
