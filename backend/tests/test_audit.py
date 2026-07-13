"""Audit layer: append-only contract at the app layer."""

import inspect

import app.audit.service as audit_service


def test_audit_service_exposes_only_record() -> None:
    public = [
        name
        for name, obj in inspect.getmembers(audit_service, inspect.isfunction)
        if not name.startswith("_") and obj.__module__ == audit_service.__name__
    ]
    assert public == ["record"], "audit service must expose record() only - append-only contract"


def test_no_update_or_delete_in_audit_service_source() -> None:
    src = inspect.getsource(audit_service)
    for forbidden in ("db.delete", ".update(", "synchronize_session"):
        assert forbidden not in src
