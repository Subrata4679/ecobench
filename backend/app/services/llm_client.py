from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import logging
import time
import re
from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def extract_kpis_from_chunk(self, text_chunk: str, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract KPIs from text chunk"""
        pass
    
    @abstractmethod
    async def generate_guidance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable guidance"""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        pass


class MockLLMClient(LLMClient):
    """Mock LLM client for testing and development"""
    
    async def extract_kpis_from_chunk(self, text_chunk: str, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Mock KPI extraction"""
        org = ctx.get("org", "Unknown")
        year = ctx.get("year", 2023)
        
        # Simple regex-based mock extraction
        mock_extractions = []
        
        # Look for scope emissions patterns
        scope_patterns = {
            "SCOPE1": r"scope\s*1.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?|metric\s*tons?\s*co2e?)",
            "SCOPE2": r"scope\s*2.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?|metric\s*tons?\s*co2e?)",
            "SCOPE3": r"scope\s*3.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?|metric\s*tons?\s*co2e?)"
        }
        
        for kpi_code, pattern in scope_patterns.items():
            matches = re.finditer(pattern, text_chunk.lower())
            for match in matches:
                value_str = match.group(1).replace(",", "")
                try:
                    value = float(value_str)
                    mock_extractions.append({
                        "kpiCode": kpi_code,
                        "value": value,
                        "unit": "tCO2e",
                        "year": year,
                        "confidence": 0.7,
                        "evidenceStart": match.start(),
                        "evidenceEnd": match.end(),
                        "pageNumber": 1
                    })
                except ValueError:
                    continue
        
        # Mock water withdrawal
        water_pattern = r"water.*?withdrawal.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(m3|cubic\s*meters?|megalit)"
        matches = re.finditer(water_pattern, text_chunk.lower())
        for match in matches:
            value_str = match.group(1).replace(",", "")
            try:
                value = float(value_str)
                mock_extractions.append({
                    "kpiCode": "WATER_WITHDRAWAL",
                    "value": value,
                    "unit": "m3",
                    "year": year,
                    "confidence": 0.6,
                    "evidenceStart": match.start(),
                    "evidenceEnd": match.end(),
                    "pageNumber": 1
                })
            except ValueError:
                continue
        
        return mock_extractions
    
    async def generate_guidance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock guidance generation"""
        org = context.get("org", "Unknown Organization")
        kpi = context.get("kpi", {})
        kpi_code = kpi.get("code", "UNKNOWN")
        percentile = kpi.get("percentile", 50)
        
        # Generate mock recommendations based on percentile
        if percentile < 25:
            effort = "low"
            impact = "Significant improvement potential"
        elif percentile < 50:
            effort = "medium"
            impact = "Moderate improvement opportunity"
        else:
            effort = "high"
            impact = "Maintain leadership position"
        
        return {
            "title": f"Improve {kpi_code} Performance for {org}",
            "rationale": f"Based on peer analysis, {org} is at the {percentile}th percentile for {kpi_code}. This presents opportunities for improvement through targeted initiatives.",
            "actions": [
                {
                    "step": f"Conduct detailed {kpi_code} audit",
                    "impact": impact,
                    "effort": effort,
                    "owner": "Sustainability Team",
                    "timeframe": "3-6 months"
                },
                {
                    "step": "Implement monitoring and tracking system",
                    "impact": "Enhanced visibility and control",
                    "effort": "medium",
                    "owner": "Operations Team",
                    "timeframe": "6-12 months"
                }
            ],
            "sources": [
                {
                    "org": "Industry Leader",
                    "report": "Sustainability Report 2023",
                    "page": 15,
                    "url": "https://example.com/report"
                }
            ],
            "confidence": 0.75
        }
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Mock embedding generation"""
        import numpy as np
        embeddings = []
        for text in texts:
            # Generate deterministic mock embeddings based on text hash
            np.random.seed(hash(text) % (2**32))
            embedding = np.random.normal(0, 1, settings.embedding_dimension).tolist()
            embeddings.append(embedding)
        return embeddings


class TinyLlamaClient(LLMClient):
    """TinyLlama local LLM client"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.embedding_model = None
        self._load_models()
    
    def _load_models(self):
        """Load TinyLlama models"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            from sentence_transformers import SentenceTransformer
            
            # Load TinyLlama for text generation
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            logger.info(f"Loading TinyLlama model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            
            # Load sentence transformer for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("TinyLlama models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load TinyLlama models: {e}")
            logger.info("Falling back to mock client")
            self.model = None
            self.tokenizer = None
            self.embedding_model = None
    
    async def extract_kpis_from_chunk(self, text_chunk: str, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract KPIs using TinyLlama"""
        if not self.model or not self.tokenizer:
            # Fallback to mock
            mock_client = MockLLMClient()
            return await mock_client.extract_kpis_from_chunk(text_chunk, ctx)
        
        org = ctx.get("org", "Unknown")
        year = ctx.get("year", 2023)
        
        # Prepare extraction prompt
        prompt = f"""You are an extractor. Input: {{"org":"{org}","year":{year},"text":"{text_chunk[:1000]}"}}
Return only valid JSON array of objects:
[ {{"kpiCode":"SCOPE1","value":1234.0,"unit":"tCO2e","year":2023,"confidence":0.95,"evidenceStart":10,"evidenceEnd":120,"pageNumber":4}}, ... ]
Do NOT add extra text."""
        
        try:
            # Generate response
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=512,
                    temperature=0.1,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response[len(prompt):].strip()
            
            # Parse JSON response
            try:
                extracted_kpis = json.loads(response)
                return extracted_kpis if isinstance(extracted_kpis, list) else []
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM JSON response, falling back to regex")
                # Fallback to mock extraction
                mock_client = MockLLMClient()
                return await mock_client.extract_kpis_from_chunk(text_chunk, ctx)
                
        except Exception as e:
            logger.error(f"TinyLlama extraction failed: {e}")
            # Fallback to mock
            mock_client = MockLLMClient()
            return await mock_client.extract_kpis_from_chunk(text_chunk, ctx)
    
    async def generate_guidance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate guidance using TinyLlama"""
        if not self.model or not self.tokenizer:
            # Fallback to mock
            mock_client = MockLLMClient()
            return await mock_client.generate_guidance(context)
        
        org = context.get("org", "Unknown")
        kpi = context.get("kpi", {})
        leaders = context.get("leaders", [])
        
        # Prepare guidance prompt
        prompt = f"""You are a sustainability strategist. Input JSON: {json.dumps(context)[:1000]}
Return only JSON:
{{ "title":"...", "rationale":"...", "actions":[{{"step":"...","impact":"...","effort":"low|medium|high","owner":"Team","timeframe":"3-12 months"}}], "sources":[{{"org":"C1","report":"CSR 2023","page":12,"url":"..."}}], "confidence":0.0-1.0 }}"""
        
        try:
            # Generate response
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=1024,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response[len(prompt):].strip()
            
            # Parse JSON response
            try:
                guidance = json.loads(response)
                return guidance
            except json.JSONDecodeError:
                logger.warning("Failed to parse guidance JSON, falling back to mock")
                mock_client = MockLLMClient()
                return await mock_client.generate_guidance(context)
                
        except Exception as e:
            logger.error(f"TinyLlama guidance generation failed: {e}")
            mock_client = MockLLMClient()
            return await mock_client.generate_guidance(context)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence transformer"""
        if not self.embedding_model:
            # Fallback to mock
            mock_client = MockLLMClient()
            return await mock_client.generate_embeddings(texts)
        
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            mock_client = MockLLMClient()
            return await mock_client.generate_embeddings(texts)


class OpenAIClient(LLMClient):
    """OpenAI LLM client"""
    
    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    async def extract_kpis_from_chunk(self, text_chunk: str, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract KPIs using OpenAI"""
        if not self.client:
            # Fallback to mock
            mock_client = MockLLMClient()
            return await mock_client.extract_kpis_from_chunk(text_chunk, ctx)
        
        org = ctx.get("org", "Unknown")
        year = ctx.get("year", 2023)
        
        prompt = f"""You are an extractor. Input: {{"org":"{org}","year":{year},"text":"{text_chunk[:2000]}"}}
Return only valid JSON array of objects:
[ {{"kpiCode":"SCOPE1","value":1234.0,"unit":"tCO2e","year":2023,"confidence":0.95,"evidenceStart":10,"evidenceEnd":120,"pageNumber":4}}, ... ]
Do NOT add extra text."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1024
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                extracted_kpis = json.loads(content)
                return extracted_kpis if isinstance(extracted_kpis, list) else []
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI JSON response")
                mock_client = MockLLMClient()
                return await mock_client.extract_kpis_from_chunk(text_chunk, ctx)
                
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            mock_client = MockLLMClient()
            return await mock_client.extract_kpis_from_chunk(text_chunk, ctx)
    
    async def generate_guidance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate guidance using OpenAI"""
        if not self.client:
            mock_client = MockLLMClient()
            return await mock_client.generate_guidance(context)
        
        prompt = f"""You are a sustainability strategist. Input JSON: {json.dumps(context, indent=2)[:2000]}
Return only JSON:
{{ "title":"...", "rationale":"...", "actions":[{{"step":"...","impact":"...","effort":"low|medium|high","owner":"Team","timeframe":"3-12 months"}}], "sources":[{{"org":"C1","report":"CSR 2023","page":12,"url":"..."}}], "confidence":0.0-1.0 }}"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                guidance = json.loads(content)
                return guidance
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI guidance JSON")
                mock_client = MockLLMClient()
                return await mock_client.generate_guidance(context)
                
        except Exception as e:
            logger.error(f"OpenAI guidance generation failed: {e}")
            mock_client = MockLLMClient()
            return await mock_client.generate_guidance(context)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        if not self.client:
            mock_client = MockLLMClient()
            return await mock_client.generate_embeddings(texts)
        
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}")
            mock_client = MockLLMClient()
            return await mock_client.generate_embeddings(texts)


# Factory function to get appropriate LLM client
def get_llm_client() -> LLMClient:
    """Get LLM client based on configuration"""
    provider = settings.llm_provider.lower()
    
    if provider == "openai" and settings.openai_api_key:
        return OpenAIClient()
    elif provider == "tinyllama":
        return TinyLlamaClient()
    else:
        logger.info("Using mock LLM client")
        return MockLLMClient()


# Global client instance
_llm_client = None

def get_llm_client_instance() -> LLMClient:
    """Get singleton LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = get_llm_client()
    return _llm_client
