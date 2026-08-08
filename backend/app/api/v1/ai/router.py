from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.models.auth import User
from app.schemas.base import StandardResponse
from app.schemas.ai import ChatRequest, StudyPlanRequest, ResumeReviewRequest, ConversationCreate, ConversationResponse, MessageResponse, ConversationUpdate
from app.services.ai_service import AIService
import json

router = APIRouter(prefix="/ai", tags=["AI Mentor"])

@router.post("/mentor/conversations", response_model=StandardResponse)
def create_conversation(data: ConversationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AIService(db)
    conv = service.create_conversation(current_user.id, data)
    return StandardResponse(success=True, message="Conversation created", data=ConversationResponse.from_orm(conv))

@router.get("/mentor/conversations", response_model=StandardResponse)
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AIService(db)
    convs = service.get_conversations(current_user.id)
    return StandardResponse(success=True, message="Conversations fetched", data=[ConversationResponse.from_orm(c) for c in convs])

@router.get("/mentor/conversations/{conv_id}", response_model=StandardResponse)
def get_conversation_history(conv_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AIService(db)
    conv = service.get_conversation(current_user.id, conv_id)
    # Return messages along with conversation metadata
    messages = [MessageResponse.from_orm(m) for m in conv.messages]
    return StandardResponse(success=True, message="History fetched", data={"conversation": ConversationResponse.from_orm(conv), "messages": messages})

@router.delete("/mentor/conversations/{conv_id}", response_model=StandardResponse)
def delete_conversation(conv_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AIService(db)
    service.delete_conversation(current_user.id, conv_id)
    return StandardResponse(success=True, message="Conversation deleted", data=None)

@router.patch("/mentor/conversations/{conv_id}", response_model=StandardResponse)
def rename_conversation(conv_id: str, data: ConversationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AIService(db)
    conv = service.rename_conversation(current_user.id, conv_id, data.title)
    return StandardResponse(success=True, message="Conversation renamed", data=ConversationResponse.from_orm(conv))

@router.post("/mentor/chat")
async def chat_with_mentor(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    General chat endpoint utilizing the Database and AI Service.
    Streams the response using Server-Sent Events (SSE).
    """
    service = AIService(db)
    
    if request.stream:
        stream_generator = await service.chat_generator(current_user.id, request.conversation_id, request.message, stream=True)
        return StreamingResponse(stream_generator, media_type="text/event-stream")
    else:
        # Non-streaming fallback
        response_text = await service.chat_generator(current_user.id, request.conversation_id, request.message, stream=False)
        return StandardResponse(success=True, message="Success", data={"response": response_text})

@router.post("/study-plan", response_model=StandardResponse)
def generate_study_plan(request: StudyPlanRequest, current_user: User = Depends(get_current_user)):
    return StandardResponse(success=True, message="Study plan generated (Placeholder)", data={})

@router.post("/resume-review", response_model=StandardResponse)
def review_resume(request: ResumeReviewRequest, current_user: User = Depends(get_current_user)):
    return StandardResponse(success=True, message="Resume reviewed (Placeholder)", data={})
