from sqlmodel import Session, create_engine, SQLModel

from app.core.config import settings

# Ensure models are imported so SQLModel metadata is populated
# When running as a module: python -m app.core.db
from app.schemas.models import DisciplineData

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def create_tables() -> None:
    SQLModel.metadata.create_all(engine)


def init_db(session: Session) -> None:
    # Create tables then seed discipline dummy data (idempotent)
    create_tables()
    try:
        from app.schemas.models import seed_inventory_data
        seed_inventory_data(session)
    except Exception as e:
        # Avoid failing init if seeding encounters an issue
        print(f"Warning: Seeding failed: {e}")
        pass


if __name__ == "__main__":
    # Allow running this module directly to create tables and seed data
    with Session(engine) as _session:
        init_db(_session)
