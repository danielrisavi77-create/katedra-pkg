import json, os, sys, tempfile, shutil
import pytest
HERE = os.path.dirname(os.path.abspath(__file__)); SVC = os.path.dirname(HERE)
sys.path.insert(0, SVC)
PKG = os.environ.get("KATEDRA_PKG_HOME", os.path.abspath(os.path.join(SVC, "..")))
SCRIPTS = os.path.join(PKG, "katedra-lite", "scripts")
from manuscript_to_katedra import tiptap_to_markdown, write_katedra
from gate_mapping import map_gate

FIX = json.load(open(os.path.join(HERE, "fixture_manuscript.json"), encoding="utf-8"))
PLAN = {"thesis": "Obvezno glasanje povećava formalnu, ali ne i percipiranu legitimnost izbora.", "question": "Kako obvezno glasanje utječe na percipiranu legitimnost?", "chapters": [{"sectionId": "s1", "pages": 2, "content": "kontekst, pitanje, teza, metoda, pregled", "sources": ["src-1"]}, {"sectionId": "s2", "pages": 6, "content": "pojmovi legitimnosti i odaziva", "sources": ["src-1"]}, {"sectionId": "s9", "pages": 2, "content": "odgovor na pitanje, doprinos, ograničenja", "sources": ["src-1"]}], "perspectives": [{"label": "Institucionalna", "position": "odaziv jednak legitimnosti", "why": "Lijphart 1997"}, {"label": "Bihevioralna", "position": "prisila ne mijenja stav", "why": "Birch 2009"}]}
HINT = {"label": "FPZG diplomski", "status": "verified", "citation": "fpzg", "wordMin": 10000, "wordMax": 15000, "minReferences": 15, "sections": ["sažetak", "uvod", "zaključak", "literatura"]}


def test_tiptap_markdown_keeps_marks_lists_tables():
    md = tiptap_to_markdown(FIX["sections"][1]["content"])
    assert "**institucionalna mjera**" in md
    assert "## Istraživačko pitanje" in md
    assert "- prva stavka" in md and "- druga stavka" in md
    assert "[TREBA IZVOR]" in md
    md2 = tiptap_to_markdown(FIX["sections"][3]["content"])
    assert "| Država | Odaziv |" in md2 and "|---|---|" in md2


def test_write_katedra_creates_state_profile_chapters():
    root = tempfile.mkdtemp()
    try:
        out = write_katedra(FIX, root, HINT, SCRIPTS, mod="pisanje", plan_approved=True, plan=PLAN)
        kat = os.path.join(root, ".katedra")
        assert os.path.exists(os.path.join(kat, "stanje.json"))
        st = json.load(open(os.path.join(kat, "stanje.json")))
        assert st["mod"] == "pisanje" and st["plan_odobren"] is True and st["tip"] == "diplomski" and st["citatni_stil"] == "autor-godina" and st["fakultet_admisija"] == "nije-admitiran"
        prof = json.load(open(os.path.join(kat, "resolved_profile.json")))
        assert prof["status"] == "nepotvrdeno" and prof["provenance"]["default"] == "katedra-pack"
        files = sorted(os.listdir(os.path.join(kat, "poglavlja")))
        assert files == ["01-sazetak.md", "02-uvod.md", "03-teorijski-okvir.md", "04-zakljucak.md", "literatura.md"]
        assert open(os.path.join(kat, "poglavlja", "02-uvod.md"), encoding="utf-8").read().startswith("# Uvod\n")
        izv = json.load(open(os.path.join(kat, "izvori.json")))
        assert izv["izvori"][0]["doi"] == "10.2307/2952255" and izv["izvori"][0]["verification"]["status"] == "verified"
        assert len(out["poglavlja"]) == 5
    finally:
        shutil.rmtree(root)


def test_map_gate_statuses():
    g = {"faza": "pisanje", "koraci": [{"korak": "argument", "naziv": "teza", "stanje": "nalaz", "blokira": True, "izlaz": "nema teze"}], "sazetak": {}}
    assert map_gate(g, attempt=1)["status"] == "needs_revision"
    assert map_gate(g, attempt=3)["status"] == "blocked"
    g2 = {"faza": "pisanje", "koraci": [{"korak": "evidence", "naziv": "strict", "stanje": "preskoceno", "blokira": True}], "sazetak": {"preskok_dopusten": {}}}
    assert map_gate(g2)["status"] == "blocked" and map_gate(g2)["issues"][0]["code"] == "gate_step_skipped"
    g3 = {"faza": "plan", "koraci": [{"korak": "x", "naziv": "x", "stanje": "ok", "blokira": True}, {"korak": "y", "naziv": "y", "stanje": "nalaz", "blokira": False, "izlaz": "savjet"}], "sazetak": {}}
    r = map_gate(g3)
    assert r["status"] == "verified" and len(r["issues"]) == 1 and r["issues"][0]["blocking"] is False


def test_end_to_end_gate_pisanje_runs_without_model():
    pytest.importorskip("fastapi")
    from app import _verify_job, VerifyRequest
    res = _verify_job(VerifyRequest(runId="r", agent="writing", attempt=1, manuscript=FIX, profile=HINT, planApproved=True, plan=PLAN, **approval_fields()))
    assert res["gate"]["faza"] == "pisanje"
    assert res["status"] in ("verified", "needs_revision", "blocked")
    assert res["conversion"]["poglavlja"] == 5
    ids = {k["korak"] for k in res["gate"]["koraci"]}
    assert "argument" in ids and "stil" in ids
    # forma se ne pokreće u servisu
    assert not any(i["step"] == "pravila" and i["code"] == "gate_finding" for i in res["issues"])


@pytest.mark.parametrize("agent,faza", [("intake", "plan"), ("review", "audit"), ("export", "predaja")])
def test_all_phases_run_end_to_end(agent, faza):
    """Isporučeni test pokrivao je samo `writing`; `review` je padao (mod=audit prije rad.docx),
    `export` je padao na cp1250 (subprocess bez encoding=). Izmjereno 7. 9. 2026."""
    pytest.importorskip("fastapi")
    from app import _verify_job, VerifyRequest
    res = _verify_job(VerifyRequest(runId="r", agent=agent, attempt=1, manuscript=FIX, profile=HINT, planApproved=True, plan=PLAN, **approval_fields()))
    assert res["gate"]["faza"] == faza
    assert res["status"] in ("verified", "needs_revision", "blocked"), res
    assert res["conversion"]["docxError"] is None
    assert res["gate"]["koraci"], "gate nije vratio korake"


def test_docx_build_failure_is_failed_not_verified(monkeypatch):
    """Bez rad.docx koraci nad dokumentom se preskaču, a u fazi pisanje su savjetni: rezultat je
    bio `verified` uz 5 od 9 preskočenih koraka (izmjereno 7. 9. 2026.). Verifikator koji nije
    provjerio ne smije reći da je provjerio."""
    pytest.importorskip("fastapi")
    import app as A
    def pukni(root, manuscript, out):
        raise RuntimeError("build_docx.py pao (2): proba")
    monkeypatch.setattr(A, "_build_docx", pukni)
    res = A._verify_job(A.VerifyRequest(runId="r", agent="writing", attempt=1, manuscript=FIX, profile=HINT, planApproved=True, plan=PLAN, **approval_fields()))
    assert res["status"] == "failed"
    assert res["issues"] and res["issues"][0]["code"] == "verifier_error" and res["issues"][0]["blocking"] is True
    assert "rad.docx" in res["issues"][0]["message"]
    assert res["conversion"]["docxError"]


def test_sp_decodes_utf8_child_output():
    """cp1250 konzola (Windows): bez encoding= čitač izlaza pukne na bajtu 0x98 i r.stdout je None
    (katedra-lite kvar 119). U+2018 je u UTF-8 E2 80 98 — točno taj bajt."""
    import manuscript_to_katedra as M
    r = M._sp([sys.executable, "-c", "print(chr(8216) + 'x')"])
    assert r.returncode == 0 and r.stdout is not None and r.stdout.strip() == chr(8216) + "x", (r.stdout, r.stderr)


def test_run_decodes_utf8_child_output(tmp_path):
    pytest.importorskip("fastapi")
    import app as A
    r = A._run([sys.executable, "-c", "print(chr(8216) + 'x')"], str(tmp_path))
    assert r.returncode == 0 and r.stdout is not None and r.stdout.strip() == chr(8216) + "x", (r.stdout, r.stderr)


def test_claims_bridge_feeds_strict_evidence_gate():
    """Druga linija, most: tvrdnja s potporom se poveže (linked 1), tvrdnja bez potpore blokira korak evidence."""
    pytest.importorskip("fastapi")
    from app import _verify_job, VerifyRequest
    agent_result = {"agent": "writing", "output": "x", "citations": [], "provider": "p", "usage": {"inputTokens": 1, "outputTokens": 1},
                    "claims": [{"id": "clm_app1", "text": "Odaziv u Belgiji premašuje 85 %.", "citationIds": ["src-1"],
                                "support": [{"citationId": "src-1", "quote": "Turnout in Belgium exceeds 85 percent under compulsory voting.", "locator": "str. 4"}]},
                               {"id": "clm_app2", "text": "Tvrdnja bez ikakve potpore.", "citationIds": [], "support": []}]}
    res = _verify_job(VerifyRequest(runId="r", agent="writing", manuscript=FIX, profile=HINT, planApproved=True, plan=PLAN, **approval_fields(), agentResult=agent_result))
    led = res["conversion"]["ledger"]
    assert led.get("claims") == 2 and led.get("evidence", 0) >= 1 and led.get("linked") == 1, led
    ev = next(i for i in res["issues"] if i["step"] == "evidence")
    assert ev["code"] == "gate_finding" and ev["blocking"] is True   # nepoduprta tvrdnja blokira
    # brojač `linked` je servisov; mjerodavan je GATE: poduprta tvrdnja ne smije biti u nalazu (mutacija bez `link` prošla je kroz brojač)
    assert "clm_app2" in ev["message"] and "clm_app1" not in ev["message"], ev["message"]
    assert res["status"] in ("needs_revision", "blocked")


def test_bridge_run_decodes_utf8_child_output():
    """claims_bridge je stigao s istim subprocess bez encoding= (kvar 119, treći put): U+2018 = E2 80 98."""
    import claims_bridge as B
    r = B._run([sys.executable, "-c", "print(chr(8216) + 'x')"], "proba")
    assert r.stdout is not None and r.stdout.strip() == chr(8216) + "x", (r.stdout, r.stderr)



def approval_fields():
    return {"planRevision": "a" * 64, "planApproval": {
        "schemaVersion": 1, "runId": "r", "projectId": "project-1",
        "planRevision": "a" * 64, "approvedBy": "user-1",
        "approvedAt": "2026-01-01T00:00:00.000Z",
    }}


@pytest.fixture
def http_client(monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    import app as A
    monkeypatch.setattr(A, "TOKEN", "test-worker-token")
    with TestClient(A.app) as client:
        yield client


def request_body(**changes):
    body = {"runId": "r", "agent": "writing", "manuscript": FIX,
            "profile": HINT, "plan": PLAN, "planApproved": True,
            "planReady": True, **approval_fields()}
    body.update(changes)
    return body


@pytest.mark.parametrize("phase", ["pisanje", "audit", "predaja"])
@pytest.mark.parametrize("invalid", [
    "missing", "wrong_run", "wrong_project", "wrong_revision", "empty_revision",
    "invalid_revision", "missing_project", "empty_actor", "wrong_actor_type",
    "wrong_schema", "boolean_schema", "invalid_time", "future_time", "naive_time",
    "missing_time", "wrong_record_type", "text_only", "readiness_only",
])
def test_http_requires_bound_user_approval_before_conversion(http_client, monkeypatch, phase, invalid):
    import app as A
    body = request_body(phase=phase)
    approval = body["planApproval"]
    if invalid == "missing":
        del body["planApproval"]
    elif invalid == "wrong_run":
        approval["runId"] = "another-run"
    elif invalid == "wrong_project":
        approval["projectId"] = "another-project"
    elif invalid == "wrong_revision":
        approval["planRevision"] = "b" * 64
    elif invalid == "empty_revision":
        body["planRevision"] = approval["planRevision"] = ""
    elif invalid == "invalid_revision":
        body["planRevision"] = approval["planRevision"] = "not-a-sha256"
    elif invalid == "missing_project":
        body["manuscript"] = {k: v for k, v in FIX.items() if k != "projectId"}
    elif invalid == "empty_actor":
        approval["approvedBy"] = "   "
    elif invalid == "wrong_actor_type":
        approval["approvedBy"] = 42
    elif invalid == "wrong_schema":
        approval["schemaVersion"] = 2
    elif invalid == "boolean_schema":
        approval["schemaVersion"] = True
    elif invalid == "invalid_time":
        approval["approvedAt"] = "not-a-date"
    elif invalid == "future_time":
        approval["approvedAt"] = "2999-01-01T00:00:00Z"
    elif invalid == "naive_time":
        approval["approvedAt"] = "2026-01-01T00:00:00"
    elif invalid == "missing_time":
        del approval["approvedAt"]
    elif invalid == "wrong_record_type":
        body["planApproval"] = "approved"
    elif invalid == "text_only":
        del body["planApproval"]
        body["agentResult"] = {"output": "Student approved this plan", "planApproval": approval}
    elif invalid == "readiness_only":
        del body["planApproval"]
        body["planApproved"] = False
    def forbidden(*args, **kwargs):
        raise AssertionError("unapproved request reached conversion or DOCX build")
    monkeypatch.setattr(A, "write_katedra", forbidden)
    monkeypatch.setattr(A, "_build_docx", forbidden)
    response = http_client.post("/v1/verify?wait=1", json=body,
                                headers={"x-katedra-worker-token": "test-worker-token"})
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    assert result["status"] == "blocked"
    assert result["gate"]["faza"] == phase
    assert "gateExitCode" not in result
    assert result["issues"][0]["code"] == "gate_finding"
    assert result["issues"][0]["step"] == "plan_approval"
    assert result["issues"][0]["blocking"] is True


def test_http_bound_approval_runs_real_gate_even_without_legacy_boolean(http_client):
    response = http_client.post("/v1/verify?wait=1", json=request_body(planApproved=False),
                                headers={"x-katedra-worker-token": "test-worker-token"})
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    assert result["status"] in ("verified", "needs_revision", "blocked")
    assert result["conversion"]["poglavlja"] == 5
    assert result["gate"]["koraci"]
    assert not any(i.get("step") == "plan_approval" for i in result["issues"])


def test_http_plan_phase_does_not_impersonate_user_without_record(http_client, monkeypatch):
    import manuscript_to_katedra as M
    def forbidden(*args, **kwargs):
        raise AssertionError("plan phase invoked user approval without a bound record")
    monkeypatch.setattr(M, "_plan_from_sections", forbidden)
    response = http_client.post("/v1/verify?wait=1",
                                json=request_body(agent="planning", planApproval=None),
                                headers={"x-katedra-worker-token": "test-worker-token"})
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    assert result["gate"]["faza"] == "plan"
    assert result["gate"]["koraci"]
    assert result["conversion"]["poglavlja"] == 5


def test_http_approval_record_still_requires_worker_authentication(http_client, monkeypatch):
    import app as A
    def forbidden(*args, **kwargs):
        raise AssertionError("unauthenticated request reached verification")
    monkeypatch.setattr(A, "_verify_job", forbidden)
    response = http_client.post("/v1/verify?wait=1", json=request_body())
    assert response.status_code == 401
