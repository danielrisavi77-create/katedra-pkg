#!/usr/bin/env python3
"""Strict validators for review artifacts consumed by reviewer_simulation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REFS = HERE.parent / "references"
SCHEMAS = {
    "evidence": REFS / "evidence_gate_schema.json",
    "consistency": REFS / "cross_chapter_consistency_schema.json",
}

def _jsonschema():
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise ValueError("jsonschema nije dostupan; review contract nije izmjeren") from exc
    return Draft202012Validator

def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"dvostruki JSON ključ: {key}")
        out[key] = value
    return out

def invalid_constant(value):
    raise ValueError(f"nedopuštena JSON konstanta: {value}")

def _schema(kind: str) -> dict[str, Any]:
    if kind not in SCHEMAS:
        raise ValueError(f"nepoznata vrsta review izvještaja: {kind}")
    return json.loads(SCHEMAS[kind].read_text(encoding="utf-8"))

def validate_report(kind: str, payload: object) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"{kind} izvještaj mora biti JSON objekt")
    Validator = _jsonschema()
    errors = sorted(Validator(_schema(kind)).iter_errors(payload), key=lambda e: list(e.path))
    if errors:
        e = errors[0]
        path = ".".join(str(x) for x in e.path) or "<root>"
        raise ValueError(f"{kind} izvještaj nije valjan na {path}: {e.message}")
    if kind == "evidence":
        matrix = payload["matrix"]
        summary = payload["summary"]
        ids = [row["claim_id"] for row in matrix]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence izvještaj ima duplikat claim_id")
        passed_rows = sum(row["gate_status"] == "pass" for row in matrix)
        blocked_rows = sum(row["gate_status"] == "block" for row in matrix)
        if summary["claims"] != len(matrix):
            raise ValueError("evidence summary.claims ne odgovara matrici")
        # Strict empty-ledger precondition is the one producer-level exception:
        # blocked can be 1 while matrix is empty.
        empty_strict = (payload["policy"] == "strict" and not matrix
                        and bool(payload["preconditions"]) and not payload["passed"])
        if not empty_strict and summary["blocked"] != blocked_rows:
            raise ValueError("evidence summary.blocked ne odgovara matrici")
        if summary["passed"] != passed_rows:
            raise ValueError("evidence summary.passed ne odgovara matrici")
        if payload["passed"] and payload["policy"] == "strict":
            if not matrix or payload["preconditions"] or blocked_rows or summary["would_block"]:
                raise ValueError("strict evidence PASS nema potpune preduvjete")
    else:
        graph = payload["graph"]
        summary = payload["summary"]
        if summary["chapters"] != len(graph["nodes"]):
            raise ValueError("consistency summary.chapters ne odgovara grafu")
        if summary["edges"] != len(graph["edges"]):
            raise ValueError("consistency summary.edges ne odgovara grafu")
        if summary["findings"] != len(payload["findings"]):
            raise ValueError("consistency summary.findings ne odgovara nalazima")
        blocking = sum(x["severity"] == "blocking" for x in payload["findings"])
        if summary["blocking"] != blocking:
            raise ValueError("consistency summary.blocking ne odgovara nalazima")
        claim_ids = [cid for edge in graph["edges"] for cid in edge["claim_ids"]]
        if len(claim_ids) != len(set(claim_ids)) and len(graph["edges"]) == 1:
            raise ValueError("consistency edge ima duplikat claim_id")

def load_report(path: str | Path, kind: str) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"{kind} izvještaj ne postoji: {p}")
    try:
        payload = json.loads(
            p.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=invalid_constant,
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{kind} izvještaj nije čitljiv JSON: {p}: {exc}") from exc
    validate_report(kind, payload)
    return payload
