# Tech Stack Decision Record — Operations Role

## Status
Accepted

---

## Context

The operations reporting system must:

- Support relational joins across production, inspection, and shipment data
- Handle structured reporting queries efficiently
- Be compatible with AI-assisted development tools
- Be simple enough for undergraduate implementation

---

## Decision

We will use the following stack:

- Python (primary language)
- Poetry (dependency management)
- Pytest (testing)
- Streamlit (UI layer)
- SQLAlchemy (ORM / data access)
- PostgreSQL (relational database)

The system architecture remains:

- Layered (UI → Service → Repository → DB)
- Monolithic
- Synchronous
- Single relational database

---

## Alternatives Considered

### NoSQL Database
Rejected because:
- Operations reporting requires relational joins
- Referential integrity is important

### Direct Excel Querying
Rejected because:
- Difficult to maintain consistency
- Harder to enforce constraints
- Poor scalability for reporting

---

## Consequences

### Positive

- Strong relational modeling with PostgreSQL
- Clear enforcement of constraints and foreign keys
- Efficient aggregation using indexed queries
- Excellent AI support ecosystem
- Easy local development for students

### Negative

- Manual Excel import required before querying
- ORM abstraction may hide query performance issues
- Not optimized for large-scale distributed systems

