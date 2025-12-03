from flask import Blueprint, jsonify, request
from . import services

mobile_uni_bp = Blueprint("mobile_api", __name__)


@mobile_uni_bp.get("/ping")
def ping():
    return jsonify({"message": "pong"})


@mobile_uni_bp.get("/ask_tuition")
def ask_tuition():
    id_str = request.args.get("id")
    if not id_str:
        return jsonify({"error": "id query parameter required"}), 400

    try:
        data = services.get_tuition(int(id_str))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data), 200


@mobile_uni_bp.post("/pay_tuition")
def pay_tuition():
    return jsonify({"error": "not implemented"}), 501