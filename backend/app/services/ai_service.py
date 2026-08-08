from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException
from app.models.ai import Conversation, Message
from app.schemas.ai import ConversationCreate
from app.agents.core import get_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.prompts.system_prompts import (
    CAREER_AGENT_PROMPT, DSA_AGENT_PROMPT, 
    RESUME_AGENT_PROMPT, INTERVIEW_AGENT_PROMPT
)
import json

# Fallback basic prompts if not defined in system_prompts.py
APTITUDE_PROMPT = """You are an expert Aptitude Placement Mentor. Your job is to help the student with quantitative aptitude, logical reasoning, and verbal ability.
Explain concepts clearly, identify weak topics, and recommend what to study. Do not make up user statistics; only use the context provided."""

COMPANY_PROMPT = """You are a Company Preparation Mentor. Help the student prepare for specific companies (e.g., Amazon, TCS)."""

GENERAL_PROMPT = """You are a general Placement Mentor. Help the student navigate their placement journey."""

class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm(streaming=True) # Ensure LLM is instantiated

    def create_conversation(self, user_id: str, data: ConversationCreate):
        conv = Conversation(user_id=user_id, title=data.title, mode=data.mode)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def get_conversations(self, user_id: str):
        return self.db.query(Conversation).filter(Conversation.user_id == user_id).order_by(desc(Conversation.updated_at)).all()

    def get_conversation(self, user_id: str, conv_id: str):
        conv = self.db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == user_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found or unauthorized")
        return conv

    def delete_conversation(self, user_id: str, conv_id: str):
        conv = self.get_conversation(user_id, conv_id)
        self.db.delete(conv)
        self.db.commit()
        return {"message": "Conversation deleted"}

    def add_message(self, conv_id: str, role: str, content: str):
        msg = Message(conversation_id=conv_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        # Update conversation updated_at
        conv = self.db.query(Conversation).filter(Conversation.id == conv_id).first()
        conv.updated_at = msg.created_at
        self.db.commit()
        return msg

    def build_user_context(self, user_id: str, mode: str) -> str:
        # In a real scenario, this would query aptitude_service, dsa_service, etc.
        # For MVP, we provide a placeholder context template that would be populated from DB stats.
        from app.services.aptitude_service import AptitudeService
        
        context_str = "USER CONTEXT:\n"
        if mode == "aptitude":
            apt_service = AptitudeService(self.db)
            try:
                progress = apt_service.get_user_progress(user_id)
                context_str += f"- Total Aptitude Tests Taken: {progress.get('total_tests_taken', 0)}\n"
                context_str += f"- Overall Accuracy: {progress.get('overall_accuracy', 0)}%\n"
                context_str += f"- Strongest Topic: {progress.get('strongest_topic', 'Unknown')}\n"
                context_str += f"- Weakest Topic: {progress.get('weakest_topic', 'Unknown')}\n"
            except Exception:
                context_str += "No aptitude data available yet.\n"
        
        return context_str

    def get_system_prompt(self, mode: str) -> str:
        prompts = {
            "career": CAREER_AGENT_PROMPT,
            "dsa": DSA_AGENT_PROMPT,
            "resume": RESUME_AGENT_PROMPT,
            "interview": INTERVIEW_AGENT_PROMPT,
            "aptitude": APTITUDE_PROMPT,
            "company": COMPANY_PROMPT,
            "general": GENERAL_PROMPT
        }
        return prompts.get(mode, GENERAL_PROMPT)

    async def chat_generator(self, user_id: str, conv_id: str, message: str, stream: bool = True):
        conv = self.get_conversation(user_id, conv_id)
        
        # Add user message to DB
        self.add_message(conv_id, "user", message)
        
        # Retrieve recent history (cost control: limit to last 10 messages)
        recent_messages = self.db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at.asc()).all()[-10:]
        
        lc_messages = []
        # Inject system prompt with context
        system_text = self.get_system_prompt(conv.mode)
        context_text = self.build_user_context(user_id, conv.mode)
        lc_messages.append(SystemMessage(content=f"{system_text}\n\n{context_text}"))
        
        for msg in recent_messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "ai":
                lc_messages.append(AIMessage(content=msg.content))
        
        if not stream:
            try:
                response = await self.llm.ainvoke(lc_messages)
                ai_content = response.content
                self.add_message(conv_id, "ai", ai_content)
                return ai_content
            except Exception as e:
                # Fallback if provider fails
                raise HTTPException(status_code=503, detail=f"AI Provider Error: {str(e)}")

        async def sse_stream():
            full_response = ""
            try:
                # Use astream for token-by-token streaming
                async for chunk in self.llm.astream(lc_messages):
                    content = chunk.content
                    if content:
                        full_response += content
                        # Escape newlines for SSE
                        escaped = content.replace("\n", "\\n").replace('"', '\\"')
                        yield f'data: {{"chunk": "{escaped}"}}\n\n'
                
                # Save full response to DB after streaming completes
                self.add_message(conv_id, "ai", full_response)
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f'data: {{"error": "AI Provider Error: {str(e)}"}}\n\n'
        
        return sse_stream()
