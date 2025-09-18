import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { benchmarksAPI, organizationsAPI, kpisAPI } from '../services/api';
import {
  ScaleIcon,
  PlusIcon,
  ChartBarIcon,
  TrophyIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Benchmarks = () => {
  const { showSuccess, showError } = useApp();
  const [snapshots, setSnapshots] = useState([]);
  const [peerGroups, setPeerGroups] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [kpiDefinitions, setKpiDefinitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('snapshots');
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('snapshot'); // 'snapshot' or 'peergroup'
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    kpi_id: '',
    year: new Date().getFullYear(),
    organization_ids: [],
  });
  const [benchmarkResults, setBenchmarkResults] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [snapshotsResponse, peerGroupsResponse, orgsResponse, kpisResponse] = await Promise.all([
        benchmarksAPI.getSnapshots(),
        benchmarksAPI.getPeerGroups(),
        organizationsAPI.getAll(),
        kpisAPI.getDefinitions(),
      ]);
      setSnapshots(snapshotsResponse.data.items || []);
      setPeerGroups(peerGroupsResponse.data.items || []);
      setOrganizations(orgsResponse.data.items || []);
      setKpiDefinitions(kpisResponse.data.items || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      showError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSnapshot = async (e) => {
    e.preventDefault();
    try {
      const response = await benchmarksAPI.createSnapshot({
        kpi_id: parseInt(formData.kpi_id),
        year: formData.year,
        organization_ids: formData.organization_ids.map(id => parseInt(id)),
      });
      showSuccess('Benchmark snapshot created successfully');
      setBenchmarkResults(response.data.results || []);
      setShowModal(false);
      loadData();
    } catch (error) {
      console.error('Failed to create snapshot:', error);
      showError('Failed to create benchmark snapshot');
    }
  };

  const handleCreatePeerGroup = async (e) => {
    e.preventDefault();
    try {
      await benchmarksAPI.createPeerGroup({
        name: formData.name,
        description: formData.description,
        organization_ids: formData.organization_ids.map(id => parseInt(id)),
      });
      showSuccess('Peer group created successfully');
      setShowModal(false);
      setFormData({ name: '', description: '', kpi_id: '', year: new Date().getFullYear(), organization_ids: [] });
      loadData();
    } catch (error) {
      console.error('Failed to create peer group:', error);
      showError('Failed to create peer group');
    }
  };

  const handleDeletePeerGroup = async (id) => {
    if (window.confirm('Are you sure you want to delete this peer group?')) {
      try {
        await benchmarksAPI.deletePeerGroup(id);
        showSuccess('Peer group deleted successfully');
        loadData();
      } catch (error) {
        console.error('Failed to delete peer group:', error);
        showError('Failed to delete peer group');
      }
    }
  };

  const openModal = (type) => {
    setModalType(type);
    setFormData({ name: '', description: '', kpi_id: '', year: new Date().getFullYear(), organization_ids: [] });
    setShowModal(true);
  };

  const filteredSnapshots = snapshots.filter(snapshot =>
    snapshot.kpi_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredPeerGroups = peerGroups.filter(group =>
    group.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (group.description && group.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getPerformanceIcon = (percentile) => {
    if (percentile >= 75) return <ArrowUpIcon className="h-4 w-4 text-success-500" />;
    if (percentile <= 25) return <ArrowDownIcon className="h-4 w-4 text-danger-500" />;
    return <ChartBarIcon className="h-4 w-4 text-warning-500" />;
  };

  const getPerformanceBadge = (percentile) => {
    if (percentile >= 75) return 'badge-success';
    if (percentile <= 25) return 'badge-danger';
    return 'badge-warning';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Benchmarks</h1>
          <p className="mt-1 text-sm text-gray-500">
            Compare organizational performance and manage peer groups
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => openModal('peergroup')}
            className="btn-outline"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Peer Group
          </button>
          <button
            onClick={() => openModal('snapshot')}
            className="btn-primary"
          >
            <ScaleIcon className="h-5 w-5 mr-2" />
            Create Benchmark
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('snapshots')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'snapshots'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Benchmark Snapshots ({snapshots.length})
          </button>
          <button
            onClick={() => setActiveTab('peergroups')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'peergroups'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Peer Groups ({peerGroups.length})
          </button>
        </nav>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder={`Search ${activeTab}...`}
          className="input pl-10"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="large" />
        </div>
      ) : activeTab === 'snapshots' ? (
        <div className="space-y-6">
          {/* Benchmark Results */}
          {benchmarkResults.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Latest Benchmark Results</h3>
              <div className="space-y-3">
                {benchmarkResults.map((result, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getPerformanceIcon(result.percentile)}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          {result.organization_name}
                        </h4>
                        <p className="text-xs text-gray-500">
                          Value: {result.value} {result.unit}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`badge ${getPerformanceBadge(result.percentile)}`}>
                        {result.percentile}th percentile
                      </span>
                      <p className="text-xs text-gray-500 mt-1">
                        Rank: {result.rank} of {result.total_organizations}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Snapshots List */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSnapshots.map((snapshot) => (
              <div key={snapshot.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <ScaleIcon className="h-8 w-8 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {snapshot.kpi_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {snapshot.year} Benchmark
                      </p>
                    </div>
                  </div>
                  <TrophyIcon className="h-6 w-6 text-warning-500" />
                </div>
                
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Organizations:</span>
                    <span className="font-medium">{snapshot.organization_count}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Avg Value:</span>
                    <span className="font-medium">
                      {snapshot.avg_value?.toFixed(2)} {snapshot.unit}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Range:</span>
                    <span className="font-medium">
                      {snapshot.min_value?.toFixed(2)} - {snapshot.max_value?.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500 mt-3 pt-3 border-t">
                    <span>Created: {new Date(snapshot.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPeerGroups.map((group) => (
            <div key={group.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-medium text-gray-900 truncate">
                    {group.name}
                  </h3>
                  {group.description && (
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                      {group.description}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => handleDeletePeerGroup(group.id)}
                  className="text-gray-400 hover:text-danger-600"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              
              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Organizations:</span>
                  <span className="font-medium">{group.organization_count || 0}</span>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-500 mt-3 pt-3 border-t">
                  <span>Created: {new Date(group.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty States */}
      {!loading && activeTab === 'snapshots' && filteredSnapshots.length === 0 && (
        <div className="text-center py-12">
          <ScaleIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No benchmark snapshots</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'No snapshots match your search.' : 'Create your first benchmark to compare organizational performance.'}
          </p>
          {!searchTerm && (
            <div className="mt-6">
              <button
                onClick={() => openModal('snapshot')}
                className="btn-primary"
              >
                <ScaleIcon className="h-5 w-5 mr-2" />
                Create Benchmark
              </button>
            </div>
          )}
        </div>
      )}

      {!loading && activeTab === 'peergroups' && filteredPeerGroups.length === 0 && (
        <div className="text-center py-12">
          <ScaleIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No peer groups</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'No peer groups match your search.' : 'Create peer groups to organize organizations for benchmarking.'}
          </p>
          {!searchTerm && (
            <div className="mt-6">
              <button
                onClick={() => openModal('peergroup')}
                className="btn-primary"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Create Peer Group
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
                {modalType === 'snapshot' ? 'Create Benchmark Snapshot' : 'Create Peer Group'}
              </h3>
              <form onSubmit={modalType === 'snapshot' ? handleCreateSnapshot : handleCreatePeerGroup} className="space-y-4">
                {modalType === 'peergroup' && (
                  <>
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
                      <label className="label">Description</label>
                      <textarea
                        rows={3}
                        className="input"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      />
                    </div>
                  </>
                )}
                
                {modalType === 'snapshot' && (
                  <>
                    <div>
                      <label className="label">KPI *</label>
                      <select
                        required
                        className="input"
                        value={formData.kpi_id}
                        onChange={(e) => setFormData({ ...formData, kpi_id: e.target.value })}
                      >
                        <option value="">Select KPI</option>
                        {kpiDefinitions.map((kpi) => (
                          <option key={kpi.id} value={kpi.id}>
                            {kpi.name} ({kpi.unit || 'no unit'})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="label">Year *</label>
                      <input
                        type="number"
                        required
                        min="2000"
                        max="2030"
                        className="input"
                        value={formData.year}
                        onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
                      />
                    </div>
                  </>
                )}
                
                <div>
                  <label className="label">Organizations *</label>
                  <select
                    multiple
                    required
                    className="input h-32"
                    value={formData.organization_ids}
                    onChange={(e) => {
                      const values = Array.from(e.target.selectedOptions, option => option.value);
                      setFormData({ ...formData, organization_ids: values });
                    }}
                  >
                    {organizations.map((org) => (
                      <option key={org.id} value={org.id}>
                        {org.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Hold Ctrl/Cmd to select multiple organizations
                  </p>
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
                    {modalType === 'snapshot' ? 'Create Benchmark' : 'Create Group'}
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

export default Benchmarks;
