"""GitHub READ integration (Phase 4).

Strictly read-only: this package fetches repository signals (last commit,
open PRs/issues, default branch) for display on project profiles. The app
never writes to any repository - there is no write client here and there
must never be one (see docs/PROJECT_SCOPE.md: no autonomous write actions
to external systems).
"""
