from flask import Blueprint, jsonify, request

mobile_uni_bp = Blueprint("api", __name__)


@mobile_uni_bp.get("/ping")
def ping():
    return jsonify({"message": "pong"})


@mobile_uni_bp.get("/ask_tuition")
def add_tuition(): 
    pass

@mobile_uni_bp.post("/pay_tuition")
def add_debt():
    pass 