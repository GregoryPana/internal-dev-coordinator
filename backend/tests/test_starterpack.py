"""Tests for the deterministic starter-pack generator (T7): FR-016 file
list is frozen, no AI, template selection varies by project_type."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.audit.models import AuditEvent
from app.vocab import (
    AuditActionType,
    Classification,
    Priority,
    ProjectPhase,
    ProjectStatus,
    ProjectType,
    Role,
)

FR_016_FILES = {
    "README.md",
    "EXIT.md",
    "OPENCODE.md",
    "CLAUDE.md",
    "AGENTS.md",
    "docs/PROJECT_SCOPE.md",
    "docs/ARCHITECTURE.md",
    "docs/DATA_MODEL.md",
    "docs/DEPLOYMENT.md",
    "docs/OPERATIONS.md",
    "docs/VERIFICATION_MATRIX.md",
}

INTAKE_PAYLOAD = {
    "users": "Internal ops staff",
    "workflow": "Track and resolve customer tickets",
    "data_sensitivity": "Internal customer data, no payment details",
    "integrations": "Existing CRM",
    "deployment_target": "Internal VM",
    "notes": "MVP only",
}


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def _create_project(client: TestClient, admin_email: str, **overrides) -> dict:
    payload = {
        "name": "Starter Pack Test Project",
        "project_type": ProjectType.INTERNAL_WEB_APP.value,
        "classification": Classification.REUSABLE.value,
        "phase": ProjectPhase.CONCEPT.value,
        "status": ProjectStatus.ACTIVE.value,
        "priority": Priority.MEDIUM.value,
        **overrides,
    }
    resp = client.post("/api/projects", json=payload, headers=_headers(admin_email))
    assert resp.status_code == 201
    return resp.json()


def test_preview_generates_exactly_the_fr016_file_list(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/preview",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 200
    body = resp.json()
    paths = {f["path"] for f in body["files"]}
    assert paths == FR_016_FILES


def test_preview_content_reflects_project_and_intake(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/preview",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    files = {f["path"]: f["content"] for f in resp.json()["files"]}
    assert "Starter Pack Test Project" in files["README.md"]
    assert "Internal ops staff" in files["AGENTS.md"]
    assert "Internal VM" in files["docs/DEPLOYMENT.md"]
    assert "Internal customer data" in files["EXIT.md"]


def test_template_selection_varies_by_project_type(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    web_app = _create_project(client, admin.email, name="Web App Variant", project_type="internal-web-app")
    tool = _create_project(client, admin.email, name="Tool Variant", project_type="operational-tool")
    prototype = _create_project(client, admin.email, name="Prototype Variant", project_type="prototype")

    def deployment_text(project_id: int) -> str:
        resp = client.post(
            f"/api/projects/{project_id}/starter-pack/preview",
            json=INTAKE_PAYLOAD,
            headers=_headers(admin.email),
        )
        files = {f["path"]: f["content"] for f in resp.json()["files"]}
        return files["docs/DEPLOYMENT.md"]

    web_app_deploy = deployment_text(web_app["id"])
    tool_deploy = deployment_text(tool["id"])
    prototype_deploy = deployment_text(prototype["id"])

    assert "NGINX" in web_app_deploy
    assert "NGINX" not in tool_deploy
    assert "Local/developer machine only" in prototype_deploy
    assert web_app_deploy != tool_deploy != prototype_deploy


def test_required_docs_reflect_project_type_in_data_model_and_agents(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    prototype = _create_project(client, admin.email, name="Prototype Docs", project_type="prototype")

    resp = client.post(
        f"/api/projects/{prototype['id']}/starter-pack/preview",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    files = {f["path"]: f["content"] for f in resp.json()["files"]}
    # prototype only requires agent_guide + exit_md per REQUIRED_DOC_PROFILES
    assert "agent_guide" in files["docs/DATA_MODEL.md"]
    assert "exit_md" in files["docs/DATA_MODEL.md"]
    assert "user_guide" not in files["docs/DATA_MODEL.md"]


def test_preview_generation_is_audited(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    client.post(
        f"/api/projects/{project['id']}/starter-pack/preview",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )

    audit = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.project_id == project["id"],
            AuditEvent.action_type == AuditActionType.STARTER_PACK_GENERATED,
        )
        .one()
    )
    assert audit.metadata_json["file_count"] == 11


def test_developer_non_member_cannot_generate_preview(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    dev = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()
    project = _create_project(client, admin.email)

    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/preview",
        json=INTAKE_PAYLOAD,
        headers=_headers(dev.email),
    )
    assert resp.status_code == 403


def test_preview_for_missing_project_is_404(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    resp = client.post(
        "/api/projects/999999/starter-pack/preview",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 404


def test_intake_missing_required_field_is_422(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    bad_intake = {k: v for k, v in INTAKE_PAYLOAD.items() if k != "workflow"}
    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/preview",
        json=bad_intake,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 422
