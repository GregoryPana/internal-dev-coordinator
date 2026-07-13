"""Unit tests for the authz choke point (no DB round-trips where avoidable)."""

from unittest.mock import MagicMock

from app.authz import service as authz
from app.registry.models import Person, Project
from app.vocab import Role


def _user(role: Role, id: int = 1) -> Person:
    return Person(id=id, name="Test", email=f"t{id}@cws.sc", role_type=role, active=True)


def _project(owner_id: int | None = None) -> Project:
    p = Project(id=10)
    p.owner_id = owner_id
    return p


def _db(member: bool) -> MagicMock:
    db = MagicMock()
    db.scalar.return_value = 1 if member else None
    return db


def test_admin_reads_and_updates_everything() -> None:
    admin = _user(Role.ADMIN)
    assert authz.can_read_project(_db(False), admin, _project())
    assert authz.can_update_project(_db(False), admin, _project())
    assert authz.can_create_project(admin)


def test_manager_and_auditor_read_only() -> None:
    for role in (Role.MANAGER, Role.AUDITOR):
        user = _user(role)
        assert authz.can_read_project(_db(False), user, _project())
        assert not authz.can_update_project(_db(False), user, _project())
        assert not authz.can_create_project(user)


def test_developer_scoped_to_membership() -> None:
    dev = _user(Role.DEVELOPER_PROJECT_OWNER, id=5)
    assert not authz.can_read_project(_db(False), dev, _project())
    assert authz.can_read_project(_db(True), dev, _project())
    assert authz.can_update_project(_db(True), dev, _project())
    # owner shortcut without membership row
    assert authz.can_read_project(_db(False), dev, _project(owner_id=5))
    assert authz.can_create_project(dev)


def test_trainee_reads_assigned_only_never_updates() -> None:
    trainee = _user(Role.TRAINEE)
    assert not authz.can_read_project(_db(False), trainee, _project())
    assert authz.can_read_project(_db(True), trainee, _project())
    assert not authz.can_update_project(_db(True), trainee, _project())


def test_end_user_no_project_access_in_mvp() -> None:
    end_user = _user(Role.END_USER)
    assert not authz.can_read_project(_db(True), end_user, _project())
    assert not authz.can_update_project(_db(True), end_user, _project())


def test_ai_service_account_inherits_membership_boundary() -> None:
    ai = _user(Role.AI_SERVICE_ACCOUNT)
    assert not authz.can_read_project(_db(False), ai, _project())
    assert authz.can_read_project(_db(True), ai, _project())
    assert not authz.can_update_project(_db(True), ai, _project())
