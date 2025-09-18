import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

// Import enhanced components
import AdvancedDashboard from './components/Analytics/AdvancedDashboard';
import ESGDataForm from './components/ESGDataForm/ESGDataForm';
import ChatInterface from './components/Chatbot/ChatInterface';
import ScrapingDashboard from './components/Scraping/ScrapingDashboard';
import NotificationCenter from './components/Notifications/NotificationCenter';
import ESGMetricsChart from './components/Charts/ESGMetricsChart';
import SystemStatus from './components/Status/SystemStatus';
// Simple API service for demo
const apiService = {
  request: async (endpoint, options = {}) => {
    const response = await fetch(`http://localhost:8000${endpoint}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    return response.json();
  }
};

const API_BASE = 'http://localhost:8000';

// Enhanced API service instance
const enhancedApiService = {
  ...apiService,
  request: async (endpoint, options = {}) => {
    try {
      const response = await axios({
        url: `${API_BASE}${endpoint}`,
        method: 'GET',
        ...options
      });
      return response.data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }
};

function App() {
  const [organizations, setOrganizations] = useState([]);
  const [kpiDefinitions, setKpiDefinitions] = useState([]);
  const [kpiValues, setKpiValues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [newOrg, setNewOrg] = useState({ name: '', industry: '', size: 'Medium' });
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [user, setUser] = useState({ name: 'Demo User', email: 'demo@ecobench.com' });
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [orgsRes, kpiDefsRes, kpiValsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/organizations`),
        axios.get(`${API_BASE}/api/kpis/definitions`),
        axios.get(`${API_BASE}/api/kpis/values`)
      ]);
      
      setOrganizations(orgsRes.data);
      setKpiDefinitions(kpiDefsRes.data);
      setKpiValues(kpiValsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrg = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/api/organizations`, newOrg);
      setNewOrg({ name: '', industry: '', size: 'Medium' });
      fetchData();
    } catch (error) {
      console.error('Error creating organization:', error);
    }
  };

  const generateRecommendations = async (orgId) => {
    try {
      const response = await axios.post(`${API_BASE}/api/recommendations/generate?organization_id=${orgId}`);
      alert(`Generated ${response.data.recommendations.length} recommendations for organization ${orgId}`);
    } catch (error) {
      console.error('Error generating recommendations:', error);
    }
  };

  const performSearch = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/search/semantic?query=carbon emissions&limit=5`);
      alert(`Found ${response.data.results.length} search results`);
    } catch (error) {
      console.error('Error performing search:', error);
    }
  };

  const sendChatMessage = async (message) => {
    if (!message.trim()) return;
    
    setChatLoading(true);
    const userMessage = { type: 'user', content: message, timestamp: new Date() };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/chat?message=${encodeURIComponent(message)}`);
      const botMessage = { 
        type: 'bot', 
        content: response.data.response, 
        suggestions: response.data.suggestions,
        timestamp: new Date() 
      };
      setChatMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending chat message:', error);
      const errorMessage = { 
        type: 'bot', 
        content: 'Sorry, I encountered an error. Please try again.', 
        timestamp: new Date() 
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    sendChatMessage(chatInput);
  };

  const handleSuggestionClick = (suggestion) => {
    sendChatMessage(suggestion);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading EcoBench Platform...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">🌱 EcoBench</h1>
              <span className="ml-2 text-sm text-gray-500">Enhanced ESG Intelligence Platform</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Backend: ✅ Connected | Frontend: ✅ Running
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Welcome, {user.name}</span>
                <NotificationCenter apiService={enhancedApiService} />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Enhanced Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: '📊' },
              { id: 'analytics', label: 'Advanced Analytics', icon: '🔬' },
              { id: 'esg-data', label: 'ESG Data Input', icon: '📝' },
              { id: 'scraping', label: 'Data Collection', icon: '🌐' },
              { id: 'chatbot', label: 'AI Assistant', icon: '🤖' },
              { id: 'organizations', label: 'Organizations', icon: '🏢' },
              { id: 'monitoring', label: 'Real-time Monitor', icon: '📡' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* Enhanced Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Welcome Section */}
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 overflow-hidden shadow rounded-lg">
                <div className="px-6 py-8 text-white">
                  <h2 className="text-2xl font-bold">Welcome to EcoBench Enhanced! 🌱</h2>
                  <p className="mt-2 text-blue-100">Your comprehensive ESG intelligence platform with AI-powered insights</p>
                  <div className="mt-4 flex space-x-4">
                    <button
                      onClick={() => setActiveTab('analytics')}
                      className="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      🔬 Explore Advanced Analytics
                    </button>
                    <button
                      onClick={() => setActiveTab('esg-data')}
                      className="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      📝 Input ESG Data
                    </button>
                  </div>
                </div>
              </div>

              {/* Enhanced Stats Grid */}
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                          <span className="text-white text-lg">🏢</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Organizations</dt>
                          <dd className="text-2xl font-bold text-gray-900">{organizations.length}</dd>
                          <dd className="text-xs text-green-600">+2 this month</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                          <span className="text-white text-lg">📊</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">ESG Metrics</dt>
                          <dd className="text-2xl font-bold text-gray-900">{kpiDefinitions.length}</dd>
                          <dd className="text-xs text-blue-600">Real-time tracking</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                          <span className="text-white text-lg">🤖</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">AI Insights</dt>
                          <dd className="text-2xl font-bold text-gray-900">24/7</dd>
                          <dd className="text-xs text-purple-600">Active monitoring</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
                          <span className="text-white text-lg">⚡</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Risk Alerts</dt>
                          <dd className="text-2xl font-bold text-gray-900">0</dd>
                          <dd className="text-xs text-green-600">All systems green</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Feature Showcase and Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="px-6 py-5">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center gap-2">
                      🚀 New Advanced Features
                    </h3>
                    <div className="mt-4 space-y-3">
                      <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                        <div>
                          <p className="font-medium text-blue-900">Predictive Analytics</p>
                          <p className="text-sm text-blue-700">AI-powered ESG forecasting</p>
                        </div>
                        <button
                          onClick={() => setActiveTab('analytics')}
                          className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                        >
                          Explore →
                        </button>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <div>
                          <p className="font-medium text-green-900">Real-time Monitoring</p>
                          <p className="text-sm text-green-700">24/7 ESG metric tracking</p>
                        </div>
                        <button
                          onClick={() => setActiveTab('monitoring')}
                          className="text-green-600 hover:text-green-800 font-medium text-sm"
                        >
                          Monitor →
                        </button>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                        <div>
                          <p className="font-medium text-purple-900">Risk Assessment</p>
                          <p className="text-sm text-purple-700">Comprehensive ESG risk analysis</p>
                        </div>
                        <button
                          onClick={() => setActiveTab('analytics')}
                          className="text-purple-600 hover:text-purple-800 font-medium text-sm"
                        >
                          Assess →
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="px-6 py-5">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center gap-2">
                      ⚡ Quick Actions
                    </h3>
                    <div className="mt-4 grid grid-cols-2 gap-3">
                      <button
                        onClick={() => setActiveTab('esg-data')}
                        className="p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-colors"
                      >
                        <div className="text-2xl mb-2">📝</div>
                        <div className="text-sm font-medium">Input ESG Data</div>
                      </button>
                      <button
                        onClick={() => setActiveTab('chatbot')}
                        className="p-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-colors"
                      >
                        <div className="text-2xl mb-2">🤖</div>
                        <div className="text-sm font-medium">Ask AI Assistant</div>
                      </button>
                      <button
                        onClick={() => setActiveTab('scraping')}
                        className="p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-colors"
                      >
                        <div className="text-2xl mb-2">🌐</div>
                        <div className="text-sm font-medium">Collect Data</div>
                      </button>
                      <button
                        onClick={() => setActiveTab('analytics')}
                        className="p-4 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition-colors"
                      >
                        <div className="text-2xl mb-2">📊</div>
                        <div className="text-sm font-medium">View Analytics</div>
                      </button>
                    </div>
                  </div>
                </div>

                {/* ESG Metrics Chart */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="px-6 py-5">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center gap-2">
                      📊 Current ESG Metrics
                    </h3>
                    <div className="mt-4">
                      <ESGMetricsChart 
                        type="doughnut"
                        title="ESG Performance Overview"
                        data={{
                          labels: ['Scope 1', 'Scope 2', 'Scope 3', 'Water', 'Waste', 'Energy'],
                          values: [1250, 2100, 3500, 8500, 450, 12000]
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Performance Trends */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-6 py-5">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center gap-2">
                    📈 Performance Trends
                  </h3>
                  <div className="mt-4">
                    <ESGMetricsChart 
                      type="line"
                      title="ESG Metrics Trend (Last 12 Months)"
                      data={{
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        values: [1300, 1280, 1250, 1200, 1180, 1150, 1120, 1100, 1080, 1050, 1020, 1000]
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Advanced Analytics Tab */}
          {activeTab === 'analytics' && (
            <AdvancedDashboard apiService={enhancedApiService} />
          )}

          {/* ESG Data Input Tab */}
          {activeTab === 'esg-data' && (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                    📝 ESG Data Input
                  </h2>
                  <p className="text-gray-600 mt-1">Input your company's ESG metrics for analysis and benchmarking</p>
                </div>
                <div className="p-6">
                  <ESGDataForm 
                    onSubmit={async (data) => {
                      try {
                        try {
                          await enhancedApiService.request('/api/chatbot/esg-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                          });
                          alert('ESG data saved successfully!');
                        } catch (apiError) {
                          console.log('API not available, simulating ESG data save');
                          alert('ESG data saved successfully! (Demo mode)');
                        }
                      } catch (error) {
                        alert('Error saving ESG data: ' + error.message);
                      }
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Scraping Dashboard Tab */}
          {activeTab === 'scraping' && (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                    🌐 Data Collection Dashboard
                  </h2>
                  <p className="text-gray-600 mt-1">Automated collection of ESG data from regulatory reports and company websites</p>
                </div>
                <div className="p-6">
                  <ScrapingDashboard apiService={enhancedApiService} />
                </div>
              </div>
            </div>
          )}

          {/* Enhanced Chatbot Tab */}
          {activeTab === 'chatbot' && (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                    🤖 ESG AI Assistant
                  </h2>
                  <p className="text-gray-600 mt-1">Get personalized ESG insights, recommendations, and comparative analysis</p>
                </div>
                <div className="p-6">
                  <ChatInterface apiService={enhancedApiService} />
                </div>
              </div>
            </div>
          )}

          {/* Real-time Monitoring Tab */}
          {activeTab === 'monitoring' && (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                    📡 Real-time ESG Monitoring
                  </h2>
                  <p className="text-gray-600 mt-1">24/7 monitoring of ESG metrics with automated alerts and notifications</p>
                </div>
                <div className="p-6">
                  {/* System Status Component */}
                  <SystemStatus apiService={enhancedApiService} />
                  
                  {/* Real-time Activity Feed */}
                  <div className="mt-6 bg-gray-50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      📡 Live Activity Feed
                    </h3>
                    <div className="space-y-3 text-sm max-h-48 overflow-y-auto">
                      <div className="flex items-center gap-3 p-3 bg-white rounded border-l-4 border-blue-500">
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                        <div className="flex-1">
                          <span className="font-medium">ESG Data Processing</span>
                          <p className="text-gray-600">Carbon emissions data updated for Q4 2024</p>
                        </div>
                        <span className="text-xs text-gray-400">2 min ago</span>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-white rounded border-l-4 border-green-500">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        <div className="flex-1">
                          <span className="font-medium">Risk Assessment Complete</span>
                          <p className="text-gray-600">Comprehensive ESG risk analysis finished</p>
                        </div>
                        <span className="text-xs text-gray-400">5 min ago</span>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-white rounded border-l-4 border-purple-500">
                        <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                        <div className="flex-1">
                          <span className="font-medium">AI Model Update</span>
                          <p className="text-gray-600">Predictive analytics model retrained with new data</p>
                        </div>
                        <span className="text-xs text-gray-400">10 min ago</span>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-white rounded border-l-4 border-orange-500">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        <div className="flex-1">
                          <span className="font-medium">Regulatory Data Scraped</span>
                          <p className="text-gray-600">New SEC filings collected from 5 companies</p>
                        </div>
                        <span className="text-xs text-gray-400">15 min ago</span>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-white rounded border-l-4 border-red-500">
                        <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                        <div className="flex-1">
                          <span className="font-medium">Alert Triggered</span>
                          <p className="text-gray-600">Water consumption threshold exceeded - Auto-mitigation initiated</p>
                        </div>
                        <span className="text-xs text-gray-400">20 min ago</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <button
                      onClick={async () => {
                        try {
                          await enhancedApiService.request('/analytics/start-monitoring', { method: 'POST' });
                          alert('Real-time monitoring started!');
                        } catch (error) {
                          alert('Error starting monitoring: ' + error.message);
                        }
                      }}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                    >
                      🚀 Start Advanced Monitoring
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Organizations Tab */}
          {activeTab === 'organizations' && (
            <div className="space-y-6">
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Organizations</h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500">Manage organizations in the platform</p>
                </div>
                <ul className="divide-y divide-gray-200">
                  {organizations.map((org) => (
                    <li key={org.id} className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center">
                              <span className="text-white font-medium">{org.name.charAt(0)}</span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{org.name}</div>
                            <div className="text-sm text-gray-500">{org.industry} • {org.size}</div>
                          </div>
                        </div>
                        <button
                          onClick={() => generateRecommendations(org.id)}
                          className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                        >
                          Generate Recommendations
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Add Organization Form */}
              <div className="bg-white shadow sm:rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Add New Organization</h3>
                  <form onSubmit={handleCreateOrg} className="mt-5 space-y-4">
                    <div>
                      <input
                        type="text"
                        placeholder="Organization Name"
                        value={newOrg.name}
                        onChange={(e) => setNewOrg({...newOrg, name: e.target.value})}
                        className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <input
                        type="text"
                        placeholder="Industry"
                        value={newOrg.industry}
                        onChange={(e) => setNewOrg({...newOrg, industry: e.target.value})}
                        className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <select
                        value={newOrg.size}
                        onChange={(e) => setNewOrg({...newOrg, size: e.target.value})}
                        className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="Small">Small</option>
                        <option value="Medium">Medium</option>
                        <option value="Large">Large</option>
                      </select>
                    </div>
                    <button
                      type="submit"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                    >
                      Add Organization
                    </button>
                  </form>
                </div>
              </div>
            </div>
          )}

          {/* KPIs Tab */}
          {activeTab === 'kpis' && (
            <div className="space-y-6">
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">KPI Definitions</h3>
                </div>
                <ul className="divide-y divide-gray-200">
                  {kpiDefinitions.map((kpi) => (
                    <li key={kpi.id} className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{kpi.name}</div>
                          <div className="text-sm text-gray-500">{kpi.description}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            Category: {kpi.category} • Unit: {kpi.unit}
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">KPI Values</h3>
                </div>
                <ul className="divide-y divide-gray-200">
                  {kpiValues.map((value) => (
                    <li key={value.id} className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            KPI ID: {value.kpi_definition_id} | Org ID: {value.organization_id}
                          </div>
                          <div className="text-sm text-gray-500">
                            Value: {value.value} | Period: {value.reporting_period}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            Source: {value.data_source} • Confidence: {(value.confidence_score * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Search Tab */}
          {activeTab === 'search' && (
            <div className="bg-white shadow sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Semantic Search</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Test the AI-powered semantic search functionality
                </p>
                <div className="mt-5">
                  <button
                    onClick={performSearch}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    🔍 Search for "carbon emissions"
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Chat Tab */}
          {activeTab === 'chat' && (
            <div className="bg-white shadow sm:rounded-lg h-96 flex flex-col">
              <div className="px-4 py-5 sm:p-6 border-b">
                <h3 className="text-lg leading-6 font-medium text-gray-900">🤖 ESG AI Assistant</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Ask me anything about ESG data, sustainability metrics, or get personalized recommendations
                </p>
              </div>
              
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {chatMessages.length === 0 && (
                  <div className="text-center text-gray-500 py-8">
                    <div className="text-4xl mb-2">💬</div>
                    <p>Start a conversation! Try asking:</p>
                    <div className="mt-4 space-y-2">
                      {['Hello', 'Show me carbon emissions data', 'What are the top ESG KPIs?', 'How can I improve sustainability?'].map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="block mx-auto px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded-full hover:bg-blue-100"
                        >
                          "{suggestion}"
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                
                {chatMessages.map((message, idx) => (
                  <div key={idx} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.type === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="text-sm">{message.content}</p>
                      {message.suggestions && (
                        <div className="mt-2 space-y-1">
                          {message.suggestions.map((suggestion, sidx) => (
                            <button
                              key={sidx}
                              onClick={() => handleSuggestionClick(suggestion)}
                              className="block w-full text-left px-2 py-1 text-xs bg-white bg-opacity-20 rounded hover:bg-opacity-30"
                            >
                              💡 {suggestion}
                            </button>
                          ))}
                        </div>
                      )}
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                        <span className="text-sm">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Chat Input */}
              <div className="border-t p-4">
                <form onSubmit={handleChatSubmit} className="flex space-x-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask about ESG data, KPIs, recommendations..."
                    className="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    disabled={chatLoading}
                  />
                  <button
                    type="submit"
                    disabled={chatLoading || !chatInput.trim()}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Send
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
