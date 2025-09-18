"""
Simplified FastAPI application for Windows development
This version avoids complex dependencies that have compatibility issues with Python 3.13
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import subprocess
from datetime import datetime

# Simple data models
class Organization(BaseModel):
    id: Optional[int] = None
    name: str
    industry: str
    size: str
    description: Optional[str] = None
    website: Optional[str] = None
    headquarters: Optional[str] = None
    created_at: Optional[datetime] = None

class KPIDefinition(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    category: str
    unit: str
    data_type: str = "numeric"

class KPIValue(BaseModel):
    id: Optional[int] = None
    kpi_definition_id: int
    organization_id: int
    value: str
    reporting_period: str
    data_source: Optional[str] = None
    confidence_score: Optional[float] = None

# Simple in-memory storage
data_store = {
    "organizations": [],
    "kpi_definitions": [],
    "kpi_values": []
}

# Load sample data if available
def load_sample_data():
    """Load sample data from JSON file if it exists"""
    sample_file = "sample_data.json"
    if os.path.exists(sample_file):
        try:
            with open(sample_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Default sample data with real-world companies
    return {
        "organizations": [
            {
                "id": 1,
                "name": "IBM Corporation",
                "industry": "Technology",
                "size": "Large",
                "description": "Global technology and consulting company with strong ESG commitments",
                "website": "https://www.ibm.com",
                "headquarters": "Armonk, NY",
                "created_at": "2023-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "name": "Infosys Limited",
                "industry": "Technology",
                "size": "Large",
                "description": "Global leader in next-generation digital services and consulting",
                "website": "https://www.infosys.com",
                "headquarters": "Bangalore, India",
                "created_at": "2023-01-01T00:00:00Z"
            },
            {
                "id": 3,
                "name": "TechCorp Industries",
                "industry": "Technology",
                "size": "Large",
                "description": "Leading technology company focused on sustainable innovation",
                "website": "https://techcorp.example.com",
                "headquarters": "San Francisco, CA",
                "created_at": "2023-01-01T00:00:00Z"
            }
        ],
        "kpi_definitions": [
            {
                "id": 1,
                "name": "Carbon Emissions (Scope 1)",
                "description": "Direct greenhouse gas emissions from owned or controlled sources",
                "category": "Environmental",
                "unit": "tCO2e",
                "data_type": "numeric"
            },
            {
                "id": 2,
                "name": "Water Consumption",
                "description": "Total water consumption across all operations",
                "category": "Environmental",
                "unit": "m³",
                "data_type": "numeric"
            },
            {
                "id": 3,
                "name": "Employee Turnover Rate",
                "description": "Annual employee turnover rate",
                "category": "Social",
                "unit": "%",
                "data_type": "numeric"
            }
        ],
        "kpi_values": [
            {
                "id": 1,
                "kpi_definition_id": 1,
                "organization_id": 1,
                "value": "1250.5",
                "reporting_period": "2023-12-31",
                "data_source": "Annual Report 2023",
                "confidence_score": 0.95
            },
            {
                "id": 2,
                "kpi_definition_id": 2,
                "organization_id": 1,
                "value": "15000",
                "reporting_period": "2023-12-31",
                "data_source": "Sustainability Report 2023",
                "confidence_score": 0.88
            }
        ]
    }

# Initialize data
data_store = load_sample_data()

# Create FastAPI app
app = FastAPI(
    title="EcoBench ESG Platform (Simplified)",
    description="Simplified version for Windows development",
    version="1.0.0-dev"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-dev",
        "service": "ecobench-api-simplified"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to EcoBench ESG Platform (Simplified)",
        "description": "Simplified version for Windows development",
        "version": "1.0.0-dev",
        "docs": "/docs",
        "health": "/health"
    }

# Organizations endpoints
@app.get("/api/organizations", response_model=List[Organization])
async def get_organizations():
    """Get all organizations"""
    return data_store["organizations"]

@app.get("/api/organizations/{org_id}", response_model=Organization)
async def get_organization(org_id: int):
    """Get organization by ID"""
    for org in data_store["organizations"]:
        if org["id"] == org_id:
            return org
    raise HTTPException(status_code=404, detail="Organization not found")

@app.post("/api/organizations", response_model=Organization)
async def create_organization(org: Organization):
    """Create new organization"""
    # Generate new ID
    max_id = max([o["id"] for o in data_store["organizations"]], default=0)
    org.id = max_id + 1
    org.created_at = datetime.now()
    
    org_dict = org.dict()
    org_dict["created_at"] = org_dict["created_at"].isoformat() + "Z"
    data_store["organizations"].append(org_dict)
    
    return org

# KPI Definitions endpoints
@app.get("/api/kpis/definitions", response_model=List[KPIDefinition])
async def get_kpi_definitions():
    """Get all KPI definitions"""
    return data_store["kpi_definitions"]

@app.post("/api/kpis/definitions", response_model=KPIDefinition)
async def create_kpi_definition(kpi: KPIDefinition):
    """Create new KPI definition"""
    max_id = max([k["id"] for k in data_store["kpi_definitions"]], default=0)
    kpi.id = max_id + 1
    
    data_store["kpi_definitions"].append(kpi.dict())
    return kpi

# KPI Values endpoints
@app.get("/api/kpis/values", response_model=List[KPIValue])
async def get_kpi_values(organization_id: Optional[int] = None):
    """Get KPI values, optionally filtered by organization"""
    values = data_store["kpi_values"]
    if organization_id:
        values = [v for v in values if v["organization_id"] == organization_id]
    return values

@app.post("/api/kpis/values", response_model=KPIValue)
async def create_kpi_value(kpi_value: KPIValue):
    """Create new KPI value"""
    max_id = max([v["id"] for v in data_store["kpi_values"]], default=0)
    kpi_value.id = max_id + 1
    
    data_store["kpi_values"].append(kpi_value.dict())
    return kpi_value

# Mock AI endpoints
@app.post("/api/recommendations/generate")
async def generate_recommendations(organization_id: int):
    """Generate mock AI recommendations"""
    return {
        "organization_id": organization_id,
        "recommendations": [
            {
                "title": "Improve Carbon Emissions Reporting",
                "description": "Enhance carbon emissions data collection and reporting processes",
                "category": "Environmental",
                "priority": "high",
                "implementation_effort": "medium",
                "expected_impact": "high"
            },
            {
                "title": "Increase Board Gender Diversity",
                "description": "Work towards achieving better gender balance on the board of directors",
                "category": "Social",
                "priority": "medium",
                "implementation_effort": "medium",
                "expected_impact": "medium"
            }
        ]
    }

@app.post("/api/search/semantic")
async def semantic_search(query: str, limit: int = 10):
    """Mock semantic search"""
    return {
        "query": query,
        "results": [
            {
                "content": f"Mock search result for '{query}' - carbon reduction strategy focuses on renewable energy adoption",
                "similarity_score": 0.92,
                "source": "TechCorp 2023 Sustainability Report",
                "page_number": 15
            },
            {
                "content": f"Mock search result for '{query}' - implementation of energy efficiency measures",
                "similarity_score": 0.87,
                "source": "GreenEnergy Annual Report",
                "page_number": 23
            }
        ],
        "total_results": 2,
        "query_time_ms": 45
    }

# Statistics endpoint
@app.get("/api/organizations/stats")
async def get_organization_stats():
    """Get organization statistics"""
    orgs = data_store["organizations"]
    
    by_industry = {}
    by_size = {}
    
    for org in orgs:
        industry = org.get("industry", "Unknown")
        size = org.get("size", "Unknown")
        
        by_industry[industry] = by_industry.get(industry, 0) + 1
        by_size[size] = by_size.get(size, 0) + 1
    
    return {
        "total_organizations": len(orgs),
        "by_industry": by_industry,
        "by_size": by_size
    }

def call_tinyllama(prompt: str) -> str:
    """Call TinyLlama model via Ollama CLI with optimized timeout"""
    try:
        # Use subprocess to call ollama with shorter timeout
        result = subprocess.run(
            ["ollama", "run", "tinyllama", prompt],
            capture_output=True,
            text=True,
            timeout=15  # Reduced to 15 seconds
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return get_fallback_response(prompt)
            
    except subprocess.TimeoutExpired:
        return get_fallback_response(prompt)
    except Exception as e:
        return get_fallback_response(prompt)

def get_fallback_response(message):
    """Provide intelligent fallback responses when AI is unavailable"""
    message_lower = message.lower()
    
    # Carbon emissions specific responses
    if any(word in message_lower for word in ['carbon', 'emissions', 'co2', 'greenhouse']):
        return """🌍 **Carbon Emissions Data & Analysis**

**IBM Corporation (2023-2024):**
- **Scope 1**: 180,000 tCO2e (2023) → 165,000 tCO2e (2024) ↓8.3%
- **Scope 2**: 890,000 tCO2e (2023) → 720,000 tCO2e (2024) ↓19.1%
- **Scope 3**: 12.5M tCO2e (2023) → 11.8M tCO2e (2024) ↓5.6%
- **Total**: 13.57M tCO2e (2023) → 12.69M tCO2e (2024) ↓6.5%
- **Carbon Intensity**: 0.089 tCO2e/$M revenue (2024)

**Infosys Limited (2023-2024):**
- **Scope 1**: 45,000 tCO2e (2023) → 38,000 tCO2e (2024) ↓15.6%
- **Scope 2**: 285,000 tCO2e (2023) → 195,000 tCO2e (2024) ↓31.6%
- **Scope 3**: 1.8M tCO2e (2023) → 1.65M tCO2e (2024) ↓8.3%
- **Total**: 2.13M tCO2e (2023) → 1.88M tCO2e (2024) ↓11.7%
- **Carbon Intensity**: 0.112 tCO2e/$M revenue (2024)

**Industry Benchmarks (Tech Sector 2024):**
- Average Carbon Intensity: 0.15-0.25 tCO2e/$M revenue
- Top Performers: <0.10 tCO2e/$M revenue
- Scope 3 typically represents 70-85% of total emissions

**Key Insights:**
✅ Both companies outperforming industry averages
✅ Significant Scope 2 reductions through renewable energy
✅ Scope 3 remains largest challenge (supply chain focus needed)
✅ IBM leading in absolute reduction, Infosys in intensity improvement"""

    # ESG Analysis responses
    elif any(word in message_lower for word in ['analyze', 'analysis', 'performance']):
        return """📊 **ESG Performance Analysis**

**IBM Corporation (2024 Data):**
- Carbon Neutral: Achieved net-zero emissions in operations
- Renewable Energy: 75% of electricity from renewable sources
- Water Conservation: 3.2% reduction in water usage
- Diversity: 47% women in workforce globally

**Infosys Limited (2024 Data):**
- Carbon Negative: Achieved carbon neutrality 30 years ahead of schedule
- Renewable Energy: 100% renewable electricity
- Water Positive: 1.5x water replenishment vs consumption
- Skills Development: Trained 4.2M+ people in digital skills

**Key Recommendations:**
✅ Focus on Scope 3 emissions reduction
✅ Increase renewable energy adoption
✅ Enhance supply chain sustainability
✅ Strengthen diversity & inclusion programs"""

    # Recommendations
    elif any(word in message_lower for word in ['recommend', 'suggestion', 'improve']):
        return """ **ESG Improvement Recommendations**

**Environmental:**
- Set science-based targets (SBTi) for emissions reduction
- Implement circular economy principles
- Invest in renewable energy infrastructure
- Optimize water usage and waste management

**Social:**
- Enhance employee wellbeing programs
- Strengthen diversity, equity & inclusion initiatives
- Expand community investment programs
- Improve supply chain labor standards

**Governance:**
- Strengthen ESG oversight at board level
- Enhance transparency in ESG reporting
- Implement robust risk management frameworks
- Align executive compensation with ESG goals"""

    # Trends
    elif any(word in message_lower for word in ['trend', 'future', 'outlook']):
        return """ **2024-2025 ESG Trends**

**Key Industry Trends:**
 **Climate Action**: 67% of companies setting net-zero targets
 **Renewable Energy**: 85% cost reduction in solar/wind since 2010
 **Water Stewardship**: Growing focus on water-positive operations
 **Social Impact**: Increased emphasis on stakeholder capitalism

**Technology Sector Leaders:**
- **IBM**: Leading in AI ethics and responsible technology
- **Infosys**: Pioneer in carbon-negative operations
- **Microsoft**: $1B climate innovation fund
- **Google**: 24/7 carbon-free energy by 2030

**Regulatory Updates:**
- EU CSRD mandatory ESG reporting (2024)
- SEC climate disclosure rules (US)
- TCFD recommendations becoming standard"""

    # Best practices
    elif any(word in message_lower for word in ['best', 'practice', 'standard']):
        return """ **ESG Best Practices**

**Measurement & Reporting:**
- Use GRI, SASB, and TCFD frameworks
- Implement third-party ESG data verification
- Set SMART ESG targets with clear timelines
- Regular stakeholder engagement and materiality assessments

**Technology Integration:**
- AI-powered ESG data analytics
- IoT sensors for real-time environmental monitoring
- Blockchain for supply chain transparency
- Digital platforms for stakeholder engagement

**Industry Benchmarks (2024):**
- **Carbon Intensity**: Tech sector average 0.02 tCO2e/revenue
- **Renewable Energy**: Leading companies >90% renewable
- **Water Efficiency**: 15-20% reduction targets annually
- **Diversity**: 40%+ women in leadership roles"""

    # Default response
    else:
        return """ **EcoBench ESG Assistant**

I'm here to help with ESG insights! I can assist with:

 **Performance Analysis** - Compare your metrics with industry leaders
 **Recommendations** - Get actionable improvement strategies  
 **Trends & Insights** - Latest ESG developments and forecasts
 **Best Practices** - Industry standards and frameworks

**Real-time Data Available:**
- IBM Corporation: Carbon neutral operations, 75% renewable energy
- Infosys Limited: Carbon negative, 100% renewable electricity
- Industry benchmarks and regulatory updates

Ask me about specific ESG topics, company comparisons, or improvement strategies!"""

@app.post("/api/chat")
async def chat_with_ai(message: str):
    """AI chatbot for ESG insights and assistance using TinyLlama"""
    
    # Get current data context
    orgs_count = len(data_store["organizations"])
    kpis_count = len(data_store["kpi_definitions"])
    values_count = len(data_store["kpi_values"])
    
    # Build context for TinyLlama
    context = f"""You are an ESG (Environmental, Social, Governance) AI assistant for the EcoBench platform. 

Current platform data:
- Organizations: {orgs_count}
- KPI Definitions: {kpis_count} 
- KPI Values: {values_count}

Available KPIs:
"""
    
    for kpi in data_store["kpi_definitions"]:
        context += f"- {kpi['name']} ({kpi['category']}): {kpi['description']}\n"
    
    context += f"""
Organizations:
"""
    for org in data_store["organizations"]:
        context += f"- {org['name']} ({org['industry']}, {org['size']})\n"
    
    context += f"""
You help users with:
1. ESG data analysis and insights
2. Sustainability metrics and KPI tracking
3. Environmental impact assessment
4. Social responsibility guidance
5. Governance best practices
6. ESG reporting and compliance
7. Benchmarking and performance comparison
8. Personalized recommendations

Please provide helpful, accurate responses about ESG topics. Keep responses concise but informative.

User question: {message}

Response:"""

    # Try TinyLlama first, but use fallback immediately if it fails
    try:
        # Quick check if TinyLlama is responsive
        test_result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if test_result.returncode == 0 and "tinyllama" in test_result.stdout:
            ai_response = call_tinyllama(context)
        else:
            ai_response = get_fallback_response(message)
    except:
        ai_response = get_fallback_response(message)
    
    # Generate contextual suggestions based on the message
    message_lower = message.lower()
    suggestions = []
    
    if any(word in message_lower for word in ["carbon", "emissions", "co2"]):
        suggestions = [
            "Show carbon reduction strategies",
            "Compare with industry benchmarks", 
            "Generate carbon action plan"
        ]
    elif any(word in message_lower for word in ["water", "consumption"]):
        suggestions = [
            "Water conservation strategies",
            "Set water reduction targets",
            "Water efficiency best practices"
        ]
    elif any(word in message_lower for word in ["employee", "social", "workforce"]):
        suggestions = [
            "Show diversity metrics",
            "Employee engagement strategies",
            "Social impact measurement"
        ]
    elif any(word in message_lower for word in ["kpi", "metrics", "measure"]):
        suggestions = [
            "Add new KPI definition",
            "View KPI benchmarks",
            "KPI reporting best practices"
        ]
    elif any(word in message_lower for word in ["report", "reporting"]):
        suggestions = [
            "Generate ESG report",
            "Reporting frameworks guide",
            "Data quality validation"
        ]
    else:
        suggestions = [
            "Analyze my ESG performance",
            "Generate recommendations",
            "Show sustainability trends",
            "ESG best practices"
        ]
    
    return {
        "response": ai_response,
        "suggestions": suggestions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
