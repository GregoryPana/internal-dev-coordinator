"""Shared test fixtures: real Postgres (docker compose db), one transaction
per test rolled back afterwards so tests never leak data into each other."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.main import app
from app.registry.models import Person
from app.vocab import Role


@pytest.fixture()
def db() -> Session:
    """Real Postgres, one outer transaction per test, rolled back after.

    Endpoints under test call session.commit(); a plain outer transaction
    would end on the first commit, so mutations run inside a SAVEPOINT that
    is restarted after every commit (standard SQLAlchemy test recipe).
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, autoflush=False, expire_on_commit=False)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    def _override_get_db():
        yield session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield session
    finally:
        event.remove(session, "after_transaction_end", _restart_savepoint)
        session.close()
        transaction.rollback()
        connection.close()
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def client(db: Session) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def make_person(db: Session):
    counter = {"n": 0}

    def _make(role: Role, email: str | None = None) -> Person:
        counter["n"] += 1
        person = Person(
            name=f"Test Person {counter['n']}",
            email=email or f"test-user-{counter['n']}@cws.sc",
            role_type=role,
            active=True,
        )
        db.add(person)
        db.flush()
        return person

    return _make
