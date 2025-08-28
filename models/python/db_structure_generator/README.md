# Financial ETL

Questo progetto mette in piedi un piccolo ETL che:
- legge i fogli di un file Excel (`financialTracker.xlsx`) con naming `schema.table`;
- crea gli schemi e le tabelle corrispondenti su PostgreSQL;
- normalizza le colonne "date" in una tabella centrale `dates.dates` e crea foreign key che puntano a `dates.dates(date_id)`;
- carica i dati nelle tabelle target.

## Requisiti
- Python 3.9+
- pacchetti (vedi `requirements.txt`): `pandas`, `openpyxl`, `psycopg2-binary`, `python-dotenv`, `python-dateutil`
- accesso alla rete al DB PostgreSQL/Neon

## Installazione
1. Creare un virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # su Windows: .venv\Scripts\activate
   pip install -r requirements.txt
Creare un file .env (o editare config.py) con le credenziali:

ini
Copy code
PGHOST=...
PGDATABASE=...
PGUSER=...
PGPASSWORD=...
EXCEL_FILE=financialTracker.xlsx
LOG_FILE=logs/financial_etl.log
Come funziona
extractor.py legge tutti i fogli e seleziona solo quelli in formato schema.table. Ignora public.overview.

ddl_builder.py costruisce le istruzioni SQL per creare schemi e tabelle:

colonne id => INTEGER PRIMARY KEY.

colonne che contengono date => INTEGER con FK su dates.dates(date_id).

tutte le altre => DECIMAL(18,4).

main.py esegue la creazione degli schemi e delle tabelle, quindi l'ETL:

le colonne data vengono parse come YYYY-MM-DD (se possibile) e inserite nella tabella dates.dates (se non presenti).

durante il LOAD le date nella tabella target vengono sostituite dal corrispondente date_id.

I log sono scritti in logs/financial_etl.log.

Avvertenze e limiti
Questo progetto effettua una minima trasformazione per mappare le date in date_id (necessario per le FK). Se desideri mantenere le colonne data come DATE native (senza FK) e non avere la tabella dates.dates, modifica ddl_builder.py ed etl.py.

I nomi schema/table/colonna sono “sanitizzati” sostituendo caratteri non permessi con underscore.

Non è pensato per carichi concorrenti o per scenari di co-authoring di Excel via OneDrive: usa un export locale del file.

Fai una copia del DB / backup prima di eseguire in produzione.

Esempio di esecuzione
bash
Copy code
python main.py
Miglioramenti possibili
supporto per tipi non-decimali (VARCHAR, BOOLEAN, ecc.)

gestione transazionale con rollback in caso di errore

controllo più raffinato per la definizione delle chiavi primarie/indice

supporto per upsert nelle tabelle target