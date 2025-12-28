"""Simple tools executor for LLM-assisted actions.

This module exposes a small `try_execute` function which detects a few
intents in the user's message and executes internal functions (like
`mobile_uni.services.get_tuition`). The goal is to give the chat bot
explicit abilities (tools) to query tuition data.
"""

import re
from typing import Optional, Dict, Any

def _extract_student_id(msg: str) -> Optional[int]:
    # look for a number following 'student' or 'id'
    m = re.search(r"student\s*(?:id\s*)?(?:#|:)?\s*(\d+)", msg, re.IGNORECASE)
    if not m:
        m = re.search(r"\bid\b[:=]?\s*(\d+)", msg, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    return None


def try_execute(message: str) -> Optional[Dict[str, Any]]:
    """If the message maps to a tool, execute it and return a result dict.

    Return value format (on success): {"tool": "get_tuition", "result": <any>}.
    Return None if no tool matched.
    """
    msg = (message or "").strip()
    if not msg:
        return None

    lower = msg.lower()

    # Query tuition intent
    if ("query tuition" in lower) or ("ask tuition" in lower) or ("get tuition" in lower):
        sid = _extract_student_id(msg)
        if sid is None:
            return {"tool": "get_tuition", "error": "student_id_not_found"}

        # lazy import to avoid circular imports on module load
        try:
            from mobile_uni import services as mu_services
        except Exception as e:
            return {"tool": "get_tuition", "error": f"import_error: {e}"}

        try:
            data = mu_services.get_tuition(sid)
            return {"tool": "get_tuition", "result": data}
        except Exception as e:
            return {"tool": "get_tuition", "error": str(e)}

    # Unpaid tuitions intent (ask admin endpoint)
    if "unpaid" in lower and "tuition" in lower:
        try:
            # call uni_admin controller via HTTP or service layer if available
            # Try import of uni_admin services if present
            from uni_admin import services as ua_services
            try:
                data = ua_services.get_unpaid_tuitions()
                return {"tool": "get_unpaid_tuitions", "result": data}
            except Exception:
                # fall back to calling admin HTTP endpoint
                pass
        except Exception:
            pass

        # fallback: return instruction for how to call unpaid tuitions
        return {"tool": "get_unpaid_tuitions", "error": "not_implemented"}

    # Pay tuition intent
    if ("pay tuition" in lower) or ("pay" in lower and "tuition" in lower):
        sid = _extract_student_id(msg)
        if sid is None:
            return {"tool": "pay_tuition", "error": "student_id_not_found"}

        try:
            from mobile_uni import services as mu_services
        except Exception as e:
            return {"tool": "pay_tuition", "error": f"import_error: {e}"}

        try:
            # call the service; it may be unimplemented and raise/return accordingly
            data = mu_services.pay_tuition(sid)
            return {"tool": "pay_tuition", "result": data}
        except Exception as e:
            return {"tool": "pay_tuition", "error": str(e)}

    return None
