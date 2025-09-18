"""
Advanced Analytics API Router
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
from pydantic import BaseModel

from app.database import get_db
from app.models import User, UserESGData
from app.routers.auth import get_current_user
from app.services.analytics_service import analytics_service
from app.services.monitoring_service import monitoring_service
from app.services.supply_chain_service import supply_chain_service
from app.services.risk_assessment_service import risk_assessment_service

logger = logging.getLogger(__name__)

router = APIRouter()


class PredictiveInsightsResponse(BaseModel):
    predictions: Dict
    trends: Dict
    risks: Dict
    optimizations: List[Dict]
    scenarios: Dict
    confidence_scores: Dict
    generated_at: str


class RiskAssessmentResponse(BaseModel):
    risk_profile: Dict
    risks_by_category: Dict
    risk_matrix: Dict
    scenarios: Dict
    mitigation_roadmap: Dict
    assessment_date: str


class MonitoringDashboardResponse(BaseModel):
    monitoring_status: str
    active_alerts: int
    monitoring_rules: int
    recent_alerts: List[Dict]
    alert_statistics: Dict
    system_health: Dict


@router.get("/predictive-insights", response_model=PredictiveInsightsResponse)
async def get_predictive_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered predictive insights for ESG performance"""
    
    try:
        insights = await analytics_service.generate_predictive_insights(current_user.id, db)
        
        if "error" in insights:
            raise HTTPException(status_code=400, detail=insights["error"])
        
        return PredictiveInsightsResponse(**insights)
    
    except Exception as e:
        logger.error(f"Error generating predictive insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


@router.get("/industry-comparison")
async def get_industry_comparison(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed industry comparison analysis"""
    
    try:
        comparison = await analytics_service.generate_industry_comparison(current_user.id, db)
        
        if "error" in comparison:
            raise HTTPException(status_code=400, detail=comparison["error"])
        
        return comparison
    
    except Exception as e:
        logger.error(f"Error generating industry comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate comparison: {str(e)}")


@router.get("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive ESG risk assessment"""
    
    try:
        assessment = await risk_assessment_service.comprehensive_risk_assessment(current_user.id, db)
        
        if "error" in assessment:
            raise HTTPException(status_code=400, detail=assessment["error"])
        
        return RiskAssessmentResponse(**assessment)
    
    except Exception as e:
        logger.error(f"Error generating risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate assessment: {str(e)}")


@router.get("/monitoring-dashboard", response_model=MonitoringDashboardResponse)
async def get_monitoring_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time monitoring dashboard"""
    
    try:
        dashboard = await monitoring_service.get_monitoring_dashboard()
        return MonitoringDashboardResponse(**dashboard)
    
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


@router.post("/start-monitoring")
async def start_monitoring(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Start real-time ESG monitoring"""
    
    try:
        background_tasks.add_task(monitoring_service.start_monitoring)
        
        return {
            "message": "Real-time ESG monitoring started",
            "status": "active"
        }
    
    except Exception as e:
        logger.error(f"Error starting monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/stop-monitoring")
async def stop_monitoring(
    current_user: User = Depends(get_current_user)
):
    """Stop real-time ESG monitoring"""
    
    try:
        await monitoring_service.stop_monitoring()
        
        return {
            "message": "Real-time ESG monitoring stopped",
            "status": "inactive"
        }
    
    except Exception as e:
        logger.error(f"Error stopping monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@router.get("/supply-chain-report")
async def get_supply_chain_report(
    organization_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supply chain ESG report"""
    
    try:
        # Use user's organization if not specified
        if not organization_id:
            # This would need to be implemented based on user-organization relationship
            organization_id = 1  # Default for demo
        
        report = await supply_chain_service.generate_supply_chain_report(organization_id, db)
        
        if "error" in report:
            raise HTTPException(status_code=400, detail=report["error"])
        
        return report
    
    except Exception as e:
        logger.error(f"Error generating supply chain report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/performance-trends")
async def get_performance_trends(
    years: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ESG performance trends over time"""
    
    try:
        # Get user's historical data
        historical_data = db.query(UserESGData).filter(
            UserESGData.user_id == current_user.id
        ).order_by(UserESGData.year.desc()).limit(years).all()
        
        if not historical_data:
            raise HTTPException(status_code=404, detail="No historical data found")
        
        # Process trends
        trends = {}
        metrics = [
            'scope1_emissions', 'scope2_emissions', 'scope3_emissions',
            'water_consumption', 'waste_generated', 'energy_consumption',
            'renewable_energy_percentage'
        ]
        
        for metric in metrics:
            values = []
            years_list = []
            
            for data in reversed(historical_data):  # Chronological order
                value = getattr(data, metric)
                if value is not None:
                    values.append(value)
                    years_list.append(data.year)
            
            if len(values) >= 2:
                # Calculate trend
                import numpy as np
                slope = np.polyfit(years_list, values, 1)[0]
                
                trends[metric] = {
                    "values": values,
                    "years": years_list,
                    "trend_direction": "increasing" if slope > 0 else "decreasing",
                    "trend_strength": abs(slope),
                    "latest_value": values[-1],
                    "change_from_first": ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                }
        
        return {
            "trends": trends,
            "data_points": len(historical_data),
            "years_covered": years,
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting performance trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


@router.get("/carbon-footprint-analysis")
async def get_carbon_footprint_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed carbon footprint analysis"""
    
    try:
        user_data = db.query(UserESGData).filter(
            UserESGData.user_id == current_user.id
        ).order_by(UserESGData.year.desc()).first()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="No ESG data found")
        
        scope1 = user_data.scope1_emissions or 0
        scope2 = user_data.scope2_emissions or 0
        scope3 = user_data.scope3_emissions or 0
        total = scope1 + scope2 + scope3
        
        analysis = {
            "total_emissions": total,
            "scope_breakdown": {
                "scope1": {
                    "value": scope1,
                    "percentage": (scope1 / total * 100) if total > 0 else 0,
                    "description": "Direct emissions from owned/controlled sources"
                },
                "scope2": {
                    "value": scope2,
                    "percentage": (scope2 / total * 100) if total > 0 else 0,
                    "description": "Indirect emissions from purchased electricity"
                },
                "scope3": {
                    "value": scope3,
                    "percentage": (scope3 / total * 100) if total > 0 else 0,
                    "description": "All other indirect emissions in value chain"
                }
            },
            "intensity_metrics": {},
            "reduction_targets": {},
            "offset_requirements": {}
        }
        
        # Calculate intensity metrics
        if user_data.revenue:
            analysis["intensity_metrics"]["emissions_per_revenue"] = total / (user_data.revenue / 1000000)
        
        if user_data.employee_count:
            analysis["intensity_metrics"]["emissions_per_employee"] = total / user_data.employee_count
        
        # Suggest reduction targets
        analysis["reduction_targets"] = {
            "science_based_target": total * 0.5,  # 50% reduction
            "net_zero_target": 0,
            "interim_2030_target": total * 0.7,  # 30% reduction by 2030
            "recommended_annual_reduction": total * 0.05  # 5% per year
        }
        
        # Calculate offset requirements for net zero
        renewable_pct = user_data.renewable_energy_percentage or 0
        potential_reduction = total * 0.6  # Assume 60% can be reduced through efficiency
        
        analysis["offset_requirements"] = {
            "residual_emissions": total - potential_reduction,
            "estimated_offset_cost": (total - potential_reduction) * 25,  # $25/tCO2e
            "offset_projects_needed": max(1, int((total - potential_reduction) / 1000))
        }
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error analyzing carbon footprint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze footprint: {str(e)}")


@router.get("/sustainability-score")
async def get_sustainability_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate comprehensive sustainability score"""
    
    try:
        user_data = db.query(UserESGData).filter(
            UserESGData.user_id == current_user.id
        ).order_by(UserESGData.year.desc()).first()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="No ESG data found")
        
        # Calculate scores for different categories (0-100)
        scores = {}
        
        # Environmental score
        env_factors = []
        
        # Emissions score (lower is better)
        total_emissions = (user_data.scope1_emissions or 0) + (user_data.scope2_emissions or 0) + (user_data.scope3_emissions or 0)
        if total_emissions > 0:
            emissions_score = max(0, 100 - (total_emissions / 1000))  # Rough scoring
            env_factors.append(emissions_score)
        
        # Renewable energy score
        renewable_pct = user_data.renewable_energy_percentage or 0
        env_factors.append(renewable_pct)
        
        # Water efficiency score (simplified)
        water_consumption = user_data.water_consumption or 0
        if user_data.employee_count and user_data.employee_count > 0:
            water_per_employee = water_consumption / user_data.employee_count
            water_score = max(0, 100 - water_per_employee)  # Simplified
            env_factors.append(water_score)
        
        scores["environmental"] = sum(env_factors) / len(env_factors) if env_factors else 0
        
        # Social score (simplified - would need more data)
        scores["social"] = 75  # Default score
        
        # Governance score (simplified - would need more data)
        scores["governance"] = 70  # Default score
        
        # Overall sustainability score
        overall_score = (scores["environmental"] * 0.5 + 
                        scores["social"] * 0.3 + 
                        scores["governance"] * 0.2)
        
        # Determine rating
        if overall_score >= 90:
            rating = "A+"
        elif overall_score >= 80:
            rating = "A"
        elif overall_score >= 70:
            rating = "B"
        elif overall_score >= 60:
            rating = "C"
        else:
            rating = "D"
        
        return {
            "overall_score": round(overall_score, 1),
            "rating": rating,
            "category_scores": {
                "environmental": round(scores["environmental"], 1),
                "social": round(scores["social"], 1),
                "governance": round(scores["governance"], 1)
            },
            "score_breakdown": {
                "strengths": [],
                "improvement_areas": [],
                "recommendations": []
            },
            "calculated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error calculating sustainability score: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate score: {str(e)}")


from datetime import datetime
