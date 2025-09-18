import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { reportsAPI, organizationsAPI, ingestionAPI } from '../services/api';
import {
  DocumentTextIcon,
  PlusIcon,
  CloudArrowUpIcon,
  LinkIcon,
  EyeIcon,
  TrashIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Reports = () => {
  const { showSuccess, showError } = useApp();
  const [reports, setReports] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrg, setSelectedOrg] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showUrlModal, setShowUrlModal] = useState(false);
  const [uploadData, setUploadData] = useState({
    title: '',
    organization_id: '',
    year: new Date().getFullYear(),
    report_type: 'sustainability',
    file: null,
  });
  const [urlData, setUrlData] = useState({
    title: '',
    organization_id: '',
    year: new Date().getFullYear(),
    report_type: 'sustainability',
    url: '',
  });
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [reportsResponse, orgsResponse] = await Promise.all([
        reportsAPI.getAll(),
        organizationsAPI.getAll(),
      ]);
      setReports(reportsResponse.data.items || []);
      setOrganizations(orgsResponse.data.items || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      showError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadData.file) {
      showError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', uploadData.file);
      formData.append('title', uploadData.title);
      formData.append('organization_id', uploadData.organization_id);
      formData.append('year', uploadData.year);
      formData.append('report_type', uploadData.report_type);

      await reportsAPI.upload(formData);
      showSuccess('Report uploaded successfully');
      setShowUploadModal(false);
      setUploadData({
        title: '',
        organization_id: '',
        year: new Date().getFullYear(),
        report_type: 'sustainability',
        file: null,
      });
      loadData();
    } catch (error) {
      console.error('Failed to upload report:', error);
      showError('Failed to upload report');
    } finally {
      setUploading(false);
    }
  };

  const handleUrlFetch = async (e) => {
    e.preventDefault();
    try {
      setUploading(true);
      await reportsAPI.fetchFromUrl(urlData);
      showSuccess('Report fetch initiated successfully');
      setShowUrlModal(false);
      setUrlData({
        title: '',
        organization_id: '',
        year: new Date().getFullYear(),
        report_type: 'sustainability',
        url: '',
      });
      loadData();
    } catch (error) {
      console.error('Failed to fetch report:', error);
      showError('Failed to fetch report');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      try {
        await reportsAPI.delete(id);
        showSuccess('Report deleted successfully');
        loadData();
      } catch (error) {
        console.error('Failed to delete report:', error);
        showError('Failed to delete report');
      }
    }
  };

  const handleExtractKPIs = async (reportId) => {
    try {
      await ingestionAPI.extractKPIs(reportId);
      showSuccess('KPI extraction initiated');
    } catch (error) {
      console.error('Failed to extract KPIs:', error);
      showError('Failed to extract KPIs');
    }
  };

  const filteredReports = reports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (report.organization_name && report.organization_name.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesOrg = !selectedOrg || report.organization_id === parseInt(selectedOrg);
    return matchesSearch && matchesOrg;
  });

  const getStatusBadge = (status) => {
    const statusMap = {
      'uploaded': 'badge-gray',
      'processing': 'badge-warning',
      'processed': 'badge-success',
      'failed': 'badge-danger',
    };
    return statusMap[status] || 'badge-gray';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage ESG and sustainability reports
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowUrlModal(true)}
            className="btn-outline"
          >
            <LinkIcon className="h-5 w-5 mr-2" />
            Fetch from URL
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="btn-primary"
          >
            <CloudArrowUpIcon className="h-5 w-5 mr-2" />
            Upload Report
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search reports..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          className="input"
          value={selectedOrg}
          onChange={(e) => setSelectedOrg(e.target.value)}
        >
          <option value="">All Organizations</option>
          {organizations.map((org) => (
            <option key={org.id} value={org.id}>
              {org.name}
            </option>
          ))}
        </select>
      </div>

      {/* Reports List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="large" />
        </div>
      ) : (
        <div className="space-y-4">
          {filteredReports.map((report) => (
            <div key={report.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-medium text-gray-900">
                      {report.title}
                    </h3>
                    <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                      <span>{report.organization_name}</span>
                      <span>•</span>
                      <span>{report.year}</span>
                      <span>•</span>
                      <span className="capitalize">{report.report_type}</span>
                    </div>
                    {report.description && (
                      <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                        {report.description}
                      </p>
                    )}
                    <div className="mt-2 flex items-center space-x-4">
                      <span className={`badge ${getStatusBadge(report.status)}`}>
                        {report.status}
                      </span>
                      {report.file_size && (
                        <span className="text-xs text-gray-500">
                          {(report.file_size / 1024 / 1024).toFixed(1)} MB
                        </span>
                      )}
                      <span className="text-xs text-gray-500">
                        Uploaded: {new Date(report.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {report.status === 'processed' && (
                    <button
                      onClick={() => handleExtractKPIs(report.id)}
                      className="text-primary-600 hover:text-primary-500"
                      title="Extract KPIs"
                    >
                      <PlusIcon className="h-5 w-5" />
                    </button>
                  )}
                  <button
                    className="text-gray-400 hover:text-primary-600"
                    title="View Details"
                  >
                    <EyeIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(report.id)}
                    className="text-gray-400 hover:text-danger-600"
                    title="Delete Report"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && filteredReports.length === 0 && (
        <div className="text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No reports</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || selectedOrg ? 'No reports match your filters.' : 'Get started by uploading your first report.'}
          </p>
          {!searchTerm && !selectedOrg && (
            <div className="mt-6">
              <button
                onClick={() => setShowUploadModal(true)}
                className="btn-primary"
              >
                <CloudArrowUpIcon className="h-5 w-5 mr-2" />
                Upload Report
              </button>
            </div>
          )}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Upload Report
              </h3>
              <form onSubmit={handleFileUpload} className="space-y-4">
                <div>
                  <label className="label">Title *</label>
                  <input
                    type="text"
                    required
                    className="input"
                    value={uploadData.title}
                    onChange={(e) => setUploadData({ ...uploadData, title: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Organization *</label>
                  <select
                    required
                    className="input"
                    value={uploadData.organization_id}
                    onChange={(e) => setUploadData({ ...uploadData, organization_id: e.target.value })}
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
                  <label className="label">Year *</label>
                  <input
                    type="number"
                    required
                    min="2000"
                    max="2030"
                    className="input"
                    value={uploadData.year}
                    onChange={(e) => setUploadData({ ...uploadData, year: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="label">Report Type</label>
                  <select
                    className="input"
                    value={uploadData.report_type}
                    onChange={(e) => setUploadData({ ...uploadData, report_type: e.target.value })}
                  >
                    <option value="sustainability">Sustainability Report</option>
                    <option value="annual">Annual Report</option>
                    <option value="esg">ESG Report</option>
                    <option value="environmental">Environmental Report</option>
                    <option value="social">Social Impact Report</option>
                    <option value="governance">Governance Report</option>
                  </select>
                </div>
                <div>
                  <label className="label">File *</label>
                  <input
                    type="file"
                    required
                    accept=".pdf,.doc,.docx"
                    className="input"
                    onChange={(e) => setUploadData({ ...uploadData, file: e.target.files[0] })}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Supported formats: PDF, DOC, DOCX
                  </p>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowUploadModal(false)}
                    className="btn-outline"
                    disabled={uploading}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary" disabled={uploading}>
                    {uploading ? <LoadingSpinner size="small" className="mr-2" /> : null}
                    Upload
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* URL Fetch Modal */}
      {showUrlModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Fetch Report from URL
              </h3>
              <form onSubmit={handleUrlFetch} className="space-y-4">
                <div>
                  <label className="label">Title *</label>
                  <input
                    type="text"
                    required
                    className="input"
                    value={urlData.title}
                    onChange={(e) => setUrlData({ ...urlData, title: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Organization *</label>
                  <select
                    required
                    className="input"
                    value={urlData.organization_id}
                    onChange={(e) => setUrlData({ ...urlData, organization_id: e.target.value })}
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
                  <label className="label">Year *</label>
                  <input
                    type="number"
                    required
                    min="2000"
                    max="2030"
                    className="input"
                    value={urlData.year}
                    onChange={(e) => setUrlData({ ...urlData, year: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="label">Report Type</label>
                  <select
                    className="input"
                    value={urlData.report_type}
                    onChange={(e) => setUrlData({ ...urlData, report_type: e.target.value })}
                  >
                    <option value="sustainability">Sustainability Report</option>
                    <option value="annual">Annual Report</option>
                    <option value="esg">ESG Report</option>
                    <option value="environmental">Environmental Report</option>
                    <option value="social">Social Impact Report</option>
                    <option value="governance">Governance Report</option>
                  </select>
                </div>
                <div>
                  <label className="label">URL *</label>
                  <input
                    type="url"
                    required
                    className="input"
                    placeholder="https://example.com/report.pdf"
                    value={urlData.url}
                    onChange={(e) => setUrlData({ ...urlData, url: e.target.value })}
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowUrlModal(false)}
                    className="btn-outline"
                    disabled={uploading}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary" disabled={uploading}>
                    {uploading ? <LoadingSpinner size="small" className="mr-2" /> : null}
                    Fetch
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

export default Reports;
