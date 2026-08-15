from fastapi import APIRouter, HTTPException, status
from rag.schemas import ChatRequest, ChatResponse, FAQResponse
from rag.service import get_rag_service

router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])


@router.post("", response_model=ChatResponse)
def handle_chat_message(payload: ChatRequest) -> ChatResponse:
    """Process a participant chat message against the rulebook RAG pipeline."""
    try:
        service = get_rag_service()
        return service.process_query(payload.message, payload.history)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing error: {str(exc)}"
        ) from exc


@router.get("/faq", response_model=FAQResponse)
def get_chat_faq_prompts() -> FAQResponse:
    """Retrieve quick-start FAQ prompts and answers."""
    service = get_rag_service()
    return FAQResponse(faqs=service.get_faqs())
