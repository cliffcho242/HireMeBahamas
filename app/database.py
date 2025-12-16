import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = None

def init_db():
    global engine

    if not DATABASE_URL:
        logging.warning("DATABASE_URL is not set")
        return None

    try:
        url = make_url(DATABASE_URL)

        if not url.username or not url.password or not url.host:
            raise ValueError("DATABASE_URL missing credentials or host")

        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"sslmode": "require"},
        )

        logging.info("Database engine initialized successfully")
        return engine

    except Exception as e:
        logging.warning(f"Invalid DATABASE_URL: {e}")
        return None
