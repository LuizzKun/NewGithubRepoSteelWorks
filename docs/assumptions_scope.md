# Assumptions and Scope — Operations Role
SteelWorks Internal Operations Reporting Tool

---

## Assumptions

### Assumption 1
We assume all production, inspection, and shipment Excel files contain a common lot identifier (e.g., Lot_ID or Lot Code) that allows relational mapping across departments.

### Assumption 2
We assume production line identifiers are consistent enough to map to a standardized production_lines table.

### Assumption 3
We assume defect types are categorized consistently in inspection logs and can be mapped to predefined defect types.

### Assumption 4
We assume shipment data contains a clear indicator of whether a lot has shipped and, if shipped, includes a shipment date.

### Assumption 5
We assume the Excel files represent historical operational data and are imported periodically rather than streamed in real time.

---

## In Scope

- Identifying which production lines had the most defects within a given time period
- Aggregating defect counts by lot, production line, and date
- Identifying defect trends over time
- Determining whether a lot has been shipped
- Comparing production, inspection, and shipment records for the same lot
- Enforcing referential integrity between lots, production lines, defects, and shipments

---

## Out of Scope

- Root cause analysis of production defects
- Predictive or AI-based defect forecasting
- Real-time production monitoring
- Inventory forecasting or materials planning
- Financial cost analysis
- Workforce or shift management
- Authentication, authorization, and role-based access control
- Enforcement of Excel data correctness at the source

