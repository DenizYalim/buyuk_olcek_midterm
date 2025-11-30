from flask import Blueprint, jsonify, request

uni_admin_bp = Blueprint("api", __name__)


@uni_admin_bp.get("/ping")
def ping():
    return jsonify({"message": "pong"})

@uni_admin_bp.post("/add_tuition")
def add_tuition(): 
    pass

@uni_admin_bp.post("/add_tuition_batch")
def add_debt():
    pass

@uni_admin_bp.get("/get_unpaid_tuitions")
def add_debt():
    pass
