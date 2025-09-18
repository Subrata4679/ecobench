import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { Alert, AlertDescription } from '../UI/Alert';
// Using emoji icons instead of lucide-react for simplicity
const TrendingUp = () => <span>📈</span>;
const TrendingDown = () => <span>📉</span>;
const AlertTriangle = () => <span>⚠️</span>;
const Target = () => <span>🎯</span>;
const Zap = () => <span>⚡</span>;
const BarChart3 = () => <span>📊</span>;
const PieChart = () => <span>🥧</span>;
const Activity = () => <span>📡</span>;
const Shield = () => <span>🛡️</span>;
const Leaf = () => <span>🍃</span>;
const Users = () => <span>👥</span>;
const Building = () => <span>🏢</span>;

const AdvancedDashboard = ({ apiService }) => {
  const [dashboardData, setDashboardData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [
        predictiveInsights,
        riskAssessment,
        sustainabilityScore,
        carbonAnalysis,
        performanceTrends
      ] = await Promise.all([
        apiService.request('/analytics/predictive-insights'),
        apiService.request('/analytics/risk-assessment'),
        apiService.request('/analytics/sustainability-score'),
        apiService.request('/analytics/carbon-footprint-analysis'),
        apiService.request('/analytics/performance-trends')
      ]);

      setDashboardData({
        insights: predictiveInsights,
        risks: riskAssessment,
        score: sustainabilityScore,
        carbon: carbonAnalysis,
        trends: performanceTrends
      });
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num?.toFixed(1) || '0';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Advanced ESG Analytics</h1>
          <p className="text-gray-600 mt-1">
            AI-powered insights and predictive analytics for your ESG performance
          </p>
        </div>
        <Button onClick={loadDashboardData} disabled={isLoading}>
          <span className="mr-2">📡</span>
          Refresh Data
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <span className="mr-2">⚠️</span>
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'predictions', label: 'Predictions', icon: '📈' },
            { id: 'risks', label: 'Risk Assessment', icon: '🛡️' },
            { id: 'carbon', label: 'Carbon Analysis', icon: '🍃' },
            { id: 'trends', label: 'Performance Trends', icon: '📡' }
          ].map((tab) => {
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && dashboardData.score && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Sustainability Score */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Sustainability Score</p>
                  <p className={`text-3xl font-bold ${getScoreColor(dashboardData.score.overall_score)}`}>
                    {dashboardData.score.overall_score}
                  </p>
                  <p className="text-sm text-gray-500">Rating: {dashboardData.score.rating}</p>
                </div>
                <span className="text-2xl">🎯</span>
              </div>
            </CardContent>
          </Card>

          {/* Risk Level */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Risk Level</p>
                  <p className={`text-2xl font-bold px-3 py-1 rounded-full ${
                    dashboardData.risks?.risk_profile ? getRiskColor(dashboardData.risks.risk_profile.risk_level) : 'text-gray-600'
                  }`}>
                    {dashboardData.risks?.risk_profile?.risk_level || 'Unknown'}
                  </p>
                </div>
                <span className="text-2xl">🛡️</span>
              </div>
            </CardContent>
          </Card>

          {/* Carbon Footprint */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Emissions</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatNumber(dashboardData.carbon?.total_emissions)} tCO2e
                  </p>
                </div>
                <span className="text-2xl">🍃</span>
              </div>
            </CardContent>
          </Card>

          {/* Active Alerts */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Risks</p>
                  <p className="text-2xl font-bold text-red-600">
                    {dashboardData.risks?.risk_profile?.total_risks || 0}
                  </p>
                </div>
                <span className="text-2xl">⚠️</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Predictions Tab */}
      {activeTab === 'predictions' && dashboardData.insights && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span>📈</span>
                Predictive Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData.insights.predictions && Object.keys(dashboardData.insights.predictions).length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(dashboardData.insights.predictions).map(([metric, prediction]) => (
                    <div key={metric} className="border rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-2">
                        {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </h4>
                      
                      {prediction.error ? (
                        <p className="text-red-600 text-sm">{prediction.error}</p>
                      ) : (
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            {prediction.trend_direction === 'increasing' ? (
                              <span className="text-red-500">📈</span>
                            ) : (
                              <span className="text-green-500">📉</span>
                            )}
                            <span className="text-sm font-medium">
                              {prediction.trend_direction} trend
                            </span>
                            <span className={`px-2 py-1 rounded text-xs ${
                              prediction.confidence === 'high' ? 'bg-green-100 text-green-800' :
                              prediction.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {prediction.confidence} confidence
                            </span>
                          </div>
                          
                          {prediction.future_values && (
                            <div className="text-sm text-gray-600">
                              <p>Next year prediction: {Object.values(prediction.future_values)[0]?.toFixed(1)}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No prediction data available. Add more historical data for better insights.</p>
              )}
            </CardContent>
          </Card>

          {/* Optimization Recommendations */}
          {dashboardData.insights.optimizations && (
            <Card>
              <CardHeader>
                <CardTitle>Optimization Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData.insights.optimizations.map((rec, index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4">
                      <h4 className="font-semibold text-gray-900">{rec.title}</h4>
                      <p className="text-gray-600 text-sm mb-2">{rec.description}</p>
                      
                      {rec.potential_impact && (
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Emission Reduction:</span>
                            <p className="text-green-600">{rec.potential_impact.emission_reduction_tco2e?.toFixed(1)} tCO2e</p>
                          </div>
                          <div>
                            <span className="font-medium">Cost Savings:</span>
                            <p className="text-green-600">${formatNumber(rec.potential_impact.cost_savings_usd)}</p>
                          </div>
                          <div>
                            <span className="font-medium">Timeline:</span>
                            <p className="text-blue-600">{rec.potential_impact.implementation_time_months} months</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Risk Assessment Tab */}
      {activeTab === 'risks' && dashboardData.risks && (
        <div className="space-y-6">
          {/* Risk Profile Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6 text-center">
                <span className="text-4xl mb-4 block">🛡️</span>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.risks.risk_profile?.overall_risk_score || 0}
                </p>
                <p className="text-sm text-gray-600">Overall Risk Score</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <span className="text-4xl mb-4 block">⚠️</span>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.risks.risk_profile?.total_risks || 0}
                </p>
                <p className="text-sm text-gray-600">Total Risks Identified</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <span className="text-4xl mb-4 block">🎯</span>
                <p className={`text-2xl font-bold ${getRiskColor(dashboardData.risks.risk_profile?.risk_level).split(' ')[0]}`}>
                  {dashboardData.risks.risk_profile?.risk_level || 'Unknown'}
                </p>
                <p className="text-sm text-gray-600">Risk Level</p>
              </CardContent>
            </Card>
          </div>

          {/* Risk Categories */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Categories</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(dashboardData.risks.risks_by_category || {}).map(([category, risks]) => (
                  <div key={category} className="border rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2 capitalize">
                      {category.replace(/_/g, ' ')} Risks
                    </h4>
                    <p className="text-2xl font-bold text-gray-900 mb-2">{risks.length}</p>
                    
                    {risks.length > 0 && (
                      <div className="space-y-2">
                        {risks.slice(0, 2).map((risk, index) => (
                          <div key={index} className="text-sm">
                            <p className="font-medium">{risk.title}</p>
                            <span className={`px-2 py-1 rounded text-xs ${getRiskColor(risk.severity)}`}>
                              {risk.severity}
                            </span>
                          </div>
                        ))}
                        {risks.length > 2 && (
                          <p className="text-xs text-gray-500">+{risks.length - 2} more risks</p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Carbon Analysis Tab */}
      {activeTab === 'carbon' && dashboardData.carbon && (
        <div className="space-y-6">
          {/* Carbon Footprint Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span>🍃</span>
                Carbon Footprint Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Scope Breakdown */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Emissions by Scope</h4>
                  <div className="space-y-3">
                    {Object.entries(dashboardData.carbon.scope_breakdown || {}).map(([scope, data]) => (
                      <div key={scope} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                        <div>
                          <p className="font-medium">{scope.toUpperCase()}</p>
                          <p className="text-sm text-gray-600">{data.description}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{formatNumber(data.value)} tCO2e</p>
                          <p className="text-sm text-gray-600">{data.percentage?.toFixed(1)}%</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Reduction Targets */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Reduction Targets</h4>
                  <div className="space-y-3">
                    {Object.entries(dashboardData.carbon.reduction_targets || {}).map(([target, value]) => (
                      <div key={target} className="flex justify-between items-center p-3 bg-green-50 rounded">
                        <span className="text-sm font-medium">
                          {target.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        <span className="font-bold text-green-700">
                          {formatNumber(value)} tCO2e
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Offset Requirements */}
              {dashboardData.carbon.offset_requirements && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-900 mb-2">Carbon Offset Requirements</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-blue-700">Residual Emissions</p>
                      <p className="font-bold text-blue-900">
                        {formatNumber(dashboardData.carbon.offset_requirements.residual_emissions)} tCO2e
                      </p>
                    </div>
                    <div>
                      <p className="text-blue-700">Estimated Cost</p>
                      <p className="font-bold text-blue-900">
                        ${formatNumber(dashboardData.carbon.offset_requirements.estimated_offset_cost)}
                      </p>
                    </div>
                    <div>
                      <p className="text-blue-700">Projects Needed</p>
                      <p className="font-bold text-blue-900">
                        {dashboardData.carbon.offset_requirements.offset_projects_needed}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Performance Trends Tab */}
      {activeTab === 'trends' && dashboardData.trends && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>📡</span>
              Performance Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            {dashboardData.trends.trends && Object.keys(dashboardData.trends.trends).length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(dashboardData.trends.trends).map(([metric, trend]) => (
                  <div key={metric} className="border rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">
                      {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h4>
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Current Value:</span>
                        <span className="font-medium">{trend.latest_value?.toFixed(1)}</span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Trend:</span>
                        <div className="flex items-center gap-1">
                          {trend.trend_direction === 'increasing' ? (
                            <span className="text-red-500">📈</span>
                          ) : (
                            <span className="text-green-500">📉</span>
                          )}
                          <span className="text-sm font-medium">{trend.trend_direction}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Change from Start:</span>
                        <span className={`font-medium ${
                          trend.change_from_first > 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {trend.change_from_first > 0 ? '+' : ''}{trend.change_from_first?.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">No trend data available. Add more historical data to see trends.</p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AdvancedDashboard;
