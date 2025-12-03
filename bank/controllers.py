from db import get_tuition as db_get_tuition, add_tuition_and_balance
from flask import Blueprint, jsonify, request, abort

bank_bp = Blueprint("bank_api", __name__)


@bank_bp.get("/ping")
def ping():
    return jsonify({"message": "pong"})


@bank_bp.get("/get_tuition")
def get_tuition_route():
    """Return student's total_tuition and balance as JSON.

    Query params:
    - id (int): student id (required)
    """
    id_str = request.args.get("id")
    if not id_str:
        return jsonify({"error": "id query parameter required"}), 400
    try:
        sid = int(id_str)
    except Exception:
        return jsonify({"error": "id must be an integer"}), 400

    try:
        tuition, balance = db_get_tuition(sid)
    except FileNotFoundError:
        return jsonify({"error": "student not found"}), 404

    return jsonify({"id": sid, "total_tuition": tuition, "balance": balance})


@bank_bp.post("/add_debt")
def add_debt():
    data = request.get_json() or {}
    try:
        sid = int(data.get("id"))
        tuition = float(data.get("tuition"))
        balance = float(data.get("balance"))
    except Exception:
        return jsonify({"error": "id, tuition, balance are required in JSON body"}), 400

    add_tuition_and_balance(sid, tuition, balance)
    return jsonify({"status": "ok"}), 200