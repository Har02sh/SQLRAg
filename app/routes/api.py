from flask import Blueprint, jsonify, request
from app.services.sqlRagChat import answer_user_question

api_bp = Blueprint('api', __name__)

@api_bp.route('/teleData', methods=['POST'])
def teleData():
    data = request.get_json()
    question = data.get('question')
    response = answer_user_question(question)
    return jsonify(response)