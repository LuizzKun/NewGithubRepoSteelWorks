-- db/schema.sql
-- SteelWorks Operations - Physical Data Design (PostgreSQL)

BEGIN;

DROP TABLE IF EXISTS shipment_records;
DROP TABLE IF EXISTS production_records;
DROP TABLE IF EXISTS production_lines;
DROP TABLE IF EXISTS lots;

-- =========================
-- Dimension tables
-- =========================

CREATE TABLE lots (
    id BIGSERIAL PRIMARY KEY,
    lot_code TEXT NOT NULL UNIQUE
);

CREATE TABLE production_lines (
    id BIGSERIAL PRIMARY KEY,
    line_code TEXT NOT NULL UNIQUE
);

-- =========================
-- Production (Ops_Production_Log)
-- =========================

CREATE TABLE production_records (
    id BIGSERIAL PRIMARY KEY,

    lot_id BIGINT NOT NULL,
    production_line_id BIGINT NOT NULL,

    record_date DATE NOT NULL,
    shift TEXT NOT NULL,

    part_number TEXT NOT NULL,

    units_planned INTEGER NOT NULL,
    units_actual INTEGER NOT NULL,
    downtime_minutes INTEGER NOT NULL,

    has_line_issue BOOLEAN NOT NULL,
    primary_issue TEXT,
    supervisor_notes TEXT,

    CONSTRAINT fk_production_records_lot
        FOREIGN KEY (lot_id)
        REFERENCES lots(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_production_records_production_line
        FOREIGN KEY (production_line_id)
        REFERENCES production_lines(id)
        ON DELETE RESTRICT,

    CONSTRAINT ck_units_planned_nonneg CHECK (units_planned >= 0),
    CONSTRAINT ck_units_actual_nonneg CHECK (units_actual >= 0),
    CONSTRAINT ck_downtime_nonneg CHECK (downtime_minutes >= 0),

    -- values observed in your Excel: Day, Night, Swing
    CONSTRAINT ck_shift_valid CHECK (shift IN ('Day', 'Night', 'Swing'))
);

-- =========================
-- Shipping (Ops_Shipping_Log)
-- NOTE: multiple shipments per lot are allowed (Partial/Backordered/etc.)
-- =========================

CREATE TABLE shipment_records (
    id BIGSERIAL PRIMARY KEY,

    lot_id BIGINT NOT NULL,

    ship_date DATE,
    ship_status TEXT NOT NULL,
    qty_shipped INTEGER NOT NULL,

    sales_order_number TEXT,
    customer TEXT,
    destination_state TEXT,
    carrier TEXT,
    bol_number TEXT,
    tracking_pro TEXT,
    hold_reason TEXT,
    shipping_notes TEXT,

    CONSTRAINT fk_shipment_records_lot
        FOREIGN KEY (lot_id)
        REFERENCES lots(id)
        ON DELETE CASCADE,

    CONSTRAINT ck_qty_shipped_nonneg CHECK (qty_shipped >= 0),

    -- values observed in your Excel: Shipped, Partial, On Hold, Backordered
    CONSTRAINT ck_ship_status_valid
        CHECK (ship_status IN ('Shipped', 'Partial', 'On Hold', 'Backordered')),

    -- If shipped/partial, require ship_date; otherwise allow null
    CONSTRAINT ck_ship_date_logic
        CHECK (
            (ship_status IN ('Shipped','Partial') AND ship_date IS NOT NULL)
            OR
            (ship_status IN ('On Hold','Backordered') AND ship_date IS NULL)
        )
);

-- =========================
-- Indexes to support reporting queries
-- =========================

CREATE INDEX idx_production_records_line_date
    ON production_records(production_line_id, record_date);

CREATE INDEX idx_production_records_lot_date
    ON production_records(lot_id, record_date);

CREATE INDEX idx_shipment_records_lot_date
    ON shipment_records(lot_id, ship_date);

CREATE INDEX idx_shipment_records_status
    ON shipment_records(ship_status);

COMMIT;

