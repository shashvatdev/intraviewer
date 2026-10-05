from sqlalchemy import create_engine, text

from app.core.config import settings


engine = create_engine(settings.DATABASE_URL)


def test_db_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()