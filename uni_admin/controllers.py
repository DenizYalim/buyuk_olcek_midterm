from flask import Blueprint, jsonify, request
from uni_admin.services import get_all_unpaid, add_tuition as add_tuition_service, add_tuition_batch as add_tuition_batch_service

# Use a distinct blueprint name to avoid endpoint collisions
uni_admin_bp = Blueprint("uni_admin", __name__)


@uni_admin_bp.get("/ping")
def ping():
    return jsonify({"message": "pong"})


@uni_admin_bp.post("/add_tuition")
def add_tuition():
    # Placeholder implementation
    return jsonify({"error": "not implemented"}), 501


@uni_admin_bp.post("/add_tuition_batch")
def add_tuition_batch():
    # Placeholder implementation for adding a batch of tuitions
    return jsonify({"error": "not implemented"}), 501


@uni_admin_bp.get("/get_unpaid_tuitions")
def get_unpaid_tuitions():
    # Placeholder implementation to return unpaid tuitions
    return jsonify({"error": "not implemented"}), 501
