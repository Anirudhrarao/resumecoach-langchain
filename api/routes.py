import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator

from resume_coach.agent import chat, analyze_resume, agent, llm
from resume_coach.memory import get_thread_config
from resume_coach.middleware import request_human_approval
from resume_coach.schemas import ResumeAnalysis, CoachRequest
from resume_coach.prompts import REWRITE_PROMPT

from langchain_core.messages import HumanMessage, AIMessageChunk


router = APIRouter()

# Request/Response Model
class AnalyzeRequest(BaseModel):
    resume_text: str 
    job_description: str 

class ChatRequest(BaseModel):
    message: str 
    thread_id: str 

class ApproveRequest(BaseModel):
    thread_id: str 
    original_summary: str
    job_description: str
    decision: str 
    edited_text: str 

class SessionResponse(BaseModel):
    thread_id: str


# Endpoints
@router.get("/health")
def health_check():
    """Liveness probe — used by EC2 and load balancers."""
    return {
        "status": "ok",
        "service": "ResumeCoach API"
    }


@router.post("/session")
def create_session() -> SessionResponse:
    """ 
    Generate a unique thread_id for new user session.
    The frontend calls this once on page load and stores the ID.
    """
    return SessionResponse(thread_id=str(uuid.uuid4()))


@router.post("/analyze")
def analyze(req: AnalyzeRequest) -> ResumeAnalysis:
    """ 
    Run a full structured analysis of a resume against a job description.
    Returns a validated ResumeAnalysis Pydantic object as JSON.
    """
    try:
        result = analyze_resume(req.resume_text, req.job_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    """
    Send a message to the coaching agent and stream the reply
    back to the frontend token-by-token using Server-Sent Events.
    """
    def token_stream():
        config = get_thread_config(req.thread_id)
        try:
            for chunk, metadata in agent.stream(
                {"messages": [HumanMessage(content=req.message)]},
                config=config,
                stream_mode="messages"
            ):
                if (
                    isinstance(chunk, AIMessageChunk)
                    and chunk.content
                    and not chunk.additional_kwargs.get("tool_calls")
                ):
                    safe_content = chunk.content.replace("\n", "<<NEWLINE>>")
                    yield f"data: {safe_content}\n\n"

        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        token_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"   # prevents nginx from buffering SSE
        }
    )


@router.post("/approve")
def approve_rewrite(req: ApproveRequest):
    """
    Human-in-the-loop endpoint.
    Frontend sends the user's approval decision; we return the final summary.
    """
    if req.decision == "yes":
        # Generate the rewrite and return it
        rewrite_prompt = REWRITE_PROMPT.format(
            original_summary=req.original_summary,
            job_description=req.job_description
        )
        rewritten = llm.invoke(rewrite_prompt).content
        return {"status": "approved", "final_summary": rewritten}

    elif req.decision == "edit":
        if not req.edited_text.strip():
            raise HTTPException(status_code=400, detail="edited_text is required for 'edit' decision")
        return {"status": "edited", "final_summary": req.edited_text}

    else:
        return {"status": "rejected", "final_summary": req.original_summary}


@router.delete("/session/{thread_id}")
def clear_session(thread_id: str):
    """
    Clear the memory for a given thread.
    Called when the user clicks 'New Session' in the frontend.
    """
    # MemorySaver doesn't expose a delete — we signal the frontend to generate a new thread_id
    return {"status": "cleared", "message": "Start a new session with a fresh thread_id"}