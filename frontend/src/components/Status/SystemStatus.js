import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';

const SystemStatus = ({ apiService }) => {
  const [systemHealth, setSystemHealth] = useState({
    backend: 'connected',
    database: 'healthy',
    monitoring: 'active',
    scraping: 'running',
    ai_services: 'operational'
  });

  const [metrics, setMetrics] = useState({
    uptime: '99.9%',
    responseTime: '45ms',
    activeUsers: 1,
    dataPoints: 15420,
    lastUpdate: new Date()
  });

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate real-time updates
      setMetrics(prev => ({
        ...prev,
        responseTime: `${Math.floor(Math.random() * 50) + 20}ms`,
        dataPoints: prev.dataPoints + Math.floor(Math.random() * 10),
        lastUpdate: new Date()
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
      case 'healthy':
      case 'active':
      case 'running':
      case 'operational':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
      case 'disconnected':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
      case 'healthy':
      case 'active':
      case 'running':
      case 'operational':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
      case 'disconnected':
        return '❌';
      default:
        return '⚪';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🔧 System Health
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(systemHealth).map(([service, status]) => (
              <div key={service} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>{getStatusIcon(status)}</span>
                  <span className="font-medium capitalize">
                    {service.replace('_', ' ')}
                  </span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                  {status}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📊 Performance Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{metrics.uptime}</div>
              <div className="text-sm text-blue-700">Uptime</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{metrics.responseTime}</div>
              <div className="text-sm text-green-700">Response Time</div>
            </div>
            <div className="text-center p-3 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{metrics.activeUsers}</div>
              <div className="text-sm text-purple-700">Active Users</div>
            </div>
            <div className="text-center p-3 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{metrics.dataPoints.toLocaleString()}</div>
              <div className="text-sm text-orange-700">Data Points</div>
            </div>
          </div>
          <div className="mt-4 text-xs text-gray-500 text-center">
            Last updated: {metrics.lastUpdate.toLocaleTimeString()}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SystemStatus;
