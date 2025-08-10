from sqlmodel import Session, create_engine, SQLModel

from app.core.config import settings

# Ensure models are imported so SQLModel metadata is populated
try:
    # When running as a module: python -m app.core.db
    from app.schemas import models as inventory_models  # type: ignore
except Exception:  # Fallback when running the file directly
    from schemas import models as inventory_models  # type: ignore


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def create_tables() -> None:
    SQLModel.metadata.create_all(engine)


def init_db(session: Session) -> None:
    # Create tables then seed inventory dummy data (idempotent)
    create_tables()
    try:
        inventory_models.seed_inventory_data(session)
    except Exception:
        # Avoid failing init if seeding encounters an issue
        pass


if __name__ == "__main__":
    # Allow running this module directly to create tables and seed data
    with Session(engine) as _session:
        init_db(_session)
