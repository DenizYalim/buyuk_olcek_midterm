from db import get_tuition, add_tuition_and_balance
from flask import Blueprint, jsonify, request

bank_bp = Blueprint("api", __name__)


@bank_bp.get("/ping")
def ping():
    return jsonify({"message": "pong"})

@bank_bp.get("/get_tuition")
def get_tuition():
    return get_tuition(id=id)

@bank_bp.post("/add_debt")
def add_debt():
    return add_tuition_and_balance(id=id, tuition=tuition, balance=balance)