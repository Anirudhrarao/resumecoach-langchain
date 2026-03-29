from pydantic import BaseModel, Field
from typing import List 

class ResumeAnalysis(BaseModel):
    """Structure ouput the agent return after analyzing a resume."""
    
    match_score: int = Field(
        description="Overall match percentage between resume and job description (0-100)"
    )

    matched_skills: List[str] = Field(
        description="Skills present in both the resume and job description"
    )

    missing_skills: List[str] = Field(
        description="Skills required by the job but absent from the resume"
    )

    rewritten_summary: str = Field(
         description="An improved resume summary tailored to the job description"
    )

    top_recommendations: List[str] = Field(
        description="3 to 5 specific, actionable improvements for this resume"
    )

class ChatMessage(BaseModel):
    """A single message in the coaching conversation."""
    role: str
    content: str 


class CoachRequest(BaseModel):
    """Payload the frontend sends to the API."""

    resume_text: str
    job_description: str
    thread_id: str     
    message: str
