-- db/sample_queries.sql
-- SteelWorks Operations - Sample Queries

-- 1) Which production lines had the most "line issues" in the last 7 days?
SELECT
  pl.line_code AS production_line,
  COUNT(*) AS issue_days
FROM production_records pr
JOIN production_lines pl ON pl.id = pr.production_line_id
WHERE pr.record_date >= (CURRENT_DATE - INTERVAL '7 days')
  AND pr.has_line_issue = TRUE
GROUP BY pl.line_code
ORDER BY issue_days DESC;


-- 2) Downtime trend by production line (weekly, last 90 days)
SELECT
  pl.line_code AS production_line,
  DATE_TRUNC('week', pr.record_date)::date AS week_start,
  SUM(pr.downtime_minutes) AS total_downtime_minutes
FROM production_records pr
JOIN production_lines pl ON pl.id = pr.production_line_id
WHERE pr.record_date >= (CURRENT_DATE - INTERVAL '90 days')
GROUP BY pl.line_code, week_start
ORDER BY week_start ASC, total_downtime_minutes DESC;


-- 3) Has a lot shipped? (latest shipping status for a lot_code)
SELECT
  l.lot_code,
  sr.ship_status,
  sr.ship_date,
  sr.qty_shipped
FROM lots l
JOIN shipment_records sr ON sr.lot_id = l.id
WHERE l.lot_code = 'LOT-20251219-001'
ORDER BY sr.ship_date DESC NULLS LAST, sr.id DESC
LIMIT 1;


-- 4) Total quantity shipped per lot (helps explain partial/backordered)
SELECT
  l.lot_code,
  SUM(sr.qty_shipped) AS total_qty_shipped
FROM lots l
JOIN shipment_records sr ON sr.lot_id = l.id
WHERE l.lot_code = 'LOT-20251219-001'
GROUP BY l.lot_code;


-- 5) Compare production + shipment by lot (single view)
SELECT
  l.lot_code,
  pr.record_date,
  pr.shift,
  pl.line_code AS production_line,
  pr.part_number,
  pr.units_planned,
  pr.units_actual,
  pr.downtime_minutes,
  pr.has_line_issue,
  pr.primary_issue,
  sr.ship_status,
  sr.ship_date,
  sr.qty_shipped
FROM lots l
LEFT JOIN production_records pr ON pr.lot_id = l.id
LEFT JOIN production_lines pl ON pl.id = pr.production_line_id
LEFT JOIN shipment_records sr ON sr.lot_id = l.id
WHERE l.lot_code = 'LOT-20251219-001'
ORDER BY pr.record_date, sr.ship_date NULLS LAST;


-- 6) Lots with production line issues that are already shipped (risk report)
SELECT
  l.lot_code,
  pl.line_code AS production_line,
  MAX(pr.record_date) AS last_issue_date,
  MAX(sr.ship_date) AS last_ship_date
FROM lots l
JOIN production_records pr ON pr.lot_id = l.id
JOIN production_lines pl ON pl.id = pr.production_line_id
JOIN shipment_records sr ON sr.lot_id = l.id
WHERE pr.has_line_issue = TRUE
  AND sr.ship_status IN ('Shipped','Partial')
GROUP BY l.lot_code, pl.line_code
ORDER BY last_ship_date DESC NULLS LAST;
