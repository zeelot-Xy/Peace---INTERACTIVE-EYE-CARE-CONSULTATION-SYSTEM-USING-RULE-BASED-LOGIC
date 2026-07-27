"""Executable checks for requirements-to-test evidence through Phase 12."""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MATRIX = PROJECT_ROOT / "docs" / "requirements-traceability.md"
REPORT = PROJECT_ROOT / "docs" / "requirements-to-test-report.md"
REQUIREMENT_ID = re.compile(r"^\| ([A-Z]+-\d{3}) \|", re.MULTILINE)


def test_every_requirement_has_detailed_test_evidence():
    matrix_ids = REQUIREMENT_ID.findall(MATRIX.read_text(encoding="utf-8"))
    report_text = REPORT.read_text(encoding="utf-8")

    assert matrix_ids
    assert len(matrix_ids) == len(set(matrix_ids))
    missing = [
        requirement_id
        for requirement_id in matrix_ids
        if f"`{requirement_id}`" not in report_text
    ]
    assert missing == []


def test_phase_10_evidence_names_reproducible_commands_and_scenarios():
    report_text = REPORT.read_text(encoding="utf-8")

    for expected in (
        "test_defence_demo.py",
        "test_quality_evidence.py",
        "App.test.tsx",
        "verify-phase10.ps1",
        "Patient safety-path demonstration",
        "Administrator governance demonstration",
    ):
        assert expected in report_text


def test_phase_11_evidence_names_security_and_privacy_gates():
    report_text = REPORT.read_text(encoding="utf-8")

    for expected in (
        "test_security.py",
        "verify-phase11.ps1",
        "Atomic refresh",
        "Audit redaction",
        "npm production advisory",
    ):
        assert expected in report_text


def test_phase_12_evidence_names_packaging_and_server_gates():
    report_text = REPORT.read_text(encoding="utf-8")

    for expected in (
        "test_runtime.py",
        "verify-phase12.ps1",
        "PyInstaller build",
        "volume persistence",
    ):
        assert expected in report_text
