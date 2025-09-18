import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [organizations, setOrganizations] = useState([]);
  const [kpiDefinitions, setKpiDefinitions] = useState([]);
  const [kpiValues, setKpiValues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [newOrg, setNewOrg] = useState({ name: '', industry: '', size: 'Medium' });

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
              <span className="ml-2 text-sm text-gray-500">ESG Benchmarking Platform</span>
            </div>
            <div className="text-sm text-gray-500">
              Backend: ✅ Connected | Frontend: ✅ Running
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['dashboard', 'organizations', 'kpis', 'search'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Platform Overview</h3>
                  <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-3">
                    <div className="bg-blue-50 overflow-hidden shadow rounded-lg">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                              <span className="text-white font-bold">🏢</span>
                            </div>
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-gray-500 truncate">Organizations</dt>
                              <dd className="text-lg font-medium text-gray-900">{organizations.length}</dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-green-50 overflow-hidden shadow rounded-lg">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                              <span className="text-white font-bold">📊</span>
                            </div>
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-gray-500 truncate">KPI Definitions</dt>
                              <dd className="text-lg font-medium text-gray-900">{kpiDefinitions.length}</dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-purple-50 overflow-hidden shadow rounded-lg">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                              <span className="text-white font-bold">📈</span>
                            </div>
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-gray-500 truncate">KPI Values</dt>
                              <dd className="text-lg font-medium text-gray-900">{kpiValues.length}</dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Quick Actions</h3>
                  <div className="mt-5 flex space-x-4">
                    <button
                      onClick={performSearch}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                    >
                      🔍 Test Semantic Search
                    </button>
                    <button
                      onClick={() => generateRecommendations(1)}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700"
                    >
                      🤖 Generate AI Recommendations
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
        </div>
      </main>
    </div>
  );
}

export default App;
