from flask import Blueprint, jsonify, request
from mobile_uni.services import get_tuition, pay_tuition

mobile_uni_bp = Blueprint("mobile_api", __name__)


@mobile_uni_bp.get("/ask_tuition")
def ask_tuition():
    """
    Ask tuition
    ---
    tags:
      - Mobile
    parameters:
      - in: query
        name: id
        required: true
        type: integer
    responses:
      200:
        description: Tuition returned
      400:
        description: ID required
      500:
        description: Server error
    """
    id_str = request.args.get("id")
    if not id_str:
        return jsonify({"error": "id query parameter required"}), 400

    try:
        data = get_tuition(int(id_str))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data), 200


@mobile_uni_bp.post("/pay_tuition")
def pay_tuition():
    """
    Pay tuition
    ---
    tags:
      - Mobile
    parameters:
      - in: query
        name: id
        required: true
        type: integer
    responses:
      200:
        description: Payment success
      500:
        description: Payment failure
    """
    id_str = request.args.get("id")

    if pay_tuition(id_str):
        return jsonify({"message": "Sucessfully paid"}), 200
    else:
        return jsonify({"message": "Payment failure"}), 500
