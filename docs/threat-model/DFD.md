# Data Flow Diagram (DFD) — OKR Tracker (FastAPI)

## Level 0 — Context Diagram
```mermaid
flowchart LR
  User[User Frontend]

  subgraph CoreTB["Trust Boundary: Core System"]
    API[OKR API]
    DB[(SQLite DB)]
  end

  User -->|F1 HTTPS| API
  API  -->|F2 DB access via ORM| DB
```

## Level 1 — Logical Data Flow (Endpoints & Services)
```mermaid
flowchart TB
  U[User Frontend]

  subgraph Edge["Trust Boundary: API Edge"]
    OBJ_CREATE[Create Objective]
    OBJ_READ[Get Objectives]
    OBJ_READ_ONE[Get Objective by id]
    OBJ_DELETE[Delete Objective]
    OBJ_PROGRESS[Get Progress]
    KR_CREATE[Create KeyResult]
    KR_UPDATE[Update KeyResult]
    KR_LIST_BY_OBJ[List KRs by Objective]
    KR_DELETE[Delete KeyResult]
  end

  subgraph Core["Trust Boundary: Core System"]
    DB[(SQLite)]
  end

  U -->|F3 POST /objectives| OBJ_CREATE
  U -->|F4 GET /objectives| OBJ_READ
  U -->|F5 GET /objectives/:id| OBJ_READ_ONE
  U -->|F6 DELETE /objectives/:id| OBJ_DELETE
  U -->|F7 GET /objectives/:id/progress| OBJ_PROGRESS
  U -->|F8 POST /key_results| KR_CREATE
  U -->|F9 PUT /key_results/:id| KR_UPDATE
  U -->|F10 GET /key_results/:obj_id/by_objective| KR_LIST_BY_OBJ
  U -->|F11 DELETE /key_results/:id| KR_DELETE

  OBJ_CREATE -->|F12 Insert| DB
  OBJ_READ -->|F13 Select| DB
  OBJ_READ_ONE -->|F14 Select| DB
  OBJ_DELETE -->|F15 Delete cascade KRs| DB
  OBJ_PROGRESS -->|F16 Aggregate| DB
  KR_CREATE -->|F17 Insert| DB
  KR_UPDATE -->|F18 Update| DB
  KR_LIST_BY_OBJ -->|F19 Select| DB
  KR_DELETE -->|F20 Delete| DB
```

## Level 2 — Internal Processes (Middleware -> Validation -> ORM -> Logging)
```mermaid
flowchart TB
  subgraph Core["Trust Boundary: Core System"]
    IN[HTTP Request]
    L1[Access logging middleware]
    EXC[Exception logging middleware]
    LIM[Body size limit 413 if gt 1MB]
    VAL[Pydantic validation]
    HND[Endpoint handler]
    ORM[SQLAlchemy ORM]
    TXN[Commit / rollback]
    OUT[JSON response]

    IN  -->|F21| L1
    L1  -->|F22| EXC
    EXC -->|F23| LIM
    LIM -->|F24| VAL
    VAL -->|F25| HND
    HND -->|F26| ORM
    ORM -->|F27| TXN
    TXN -->|F28| OUT
  end
```

## Trust Boundaries
- TB1: HTTP boundary — User <-> API
- TB2: DB boundary — API <-> SQLite
- TB3: Middleware boundary — Request <-> Validation/Logging/Body Limit
