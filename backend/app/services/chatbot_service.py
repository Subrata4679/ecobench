"""
Intelligent chatbot service for ESG comparative analysis
"""
import openai
from typing import List, Dict, Optional, Any
import json
import logging
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models import (
    ChatSession, ChatMessage, UserESGData, Organization, 
    KPIValue, KPIDefinition, RegulatoryReport, User
)
from app.config import settings

logger = logging.getLogger(__name__)


class ESGChatbotService:
    """Intelligent chatbot for ESG comparative analysis"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        
        # ESG metrics mapping for standardization
        self.esg_metrics_mapping = {
            'scope1_emissions': {
                'name': 'Scope 1 Emissions',
                'unit': 'tCO2e',
                'description': 'Direct greenhouse gas emissions from owned or controlled sources'
            },
            'scope2_emissions': {
                'name': 'Scope 2 Emissions', 
                'unit': 'tCO2e',
                'description': 'Indirect greenhouse gas emissions from purchased energy'
            },
            'scope3_emissions': {
                'name': 'Scope 3 Emissions',
                'unit': 'tCO2e', 
                'description': 'Indirect greenhouse gas emissions from value chain activities'
            },
            'water_consumption': {
                'name': 'Water Consumption',
                'unit': 'm³',
                'description': 'Total water consumption across operations'
            },
            'waste_generated': {
                'name': 'Waste Generated',
                'unit': 'tonnes',
                'description': 'Total waste generated across operations'
            },
            'energy_consumption': {
                'name': 'Energy Consumption',
                'unit': 'MWh',
                'description': 'Total energy consumption across operations'
            },
            'renewable_energy_percentage': {
                'name': 'Renewable Energy Percentage',
                'unit': '%',
                'description': 'Percentage of energy from renewable sources'
            }
        }
    
    async def create_chat_session(self, user_id: int, session_name: str, db: Session) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            user_id=user_id,
            session_name=session_name or f"ESG Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    async def get_user_esg_data(self, user_id: int, db: Session) -> Optional[UserESGData]:
        """Get the most recent ESG data for a user"""
        return db.query(UserESGData).filter(
            UserESGData.user_id == user_id
        ).order_by(UserESGData.year.desc()).first()
    
    async def get_industry_benchmarks(self, metric: str, year: int, db: Session) -> Dict:
        """Get industry benchmarks for a specific metric"""
        
        # Map user metric to KPI definition
        kpi_code_mapping = {
            'scope1_emissions': 'SCOPE1_EMISSIONS',
            'scope2_emissions': 'SCOPE2_EMISSIONS', 
            'scope3_emissions': 'SCOPE3_EMISSIONS',
            'water_consumption': 'WATER_CONSUMPTION',
            'waste_generated': 'WASTE_GENERATED',
            'energy_consumption': 'ENERGY_CONSUMPTION',
            'renewable_energy_percentage': 'RENEWABLE_ENERGY_PCT'
        }
        
        kpi_code = kpi_code_mapping.get(metric)
        if not kpi_code:
            return {}
        
        # Get KPI definition
        kpi_def = db.query(KPIDefinition).filter(
            KPIDefinition.code == kpi_code
        ).first()
        
        if not kpi_def:
            return {}
        
        # Get IT sector organizations
        it_orgs = db.query(Organization).filter(
            Organization.sector == 'Information Technology'
        ).all()
        
        if not it_orgs:
            return {}
        
        org_ids = [org.id for org in it_orgs]
        
        # Get KPI values for IT companies
        kpi_values = db.query(KPIValue).filter(
            and_(
                KPIValue.kpi_id == kpi_def.id,
                KPIValue.year == year,
                KPIValue.organization_id.in_(org_ids),
                KPIValue.value_numeric.isnot(None)
            )
        ).all()
        
        if not kpi_values:
            return {}
        
        values = [kv.value_numeric for kv in kpi_values]
        
        # Calculate statistics
        stats = {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': np.mean(values),
            'median': np.median(values),
            'p25': np.percentile(values, 25),
            'p75': np.percentile(values, 75),
            'std': np.std(values)
        }
        
        # Get company details for context
        companies = []
        for kv in kpi_values:
            org = next((o for o in it_orgs if o.id == kv.organization_id), None)
            if org:
                companies.append({
                    'name': org.name,
                    'ticker': org.ticker,
                    'value': kv.value_numeric
                })
        
        return {
            'metric': metric,
            'year': year,
            'statistics': stats,
            'companies': companies,
            'unit': self.esg_metrics_mapping.get(metric, {}).get('unit', '')
        }
    
    async def analyze_user_performance(self, user_data: UserESGData, db: Session) -> Dict:
        """Analyze user's ESG performance against industry benchmarks"""
        
        analysis = {
            'company_name': user_data.company_name,
            'year': user_data.year,
            'metrics_analysis': {},
            'overall_score': 0,
            'recommendations': []
        }
        
        metrics_to_analyze = [
            'scope1_emissions', 'scope2_emissions', 'scope3_emissions',
            'water_consumption', 'waste_generated', 'energy_consumption',
            'renewable_energy_percentage'
        ]
        
        total_score = 0
        analyzed_metrics = 0
        
        for metric in metrics_to_analyze:
            user_value = getattr(user_data, metric)
            if user_value is None:
                continue
            
            benchmarks = await self.get_industry_benchmarks(metric, user_data.year, db)
            if not benchmarks or not benchmarks.get('statistics'):
                continue
            
            stats = benchmarks['statistics']
            
            # Calculate percentile ranking
            percentile = self.calculate_percentile(user_value, benchmarks['companies'])
            
            # Determine performance level
            performance_level = self.get_performance_level(percentile, metric)
            
            # Calculate score (0-100)
            score = self.calculate_metric_score(user_value, stats, metric)
            
            analysis['metrics_analysis'][metric] = {
                'user_value': user_value,
                'industry_median': stats['median'],
                'industry_mean': stats['mean'],
                'percentile': percentile,
                'performance_level': performance_level,
                'score': score,
                'unit': self.esg_metrics_mapping.get(metric, {}).get('unit', ''),
                'comparison': self.generate_comparison_text(user_value, stats, metric, percentile)
            }
            
            total_score += score
            analyzed_metrics += 1
        
        if analyzed_metrics > 0:
            analysis['overall_score'] = total_score / analyzed_metrics
        
        # Generate recommendations
        analysis['recommendations'] = await self.generate_recommendations(analysis, db)
        
        return analysis
    
    def calculate_percentile(self, user_value: float, companies: List[Dict]) -> float:
        """Calculate percentile ranking of user value"""
        if not companies:
            return 50.0
        
        values = [c['value'] for c in companies]
        values.sort()
        
        # Find position of user value
        position = 0
        for value in values:
            if user_value <= value:
                break
            position += 1
        
        percentile = (position / len(values)) * 100
        return round(percentile, 1)
    
    def get_performance_level(self, percentile: float, metric: str) -> str:
        """Determine performance level based on percentile"""
        
        # For emissions and waste metrics, lower is better
        lower_is_better = metric in ['scope1_emissions', 'scope2_emissions', 'scope3_emissions', 'waste_generated', 'water_consumption', 'energy_consumption']
        
        if lower_is_better:
            if percentile <= 25:
                return 'Excellent'
            elif percentile <= 50:
                return 'Good'
            elif percentile <= 75:
                return 'Average'
            else:
                return 'Needs Improvement'
        else:
            # For renewable energy percentage, higher is better
            if percentile >= 75:
                return 'Excellent'
            elif percentile >= 50:
                return 'Good'
            elif percentile >= 25:
                return 'Average'
            else:
                return 'Needs Improvement'
    
    def calculate_metric_score(self, user_value: float, stats: Dict, metric: str) -> float:
        """Calculate a score (0-100) for a metric"""
        
        lower_is_better = metric in ['scope1_emissions', 'scope2_emissions', 'scope3_emissions', 'waste_generated', 'water_consumption', 'energy_consumption']
        
        if lower_is_better:
            # Score based on how much below the median
            if user_value <= stats['p25']:
                return 90 + (stats['p25'] - user_value) / stats['p25'] * 10
            elif user_value <= stats['median']:
                return 70 + (stats['median'] - user_value) / (stats['median'] - stats['p25']) * 20
            elif user_value <= stats['p75']:
                return 40 + (stats['p75'] - user_value) / (stats['p75'] - stats['median']) * 30
            else:
                return max(0, 40 - (user_value - stats['p75']) / stats['p75'] * 40)
        else:
            # For renewable energy, higher is better
            if user_value >= stats['p75']:
                return 90 + (user_value - stats['p75']) / stats['p75'] * 10
            elif user_value >= stats['median']:
                return 70 + (user_value - stats['median']) / (stats['p75'] - stats['median']) * 20
            elif user_value >= stats['p25']:
                return 40 + (user_value - stats['p25']) / (stats['median'] - stats['p25']) * 30
            else:
                return max(0, 40 - (stats['p25'] - user_value) / stats['p25'] * 40)
    
    def generate_comparison_text(self, user_value: float, stats: Dict, metric: str, percentile: float) -> str:
        """Generate human-readable comparison text"""
        
        metric_info = self.esg_metrics_mapping.get(metric, {})
        unit = metric_info.get('unit', '')
        
        diff_from_median = user_value - stats['median']
        diff_percentage = (abs(diff_from_median) / stats['median']) * 100
        
        if diff_from_median > 0:
            comparison = f"{diff_percentage:.1f}% higher than"
        else:
            comparison = f"{diff_percentage:.1f}% lower than"
        
        return f"Your {metric_info.get('name', metric)} of {user_value:,.1f} {unit} is {comparison} the industry median of {stats['median']:,.1f} {unit}. You rank in the {percentile:.0f}th percentile."
    
    async def generate_recommendations(self, analysis: Dict, db: Session) -> List[str]:
        """Generate AI-powered recommendations based on analysis"""
        
        recommendations = []
        
        for metric, data in analysis['metrics_analysis'].items():
            if data['performance_level'] in ['Needs Improvement', 'Average']:
                metric_info = self.esg_metrics_mapping.get(metric, {})
                
                if metric in ['scope1_emissions', 'scope2_emissions', 'scope3_emissions']:
                    recommendations.append(
                        f"Consider implementing carbon reduction strategies for {metric_info['name']}. "
                        f"Your current emissions are {data['percentile']:.0f}th percentile - "
                        f"targeting the industry median could reduce emissions by {abs(data['user_value'] - data['industry_median']):.0f} tCO2e."
                    )
                elif metric == 'renewable_energy_percentage':
                    recommendations.append(
                        f"Increase renewable energy adoption. Your current {data['user_value']:.1f}% "
                        f"is below the industry median of {data['industry_median']:.1f}%. "
                        f"Consider setting a target of {data['industry_median'] + 10:.0f}% renewable energy."
                    )
                elif metric == 'water_consumption':
                    recommendations.append(
                        f"Implement water efficiency measures. Your consumption is {data['percentile']:.0f}th percentile. "
                        f"Water recycling and efficiency programs could reduce usage significantly."
                    )
                elif metric == 'waste_generated':
                    recommendations.append(
                        f"Enhance waste reduction and circular economy practices. "
                        f"Your waste generation is above industry median - consider waste-to-energy programs and material efficiency improvements."
                    )
        
        return recommendations
    
    async def process_chat_message(self, session_id: int, user_message: str, db: Session) -> Dict:
        """Process a chat message and generate AI response"""
        
        # Get chat session
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise ValueError("Chat session not found")
        
        # Store user message
        user_msg = ChatMessage(
            session_id=session_id,
            role='user',
            content=user_message
        )
        db.add(user_msg)
        
        # Get user's ESG data for context
        user_esg_data = await self.get_user_esg_data(session.user_id, db)
        
        # Get conversation history
        previous_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        
        # Generate AI response
        response_content, metadata = await self.generate_ai_response(
            user_message, user_esg_data, previous_messages, db
        )
        
        # Store AI response
        ai_msg = ChatMessage(
            session_id=session_id,
            role='assistant',
            content=response_content,
            metadata=metadata
        )
        db.add(ai_msg)
        db.commit()
        
        return {
            'message': response_content,
            'metadata': metadata,
            'session_id': session_id
        }
    
    async def generate_ai_response(self, user_message: str, user_esg_data: Optional[UserESGData], 
                                 conversation_history: List[ChatMessage], db: Session) -> tuple[str, Dict]:
        """Generate AI response using OpenAI"""
        
        # Build context
        context_parts = []
        
        if user_esg_data:
            analysis = await self.analyze_user_performance(user_esg_data, db)
            context_parts.append(f"User's ESG Data Analysis: {json.dumps(analysis, indent=2)}")
        
        # Get recent regulatory reports for context
        recent_reports = db.query(RegulatoryReport).join(Organization).filter(
            Organization.sector == 'Information Technology'
        ).order_by(RegulatoryReport.filing_date.desc()).limit(5).all()
        
        if recent_reports:
            reports_context = "Recent IT Industry Regulatory Reports:\n"
            for report in recent_reports:
                reports_context += f"- {report.organization.name}: {report.report_type} ({report.filing_date.strftime('%Y-%m-%d')})\n"
            context_parts.append(reports_context)
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            conversation_context = "Previous conversation:\n"
            for msg in reversed(conversation_history[-5:]):  # Last 5 messages
                conversation_context += f"{msg.role}: {msg.content}\n"
        
        # Create system prompt
        system_prompt = f"""
You are an expert ESG (Environmental, Social, Governance) analyst specializing in the Information Technology sector. 
You help companies understand their ESG performance compared to industry peers and provide actionable recommendations.

Context Information:
{chr(10).join(context_parts)}

{conversation_context}

Guidelines:
1. Provide specific, data-driven insights based on the user's ESG metrics
2. Compare performance against IT industry benchmarks when available
3. Explain why certain metrics are higher or lower than peers
4. Suggest concrete actions for improvement
5. Reference relevant regulatory requirements and industry best practices
6. Be encouraging but honest about areas needing improvement
7. Use the regulatory reports context to provide industry insights

Always structure your responses clearly and provide quantitative comparisons when possible.
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Extract metadata for structured response
            metadata = {
                'analysis_type': 'esg_comparison',
                'has_user_data': user_esg_data is not None,
                'industry_context': len(recent_reports) > 0,
                'timestamp': datetime.now().isoformat()
            }
            
            return ai_response, metadata
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            
            fallback_response = """
I apologize, but I'm experiencing technical difficulties generating a detailed response. 
However, I can still help you with your ESG analysis. Could you please rephrase your question 
or let me know what specific ESG metrics you'd like to discuss?
"""
            
            return fallback_response, {'error': str(e)}
    
    async def get_chat_sessions(self, user_id: int, db: Session) -> List[Dict]:
        """Get all chat sessions for a user"""
        
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc()).all()
        
        result = []
        for session in sessions:
            # Get last message for preview
            last_message = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            result.append({
                'id': session.id,
                'session_name': session.session_name,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'last_message_preview': last_message.content[:100] + '...' if last_message else None
            })
        
        return result
    
    async def get_chat_history(self, session_id: int, db: Session) -> List[Dict]:
        """Get chat history for a session"""
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'metadata': msg.metadata,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]


# Singleton instance
chatbot_service = ESGChatbotService()
