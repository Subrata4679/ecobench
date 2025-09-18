#!/usr/bin/env python3
"""
Sample Data Generation Script for EcoBench

This script generates realistic sample data for development and testing purposes.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json
import random
from typing import List, Dict, Any

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session, init_db
from app.models import (
    Organization, User, Report, KPIDefinition, KPIValue, 
    IngestionJob, PeerGroup, BenchmarkSnapshot, Recommendation, AuditLog
)
from app.utils.logging import get_logger

logger = get_logger("sample_data")

# Sample data configurations
SAMPLE_ORGANIZATIONS = [
    {
        "name": "TechCorp Industries",
        "industry": "Technology",
        "size": "Large",
        "description": "Leading technology company focused on sustainable innovation",
        "website": "https://techcorp.example.com",
        "headquarters": "San Francisco, CA"
    },
    {
        "name": "GreenEnergy Solutions",
        "industry": "Energy",
        "size": "Medium",
        "description": "Renewable energy provider with focus on solar and wind",
        "website": "https://greenenergy.example.com",
        "headquarters": "Austin, TX"
    },
    {
        "name": "EcoManufacturing Co",
        "industry": "Manufacturing",
        "size": "Large",
        "description": "Sustainable manufacturing with circular economy principles",
        "website": "https://ecomanuf.example.com",
        "headquarters": "Detroit, MI"
    },
    {
        "name": "FinanceForward",
        "industry": "Financial Services",
        "size": "Large",
        "description": "ESG-focused financial services and sustainable investing",
        "website": "https://financeforward.example.com",
        "headquarters": "New York, NY"
    },
    {
        "name": "RetailGreen",
        "industry": "Retail",
        "size": "Medium",
        "description": "Sustainable retail chain with zero-waste initiatives",
        "website": "https://retailgreen.example.com",
        "headquarters": "Seattle, WA"
    }
]

SAMPLE_USERS = [
    {
        "email": "admin@ecobench.com",
        "full_name": "System Administrator",
        "role": "admin",
        "is_active": True
    },
    {
        "email": "sarah.johnson@techcorp.example.com",
        "full_name": "Sarah Johnson",
        "role": "manager",
        "is_active": True
    },
    {
        "email": "mike.chen@greenenergy.example.com",
        "full_name": "Mike Chen",
        "role": "analyst",
        "is_active": True
    },
    {
        "email": "lisa.rodriguez@ecomanuf.example.com",
        "full_name": "Lisa Rodriguez",
        "role": "manager",
        "is_active": True
    },
    {
        "email": "david.kim@financeforward.example.com",
        "full_name": "David Kim",
        "role": "analyst",
        "is_active": True
    }
]

SAMPLE_KPI_DEFINITIONS = [
    {
        "name": "Carbon Emissions (Scope 1)",
        "description": "Direct greenhouse gas emissions from owned or controlled sources",
        "category": "Environmental",
        "unit": "tCO2e",
        "data_type": "numeric"
    },
    {
        "name": "Carbon Emissions (Scope 2)",
        "description": "Indirect greenhouse gas emissions from purchased energy",
        "category": "Environmental",
        "unit": "tCO2e",
        "data_type": "numeric"
    },
    {
        "name": "Water Consumption",
        "description": "Total water consumption across all operations",
        "category": "Environmental",
        "unit": "m³",
        "data_type": "numeric"
    },
    {
        "name": "Waste Generated",
        "description": "Total waste generated including hazardous and non-hazardous",
        "category": "Environmental",
        "unit": "tonnes",
        "data_type": "numeric"
    },
    {
        "name": "Renewable Energy Usage",
        "description": "Percentage of energy from renewable sources",
        "category": "Environmental",
        "unit": "%",
        "data_type": "numeric"
    },
    {
        "name": "Employee Turnover Rate",
        "description": "Annual employee turnover rate",
        "category": "Social",
        "unit": "%",
        "data_type": "numeric"
    },
    {
        "name": "Gender Diversity (Board)",
        "description": "Percentage of women on board of directors",
        "category": "Social",
        "unit": "%",
        "data_type": "numeric"
    },
    {
        "name": "Training Hours per Employee",
        "description": "Average training hours per employee per year",
        "category": "Social",
        "unit": "hours",
        "data_type": "numeric"
    },
    {
        "name": "Board Independence",
        "description": "Percentage of independent board members",
        "category": "Governance",
        "unit": "%",
        "data_type": "numeric"
    },
    {
        "name": "Ethics Training Completion",
        "description": "Percentage of employees completing ethics training",
        "category": "Governance",
        "unit": "%",
        "data_type": "numeric"
    }
]

SAMPLE_REPORTS = [
    {
        "title": "2023 Sustainability Report",
        "file_type": "pdf",
        "file_size": 2048000,
        "description": "Annual sustainability report covering ESG performance"
    },
    {
        "title": "Q4 2023 ESG Metrics",
        "file_type": "pdf",
        "file_size": 1024000,
        "description": "Quarterly ESG metrics and performance indicators"
    },
    {
        "title": "Carbon Footprint Assessment 2023",
        "file_type": "pdf",
        "file_size": 1536000,
        "description": "Comprehensive carbon footprint analysis"
    }
]


class SampleDataGenerator:
    """Generate sample data for EcoBench development and testing."""
    
    def __init__(self):
        self.organizations: List[Organization] = []
        self.users: List[User] = []
        self.kpi_definitions: List[KPIDefinition] = []
        self.reports: List[Report] = []
    
    async def generate_all_data(self, session: AsyncSession):
        """Generate all sample data."""
        logger.info("Starting sample data generation")
        
        try:
            await self.create_organizations(session)
            await self.create_users(session)
            await self.create_kpi_definitions(session)
            await self.create_reports(session)
            await self.create_kpi_values(session)
            await self.create_ingestion_jobs(session)
            await self.create_peer_groups(session)
            await self.create_benchmark_snapshots(session)
            await self.create_recommendations(session)
            await self.create_audit_logs(session)
            
            await session.commit()
            logger.info("Sample data generation completed successfully")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error generating sample data: {e}")
            raise
    
    async def create_organizations(self, session: AsyncSession):
        """Create sample organizations."""
        logger.info("Creating sample organizations")
        
        for org_data in SAMPLE_ORGANIZATIONS:
            org = Organization(**org_data)
            session.add(org)
            self.organizations.append(org)
        
        await session.flush()  # Get IDs
    
    async def create_users(self, session: AsyncSession):
        """Create sample users."""
        logger.info("Creating sample users")
        
        for i, user_data in enumerate(SAMPLE_USERS):
            user = User(
                **user_data,
                organization_id=self.organizations[i % len(self.organizations)].id if i > 0 else None,
                hashed_password="$2b$12$dummy.hash.for.sample.data"  # Mock hash
            )
            session.add(user)
            self.users.append(user)
        
        await session.flush()
    
    async def create_kpi_definitions(self, session: AsyncSession):
        """Create sample KPI definitions."""
        logger.info("Creating sample KPI definitions")
        
        for kpi_data in SAMPLE_KPI_DEFINITIONS:
            kpi = KPIDefinition(**kpi_data)
            session.add(kpi)
            self.kpi_definitions.append(kpi)
        
        await session.flush()
    
    async def create_reports(self, session: AsyncSession):
        """Create sample reports."""
        logger.info("Creating sample reports")
        
        for org in self.organizations:
            for report_data in SAMPLE_REPORTS:
                report = Report(
                    **report_data,
                    organization_id=org.id,
                    file_path=f"/uploads/{org.name.lower().replace(' ', '_')}_{report_data['title'].lower().replace(' ', '_')}.pdf",
                    uploaded_by=self.users[1].id,  # Non-admin user
                    upload_date=datetime.utcnow() - timedelta(days=random.randint(1, 365))
                )
                session.add(report)
                self.reports.append(report)
        
        await session.flush()
    
    async def create_kpi_values(self, session: AsyncSession):
        """Create sample KPI values."""
        logger.info("Creating sample KPI values")
        
        for org in self.organizations:
            for kpi_def in self.kpi_definitions:
                # Generate values for the last 3 years
                for year in [2021, 2022, 2023]:
                    value = self._generate_kpi_value(kpi_def.name, org.industry)
                    
                    kpi_value = KPIValue(
                        kpi_definition_id=kpi_def.id,
                        organization_id=org.id,
                        value=str(value),
                        reporting_period=f"{year}-12-31",
                        data_source="Sample Data",
                        confidence_score=random.uniform(0.7, 0.95),
                        created_by=self.users[1].id
                    )
                    session.add(kpi_value)
        
        await session.flush()
    
    async def create_ingestion_jobs(self, session: AsyncSession):
        """Create sample ingestion jobs."""
        logger.info("Creating sample ingestion jobs")
        
        job_types = ["pdf_processing", "kpi_extraction", "embedding_generation"]
        statuses = ["completed", "completed", "completed", "failed", "running"]
        
        for report in self.reports[:10]:  # Create jobs for first 10 reports
            job = IngestionJob(
                report_id=report.id,
                job_type=random.choice(job_types),
                status=random.choice(statuses),
                started_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                completed_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 60)) if random.choice([True, False]) else None,
                result={"processed_pages": random.randint(10, 100), "extracted_kpis": random.randint(5, 20)},
                created_by=self.users[0].id
            )
            session.add(job)
        
        await session.flush()
    
    async def create_peer_groups(self, session: AsyncSession):
        """Create sample peer groups."""
        logger.info("Creating sample peer groups")
        
        # Group by industry
        industries = {}
        for org in self.organizations:
            if org.industry not in industries:
                industries[org.industry] = []
            industries[org.industry].append(org.id)
        
        for industry, org_ids in industries.items():
            if len(org_ids) > 1:  # Only create peer group if multiple orgs
                peer_group = PeerGroup(
                    name=f"{industry} Peer Group",
                    description=f"Peer group for organizations in the {industry} industry",
                    criteria={"industry": industry},
                    organization_ids=org_ids,
                    created_by=self.users[0].id
                )
                session.add(peer_group)
        
        await session.flush()
    
    async def create_benchmark_snapshots(self, session: AsyncSession):
        """Create sample benchmark snapshots."""
        logger.info("Creating sample benchmark snapshots")
        
        for org in self.organizations:
            snapshot = BenchmarkSnapshot(
                organization_id=org.id,
                benchmark_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                metrics={
                    "esg_score": random.uniform(60, 95),
                    "environmental_score": random.uniform(50, 90),
                    "social_score": random.uniform(60, 95),
                    "governance_score": random.uniform(70, 100),
                    "peer_rank": random.randint(1, 10),
                    "industry_percentile": random.uniform(40, 95)
                },
                peer_comparison={
                    "better_than": random.uniform(40, 80),
                    "similar_to": random.uniform(10, 30),
                    "worse_than": random.uniform(5, 20)
                },
                created_by=self.users[0].id
            )
            session.add(snapshot)
        
        await session.flush()
    
    async def create_recommendations(self, session: AsyncSession):
        """Create sample recommendations."""
        logger.info("Creating sample recommendations")
        
        recommendation_templates = [
            {
                "title": "Improve Carbon Emissions Reporting",
                "description": "Enhance carbon emissions data collection and reporting processes",
                "category": "Environmental",
                "priority": "high"
            },
            {
                "title": "Increase Board Gender Diversity",
                "description": "Work towards achieving better gender balance on the board of directors",
                "category": "Social",
                "priority": "medium"
            },
            {
                "title": "Implement ESG Training Program",
                "description": "Develop comprehensive ESG training for all employees",
                "category": "Governance",
                "priority": "medium"
            },
            {
                "title": "Set Science-Based Targets",
                "description": "Establish science-based targets for carbon emission reductions",
                "category": "Environmental",
                "priority": "high"
            }
        ]
        
        for org in self.organizations:
            for template in recommendation_templates:
                recommendation = Recommendation(
                    organization_id=org.id,
                    **template,
                    implementation_effort="medium",
                    expected_impact="high",
                    status=random.choice(["pending", "in_progress", "completed"]),
                    generated_by="ai",
                    created_by=self.users[0].id
                )
                session.add(recommendation)
        
        await session.flush()
    
    async def create_audit_logs(self, session: AsyncSession):
        """Create sample audit logs."""
        logger.info("Creating sample audit logs")
        
        actions = ["create", "update", "delete", "view"]
        resources = ["organization", "report", "kpi_value", "recommendation"]
        
        for _ in range(50):  # Create 50 audit log entries
            audit_log = AuditLog(
                user_id=random.choice(self.users).id,
                action=random.choice(actions),
                resource_type=random.choice(resources),
                resource_id=random.randint(1, 100),
                details={"sample": "audit log entry"},
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (Sample User Agent)",
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720))
            )
            session.add(audit_log)
        
        await session.flush()
    
    def _generate_kpi_value(self, kpi_name: str, industry: str) -> float:
        """Generate realistic KPI values based on KPI type and industry."""
        base_values = {
            "Carbon Emissions (Scope 1)": {"Technology": 500, "Energy": 2000, "Manufacturing": 5000, "Financial Services": 200, "Retail": 800},
            "Carbon Emissions (Scope 2)": {"Technology": 300, "Energy": 1000, "Manufacturing": 3000, "Financial Services": 150, "Retail": 500},
            "Water Consumption": {"Technology": 10000, "Energy": 50000, "Manufacturing": 100000, "Financial Services": 5000, "Retail": 20000},
            "Waste Generated": {"Technology": 100, "Energy": 500, "Manufacturing": 2000, "Financial Services": 50, "Retail": 800},
            "Renewable Energy Usage": {"Technology": 60, "Energy": 80, "Manufacturing": 30, "Financial Services": 40, "Retail": 50},
            "Employee Turnover Rate": {"Technology": 15, "Energy": 8, "Manufacturing": 12, "Financial Services": 10, "Retail": 20},
            "Gender Diversity (Board)": {"Technology": 35, "Energy": 25, "Manufacturing": 20, "Financial Services": 30, "Retail": 40},
            "Training Hours per Employee": {"Technology": 40, "Energy": 30, "Manufacturing": 25, "Financial Services": 35, "Retail": 20},
            "Board Independence": {"Technology": 75, "Energy": 70, "Manufacturing": 65, "Financial Services": 80, "Retail": 70},
            "Ethics Training Completion": {"Technology": 95, "Energy": 90, "Manufacturing": 85, "Financial Services": 98, "Retail": 88}
        }
        
        base_value = base_values.get(kpi_name, {}).get(industry, 50)
        # Add some random variation (±20%)
        variation = random.uniform(0.8, 1.2)
        return round(base_value * variation, 2)


async def main():
    """Main function to generate sample data."""
    try:
        # Initialize database
        await init_db()
        
        # Generate sample data
        generator = SampleDataGenerator()
        
        async for session in get_async_session():
            await generator.generate_all_data(session)
            break
        
        print("✅ Sample data generation completed successfully!")
        print("\n📊 Generated data includes:")
        print(f"  • {len(SAMPLE_ORGANIZATIONS)} Organizations")
        print(f"  • {len(SAMPLE_USERS)} Users")
        print(f"  • {len(SAMPLE_KPI_DEFINITIONS)} KPI Definitions")
        print(f"  • {len(SAMPLE_ORGANIZATIONS) * len(SAMPLE_REPORTS)} Reports")
        print(f"  • {len(SAMPLE_ORGANIZATIONS) * len(SAMPLE_KPI_DEFINITIONS) * 3} KPI Values (3 years)")
        print("  • Ingestion Jobs, Peer Groups, Benchmarks, Recommendations, and Audit Logs")
        
    except Exception as e:
        logger.error(f"Failed to generate sample data: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
