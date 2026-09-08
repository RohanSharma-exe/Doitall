"""Knowledge ingestion and management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from doitall.api.errors import INGEST_FAILED
from doitall.api.models import (
    IngestRequest,
    IngestResponse,
    KnowledgeDocument,
    KnowledgeListResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
)
from doitall.core.exceptions import DoitallError, ValidationError
from doitall.knowledge.document import Document
from doitall.security.auth import require_api_key
from doitall.services.registry import container

router = APIRouter()

_NOT_FOUND = "Document not found"
_SEARCH_FAILED = "Knowledge search failed"
_DELETE_FAILED = "Knowledge delete failed"
_LIST_FAILED = "Knowledge list failed"


def _resolve_repo():  # type: ignore[no-untyped-def]
    return container.resolve("knowledge_repository")


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------


@router.post(
    "/knowledge/ingest",
    response_model=IngestResponse,
    status_code=201,
    summary="Ingest a document into the knowledge base",
    tags=["knowledge"],
    dependencies=[Depends(require_api_key)],
)
async def ingest(request: IngestRequest) -> IngestResponse:
    """
    Index a document for retrieval-augmented generation (RAG).

    The document is chunked, embedded, and stored in Qdrant. Future chat
    turns will automatically retrieve relevant chunks from this document
    when answering questions.
    """
    try:
        ingestion_service = container.resolve("knowledge_ingestion")
        doc = Document(
            content=request.content,
            metadata={
                **({"title": request.title} if request.title else {}),
                **request.metadata,
            },
        )
        result = await ingestion_service.ingest(doc)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DoitallError as exc:
        logger.warning("Knowledge ingestion domain failure: {}", exc)
        raise HTTPException(status_code=500, detail=INGEST_FAILED) from exc
    except Exception as exc:
        logger.exception("Knowledge ingestion failed")
        raise HTTPException(status_code=500, detail=INGEST_FAILED) from exc

    return IngestResponse(
        document_id=result.document_id,
        chunk_count=result.chunk_count,
        status=result.status,
    )


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


@router.get(
    "/knowledge",
    response_model=KnowledgeListResponse,
    summary="List indexed knowledge documents",
    tags=["knowledge"],
    dependencies=[Depends(require_api_key)],
)
async def list_documents(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> KnowledgeListResponse:
    """Return a paged list of documents currently indexed in the knowledge base."""
    try:
        repo = _resolve_repo()
        summaries = await repo.list_documents(limit=limit, offset=offset)
        total = await repo.count()
    except Exception as exc:
        logger.exception("Knowledge list failed")
        raise HTTPException(status_code=500, detail=_LIST_FAILED) from exc

    return KnowledgeListResponse(
        documents=[
            KnowledgeDocument(
                document_id=s["document_id"],
                title=s.get("title"),
                chunk_count=s["chunk_count"],
                metadata=s.get("metadata", {}),
            )
            for s in summaries
        ],
        total=total,
    )


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------


@router.get(
    "/knowledge/{document_id}",
    response_model=KnowledgeDocument,
    summary="Get knowledge document detail",
    tags=["knowledge"],
    dependencies=[Depends(require_api_key)],
)
async def get_document(document_id: str) -> KnowledgeDocument:
    """Return metadata and chunk count for a single indexed document."""
    try:
        repo = _resolve_repo()
        summary = await repo.get_document(document_id)
    except Exception as exc:
        logger.exception("Knowledge detail failed")
        raise HTTPException(status_code=500, detail=_LIST_FAILED) from exc

    if summary is None:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)

    return KnowledgeDocument(
        document_id=summary["document_id"],
        title=summary.get("title"),
        chunk_count=summary["chunk_count"],
        metadata=summary.get("metadata", {}),
    )


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


@router.delete(
    "/knowledge/{document_id}",
    status_code=204,
    summary="Delete a knowledge document",
    tags=["knowledge"],
    dependencies=[Depends(require_api_key)],
)
async def delete_document(document_id: str) -> None:
    """Remove a document and all its chunks from the knowledge base."""
    try:
        repo = _resolve_repo()
        removed = await repo.delete(document_id)
    except Exception as exc:
        logger.exception("Knowledge delete failed document_id={}", document_id)
        raise HTTPException(status_code=500, detail=_DELETE_FAILED) from exc

    if removed == 0:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)


# ---------------------------------------------------------------------------
# Search preview
# ---------------------------------------------------------------------------


@router.post(
    "/knowledge/search",
    response_model=KnowledgeSearchResponse,
    summary="Semantic search over the knowledge base",
    tags=["knowledge"],
    dependencies=[Depends(require_api_key)],
)
async def search_knowledge(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    """Perform a semantic similarity search and return the top-K matching chunks.

    Useful for previewing what the RAG pipeline would retrieve for a given query
    before sending it as a chat message.
    """
    try:
        repo = _resolve_repo()
        docs = await repo.search(request.query, limit=request.limit)
    except Exception as exc:
        logger.exception("Knowledge search failed")
        raise HTTPException(status_code=500, detail=_SEARCH_FAILED) from exc

    return KnowledgeSearchResponse(
        query=request.query,
        results=[
            KnowledgeSearchResult(
                document_id=doc.id,
                text=doc.content,
                metadata=doc.metadata,
            )
            for doc in docs
        ],
    )
