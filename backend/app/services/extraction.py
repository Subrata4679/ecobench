import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import asyncio

from app.models import KPIDefinition, KPIValue, Report, Organization, Embedding
from app.services.llm_client import get_llm_client_instance
from app.config import settings

logger = logging.getLogger(__name__)


class ExtractionService:
    """Hybrid extraction service using regex heuristics + LLM"""
    
    def __init__(self):
        self.llm_client = get_llm_client_instance()
        self.regex_patterns = self._initialize_regex_patterns()
    
    def _initialize_regex_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize regex patterns for common KPI extraction"""
        return {
            "SCOPE1": [
                {
                    "pattern": r"scope\s*1.*?emissions?.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?|metric\s*tons?\s*co2e?)",
                    "confidence": 0.8,
                    "unit_mapping": {"tco2e": "tCO2e", "tonnes co2e": "tCO2e", "metric tons co2e": "tCO2e"}
                },
                {
                    "pattern": r"direct.*?emissions?.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?)",
                    "confidence": 0.7,
                    "unit_mapping": {"tco2e": "tCO2e", "tonnes co2e": "tCO2e"}
                }
            ],
            "SCOPE2": [
                {
                    "pattern": r"scope\s*2.*?emissions?.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?|metric\s*tons?\s*co2e?)",
                    "confidence": 0.8,
                    "unit_mapping": {"tco2e": "tCO2e", "tonnes co2e": "tCO2e", "metric tons co2e": "tCO2e"}
                },
                {
                    "pattern": r"indirect.*?energy.*?emissions?.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?)",
                    "confidence": 0.7,
                    "unit_mapping": {"tco2e": "tCO2e", "tonnes co2e": "tCO2e"}
                }
            ],
            "SCOPE3": [
                {
                    "pattern": r"scope\s*3.*?emissions?.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?|metric\s*tons?\s*co2e?)",
                    "confidence": 0.8,
                    "unit_mapping": {"tco2e": "tCO2e", "tonnes co2e": "tCO2e", "metric tons co2e": "tCO2e"}
                },
                {
                    "pattern": r"other.*?indirect.*?emissions?.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tco2e?|tonnes?\s*co2e?)",
                    "confidence": 0.6,
                    "unit_mapping": {"tco2e": "tCO2e", "tonnes co2e": "tCO2e"}
                }
            ],
            "WATER_WITHDRAWAL": [
                {
                    "pattern": r"water.*?withdrawal.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(m3|cubic\s*meters?|megalit|ml)",
                    "confidence": 0.8,
                    "unit_mapping": {"m3": "m3", "cubic meters": "m3", "megalit": "ML", "ml": "ML"}
                },
                {
                    "pattern": r"total.*?water.*?consumption.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(m3|cubic\s*meters?|megalit)",
                    "confidence": 0.7,
                    "unit_mapping": {"m3": "m3", "cubic meters": "m3", "megalit": "ML"}
                }
            ],
            "WASTE_GENERATED": [
                {
                    "pattern": r"waste.*?generated.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tonnes?|tons?|kg|mt)",
                    "confidence": 0.8,
                    "unit_mapping": {"tonnes": "tonnes", "tons": "tonnes", "kg": "kg", "mt": "tonnes"}
                },
                {
                    "pattern": r"total.*?waste.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(tonnes?|tons?|kg)",
                    "confidence": 0.7,
                    "unit_mapping": {"tonnes": "tonnes", "tons": "tonnes", "kg": "kg"}
                }
            ],
            "ENERGY_INTENSITY": [
                {
                    "pattern": r"energy.*?intensity.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(mj\/\$|kwh\/\$|gj\/\$)",
                    "confidence": 0.8,
                    "unit_mapping": {"mj/$": "MJ/$", "kwh/$": "kWh/$", "gj/$": "GJ/$"}
                }
            ],
            "RENEWABLE_SHARE": [
                {
                    "pattern": r"renewable.*?energy.*?(\d+(?:\.\d+)?)\s*(%|percent)",
                    "confidence": 0.8,
                    "unit_mapping": {"%": "%", "percent": "%"}
                }
            ]
        }
    
    def extract_with_regex(self, text: str, kpi_code: str, year: int) -> List[Dict[str, Any]]:
        """Extract KPI values using regex patterns"""
        extractions = []
        patterns = self.regex_patterns.get(kpi_code, [])
        
        for pattern_info in patterns:
            pattern = pattern_info["pattern"]
            confidence = pattern_info["confidence"]
            unit_mapping = pattern_info["unit_mapping"]
            
            matches = re.finditer(pattern, text.lower(), re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                try:
                    # Extract numeric value
                    value_str = match.group(1).replace(",", "")
                    value = float(value_str)
                    
                    # Extract and normalize unit
                    unit_raw = match.group(2).lower().strip()
                    unit = unit_mapping.get(unit_raw, unit_raw)
                    
                    extraction = {
                        "kpiCode": kpi_code,
                        "value": value,
                        "unit": unit,
                        "year": year,
                        "confidence": confidence,
                        "evidenceStart": match.start(),
                        "evidenceEnd": match.end(),
                        "pageNumber": None,  # Will be determined from chunk metadata
                        "extractionMethod": "regex"
                    }
                    
                    extractions.append(extraction)
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse regex match for {kpi_code}: {e}")
                    continue
        
        return extractions
    
    async def extract_with_llm(self, text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract KPI values using LLM"""
        try:
            extractions = await self.llm_client.extract_kpis_from_chunk(text, context)
            
            # Add extraction method to results
            for extraction in extractions:
                extraction["extractionMethod"] = "llm"
            
            return extractions
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return []
    
    def merge_extractions(self, regex_results: List[Dict[str, Any]], 
                         llm_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate extraction results from regex and LLM"""
        merged = []
        
        # Start with regex results (typically more reliable for structured data)
        for regex_result in regex_results:
            merged.append(regex_result)
        
        # Add LLM results that don't conflict with regex results
        for llm_result in llm_results:
            # Check for conflicts with existing results
            conflict_found = False
            
            for existing in merged:
                # Consider it a conflict if same KPI, similar value, and overlapping evidence
                if (existing["kpiCode"] == llm_result["kpiCode"] and
                    abs(existing.get("value", 0) - llm_result.get("value", 0)) < existing.get("value", 1) * 0.1 and
                    self._evidence_overlaps(existing, llm_result)):
                    
                    # Keep the result with higher confidence
                    if llm_result.get("confidence", 0) > existing.get("confidence", 0):
                        merged.remove(existing)
                        merged.append(llm_result)
                    
                    conflict_found = True
                    break
            
            if not conflict_found:
                merged.append(llm_result)
        
        return merged
    
    def _evidence_overlaps(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> bool:
        """Check if two extraction results have overlapping evidence spans"""
        start1 = result1.get("evidenceStart", 0)
        end1 = result1.get("evidenceEnd", 0)
        start2 = result2.get("evidenceStart", 0)
        end2 = result2.get("evidenceEnd", 0)
        
        # Check for overlap
        return not (end1 <= start2 or end2 <= start1)
    
    async def extract_from_chunk(self, chunk_text: str, context: Dict[str, Any], 
                                target_kpis: List[str] = None) -> List[Dict[str, Any]]:
        """
        Extract KPIs from a text chunk using hybrid approach
        
        Args:
            chunk_text: Text to extract from
            context: Context information (org, year, etc.)
            target_kpis: List of KPI codes to extract (if None, extract all)
        
        Returns:
            List of extracted KPI values
        """
        if target_kpis is None:
            target_kpis = list(self.regex_patterns.keys())
        
        year = context.get("year", 2023)
        all_extractions = []
        
        # 1. Extract using regex patterns
        regex_extractions = []
        for kpi_code in target_kpis:
            kpi_regex_results = self.extract_with_regex(chunk_text, kpi_code, year)
            regex_extractions.extend(kpi_regex_results)
        
        # 2. Extract using LLM
        llm_extractions = await self.extract_with_llm(chunk_text, context)
        
        # 3. Merge results
        merged_extractions = self.merge_extractions(regex_extractions, llm_extractions)
        
        logger.info(f"Extracted {len(regex_extractions)} regex + {len(llm_extractions)} LLM = {len(merged_extractions)} merged KPIs")
        
        return merged_extractions
    
    async def extract_from_report(self, db: Session, report_id: int, 
                                 target_kpis: List[str] = None) -> Dict[str, Any]:
        """
        Extract KPIs from all chunks of a report
        
        Args:
            db: Database session
            report_id: Report ID to process
            target_kpis: List of KPI codes to extract
        
        Returns:
            Extraction results summary
        """
        # Get report and organization info
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"success": False, "error": "Report not found"}
        
        organization = db.query(Organization).filter(Organization.id == report.organization_id).first()
        
        # Get all embeddings (chunks) for the report
        embeddings = db.query(Embedding).filter(Embedding.report_id == report_id).all()
        
        if not embeddings:
            return {"success": False, "error": "No text chunks found for report"}
        
        context = {
            "org": organization.name if organization else "Unknown",
            "year": report.year,
            "report_title": report.title
        }
        
        all_extractions = []
        
        # Process each chunk
        for embedding in embeddings:
            chunk_extractions = await self.extract_from_chunk(
                embedding.chunk_text, context, target_kpis
            )
            
            # Add chunk metadata to extractions
            for extraction in chunk_extractions:
                extraction["chunk_id"] = embedding.id
                extraction["report_id"] = report_id
                
                # Try to determine page number from metadata
                if embedding.metadata and "page_info" in embedding.metadata:
                    page_info = embedding.metadata["page_info"]
                    if isinstance(page_info, list) and page_info:
                        extraction["pageNumber"] = page_info[0].get("page_number", 1)
            
            all_extractions.extend(chunk_extractions)
        
        # Group extractions by KPI code for summary
        kpi_summary = {}
        for extraction in all_extractions:
            kpi_code = extraction["kpiCode"]
            if kpi_code not in kpi_summary:
                kpi_summary[kpi_code] = []
            kpi_summary[kpi_code].append(extraction)
        
        return {
            "success": True,
            "report_id": report_id,
            "total_extractions": len(all_extractions),
            "kpi_summary": kpi_summary,
            "extractions": all_extractions,
            "chunks_processed": len(embeddings)
        }
    
    async def save_extractions_to_db(self, db: Session, extractions: List[Dict[str, Any]]) -> List[KPIValue]:
        """
        Save extracted KPI values to database
        
        Args:
            db: Database session
            extractions: List of extraction results
        
        Returns:
            List of created KPIValue records
        """
        kpi_values = []
        
        for extraction in extractions:
            # Get KPI definition
            kpi_def = db.query(KPIDefinition).filter(
                KPIDefinition.code == extraction["kpiCode"]
            ).first()
            
            if not kpi_def:
                logger.warning(f"KPI definition not found for code: {extraction['kpiCode']}")
                continue
            
            # Create KPI value record
            kpi_value = KPIValue(
                organization_id=extraction.get("organization_id"),
                kpi_id=kpi_def.id,
                report_id=extraction.get("report_id"),
                year=extraction["year"],
                value_numeric=extraction.get("value"),
                unit=extraction.get("unit"),
                confidence=extraction.get("confidence"),
                extraction_method=extraction.get("extractionMethod", "hybrid"),
                evidence_span={
                    "start": extraction.get("evidenceStart"),
                    "end": extraction.get("evidenceEnd"),
                    "page_number": extraction.get("pageNumber"),
                    "chunk_id": extraction.get("chunk_id")
                }
            )
            
            kpi_values.append(kpi_value)
        
        # Bulk insert
        db.add_all(kpi_values)
        db.commit()
        
        logger.info(f"Saved {len(kpi_values)} KPI values to database")
        return kpi_values
    
    def normalize_units(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """
        Normalize units to base units
        
        Args:
            value: Numeric value
            from_unit: Source unit
            to_unit: Target unit
        
        Returns:
            Normalized value or None if conversion not supported
        """
        # Define conversion factors to base units
        conversions = {
            # CO2 emissions (to tCO2e)
            "tCO2e": {"tCO2e": 1.0, "tonnes CO2e": 1.0, "metric tons CO2e": 1.0, "kg CO2e": 0.001},
            
            # Water (to m3)
            "m3": {"m3": 1.0, "cubic meters": 1.0, "ML": 1000.0, "megalit": 1000.0, "L": 0.001},
            
            # Waste (to tonnes)
            "tonnes": {"tonnes": 1.0, "tons": 1.0, "kg": 0.001, "mt": 1.0},
            
            # Energy intensity (normalize to MJ/$)
            "MJ/$": {"MJ/$": 1.0, "kWh/$": 3.6, "GJ/$": 1000.0},
            
            # Percentage
            "%": {"%": 1.0, "percent": 1.0}
        }
        
        if to_unit in conversions and from_unit in conversions[to_unit]:
            return value * conversions[to_unit][from_unit]
        
        return None


# Global service instance
_extraction_service = None

def get_extraction_service() -> ExtractionService:
    """Get singleton extraction service instance"""
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service
