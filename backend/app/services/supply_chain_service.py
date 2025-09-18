"""
Supply Chain ESG Tracking Service
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from sqlalchemy.orm import Session
from sqlalchemy import Column, BigInteger, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base
from app.models import User, Organization

logger = logging.getLogger(__name__)


class SupplierRiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ESGCategory(Enum):
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"


@dataclass
class SupplierESGScore:
    supplier_id: int
    environmental_score: float
    social_score: float
    governance_score: float
    overall_score: float
    risk_level: SupplierRiskLevel
    last_updated: datetime


class Supplier(Base):
    __tablename__ = "supplier"
    
    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(BigInteger, ForeignKey("organization.id"), nullable=False)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    tier = Column(String(20), nullable=True)  # Tier 1, 2, 3
    annual_spend = Column(Float, nullable=True)
    esg_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)
    certifications = Column(JSONB, nullable=True)
    contact_info = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)


class SupplyChainESGTracker:
    """Advanced supply chain ESG tracking and management"""
    
    def __init__(self):
        self.supplier_scores = {}
        self.risk_assessments = {}
        
    async def assess_supplier_esg(self, supplier_id: int, db: Session) -> SupplierESGScore:
        """Comprehensive ESG assessment of supplier"""
        
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise ValueError("Supplier not found")
        
        # Environmental assessment
        env_score = await self._assess_environmental_impact(supplier)
        
        # Social assessment  
        social_score = await self._assess_social_impact(supplier)
        
        # Governance assessment
        gov_score = await self._assess_governance(supplier)
        
        # Calculate overall score
        overall_score = (env_score * 0.4 + social_score * 0.35 + gov_score * 0.25)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        esg_score = SupplierESGScore(
            supplier_id=supplier_id,
            environmental_score=env_score,
            social_score=social_score,
            governance_score=gov_score,
            overall_score=overall_score,
            risk_level=risk_level,
            last_updated=datetime.now()
        )
        
        # Update supplier record
        supplier.esg_score = overall_score
        supplier.risk_level = risk_level.value
        db.commit()
        
        return esg_score
    
    async def _assess_environmental_impact(self, supplier: Supplier) -> float:
        """Assess environmental impact of supplier"""
        
        score = 50.0  # Base score
        
        # Industry-based scoring
        high_impact_industries = ['mining', 'oil_gas', 'chemicals', 'steel']
        if supplier.industry and supplier.industry.lower() in high_impact_industries:
            score -= 20
        
        # Country-based environmental regulations
        strong_env_countries = ['sweden', 'denmark', 'switzerland', 'germany']
        if supplier.country and supplier.country.lower() in strong_env_countries:
            score += 15
        
        # Certifications boost
        if supplier.certifications:
            env_certs = ['iso14001', 'carbon_neutral', 'renewable_energy']
            for cert in env_certs:
                if cert in supplier.certifications:
                    score += 10
        
        return min(max(score, 0), 100)
    
    async def _assess_social_impact(self, supplier: Supplier) -> float:
        """Assess social impact of supplier"""
        
        score = 50.0  # Base score
        
        # Country-based labor standards
        strong_labor_countries = ['norway', 'sweden', 'denmark', 'netherlands']
        weak_labor_countries = ['bangladesh', 'myanmar', 'uzbekistan']
        
        if supplier.country:
            country_lower = supplier.country.lower()
            if country_lower in strong_labor_countries:
                score += 20
            elif country_lower in weak_labor_countries:
                score -= 25
        
        # Social certifications
        if supplier.certifications:
            social_certs = ['sa8000', 'fair_trade', 'b_corp']
            for cert in social_certs:
                if cert in supplier.certifications:
                    score += 15
        
        return min(max(score, 0), 100)
    
    async def _assess_governance(self, supplier: Supplier) -> float:
        """Assess governance standards of supplier"""
        
        score = 50.0  # Base score
        
        # Country corruption index (simplified)
        low_corruption_countries = ['denmark', 'new_zealand', 'finland', 'singapore']
        high_corruption_countries = ['somalia', 'south_sudan', 'syria']
        
        if supplier.country:
            country_lower = supplier.country.lower()
            if country_lower in low_corruption_countries:
                score += 25
            elif country_lower in high_corruption_countries:
                score -= 30
        
        # Governance certifications
        if supplier.certifications:
            gov_certs = ['iso37001', 'transparency_international']
            for cert in gov_certs:
                if cert in supplier.certifications:
                    score += 15
        
        return min(max(score, 0), 100)
    
    def _determine_risk_level(self, overall_score: float) -> SupplierRiskLevel:
        """Determine risk level based on ESG score"""
        
        if overall_score >= 80:
            return SupplierRiskLevel.LOW
        elif overall_score >= 60:
            return SupplierRiskLevel.MEDIUM
        elif overall_score >= 40:
            return SupplierRiskLevel.HIGH
        else:
            return SupplierRiskLevel.CRITICAL
    
    async def generate_supply_chain_report(self, organization_id: int, db: Session) -> Dict[str, Any]:
        """Generate comprehensive supply chain ESG report"""
        
        suppliers = db.query(Supplier).filter(
            Supplier.organization_id == organization_id,
            Supplier.is_active == True
        ).all()
        
        if not suppliers:
            return {"error": "No suppliers found"}
        
        # Calculate metrics
        total_suppliers = len(suppliers)
        high_risk_suppliers = len([s for s in suppliers if s.risk_level in ['high', 'critical']])
        avg_esg_score = sum(s.esg_score or 0 for s in suppliers) / total_suppliers
        
        # Risk distribution
        risk_distribution = {}
        for supplier in suppliers:
            risk = supplier.risk_level or 'unknown'
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        # Top risks
        top_risks = await self._identify_top_risks(suppliers)
        
        # Improvement recommendations
        recommendations = await self._generate_improvement_recommendations(suppliers)
        
        return {
            "summary": {
                "total_suppliers": total_suppliers,
                "high_risk_suppliers": high_risk_suppliers,
                "average_esg_score": round(avg_esg_score, 2),
                "risk_distribution": risk_distribution
            },
            "top_risks": top_risks,
            "recommendations": recommendations,
            "supplier_details": [
                {
                    "id": s.id,
                    "name": s.name,
                    "country": s.country,
                    "esg_score": s.esg_score,
                    "risk_level": s.risk_level,
                    "annual_spend": s.annual_spend
                }
                for s in suppliers
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    async def _identify_top_risks(self, suppliers: List[Supplier]) -> List[Dict[str, Any]]:
        """Identify top supply chain risks"""
        
        risks = []
        
        # Geographic concentration risk
        country_counts = {}
        for supplier in suppliers:
            if supplier.country:
                country_counts[supplier.country] = country_counts.get(supplier.country, 0) + 1
        
        max_country_concentration = max(country_counts.values()) if country_counts else 0
        if max_country_concentration > len(suppliers) * 0.5:
            risks.append({
                "type": "geographic_concentration",
                "severity": "high",
                "description": f"Over 50% of suppliers concentrated in single country",
                "affected_suppliers": max_country_concentration
            })
        
        # High-risk suppliers
        critical_suppliers = [s for s in suppliers if s.risk_level == 'critical']
        if critical_suppliers:
            risks.append({
                "type": "critical_esg_risk",
                "severity": "critical",
                "description": f"{len(critical_suppliers)} suppliers with critical ESG risks",
                "affected_suppliers": len(critical_suppliers)
            })
        
        return risks
    
    async def _generate_improvement_recommendations(self, suppliers: List[Supplier]) -> List[Dict[str, Any]]:
        """Generate supply chain improvement recommendations"""
        
        recommendations = []
        
        # Diversification recommendation
        country_counts = {}
        for supplier in suppliers:
            if supplier.country:
                country_counts[supplier.country] = country_counts.get(supplier.country, 0) + 1
        
        if len(country_counts) < 3:
            recommendations.append({
                "category": "diversification",
                "priority": "high",
                "title": "Diversify Geographic Supply Base",
                "description": "Reduce geographic concentration risk by sourcing from multiple regions",
                "implementation_steps": [
                    "Identify alternative suppliers in different regions",
                    "Conduct ESG assessments of potential new suppliers",
                    "Gradually shift procurement to reduce concentration"
                ]
            })
        
        # ESG improvement recommendation
        low_score_suppliers = [s for s in suppliers if (s.esg_score or 0) < 60]
        if low_score_suppliers:
            recommendations.append({
                "category": "esg_improvement",
                "priority": "medium",
                "title": "Supplier ESG Development Program",
                "description": f"Improve ESG performance of {len(low_score_suppliers)} underperforming suppliers",
                "implementation_steps": [
                    "Establish supplier ESG requirements",
                    "Provide ESG training and support",
                    "Implement regular ESG audits",
                    "Create incentive programs for ESG improvements"
                ]
            })
        
        return recommendations


# Singleton instance
supply_chain_service = SupplyChainESGTracker()
