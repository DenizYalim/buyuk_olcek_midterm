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


def try_execute(message: str = None, tool: str = None, student_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """If the message or explicit tool maps to a tool, execute it and return a result dict.

    Can be called as either `try_execute(message=...)` (old behavior) or
    `try_execute(tool="get_tuition", student_id=123)` when the LLM
    explicitly requests a tool.
    """
    # If tool is explicitly provided, prefer that path
    if tool:
        t = tool.lower()
        if t in ("get_tuition", "get-tuition", "get tuition"):
            sid = student_id
            if sid is None:
                return {"tool": "get_tuition", "error": "student_id_not_found"}
            try:
                from mobile_uni import services as mu_services
            except Exception as e:
                return {"tool": "get_tuition", "error": f"import_error: {e}"}
            try:
                data = mu_services.get_tuition(sid)
                return {"tool": "get_tuition", "result": data}
            except Exception as e:
                return {"tool": "get_tuition", "error": str(e)}

        if t in ("pay_tuition", "pay-tuition", "pay tuition"):
            sid = student_id
            if sid is None:
                return {"tool": "pay_tuition", "error": "student_id_not_found"}
            try:
                from mobile_uni import services as mu_services
            except Exception as e:
                return {"tool": "pay_tuition", "error": f"import_error: {e}"}
            try:
                data = mu_services.pay_tuition(sid)
                return {"tool": "pay_tuition", "result": data}
            except Exception as e:
                return {"tool": "pay_tuition", "error": str(e)}

        if t in ("get_unpaid_tuitions", "get-unpaid-tuitions", "get unpaid tuitions"):
            try:
                from uni_admin import services as ua_services
                data = ua_services.get_unpaid_tuitions()
                return {"tool": "get_unpaid_tuitions", "result": data}
            except Exception:
                return {"tool": "get_unpaid_tuitions", "error": "not_implemented"}

        return None

    # Old behavior: decide based on the free-form message
    msg = (message or "").strip()
    if not msg:
        return None

    lower = msg.lower()

    # Query tuition intent
    if ("query tuition" in lower) or ("ask tuition" in lower) or ("get tuition" in lower):
        sid = _extract_student_id(msg)
        if sid is None:
            return {"tool": "get_tuition", "error": "student_id_not_found"}
        try:
            from mobile_uni import services as mu_services
        except Exception as e:
            return {"tool": "get_tuition", "error": f"import_error: {e}"}
        try:
            data = mu_services.get_tuition(sid)
            return {"tool": "get_tuition", "result": data}
        except Exception as e:
            return {"tool": "get_tuition", "error": str(e)}

    # Unpaid tuitions intent
    if "unpaid" in lower and "tuition" in lower:
        try:
            from uni_admin import services as ua_services
            try:
                data = ua_services.get_unpaid_tuitions()
                return {"tool": "get_unpaid_tuitions", "result": data}
            except Exception:
                pass
        except Exception:
            pass
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
            data = mu_services.pay_tuition(sid)
            return {"tool": "pay_tuition", "result": data}
        except Exception as e:
            return {"tool": "pay_tuition", "error": str(e)}

    return None
