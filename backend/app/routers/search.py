from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models import Embedding, Report, Organization, KPIDefinition, User
from app.schemas import SearchRequest, SearchResponse, SearchResult
from app.routers.auth import get_current_user
from app.services.llm_client import get_llm_client_instance

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=1, max_length=1000, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    kpi_id: Optional[int] = Query(None, description="Filter by KPI"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Semantic search across document embeddings using vector similarity
    """
    try:
        # Generate embedding for the search query
        llm_client = get_llm_client_instance()
        query_embeddings = await llm_client.generate_embeddings([q])
        
        if not query_embeddings or not query_embeddings[0]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate search embedding"
            )
        
        query_embedding = query_embeddings[0]
        
        # Build the base query
        query_builder = db.query(Embedding)
        
        # Apply filters
        if organization_id:
            query_builder = query_builder.join(Report).filter(Report.organization_id == organization_id)
        
        if kpi_id:
            query_builder = query_builder.filter(Embedding.kpi_definition_id == kpi_id)
        
        # Perform vector similarity search using pgvector
        # Using cosine distance (1 - cosine_similarity) for ordering
        from sqlalchemy import text
        
        # Convert embedding to string format for SQL
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Use raw SQL for vector similarity search
        similarity_query = text(f"""
            SELECT 
                e.id,
                e.chunk_text,
                e.metadata,
                e.created_at,
                e.report_id,
                e.kpi_definition_id,
                (1 - (e.vector <=> '{embedding_str}'::vector)) as similarity_score
            FROM embedding e
            {f"JOIN report r ON e.report_id = r.id" if organization_id else ""}
            WHERE 1=1
            {f"AND r.organization_id = {organization_id}" if organization_id else ""}
            {f"AND e.kpi_definition_id = {kpi_id}" if kpi_id else ""}
            ORDER BY e.vector <=> '{embedding_str}'::vector
            LIMIT {limit}
        """)
        
        results = db.execute(similarity_query).fetchall()
        
        # Format results
        search_results = []
        for result in results:
            search_result = SearchResult(
                chunk_text=result.chunk_text,
                similarity_score=float(result.similarity_score),
                report_id=result.report_id,
                kpi_definition_id=result.kpi_definition_id,
                metadata=result.metadata
            )
            search_results.append(search_result)
        
        logger.info(f"Search query '{q}' returned {len(search_results)} results")
        
        return SearchResponse(
            results=search_results,
            total=len(search_results),
            query=q
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


@router.post("/", response_model=SearchResponse)
async def search_documents_post(
    search_request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Semantic search using POST request with full search parameters
    """
    try:
        # Generate embedding for the search query
        llm_client = get_llm_client_instance()
        query_embeddings = await llm_client.generate_embeddings([search_request.query])
        
        if not query_embeddings or not query_embeddings[0]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate search embedding"
            )
        
        query_embedding = query_embeddings[0]
        
        # Convert embedding to string format for SQL
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Build dynamic SQL query with filters
        where_conditions = ["1=1"]
        joins = []
        
        if search_request.organization_id:
            joins.append("JOIN report r ON e.report_id = r.id")
            where_conditions.append(f"r.organization_id = {search_request.organization_id}")
        
        if search_request.kpi_id:
            where_conditions.append(f"e.kpi_definition_id = {search_request.kpi_id}")
        
        joins_str = " ".join(joins)
        where_str = " AND ".join(where_conditions)
        
        from sqlalchemy import text
        
        similarity_query = text(f"""
            SELECT 
                e.id,
                e.chunk_text,
                e.metadata,
                e.created_at,
                e.report_id,
                e.kpi_definition_id,
                (1 - (e.vector <=> '{embedding_str}'::vector)) as similarity_score
            FROM embedding e
            {joins_str}
            WHERE {where_str}
            ORDER BY e.vector <=> '{embedding_str}'::vector
            LIMIT {search_request.limit}
        """)
        
        results = db.execute(similarity_query).fetchall()
        
        # Format results
        search_results = []
        for result in results:
            search_result = SearchResult(
                chunk_text=result.chunk_text,
                similarity_score=float(result.similarity_score),
                report_id=result.report_id,
                kpi_definition_id=result.kpi_definition_id,
                metadata=result.metadata
            )
            search_results.append(search_result)
        
        return SearchResponse(
            results=search_results,
            total=len(search_results),
            query=search_request.query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


@router.get("/similar/{embedding_id}")
async def find_similar_chunks(
    embedding_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find chunks similar to a specific embedding"""
    try:
        # Get the source embedding
        source_embedding = db.query(Embedding).filter(Embedding.id == embedding_id).first()
        
        if not source_embedding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Embedding not found"
            )
        
        # Convert source embedding vector to string
        source_vector = source_embedding.vector
        embedding_str = "[" + ",".join(map(str, source_vector)) + "]"
        
        from sqlalchemy import text
        
        # Find similar embeddings (excluding the source)
        similarity_query = text(f"""
            SELECT 
                e.id,
                e.chunk_text,
                e.metadata,
                e.created_at,
                e.report_id,
                e.kpi_definition_id,
                (1 - (e.vector <=> '{embedding_str}'::vector)) as similarity_score
            FROM embedding e
            WHERE e.id != {embedding_id}
            ORDER BY e.vector <=> '{embedding_str}'::vector
            LIMIT {limit}
        """)
        
        results = db.execute(similarity_query).fetchall()
        
        # Format results
        similar_chunks = []
        for result in results:
            similar_chunks.append({
                "id": result.id,
                "chunk_text": result.chunk_text,
                "similarity_score": float(result.similarity_score),
                "report_id": result.report_id,
                "kpi_definition_id": result.kpi_definition_id,
                "metadata": result.metadata,
                "created_at": result.created_at
            })
        
        return {
            "source_embedding_id": embedding_id,
            "source_text": source_embedding.chunk_text[:200] + "..." if len(source_embedding.chunk_text) > 200 else source_embedding.chunk_text,
            "similar_chunks": similar_chunks,
            "total": len(similar_chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similar chunks search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Similar chunks search failed"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search suggestions based on partial query"""
    try:
        # Get suggestions from KPI definitions
        kpi_suggestions = db.query(KPIDefinition.name, KPIDefinition.code).filter(
            KPIDefinition.name.ilike(f"%{q}%") |
            KPIDefinition.code.ilike(f"%{q}%")
        ).limit(limit).all()
        
        # Get suggestions from organization names
        org_suggestions = db.query(Organization.name).filter(
            Organization.name.ilike(f"%{q}%")
        ).limit(limit).all()
        
        suggestions = []
        
        # Add KPI suggestions
        for kpi_name, kpi_code in kpi_suggestions:
            suggestions.append({
                "type": "kpi",
                "text": kpi_name,
                "code": kpi_code,
                "category": "KPI"
            })
        
        # Add organization suggestions
        for (org_name,) in org_suggestions:
            suggestions.append({
                "type": "organization",
                "text": org_name,
                "category": "Organization"
            })
        
        # Add common search terms
        common_terms = [
            "scope 1 emissions", "scope 2 emissions", "scope 3 emissions",
            "water withdrawal", "waste generated", "energy intensity",
            "renewable energy", "carbon footprint", "sustainability"
        ]
        
        matching_terms = [term for term in common_terms if q.lower() in term.lower()]
        for term in matching_terms[:3]:  # Limit to 3 common terms
            suggestions.append({
                "type": "term",
                "text": term,
                "category": "Common Search"
            })
        
        return {
            "query": q,
            "suggestions": suggestions[:limit]
        }
        
    except Exception as e:
        logger.error(f"Search suggestions failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search suggestions"
        )


@router.get("/stats")
async def get_search_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search-related statistics"""
    try:
        # Count total embeddings
        total_embeddings = db.query(Embedding).count()
        
        # Count embeddings by report
        embeddings_by_report = db.query(
            Report.id, Report.title, db.func.count(Embedding.id).label('embedding_count')
        ).join(Embedding).group_by(Report.id, Report.title).all()
        
        # Count unique organizations with embeddings
        orgs_with_embeddings = db.query(Organization.id).join(Report).join(Embedding).distinct().count()
        
        # Get recent embeddings
        recent_embeddings = db.query(Embedding).order_by(Embedding.created_at.desc()).limit(5).all()
        
        return {
            "total_embeddings": total_embeddings,
            "organizations_with_data": orgs_with_embeddings,
            "reports_with_embeddings": len(embeddings_by_report),
            "recent_embeddings": [
                {
                    "id": emb.id,
                    "report_id": emb.report_id,
                    "text_preview": emb.chunk_text[:100] + "..." if len(emb.chunk_text) > 100 else emb.chunk_text,
                    "created_at": emb.created_at
                }
                for emb in recent_embeddings
            ],
            "top_reports_by_embeddings": [
                {
                    "report_id": report_id,
                    "report_title": title,
                    "embedding_count": count
                }
                for report_id, title, count in embeddings_by_report[:10]
            ]
        }
        
    except Exception as e:
        logger.error(f"Search stats failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search statistics"
        )
