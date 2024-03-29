import warnings
import os
import sys

import pytest
from asgi_lifespan import LifespanManager

from fastapi import FastAPI
from httpx import AsyncClient
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import Session, sessionmaker
from utils.functions import refresh_materialized_view_query

from db.connection import Base, get_session, get_db_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


# Apply migrations at beginning and end of testing session
@pytest.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")
    command.upgrade(config, "head")


# Create a new application for testing
@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    from core.config import app

    engine = create_engine(get_db_url())
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_db
    return app


# Grab a reference to our database when needed
@pytest.fixture
def session() -> Session:
    engine = create_engine(get_db_url())
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    return TestingSessionLocal()


# Make requests in our tests
@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app, base_url="http://testserver"
        ) as client:
            yield client


# refresh materialized view on test
def test_refresh_materialized_data():
    engine = create_engine(get_db_url())
    Base.metadata.create_all(bind=engine)
    try:
        query = refresh_materialized_view_query()
        engine.execute(query)
    except exc.SQLAlchemyError:
        print("Error refresh materialzed view")
        pass
