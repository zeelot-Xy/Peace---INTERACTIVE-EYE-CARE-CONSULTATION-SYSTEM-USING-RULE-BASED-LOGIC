"""Immutable consultation report composition and secure retrieval."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from html import escape
from io import BytesIO
from pathlib import Path
from threading import Lock
from typing import Any

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.extensions import db
from app.models import ConsultationSession, Report, User
from app.services.audit_service import record_audit
from app.services.consultation_service import ConsultationStateError, _package_for


class ReportError(RuntimeError):
    code = "report_error"
    status_code = 400


class ReportNotFound(ReportError):
    code = "report_not_found"
    status_code = 404


_font_lock = Lock()
_fonts_registered = False


def _register_fonts() -> tuple[str, str]:
    global _fonts_registered
    with _font_lock:
        if not _fonts_registered:
            fonts = Path(reportlab.__file__).resolve().parent / "fonts"
            pdfmetrics.registerFont(TTFont("EyeCareSans", str(fonts / "Vera.ttf")))
            pdfmetrics.registerFont(TTFont("EyeCareSans-Bold", str(fonts / "VeraBd.ttf")))
            _fonts_registered = True
    return "EyeCareSans", "EyeCareSans-Bold"


def _answer_label(question: dict[str, Any], value: Any) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    for option in question.get("options", ()):
        if option["value"] == value:
            return str(option["label"])
    return str(value)


def _build_snapshot(
    consultation: ConsultationSession,
    patient: User,
    generated_at: datetime,
) -> dict[str, Any]:
    package = _package_for(consultation)
    questions = package.indexes["questions"]
    answers = []
    for response in sorted(consultation.responses, key=lambda item: item.created_at):
        question = questions.get(response.question_id)
        if question is None:
            continue
        value = response.answer["value"]
        answers.append(
            {
                "question_id": response.question_id,
                "prompt": question["prompt"],
                "answer": _answer_label(question, value),
                "raw_value": value,
            }
        )
    return {
        "schema_version": "1.0",
        "generated_at": generated_at.isoformat(),
        "patient": {
            "id": patient.id,
            "full_name": patient.full_name,
            "email": patient.email,
            "phone": patient.phone,
            "date_of_birth": (
                patient.date_of_birth.isoformat() if patient.date_of_birth else None
            ),
        },
        "consultation": {
            "id": consultation.id,
            "created_at": consultation.created_at.isoformat(),
            "completed_at": (
                consultation.completed_at.isoformat()
                if consultation.completed_at
                else None
            ),
            "knowledge": {
                "package_id": consultation.knowledge_package_id,
                "content_version": consultation.knowledge_version,
                "fingerprint": consultation.knowledge_fingerprint,
            },
            "answers": answers,
            "skipped_question_ids": list(
                consultation.skipped_question_ids or ()
            ),
        },
        "result": consultation.result_snapshot,
    }


def _paragraph(value: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(value or "Not provided")), style)


def _item_list(
    items: list[dict[str, Any]],
    style: ParagraphStyle,
    *,
    title_field: str = "title",
    detail_fields: tuple[str, ...] = ("message", "summary", "explanation"),
) -> ListFlowable | Paragraph:
    if not items:
        return Paragraph("None recorded.", style)
    entries = []
    for item in items:
        title = (
            item.get(title_field)
            or item.get("name")
            or item.get("risk_label")
            or item.get("id")
            or "Item"
        )
        detail = next(
            (item.get(field) for field in detail_fields if item.get(field)),
            None,
        )
        text = f"<b>{escape(str(title))}</b>"
        if detail:
            text += f"<br/>{escape(str(detail))}"
        entries.append(ListItem(Paragraph(text, style), leftIndent=4 * mm))
    return ListFlowable(
        entries,
        bulletType="bullet",
        bulletFontName=style.fontName,
        leftIndent=6 * mm,
    )


def render_report_pdf(snapshot: dict[str, Any]) -> bytes:
    regular, bold = _register_fonts()
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=19 * mm,
        bottomMargin=19 * mm,
        title="Eye Care Consultation Report",
        author="EyeCare Guide",
        subject="Educational eye-care consultation guidance",
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "EyeBody",
        parent=styles["BodyText"],
        fontName=regular,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#263648"),
        spaceAfter=4 * mm,
    )
    heading = ParagraphStyle(
        "EyeHeading",
        parent=styles["Heading2"],
        fontName=bold,
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
    )
    title = ParagraphStyle(
        "EyeTitle",
        parent=styles["Title"],
        fontName=bold,
        fontSize=24,
        leading=29,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0f4c5c"),
        spaceAfter=4 * mm,
    )
    small = ParagraphStyle(
        "EyeSmall",
        parent=body,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#526273"),
    )
    warning = ParagraphStyle(
        "EyeWarning",
        parent=body,
        fontName=bold,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#7f1d1d"),
        borderColor=colors.HexColor("#dc2626"),
        borderWidth=1,
        borderPadding=8,
        backColor=colors.HexColor("#fef2f2"),
    )
    table_header = ParagraphStyle(
        "EyeTableHeader",
        parent=body,
        fontName=bold,
        textColor=colors.white,
        spaceAfter=0,
    )

    patient = snapshot["patient"]
    consultation = snapshot["consultation"]
    result = snapshot["result"] or {}
    risk = result.get("overall_risk") or {}
    story: list[Any] = [
        Paragraph("Eye Care Consultation Report", title),
        Paragraph(
            "Educational decision support - this report is not a diagnosis or prescription.",
            ParagraphStyle("Subtitle", parent=small, alignment=TA_CENTER),
        ),
        Spacer(1, 5 * mm),
        Paragraph("Important safety notice", heading),
        Paragraph(
            result.get("disclaimer")
            or "Seek qualified professional care for symptoms that concern you.",
            warning,
        ),
        Paragraph("Patient and consultation details", heading),
    ]
    details = [
        ["Patient", patient["full_name"], "Email", patient["email"]],
        [
            "Date of birth",
            patient.get("date_of_birth") or "Not provided",
            "Phone",
            patient.get("phone") or "Not provided",
        ],
        [
            "Completed",
            consultation.get("completed_at") or "Not recorded",
            "Knowledge version",
            consultation["knowledge"].get("content_version") or "Not recorded",
        ],
        ["Consultation ID", consultation["id"], "Report generated", snapshot["generated_at"]],
    ]
    detail_table = Table(
        [[_paragraph(cell, body) for cell in row] for row in details],
        colWidths=[29 * mm, 55 * mm, 31 * mm, 56 * mm],
        repeatRows=0,
    )
    detail_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), regular),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e6fffb")),
                ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e6fffb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c5cf")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([detail_table, Paragraph("Recommended action level", heading)])
    risk_text = (
        f"<b>{escape(str(risk.get('label') or 'No specific pathway matched'))}</b>"
    )
    if risk.get("action_window"):
        risk_text += f"<br/>{escape(str(risk['action_window']))}"
    story.append(Paragraph(risk_text, body))

    story.extend(
        [
            Paragraph("Important warning signs", heading),
            _item_list(result.get("red_flags", []), body),
            Paragraph("Recommended next steps", heading),
            _item_list(result.get("recommendations", []), body),
            Paragraph("Possible indications", heading),
            Paragraph(
                "These are symptom patterns produced by authored rules, not diagnoses.",
                small,
            ),
            _item_list(
                result.get("possible_indications", []),
                body,
                title_field="possible_indication_label",
            ),
            CondPageBreak(75 * mm),
            Paragraph("Consultation responses", heading),
        ]
    )
    answer_rows = [
        [
            _paragraph("Question", table_header),
            _paragraph("Recorded answer", table_header),
        ]
    ]
    for answer in consultation["answers"]:
        answer_rows.append(
            [
                _paragraph(answer["prompt"], body),
                _paragraph(answer["answer"], body),
            ]
        )
    answer_table = Table(
        answer_rows,
        colWidths=[125 * mm, 46 * mm],
        repeatRows=1,
    )
    answer_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), regular),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c7d2da")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.extend(
        [
            answer_table,
            Paragraph("Rule-based explanation", heading),
            Paragraph(result.get("match_score_notice") or "", small),
            _item_list(
                result.get("matched_rules", []),
                body,
                title_field="name",
                detail_fields=("explanation", "rationale"),
            ),
            Paragraph("Sources", heading),
        ]
    )
    source_blocks = []
    for source in result.get("evidence", []):
        source_text = f"<b>{escape(str(source.get('title') or source.get('id')))}</b>"
        if source.get("organization"):
            source_text += f" - {escape(str(source['organization']))}"
        if source.get("url"):
            source_text += f"<br/>{escape(str(source['url']))}"
        source_blocks.append(ListItem(Paragraph(source_text, small), leftIndent=4 * mm))
    story.append(
        ListFlowable(
            source_blocks,
            bulletType="bullet",
            bulletFontName=small.fontName,
            leftIndent=6 * mm,
        )
        if source_blocks
        else Paragraph("No source references recorded.", body)
    )
    story.extend(
        [
            Paragraph("Inference provenance", heading),
            Paragraph(
                "Knowledge fingerprint: "
                + escape(str(consultation["knowledge"].get("fingerprint"))),
                small,
            ),
            Paragraph(
                "The complete immutable result and inference trace are retained with this report.",
                small,
            ),
        ]
    )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(regular, 7.5)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(18 * mm, 10 * mm, "EyeCare Guide - educational support only")
        canvas.drawRightString(192 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()


def _metadata(report: Report) -> dict[str, Any]:
    snapshot = report.snapshot
    result = snapshot.get("result") or {}
    return {
        "id": report.id,
        "consultation_id": report.consultation_id,
        "filename": report.filename,
        "content_type": report.content_type,
        "sha256": report.pdf_sha256,
        "generated_at": report.generated_at.isoformat(),
        "risk": result.get("overall_risk"),
        "knowledge_version": snapshot["consultation"]["knowledge"].get(
            "content_version"
        ),
        "download_url": f"/api/v1/reports/{report.id}/download",
    }


def create_report(user_id: str, consultation_id: str) -> tuple[dict[str, Any], bool]:
    existing = db.session.scalar(
        db.select(Report).where(
            Report.consultation_id == consultation_id,
            Report.user_id == user_id,
        )
    )
    if existing is not None:
        return _metadata(existing), False
    consultation = db.session.scalar(
        db.select(ConsultationSession).where(
            ConsultationSession.id == consultation_id,
            ConsultationSession.user_id == user_id,
        )
    )
    if consultation is None:
        raise ReportNotFound("Consultation was not found.")
    if consultation.status != "completed" or consultation.result_snapshot is None:
        raise ConsultationStateError(
            "A report can only be generated for a completed consultation."
        )
    patient = db.session.get(User, user_id)
    generated_at = datetime.now(UTC)
    snapshot = _build_snapshot(consultation, patient, generated_at)
    pdf_data = render_report_pdf(snapshot)
    filename = (
        f"eye-care-report-{generated_at:%Y%m%d}-{consultation.id[:8]}.pdf"
    )
    report = Report(
        consultation_id=consultation.id,
        user_id=user_id,
        snapshot=snapshot,
        filename=filename,
        content_type="application/pdf",
        pdf_sha256=hashlib.sha256(pdf_data).hexdigest(),
        pdf_data=pdf_data,
        generated_at=generated_at,
    )
    db.session.add(report)
    db.session.flush()
    record_audit(
        "report.generate",
        actor_user_id=user_id,
        resource_type="report",
        resource_id=report.id,
        event_data={
            "consultation_id": consultation.id,
            "knowledge_fingerprint": consultation.knowledge_fingerprint,
            "pdf_sha256": report.pdf_sha256,
        },
    )
    db.session.commit()
    return _metadata(report), True


def _accessible_report(report_id: str, user_id: str, role: str) -> Report:
    statement = db.select(Report).where(Report.id == report_id)
    if role != "admin":
        statement = statement.where(Report.user_id == user_id)
    report = db.session.scalar(statement)
    if report is None:
        raise ReportNotFound("Report was not found.")
    return report


def get_report(report_id: str, user_id: str, role: str) -> dict[str, Any]:
    return _metadata(_accessible_report(report_id, user_id, role))


def get_report_file(
    report_id: str, user_id: str, role: str
) -> tuple[bytes, str, str]:
    report = _accessible_report(report_id, user_id, role)
    record_audit(
        "report.download",
        actor_user_id=user_id,
        resource_type="report",
        resource_id=report.id,
    )
    db.session.commit()
    return report.pdf_data, report.filename, report.content_type


def list_reports(
    user_id: str,
    role: str,
    *,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    statement = db.select(Report).order_by(Report.generated_at.desc(), Report.id)
    if role != "admin":
        statement = statement.where(Report.user_id == user_id)
    pagination = db.paginate(
        statement,
        page=page,
        per_page=per_page,
        max_per_page=50,
        error_out=False,
    )
    return {
        "items": [_metadata(report) for report in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    }
