"""
Integration Tests for SteelWorks Operations Reporting.

These tests verify the entire workflow from database operations through
the service layer using a test database instance.

Requirements:
    - Test database must be set up (see .env.test)
    - Run: pytest tests/test_integration.py -v
"""

import pytest
import os
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from src.steelworks.models import (
    Base,
    Lot,
    ProductionLine,
    ProductionRecord,
    InspectionRecord,
    ShipmentRecord,
    get_database_url,
)
from src.steelworks.service import OperationsReportingService

# Load test environment variables
test_env_path = Path(__file__).parent.parent / ".env.test"
load_dotenv(dotenv_path=test_env_path, override=True)


@pytest.fixture(scope="module")
def test_engine():
    """Create test database engine."""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    
    # Create all tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a new database session for each test with transaction isolation."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def sample_data(test_session):
    """Create sample data for testing."""
    # Create production lines
    line_a = ProductionLine(line_code="LINE-A")
    line_b = ProductionLine(line_code="LINE-B")
    test_session.add_all([line_a, line_b])
    test_session.flush()
    
    # Create lots
    lot1 = Lot(lot_code="LOT-2024-001")
    lot2 = Lot(lot_code="LOT-2024-002")
    lot3 = Lot(lot_code="LOT-2024-003")
    test_session.add_all([lot1, lot2, lot3])
    test_session.flush()
    
    # Create production records
    today = date.today()
    prod1 = ProductionRecord(
        lot_id=lot1.id,
        production_line_id=line_a.id,
        record_date=today - timedelta(days=5),
        shift="Day",
        part_number="PART-001",
        units_planned=100,
        units_actual=95,
        downtime_minutes=30,
        has_line_issue=True,
        primary_issue="Tooling wear",
    )
    prod2 = ProductionRecord(
        lot_id=lot2.id,
        production_line_id=line_b.id,
        record_date=today - timedelta(days=3),
        shift="Night",
        part_number="PART-002",
        units_planned=200,
        units_actual=200,
        downtime_minutes=0,
        has_line_issue=False,
    )
    prod3 = ProductionRecord(
        lot_id=lot3.id,
        production_line_id=line_a.id,
        record_date=today - timedelta(days=1),
        shift="Day",
        part_number="PART-003",
        units_planned=150,
        units_actual=145,
        downtime_minutes=15,
        has_line_issue=True,
        primary_issue="Material delay",
    )
    test_session.add_all([prod1, prod2, prod3])
    test_session.flush()
    
    # Create inspection records (defects)
    insp1 = InspectionRecord(
        lot_id=lot1.id,
        inspection_date=today - timedelta(days=4),
        defect_type="Scratch",
        quantity_defective=5,
    )
    insp2 = InspectionRecord(
        lot_id=lot1.id,
        inspection_date=today - timedelta(days=4),
        defect_type="Dent",
        quantity_defective=3,
    )
    insp3 = InspectionRecord(
        lot_id=lot3.id,
        inspection_date=today,
        defect_type="Scratch",
        quantity_defective=8,
    )
    test_session.add_all([insp1, insp2, insp3])
    test_session.flush()
    
    # Create shipment records
    ship1 = ShipmentRecord(
        lot_id=lot1.id,
        ship_status="Shipped",
        ship_date=today - timedelta(days=2),
        qty_shipped=95,
        customer="Customer A",
    )
    ship2 = ShipmentRecord(
        lot_id=lot2.id,
        ship_status="On Hold",
        ship_date=None,
        qty_shipped=0,
        hold_reason="Quality hold",
    )
    ship3 = ShipmentRecord(
        lot_id=lot3.id,
        ship_status="Partial",
        ship_date=None,
        qty_shipped=0,
    )
    test_session.add_all([ship1, ship2, ship3])
    test_session.commit()
    
    return {
        "lines": [line_a, line_b],
        "lots": [lot1, lot2, lot3],
        "productions": [prod1, prod2, prod3],
        "inspections": [insp1, insp2, insp3],
        "shipments": [ship1, ship2, ship3],
    }


class TestOperationsReportingServiceIntegration:
    """Integration tests for OperationsReportingService."""
    
    def test_get_lines_with_most_defects(self, test_session, sample_data):
        """Test AC 1: Identify production lines with most defects."""
        service = OperationsReportingService(test_session)
        today = date.today()
        start_date = today - timedelta(days=10)
        end_date = today
        
        result = service.get_lines_with_most_defects(start_date, end_date)
        
        assert len(result) > 0
        # LINE-A should have more defects (lot1 + lot3)
        assert result[0][0] == "LINE-A"
        assert result[0][1] >= 3  # At least 3 defect records
    
    def test_get_defect_trend_over_time(self, test_session, sample_data):
        """Test AC 2: Identify defect trends over time."""
        service = OperationsReportingService(test_session)
        today = date.today()
        start_date = today - timedelta(days=10)
        end_date = today
        
        result = service.get_defect_trend_over_time(start_date, end_date)
        
        assert len(result) > 0
        assert all("date" in item for item in result)
        assert all("total_defects" in item for item in result)
        assert all("trend_indicator" in item for item in result)
    
    def test_get_defects_by_type(self, test_session, sample_data):
        """Test AC 3: Aggregate defects by type."""
        service = OperationsReportingService(test_session)
        today = date.today()
        start_date = today - timedelta(days=10)
        end_date = today
        
        result = service.get_defects_by_type(start_date, end_date)
        
        assert len(result) > 0
        # Should have "Scratch" and "Dent" types
        defect_types = [item["defect_code"] for item in result]
        assert "Scratch" in defect_types
        assert "Dent" in defect_types
        
        # Check percentages sum to 100
        total_percentage = sum(item["percentage"] for item in result)
        assert 99.0 <= total_percentage <= 100.0
    
    def test_get_shipped_lots_summary(self, test_session, sample_data):
        """Test AC 4: Determine shipped lots."""
        service = OperationsReportingService(test_session)
        
        result = service.get_shipped_lots_summary()
        
        assert len(result) == 3  # 3 lots total
        shipped = [item for item in result if item["ship_status"] == "Shipped"]
        pending = [item for item in result if item["ship_status"] != "Shipped"]
        
        assert len(shipped) == 1  # LOT-2024-001
        assert len(pending) == 2  # LOT-2024-002, LOT-2024-003
    
    def test_get_lot_report(self, test_session, sample_data):
        """Test AC 5: Lot drill-down with cross-functional data."""
        service = OperationsReportingService(test_session)
        
        result = service.get_lot_report("LOT-2024-001")
        
        assert result is not None
        assert result["lot_code"] == "LOT-2024-001"
        
        # Check production info
        assert len(result["production_info"]) > 0
        assert result["production_info"][0]["line"] == "LINE-A"
        
        # Check quality info
        assert result["quality_info"]["total_defects"] == 8  # 5 + 3
        assert len(result["quality_info"]["defects"]) == 2
        
        # Check shipment info
        assert result["shipment_info"]["ship_status"] == "Shipped"
        assert result["shipment_info"]["ship_date"] is not None
    
    def test_get_production_summary(self, test_session, sample_data):
        """Test AC 6: Production aggregation by date and line."""
        service = OperationsReportingService(test_session)
        today = date.today()
        start_date = today - timedelta(days=10)
        end_date = today
        
        result = service.get_production_summary(start_date, end_date)
        
        assert len(result) == 3  # 3 production records
        assert all("date" in item for item in result)
        assert all("line_code" in item for item in result)
        assert all("lot_code" in item for item in result)
    
    def test_get_pending_shipments(self, test_session, sample_data):
        """Test utility method: get pending shipments."""
        service = OperationsReportingService(test_session)
        
        result = service.get_pending_shipments()
        
        assert len(result) == 2
        assert "LOT-2024-002" in result
        assert "LOT-2024-003" in result
    
    def test_get_shipped_lots(self, test_session, sample_data):
        """Test utility method: get shipped lots."""
        service = OperationsReportingService(test_session)
        
        result = service.get_shipped_lots()
        
        assert len(result) == 1
        assert result[0][0] == "LOT-2024-001"
        assert result[0][1] is not None  # Ship date exists


class TestDatabaseConsistency:
    """Test database schema and data consistency."""
    
    def test_lot_unique_constraint(self, test_session):
        """Verify lot_code uniqueness is enforced."""
        lot1 = Lot(lot_code="UNIQUE-LOT")
        test_session.add(lot1)
        test_session.commit()
        
        lot2 = Lot(lot_code="UNIQUE-LOT")
        test_session.add(lot2)
        
        with pytest.raises(Exception):  # IntegrityError
            test_session.commit()
    
    def test_foreign_key_constraints(self, test_session):
        """Verify foreign key relationships work correctly."""
        line = ProductionLine(line_code="FK-TEST-LINE")
        lot = Lot(lot_code="FK-TEST-LOT")
        test_session.add_all([line, lot])
        test_session.flush()
        
        prod = ProductionRecord(
            lot_id=lot.id,
            production_line_id=line.id,
            record_date=date.today(),
            shift="Day",
            part_number="TEST-PART",
            units_planned=100,
            units_actual=100,
            downtime_minutes=0,
            has_line_issue=False,
        )
        test_session.add(prod)
        test_session.commit()
        
        # Verify relationship navigation
        assert prod.lot.lot_code == "FK-TEST-LOT"
        assert prod.production_line.line_code == "FK-TEST-LINE"
