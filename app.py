from uni_admin.controllers import uni_admin_bp
from mobile_uni.controllers import mobile_uni_bp

from flask import Flask, request, jsonify
from flask_cors import CORS

import json
import os
import llm
from llm import base_LLM
from uuid import uuid4


def app_from_bp():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(mobile_uni_bp, url_prefix="/mobile")
    app.register_blueprint(uni_admin_bp, url_prefix="/admin")

    # Single LLM instance for the app
    app.llm = base_LLM()
    # in-memory chat history per session
    app.chat_history = {}

    @app.route("/chat", methods=["POST"])
    def chat():
        payload = request.get_json(silent=True) or {}
        message = payload.get("message")
        if not message:
            return jsonify({"error": "message required"}), 400

        # session handling: accept `session_id` or create a new one
        session_id = payload.get("session_id")
        new_session = False
        if not session_id:
            session_id = str(uuid4())
            new_session = True

        # ensure history exists and append user message
        app.chat_history.setdefault(session_id, [])
        app.chat_history[session_id].append({"role": "user", "text": message})

        # build a short textual summary of recent history for inclusion in LLM prompts
        def _history_text(sid, limit=20):
            hist = app.chat_history.get(sid, [])[-limit:]
            lines = []
            for m in hist:
                role = "User" if m.get("role") == "user" else "Assistant"
                lines.append(f"{role}: {m.get('text')}")
            return "\n".join(lines)

        history_str = _history_text(session_id)

        # Determine if we can let the LLM decide to call tools.
        openai_key = os.getenv("OPENAI_API_KEY")
        use_llm_tools = (openai_key is not None) and (llm.OpenAI is not None)

        # helper: call a tool and return structured response
        try:
            from llm_tools import try_execute
        except Exception:
            try_execute = None

        if use_llm_tools and try_execute is not None:
            # 1) Ask the LLM whether it wants to call a tool. Expect JSON output.
            decide_prompt = (
                "You are an assistant with access to the following tools:\n"
                "1) get_tuition(student_id) -> returns tuition data for a student id\n"
                "2) get_unpaid_tuitions() -> returns unpaid tuition list\n"
                "3) pay_tuition(student_id) -> attempts to pay tuition for student id\n\n"
                "When appropriate, output ONLY valid JSON with one of these forms:\n"
                "{\"action\": \"tool\", \"tool\": \"get_tuition\", \"student_id\": 123}\n"
                "{\"action\": \"tool\", \"tool\": \"pay_tuition\", \"student_id\": 123}\n"
                "{\"action\": \"tool\", \"tool\": \"get_unpaid_tuitions\"}\n"
                "Or, if no tool is needed, output:\n"
                "{\"action\": \"respond\", \"response\": \"<final text answer>\"}\n\n"
                "User message: " + message
            )

            # include conversation history before the decision prompt
            decide_prompt_with_history = "Conversation history:\n" + history_str + "\n\n" + decide_prompt
            try:
                decision = app.llm.getResponse(decide_prompt_with_history)
            except Exception as e:
                return jsonify({"error": f"llm_decision_error: {e}"}), 500

            # Try to parse JSON decision
            try:
                decision_json = json.loads(decision)
            except Exception:
                # If LLM didn't return JSON, just return its text answer
                try:
                    resp_text = decision if isinstance(decision, str) else str(decision)
                except Exception:
                    resp_text = ""
                return jsonify({"response": resp_text})

            # If LLM decided to call a tool, execute it
            if decision_json.get("action") == "tool":
                tool_name = decision_json.get("tool")
                # If the LLM provided a student_id explicitly, include it in the tool message
                student_id = decision_json.get("student_id")
                if student_id is not None:
                    # Call try_execute with explicit tool and student_id
                    try:
                        tool_res = try_execute(tool=tool_name, student_id=student_id)
                    except Exception as e:
                        return jsonify({"error": f"tool_exec_error: {e}"}), 500
                else:
                    # Fall back to original user message to let try_execute extract ids
                    try:
                        tool_res = try_execute(message)
                    except Exception as e:
                        return jsonify({"error": f"tool_exec_error: {e}"}), 500

                if tool_res is None:
                    return jsonify({"error": "tool_execution_returned_none", "decision": decision_json}), 500

                # Provide tool result back to LLM for a final answer, include history
                followup_prompt = (
                    "Conversation history:\n" + history_str + "\n\n"
                    "Tool result (JSON): " + json.dumps(tool_res) + "\n"
                    "Based on the tool result and the original user message, produce a helpful final answer."
                )

                try:
                    final = app.llm.getResponse(followup_prompt)
                except Exception as e:
                    return jsonify({"error": f"llm_final_error: {e}"}), 500

                try:
                    final_text = final if isinstance(final, str) else str(final)
                except Exception:
                    final_text = ""

                # append assistant reply to history
                app.chat_history[session_id].append({"role": "assistant", "text": final_text})
                res = {
                    "tool": tool_res.get("tool") if isinstance(tool_res, dict) else tool_name,
                    "result": tool_res.get("result") if isinstance(tool_res, dict) else tool_res,
                    "response": final_text,
                    "error": tool_res.get("error") if isinstance(tool_res, dict) else None,
                    "session_id": session_id,
                }
                if new_session:
                    res["new_session"] = True
                return jsonify(res)

            # If action was respond, return the content
            if decision_json.get("action") == "respond":
                resp_text = decision_json.get("response")
                # append assistant reply to history
                app.chat_history[session_id].append({"role": "assistant", "text": resp_text})
                res = {"response": resp_text, "session_id": session_id}
                if new_session:
                    res["new_session"] = True
                return jsonify(res)

        # Fallback: try direct tool matching (no OpenAI or LLM didn't choose tools)
        if try_execute is not None:
            try:
                tool_res = try_execute(message)
                if tool_res is not None:
                    assistant_text = None
                    if isinstance(tool_res, dict) and tool_res.get("result") is not None:
                        try:
                            assistant_text = json.dumps(tool_res.get("result"))
                        except Exception:
                            assistant_text = str(tool_res.get("result"))
                    elif isinstance(tool_res, dict) and tool_res.get("error") is not None:
                        assistant_text = "Error: " + str(tool_res.get("error"))
                    else:
                        assistant_text = str(tool_res)

                    # append assistant reply to history and return
                    app.chat_history[session_id].append({"role": "assistant", "text": assistant_text})
                    res = {"tool": tool_res.get("tool"), "result": tool_res.get("result"), "error": tool_res.get("error"), "session_id": session_id}
                    if new_session:
                        res["new_session"] = True
                    return jsonify(res)
            except Exception as e:
                return jsonify({"error": f"tool_error: {e}"}), 500

        # Final fallback to plain LLM response (or local fallback responder)
        try:
            resp = app.llm.getResponse(message)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        try:
            resp_text = resp if isinstance(resp, str) else str(resp)
        except Exception:
            resp_text = ""

        return jsonify({"response": resp_text})

    return app


if __name__ == "__main__":
    app = app_from_bp()
    app.run(host="0.0.0.0", port=5000)


""" 
    TODO
    * paging ok; auth todo
    * to host
    * to film later
    * add logging
    * get batch return
"""