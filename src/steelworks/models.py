"""SQLAlchemy models for SteelWorks Operations"""

import os
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

Base = declarative_base()  # type: ignore[call-overload]


def get_database_url() -> str:
    """
    Get PostgreSQL database URL from environment variables.

    Returns:
        str: Database connection string

    Priority:
        1. DATABASE_URL environment variable
        2. Individual DB_* variables
        3. Default to localhost
    """
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL", "")

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "steelworks_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def create_session() -> Session:
    """
    Create and return a SQLAlchemy database session.

    Returns:
        Session: SQLAlchemy session connected to configured database

    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    engine = create_engine(get_database_url(), echo=False)
    session = Session(engine)
    return session


class Lot(Base):  # type: ignore[name-defined,valid-type,misc]
    """Represents a production lot"""

    __tablename__ = "lots"

    id = Column(Integer, primary_key=True)
    lot_code = Column(String(255), unique=True, nullable=False)

    production_records = relationship("ProductionRecord", back_populates="lot")
    inspection_records = relationship("InspectionRecord", back_populates="lot")
    shipment_records = relationship("ShipmentRecord", back_populates="lot")


class ProductionLine(Base):  # type: ignore[name-defined,valid-type,misc]
    """Represents a production line"""

    __tablename__ = "production_lines"

    id = Column(Integer, primary_key=True)
    line_code = Column(String(255), unique=True, nullable=False)

    production_records = relationship(
        "ProductionRecord", back_populates="production_line"
    )


class ProductionRecord(Base):  # type: ignore[name-defined,valid-type,misc]
    """Represents a production record for a lot on a line"""

    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    production_line_id = Column(
        Integer, ForeignKey("production_lines.id"), nullable=False
    )
    record_date = Column(Date, nullable=False)
    shift = Column(String(50), nullable=False)
    part_number = Column(String(255), nullable=False)
    units_planned = Column(Integer, nullable=False)
    units_actual = Column(Integer, nullable=False)
    downtime_minutes = Column(Integer, nullable=False)
    has_line_issue = Column(Boolean, nullable=False)
    primary_issue = Column(String(255))
    supervisor_notes = Column(String(255))

    lot = relationship("Lot", back_populates="production_records")
    production_line = relationship(
        "ProductionLine", back_populates="production_records"
    )


class InspectionRecord(Base):  # type: ignore[name-defined,valid-type,misc]
    """Represents an inspection/quality record for a production lot"""

    __tablename__ = "inspection_records"

    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    inspection_date = Column(Date, nullable=False)
    defect_type = Column(String(255), nullable=False)
    quantity_defective = Column(Integer, nullable=False)

    lot = relationship("Lot", back_populates="inspection_records")


class ShipmentRecord(Base):  # type: ignore[name-defined,valid-type,misc]
    """Represents a shipment record for a lot"""

    __tablename__ = "shipment_records"

    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    ship_status = Column(String(50), nullable=False)
    ship_date = Column(Date)
    qty_shipped = Column(Integer, nullable=False, default=0)
    sales_order_number = Column(String(255))
    customer = Column(String(255))
    destination_state = Column(String(50))
    carrier = Column(String(255))
    bol_number = Column(String(255))
    tracking_pro = Column(String(255))
    hold_reason = Column(String(255))
    shipping_notes = Column(String(255))

    lot = relationship("Lot", back_populates="shipment_records")
