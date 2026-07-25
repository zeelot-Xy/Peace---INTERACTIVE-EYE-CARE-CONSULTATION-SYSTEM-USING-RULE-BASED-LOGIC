from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.schemas import ConsultationAnswerSchema, ConsultationRevisionSchema
from app.services.consultation_service import (
    cancel_consultation,
    clear_answer,
    complete_consultation,
    create_consultation,
    get_consultation,
    get_result,
    list_consultations,
    save_answer,
)
from app.utils.responses import error_response, success_response
from app.utils.validation import load_json

consultations_blueprint = Blueprint("consultations", __name__)


@consultations_blueprint.post("")
@jwt_required()
def create():
    return success_response(
        {"consultation": create_consultation(get_jwt_identity())}, 201
    )


@consultations_blueprint.get("")
@jwt_required()
def history():
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 20)), 1), 50)
    except ValueError:
        return error_response(
            "Pagination values must be integers.", 422, "validation_error"
        )
    return success_response(
        list_consultations(get_jwt_identity(), page=page, per_page=per_page)
    )


@consultations_blueprint.get("/<consultation_id>")
@jwt_required()
def detail(consultation_id: str):
    return success_response(
        {
            "consultation": get_consultation(
                get_jwt_identity(), consultation_id
            )
        }
    )


@consultations_blueprint.put("/<consultation_id>/responses/<question_id>")
@jwt_required()
def answer(consultation_id: str, question_id: str):
    data = load_json(ConsultationAnswerSchema())
    consultation = save_answer(
        get_jwt_identity(),
        consultation_id,
        question_id,
        answer=data["answer"],
        skip=data["skip"],
        expected_revision=data["revision"],
    )
    return success_response({"consultation": consultation})


@consultations_blueprint.delete("/<consultation_id>/responses/<question_id>")
@jwt_required()
def remove_answer(consultation_id: str, question_id: str):
    data = load_json(ConsultationRevisionSchema())
    consultation = clear_answer(
        get_jwt_identity(), consultation_id, question_id, data["revision"]
    )
    return success_response({"consultation": consultation})


@consultations_blueprint.post("/<consultation_id>/complete")
@jwt_required()
def complete(consultation_id: str):
    data = load_json(ConsultationRevisionSchema())
    return success_response(
        complete_consultation(
            get_jwt_identity(), consultation_id, data["revision"]
        )
    )


@consultations_blueprint.post("/<consultation_id>/cancel")
@jwt_required()
def cancel(consultation_id: str):
    data = load_json(ConsultationRevisionSchema())
    return success_response(
        {
            "consultation": cancel_consultation(
                get_jwt_identity(), consultation_id, data["revision"]
            )
        }
    )


@consultations_blueprint.get("/<consultation_id>/result")
@jwt_required()
def result(consultation_id: str):
    return success_response(
        {"result": get_result(get_jwt_identity(), consultation_id)}
    )
