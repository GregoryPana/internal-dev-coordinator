"""Imports every model module so Base.metadata (and Alembic autogenerate)
sees the full schema. Import new model modules here as tasks land."""

import app.ai.models  # noqa: F401
import app.audit.models  # noqa: F401
import app.docs_matrix.models  # noqa: F401
import app.registry.models  # noqa: F401
import app.starterpack.models  # noqa: F401
import app.status.models  # noqa: F401
