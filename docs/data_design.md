# Data Design — Operations User Story (SteelWorks)

---

## Source: Operations User Story

As an operations team member,  
I want to review and summarize production, quality, and shipment information by lot ID and date,  
So that I can answer report questions about line issues, defect trends, and shipped batches without manually combining spreadsheets.

---

## ProductionRecords
- record_date
- lot_id
- production_line

## InspectionRecords
- inspection_date
- qty_defects
- lot_id
- defect_code

## ShipmentRecords
- ship_date
- is_shipped
- lot_id

## Lot
- lot_id

## ProductionLine
- production_line

## Defect
- defect_code

---

## Relationships

- One lot can have many production records  
- One production line can have many production records  
- One lot can have many inspection records  
- One defect can appear in many inspection records  
- One lot can have zero or one shipment record  

---

## ERD

```mermaid
erDiagram
    LOT ||--o{ PRODUCTION_RECORD : has
    PRODUCTION_LINE ||--o{ PRODUCTION_RECORD : runs_on
    LOT ||--o{ INSPECTION_RECORD : has
    DEFECT ||--o{ INSPECTION_RECORD : appears_in
    LOT ||--o| SHIPMENT_RECORD : ships_as

    LOT {
        lot_id string
    }

    PRODUCTION_LINE {
        production_line string
    }

    DEFECT {
        defect_code string
    }

    PRODUCTION_RECORD {
        record_date string
    }

    INSPECTION_RECORD {
        inspection_date string
        qty_defects int
    }

    SHIPMENT_RECORD {
        ship_date string
        is_shipped boolean
    }


