import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { kpisAPI, organizationsAPI } from '../services/api';
import {
  ChartBarIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const KPIs = () => {
  const { showSuccess, showError } = useApp();
  const [kpiDefinitions, setKpiDefinitions] = useState([]);
  const [kpiValues, setKpiValues] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('definitions');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [organizationFilter, setOrganizationFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingKPI, setEditingKPI] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    unit: '',
    calculation_method: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [defsResponse, valuesResponse, orgsResponse, catsResponse] = await Promise.all([
        kpisAPI.getDefinitions(),
        kpisAPI.getValues(),
        organizationsAPI.getAll(),
        kpisAPI.getCategories(),
      ]);
      setKpiDefinitions(defsResponse.data.items || []);
      setKpiValues(valuesResponse.data.items || []);
      setOrganizations(orgsResponse.data.items || []);
      setCategories(catsResponse.data || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      showError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingKPI) {
        // Update not implemented in backend yet
        showError('Update functionality not yet implemented');
      } else {
        await kpisAPI.createDefinition(formData);
        showSuccess('KPI definition created successfully');
      }
      
      setShowModal(false);
      setEditingKPI(null);
      setFormData({ name: '', description: '', category: '', unit: '', calculation_method: '' });
      loadData();
    } catch (error) {
      console.error('Failed to save KPI:', error);
      showError('Failed to save KPI definition');
    }
  };

  const handleEdit = (kpi) => {
    setEditingKPI(kpi);
    setFormData({
      name: kpi.name,
      description: kpi.description || '',
      category: kpi.category || '',
      unit: kpi.unit || '',
      calculation_method: kpi.calculation_method || '',
    });
    setShowModal(true);
  };

  const filteredDefinitions = kpiDefinitions.filter(kpi => {
    const matchesSearch = kpi.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (kpi.description && kpi.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = !categoryFilter || kpi.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const filteredValues = kpiValues.filter(value => {
    const matchesSearch = value.kpi_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      value.organization_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesOrg = !organizationFilter || value.organization_id === parseInt(organizationFilter);
    return matchesSearch && matchesOrg;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">KPIs</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage KPI definitions and track performance values
          </p>
        </div>
        <button
          onClick={() => {
            setEditingKPI(null);
            setFormData({ name: '', description: '', category: '', unit: '', calculation_method: '' });
            setShowModal(true);
          }}
          className="btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add KPI Definition
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('definitions')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'definitions'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            KPI Definitions ({kpiDefinitions.length})
          </button>
          <button
            onClick={() => setActiveTab('values')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'values'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            KPI Values ({kpiValues.length})
          </button>
        </nav>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search KPIs..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        {activeTab === 'definitions' ? (
          <select
            className="input"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        ) : (
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
        )}
        <div className="flex items-center text-sm text-gray-500">
          <FunnelIcon className="h-4 w-4 mr-1" />
          {activeTab === 'definitions' 
            ? `${filteredDefinitions.length} of ${kpiDefinitions.length} definitions`
            : `${filteredValues.length} of ${kpiValues.length} values`
          }
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="large" />
        </div>
      ) : activeTab === 'definitions' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDefinitions.map((kpi) => (
            <div key={kpi.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-8 w-8 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {kpi.name}
                    </h3>
                    {kpi.category && (
                      <span className="badge-primary text-xs">
                        {kpi.category}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(kpi)}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <PencilIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
              
              <div className="mt-4 space-y-2">
                {kpi.description && (
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {kpi.description}
                  </p>
                )}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Unit:</span>
                  <span className="font-medium">{kpi.unit || 'No unit'}</span>
                </div>
                {kpi.calculation_method && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Method:</span>
                    <span className="font-medium text-xs truncate">
                      {kpi.calculation_method}
                    </span>
                  </div>
                )}
                <div className="flex items-center justify-between text-xs text-gray-500 mt-3 pt-3 border-t">
                  <span>Created: {new Date(kpi.created_at).toLocaleDateString()}</span>
                  <span>{kpi.values_count || 0} values</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredValues.map((value) => (
            <div key={value.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {value.kpi_name}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{value.organization_name}</span>
                      <span>•</span>
                      <span>{value.year}</span>
                      {value.period && (
                        <>
                          <span>•</span>
                          <span>{value.period}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-gray-900">
                    {typeof value.value === 'number' 
                      ? value.value.toLocaleString() 
                      : value.value
                    }
                  </div>
                  {value.unit && (
                    <div className="text-sm text-gray-500">{value.unit}</div>
                  )}
                </div>
              </div>
              {value.source && (
                <div className="mt-2 text-xs text-gray-500">
                  Source: {value.source}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty States */}
      {!loading && activeTab === 'definitions' && filteredDefinitions.length === 0 && (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No KPI definitions</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || categoryFilter ? 'No KPIs match your filters.' : 'Get started by creating your first KPI definition.'}
          </p>
          {!searchTerm && !categoryFilter && (
            <div className="mt-6">
              <button
                onClick={() => {
                  setEditingKPI(null);
                  setFormData({ name: '', description: '', category: '', unit: '', calculation_method: '' });
                  setShowModal(true);
                }}
                className="btn-primary"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Add KPI Definition
              </button>
            </div>
          )}
        </div>
      )}

      {!loading && activeTab === 'values' && filteredValues.length === 0 && (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No KPI values</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || organizationFilter ? 'No values match your filters.' : 'KPI values will appear here after processing reports.'}
          </p>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingKPI ? 'Edit KPI Definition' : 'Add KPI Definition'}
              </h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="label">Name *</label>
                  <input
                    type="text"
                    required
                    className="input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Category</label>
                  <select
                    className="input"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    <option value="">Select category</option>
                    <option value="Environmental">Environmental</option>
                    <option value="Social">Social</option>
                    <option value="Governance">Governance</option>
                    <option value="Economic">Economic</option>
                  </select>
                </div>
                <div>
                  <label className="label">Unit</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g., tons CO2, %, count"
                    value={formData.unit}
                    onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Description</label>
                  <textarea
                    rows={3}
                    className="input"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Calculation Method</label>
                  <textarea
                    rows={2}
                    className="input"
                    placeholder="How is this KPI calculated?"
                    value={formData.calculation_method}
                    onChange={(e) => setFormData({ ...formData, calculation_method: e.target.value })}
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="btn-outline"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    {editingKPI ? 'Update' : 'Create'}
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

export default KPIs;
