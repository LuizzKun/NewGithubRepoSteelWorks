# Architecture Decision Record — Operations Role

## Status
Accepted

---

## Context

The operations team needs the ability to review and summarize production, inspection, and shipment information across multiple Excel data sources.

The system must:

- Allow cross-departmental data comparison by lot and date
- Support summary-level operational reporting
- Maintain data consistency across production, inspection, and shipment records
- Be easy to understand and maintain within a course project environment

Because the system is part of a student-developed internal tool, simplicity and clarity are more important than scalability or distributed system design.

---

## Decision

We will use a single relational database to store normalized operational data and support reporting queries.

The architecture will follow:

- Client–Server model
- Monolithic codebase
- Layered structure:
  - Presentation Layer (Streamlit UI)
  - Service Layer (business logic for reporting)
  - Data Access Layer (SQLAlchemy models and queries)
  - PostgreSQL database
- Synchronous request/response workflow

---

## Alternatives Considered

### Denormalized Spreadsheet Storage
Rejected because:
- Difficult to enforce referential integrity
- Harder to perform cross-table aggregation

### Event-Driven or Microservices Architecture
Rejected because:
- Adds unnecessary complexity for a course project
- Not required for summary-level operational reporting

---

## Consequences

### Positive

- Clear mapping between operations questions and database schema
- Strong referential integrity using foreign keys
- Efficient aggregation through indexed queries
- Simple deployment and demonstration
- Easy to test reporting queries

### Negative

- Limited scalability compared to distributed architectures
- Tight coupling to a single relational schema
- Requires data import step from Excel before reporting

---
