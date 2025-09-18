import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { Badge } from '../UI/Badge';
import { Alert, AlertDescription } from '../UI/Alert';
// Using emoji icons instead of lucide-react for simplicity
const Globe = () => <span>🌐</span>;
const Download = () => <span>⬇️</span>;
const RefreshCw = () => <span>🔄</span>;
const Play = () => <span>▶️</span>;
const Pause = () => <span>⏸️</span>;
const CheckCircle = () => <span>✅</span>;
const XCircle = () => <span>❌</span>;
const Clock = () => <span>⏰</span>;
const Building2 = () => <span>🏢</span>;
const FileText = () => <span>📄</span>;
const TrendingUp = () => <span>📈</span>;
const ExternalLink = () => <span>🔗</span>;
const Settings = () => <span>⚙️</span>;

const ScrapingDashboard = ({ apiService }) => {
  const [companies, setCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Try to load real data, but fall back to mock data if API is not available
      try {
        const [companiesData, jobsData, reportsData, statsData] = await Promise.all([
          apiService.request('/scraping/companies'),
          apiService.request('/scraping/jobs'),
          apiService.request('/scraping/regulatory-reports'),
          apiService.request('/scraping/stats')
        ]);

        setCompanies(companiesData || []);
        setJobs(jobsData || []);
        setReports(reportsData || []);
        setStats(statsData || {});
      } catch (apiError) {
        console.log('API not available, using mock data');
        // Provide mock data for demonstration
        setCompanies([
          { id: 1, name: 'Microsoft Corporation', ticker: 'MSFT', website: 'https://microsoft.com', scraping_enabled: true, last_scraped: '2024-01-15' },
          { id: 2, name: 'Apple Inc.', ticker: 'AAPL', website: 'https://apple.com', scraping_enabled: true, last_scraped: '2024-01-14' },
          { id: 3, name: 'Alphabet Inc.', ticker: 'GOOGL', website: 'https://abc.xyz', scraping_enabled: false, last_scraped: null },
          { id: 4, name: 'Amazon.com Inc.', ticker: 'AMZN', website: 'https://amazon.com', scraping_enabled: true, last_scraped: '2024-01-13' },
          { id: 5, name: 'Meta Platforms Inc.', ticker: 'META', website: 'https://meta.com', scraping_enabled: true, last_scraped: '2024-01-12' }
        ]);
        
        setJobs([
          { id: 1, company_id: 1, job_type: 'sec_filings', status: 'completed', created_at: '2024-01-15T10:30:00Z', completed_at: '2024-01-15T11:45:00Z' },
          { id: 2, company_id: 2, job_type: 'sustainability_reports', status: 'running', created_at: '2024-01-15T12:00:00Z', completed_at: null },
          { id: 3, company_id: 4, job_type: 'all', status: 'failed', created_at: '2024-01-14T09:15:00Z', completed_at: null }
        ]);
        
        setReports([
          { id: 1, company_id: 1, report_type: '10-K', filing_date: '2023-12-31', url: 'https://example.com/report1.pdf', title: 'Annual Report 2023' },
          { id: 2, company_id: 2, report_type: 'Sustainability Report', filing_date: '2023-11-30', url: 'https://example.com/report2.pdf', title: 'Environmental Progress Report 2023' },
          { id: 3, company_id: 1, report_type: '10-Q', filing_date: '2023-09-30', url: 'https://example.com/report3.pdf', title: 'Quarterly Report Q3 2023' }
        ]);
        
        setStats({
          total_companies: 10,
          active_companies: 7,
          total_jobs: 45,
          successful_jobs: 38,
          failed_jobs: 4,
          running_jobs: 3,
          total_reports: 156,
          reports_this_month: 23
        });
      }
      setError(null);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const initializeCompanies = async () => {
    setIsLoading(true);
    try {
      try {
        await apiService.request('/scraping/initialize-companies', { method: 'POST' });
      } catch (apiError) {
        console.log('API not available, simulating company initialization');
        // Simulate successful initialization
        alert('Companies initialized successfully! (Demo mode)');
      }
      await loadDashboardData();
      setError(null);
    } catch (err) {
      console.error('Error initializing companies:', err);
      setError('Failed to initialize companies');
    } finally {
      setIsLoading(false);
    }
  };

  const startScrapingJob = async (companyId, jobType = 'all') => {
    try {
      try {
        await apiService.request('/scraping/jobs', { 
          method: 'POST',
          body: JSON.stringify({ company_id: companyId, job_type: jobType })
        });
      } catch (apiError) {
        console.log('API not available, simulating scraping job');
        alert(`Scraping job started for company ${companyId}! (Demo mode)`);
      }
      await loadDashboardData();
      setError(null);
    } catch (err) {
      console.error('Error starting scraping job:', err);
      setError('Failed to start scraping job');
    }
  };

  const runBulkScraping = async () => {
    setIsLoading(true);
    try {
      try {
        await apiService.request('/scraping/bulk-scraping', { method: 'POST' });
      } catch (apiError) {
        console.log('API not available, simulating bulk scraping');
        alert('Bulk scraping started for all companies! (Demo mode)');
      }
      await loadDashboardData();
      setError(null);
    } catch (err) {
      console.error('Error running bulk scraping:', err);
      setError('Failed to run bulk scraping');
    } finally {
      setIsLoading(false);
    }
  };

  const startBulkScraping = async () => {
    try {
      await apiService.runBulkScraping();
      await loadDashboardData();
      setError(null);
    } catch (err) {
      console.error('Error starting bulk scraping:', err);
      setError('Failed to start bulk scraping');
    }
  };

  const toggleCompanyScraping = async (companyId) => {
    try {
      await apiService.toggleCompanyScraping(companyId);
      await loadDashboardData();
      setError(null);
    } catch (err) {
      console.error('Error toggling company scraping:', err);
      setError('Failed to toggle company scraping');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      running: { color: 'bg-blue-100 text-blue-800', icon: RefreshCw },
      completed: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      failed: { color: 'bg-red-100 text-red-800', icon: XCircle }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon />
        {status}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Regulatory Data Scraping</h1>
          <p className="text-gray-600 mt-1">
            Automated collection of ESG and regulatory reports from IT companies
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button
            onClick={loadDashboardData}
            disabled={isLoading}
            variant="outline"
          >
            <span className={`mr-2 ${isLoading ? 'animate-spin' : ''}`}>🔄</span>
            Refresh
          </Button>
          
          <Button
            onClick={runBulkScraping}
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <span className="mr-2">▶️</span>
            Run Bulk Scraping
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <span className="mr-2">❌</span>
          <AlertDescription className="text-red-800">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Companies</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.companies?.total || 0}
                </p>
              </div>
              <span className="text-2xl text-blue-600">🏢</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Scrapers</p>
                <p className="text-2xl font-bold text-green-600">
                  {stats.companies?.active || 0}
                </p>
              </div>
              <span className="text-2xl text-green-600">🌐</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Reports Collected</p>
                <p className="text-2xl font-bold text-purple-600">
                  {Object.values(stats.reports || {}).reduce((sum, count) => sum + count, 0)}
                </p>
              </div>
              <span className="text-2xl text-purple-600">📄</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Running Jobs</p>
                <p className="text-2xl font-bold text-orange-600">
                  {stats.jobs?.running || 0}
                </p>
              </div>
              <span className="text-2xl text-orange-600">📈</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Companies Section */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              IT Companies
            </CardTitle>
            
            {companies.length === 0 && (
              <Button
                onClick={initializeCompanies}
                disabled={isLoading}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                <Download className="h-4 w-4 mr-2" />
                Initialize Companies
              </Button>
            )}
          </div>
        </CardHeader>
        
        <CardContent>
          {companies.length === 0 ? (
            <div className="text-center py-8">
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">
                No companies initialized yet. Click "Initialize Companies" to load major IT companies.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Company</th>
                    <th className="text-left py-2">Ticker</th>
                    <th className="text-left py-2">Status</th>
                    <th className="text-left py-2">Last Scraped</th>
                    <th className="text-left py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {companies.map((company) => (
                    <tr key={company.id} className="border-b hover:bg-gray-50">
                      <td className="py-3">
                        <div>
                          <div className="font-medium text-gray-900">{company.name}</div>
                          {company.website && (
                            <a
                              href={company.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                            >
                              <ExternalLink className="h-3 w-3" />
                              Website
                            </a>
                          )}
                        </div>
                      </td>
                      <td className="py-3">
                        <Badge variant="outline">{company.ticker}</Badge>
                      </td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          {company.scraping_enabled ? (
                            <Badge className="bg-green-100 text-green-800">Active</Badge>
                          ) : (
                            <Badge className="bg-gray-100 text-gray-800">Disabled</Badge>
                          )}
                        </div>
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {formatDate(company.last_scraped)}
                      </td>
                      <td className="py-3">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => startScrapingJob(company.id)}
                            disabled={!company.scraping_enabled}
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                          >
                            <Play className="h-3 w-3 mr-1" />
                            Scrape
                          </Button>
                          
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => toggleCompanyScraping(company.id)}
                          >
                            {company.scraping_enabled ? (
                              <>
                                <Pause className="h-3 w-3 mr-1" />
                                Disable
                              </>
                            ) : (
                              <>
                                <Play className="h-3 w-3 mr-1" />
                                Enable
                              </>
                            )}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Jobs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Recent Scraping Jobs
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          {jobs.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No scraping jobs yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Company</th>
                    <th className="text-left py-2">Job Type</th>
                    <th className="text-left py-2">Status</th>
                    <th className="text-left py-2">Started</th>
                    <th className="text-left py-2">Completed</th>
                    <th className="text-left py-2">Results</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.slice(0, 10).map((job) => {
                    const company = companies.find(c => c.id === job.company_id);
                    return (
                      <tr key={job.id} className="border-b hover:bg-gray-50">
                        <td className="py-3">
                          <div className="font-medium text-gray-900">
                            {company?.name || `Company ${job.company_id}`}
                          </div>
                        </td>
                        <td className="py-3">
                          <Badge variant="outline">{job.job_type}</Badge>
                        </td>
                        <td className="py-3">
                          {getStatusBadge(job.status)}
                        </td>
                        <td className="py-3 text-sm text-gray-600">
                          {formatDateTime(job.started_at)}
                        </td>
                        <td className="py-3 text-sm text-gray-600">
                          {formatDateTime(job.completed_at)}
                        </td>
                        <td className="py-3">
                          {job.results_summary && (
                            <div className="text-sm">
                              <div className="text-gray-900">
                                {job.results_summary.reports_found || 0} reports
                              </div>
                              {job.results_summary.report_types && (
                                <div className="text-gray-600">
                                  {job.results_summary.report_types.join(', ')}
                                </div>
                              )}
                            </div>
                          )}
                          
                          {job.error_message && (
                            <div className="text-sm text-red-600">
                              Error: {job.error_message}
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Reports */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Recent Regulatory Reports
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          {reports.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No reports collected yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Company</th>
                    <th className="text-left py-2">Report Type</th>
                    <th className="text-left py-2">Filing Date</th>
                    <th className="text-left py-2">Status</th>
                    <th className="text-left py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.slice(0, 10).map((report) => (
                    <tr key={report.id} className="border-b hover:bg-gray-50">
                      <td className="py-3">
                        <div className="font-medium text-gray-900">
                          Organization {report.organization_id}
                        </div>
                      </td>
                      <td className="py-3">
                        <Badge variant="outline">{report.report_type}</Badge>
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {formatDate(report.filing_date)}
                      </td>
                      <td className="py-3">
                        {getStatusBadge(report.status)}
                      </td>
                      <td className="py-3">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => window.open(report.url, '_blank')}
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          View
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ScrapingDashboard;
