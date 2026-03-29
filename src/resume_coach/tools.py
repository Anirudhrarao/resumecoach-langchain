# src/resume_coach/tools.py
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from resume_coach.config import TAVILY_API_KEY, MAX_SEARCH_RESULTS


@tool
def analyze_skill_gap(resume_skills: str, job_required_skills: str) -> str:
    """
    Compares skills listed in a resume against skills required in a job description.
    Returns matched skills, missing skills, and a match score percentage.

    Args:
        resume_skills: comma-separated list of skills from the resume as a plain string
        job_required_skills: comma-separated list of skills required by the job as a plain string
    """
    # Guard: ensure inputs are always plain strings before processing
    if not isinstance(resume_skills, str):
        resume_skills = ", ".join(str(s) for s in resume_skills)
    if not isinstance(job_required_skills, str):
        job_required_skills = ", ".join(str(s) for s in job_required_skills)

    # Clean and normalize into sets
    resume_set = {s.strip().lower() for s in resume_skills.split(",") if s.strip()}
    job_set    = {s.strip().lower() for s in job_required_skills.split(",") if s.strip()}

    # Guard: if either set is empty return a helpful message
    if not resume_set:
        return "Could not parse resume skills. Please provide a comma-separated list."
    if not job_set:
        return "Could not parse job skills. Please provide a comma-separated list."

    matched = resume_set & job_set
    missing = job_set - resume_set

    # Safe score calculation — both operands are guaranteed ints
    total_job_skills = len(job_set)
    matched_count    = len(matched)
    score            = round((matched_count / total_job_skills) * 100) if total_job_skills > 0 else 0

    return (
        f"Match score     : {score}%\n"
        f"Matched skills  ({matched_count}): {', '.join(sorted(matched)) or 'none'}\n"
        f"Missing skills  ({len(missing)}): {', '.join(sorted(missing)) or 'none'}\n"
    )


# ── Tavily with truncation wrapper ────────────────────────
_tavily = TavilySearchResults(
    max_results=MAX_SEARCH_RESULTS,
    api_key=TAVILY_API_KEY
)

@tool
def web_search(query: str) -> str:
    """
    Searches the web for current information about companies, job roles,
    required skills, or industry trends. Use when the user mentions a specific
    company name or asks about market demand for a skill.

    Args:
        query: the search query string
    """
    # Guard: ensure query is a plain string
    if not isinstance(query, str):
        query = str(query)

    results = _tavily.invoke(query)

    if not results:
        return "No search results found."

    snippets = [
        f"[{r['url']}]\n{r['content'][:300]}"
        for r in results
        if isinstance(r, dict) and "content" in r
    ]
    return "\n\n".join(snippets) if snippets else "No usable results found."


TOOLS = [analyze_skill_gap, web_search]