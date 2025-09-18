import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { organizationsAPI } from '../services/api';
import {
  BuildingOfficeIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Organizations = () => {
  const { showSuccess, showError } = useApp();
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingOrg, setEditingOrg] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    industry: '',
    size: '',
    description: '',
    website: '',
  });

  useEffect(() => {
    loadOrganizations();
  }, []);

  const loadOrganizations = async () => {
    try {
      setLoading(true);
      const response = await organizationsAPI.getAll();
      setOrganizations(response.data.items || []);
    } catch (error) {
      console.error('Failed to load organizations:', error);
      showError('Failed to load organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingOrg) {
        await organizationsAPI.update(editingOrg.id, formData);
        showSuccess('Organization updated successfully');
      } else {
        await organizationsAPI.create(formData);
        showSuccess('Organization created successfully');
      }
      
      setShowModal(false);
      setEditingOrg(null);
      setFormData({ name: '', industry: '', size: '', description: '', website: '' });
      loadOrganizations();
    } catch (error) {
      console.error('Failed to save organization:', error);
      showError('Failed to save organization');
    }
  };

  const handleEdit = (org) => {
    setEditingOrg(org);
    setFormData({
      name: org.name,
      industry: org.industry || '',
      size: org.size || '',
      description: org.description || '',
      website: org.website || '',
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this organization?')) {
      try {
        await organizationsAPI.delete(id);
        showSuccess('Organization deleted successfully');
        loadOrganizations();
      } catch (error) {
        console.error('Failed to delete organization:', error);
        showError('Failed to delete organization');
      }
    }
  };

  const filteredOrganizations = organizations.filter(org =>
    org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (org.industry && org.industry.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getSizeLabel = (size) => {
    const sizeMap = {
      'small': 'Small (1-50)',
      'medium': 'Medium (51-250)',
      'large': 'Large (251-1000)',
      'enterprise': 'Enterprise (1000+)'
    };
    return sizeMap[size] || size;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Organizations</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage organizations in your ESG benchmarking system
          </p>
        </div>
        <button
          onClick={() => {
            setEditingOrg(null);
            setFormData({ name: '', industry: '', size: '', description: '', website: '' });
            setShowModal(true);
          }}
          className="btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Organization
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="Search organizations..."
          className="input pl-10"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Organizations Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="large" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredOrganizations.map((org) => (
            <div key={org.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <BuildingOfficeIcon className="h-8 w-8 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {org.name}
                    </h3>
                    {org.industry && (
                      <p className="text-sm text-gray-500">{org.industry}</p>
                    )}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(org)}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <PencilIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(org.id)}
                    className="text-gray-400 hover:text-danger-600"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
              
              <div className="mt-4 space-y-2">
                {org.size && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Size:</span>
                    <span className="badge-gray">{getSizeLabel(org.size)}</span>
                  </div>
                )}
                {org.website && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Website:</span>
                    <a
                      href={org.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:text-primary-500 truncate"
                    >
                      {org.website}
                    </a>
                  </div>
                )}
                {org.description && (
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                    {org.description}
                  </p>
                )}
                <div className="flex items-center justify-between text-xs text-gray-500 mt-3">
                  <span>Created: {new Date(org.created_at).toLocaleDateString()}</span>
                  <span>{org.reports_count || 0} reports</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && filteredOrganizations.length === 0 && (
        <div className="text-center py-12">
          <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No organizations</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'No organizations match your search.' : 'Get started by creating a new organization.'}
          </p>
          {!searchTerm && (
            <div className="mt-6">
              <button
                onClick={() => {
                  setEditingOrg(null);
                  setFormData({ name: '', industry: '', size: '', description: '', website: '' });
                  setShowModal(true);
                }}
                className="btn-primary"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Add Organization
              </button>
            </div>
          )}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingOrg ? 'Edit Organization' : 'Add Organization'}
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
                  <label className="label">Industry</label>
                  <input
                    type="text"
                    className="input"
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Size</label>
                  <select
                    className="input"
                    value={formData.size}
                    onChange={(e) => setFormData({ ...formData, size: e.target.value })}
                  >
                    <option value="">Select size</option>
                    <option value="small">Small (1-50)</option>
                    <option value="medium">Medium (51-250)</option>
                    <option value="large">Large (251-1000)</option>
                    <option value="enterprise">Enterprise (1000+)</option>
                  </select>
                </div>
                <div>
                  <label className="label">Website</label>
                  <input
                    type="url"
                    className="input"
                    value={formData.website}
                    onChange={(e) => setFormData({ ...formData, website: e.target.value })}
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
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="btn-outline"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    {editingOrg ? 'Update' : 'Create'}
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

export default Organizations;
