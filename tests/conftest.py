"""Shared fixtures."""

import os

import pytest
import transaction
import webtest

from datetime import datetime, timedelta
import random

from paste.deploy.loadwsgi import appconfig

from pyramid_app_caseinterview import main
from pyramid_app_caseinterview.models import Base, get_tm_session
from pyramid_app_caseinterview.models.timeseries import Timeseries

from .helpers import sign_in, user_remove

INI_FILE = os.path.join(os.path.dirname(__file__), "testing.ini")
SETTINGS = appconfig("config:" + INI_FILE)


@pytest.fixture(scope="module")
def app():
    app = main({}, **SETTINGS)
    print("SETUP app")
    from pyramid_app_caseinterview.scripts import initializedb

    initializedb.main([str(INI_FILE), "--drop-all"])
    yield app
    print("TEARDOWN app")
    Base.metadata.drop_all(app.registry["session_factory"].kw["bind"])
    print("TEARDOWN app complete")


@pytest.fixture(scope="module")
def engine(app):
    yield app.registry["session_factory"].kw["bind"]


@pytest.fixture(scope="module")
def testapp(app):
    testapp = webtest.TestApp(app)
    yield testapp
    del testapp


@pytest.fixture(scope="module")
def session(app):
    # session without transaction manager
    session_factory = app.registry["session_factory"]
    session = session_factory()
    yield session
    session.close()


@pytest.fixture(scope="function")
def session_tm(app):
    """Transaction managed session with rolback."""
    session_factory = app.registry["session_factory"]
    session = get_tm_session(session_factory, transaction.manager)
    yield session
    session.close()


@pytest.fixture(scope="module")
def session_tm_module_scope(app):
    """Transaction managed session in module scope with rolback."""
    session_factory = app.registry["session_factory"]
    session = get_tm_session(session_factory, transaction.manager)
    yield session
    session.close()


@pytest.fixture()
def as_admin(testapp):
    yield sign_in(testapp, "admin", "admin")
    testapp.get("/sign_out")


@pytest.fixture(scope="module")
def admin_user(session):
    yield session.query(User).filter(User.name == "admin").one()


@pytest.fixture()
def authenticated_user(testapp, session_tm):
    with transaction.manager:
        user = User(name="user", email="user@example.com")
        user.password = "user"
        session_tm.add(user)
        session_tm.flush()
        user_id = user.id
    yield session_tm.query(User).filter(User.name == "user").one()
    user_remove(testapp, user_id)

@pytest.fixture(scope="function")
def populate_timeseries_data(session_tm):
    """Fixture to populate dummy data into the 'timeseries' table."""
    print("Populating dummy data into 'timeseries' table...")

    # Generate 100 dummy rows
    dummy_data = []
    for i in range(100):
        random_datetime = datetime(
            year=random.randint(2020, 2023),
            month=random.randint(1, 12),
            day=random.randint(1, 28),
        )
        dummy_entry = Timeseries(
            datetime=random_datetime,
            value=round(random.uniform(10.0, 100.0), 2)  # Random value between 10 and 100
        )
        dummy_data.append(dummy_entry)

    # Add the data to the session and commit within the transaction manager scope
    session_tm.add_all(dummy_data)
    session_tm.flush()  # Flush changes to ensure they are saved to the DB
    transaction.manager.commit()  # Commit the transaction
    
    yield
    pass