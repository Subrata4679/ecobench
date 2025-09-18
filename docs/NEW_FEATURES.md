# EcoBench Enhanced Features Documentation

## Overview

This document describes the new features added to the EcoBench ESG benchmarking platform, including automated regulatory report scraping and an intelligent ESG chatbot for comparative analysis.

## New Features

### 1. Automated Regulatory Report Scraping

#### Description
Automatically collects ESG and regulatory reports from major IT companies' official websites and SEC filings.

#### Key Components
- **Web Scraping Service**: Automated collection from multiple sources
- **IT Company Database**: Pre-configured list of major tech companies
- **Regulatory Report Storage**: Structured storage of collected documents
- **Scraping Jobs Management**: Background job processing and monitoring

#### Supported Data Sources
- SEC EDGAR filings (10-K, 10-Q, 20-F, 8-K)
- Company sustainability reports
- Investor relations documents
- Corporate responsibility reports

#### Major IT Companies Included
- Microsoft Corporation (MSFT)
- Apple Inc. (AAPL)
- Alphabet Inc. (GOOGL)
- Amazon.com Inc. (AMZN)
- Meta Platforms Inc. (META)
- Tesla Inc. (TSLA)
- NVIDIA Corporation (NVDA)
- Oracle Corporation (ORCL)
- Salesforce Inc. (CRM)
- Adobe Inc. (ADBE)

### 2. Intelligent ESG Chatbot

#### Description
AI-powered chatbot that provides personalized ESG insights and recommendations based on user's company data and industry benchmarks.

#### Key Features
- **Comparative Analysis**: Compare user's ESG metrics against industry peers
- **Personalized Recommendations**: AI-generated improvement suggestions
- **Industry Benchmarking**: Real-time comparison with IT sector companies
- **Regulatory Insights**: Information from collected regulatory reports
- **Interactive Chat Interface**: Natural language conversation

#### Supported ESG Metrics
- Scope 1, 2, and 3 emissions (tCO2e)
- Water consumption (m³)
- Waste generation (tonnes)
- Energy consumption (MWh)
- Renewable energy percentage (%)
- Employee count
- Annual revenue (USD)

## API Endpoints

### Scraping Endpoints

#### Companies Management
```
GET /api/scraping/companies - Get list of IT companies
POST /api/scraping/initialize-companies - Initialize company database
PUT /api/scraping/companies/{id}/toggle-scraping - Enable/disable scraping
```

#### Scraping Jobs
```
GET /api/scraping/jobs - Get scraping jobs
POST /api/scraping/jobs - Create new scraping job
POST /api/scraping/bulk-scraping - Run bulk scraping for all companies
GET /api/scraping/jobs/{id} - Get specific job details
```

#### Regulatory Reports
```
GET /api/scraping/regulatory-reports - Get collected reports
GET /api/scraping/regulatory-reports/{id} - Get specific report
```

#### Statistics
```
GET /api/scraping/stats - Get scraping statistics
```

### Chatbot Endpoints

#### ESG Data Management
```
POST /api/chatbot/esg-data - Create/update user ESG data
GET /api/chatbot/esg-data - Get user's ESG data
GET /api/chatbot/esg-data/{year} - Get ESG data for specific year
```

#### Analysis
```
GET /api/chatbot/analysis - Get comprehensive ESG analysis
GET /api/chatbot/quick-analysis - Get quick analysis summary
GET /api/chatbot/benchmarks/{metric} - Get industry benchmarks
```

#### Chat Sessions
```
POST /api/chatbot/chat/sessions - Create new chat session
GET /api/chatbot/chat/sessions - Get user's chat sessions
DELETE /api/chatbot/chat/sessions/{id} - Delete chat session
```

#### Chat Messages
```
GET /api/chatbot/chat/sessions/{id}/messages - Get chat history
POST /api/chatbot/chat/sessions/{id}/messages - Send message
```

## Database Schema Changes

### New Tables

#### `it_company`
Stores information about IT companies for scraping:
- Company details (name, ticker, website)
- SEC information (CIK number)
- Scraping configuration
- Last scraping timestamp

#### `scraping_job`
Tracks scraping job execution:
- Job type and status
- Start/completion timestamps
- Results summary
- Error messages

#### `regulatory_report`
Stores collected regulatory reports:
- Report metadata (type, filing date)
- Source URL and file path
- Processing status
- Extracted data (JSON)

#### `user_esg_data`
Stores user's ESG metrics:
- Company information
- ESG metrics (emissions, water, waste, energy)
- Additional custom metrics
- Year-based tracking

#### `chat_session`
Manages chat sessions:
- User association
- Session metadata
- Context data for analysis

#### `chat_message`
Stores chat conversation:
- Message content and role
- Metadata (analysis results, sources)
- Timestamps

## Frontend Components

### 1. ESGDataForm Component
- **Location**: `src/components/ESGDataForm/ESGDataForm.js`
- **Purpose**: User input form for ESG metrics
- **Features**:
  - Comprehensive ESG data input
  - Real-time validation
  - Visual indicators for metric types
  - Advanced fields toggle
  - Help documentation

### 2. ChatInterface Component
- **Location**: `src/components/Chatbot/ChatInterface.js`
- **Purpose**: Interactive chatbot interface
- **Features**:
  - Real-time messaging
  - Suggested questions
  - Analysis metadata display
  - Chat history management
  - Error handling

### 3. ScrapingDashboard Component
- **Location**: `src/components/Scraping/ScrapingDashboard.js`
- **Purpose**: Scraping management interface
- **Features**:
  - Company management
  - Job monitoring
  - Report viewing
  - Statistics dashboard
  - Bulk operations

## Configuration

### Environment Variables

#### Required for Chatbot
```bash
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
CHATBOT_ENABLED=true
```

#### Required for Scraping
```bash
SCRAPING_ENABLED=true
SCRAPING_DELAY_SECONDS=2
MAX_CONCURRENT_SCRAPING_JOBS=3
```

### Dependencies Added

#### Backend
- `beautifulsoup4==4.12.2` - HTML parsing
- `selenium==4.15.2` - Web automation
- `requests==2.31.0` - HTTP requests
- `lxml==4.9.3` - XML/HTML processing
- `scrapy==2.11.0` - Web scraping framework
- `feedparser==6.0.10` - RSS/Atom feed parsing
- `schedule==1.2.0` - Job scheduling

## Usage Guide

### Setting Up Scraping

1. **Initialize Companies**:
   ```bash
   POST /api/scraping/initialize-companies
   ```

2. **Start Scraping for Specific Company**:
   ```bash
   POST /api/scraping/jobs
   {
     "company_id": 1,
     "job_type": "all"
   }
   ```

3. **Run Bulk Scraping**:
   ```bash
   POST /api/scraping/bulk-scraping
   ```

### Using the Chatbot

1. **Input ESG Data**:
   - Use the ESG Data Form to input your company's metrics
   - Data is automatically saved and associated with your user account

2. **Start Chat Session**:
   - Create a new chat session
   - The chatbot has access to your ESG data for personalized analysis

3. **Ask Questions**:
   - "How does my carbon footprint compare to industry peers?"
   - "What are my top improvement areas?"
   - "Show me the latest regulatory requirements"

### Example Analysis Output

The chatbot provides detailed analysis including:

```json
{
  "company_name": "Your Company",
  "year": 2023,
  "overall_score": 75.2,
  "metrics_analysis": {
    "scope1_emissions": {
      "user_value": 1250.5,
      "industry_median": 1500.0,
      "percentile": 35.2,
      "performance_level": "Good",
      "comparison": "Your Scope 1 Emissions of 1,250.5 tCO2e is 16.6% lower than the industry median..."
    }
  },
  "recommendations": [
    "Consider implementing carbon reduction strategies...",
    "Increase renewable energy adoption..."
  ]
}
```

## Security Considerations

### Data Protection
- All user ESG data is encrypted at rest
- API endpoints require authentication
- Rate limiting on scraping operations
- Secure handling of external API keys

### Scraping Ethics
- Respectful delays between requests
- Compliance with robots.txt
- User-Agent identification
- No aggressive scraping patterns

## Monitoring and Maintenance

### Scraping Jobs
- Monitor job success rates
- Review error logs regularly
- Update company information as needed
- Manage storage for collected reports

### Chatbot Performance
- Monitor OpenAI API usage and costs
- Track user engagement metrics
- Review and improve response quality
- Update industry benchmarks regularly

## Troubleshooting

### Common Issues

#### Scraping Failures
- **Issue**: Jobs failing with timeout errors
- **Solution**: Increase delay between requests, check network connectivity

#### Chatbot Not Responding
- **Issue**: OpenAI API errors
- **Solution**: Verify API key, check quota limits, review error logs

#### Missing Industry Data
- **Issue**: No benchmark data available
- **Solution**: Run scraping jobs, verify data processing, check database

### Logs and Debugging
- Application logs: `/var/log/ecobench/`
- Scraping logs: Check `scraping_job` table error messages
- Chat logs: Review `chat_message` metadata for errors

## Future Enhancements

### Planned Features
1. **Advanced Analytics Dashboard**
   - Trend analysis over time
   - Peer group comparisons
   - Regulatory compliance tracking

2. **Enhanced Scraping**
   - Support for more document types
   - Automated data extraction improvements
   - Real-time monitoring alerts

3. **Chatbot Improvements**
   - Multi-language support
   - Voice interface
   - Integration with external ESG databases

4. **Reporting Features**
   - Automated ESG report generation
   - Compliance reporting templates
   - Stakeholder communication tools

## Support and Contact

For technical support or questions about the new features:
- Documentation: `/docs/`
- API Documentation: `/docs` (Swagger UI)
- Issues: Create GitHub issues for bug reports
- Feature Requests: Use GitHub discussions

---

*Last Updated: September 2024*
*Version: 2.0.0*
