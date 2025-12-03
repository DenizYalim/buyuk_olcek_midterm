from flask import Blueprint, jsonify, request
from uni_admin.services import get_all_unpaid, add_tuition as add_tuition_service, add_tuition_batch as add_tuition_batch_service

uni_admin_bp = Blueprint("admin_api", __name__)


@uni_admin_bp.post("/add_tuition")
def add_tuition():
    """
    adds tuition amount to id
    ---
    tags:
      - Admin
    parameters:
      - in: query
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Tuition added
      400:
        description: Invalid input
    """
    id_str = request.args.get("id")

    if not id_str:
        return {"error": "id required"}, 400

    try:
        sid = int(id_str)
    except:
        return {"error": "id must be integer"}, 400

    return add_tuition_service(sid)


@uni_admin_bp.post("/add_tuition_batch")
def add_tutiton_batch():
    """
    adds tuitions from csv
    ---
    tags:
      - Admin
    parameters:
      - in: query
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Tuition added
      400:
        description: Invalid input
    """
    pass

@uni_admin_bp.post("/get_unpaid_tuitions")
def get_unpaid_tuitions():
    page_num = request.args.get("page")
    """
    queries unpaid tuitions
    ---
    tags:
      - Admin
    parameters:
      - in: query
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Tuition added
      400:
        description: Invalid input
    """
    return get_all_unpaid(page_num)
