from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None
    history: list[ChatMessage] = []


class ChatSource(BaseModel):
    section_id: str
    title: str
    excerpt: str
    score: float = 0.0


class ChatResponse(BaseModel):
    reply: str
    sources: list[ChatSource] = []
    suggested_questions: list[str] = []
    confidence: float = 1.0


class FAQItem(BaseModel):
    category: str
    question: str
    answer: str
    section_id: str


class FAQResponse(BaseModel):
    faqs: list[FAQItem]
