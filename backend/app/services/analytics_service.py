"""
Advanced Analytics Service with Predictive Modeling for ESG Data
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models import (
    UserESGData, Organization, KPIValue, KPIDefinition, 
    RegulatoryReport, BenchmarkSnapshot
)

logger = logging.getLogger(__name__)


class ESGAnalyticsService:
    """Advanced analytics service for ESG data with predictive modeling"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
    async def generate_predictive_insights(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Generate comprehensive predictive insights for a user"""
        
        # Get user's historical data
        user_data = db.query(UserESGData).filter(
            UserESGData.user_id == user_id
        ).order_by(UserESGData.year.asc()).all()
        
        if len(user_data) < 2:
            return {
                "error": "Insufficient historical data for predictions",
                "message": "Need at least 2 years of data for trend analysis"
            }
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([{
            'year': data.year,
            'scope1_emissions': data.scope1_emissions or 0,
            'scope2_emissions': data.scope2_emissions or 0,
            'scope3_emissions': data.scope3_emissions or 0,
            'water_consumption': data.water_consumption or 0,
            'waste_generated': data.waste_generated or 0,
            'energy_consumption': data.energy_consumption or 0,
            'renewable_energy_percentage': data.renewable_energy_percentage or 0,
            'employee_count': data.employee_count or 0,
            'revenue': data.revenue or 0
        } for data in user_data])
        
        # Generate predictions
        predictions = await self._generate_metric_predictions(df)
        
        # Calculate trends
        trends = await self._calculate_trends(df)
        
        # Risk assessment
        risks = await self._assess_esg_risks(df, db)
        
        # Optimization recommendations
        optimizations = await self._generate_optimization_recommendations(df, db)
        
        # Scenario analysis
        scenarios = await self._perform_scenario_analysis(df)
        
        return {
            "predictions": predictions,
            "trends": trends,
            "risks": risks,
            "optimizations": optimizations,
            "scenarios": scenarios,
            "confidence_scores": await self._calculate_confidence_scores(df),
            "generated_at": datetime.now().isoformat()
        }
    
    async def _generate_metric_predictions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions for each ESG metric"""
        predictions = {}
        
        metrics = [
            'scope1_emissions', 'scope2_emissions', 'scope3_emissions',
            'water_consumption', 'waste_generated', 'energy_consumption',
            'renewable_energy_percentage'
        ]
        
        for metric in metrics:
            if metric in df.columns and df[metric].sum() > 0:
                try:
                    # Prepare data for prediction
                    X = df[['year']].values
                    y = df[metric].values
                    
                    # Train multiple models
                    models = {
                        'linear': LinearRegression(),
                        'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                        'gradient_boost': GradientBoostingRegressor(random_state=42)
                    }
                    
                    best_model = None
                    best_score = -float('inf')
                    
                    for name, model in models.items():
                        if len(X) > 3:  # Need enough data for train/test split
                            X_train, X_test, y_train, y_test = train_test_split(
                                X, y, test_size=0.3, random_state=42
                            )
                            model.fit(X_train, y_train)
                            score = model.score(X_test, y_test)
                        else:
                            model.fit(X, y)
                            score = model.score(X, y)
                        
                        if score > best_score:
                            best_score = score
                            best_model = model
                    
                    # Generate future predictions
                    current_year = datetime.now().year
                    future_years = np.array([[current_year + i] for i in range(1, 6)])
                    future_predictions = best_model.predict(future_years)
                    
                    # Calculate trend direction
                    recent_trend = np.polyfit(X[-3:].flatten(), y[-3:], 1)[0] if len(X) >= 3 else 0
                    
                    predictions[metric] = {
                        "future_values": {
                            str(current_year + i): float(pred) 
                            for i, pred in enumerate(future_predictions, 1)
                        },
                        "trend_direction": "increasing" if recent_trend > 0 else "decreasing",
                        "trend_strength": abs(float(recent_trend)),
                        "model_accuracy": float(best_score),
                        "confidence": "high" if best_score > 0.8 else "medium" if best_score > 0.5 else "low"
                    }
                    
                except Exception as e:
                    logger.error(f"Error predicting {metric}: {str(e)}")
                    predictions[metric] = {"error": f"Prediction failed: {str(e)}"}
        
        return predictions
    
    async def _calculate_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive trend analysis"""
        trends = {}
        
        metrics = [
            'scope1_emissions', 'scope2_emissions', 'scope3_emissions',
            'water_consumption', 'waste_generated', 'energy_consumption',
            'renewable_energy_percentage'
        ]
        
        for metric in metrics:
            if metric in df.columns and len(df) >= 2:
                values = df[metric].values
                years = df['year'].values
                
                # Calculate various trend metrics
                slope, intercept = np.polyfit(years, values, 1)
                correlation = np.corrcoef(years, values)[0, 1]
                
                # Year-over-year changes
                yoy_changes = []
                for i in range(1, len(values)):
                    if values[i-1] != 0:
                        change = ((values[i] - values[i-1]) / values[i-1]) * 100
                        yoy_changes.append(change)
                
                # Volatility (standard deviation of changes)
                volatility = np.std(yoy_changes) if yoy_changes else 0
                
                trends[metric] = {
                    "slope": float(slope),
                    "correlation": float(correlation),
                    "average_yoy_change": float(np.mean(yoy_changes)) if yoy_changes else 0,
                    "volatility": float(volatility),
                    "trend_classification": self._classify_trend(slope, correlation),
                    "recent_performance": self._analyze_recent_performance(values[-3:] if len(values) >= 3 else values)
                }
        
        return trends
    
    def _classify_trend(self, slope: float, correlation: float) -> str:
        """Classify trend based on slope and correlation"""
        if abs(correlation) < 0.3:
            return "no_clear_trend"
        elif slope > 0:
            return "strong_increase" if correlation > 0.7 else "moderate_increase"
        else:
            return "strong_decrease" if correlation < -0.7 else "moderate_decrease"
    
    def _analyze_recent_performance(self, recent_values: np.ndarray) -> Dict[str, Any]:
        """Analyze recent performance trends"""
        if len(recent_values) < 2:
            return {"status": "insufficient_data"}
        
        recent_change = ((recent_values[-1] - recent_values[0]) / recent_values[0]) * 100
        
        return {
            "recent_change_percent": float(recent_change),
            "direction": "improving" if recent_change < 0 else "worsening",  # For emissions, lower is better
            "momentum": "accelerating" if len(recent_values) >= 3 and 
                       abs(recent_values[-1] - recent_values[-2]) > abs(recent_values[-2] - recent_values[-3])
                       else "stable"
        }
    
    async def _assess_esg_risks(self, df: pd.DataFrame, db: Session) -> Dict[str, Any]:
        """Comprehensive ESG risk assessment"""
        risks = {
            "climate_risks": [],
            "regulatory_risks": [],
            "reputational_risks": [],
            "financial_risks": [],
            "overall_risk_score": 0
        }
        
        latest_data = df.iloc[-1]
        
        # Climate risks
        total_emissions = (latest_data.get('scope1_emissions', 0) + 
                          latest_data.get('scope2_emissions', 0) + 
                          latest_data.get('scope3_emissions', 0))
        
        if total_emissions > 10000:  # High emissions threshold
            risks["climate_risks"].append({
                "type": "high_carbon_footprint",
                "severity": "high",
                "description": "Total emissions exceed 10,000 tCO2e, indicating high climate risk",
                "mitigation": "Implement aggressive carbon reduction strategy"
            })
        
        # Renewable energy risk
        renewable_pct = latest_data.get('renewable_energy_percentage', 0)
        if renewable_pct < 30:
            risks["climate_risks"].append({
                "type": "low_renewable_energy",
                "severity": "medium",
                "description": f"Only {renewable_pct}% renewable energy usage",
                "mitigation": "Increase renewable energy adoption to at least 50%"
            })
        
        # Regulatory risks (based on trends)
        emissions_trend = np.polyfit(df['year'], df['scope1_emissions'].fillna(0), 1)[0]
        if emissions_trend > 0:
            risks["regulatory_risks"].append({
                "type": "increasing_emissions",
                "severity": "high",
                "description": "Emissions are trending upward, may face regulatory penalties",
                "mitigation": "Implement immediate emission reduction measures"
            })
        
        # Calculate overall risk score (0-100)
        risk_factors = len(risks["climate_risks"]) + len(risks["regulatory_risks"])
        risks["overall_risk_score"] = min(risk_factors * 20, 100)
        
        return risks
    
    async def _generate_optimization_recommendations(self, df: pd.DataFrame, db: Session) -> List[Dict[str, Any]]:
        """Generate AI-powered optimization recommendations"""
        recommendations = []
        
        latest_data = df.iloc[-1]
        
        # Energy optimization
        energy_consumption = latest_data.get('energy_consumption', 0)
        renewable_pct = latest_data.get('renewable_energy_percentage', 0)
        
        if energy_consumption > 0 and renewable_pct < 80:
            potential_savings = energy_consumption * (80 - renewable_pct) / 100
            recommendations.append({
                "category": "energy_optimization",
                "priority": "high",
                "title": "Increase Renewable Energy Adoption",
                "description": f"Increase renewable energy from {renewable_pct}% to 80%",
                "potential_impact": {
                    "emission_reduction_tco2e": potential_savings * 0.5,  # Rough conversion
                    "cost_savings_usd": potential_savings * 100,  # Rough estimate
                    "implementation_time_months": 12
                },
                "action_steps": [
                    "Conduct renewable energy feasibility study",
                    "Install solar panels or wind turbines",
                    "Sign renewable energy purchase agreements",
                    "Implement energy storage solutions"
                ]
            })
        
        # Waste reduction
        waste_generated = latest_data.get('waste_generated', 0)
        if waste_generated > 100:  # tonnes
            recommendations.append({
                "category": "waste_reduction",
                "priority": "medium",
                "title": "Implement Circular Economy Practices",
                "description": f"Reduce waste generation from {waste_generated} tonnes",
                "potential_impact": {
                    "waste_reduction_percent": 30,
                    "cost_savings_usd": waste_generated * 200,  # Waste disposal costs
                    "implementation_time_months": 6
                },
                "action_steps": [
                    "Implement waste segregation and recycling",
                    "Partner with waste-to-energy facilities",
                    "Design products for circularity",
                    "Establish take-back programs"
                ]
            })
        
        # Water conservation
        water_consumption = latest_data.get('water_consumption', 0)
        if water_consumption > 1000:  # m³
            recommendations.append({
                "category": "water_conservation",
                "priority": "medium",
                "title": "Implement Water Efficiency Measures",
                "description": f"Reduce water consumption from {water_consumption} m³",
                "potential_impact": {
                    "water_savings_percent": 25,
                    "cost_savings_usd": water_consumption * 5,  # Water costs
                    "implementation_time_months": 4
                },
                "action_steps": [
                    "Install water-efficient fixtures",
                    "Implement rainwater harvesting",
                    "Recycle and reuse wastewater",
                    "Monitor water usage with smart meters"
                ]
            })
        
        return recommendations
    
    async def _perform_scenario_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform scenario analysis for different ESG strategies"""
        scenarios = {}
        
        latest_data = df.iloc[-1]
        
        # Business as usual scenario
        scenarios["business_as_usual"] = {
            "description": "Continue current practices without changes",
            "projected_outcomes": {
                "2025_emissions": latest_data.get('scope1_emissions', 0) * 1.05,  # 5% increase
                "2030_emissions": latest_data.get('scope1_emissions', 0) * 1.25,  # 25% increase
                "risk_level": "high"
            }
        }
        
        # Aggressive reduction scenario
        scenarios["aggressive_reduction"] = {
            "description": "Implement all recommended ESG improvements",
            "projected_outcomes": {
                "2025_emissions": latest_data.get('scope1_emissions', 0) * 0.7,   # 30% reduction
                "2030_emissions": latest_data.get('scope1_emissions', 0) * 0.4,   # 60% reduction
                "risk_level": "low",
                "investment_required": 1000000,  # USD
                "roi_years": 5
            }
        }
        
        # Moderate improvement scenario
        scenarios["moderate_improvement"] = {
            "description": "Implement cost-effective ESG measures",
            "projected_outcomes": {
                "2025_emissions": latest_data.get('scope1_emissions', 0) * 0.85,  # 15% reduction
                "2030_emissions": latest_data.get('scope1_emissions', 0) * 0.7,   # 30% reduction
                "risk_level": "medium",
                "investment_required": 500000,  # USD
                "roi_years": 3
            }
        }
        
        return scenarios
    
    async def _calculate_confidence_scores(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate confidence scores for predictions"""
        confidence_scores = {}
        
        # Data quality score
        data_completeness = df.notna().mean().mean()
        data_consistency = 1 - df.std().mean() / df.mean().mean() if df.mean().mean() != 0 else 0
        
        confidence_scores["data_quality"] = float(data_completeness * 0.7 + data_consistency * 0.3)
        confidence_scores["prediction_reliability"] = min(len(df) / 5, 1.0)  # More data = higher confidence
        confidence_scores["trend_stability"] = float(1 - df.std().mean() / df.mean().mean()) if df.mean().mean() != 0 else 0
        
        # Overall confidence
        confidence_scores["overall"] = float(np.mean(list(confidence_scores.values())))
        
        return confidence_scores
    
    async def generate_industry_comparison(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Generate detailed industry comparison analysis"""
        
        # Get user's latest data
        user_data = db.query(UserESGData).filter(
            UserESGData.user_id == user_id
        ).order_by(UserESGData.year.desc()).first()
        
        if not user_data:
            return {"error": "No user data found"}
        
        # Get industry benchmarks
        industry_data = db.query(UserESGData).filter(
            UserESGData.year == user_data.year
        ).all()
        
        if len(industry_data) < 5:
            return {"error": "Insufficient industry data for comparison"}
        
        # Convert to DataFrame
        industry_df = pd.DataFrame([{
            'scope1_emissions': data.scope1_emissions or 0,
            'scope2_emissions': data.scope2_emissions or 0,
            'scope3_emissions': data.scope3_emissions or 0,
            'water_consumption': data.water_consumption or 0,
            'waste_generated': data.waste_generated or 0,
            'energy_consumption': data.energy_consumption or 0,
            'renewable_energy_percentage': data.renewable_energy_percentage or 0
        } for data in industry_data])
        
        comparison = {}
        
        metrics = [
            'scope1_emissions', 'scope2_emissions', 'scope3_emissions',
            'water_consumption', 'waste_generated', 'energy_consumption',
            'renewable_energy_percentage'
        ]
        
        for metric in metrics:
            user_value = getattr(user_data, metric) or 0
            industry_values = industry_df[metric]
            
            comparison[metric] = {
                "user_value": float(user_value),
                "industry_median": float(industry_values.median()),
                "industry_mean": float(industry_values.mean()),
                "percentile": float((industry_values < user_value).mean() * 100),
                "best_in_class": float(industry_values.min()),
                "worst_in_class": float(industry_values.max()),
                "performance_gap": float(user_value - industry_values.median()),
                "improvement_potential": float(industry_values.quantile(0.25) - user_value) if user_value > industry_values.quantile(0.25) else 0
            }
        
        return {
            "comparison": comparison,
            "overall_ranking": self._calculate_overall_ranking(comparison),
            "peer_analysis": await self._generate_peer_analysis(user_data, industry_df),
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_overall_ranking(self, comparison: Dict) -> Dict[str, Any]:
        """Calculate overall ESG ranking"""
        
        # Weight different metrics (emissions are negative, renewable energy is positive)
        weights = {
            'scope1_emissions': -0.2,
            'scope2_emissions': -0.2,
            'scope3_emissions': -0.15,
            'water_consumption': -0.15,
            'waste_generated': -0.15,
            'energy_consumption': -0.1,
            'renewable_energy_percentage': 0.15
        }
        
        weighted_score = 0
        total_weight = 0
        
        for metric, weight in weights.items():
            if metric in comparison:
                percentile = comparison[metric]['percentile']
                # For negative weights (bad metrics), invert the percentile
                if weight < 0:
                    percentile = 100 - percentile
                
                weighted_score += percentile * abs(weight)
                total_weight += abs(weight)
        
        overall_score = weighted_score / total_weight if total_weight > 0 else 0
        
        return {
            "overall_score": float(overall_score),
            "ranking_tier": self._get_ranking_tier(overall_score),
            "improvement_areas": self._identify_improvement_areas(comparison)
        }
    
    def _get_ranking_tier(self, score: float) -> str:
        """Get ranking tier based on score"""
        if score >= 80:
            return "ESG Leader"
        elif score >= 60:
            return "ESG Performer"
        elif score >= 40:
            return "ESG Improver"
        else:
            return "ESG Laggard"
    
    def _identify_improvement_areas(self, comparison: Dict) -> List[str]:
        """Identify key areas for improvement"""
        improvement_areas = []
        
        for metric, data in comparison.items():
            if data['percentile'] > 75:  # Worse than 75% of peers
                improvement_areas.append(metric)
        
        return improvement_areas
    
    async def _generate_peer_analysis(self, user_data: UserESGData, industry_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate peer analysis insights"""
        
        # Find similar companies (by size/revenue if available)
        user_revenue = user_data.revenue or 0
        user_employees = user_data.employee_count or 0
        
        # This would be enhanced with actual peer company data
        peer_analysis = {
            "similar_size_companies": {
                "count": len(industry_df),  # Simplified
                "average_performance": {
                    "scope1_emissions": float(industry_df['scope1_emissions'].mean()),
                    "renewable_energy": float(industry_df['renewable_energy_percentage'].mean())
                }
            },
            "best_practices": [
                "Top performers typically have >70% renewable energy",
                "Leading companies show consistent year-over-year emission reductions",
                "Best-in-class waste management achieves <50 tonnes/year"
            ],
            "competitive_positioning": "Analysis based on current industry data"
        }
        
        return peer_analysis


# Singleton instance
analytics_service = ESGAnalyticsService()
