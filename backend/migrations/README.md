# Alembic Baseline

The first inspection against a legacy database must be read-only. Use `konwhub.infrastructure.persistence.database.inspect_tables` to capture current names before authoring a migration. Do not run `upgrade` against the existing database until a reviewed baseline and backup are available.

Local service connection settings belong in `backend/.env`. Start commands can be run from the repository root or `backend/`; the settings path is resolved relative to this package, not the current directory. Copy `.env.example` to `.env` and replace the sample values. The real `.env` is ignored by Git.
