# Retail Data Warehouse ETL Pipeline

A production-grade ETL pipeline that extracts transactional retail data from an Oracle OLTP source, validates it at every stage, and loads it into a clean star-schema data warehouse ready for analytics and reporting.

---

## What This Project Does

Most raw retail data sits in transactional systems optimized for writes, not analysis. This pipeline bridges that gap — it pulls daily snapshots of sales, store, product, and distributor data, validates it rigorously, transforms it into a dimensional model, and loads it into a structured Oracle data warehouse that analysts can actually query.

The result is a re-runnable, auditable pipeline that mirrors how real enterprise data engineering teams operate.

---

## Architecture

```
Oracle OLTP (Source)
        |
Daily CSV Snapshots  (pipe-delimited, timestamped)
        |
Data Validation      (file-level + table-level checks)
        |
Dimensional Transform (surrogate keys, incremental loads)
        |
Oracle Target DW     (star schema)
        |
Analytics / Reporting
```

---

## Data Layers

**Source Layer** — Read-only Oracle OLTP tables: `fact_sales`, `dim_store_master`, `dim_product`, `dim_distributor`, `dim_date`. Nothing is modified here.

**Extract Layer** — SQL joins produce daily pipe-delimited CSV snapshots stored under:

```
/opt/airflow/data_extracts/
    incoming/   sales_snapshot_YYYYMMDD_HHMM.csv
    current/
    archive/
```

Files decouple the source from the warehouse and make reprocessing straightforward.

**Validation Layer** — Two levels of checks run before any data reaches the warehouse:

- File validation: required columns, numeric types, Y/N flag values, minimum row count, delimiter integrity
- Table validation: row count thresholds, NULL checks on critical columns, duplicate primary key detection, fact table freshness

If any check fails, the pipeline stops immediately. No partial or silently corrupt loads.

**Target Data Warehouse** — A star schema under the `target_dw` schema in Oracle:

| Dimensions | Fact |
|---|---|
| `dim_store_dw` | `fact_sales_dw` |
| `dim_store_chain_dw` | |
| `dim_product_dw` | |
| `dim_category` | |
| `dim_sub_category` | |
| `dim_manufacturer` | |
| `dim_distributor_dw` | |
| `dim_date_dw` | |

---

## How Dimensions Are Loaded

Each dimension follows a set-based incremental load pattern:

1. Read the latest incoming file
2. Extract unique business keys
3. Pull existing keys from the DW into an in-memory cache
4. Identify only new records
5. Insert new records, update the cache
6. Map surrogate keys back to the working dataset

This avoids full-table reloads on every run and scales cleanly as data volumes grow.

---

## Manufacturer Enrichment

Manufacturers are derived from product category using controlled mappings, mimicking real master data enrichment:

| Category | Mapped Manufacturers |
|---|---|
| Grocery | Nestle, Tata Consumer, Britannia |
| BabyCare | Johnson & Johnson, P&G |
| PersonalCare | HUL, Dabur |

---

## Orchestration

Three Airflow DAGs run in sequence:

**Extraction DAG** — Generates daily snapshot files from the source system.

**Validation DAG** — Validates extracted files and source tables before any transformation begins.

**Target DW Load DAG** — Loads dimensions and facts in dependency order:

```
load_dim_store_dw
    >> load_dim_product_dw
    >> load_dim_distributor_dw
    >> load_dim_date_dw
    >> load_fact_sales_dw
```

All tasks have retry logic enabled. Failures are loud and logged clearly — nothing fails silently.

---

## Tech Stack

| Component | Tool |
|---|---|
| Database | Oracle |
| Orchestration | Apache Airflow |
| Language | Python |
| Libraries | pandas, oracledb |
| Containerization | Docker |
| Scheduling | Cron via Airflow |

---

## Running the Project

**Start Airflow**
```bash
docker-compose up -d
```

**Verify containers are running**
```bash
docker ps
```

**Open the Airflow UI**
```
http://localhost:8080
```

**Trigger DAGs in order**
1. Extraction pipeline
2. Validation pipeline
3. Target DW load pipeline

---

## Error Handling

The pipeline handles these failure modes explicitly:

- Invalid numeric values (`DPY-4004`)
- Empty or malformed files
- Missing foreign keys
- Duplicate business keys
- Partial data loads

Every failure produces clear logs. The pipeline is designed to be re-run safely after any fix.

---

## Outcome

After a successful run you get a fully populated star schema in Oracle with clean, validated, surrogate-key-based tables that are ready for BI tools or SQL-based analysis — with a complete audit trail of every load.
