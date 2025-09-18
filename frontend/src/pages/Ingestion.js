import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { ingestionAPI, reportsAPI } from '../services/api';
import {
  CloudArrowUpIcon,
  PlayIcon,
  StopIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Ingestion = () => {
  const { showSuccess, showError } = useApp();
  const [jobs, setJobs] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadData();
    // Poll for job status updates every 5 seconds
    const interval = setInterval(loadJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [jobsResponse, reportsResponse] = await Promise.all([
        ingestionAPI.getJobs(),
        reportsAPI.getAll(),
      ]);
      setJobs(jobsResponse.data.items || []);
      setReports(reportsResponse.data.items || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      showError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadJobs = async () => {
    try {
      const response = await ingestionAPI.getJobs();
      setJobs(response.data.items || []);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  const handleRunJob = async (jobId) => {
    try {
      await ingestionAPI.runJob(jobId);
      showSuccess('Job started successfully');
      loadJobs();
    } catch (error) {
      console.error('Failed to run job:', error);
      showError('Failed to run job');
    }
  };

  const handleDeleteJob = async (jobId) => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      try {
        await ingestionAPI.deleteJob(jobId);
        showSuccess('Job deleted successfully');
        loadJobs();
      } catch (error) {
        console.error('Failed to delete job:', error);
        showError('Failed to delete job');
      }
    }
  };

  const handleCreateIngestionJob = async (reportId) => {
    try {
      await ingestionAPI.createJob({
        report_id: reportId,
        job_type: 'ingestion',
      });
      showSuccess('Ingestion job created successfully');
      loadJobs();
    } catch (error) {
      console.error('Failed to create job:', error);
      showError('Failed to create job');
    }
  };

  const handleCreateExtractionJob = async (reportId) => {
    try {
      await ingestionAPI.extractKPIs(reportId);
      showSuccess('Extraction job created successfully');
      loadJobs();
    } catch (error) {
      console.error('Failed to create extraction job:', error);
      showError('Failed to create extraction job');
    }
  };

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.report_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.job_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !statusFilter || job.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-warning-500" />;
      case 'running':
        return <LoadingSpinner size="small" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-success-500" />;
      case 'failed':
        return <ExclamationCircleIcon className="h-5 w-5 text-danger-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'pending': 'badge-warning',
      'running': 'badge-primary',
      'completed': 'badge-success',
      'failed': 'badge-danger',
    };
    return statusMap[status] || 'badge-gray';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Ingestion Jobs</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor and manage document processing and KPI extraction jobs
        </p>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search jobs..."
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
          <option value="running">Running</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Jobs List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="large" />
        </div>
      ) : (
        <div className="space-y-4">
          {filteredJobs.map((job) => (
            <div key={job.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 mt-1">
                    {getStatusIcon(job.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-medium text-gray-900">
                        {job.job_type === 'ingestion' ? 'Document Processing' : 'KPI Extraction'}
                      </h3>
                      <span className={`badge ${getStatusBadge(job.status)}`}>
                        {job.status}
                      </span>
                    </div>
                    <div className="mt-1 text-sm text-gray-500">
                      Report: {job.report_title || `Report ID: ${job.report_id}`}
                    </div>
                    {job.error_message && (
                      <div className="mt-2 text-sm text-danger-600">
                        Error: {job.error_message}
                      </div>
                    )}
                    <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                      <span>Created: {new Date(job.created_at).toLocaleString()}</span>
                      {job.started_at && (
                        <span>Started: {new Date(job.started_at).toLocaleString()}</span>
                      )}
                      {job.completed_at && (
                        <span>Completed: {new Date(job.completed_at).toLocaleString()}</span>
                      )}
                    </div>
                    {job.progress && (
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                          <span>Progress</span>
                          <span>{job.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${job.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {job.status === 'pending' && (
                    <button
                      onClick={() => handleRunJob(job.id)}
                      className="text-primary-600 hover:text-primary-500"
                      title="Run Job"
                    >
                      <PlayIcon className="h-5 w-5" />
                    </button>
                  )}
                  <button
                    onClick={() => handleDeleteJob(job.id)}
                    className="text-gray-400 hover:text-danger-600"
                    title="Delete Job"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && filteredJobs.length === 0 && (
        <div className="text-center py-12">
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No ingestion jobs</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || statusFilter ? 'No jobs match your filters.' : 'Upload reports to start processing jobs.'}
          </p>
        </div>
      )}

      {/* Available Reports for Processing */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Available Reports</h3>
        <div className="space-y-3">
          {reports.filter(r => r.status === 'uploaded' || r.status === 'processed').slice(0, 5).map((report) => (
            <div key={report.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="text-sm font-medium text-gray-900">{report.title}</h4>
                <p className="text-xs text-gray-500">
                  {report.organization_name} • {report.year} • {report.status}
                </p>
              </div>
              <div className="flex space-x-2">
                {report.status === 'uploaded' && (
                  <button
                    onClick={() => handleCreateIngestionJob(report.id)}
                    className="btn btn-sm bg-primary-600 text-white hover:bg-primary-700"
                  >
                    Process
                  </button>
                )}
                {report.status === 'processed' && (
                  <button
                    onClick={() => handleCreateExtractionJob(report.id)}
                    className="btn btn-sm bg-success-600 text-white hover:bg-success-700"
                  >
                    Extract KPIs
                  </button>
                )}
              </div>
            </div>
          ))}
          {reports.filter(r => r.status === 'uploaded' || r.status === 'processed').length === 0 && (
            <p className="text-sm text-gray-500 text-center py-4">
              No reports available for processing
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Ingestion;
