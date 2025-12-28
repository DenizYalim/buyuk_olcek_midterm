from uni_admin.controllers import uni_admin_bp
from mobile_uni.controllers import mobile_uni_bp

from flask import Flask, request, jsonify
from flask_cors import CORS

from llm import base_LLM


def app_from_bp():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(mobile_uni_bp, url_prefix="/mobile")
    app.register_blueprint(uni_admin_bp, url_prefix="/admin")

    # Single LLM instance for the app
    app.llm = base_LLM()

    @app.route("/chat", methods=["POST"])
    def chat():
        payload = request.get_json(silent=True) or {}
        message = payload.get("message")
        if not message:
            return jsonify({"error": "message required"}), 400

        # First, see if a tool can directly handle the request (query/pay tuition etc.)
        try:
            from llm_tools import try_execute
        except Exception:
            try_execute = None

        if try_execute is not None:
            try:
                tool_res = try_execute(message)
                if tool_res is not None:
                    # Return structured tool result right away
                    return jsonify({"tool": tool_res.get("tool"), "result": tool_res.get("result"), "error": tool_res.get("error")})
            except Exception as e:
                return jsonify({"error": f"tool_error: {e}"}), 500

        # Fallback to LLM text response
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

