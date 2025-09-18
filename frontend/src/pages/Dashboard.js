import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { organizationsAPI, kpisAPI, reportsAPI, recommendationsAPI } from '../services/api';
import {
  BuildingOfficeIcon,
  DocumentTextIcon,
  ChartBarIcon,
  LightBulbIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Dashboard = () => {
  const { showError } = useApp();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    organizations: 0,
    reports: 0,
    kpis: 0,
    recommendations: 0,
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [topKPIs, setTopKPIs] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load basic stats
      const [orgsResponse, reportsResponse, kpisResponse, recsResponse] = await Promise.all([
        organizationsAPI.getAll({ limit: 1 }),
        reportsAPI.getAll({ limit: 1 }),
        kpisAPI.getDefinitions({ limit: 1 }),
        recommendationsAPI.getAll({ limit: 1 }),
      ]);

      setStats({
        organizations: orgsResponse.data.total || 0,
        reports: reportsResponse.data.total || 0,
        kpis: kpisResponse.data.total || 0,
        recommendations: recsResponse.data.total || 0,
      });

      // Load recent reports for activity
      const recentReports = await reportsAPI.getAll({ limit: 5, sort: 'created_at', order: 'desc' });
      setRecentActivity(recentReports.data.items || []);

      // Load top KPIs
      const kpiDefinitions = await kpisAPI.getDefinitions({ limit: 6 });
      setTopKPIs(kpiDefinitions.data.items || []);

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      showError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      name: 'Organizations',
      value: stats.organizations,
      icon: BuildingOfficeIcon,
      color: 'bg-primary-500',
      change: '+12%',
      changeType: 'increase',
    },
    {
      name: 'Reports',
      value: stats.reports,
      icon: DocumentTextIcon,
      color: 'bg-success-500',
      change: '+8%',
      changeType: 'increase',
    },
    {
      name: 'KPIs Tracked',
      value: stats.kpis,
      icon: ChartBarIcon,
      color: 'bg-warning-500',
      change: '+15%',
      changeType: 'increase',
    },
    {
      name: 'Recommendations',
      value: stats.recommendations,
      icon: LightBulbIcon,
      color: 'bg-purple-500',
      change: '-2%',
      changeType: 'decrease',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your ESG benchmarking activities
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="stat-card">
            <div className="stat-card-content">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`stat-card-icon ${stat.color} rounded-md p-3`}>
                    <stat.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">
                        {stat.value.toLocaleString()}
                      </div>
                      <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                        stat.changeType === 'increase' ? 'text-success-600' : 'text-danger-600'
                      }`}>
                        {stat.changeType === 'increase' ? (
                          <ArrowUpIcon className="self-center flex-shrink-0 h-4 w-4" />
                        ) : (
                          <ArrowDownIcon className="self-center flex-shrink-0 h-4 w-4" />
                        )}
                        <span className="sr-only">
                          {stat.changeType === 'increase' ? 'Increased' : 'Decreased'} by
                        </span>
                        {stat.change}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Recent Reports</h3>
            <button className="text-sm text-primary-600 hover:text-primary-500">
              View all
            </button>
          </div>
          <div className="space-y-3">
            {recentActivity.length > 0 ? (
              recentActivity.map((report) => (
                <div key={report.id} className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {report.title}
                    </p>
                    <p className="text-sm text-gray-500">
                      {report.organization_name} • {new Date(report.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <span className={`badge ${
                      report.status === 'processed' ? 'badge-success' :
                      report.status === 'processing' ? 'badge-warning' : 'badge-gray'
                    }`}>
                      {report.status}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">No recent reports</p>
            )}
          </div>
        </div>

        {/* Top KPIs */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">KPI Categories</h3>
            <button className="text-sm text-primary-600 hover:text-primary-500">
              View all
            </button>
          </div>
          <div className="space-y-3">
            {topKPIs.length > 0 ? (
              topKPIs.map((kpi) => (
                <div key={kpi.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <ChartBarIcon className="h-6 w-6 text-gray-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {kpi.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {kpi.category} • {kpi.unit || 'No unit'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUpIcon className="h-4 w-4 text-success-500" />
                    <span className="text-sm text-gray-500">Active</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">No KPIs defined</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="btn-outline flex flex-col items-center p-4 space-y-2">
            <BuildingOfficeIcon className="h-8 w-8 text-gray-400" />
            <span>Add Organization</span>
          </button>
          <button className="btn-outline flex flex-col items-center p-4 space-y-2">
            <DocumentTextIcon className="h-8 w-8 text-gray-400" />
            <span>Upload Report</span>
          </button>
          <button className="btn-outline flex flex-col items-center p-4 space-y-2">
            <ChartBarIcon className="h-8 w-8 text-gray-400" />
            <span>Define KPI</span>
          </button>
          <button className="btn-outline flex flex-col items-center p-4 space-y-2">
            <LightBulbIcon className="h-8 w-8 text-gray-400" />
            <span>Get Recommendations</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
