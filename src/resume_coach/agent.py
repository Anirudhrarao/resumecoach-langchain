from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from resume_coach.config   import GROQ_API_KEY, MODEL, TEMPERATURE
from resume_coach.prompts  import COACH_SYSTEM_PROMPT, REWRITE_PROMPT
from resume_coach.tools    import TOOLS
from resume_coach.memory   import memory_store, get_thread_config
from resume_coach.schemas  import ResumeAnalysis
from resume_coach.middleware import summarize_if_needed, request_human_approval

from langchain_core.messages import HumanMessage

llm = ChatGroq(
    model=MODEL,
    temperature=TEMPERATURE,
    api_key=GROQ_API_KEY
)

structured_llm = llm.with_structured_output(ResumeAnalysis)


agent = create_react_agent(
    llm,
    TOOLS,
    prompt = COACH_SYSTEM_PROMPT,
    checkpointer=memory_store
)

def chat(message: str, thread_id: str) -> str:
    """
    Send a message to the agent and get a reply.
    Memory is automatically managed per thread_id.
    """
    config = get_thread_config(thread_id)
    result = agent.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )
    return result["messages"][-1].content


def analyze_resume(resume_text: str, job_description: str) -> ResumeAnalysis:
    """
    Run a full structured analysis of a resume against a job description.
    Returns a validated ResumeAnalysis Pydantic object.
    """
    prompt = f"""
            Analyze this resume against the job description and return structured feedback.

            RESUME:
            {resume_text}

            JOB DESCRIPTION:
            {job_description}
        """
    return structured_llm.invoke(prompt)