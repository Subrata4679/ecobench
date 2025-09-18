import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import (
    Organization, KPIValue, KPIDefinition, Recommendation, 
    Report, Embedding
)
from app.services.llm_client import get_llm_client_instance
from app.services.benchmark import get_benchmark_service
from app.schemas import RecommendationCreate, Recommendation as RecommendationSchema

logger = logging.getLogger(__name__)


class GuidanceService:
    """Service for generating AI-powered sustainability guidance and recommendations"""
    
    def __init__(self):
        self.llm_client = get_llm_client_instance()
        self.benchmark_service = get_benchmark_service()
    
    async def generate_kpi_guidance(self, db: Session, organization_id: int, 
                                   kpi_id: int, period: str = "2023") -> Dict[str, Any]:
        """
        Generate actionable guidance for an organization's KPI performance
        
        Args:
            db: Database session
            organization_id: Target organization
            kpi_id: KPI to analyze
            period: Time period for analysis
        
        Returns:
            Generated guidance and recommendations
        """
        try:
            # Get organization and KPI information
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == kpi_id).first()
            
            if not org or not kpi_def:
                return {"success": False, "error": "Organization or KPI not found"}
            
            # Get organization's performance data
            percentile_data = self.benchmark_service.get_organization_percentile(
                db, organization_id, kpi_id, period
            )
            
            if "error" in percentile_data:
                return {"success": False, "error": percentile_data["error"]}
            
            # Get top performers for learning opportunities
            top_performers = self.benchmark_service.get_top_performers(
                db, kpi_id, period, limit=3
            )
            
            # Get relevant evidence from reports
            evidence_snippets = await self._get_evidence_snippets(
                db, organization_id, kpi_def.code, limit=3
            )
            
            # Prepare context for LLM
            context = {
                "org": org.name,
                "kpi": {
                    "code": kpi_def.code,
                    "name": kpi_def.name,
                    "unit": kpi_def.unit,
                    "value": percentile_data["organization_value"],
                    "percentile": percentile_data["percentile"],
                    "rank": percentile_data["rank"],
                    "total_peers": percentile_data["total_peers"],
                    "is_higher_better": percentile_data["is_higher_better"]
                },
                "leaders": [
                    {
                        "org": perf["organization_name"],
                        "value": perf["value"],
                        "sector": perf["sector"],
                        "snippet": f"Leading performer in {perf['sector']} sector"
                    }
                    for perf in top_performers
                ],
                "benchmark_stats": percentile_data["benchmark_stats"],
                "evidence": evidence_snippets,
                "period": period
            }
            
            # Generate guidance using LLM
            guidance = await self.llm_client.generate_guidance(context)
            
            # Enhance guidance with additional context
            enhanced_guidance = self._enhance_guidance(guidance, context)
            
            return {
                "success": True,
                "organization_id": organization_id,
                "kpi_id": kpi_id,
                "period": period,
                "guidance": enhanced_guidance,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Guidance generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_evidence_snippets(self, db: Session, organization_id: int, 
                                    kpi_code: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get relevant evidence snippets from organization's reports"""
        try:
            # Get recent reports for the organization
            reports = db.query(Report).filter(
                Report.organization_id == organization_id
            ).order_by(Report.year.desc()).limit(3).all()
            
            evidence = []
            
            for report in reports:
                # Get embeddings that might contain relevant KPI information
                embeddings = db.query(Embedding).filter(
                    Embedding.report_id == report.id
                ).limit(5).all()  # Limit per report
                
                for embedding in embeddings:
                    # Simple keyword matching for relevance
                    chunk_lower = embedding.chunk_text.lower()
                    kpi_keywords = kpi_code.lower().replace("_", " ").split()
                    
                    if any(keyword in chunk_lower for keyword in kpi_keywords):
                        evidence.append({
                            "text": embedding.chunk_text[:300] + "..." if len(embedding.chunk_text) > 300 else embedding.chunk_text,
                            "report_title": report.title,
                            "year": report.year,
                            "report_id": report.id,
                            "relevance_score": sum(1 for kw in kpi_keywords if kw in chunk_lower)
                        })
            
            # Sort by relevance and return top results
            evidence.sort(key=lambda x: x["relevance_score"], reverse=True)
            return evidence[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get evidence snippets: {e}")
            return []
    
    def _enhance_guidance(self, guidance: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance LLM-generated guidance with additional context and validation"""
        enhanced = guidance.copy()
        
        # Add performance context
        kpi_info = context["kpi"]
        percentile = kpi_info["percentile"]
        
        # Categorize performance level
        if percentile >= 75:
            performance_level = "excellent"
            priority = "maintain"
        elif percentile >= 50:
            performance_level = "good"
            priority = "improve"
        elif percentile >= 25:
            performance_level = "below_average"
            priority = "urgent"
        else:
            performance_level = "poor"
            priority = "critical"
        
        enhanced["performance_analysis"] = {
            "level": performance_level,
            "priority": priority,
            "percentile": percentile,
            "benchmark_position": f"{kpi_info['rank']} of {kpi_info['total_peers']}"
        }
        
        # Add industry context
        if context.get("leaders"):
            leader_values = [leader["value"] for leader in context["leaders"]]
            if leader_values:
                best_in_class = min(leader_values) if not kpi_info["is_higher_better"] else max(leader_values)
                gap_to_leader = abs(kpi_info["value"] - best_in_class)
                
                enhanced["improvement_potential"] = {
                    "best_in_class_value": best_in_class,
                    "current_gap": gap_to_leader,
                    "improvement_percentage": (gap_to_leader / kpi_info["value"]) * 100 if kpi_info["value"] > 0 else 0
                }
        
        # Validate and enhance actions
        if "actions" in enhanced and isinstance(enhanced["actions"], list):
            for action in enhanced["actions"]:
                # Add default timeframe if missing
                if "timeframe" not in action:
                    if action.get("effort") == "low":
                        action["timeframe"] = "1-3 months"
                    elif action.get("effort") == "medium":
                        action["timeframe"] = "3-6 months"
                    else:
                        action["timeframe"] = "6-12 months"
                
                # Add default owner if missing
                if "owner" not in action:
                    action["owner"] = "Sustainability Team"
        
        return enhanced
    
    async def save_recommendation(self, db: Session, recommendation_data: Dict[str, Any]) -> Recommendation:
        """Save a generated recommendation to the database"""
        try:
            recommendation = Recommendation(
                organization_id=recommendation_data["organization_id"],
                kpi_id=recommendation_data.get("kpi_id"),
                title=recommendation_data["title"],
                rationale=recommendation_data.get("rationale"),
                actions=recommendation_data.get("actions", []),
                confidence=recommendation_data.get("confidence"),
                sources=recommendation_data.get("sources", [])
            )
            
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            
            logger.info(f"Saved recommendation {recommendation.id} for organization {recommendation.organization_id}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to save recommendation: {e}")
            raise
    
    async def generate_comprehensive_guidance(self, db: Session, organization_id: int, 
                                            period: str = "2023") -> Dict[str, Any]:
        """
        Generate comprehensive guidance across all KPIs for an organization
        
        Args:
            db: Database session
            organization_id: Target organization
            period: Time period for analysis
        
        Returns:
            Comprehensive guidance report
        """
        try:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                return {"success": False, "error": "Organization not found"}
            
            # Get all KPIs with data for this organization
            kpi_values = db.query(KPIValue, KPIDefinition).join(
                KPIDefinition, KPIValue.kpi_id == KPIDefinition.id
            ).filter(
                KPIValue.organization_id == organization_id,
                KPIValue.year == int(period) if period.isdigit() else True
            ).all()
            
            if not kpi_values:
                return {"success": False, "error": "No KPI data found for organization"}
            
            comprehensive_report = {
                "organization": {
                    "id": org.id,
                    "name": org.name,
                    "sector": org.sector,
                    "country": org.country
                },
                "period": period,
                "kpi_guidance": {},
                "priority_actions": [],
                "overall_performance": {},
                "generated_at": datetime.now().isoformat()
            }
            
            # Generate guidance for each KPI
            for kpi_value, kpi_def in kpi_values:
                kpi_guidance = await self.generate_kpi_guidance(
                    db, organization_id, kpi_def.id, period
                )
                
                if kpi_guidance["success"]:
                    comprehensive_report["kpi_guidance"][kpi_def.code] = kpi_guidance["guidance"]
                    
                    # Extract high-priority actions
                    guidance = kpi_guidance["guidance"]
                    if "actions" in guidance:
                        for action in guidance["actions"]:
                            if action.get("effort") in ["high", "medium"]:
                                action["kpi_code"] = kpi_def.code
                                action["kpi_name"] = kpi_def.name
                                comprehensive_report["priority_actions"].append(action)
            
            # Calculate overall performance summary
            percentiles = []
            for kpi_value, kpi_def in kpi_values:
                perf_data = self.benchmark_service.get_organization_percentile(
                    db, organization_id, kpi_def.id, period
                )
                if "percentile" in perf_data:
                    percentiles.append(perf_data["percentile"])
            
            if percentiles:
                comprehensive_report["overall_performance"] = {
                    "average_percentile": sum(percentiles) / len(percentiles),
                    "kpis_analyzed": len(percentiles),
                    "top_quartile_kpis": sum(1 for p in percentiles if p >= 75),
                    "bottom_quartile_kpis": sum(1 for p in percentiles if p <= 25)
                }
            
            return {
                "success": True,
                "comprehensive_report": comprehensive_report
            }
            
        except Exception as e:
            logger.error(f"Comprehensive guidance generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_organization_recommendations(self, db: Session, organization_id: int, 
                                       limit: int = 10) -> List[Recommendation]:
        """Get existing recommendations for an organization"""
        return db.query(Recommendation).filter(
            Recommendation.organization_id == organization_id
        ).order_by(Recommendation.created_at.desc()).limit(limit).all()
    
    async def update_recommendation_status(self, db: Session, recommendation_id: int, 
                                          status: str, notes: str = None) -> bool:
        """Update the status of a recommendation (for tracking implementation)"""
        try:
            recommendation = db.query(Recommendation).filter(
                Recommendation.id == recommendation_id
            ).first()
            
            if not recommendation:
                return False
            
            # Add status tracking to sources field
            if not recommendation.sources:
                recommendation.sources = []
            
            recommendation.sources.append({
                "type": "status_update",
                "status": status,
                "notes": notes,
                "updated_at": datetime.now().isoformat()
            })
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update recommendation status: {e}")
            return False


# Global service instance
_guidance_service = None

def get_guidance_service() -> GuidanceService:
    """Get singleton guidance service instance"""
    global _guidance_service
    if _guidance_service is None:
        _guidance_service = GuidanceService()
    return _guidance_service
