from db import get_tuition as db_get_tuition, add_tuition_and_balance
from flask import Blueprint, jsonify, request, abort

bank_bp = Blueprint("bank_api", __name__)


@bank_bp.get("/ping")
def ping():
    return jsonify({"message": "pong"})


@bank_bp.get("/get_tuition")
def get_tuition_route():  
    id_str = request.args.get("id") # request parameters
    if not id_str:
        return jsonify({"error": "id required"}), 400 

    try:    
        sid = int(id_str)
    except Exception:
        return jsonify({"error": "id must be an integer"}), 400

    try:
        tuition, balance = db_get_tuition(sid)
    
    except FileNotFoundError: # öğrenci yoksa
        return jsonify({"error": "student not found"}), 404


    return jsonify({"id": sid, "total_tuition": tuition, "balance": balance})


@bank_bp.post("/add_debt")
def add_debt():
    data = request.get_json()

    try:
        sid = int(data.get("id"))
        tuition = float(data.get("tuition"))
        balance = float(data.get("balance"))
    except Exception:
        return jsonify({"error": "id, tuition, balance parameters are required"}), 400

    a = add_tuition_and_balance(sid, tuition, balance)
    return jsonify({"status": f"Success! For id:{sid}; tuition={a[0]}, balance={a[1]}"}), 200