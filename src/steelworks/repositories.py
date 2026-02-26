"""Repository layer for data access"""

from typing import Optional

from sqlalchemy.orm import Session

from steelworks.models import Lot, ProductionRecord


class LotRepository:
    """Repository for Lot operations"""

    def __init__(self, session: Session):
        self.session = session

    def create_lot(self, lot_code: str) -> Lot:
        """Create a new lot"""
        lot = Lot(lot_code=lot_code)
        self.session.add(lot)
        self.session.commit()
        return lot

    def get_lot_by_code(self, lot_code: str) -> Optional[Lot]:
        """Get a lot by its code"""
        return self.session.query(Lot).filter(Lot.lot_code == lot_code).first()

    def get_lot_by_id(self, lot_id: int) -> Optional[Lot]:
        """Get a lot by its ID"""
        return self.session.query(Lot).filter(Lot.id == lot_id).first()


class ProductionRecordRepository:
    """Repository for ProductionRecord operations"""

    def __init__(self, session: Session):
        self.session = session

    def get_records_by_lot_id(self, lot_id: int) -> list[ProductionRecord]:
        """Get all production records for a lot"""
        return (
            self.session.query(ProductionRecord)
            .filter(ProductionRecord.lot_id == lot_id)
            .all()
        )
