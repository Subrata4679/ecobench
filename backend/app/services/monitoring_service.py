"""
Real-time ESG Monitoring Service with IoT Integration and Alerts
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import UserESGData, Organization, User
from app.database import get_db

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    EMISSIONS = "emissions"
    ENERGY = "energy"
    WATER = "water"
    WASTE = "waste"
    AIR_QUALITY = "air_quality"
    BIODIVERSITY = "biodiversity"


@dataclass
class ESGAlert:
    id: str
    metric_type: MetricType
    severity: AlertSeverity
    title: str
    description: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    user_id: int
    organization_id: Optional[int] = None
    recommendations: List[str] = None
    auto_actions: List[str] = None


@dataclass
class MonitoringRule:
    id: str
    metric_name: str
    threshold_value: float
    comparison_operator: str  # >, <, >=, <=, ==
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 60
    auto_actions: List[str] = None


class RealTimeESGMonitor:
    """Real-time ESG monitoring system with IoT integration"""
    
    def __init__(self):
        self.monitoring_rules: Dict[str, MonitoringRule] = {}
        self.active_alerts: Dict[str, ESGAlert] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.iot_connections: Dict[str, Any] = {}
        self.monitoring_active = False
        
        # Initialize default monitoring rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default monitoring rules"""
        
        default_rules = [
            MonitoringRule(
                id="high_scope1_emissions",
                metric_name="scope1_emissions",
                threshold_value=5000.0,  # tCO2e
                comparison_operator=">",
                severity=AlertSeverity.HIGH,
                auto_actions=["send_notification", "log_incident"]
            ),
            MonitoringRule(
                id="critical_scope1_emissions",
                metric_name="scope1_emissions",
                threshold_value=10000.0,  # tCO2e
                comparison_operator=">",
                severity=AlertSeverity.CRITICAL,
                auto_actions=["send_notification", "log_incident", "escalate_to_management"]
            ),
            MonitoringRule(
                id="low_renewable_energy",
                metric_name="renewable_energy_percentage",
                threshold_value=30.0,  # %
                comparison_operator="<",
                severity=AlertSeverity.MEDIUM,
                auto_actions=["send_notification"]
            ),
            MonitoringRule(
                id="high_water_consumption",
                metric_name="water_consumption",
                threshold_value=10000.0,  # m³
                comparison_operator=">",
                severity=AlertSeverity.HIGH,
                auto_actions=["send_notification", "suggest_conservation"]
            ),
            MonitoringRule(
                id="excessive_waste",
                metric_name="waste_generated",
                threshold_value=500.0,  # tonnes
                comparison_operator=">",
                severity=AlertSeverity.HIGH,
                auto_actions=["send_notification", "review_waste_management"]
            )
        ]
        
        for rule in default_rules:
            self.monitoring_rules[rule.id] = rule
    
    async def start_monitoring(self):
        """Start the real-time monitoring system"""
        self.monitoring_active = True
        logger.info("ESG Real-time monitoring started")
        
        # Start monitoring tasks
        asyncio.create_task(self._continuous_monitoring_loop())
        asyncio.create_task(self._iot_data_collector())
        asyncio.create_task(self._alert_processor())
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        logger.info("ESG Real-time monitoring stopped")
    
    async def _continuous_monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._check_all_metrics()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_all_metrics(self):
        """Check all metrics against monitoring rules"""
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get all users with recent ESG data
            recent_data = db.query(UserESGData).filter(
                UserESGData.created_at >= datetime.now() - timedelta(hours=24)
            ).all()
            
            for data in recent_data:
                await self._check_user_metrics(data, db)
                
        finally:
            db.close()
    
    async def _check_user_metrics(self, user_data: UserESGData, db: Session):
        """Check metrics for a specific user"""
        
        metrics = {
            'scope1_emissions': user_data.scope1_emissions,
            'scope2_emissions': user_data.scope2_emissions,
            'scope3_emissions': user_data.scope3_emissions,
            'water_consumption': user_data.water_consumption,
            'waste_generated': user_data.waste_generated,
            'energy_consumption': user_data.energy_consumption,
            'renewable_energy_percentage': user_data.renewable_energy_percentage
        }
        
        for metric_name, value in metrics.items():
            if value is not None:
                await self._evaluate_metric(
                    user_data.user_id, 
                    metric_name, 
                    value, 
                    user_data.company_name
                )
    
    async def _evaluate_metric(self, user_id: int, metric_name: str, value: float, company_name: str):
        """Evaluate a metric against monitoring rules"""
        
        for rule_id, rule in self.monitoring_rules.items():
            if rule.metric_name == metric_name and rule.enabled:
                
                # Check if rule is triggered
                triggered = self._check_rule_condition(value, rule)
                
                if triggered:
                    # Check cooldown period
                    if not self._is_in_cooldown(rule_id, user_id):
                        alert = await self._create_alert(
                            user_id, metric_name, value, rule, company_name
                        )
                        await self._process_alert(alert)
    
    def _check_rule_condition(self, value: float, rule: MonitoringRule) -> bool:
        """Check if a rule condition is met"""
        
        if rule.comparison_operator == ">":
            return value > rule.threshold_value
        elif rule.comparison_operator == "<":
            return value < rule.threshold_value
        elif rule.comparison_operator == ">=":
            return value >= rule.threshold_value
        elif rule.comparison_operator == "<=":
            return value <= rule.threshold_value
        elif rule.comparison_operator == "==":
            return value == rule.threshold_value
        
        return False
    
    def _is_in_cooldown(self, rule_id: str, user_id: int) -> bool:
        """Check if alert is in cooldown period"""
        
        alert_key = f"{rule_id}_{user_id}"
        
        if alert_key in self.active_alerts:
            last_alert = self.active_alerts[alert_key]
            rule = self.monitoring_rules[rule_id]
            
            time_since_last = datetime.now() - last_alert.timestamp
            return time_since_last.total_seconds() < (rule.cooldown_minutes * 60)
        
        return False
    
    async def _create_alert(self, user_id: int, metric_name: str, value: float, 
                          rule: MonitoringRule, company_name: str) -> ESGAlert:
        """Create an ESG alert"""
        
        alert_id = f"{rule.id}_{user_id}_{int(datetime.now().timestamp())}"
        
        # Generate contextual description and recommendations
        description, recommendations = self._generate_alert_content(
            metric_name, value, rule.threshold_value, rule.comparison_operator
        )
        
        alert = ESGAlert(
            id=alert_id,
            metric_type=self._get_metric_type(metric_name),
            severity=rule.severity,
            title=f"{metric_name.replace('_', ' ').title()} Alert - {company_name}",
            description=description,
            current_value=value,
            threshold_value=rule.threshold_value,
            timestamp=datetime.now(),
            user_id=user_id,
            recommendations=recommendations,
            auto_actions=rule.auto_actions or []
        )
        
        return alert
    
    def _get_metric_type(self, metric_name: str) -> MetricType:
        """Get metric type from metric name"""
        
        if 'emission' in metric_name:
            return MetricType.EMISSIONS
        elif 'energy' in metric_name:
            return MetricType.ENERGY
        elif 'water' in metric_name:
            return MetricType.WATER
        elif 'waste' in metric_name:
            return MetricType.WASTE
        else:
            return MetricType.EMISSIONS  # Default
    
    def _generate_alert_content(self, metric_name: str, value: float, 
                              threshold: float, operator: str) -> tuple[str, List[str]]:
        """Generate alert description and recommendations"""
        
        descriptions = {
            'scope1_emissions': f"Direct emissions have reached {value:,.1f} tCO2e, exceeding the threshold of {threshold:,.1f} tCO2e",
            'scope2_emissions': f"Indirect emissions from energy have reached {value:,.1f} tCO2e, exceeding the threshold of {threshold:,.1f} tCO2e",
            'scope3_emissions': f"Value chain emissions have reached {value:,.1f} tCO2e, exceeding the threshold of {threshold:,.1f} tCO2e",
            'water_consumption': f"Water consumption has reached {value:,.1f} m³, exceeding the threshold of {threshold:,.1f} m³",
            'waste_generated': f"Waste generation has reached {value:,.1f} tonnes, exceeding the threshold of {threshold:,.1f} tonnes",
            'energy_consumption': f"Energy consumption has reached {value:,.1f} MWh, exceeding the threshold of {threshold:,.1f} MWh",
            'renewable_energy_percentage': f"Renewable energy percentage is {value:.1f}%, below the target of {threshold:.1f}%"
        }
        
        recommendations_map = {
            'scope1_emissions': [
                "Implement immediate emission reduction measures",
                "Review and optimize industrial processes",
                "Consider switching to cleaner fuel alternatives",
                "Enhance energy efficiency programs"
            ],
            'scope2_emissions': [
                "Increase renewable energy procurement",
                "Implement energy efficiency measures",
                "Consider on-site renewable energy generation",
                "Optimize HVAC and lighting systems"
            ],
            'scope3_emissions': [
                "Engage with suppliers on emission reduction",
                "Optimize supply chain logistics",
                "Promote sustainable business travel policies",
                "Implement circular economy practices"
            ],
            'water_consumption': [
                "Implement water conservation measures",
                "Install water-efficient fixtures",
                "Implement rainwater harvesting",
                "Monitor and fix water leaks promptly"
            ],
            'waste_generated': [
                "Implement waste reduction strategies",
                "Enhance recycling programs",
                "Partner with waste-to-energy facilities",
                "Design products for circularity"
            ],
            'energy_consumption': [
                "Implement energy efficiency measures",
                "Upgrade to energy-efficient equipment",
                "Optimize building management systems",
                "Conduct energy audits"
            ],
            'renewable_energy_percentage': [
                "Increase renewable energy procurement",
                "Install on-site solar or wind generation",
                "Sign renewable energy purchase agreements",
                "Implement energy storage solutions"
            ]
        }
        
        description = descriptions.get(metric_name, f"{metric_name} has triggered an alert")
        recommendations = recommendations_map.get(metric_name, ["Review and optimize current practices"])
        
        return description, recommendations
    
    async def _process_alert(self, alert: ESGAlert):
        """Process and handle an alert"""
        
        # Store alert
        alert_key = f"{alert.metric_type.value}_{alert.user_id}"
        self.active_alerts[alert_key] = alert
        
        # Execute auto actions
        for action in alert.auto_actions:
            await self._execute_auto_action(action, alert)
        
        # Notify subscribers
        await self._notify_subscribers(alert)
        
        logger.info(f"Alert processed: {alert.title} - Severity: {alert.severity.value}")
    
    async def _execute_auto_action(self, action: str, alert: ESGAlert):
        """Execute automatic actions for alerts"""
        
        try:
            if action == "send_notification":
                await self._send_notification(alert)
            elif action == "log_incident":
                await self._log_incident(alert)
            elif action == "escalate_to_management":
                await self._escalate_to_management(alert)
            elif action == "suggest_conservation":
                await self._suggest_conservation_measures(alert)
            elif action == "review_waste_management":
                await self._trigger_waste_review(alert)
            
        except Exception as e:
            logger.error(f"Error executing auto action {action}: {str(e)}")
    
    async def _send_notification(self, alert: ESGAlert):
        """Send notification for alert"""
        
        notification = {
            "type": "esg_alert",
            "severity": alert.severity.value,
            "title": alert.title,
            "message": alert.description,
            "timestamp": alert.timestamp.isoformat(),
            "recommendations": alert.recommendations
        }
        
        # In a real implementation, this would send to notification service
        logger.info(f"Notification sent: {notification}")
    
    async def _log_incident(self, alert: ESGAlert):
        """Log incident for alert"""
        
        incident = {
            "alert_id": alert.id,
            "type": "esg_incident",
            "severity": alert.severity.value,
            "metric": alert.metric_type.value,
            "value": alert.current_value,
            "threshold": alert.threshold_value,
            "timestamp": alert.timestamp.isoformat()
        }
        
        # In a real implementation, this would log to incident management system
        logger.info(f"Incident logged: {incident}")
    
    async def _escalate_to_management(self, alert: ESGAlert):
        """Escalate critical alerts to management"""
        
        escalation = {
            "alert_id": alert.id,
            "type": "management_escalation",
            "urgency": "high",
            "summary": f"Critical ESG alert: {alert.title}",
            "details": alert.description,
            "required_action": "Immediate review and response required"
        }
        
        # In a real implementation, this would notify management
        logger.warning(f"Management escalation: {escalation}")
    
    async def _suggest_conservation_measures(self, alert: ESGAlert):
        """Suggest conservation measures"""
        
        suggestions = {
            "alert_id": alert.id,
            "conservation_measures": alert.recommendations,
            "priority": "implement_immediately",
            "estimated_impact": "20-30% reduction in consumption"
        }
        
        logger.info(f"Conservation suggestions: {suggestions}")
    
    async def _trigger_waste_review(self, alert: ESGAlert):
        """Trigger waste management review"""
        
        review = {
            "alert_id": alert.id,
            "review_type": "waste_management_audit",
            "scheduled_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "focus_areas": ["waste_segregation", "recycling_efficiency", "circular_economy"]
        }
        
        logger.info(f"Waste review triggered: {review}")
    
    async def _notify_subscribers(self, alert: ESGAlert):
        """Notify all subscribers of the alert"""
        
        alert_type = alert.metric_type.value
        
        if alert_type in self.subscribers:
            for callback in self.subscribers[alert_type]:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error notifying subscriber: {str(e)}")
    
    def subscribe_to_alerts(self, metric_type: str, callback: Callable):
        """Subscribe to alerts for a specific metric type"""
        
        if metric_type not in self.subscribers:
            self.subscribers[metric_type] = []
        
        self.subscribers[metric_type].append(callback)
    
    def unsubscribe_from_alerts(self, metric_type: str, callback: Callable):
        """Unsubscribe from alerts"""
        
        if metric_type in self.subscribers:
            try:
                self.subscribers[metric_type].remove(callback)
            except ValueError:
                pass
    
    async def _iot_data_collector(self):
        """Collect data from IoT sensors"""
        
        while self.monitoring_active:
            try:
                # Simulate IoT data collection
                await self._collect_sensor_data()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                logger.error(f"Error collecting IoT data: {str(e)}")
                await asyncio.sleep(30)
    
    async def _collect_sensor_data(self):
        """Collect data from various IoT sensors"""
        
        # Simulate real-time sensor data
        sensor_data = {
            "air_quality": {
                "pm25": np.random.normal(15, 5),  # PM2.5 levels
                "co2": np.random.normal(400, 50),  # CO2 ppm
                "nox": np.random.normal(20, 10)   # NOx levels
            },
            "energy": {
                "current_consumption": np.random.normal(1000, 200),  # kWh
                "renewable_generation": np.random.normal(300, 100),  # kWh
                "grid_carbon_intensity": np.random.normal(0.5, 0.1)  # kgCO2/kWh
            },
            "water": {
                "flow_rate": np.random.normal(50, 10),  # L/min
                "quality_index": np.random.normal(85, 15),  # Quality score
                "temperature": np.random.normal(20, 5)  # Celsius
            },
            "waste": {
                "bin_fill_level": np.random.uniform(0, 100),  # Percentage
                "recycling_rate": np.random.normal(60, 20),  # Percentage
                "organic_waste": np.random.normal(30, 10)  # kg/day
            }
        }
        
        # Process sensor data and check for anomalies
        await self._process_sensor_data(sensor_data)
    
    async def _process_sensor_data(self, sensor_data: Dict[str, Any]):
        """Process IoT sensor data and detect anomalies"""
        
        # Check air quality
        if sensor_data["air_quality"]["pm25"] > 35:  # WHO guideline
            await self._create_sensor_alert(
                "air_quality", 
                "PM2.5 levels exceed WHO guidelines",
                sensor_data["air_quality"]["pm25"],
                35
            )
        
        # Check energy efficiency
        renewable_percentage = (sensor_data["energy"]["renewable_generation"] / 
                              sensor_data["energy"]["current_consumption"]) * 100
        
        if renewable_percentage < 20:
            await self._create_sensor_alert(
                "energy_efficiency",
                "Low renewable energy percentage detected",
                renewable_percentage,
                20
            )
        
        # Check water quality
        if sensor_data["water"]["quality_index"] < 70:
            await self._create_sensor_alert(
                "water_quality",
                "Water quality index below acceptable levels",
                sensor_data["water"]["quality_index"],
                70
            )
    
    async def _create_sensor_alert(self, sensor_type: str, description: str, 
                                 current_value: float, threshold: float):
        """Create alert from sensor data"""
        
        alert = ESGAlert(
            id=f"sensor_{sensor_type}_{int(datetime.now().timestamp())}",
            metric_type=MetricType.AIR_QUALITY if sensor_type == "air_quality" else MetricType.ENERGY,
            severity=AlertSeverity.MEDIUM,
            title=f"Sensor Alert: {sensor_type.replace('_', ' ').title()}",
            description=description,
            current_value=current_value,
            threshold_value=threshold,
            timestamp=datetime.now(),
            user_id=0,  # System alert
            recommendations=[f"Review {sensor_type} systems immediately"]
        )
        
        await self._process_alert(alert)
    
    async def _alert_processor(self):
        """Process and manage alerts"""
        
        while self.monitoring_active:
            try:
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                # Generate alert summaries
                await self._generate_alert_summaries()
                
                await asyncio.sleep(300)  # Process every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in alert processor: {str(e)}")
                await asyncio.sleep(300)
    
    async def _cleanup_old_alerts(self):
        """Clean up alerts older than 24 hours"""
        
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        alerts_to_remove = []
        for alert_key, alert in self.active_alerts.items():
            if alert.timestamp < cutoff_time:
                alerts_to_remove.append(alert_key)
        
        for alert_key in alerts_to_remove:
            del self.active_alerts[alert_key]
    
    async def _generate_alert_summaries(self):
        """Generate periodic alert summaries"""
        
        if not self.active_alerts:
            return
        
        # Group alerts by severity
        severity_counts = {}
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_active_alerts": len(self.active_alerts),
            "severity_breakdown": severity_counts,
            "top_alert_types": self._get_top_alert_types()
        }
        
        logger.info(f"Alert summary: {summary}")
    
    def _get_top_alert_types(self) -> List[str]:
        """Get most common alert types"""
        
        type_counts = {}
        for alert in self.active_alerts.values():
            alert_type = alert.metric_type.value
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        # Return top 3 alert types
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return [alert_type for alert_type, _ in sorted_types[:3]]
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get real-time monitoring dashboard data"""
        
        return {
            "monitoring_status": "active" if self.monitoring_active else "inactive",
            "active_alerts": len(self.active_alerts),
            "monitoring_rules": len(self.monitoring_rules),
            "recent_alerts": [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "metric_type": alert.metric_type.value
                }
                for alert in sorted(
                    self.active_alerts.values(), 
                    key=lambda x: x.timestamp, 
                    reverse=True
                )[:10]
            ],
            "alert_statistics": await self._get_alert_statistics(),
            "system_health": await self._get_system_health()
        }
    
    async def _get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        
        if not self.active_alerts:
            return {"total": 0}
        
        # Calculate statistics
        severity_counts = {}
        type_counts = {}
        
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            alert_type = alert.metric_type.value
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        return {
            "total": len(self.active_alerts),
            "by_severity": severity_counts,
            "by_type": type_counts,
            "average_per_hour": len(self.active_alerts) / 24  # Rough estimate
        }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get monitoring system health status"""
        
        return {
            "monitoring_active": self.monitoring_active,
            "rules_active": sum(1 for rule in self.monitoring_rules.values() if rule.enabled),
            "iot_connections": len(self.iot_connections),
            "subscribers": sum(len(subs) for subs in self.subscribers.values()),
            "last_check": datetime.now().isoformat(),
            "uptime_hours": 24  # Simplified
        }


# Singleton instance
monitoring_service = RealTimeESGMonitor()
