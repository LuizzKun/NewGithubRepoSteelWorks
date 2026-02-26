"""Unit tests for repository layer"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from steelworks.models import Base
from steelworks.repositories import LotRepository


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


class TestLotRepository:
    """Test Lot repository operations"""

    def test_create_lot(self, db_session):
        """Test creating a lot"""
        repo = LotRepository(db_session)
        lot = repo.create_lot("LOT-001")

        assert lot.id is not None
        assert lot.lot_code == "LOT-001"

    def test_get_lot_by_code(self, db_session):
        """Test retrieving a lot by code"""
        repo = LotRepository(db_session)
        repo.create_lot("LOT-002")

        lot = repo.get_lot_by_code("LOT-002")

        assert lot is not None
        assert lot.lot_code == "LOT-002"

    def test_get_lot_by_id(self, db_session):
        """Test retrieving a lot by ID"""
        repo = LotRepository(db_session)
        created_lot = repo.create_lot("LOT-003")

        lot = repo.get_lot_by_id(created_lot.id)

        assert lot is not None
        assert lot.lot_code == "LOT-003"
        assert lot.id == created_lot.id
