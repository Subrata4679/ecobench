import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { recommendationsAPI, organizationsAPI, kpisAPI } from '../services/api';
import {
  LightBulbIcon,
  PlusIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Recommendations = () => {
  const { showSuccess, showError } = useApp();
  const [recommendations, setRecommendations] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [kpiDefinitions, setKpiDefinitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [organizationFilter, setOrganizationFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [formData, setFormData] = useState({
    organization_id: '',
    kpi_id: '',
    type: 'improvement',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [recsResponse, orgsResponse, kpisResponse] = await Promise.all([
        recommendationsAPI.getAll(),
        organizationsAPI.getAll(),
        kpisAPI.getDefinitions(),
      ]);
      setRecommendations(recsResponse.data.items || []);
      setOrganizations(orgsResponse.data.items || []);
      setKpiDefinitions(kpisResponse.data.items || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      showError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    try {
      setGenerating(true);
      await recommendationsAPI.generate({
        organization_id: parseInt(formData.organization_id),
        kpi_id: parseInt(formData.kpi_id),
        type: formData.type,
      });
      showSuccess('Recommendations generated successfully');
      setShowModal(false);
      setFormData({ organization_id: '', kpi_id: '', type: 'improvement' });
      loadData();
    } catch (error) {
      console.error('Failed to generate recommendations:', error);
      showError('Failed to generate recommendations');
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateComprehensive = async (organizationId) => {
    try {
      setGenerating(true);
      await recommendationsAPI.generateComprehensive({
        organization_id: organizationId,
      });
      showSuccess('Comprehensive guidance generated successfully');
      loadData();
    } catch (error) {
      console.error('Failed to generate comprehensive guidance:', error);
      showError('Failed to generate comprehensive guidance');
    } finally {
      setGenerating(false);
    }
  };

  const handleUpdateStatus = async (id, status) => {
    try {
      await recommendationsAPI.updateStatus(id, { status });
      showSuccess('Status updated successfully');
      loadData();
    } catch (error) {
      console.error('Failed to update status:', error);
      showError('Failed to update status');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this recommendation?')) {
      try {
        await recommendationsAPI.delete(id);
        showSuccess('Recommendation deleted successfully');
        loadData();
      } catch (error) {
        console.error('Failed to delete recommendation:', error);
        showError('Failed to delete recommendation');
      }
    }
  };

  const filteredRecommendations = recommendations.filter(rec => {
    const matchesSearch = rec.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rec.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rec.organization_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !statusFilter || rec.status === statusFilter;
    const matchesOrg = !organizationFilter || rec.organization_id === parseInt(organizationFilter);
    return matchesSearch && matchesStatus && matchesOrg;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-warning-500" />;
      case 'implemented':
        return <CheckCircleIcon className="h-5 w-5 text-success-500" />;
      case 'in_progress':
        return <ExclamationTriangleIcon className="h-5 w-5 text-primary-500" />;
      default:
        return <LightBulbIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'pending': 'badge-warning',
      'in_progress': 'badge-primary',
      'implemented': 'badge-success',
      'dismissed': 'badge-gray',
    };
    return statusMap[status] || 'badge-gray';
  };

  const getPriorityBadge = (priority) => {
    const priorityMap = {
      'high': 'badge-danger',
      'medium': 'badge-warning',
      'low': 'badge-success',
    };
    return priorityMap[priority] || 'badge-gray';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Recommendations</h1>
          <p className="mt-1 text-sm text-gray-500">
            AI-powered recommendations for ESG performance improvement
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary"
          disabled={generating}
        >
          {generating ? (
            <LoadingSpinner size="small" className="mr-2" />
          ) : (
            <SparklesIcon className="h-5 w-5 mr-2" />
          )}
          Generate Recommendations
        </button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search recommendations..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          className="input"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="implemented">Implemented</option>
          <option value="dismissed">Dismissed</option>
        </select>
        <select
          className="input"
          value={organizationFilter}
          onChange={(e) => setOrganizationFilter(e.target.value)}
        >
          <option value="">All Organizations</option>
          {organizations.map((org) => (
            <option key={org.id} value={org.id}>
              {org.name}
            </option>
          ))}
        </select>
      </div>

      {/* Recommendations List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="large" />
        </div>
      ) : (
        <div className="space-y-4">
          {filteredRecommendations.map((rec) => (
            <div key={rec.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="flex-shrink-0 mt-1">
                    {getStatusIcon(rec.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">
                        {rec.title}
                      </h3>
                      <span className={`badge ${getStatusBadge(rec.status)}`}>
                        {rec.status?.replace('_', ' ')}
                      </span>
                      {rec.priority && (
                        <span className={`badge ${getPriorityBadge(rec.priority)}`}>
                          {rec.priority} priority
                        </span>
                      )}
                    </div>
                    
                    <div className="text-sm text-gray-500 mb-2">
                      {rec.organization_name} • {rec.kpi_name || 'General recommendation'}
                    </div>
                    
                    {rec.description && (
                      <p className="text-sm text-gray-600 mb-3 line-clamp-3">
                        {rec.description}
                      </p>
                    )}
                    
                    {rec.action_items && rec.action_items.length > 0 && (
                      <div className="mb-3">
                        <h4 className="text-sm font-medium text-gray-900 mb-1">Action Items:</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {rec.action_items.slice(0, 3).map((item, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-primary-600 mr-2">•</span>
                              {item}
                            </li>
                          ))}
                          {rec.action_items.length > 3 && (
                            <li className="text-gray-500 italic">
                              +{rec.action_items.length - 3} more items
                            </li>
                          )}
                        </ul>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Created: {new Date(rec.created_at).toLocaleDateString()}</span>
                      {rec.confidence_score && (
                        <span>Confidence: {(rec.confidence_score * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col space-y-2 ml-4">
                  {rec.status === 'pending' && (
                    <>
                      <button
                        onClick={() => handleUpdateStatus(rec.id, 'in_progress')}
                        className="btn btn-sm bg-primary-600 text-white hover:bg-primary-700"
                      >
                        Start
                      </button>
                      <button
                        onClick={() => handleUpdateStatus(rec.id, 'dismissed')}
                        className="btn btn-sm bg-gray-600 text-white hover:bg-gray-700"
                      >
                        Dismiss
                      </button>
                    </>
                  )}
                  {rec.status === 'in_progress' && (
                    <button
                      onClick={() => handleUpdateStatus(rec.id, 'implemented')}
                      className="btn btn-sm bg-success-600 text-white hover:bg-success-700"
                    >
                      Complete
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(rec.id)}
                    className="btn btn-sm bg-danger-600 text-white hover:bg-danger-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && filteredRecommendations.length === 0 && (
        <div className="text-center py-12">
          <LightBulbIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No recommendations</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || statusFilter || organizationFilter 
              ? 'No recommendations match your filters.' 
              : 'Generate AI-powered recommendations to improve ESG performance.'}
          </p>
          {!searchTerm && !statusFilter && !organizationFilter && (
            <div className="mt-6">
              <button
                onClick={() => setShowModal(true)}
                className="btn-primary"
              >
                <SparklesIcon className="h-5 w-5 mr-2" />
                Generate Recommendations
              </button>
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {organizations.slice(0, 3).map((org) => (
            <button
              key={org.id}
              onClick={() => handleGenerateComprehensive(org.id)}
              disabled={generating}
              className="btn-outline flex flex-col items-center p-4 space-y-2"
            >
              <SparklesIcon className="h-8 w-8 text-gray-400" />
              <span className="text-sm">Generate Comprehensive Guidance</span>
              <span className="text-xs text-gray-500">{org.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Generate Recommendations
              </h3>
              <form onSubmit={handleGenerate} className="space-y-4">
                <div>
                  <label className="label">Organization *</label>
                  <select
                    required
                    className="input"
                    value={formData.organization_id}
                    onChange={(e) => setFormData({ ...formData, organization_id: e.target.value })}
                  >
                    <option value="">Select organization</option>
                    {organizations.map((org) => (
                      <option key={org.id} value={org.id}>
                        {org.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">KPI (Optional)</label>
                  <select
                    className="input"
                    value={formData.kpi_id}
                    onChange={(e) => setFormData({ ...formData, kpi_id: e.target.value })}
                  >
                    <option value="">All KPIs</option>
                    {kpiDefinitions.map((kpi) => (
                      <option key={kpi.id} value={kpi.id}>
                        {kpi.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Recommendation Type</label>
                  <select
                    className="input"
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  >
                    <option value="improvement">Performance Improvement</option>
                    <option value="compliance">Compliance & Standards</option>
                    <option value="best_practice">Best Practices</option>
                    <option value="risk_mitigation">Risk Mitigation</option>
                  </select>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="btn-outline"
                    disabled={generating}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary" disabled={generating}>
                    {generating ? <LoadingSpinner size="small" className="mr-2" /> : null}
                    Generate
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
