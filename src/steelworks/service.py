"""
Service Layer (Business Logic) for SteelWorks Operations Reporting.

This module provides high-level reporting functions that answer
operations questions:
- Production line quality analysis
- Defect trend identification
- Shipment tracking
- Lot-level drill-down

The service layer abstracts repository queries and implements business rules
to support the operations user story.

Time Complexity Notes:
    - Most aggregation queries: O(n) where n = total records in date range
    - With proper indexes: Effective O(log n) index lookup + O(m) result scan

Space Complexity: O(m) where m = result rows

Author: SteelWorks Operations Team
Date: 2024-02-16
"""

from typing import List, Dict, Tuple, Optional, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from src.steelworks.models import (
    Lot,
    ProductionRecord,
    InspectionRecord,
    ShipmentRecord,
    ProductionLine,
)

logger = logging.getLogger(__name__)


class OperationsReportingService:
    """
    Main service class for operations reporting.

    Implements the operations user story:
    "As an operations team member, I want to review and summarize production,
    quality, and shipment information by lot ID and date, so that I can answer
    report questions about line issues, defect trends, and shipped batches
    without manually combining spreadsheets."

    Time Complexity: See individual methods
    Space Complexity: O(m) where m = result rows
    """

    def __init__(self, session: Session):
        """
        Initialize the reporting service with database session.

        Args:
            session (Session): SQLAlchemy database session

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.session = session
        logger.info("OperationsReportingService initialized")

    # ===== AC 1: Identify which production lines had the most defects =====

    def get_lines_with_most_defects(
        self, start_date: date, end_date: date
    ) -> List[Tuple[str, int]]:
        """
        AC 1: Identify which production lines had the most defects within a date period.

        User Story: Operations team wants to know problem areas by production line.

        Args:
            start_date (date): Start of reporting period
            end_date (date): End of reporting period

        Returns:
            List[Tuple[str, int]]: [(line_code, total_defects), ...]
                                   sorted by defects descending

        Time Complexity: O(n) where n = inspection records in date range
        Space Complexity: O(p) where p = number of production lines

        Coverage: AC 1
        """
        logger.info(f"Querying production lines with most defects: {start_date} to {end_date}")
        try:
            result = (
                self.session.query(
                    ProductionLine.line_code,
                    func.count(InspectionRecord.id).label("defect_count"),
                )
                .join(
                    ProductionRecord,
                    ProductionLine.id == ProductionRecord.production_line_id,
                )
                .join(InspectionRecord, ProductionRecord.lot_id == InspectionRecord.lot_id)
                .filter(InspectionRecord.inspection_date.between(start_date, end_date))
                .group_by(ProductionLine.line_code)
                .order_by(func.count(InspectionRecord.id).desc())
                .all()
            )
            logger.info(f"Found {len(result)} production lines with defects")
            return [(line_code, int(count)) for line_code, count in result]
        except Exception as e:
            logger.error(f"Error querying production lines with defects: {str(e)}")
            raise

    # ===== AC 2: Defect trends over time =====

    def get_defect_trend_over_time(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """
        AC 2: Identify defect trends over time.

        Returns daily aggregation of defects to show trends/spikes.

        Args:
            start_date (date): Trend period start
            end_date (date): Trend period end

        Returns:
            List[Dict]: [{
                'date': date,
                'total_defects': int,
                'trend_indicator': str ('increasing', 'stable', 'decreasing')
            }, ...]

        Time Complexity: O(d) where d = days in date range
        Space Complexity: O(d)

        Coverage: AC 2
        """
        logger.info(f"Querying defect trend over time: {start_date} to {end_date}")
        try:
            trend_data = (
                self.session.query(
                    InspectionRecord.inspection_date,
                    func.count(InspectionRecord.id).label("defect_count"),
                )
                .filter(InspectionRecord.inspection_date.between(start_date, end_date))
                .group_by(InspectionRecord.inspection_date)
                .order_by(InspectionRecord.inspection_date)
                .all()
            )

            result = []
            prev_count = None

            for inspection_date, defect_count in trend_data:
                defect_count = defect_count or 0

                # Determine trend: up/down/stable vs previous day
                if prev_count is None:
                    trend = "baseline"
                elif defect_count > prev_count:
                    trend = "increasing"
                elif defect_count < prev_count:
                    trend = "decreasing"
                else:
                    trend = "stable"

                result.append(
                    {
                        "date": inspection_date,
                        "total_defects": int(defect_count),
                        "trend_indicator": trend,
                    }
                )

                prev_count = defect_count

            logger.info(f"Processed {len(result)} days of defect trend data")
            return result
        except Exception as e:
            logger.error(f"Error querying defect trend: {str(e)}")
            raise

    # ===== AC 3: Defect aggregation by defect type =====

    def get_defects_by_type(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """
        AC 3: Aggregate defect counts by type in a date period.

        Supports: "Which defect types appear most frequently?"

        Args:
            start_date (date): Period start
            end_date (date): Period end

        Returns:
            List[Dict]: [{
                'defect_code': str,
                'total_qty': int,
                'percentage': float (of total defects)
            }, ...] sorted by quantity descending

        Time Complexity: O(n) table scan + O(m log m) sorting
        Space Complexity: O(m) where m = distinct defect types

        Coverage: AC 3
        """
        logger.info(f"Querying defects by type: {start_date} to {end_date}")
        try:
            defect_data = (
                self.session.query(
                    InspectionRecord.defect_type,
                    func.sum(InspectionRecord.quantity_defective).label("total_qty"),
                )
                .filter(InspectionRecord.inspection_date.between(start_date, end_date))
                .group_by(InspectionRecord.defect_type)
                .order_by(func.sum(InspectionRecord.quantity_defective).desc())
                .all()
            )

            total = sum(qty or 0 for _, qty in defect_data)

            if total == 0:
                logger.info("No defects found in specified date range")
                return []

            result = []
            for defect_code, qty in defect_data:
                qty = qty or 0
                result.append(
                    {
                        "defect_code": defect_code,
                        "total_qty": int(qty),
                        "percentage": round((qty / total) * 100, 2),
                    }
                )

            logger.info(f"Found {len(result)} defect types totaling {total} defects")
            return result
        except Exception as e:
            logger.error(f"Error querying defects by type: {str(e)}")
            raise
    # ===== AC 4: Lot shipment status and data comparison =====

    def get_shipped_lots_summary(self) -> List[Dict[str, Any]]:
        """
        AC 4: Determine which lots have been shipped with summary data.

        Returns shipment status for all lots with defect counts.

        Returns:
            List[Dict]: [{
                'lot_code': str,
                'ship_status': str,
                'ship_date': Optional[date],
                'total_defects': int
            }, ...] sorted by lot_code

        Time Complexity: O(n) + O(m) where n = lots, m = inspections
        Space Complexity: O(n)

        Coverage: AC 4
        """
        logger.info("Querying shipped lots summary")
        try:
            lots = self.session.query(Lot).all()
            result = []

            for lot in lots:
                # Count defects for this lot
                defect_count = (
                    self.session.query(func.count(InspectionRecord.id))
                    .filter(InspectionRecord.lot_id == lot.id)
                    .scalar()
                    or 0
                )

                # Get shipment status
                shipment = (
                    self.session.query(ShipmentRecord)
                    .filter(ShipmentRecord.lot_id == lot.id)
                    .first()
                )

                result.append(
                    {
                        "lot_code": lot.lot_code,
                        "ship_status": shipment.ship_status if shipment else "Pending",
                        "ship_date": shipment.ship_date if shipment else None,
                        "total_defects": int(defect_count),
                    }
                )

            logger.info(f"Processed shipment summary for {len(result)} lots")
            return sorted(result, key=lambda x: x["lot_code"])
        except Exception as e:
            logger.error(f"Error querying shipped lots summary: {str(e)}")
            raise

    # ===== AC 5: Lot drill-down comparison across departments =====

    def get_lot_report(self, lot_code: str) -> Optional[Dict[str, Any]]:
        """
        AC 5: Cross-departmental lot data comparison.

        Pulls production, inspection, and shipment data for a single lot.
        Enables operations team to answer: "What's the full history of lot X?"

        Args:
            lot_code (str): Lot identifier (e.g., 'LOT-2024-01-001')

        Returns:
            Dict: {
                'lot_code': str,
                'production_info': [
                    {'line': str, 'date': date}, ...
                ],
                'quality_info': {
                    'total_defects': int,
                    'defects': [
                        {'defect_code': str, 'qty': int, 'date': date}, ...
                    ]
                },
                'shipment_info': {
                    'ship_status': str,
                    'ship_date': Optional[date],
                    'days_to_ship': Optional[int]
                }
            }
            or None if lot not found

        Time Complexity: O(log n) lookup + O(m) join operations
        Space Complexity: O(m)

        Coverage: AC 5
        """
        logger.info(f"Querying lot report for: {lot_code}")
        try:
            lot = self.session.query(Lot).filter(Lot.lot_code == lot_code).first()

            if not lot:
                logger.warning(f"Lot not found: {lot_code}")
                return None

            # Get production records for this lot
            production_records = (
                self.session.query(
                    ProductionLine.line_code, ProductionRecord.record_date
                )
                .join(
                    ProductionRecord,
                    ProductionLine.id == ProductionRecord.production_line_id,
                )
                .filter(ProductionRecord.lot_id == lot.id)
                .all()
            )

            # Get inspection/defect records for this lot
            inspection_records = (
                self.session.query(
                    InspectionRecord.defect_type,
                    InspectionRecord.quantity_defective,
                    InspectionRecord.inspection_date,
                )
                .filter(InspectionRecord.lot_id == lot.id)
                .all()
            )

            total_defects = sum(qty or 0 for _, qty, _ in inspection_records)

            # Get shipment status
            shipment = (
                self.session.query(ShipmentRecord)
                .filter(ShipmentRecord.lot_id == lot.id)
                .first()
            )

            # Calculate days to ship if applicable
            days_to_ship = None
            if shipment and shipment.ship_status == 'Shipped' and production_records:
                first_prod_date = min(date for _, date in production_records)
                days_to_ship = (shipment.ship_date - first_prod_date).days

            logger.info(f"Lot report generated for {lot_code}: {len(production_records)} production records, {total_defects} defects")
            return {
                "lot_code": lot.lot_code,
                "production_info": [
                    {"line": line, "date": dt} for line, dt in production_records
                ],
                "quality_info": {
                    "total_defects": int(total_defects),
                    "defects": [
                        {
                            "defect_code": defect_code,
                            "qty": int(qty or 0),
                            "date": insp_date,
                        }
                        for defect_code, qty, insp_date in inspection_records
                    ],
                },
                "shipment_info": {
                    "ship_status": shipment.ship_status if shipment else "Pending",
                    "ship_date": shipment.ship_date if shipment else None,
                    "days_to_ship": days_to_ship,
                },
            }
        except Exception as e:
            logger.error(f"Error generating lot report for {lot_code}: {str(e)}")
            raise

    # ===== AC 6: Production aggregation by date =====

    def get_production_summary(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """
        AC 6: Aggregate production records by date and line.

        Shows production volume and line utilization over time.

        Args:
            start_date (date): Period start
            end_date (date): Period end

        Returns:
            List[Dict]: [{
                'date': date,
                'line_code': str,
                'lot_code': str
            }, ...] sorted by date, then line

        Time Complexity: O(p) where p = production records in range
        Space Complexity: O(p)

        Coverage: AC 6
        """
        records = (
            self.session.query(
                Lot.lot_code, ProductionLine.line_code, ProductionRecord.record_date
            )
            .join(ProductionRecord, Lot.id == ProductionRecord.lot_id)
            .join(
                ProductionLine, ProductionLine.id == ProductionRecord.production_line_id
            )
            .filter(ProductionRecord.record_date.between(start_date, end_date))
            .all()
        )

        result = []
        for lot_code, line_code, record_date in records:
            result.append(
                {"date": record_date, "line_code": line_code, "lot_code": lot_code}
            )

        return sorted(result, key=lambda x: (x["date"], x["line_code"]))

    # ===== Utility methods =====

    def get_pending_shipments(self) -> List[str]:
        """
        Get list of lots waiting to ship (not yet shipped).

        Returns:
            List[str]: Lot codes of lots with ship_status not 'Shipped'

        Time Complexity: O(log n) index + O(m)
        Space Complexity: O(m)
        """
        results = (
            self.session.query(Lot.lot_code)
            .join(ShipmentRecord, Lot.id == ShipmentRecord.lot_id)
            .filter(ShipmentRecord.ship_status.in_(['On Hold', 'Backordered', 'Partial']))
            .all()
        )
        return [lot_code for (lot_code,) in results]

    def get_shipped_lots(self) -> List[Tuple[str, date]]:
        """
        Get all shipped lots with ship dates.

        Returns:
            List[Tuple]: [(lot_code, ship_date), ...] most recent first

        Time Complexity: O(log n) + O(m)
        Space Complexity: O(m)
        """
        results = (
            self.session.query(Lot.lot_code, ShipmentRecord.ship_date)
            .join(ShipmentRecord, Lot.id == ShipmentRecord.lot_id)
            .filter(ShipmentRecord.ship_status == 'Shipped')
            .order_by(ShipmentRecord.ship_date.desc())
            .all()
        )
        return results

    def close(self) -> None:
        """
        Close database session (cleanup).

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if self.session:
            self.session.close()

    def __enter__(self) -> "OperationsReportingService":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit (cleanup)."""
        self.close()
