"""SQLAlchemy models for SteelWorks Operations"""

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()  # type: ignore[call-overload]


class Lot(Base):  # type: ignore[name-defined,valid-type,misc]
    """Represents a production lot"""

    __tablename__ = "lots"

    id = Column(Integer, primary_key=True)
    lot_code = Column(String(255), unique=True, nullable=False)

    production_records = relationship("ProductionRecord", back_populates="lot")
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


class ShipmentRecord(Base):  # type: ignore[name-defined,valid-type,misc]
    """Represents a shipment record for a lot"""

    __tablename__ = "shipment_records"

    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    ship_date = Column(Date)
    ship_status = Column(String(50), nullable=False)
    qty_shipped = Column(Integer, nullable=False)
    sales_order_number = Column(String(255))
    customer = Column(String(255))
    destination_state = Column(String(50))
    carrier = Column(String(255))
    bol_number = Column(String(255))
    tracking_pro = Column(String(255))
    hold_reason = Column(String(255))
    shipping_notes = Column(String(255))

    lot = relationship("Lot", back_populates="shipment_records")
