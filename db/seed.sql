-- Seed Data for SteelWorks Operations Database
-- This file populates the database with sample data for testing and demo purposes

-- Insert Production Lines
INSERT INTO production_lines (line_code) VALUES
('LINE-A'),
('LINE-B'),
('LINE-C')
ON CONFLICT (line_code) DO NOTHING;

-- Insert Lots
INSERT INTO lots (lot_code) VALUES
('LOT-2026-001'),
('LOT-2026-002'),
('LOT-2026-003'),
('LOT-2026-004'),
('LOT-2026-005')
ON CONFLICT (lot_code) DO NOTHING;

-- Insert Production Records
INSERT INTO production_records (
    lot_id, production_line_id, record_date, shift, 
    part_number, units_planned, units_actual, downtime_minutes,
    has_line_issue, primary_issue
)
SELECT 
    l.id, pl.id, 
    CURRENT_DATE - (random() * 30)::integer,
    CASE WHEN random() < 0.5 THEN 'Day' ELSE 'Night' END,
    'PART-' || LPAD((random() * 100)::integer::text, 3, '0'),
    (80 + random() * 120)::integer,
    (70 + random() * 120)::integer,
    (random() * 60)::integer,
    random() < 0.3,
    CASE WHEN random() < 0.3 THEN 
        CASE (random() * 3)::integer
            WHEN 0 THEN 'Tooling wear'
            WHEN 1 THEN 'Material delay'
            ELSE 'Equipment malfunction'
        END
    ELSE NULL END
FROM lots l
CROSS JOIN production_lines pl
WHERE random() < 0.6
ON CONFLICT DO NOTHING;

-- Insert Inspection Records (Defects)
INSERT INTO inspection_records (
    lot_id, inspection_date, defect_type, quantity_defective
)
SELECT 
    l.id,
    CURRENT_DATE - (random() * 25)::integer,
    CASE (random() * 5)::integer
        WHEN 0 THEN 'Scratch'
        WHEN 1 THEN 'Dent'
        WHEN 2 THEN 'Discoloration'
        WHEN 3 THEN 'Crack'
        ELSE 'Deformation'
    END,
    (1 + random() * 15)::integer
FROM lots l
CROSS JOIN generate_series(1, 3) s
WHERE random() < 0.4
ON CONFLICT DO NOTHING;

-- Insert Shipment Records (Shipped)
INSERT INTO shipment_records (
    lot_id, ship_status, ship_date, qty_shipped, customer
)
SELECT 
    l.id,
    'Shipped',
    CURRENT_DATE - (random() * 20)::integer,
    (50 + random() * 100)::integer,
    'Customer-' || CHR(65 + (random() * 5)::integer)
FROM lots l
WHERE random() < 0.6
ON CONFLICT DO NOTHING;

-- Insert Shipment Records (On Hold)
INSERT INTO shipment_records (
    lot_id, ship_status, ship_date, qty_shipped, customer
)
SELECT 
    l.id,
    'On Hold',
    NULL,
    (50 + random() * 100)::integer,
    'Customer-' || CHR(65 + (random() * 5)::integer)
FROM lots l
WHERE id NOT IN (SELECT lot_id FROM shipment_records)
ON CONFLICT DO NOTHING;

-- Success message
SELECT 'Seed data successfully loaded!' as status;
