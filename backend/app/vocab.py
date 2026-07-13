"""Controlled vocabularies - the ONLY source of enum values in this app.

Mirrors docs/DATA_MODEL.md and the vault note 'Controlled Vocabularies and
Required Documentation Profiles' (confirmed 2026-07-13). Changing a value
here requires an Alembic migration and a docs update. Never use inline
strings for these domains.
"""

from enum import StrEnum


class ProjectPhase(StrEnum):
    """Consolidated per Gregory 2026-07-14: exactly these five phases.
    (Old values discovery->concept, build->ongoing-development,
    pilot->pilot-test, retired->handover; migration a1c4f9d2b7e0.)"""

    CONCEPT = "concept"
    ONGOING_DEVELOPMENT = "ongoing-development"
    PILOT_TEST = "pilot-test"
    LIVE = "live"
    HANDOVER = "handover"


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    PAUSED = "paused"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


class Priority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProjectType(StrEnum):
    INTERNAL_WEB_APP = "internal-web-app"
    OPERATIONAL_TOOL = "operational-tool"
    PROTOTYPE = "prototype"


class Classification(StrEnum):
    ONE_OFF = "one-off"
    REUSABLE = "reusable"
    PLATFORM = "platform"


class ArtifactType(StrEnum):
    USER_GUIDE = "user_guide"
    ADMIN_GUIDE = "admin_guide"
    DEVELOPER_GUIDE = "developer_guide"
    AGENT_GUIDE = "agent_guide"
    SUPPORT_RUNBOOK = "support_runbook"
    DEPLOYMENT_GUIDE = "deployment_guide"
    VERIFICATION_MATRIX = "verification_matrix"
    EXIT_MD = "exit_md"


class ArtifactStatus(StrEnum):
    MISSING = "missing"
    DRAFT = "draft"
    CURRENT = "current"
    STALE = "stale"
    APPROVED = "approved"
    RETIRED = "retired"


class Role(StrEnum):
    ADMIN = "admin"
    DEVELOPER_PROJECT_OWNER = "developer_project_owner"
    TRAINEE = "trainee"  # view deferred; enum exists from day one
    MANAGER = "manager"
    END_USER = "end_user"  # view deferred; enum exists from day one
    AUDITOR = "auditor"
    AI_SERVICE_ACCOUNT = "ai_service_account"


class AITaskType(StrEnum):
    PROJECT_SUMMARY = "project_summary"
    STARTER_PACK_TAILORING = "starter_pack_tailoring"


class AIAudience(StrEnum):
    DEVELOPER = "developer"
    MANAGER = "manager"


class ValidationStatus(StrEnum):
    PASSED = "passed"
    FAILED_SCHEMA = "failed_schema"
    FAILED_MISSING_SOURCES = "failed_missing_sources"
    FAILED_FORBIDDEN_DATA = "failed_forbidden_data"


class HumanReviewStatus(StrEnum):
    GENERATED = "generated"
    REVIEWED = "reviewed"
    EXPORTED = "exported"
    REJECTED = "rejected"


class JobType(StrEnum):
    AI_RUN = "ai_run"
    SEED_IMPORT = "seed_import"
    STARTER_PACK_GENERATION = "starter_pack_generation"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ErrorCategory(StrEnum):
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    CONTEXT_TOO_LARGE = "context_too_large"
    MALFORMED_OUTPUT = "malformed_output"
    VALIDATION_FAILED = "validation_failed"
    FORBIDDEN_DATA_DETECTED = "forbidden_data_detected"
    ACCESS_DENIED = "access_denied"
    BUDGET_EXCEEDED = "budget_exceeded"
    INTERNAL_ERROR = "internal_error"


class AuditActionType(StrEnum):
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    STATUS_EVENT_CREATED = "status_event_created"
    DOC_ARTIFACT_CREATED = "doc_artifact_created"
    DOC_ARTIFACT_UPDATED = "doc_artifact_updated"
    STARTER_PACK_GENERATED = "starter_pack_generated"
    STARTER_PACK_REVIEWED = "starter_pack_reviewed"
    STARTER_PACK_EXPORTED = "starter_pack_exported"
    AI_RUN_CREATED = "ai_run_created"
    AI_OUTPUT_REVIEWED = "ai_output_reviewed"
    SEED_IMPORT_RUN = "seed_import_run"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"


class AuditObjectType(StrEnum):
    PROJECT = "project"
    STATUS_EVENT = "status_event"
    DOCUMENTATION_ARTIFACT = "documentation_artifact"
    STARTER_PACK = "starter_pack"
    AI_INTERACTION = "ai_interaction"
    PROJECT_MEMBER = "project_member"
    JOB = "job"


# Required documentation profiles: project_type -> set of required artifact types.
REQUIRED_DOC_PROFILES: dict[ProjectType, frozenset[ArtifactType]] = {
    ProjectType.INTERNAL_WEB_APP: frozenset(ArtifactType),
    ProjectType.OPERATIONAL_TOOL: frozenset(
        {
            ArtifactType.DEVELOPER_GUIDE,
            ArtifactType.AGENT_GUIDE,
            ArtifactType.SUPPORT_RUNBOOK,
            ArtifactType.DEPLOYMENT_GUIDE,
            ArtifactType.VERIFICATION_MATRIX,
            ArtifactType.EXIT_MD,
        }
    ),
    ProjectType.PROTOTYPE: frozenset({ArtifactType.AGENT_GUIDE, ArtifactType.EXIT_MD}),
}
