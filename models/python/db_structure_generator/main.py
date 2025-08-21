# models/python/db_structure_generator/main.py
import os
import sys
from pathlib import Path

# Aggiungi il percorso dei moduli
sys.path.append(str(Path(__file__).parent))

from excel_reader import ExcelReader
from schema_analyzer import SchemaAnalyzer
from sql_generator import SQLGenerator
from utils import setup_logging, ensure_output_directory

def main():
    """
    Funzione principale per generare la struttura del database
    """
    # Setup logging
    logger = setup_logging()
    logger.info("Avvio generazione struttura database")
    
    try:
        # Percorsi
        base_path = Path(__file__).parent.parent.parent.parent  # Torna alla root
        excel_file = base_path / "data" / "financialTracker.xlsx"
        output_dir = base_path / "sql" / "ddl"
        
        # Verifica esistenza file Excel
        if not excel_file.exists():
            raise FileNotFoundError(f"File Excel non trovato: {excel_file}")
        
        # Crea directory di output se non esistente
        ensure_output_directory(output_dir)
        
        # 1. Lettura Excel
        logger.info("Lettura file Excel...")
        excel_reader = ExcelReader(excel_file)
        sheets_data = excel_reader.read_all_sheets()
        
        # 2. Analisi schemi
        logger.info("Analisi schemi e tabelle...")
        analyzer = SchemaAnalyzer()
        schema_structure = analyzer.analyze_sheets(sheets_data)
        
        # 3. Generazione SQL
        logger.info("Generazione codice SQL...")
        sql_generator = SQLGenerator()
        sql_content = sql_generator.generate_ddl(schema_structure)
        
        # 4. Salvataggio file
        output_file = output_dir / "financial_tracker_ddl.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        logger.info(f"DDL generato con successo: {output_file}")
        print(f"✅ File SQL generato: {output_file}")
        
    except Exception as e:
        logger.error(f"Errore durante la generazione: {str(e)}")
        print(f"❌ Errore: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()