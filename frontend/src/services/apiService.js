// Enhanced API service with new scraping and chatbot endpoints

class APIService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    this.token = localStorage.getItem('auth_token');
  }

  setAuthToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication
  async login(email, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (response.access_token) {
      this.setAuthToken(response.access_token);
    }
    
    return response;
  }

  async logout() {
    this.setAuthToken(null);
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  // Organizations
  async getOrganizations(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/organizations${queryString ? `?${queryString}` : ''}`);
  }

  async createOrganization(data) {
    return this.request('/organizations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateOrganization(id, data) {
    return this.request(`/organizations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteOrganization(id) {
    return this.request(`/organizations/${id}`, {
      method: 'DELETE',
    });
  }

  // Reports
  async getReports(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/reports${queryString ? `?${queryString}` : ''}`);
  }

  async uploadReport(formData) {
    return this.request('/reports/upload', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    });
  }

  // KPIs
  async getKPIs(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/kpis${queryString ? `?${queryString}` : ''}`);
  }

  async getKPIValues(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/kpis/values${queryString ? `?${queryString}` : ''}`);
  }

  // Benchmarks
  async getBenchmarks(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/benchmarks${queryString ? `?${queryString}` : ''}`);
  }

  // Recommendations
  async getRecommendations(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/recommendations${queryString ? `?${queryString}` : ''}`);
  }

  // Search
  async search(query, params = {}) {
    return this.request('/search', {
      method: 'POST',
      body: JSON.stringify({ query, ...params }),
    });
  }

  // ============ NEW SCRAPING ENDPOINTS ============

  // IT Companies
  async getITCompanies(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/scraping/companies${queryString ? `?${queryString}` : ''}`);
  }

  async initializeCompanies() {
    return this.request('/scraping/initialize-companies', {
      method: 'POST',
    });
  }

  async toggleCompanyScraping(companyId) {
    return this.request(`/scraping/companies/${companyId}/toggle-scraping`, {
      method: 'PUT',
    });
  }

  // Scraping Jobs
  async getScrapingJobs(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/scraping/jobs${queryString ? `?${queryString}` : ''}`);
  }

  async getScrapingJob(jobId) {
    return this.request(`/scraping/jobs/${jobId}`);
  }

  async createScrapingJob(companyId, jobType) {
    return this.request('/scraping/jobs', {
      method: 'POST',
      body: JSON.stringify({
        company_id: companyId,
        job_type: jobType,
      }),
    });
  }

  async runBulkScraping() {
    return this.request('/scraping/bulk-scraping', {
      method: 'POST',
    });
  }

  // Regulatory Reports
  async getRegulatoryReports(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/scraping/regulatory-reports${queryString ? `?${queryString}` : ''}`);
  }

  async getRegulatoryReport(reportId) {
    return this.request(`/scraping/regulatory-reports/${reportId}`);
  }

  // Scraping Stats
  async getScrapingStats() {
    return this.request('/scraping/stats');
  }

  // ============ NEW CHATBOT ENDPOINTS ============

  // ESG Data Management
  async createESGData(data) {
    return this.request('/chatbot/esg-data', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getUserESGData() {
    return this.request('/chatbot/esg-data');
  }

  async getESGDataByYear(year) {
    return this.request(`/chatbot/esg-data/${year}`);
  }

  async updateESGData(data) {
    return this.request('/chatbot/esg-data', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ESG Analysis
  async getESGAnalysis(year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`/chatbot/analysis${params}`);
  }

  async getQuickAnalysis() {
    return this.request('/chatbot/quick-analysis');
  }

  async getIndustryBenchmarks(metric, year = 2023) {
    return this.request(`/chatbot/benchmarks/${metric}?year=${year}`);
  }

  // Chat Sessions
  async createChatSession(sessionName = null) {
    return this.request('/chatbot/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({
        session_name: sessionName,
      }),
    });
  }

  async getChatSessions() {
    return this.request('/chatbot/chat/sessions');
  }

  async deleteChatSession(sessionId) {
    return this.request(`/chatbot/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // Chat Messages
  async getChatHistory(sessionId) {
    return this.request(`/chatbot/chat/sessions/${sessionId}/messages`);
  }

  async sendChatMessage(sessionId, message) {
    return this.request(`/chatbot/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({
        message: message,
      }),
    });
  }

  // ============ UTILITY METHODS ============

  // File Upload Helper
  async uploadFile(file, endpoint = '/reports/upload') {
    const formData = new FormData();
    formData.append('file', file);

    return this.request(endpoint, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    });
  }

  // Health Check
  async healthCheck() {
    return this.request('/health', {
      headers: {},
    });
  }

  // Batch Operations
  async batchRequest(requests) {
    const promises = requests.map(({ endpoint, options }) =>
      this.request(endpoint, options).catch(error => ({ error: error.message }))
    );

    return Promise.all(promises);
  }

  // Real-time Updates (WebSocket simulation)
  subscribeToUpdates(callback) {
    // Simulate real-time updates with polling
    const interval = setInterval(async () => {
      try {
        const [jobs, reports] = await Promise.all([
          this.getScrapingJobs({ limit: 5 }),
          this.getRegulatoryReports({ limit: 5 })
        ]);

        callback({
          type: 'update',
          data: { jobs, reports }
        });
      } catch (error) {
        callback({
          type: 'error',
          error: error.message
        });
      }
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(interval);
  }

  // Data Export
  async exportData(type, format = 'json', params = {}) {
    const endpoint = `/export/${type}`;
    const queryParams = new URLSearchParams({ format, ...params }).toString();
    
    const response = await fetch(`${this.baseURL}${endpoint}?${queryParams}`, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }

    if (format === 'json') {
      return response.json();
    } else {
      return response.blob();
    }
  }

  // Cache Management
  clearCache() {
    // Clear any cached data
    if (typeof window !== 'undefined' && window.localStorage) {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('cache_')) {
          localStorage.removeItem(key);
        }
      });
    }
  }

  // Error Handling Helper
  handleError(error) {
    console.error('API Error:', error);
    
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
      this.setAuthToken(null);
      window.location.href = '/login';
    }
    
    return {
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

// Create singleton instance
const apiService = new APIService();

export default apiService;
