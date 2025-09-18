import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import statistics
from datetime import datetime

from app.models import (
    Organization, KPIValue, KPIDefinition, PeerGroup, 
    BenchmarkSnapshot, Report
)
from app.schemas import BenchmarkStats

logger = logging.getLogger(__name__)


class BenchmarkService:
    """Service for peer benchmarking and performance analysis"""
    
    def __init__(self):
        pass
    
    def create_peer_group(self, db: Session, name: str, criteria: Dict[str, Any]) -> PeerGroup:
        """
        Create a new peer group with specified criteria
        
        Args:
            db: Database session
            name: Name of the peer group
            criteria: Selection criteria (sector, country, size, etc.)
        
        Returns:
            Created PeerGroup instance
        """
        peer_group = PeerGroup(name=name, criteria=criteria)
        db.add(peer_group)
        db.commit()
        db.refresh(peer_group)
        
        logger.info(f"Created peer group '{name}' with criteria: {criteria}")
        return peer_group
    
    def get_peer_organizations(self, db: Session, criteria: Dict[str, Any]) -> List[Organization]:
        """
        Get organizations matching peer group criteria
        
        Args:
            db: Database session
            criteria: Selection criteria
        
        Returns:
            List of matching organizations
        """
        query = db.query(Organization)
        
        # Apply filters based on criteria
        if "sector" in criteria:
            sectors = criteria["sector"] if isinstance(criteria["sector"], list) else [criteria["sector"]]
            query = query.filter(Organization.sector.in_(sectors))
        
        if "country" in criteria:
            countries = criteria["country"] if isinstance(criteria["country"], list) else [criteria["country"]]
            query = query.filter(Organization.country.in_(countries))
        
        if "exclude_org_ids" in criteria:
            exclude_ids = criteria["exclude_org_ids"]
            query = query.filter(~Organization.id.in_(exclude_ids))
        
        # Size-based filtering could be added here based on revenue, employees, etc.
        # This would require additional organization metadata
        
        organizations = query.all()
        logger.info(f"Found {len(organizations)} organizations matching criteria")
        return organizations
    
    def calculate_benchmark_stats(self, values: List[float]) -> BenchmarkStats:
        """
        Calculate statistical benchmarks from a list of values
        
        Args:
            values: List of numeric values
        
        Returns:
            BenchmarkStats with percentiles and statistics
        """
        if not values:
            return BenchmarkStats(count=0)
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        stats = BenchmarkStats(
            min_value=min(sorted_values),
            max_value=max(sorted_values),
            count=count
        )
        
        if count >= 1:
            stats.median = statistics.median(sorted_values)
        
        if count >= 4:
            # Calculate quartiles
            stats.p25 = statistics.quantiles(sorted_values, n=4)[0]  # 25th percentile
            stats.p75 = statistics.quantiles(sorted_values, n=4)[2]  # 75th percentile
        
        return stats
    
    def create_benchmark_snapshot(self, db: Session, peer_group_id: int, 
                                 kpi_id: int, period: str) -> Optional[BenchmarkSnapshot]:
        """
        Create a benchmark snapshot for a peer group and KPI
        
        Args:
            db: Database session
            peer_group_id: ID of the peer group
            kpi_id: ID of the KPI
            period: Time period (e.g., "2023", "2022-2023")
        
        Returns:
            Created BenchmarkSnapshot or None if insufficient data
        """
        # Get peer group and criteria
        peer_group = db.query(PeerGroup).filter(PeerGroup.id == peer_group_id).first()
        if not peer_group:
            logger.error(f"Peer group {peer_group_id} not found")
            return None
        
        # Get organizations in peer group
        peer_orgs = self.get_peer_organizations(db, peer_group.criteria)
        if len(peer_orgs) < 3:  # Minimum peers for meaningful benchmark
            logger.warning(f"Insufficient peers ({len(peer_orgs)}) for benchmark")
            return None
        
        org_ids = [org.id for org in peer_orgs]
        
        # Parse period to get year range
        if "-" in period:
            start_year, end_year = map(int, period.split("-"))
            year_filter = and_(KPIValue.year >= start_year, KPIValue.year <= end_year)
        else:
            year = int(period)
            year_filter = KPIValue.year == year
        
        # Get KPI values for peer organizations in the period
        kpi_values = db.query(KPIValue).filter(
            and_(
                KPIValue.organization_id.in_(org_ids),
                KPIValue.kpi_id == kpi_id,
                year_filter,
                KPIValue.value_numeric.isnot(None)
            )
        ).all()
        
        if len(kpi_values) < 3:
            logger.warning(f"Insufficient KPI values ({len(kpi_values)}) for benchmark")
            return None
        
        # Extract numeric values
        values = [kv.value_numeric for kv in kpi_values if kv.value_numeric is not None]
        
        # Calculate statistics
        stats = self.calculate_benchmark_stats(values)
        
        # Create or update benchmark snapshot
        existing_snapshot = db.query(BenchmarkSnapshot).filter(
            and_(
                BenchmarkSnapshot.peer_group_id == peer_group_id,
                BenchmarkSnapshot.kpi_id == kpi_id,
                BenchmarkSnapshot.period == period
            )
        ).first()
        
        if existing_snapshot:
            existing_snapshot.stats = stats.dict()
            existing_snapshot.created_at = datetime.now()
            snapshot = existing_snapshot
        else:
            snapshot = BenchmarkSnapshot(
                peer_group_id=peer_group_id,
                kpi_id=kpi_id,
                period=period,
                stats=stats.dict()
            )
            db.add(snapshot)
        
        db.commit()
        db.refresh(snapshot)
        
        logger.info(f"Created benchmark snapshot for peer group {peer_group_id}, KPI {kpi_id}, period {period}")
        return snapshot
    
    def get_organization_percentile(self, db: Session, organization_id: int, 
                                   kpi_id: int, period: str, 
                                   peer_group_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Calculate an organization's percentile ranking for a KPI
        
        Args:
            db: Database session
            organization_id: Organization to analyze
            kpi_id: KPI to analyze
            period: Time period
            peer_group_id: Optional specific peer group
        
        Returns:
            Dictionary with percentile, rank, and benchmark data
        """
        # Get organization's KPI value
        if "-" in period:
            start_year, end_year = map(int, period.split("-"))
            year_filter = and_(KPIValue.year >= start_year, KPIValue.year <= end_year)
        else:
            year = int(period)
            year_filter = KPIValue.year == year
        
        org_value = db.query(KPIValue).filter(
            and_(
                KPIValue.organization_id == organization_id,
                KPIValue.kpi_id == kpi_id,
                year_filter,
                KPIValue.value_numeric.isnot(None)
            )
        ).first()
        
        if not org_value:
            return {"error": "Organization KPI value not found"}
        
        # Determine peer group
        if peer_group_id:
            peer_group = db.query(PeerGroup).filter(PeerGroup.id == peer_group_id).first()
            if not peer_group:
                return {"error": "Peer group not found"}
            
            peer_orgs = self.get_peer_organizations(db, peer_group.criteria)
        else:
            # Use sector-based peer group
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org or not org.sector:
                return {"error": "Organization or sector not found"}
            
            peer_orgs = self.get_peer_organizations(db, {"sector": org.sector})
        
        org_ids = [org.id for org in peer_orgs]
        
        # Get all peer KPI values
        peer_values = db.query(KPIValue).filter(
            and_(
                KPIValue.organization_id.in_(org_ids),
                KPIValue.kpi_id == kpi_id,
                year_filter,
                KPIValue.value_numeric.isnot(None)
            )
        ).all()
        
        if len(peer_values) < 3:
            return {"error": "Insufficient peer data"}
        
        # Calculate percentile
        values = [pv.value_numeric for pv in peer_values]
        org_val = org_value.value_numeric
        
        # Determine if higher is better
        kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == kpi_id).first()
        is_higher_better = kpi_def.is_higher_better if kpi_def else False
        
        if is_higher_better:
            # For metrics where higher is better (e.g., renewable energy %)
            percentile = (sum(1 for v in values if v <= org_val) / len(values)) * 100
        else:
            # For metrics where lower is better (e.g., emissions)
            percentile = (sum(1 for v in values if v >= org_val) / len(values)) * 100
        
        # Calculate rank
        sorted_values = sorted(values, reverse=is_higher_better)
        try:
            rank = sorted_values.index(org_val) + 1
        except ValueError:
            rank = None
        
        # Get benchmark stats
        stats = self.calculate_benchmark_stats(values)
        
        return {
            "organization_id": organization_id,
            "kpi_id": kpi_id,
            "period": period,
            "organization_value": org_val,
            "percentile": round(percentile, 1),
            "rank": rank,
            "total_peers": len(values),
            "benchmark_stats": stats.dict(),
            "is_higher_better": is_higher_better
        }
    
    def get_top_performers(self, db: Session, kpi_id: int, period: str, 
                          peer_group_id: Optional[int] = None, 
                          limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top performing organizations for a KPI
        
        Args:
            db: Database session
            kpi_id: KPI to analyze
            period: Time period
            peer_group_id: Optional peer group filter
            limit: Number of top performers to return
        
        Returns:
            List of top performer data
        """
        # Parse period
        if "-" in period:
            start_year, end_year = map(int, period.split("-"))
            year_filter = and_(KPIValue.year >= start_year, KPIValue.year <= end_year)
        else:
            year = int(period)
            year_filter = KPIValue.year == year
        
        # Get KPI definition to determine sort order
        kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == kpi_id).first()
        is_higher_better = kpi_def.is_higher_better if kpi_def else False
        
        # Build query
        query = db.query(KPIValue, Organization).join(
            Organization, KPIValue.organization_id == Organization.id
        ).filter(
            and_(
                KPIValue.kpi_id == kpi_id,
                year_filter,
                KPIValue.value_numeric.isnot(None)
            )
        )
        
        # Apply peer group filter if specified
        if peer_group_id:
            peer_group = db.query(PeerGroup).filter(PeerGroup.id == peer_group_id).first()
            if peer_group:
                peer_orgs = self.get_peer_organizations(db, peer_group.criteria)
                org_ids = [org.id for org in peer_orgs]
                query = query.filter(Organization.id.in_(org_ids))
        
        # Sort by performance
        if is_higher_better:
            query = query.order_by(KPIValue.value_numeric.desc())
        else:
            query = query.order_by(KPIValue.value_numeric.asc())
        
        results = query.limit(limit).all()
        
        top_performers = []
        for kpi_value, org in results:
            top_performers.append({
                "organization_id": org.id,
                "organization_name": org.name,
                "sector": org.sector,
                "country": org.country,
                "value": kpi_value.value_numeric,
                "unit": kpi_value.unit,
                "year": kpi_value.year,
                "confidence": kpi_value.confidence
            })
        
        return top_performers
    
    def compare_organizations(self, db: Session, org_ids: List[int], 
                             kpi_id: int, period: str) -> Dict[str, Any]:
        """
        Compare multiple organizations on a specific KPI
        
        Args:
            db: Database session
            org_ids: List of organization IDs to compare
            kpi_id: KPI to compare
            period: Time period
        
        Returns:
            Comparison data
        """
        # Parse period
        if "-" in period:
            start_year, end_year = map(int, period.split("-"))
            year_filter = and_(KPIValue.year >= start_year, KPIValue.year <= end_year)
        else:
            year = int(period)
            year_filter = KPIValue.year == year
        
        # Get KPI values for all organizations
        results = db.query(KPIValue, Organization).join(
            Organization, KPIValue.organization_id == Organization.id
        ).filter(
            and_(
                KPIValue.organization_id.in_(org_ids),
                KPIValue.kpi_id == kpi_id,
                year_filter,
                KPIValue.value_numeric.isnot(None)
            )
        ).all()
        
        comparison_data = {
            "kpi_id": kpi_id,
            "period": period,
            "organizations": [],
            "summary": {}
        }
        
        values = []
        for kpi_value, org in results:
            org_data = {
                "organization_id": org.id,
                "organization_name": org.name,
                "sector": org.sector,
                "value": kpi_value.value_numeric,
                "unit": kpi_value.unit,
                "year": kpi_value.year
            }
            comparison_data["organizations"].append(org_data)
            values.append(kpi_value.value_numeric)
        
        # Calculate summary statistics
        if values:
            comparison_data["summary"] = self.calculate_benchmark_stats(values).dict()
        
        return comparison_data


# Global service instance
_benchmark_service = None

def get_benchmark_service() -> BenchmarkService:
    """Get singleton benchmark service instance"""
    global _benchmark_service
    if _benchmark_service is None:
        _benchmark_service = BenchmarkService()
    return _benchmark_service
