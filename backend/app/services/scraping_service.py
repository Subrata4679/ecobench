"""
Web scraping service for collecting regulatory reports from IT companies
"""
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict, Optional, Any
import json
import re
from datetime import datetime, timedelta
import logging
from urllib.parse import urljoin, urlparse
import feedparser
import time

from app.models import ITCompany, RegulatoryReport, ScrapingJob, Organization
from app.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ITCompanyScrapingService:
    """Service for scraping regulatory reports from IT companies"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Major IT companies to track
        self.it_companies_data = [
            {
                "name": "Microsoft Corporation",
                "ticker": "MSFT",
                "exchange": "NASDAQ",
                "website": "https://www.microsoft.com",
                "sec_cik": "0000789019",
                "investor_relations": "https://www.microsoft.com/en-us/Investor/",
                "sustainability_url": "https://www.microsoft.com/en-us/corporate-responsibility/sustainability"
            },
            {
                "name": "Apple Inc.",
                "ticker": "AAPL",
                "exchange": "NASDAQ",
                "website": "https://www.apple.com",
                "sec_cik": "0000320193",
                "investor_relations": "https://investor.apple.com/",
                "sustainability_url": "https://www.apple.com/environment/"
            },
            {
                "name": "Alphabet Inc.",
                "ticker": "GOOGL",
                "exchange": "NASDAQ",
                "website": "https://www.alphabet.com",
                "sec_cik": "0001652044",
                "investor_relations": "https://abc.xyz/investor/",
                "sustainability_url": "https://sustainability.google/"
            },
            {
                "name": "Amazon.com Inc.",
                "ticker": "AMZN",
                "exchange": "NASDAQ",
                "website": "https://www.amazon.com",
                "sec_cik": "0001018724",
                "investor_relations": "https://ir.aboutamazon.com/",
                "sustainability_url": "https://sustainability.aboutamazon.com/"
            },
            {
                "name": "Meta Platforms Inc.",
                "ticker": "META",
                "exchange": "NASDAQ",
                "website": "https://www.meta.com",
                "sec_cik": "0001326801",
                "investor_relations": "https://investor.fb.com/",
                "sustainability_url": "https://sustainability.fb.com/"
            },
            {
                "name": "Tesla Inc.",
                "ticker": "TSLA",
                "exchange": "NASDAQ",
                "website": "https://www.tesla.com",
                "sec_cik": "0001318605",
                "investor_relations": "https://ir.tesla.com/",
                "sustainability_url": "https://www.tesla.com/impact"
            },
            {
                "name": "NVIDIA Corporation",
                "ticker": "NVDA",
                "exchange": "NASDAQ",
                "website": "https://www.nvidia.com",
                "sec_cik": "0001045810",
                "investor_relations": "https://investor.nvidia.com/",
                "sustainability_url": "https://www.nvidia.com/en-us/about-nvidia/corporate-responsibility/"
            },
            {
                "name": "Oracle Corporation",
                "ticker": "ORCL",
                "exchange": "NYSE",
                "website": "https://www.oracle.com",
                "sec_cik": "0001341439",
                "investor_relations": "https://investor.oracle.com/",
                "sustainability_url": "https://www.oracle.com/corporate/citizenship/"
            },
            {
                "name": "Salesforce Inc.",
                "ticker": "CRM",
                "exchange": "NYSE",
                "website": "https://www.salesforce.com",
                "sec_cik": "0001108524",
                "investor_relations": "https://investor.salesforce.com/",
                "sustainability_url": "https://www.salesforce.com/company/sustainability/"
            },
            {
                "name": "Adobe Inc.",
                "ticker": "ADBE",
                "exchange": "NASDAQ",
                "website": "https://www.adobe.com",
                "sec_cik": "0000796343",
                "investor_relations": "https://www.adobe.com/investor-relations.html",
                "sustainability_url": "https://www.adobe.com/corporate-responsibility.html"
            }
        ]
    
    async def initialize_companies(self, db: Session) -> List[ITCompany]:
        """Initialize IT companies in the database"""
        companies = []
        
        for company_data in self.it_companies_data:
            # Check if company already exists
            existing_company = db.query(ITCompany).filter(
                ITCompany.ticker == company_data["ticker"]
            ).first()
            
            if not existing_company:
                company = ITCompany(
                    name=company_data["name"],
                    ticker=company_data["ticker"],
                    exchange=company_data["exchange"],
                    website=company_data["website"],
                    sec_cik=company_data["sec_cik"]
                )
                db.add(company)
                companies.append(company)
            else:
                companies.append(existing_company)
        
        db.commit()
        return companies
    
    def get_selenium_driver(self) -> webdriver.Chrome:
        """Get configured Selenium Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        return webdriver.Chrome(options=chrome_options)
    
    async def scrape_sec_filings(self, company: ITCompany, db: Session) -> List[Dict]:
        """Scrape SEC filings for a company"""
        filings = []
        
        try:
            # SEC EDGAR API endpoint
            sec_url = f"https://data.sec.gov/submissions/CIK{company.sec_cik.zfill(10)}.json"
            
            headers = {
                'User-Agent': 'EcoBench ESG Platform contact@ecobench.com',
                'Accept-Encoding': 'gzip, deflate',
                'Host': 'data.sec.gov'
            }
            
            response = requests.get(sec_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                recent_filings = data.get('filings', {}).get('recent', {})
                forms = recent_filings.get('form', [])
                filing_dates = recent_filings.get('filingDate', [])
                accession_numbers = recent_filings.get('accessionNumber', [])
                
                # Filter for relevant forms (10-K, 10-Q, 20-F, etc.)
                relevant_forms = ['10-K', '10-Q', '20-F', '8-K']
                
                for i, form in enumerate(forms):
                    if form in relevant_forms and i < len(filing_dates):
                        filing_date = datetime.strptime(filing_dates[i], '%Y-%m-%d')
                        
                        # Only get filings from last 2 years
                        if filing_date > datetime.now() - timedelta(days=730):
                            accession = accession_numbers[i].replace('-', '')
                            filing_url = f"https://www.sec.gov/Archives/edgar/data/{company.sec_cik}/{accession}/{accession_numbers[i]}-index.htm"
                            
                            filings.append({
                                'report_type': form,
                                'filing_date': filing_date,
                                'url': filing_url,
                                'accession_number': accession_numbers[i]
                            })
            
        except Exception as e:
            logger.error(f"Error scraping SEC filings for {company.name}: {str(e)}")
        
        return filings
    
    async def scrape_sustainability_reports(self, company: ITCompany, db: Session) -> List[Dict]:
        """Scrape sustainability reports from company websites"""
        reports = []
        
        try:
            # Common sustainability report URLs and patterns
            sustainability_urls = [
                f"{company.website}/sustainability",
                f"{company.website}/corporate-responsibility",
                f"{company.website}/esg",
                f"{company.website}/environment",
                f"{company.website}/impact"
            ]
            
            for url in sustainability_urls:
                try:
                    response = requests.get(url, headers=self.session.headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for PDF links containing sustainability keywords
                        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
                        
                        for link in pdf_links:
                            href = link.get('href')
                            text = link.get_text().lower()
                            
                            # Check if it's a sustainability-related document
                            sustainability_keywords = [
                                'sustainability', 'esg', 'corporate responsibility',
                                'environmental', 'social impact', 'climate'
                            ]
                            
                            if any(keyword in text for keyword in sustainability_keywords):
                                full_url = urljoin(url, href)
                                
                                # Extract year from text or URL
                                year_match = re.search(r'20\d{2}', text + href)
                                year = int(year_match.group()) if year_match else datetime.now().year
                                
                                reports.append({
                                    'report_type': 'Sustainability Report',
                                    'filing_date': datetime(year, 12, 31),
                                    'url': full_url,
                                    'title': link.get_text().strip()
                                })
                        
                        break  # If we found the sustainability page, no need to check others
                        
                except requests.RequestException:
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping sustainability reports for {company.name}: {str(e)}")
        
        return reports
    
    async def scrape_investor_relations(self, company: ITCompany, db: Session) -> List[Dict]:
        """Scrape investor relations documents"""
        reports = []
        
        try:
            # Get company data with investor relations URL
            company_data = next(
                (c for c in self.it_companies_data if c["ticker"] == company.ticker), 
                None
            )
            
            if not company_data or "investor_relations" not in company_data:
                return reports
            
            ir_url = company_data["investor_relations"]
            response = requests.get(ir_url, headers=self.session.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for annual reports, proxy statements, etc.
                report_keywords = [
                    'annual report', 'proxy statement', 'form 10-k',
                    'corporate governance', 'esg report'
                ]
                
                links = soup.find_all('a', href=True)
                
                for link in links:
                    text = link.get_text().lower()
                    href = link.get('href')
                    
                    if any(keyword in text for keyword in report_keywords):
                        full_url = urljoin(ir_url, href)
                        
                        # Extract year
                        year_match = re.search(r'20\d{2}', text + href)
                        year = int(year_match.group()) if year_match else datetime.now().year
                        
                        reports.append({
                            'report_type': 'Investor Relations',
                            'filing_date': datetime(year, 12, 31),
                            'url': full_url,
                            'title': link.get_text().strip()
                        })
        
        except Exception as e:
            logger.error(f"Error scraping investor relations for {company.name}: {str(e)}")
        
        return reports
    
    async def store_regulatory_reports(self, company: ITCompany, reports: List[Dict], db: Session):
        """Store scraped reports in the database"""
        
        # First, ensure the company exists in the Organization table
        org = db.query(Organization).filter(Organization.name == company.name).first()
        if not org:
            org = Organization(
                name=company.name,
                ticker=company.ticker,
                sector="Information Technology",
                website=company.website
            )
            db.add(org)
            db.flush()
        
        for report_data in reports:
            # Check if report already exists
            existing_report = db.query(RegulatoryReport).filter(
                RegulatoryReport.organization_id == org.id,
                RegulatoryReport.url == report_data['url']
            ).first()
            
            if not existing_report:
                regulatory_report = RegulatoryReport(
                    organization_id=org.id,
                    report_type=report_data['report_type'],
                    filing_date=report_data['filing_date'],
                    url=report_data['url'],
                    status='pending',
                    last_scraped=datetime.now()
                )
                db.add(regulatory_report)
        
        db.commit()
    
    async def run_scraping_job(self, company_id: int, job_type: str, db: Session) -> Dict:
        """Run a scraping job for a specific company"""
        
        # Create scraping job record
        job = ScrapingJob(
            company_id=company_id,
            job_type=job_type,
            status='running',
            started_at=datetime.now()
        )
        db.add(job)
        db.commit()
        
        try:
            company = db.query(ITCompany).filter(ITCompany.id == company_id).first()
            if not company:
                raise ValueError(f"Company with ID {company_id} not found")
            
            all_reports = []
            
            if job_type == 'sec_filings':
                reports = await self.scrape_sec_filings(company, db)
                all_reports.extend(reports)
            elif job_type == 'sustainability_reports':
                reports = await self.scrape_sustainability_reports(company, db)
                all_reports.extend(reports)
            elif job_type == 'investor_relations':
                reports = await self.scrape_investor_relations(company, db)
                all_reports.extend(reports)
            elif job_type == 'all':
                sec_reports = await self.scrape_sec_filings(company, db)
                sustainability_reports = await self.scrape_sustainability_reports(company, db)
                ir_reports = await self.scrape_investor_relations(company, db)
                all_reports.extend(sec_reports + sustainability_reports + ir_reports)
            
            # Store reports in database
            await self.store_regulatory_reports(company, all_reports, db)
            
            # Update company last scraped time
            company.last_scraped = datetime.now()
            
            # Update job status
            job.status = 'completed'
            job.completed_at = datetime.now()
            job.results_summary = {
                'reports_found': len(all_reports),
                'report_types': list(set(r['report_type'] for r in all_reports))
            }
            
            db.commit()
            
            return {
                'status': 'success',
                'reports_found': len(all_reports),
                'company': company.name
            }
            
        except Exception as e:
            job.status = 'failed'
            job.completed_at = datetime.now()
            job.error_message = str(e)
            db.commit()
            
            logger.error(f"Scraping job failed for company {company_id}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_bulk_scraping(self, db: Session) -> Dict:
        """Run scraping for all active IT companies"""
        
        companies = await self.initialize_companies(db)
        results = []
        
        for company in companies:
            if company.scraping_enabled:
                result = await self.run_scraping_job(company.id, 'all', db)
                results.append({
                    'company': company.name,
                    'result': result
                })
                
                # Add delay between companies to be respectful
                await asyncio.sleep(2)
        
        return {
            'status': 'completed',
            'companies_processed': len(results),
            'results': results
        }


# Singleton instance
scraping_service = ITCompanyScrapingService()
