# Database Structure Generator

Questo modulo genera automaticamente la struttura del database SQL a partire dal file Excel `financialTracker.xlsx`.

## Struttura del Progetto

```
models/python/db_structure_generator/
├── __init__.py
├── main.py                 # Script principale
├── excel_reader.py         # Lettura file Excel
├── schema_analyzer.py      # Analisi schemi e tabelle
├── sql_generator.py        # Generazione codice SQL
├── utils.py               # Funzioni di utilità
├── requirements.txt       # Dipendenze Python
└── README.md             # Documentazione
```

## Funzionalità

- **Lettura Excel**: Legge tutti i fogli dal file `financialTracker.xlsx`
- **Filtro fogli**: Considera solo i fogli con formato `schema.tabella` (escluso `public.overview`)
- **Analisi colonne**: Identifica automaticamente i tipi di dato:
  - Colonna `date`: VARCHAR(7) per formato MM/YYYY
  - Altre colonne: DECIMAL(15,2) per valori monetari in €
- **Primary/Foreign Keys**: 
  - `dates.dates.date` è PRIMARY KEY
  - Tutte le altre tabelle hanno `date` come PK e FK verso `dates.dates`
- **Transazione atomica**: Tutto o niente - se un elemento fallisce, rollback completo

## Requisiti

- Python 3.8+
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- xlrd >= 2.0.0

## Installazione

```bash
cd models/python/db_structure_generator
pip install -r requirements.txt
```

## Utilizzo

```bash
python main.py
```

Il script:
1. Legge `data/financialTracker.xlsx` (relativamente alla root del progetto)
2. Analizza tutti i fogli con formato `schema.tabella`
3. Genera il file SQL `sql/ddl/financial_tracker_ddl.sql`

## Struttura Output

Il file SQL generato include:

1. **Header informativo** con timestamp
2. **BEGIN transaction** per atomicità
3. **CREATE SCHEMA** per tutti gli schemi identificati
4. **CREATE TABLE** (prima `dates.dates`, poi le altre)
5. **ALTER TABLE** per i vincoli Foreign Key
6. **COMMIT transaction**

## Esempio Output SQL

```sql
-- =====================================
-- FINANCIAL TRACKER DATABASE DDL
-- =====================================

BEGIN;

-- =====================================
-- CREAZIONE SCHEMI
-- =====================================

CREATE SCHEMA IF NOT EXISTS dates;
CREATE SCHEMA IF NOT EXISTS expenses;

-- =====================================
-- CREAZIONE TABELLE
-- =====================================

-- Tabella: dates.dates
CREATE TABLE dates.dates (
    date VARCHAR(7) NOT NULL,
    CONSTRAINT pk_dates_dates PRIMARY KEY (date)
);

-- Tabella: expenses.monthly
CREATE TABLE expenses.monthly (
    date VARCHAR(7) NOT NULL,
    rent DECIMAL(15,2),
    utilities DECIMAL(15,2),
    CONSTRAINT pk_expenses_monthly PRIMARY KEY (date)
);

-- =====================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================

ALTER TABLE expenses.monthly
    ADD CONSTRAINT fk_expenses_monthly_