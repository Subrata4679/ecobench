# EcoBench Enhanced Features - Quick Integration Guide

## 🚀 Quick Start

This guide will help you set up and use the new automated scraping and intelligent chatbot features in EcoBench.

## Prerequisites

1. **OpenAI API Key** (for chatbot functionality)
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Generate an API key
   - Ensure you have sufficient credits/quota

2. **Updated Dependencies**
   - Run `pip install -r requirements.txt` in the backend directory
   - Install Chrome/Chromium for Selenium (web scraping)

## 🔧 Setup Instructions

### 1. Environment Configuration

Update your `.env` file with the new variables:

```bash
# Copy from .env.example
cp backend/.env.example backend/.env

# Edit the .env file and add:
OPENAI_API_KEY=your_actual_openai_api_key_here
LLM_PROVIDER=openai
SCRAPING_ENABLED=true
CHATBOT_ENABLED=true
```

### 2. Database Migration

Run the new database migrations:

```bash
cd backend
alembic upgrade head
```

This will create the new tables for:
- IT companies and scraping jobs
- Regulatory reports
- User ESG data
- Chat sessions and messages

### 3. Start the Services

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
cd frontend
npm start
```

## 📊 Using the New Features

### Step 1: Initialize IT Companies

1. Navigate to the **Scraping Dashboard** in the web interface
2. Click **"Initialize Companies"** to load the pre-configured IT companies
3. This adds 10 major tech companies (Microsoft, Apple, Google, etc.) to the database

### Step 2: Start Data Collection

**Option A: Single Company Scraping**
1. In the Scraping Dashboard, find a company (e.g., Microsoft)
2. Click **"Scrape"** to collect their regulatory reports
3. Monitor the job progress in the "Recent Scraping Jobs" section

**Option B: Bulk Scraping**
1. Click **"Run Bulk Scraping"** to collect data from all active companies
2. This runs in the background and may take several minutes

### Step 3: Input Your ESG Data

1. Navigate to the **ESG Data Input** section
2. Fill in your company's ESG metrics:
   - Company name and reporting year
   - Emissions data (Scope 1, 2, 3)
   - Resource consumption (water, waste, energy)
   - Renewable energy percentage
   - Optional: Employee count and revenue

3. Click **"Save ESG Data"**

### Step 4: Use the Intelligent Chatbot

1. Go to the **ESG Chatbot** section
2. Click **"Start New Chat"** to create a session
3. Try these example questions:

```
"How does my company's carbon footprint compare to industry peers?"

"What are the top 3 areas where I can improve my ESG performance?"

"Show me the latest regulatory requirements for IT companies"

"What ESG metrics should I focus on for better investor relations?"
```

## 🎯 Key Features Demonstration

### Automated Scraping Results

After running scraping jobs, you'll see:
- **Regulatory reports** from SEC filings (10-K, 10-Q forms)
- **Sustainability reports** from company websites
- **Investor relations** documents
- **Real-time job status** and progress tracking

### Intelligent Analysis

The chatbot provides:
- **Percentile rankings** against industry peers
- **Performance levels** (Excellent, Good, Average, Needs Improvement)
- **Specific recommendations** for improvement
- **Industry context** from collected regulatory data

### Example Analysis Output

```
Your Scope 1 Emissions of 1,250.5 tCO2e is 16.6% lower than the 
industry median of 1,500.0 tCO2e. You rank in the 35th percentile.

Recommendations:
• Consider implementing carbon reduction strategies for Scope 2 Emissions
• Increase renewable energy adoption from 45% to 65%
• Implement water efficiency measures to reduce consumption
```

## 🔍 Monitoring and Troubleshooting

### Check Scraping Status

```bash
# View recent scraping jobs
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/scraping/jobs

# Check scraping statistics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/scraping/stats
```

### Verify Chatbot Functionality

```bash
# Test ESG analysis endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/chatbot/analysis

# Check if OpenAI integration is working
curl -H "Authorization: Bearer YOUR_TOKEN" \
  -X POST http://localhost:8000/api/chatbot/chat/sessions \
  -d '{"session_name": "Test Session"}'
```

### Common Issues and Solutions

**Issue: Scraping jobs failing**
- Check internet connectivity
- Verify Chrome/Chromium installation
- Review error messages in scraping jobs table

**Issue: Chatbot not responding**
- Verify OpenAI API key is correct
- Check API quota and billing
- Ensure `LLM_PROVIDER=openai` in .env

**Issue: No industry benchmarks available**
- Run scraping jobs to collect industry data
- Wait for data processing to complete
- Check that companies have been initialized

## 📈 Advanced Usage

### Custom ESG Metrics

Add custom metrics to your ESG data:

```json
{
  "additional_metrics": {
    "diversity_percentage": 45.2,
    "supplier_sustainability_score": 78.5,
    "community_investment_usd": 250000
  }
}
```

### Automated Reporting

Set up scheduled scraping (add to cron or task scheduler):

```bash
# Daily scraping at 2 AM
0 2 * * * curl -X POST http://localhost:8000/api/scraping/bulk-scraping
```

### API Integration

Integrate with your existing systems:

```python
import requests

# Submit ESG data programmatically
esg_data = {
    "company_name": "Your Company",
    "year": 2023,
    "scope1_emissions": 1250.5,
    "scope2_emissions": 2100.3,
    # ... other metrics
}

response = requests.post(
    "http://localhost:8000/api/chatbot/esg-data",
    json=esg_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

## 🎉 Success Indicators

You'll know everything is working when you see:

✅ **Scraping Dashboard** shows active companies and recent jobs
✅ **Regulatory Reports** are being collected (check the reports table)
✅ **ESG Analysis** shows your percentile rankings and comparisons
✅ **Chatbot** provides intelligent, contextual responses
✅ **Industry Benchmarks** are available for your metrics

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: Backend logs show detailed error information
2. **Review the API docs**: Visit `/docs` for interactive API documentation
3. **Verify configuration**: Ensure all environment variables are set correctly
4. **Test step by step**: Use the API endpoints directly to isolate issues

## 📚 Next Steps

Once you have the basic features working:

1. **Explore advanced analytics** in the dashboard
2. **Set up automated scraping schedules**
3. **Integrate with your existing ESG reporting workflows**
4. **Customize the chatbot prompts** for your specific needs
5. **Export data** for external analysis and reporting

---

**Need more help?** Check the full documentation in `/docs/NEW_FEATURES.md` or create an issue in the project repository.
