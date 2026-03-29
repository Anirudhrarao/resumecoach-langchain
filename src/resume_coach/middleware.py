from langchain_core.messages import SystemMessage, HumanMessage
from resume_coach.config import MAX_MESSAGES_BEFORE_SUMMARY
from resume_coach.prompts import SUMMARIZER_PROMPT


def summarize_if_needed(messages: list, llm) -> list:
    """ 
    Compresses conversation history when it exceeds MAX_MESSAGES_BEFORE_SUMMARY.
    Older messages are replaced by a single SystemMessage summary.
    The 4 most recent messages are always kept verbatim.
    """
    if len(messages) <= MAX_MESSAGES_BEFORE_SUMMARY:
        return messages 
    
    recent_messages = messages[-4:]
    older_messages = messages[:-4]

    history_text = "\n".join(
        f"{type(m).__name__}: {m.content[:150]}"
        for m in messages
        if hasattr(m, "content")
    )

    summary_response = llm.invoke([
        SystemMessage(content="You are a concise conversation summarizer."),
        HumanMessage(content=SUMMARIZER_PROMPT.format(history=history_text))
    ])

    summary_message = SystemMessage(
        content=f"[Prior conversation summary]\n{summary_response.content}"
    )

    print(f"[Middleware] Summarized {len(older_messages)} messages → 1 summary block")
    return [summary_message] + recent_messages


def request_human_approval(proposed_rewrite: str, llm, original: str, jd: str) -> str:
    """
    Shows the agent's proposed resume rewrite to the human and
    waits for explicit approval before applying it.

    Returns the final string to use (approved, edited, or original).
    """
    print("\n" + "=" * 60)
    print("ORIGINAL SUMMARY:")
    print(original.strip())
    print("\nPROPOSED REWRITE:")
    print(proposed_rewrite.strip())
    print("=" * 60)

    decision = input("\nApprove this rewrite? (yes / no / edit): ").strip().lower()

    if decision == "yes":
        print("[HITL] Rewrite approved.")
        return proposed_rewrite
    elif decision == "edit":
        edited = input("Enter your edited version: ").strip()
        print("[HITL] Edited version saved.")
        return edited
    else:
        print("[HITL] Rewrite rejected. Original kept.")
        return original