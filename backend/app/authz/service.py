"""Single authorization choke point.

EVERY permission decision in the app goes through this module - no inline
role checks in routers or services. The AI source-bundle builder (T9) must
also call these functions so AI never sees what the requesting user cannot.

Auth mode:
- dev  : login stub only - identity comes from the X-User-Email header,
         falling back to settings.dev_default_user_email. The permission
         model below is REAL and enforced.
- entra: Bearer-token validation against the CWS Entra tenant (see
         app.authz.entra). Mandatory the moment a second user exists.

Either way, identity resolution ends in the same place: an active Person
row, whose role drives every permission below.
"""

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.registry.models import Person, Project, ProjectMember
from app.vocab import Role

# Roles that may read any project-level data (portfolio-wide read).
_PORTFOLIO_READ_ROLES = {Role.ADMIN, Role.MANAGER, Role.AUDITOR}


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    x_user_email: str | None = Header(default=None),
) -> Person:
    if settings.auth_mode == "dev":
        email = (x_user_email or settings.dev_default_user_email).strip().lower()
    elif settings.auth_mode == "entra":
        from app.authz import entra

        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        email = entra.validate_token(token.strip())
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Unknown auth_mode '{settings.auth_mode}'; expected 'dev' or 'entra'.",
        )
    person = db.scalar(select(Person).where(Person.email == email, Person.active.is_(True)))
    if person is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown or inactive user.")
    return person


def is_admin(user: Person) -> bool:
    return user.role_type == Role.ADMIN


def _is_member(db: Session, user: Person, project: Project) -> bool:
    if project.owner_id == user.id:
        return True
    return (
        db.scalar(
            select(ProjectMember.id).where(
                ProjectMember.project_id == project.id, ProjectMember.person_id == user.id
            )
        )
        is not None
    )


def can_read_project(db: Session, user: Person, project: Project) -> bool:
    if user.role_type in _PORTFOLIO_READ_ROLES:
        return True
    if user.role_type in {Role.DEVELOPER_PROJECT_OWNER, Role.TRAINEE, Role.AI_SERVICE_ACCOUNT}:
        return _is_member(db, user, project)
    # end_user: approved end-user docs only (portal deferred) - no project reads in MVP.
    return False


def can_update_project(db: Session, user: Person, project: Project) -> bool:
    if is_admin(user):
        return True
    if user.role_type == Role.DEVELOPER_PROJECT_OWNER:
        return _is_member(db, user, project)
    return False


def can_create_project(user: Person) -> bool:
    return user.role_type in {Role.ADMIN, Role.DEVELOPER_PROJECT_OWNER}


def require_read(db: Session, user: Person, project: Project) -> None:
    if not can_read_project(db, user, project):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No read access to this project.")


def require_update(db: Session, user: Person, project: Project) -> None:
    if not can_update_project(db, user, project):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No update access to this project.")


def require_create(user: Person) -> None:
    if not can_create_project(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No project-creation access.")


# Portfolio-wide audit feed is oversight tooling: admin and auditor only.
# Project-scoped audit history reuses can_read_project (members see their
# own project's trail).
_AUDIT_PORTFOLIO_ROLES = {Role.ADMIN, Role.AUDITOR}


def can_read_audit_portfolio(user: Person) -> bool:
    return user.role_type in _AUDIT_PORTFOLIO_ROLES


def require_audit_portfolio_read(user: Person) -> None:
    if not can_read_audit_portfolio(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Portfolio-wide audit access requires admin or auditor role.",
        )
