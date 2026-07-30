"""Knowledge ingestion route — add documents to the RAG knowledge base."""
from fastapi import APIRouter, Depends, HTTPException

from doitall.api.models import IngestRequest, IngestResponse
from doitall.core.exceptions import DoitallError, ValidationError
from doitall.knowledge.document import Document
from doitall.security.auth import require_api_key
from doitall.services.registry import container

router = APIRouter()


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
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc

    return IngestResponse(
        document_id=result.document_id,
        chunk_count=result.chunk_count,
        status=result.status,
    )
