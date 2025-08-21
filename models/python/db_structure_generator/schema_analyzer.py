# models/python/db_structure_generator/schema_analyzer.py
import pandas as pd
from typing import Dict, List, Set, Tuple
import logging
import re

class SchemaAnalyzer:
    """
    Classe per analizzare gli schemi e le tabelle dal file Excel
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.schemas = set()
        self.tables = {}
        
    def analyze_sheets(self, sheets_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Analizza tutti i fogli per estrarre la struttura degli schemi
        
        Args:
            sheets_data: Dizionario con i dati dei fogli
            
        Returns:
            Struttura degli schemi e tabelle
        """
        schema_structure = {
            'schemas': set(),
            'tables': {},
            'relationships': []
        }
        
        # Analizza ogni foglio
        for sheet_name, df in sheets_data.items():
            schema_name, table_name = self._parse_sheet_name(sheet_name)
            
            # Aggiungi schema
            schema_structure['schemas'].add(schema_name)
            
            # Analizza colonne della tabella
            columns = self._analyze_columns(df, sheet_name)
            
            # Determina primary key
            primary_key = self._determine_primary_key(columns, sheet_name)
            
            # Aggiungi tabella
            schema_structure['tables'][sheet_name] = {
                'schema': schema_name,
                'table': table_name,
                'columns': columns,
                'primary_key': primary_key
            }
            
            # Aggiungi relazioni (FK verso dates.dates)
            if sheet_name != "dates.dates":
                relationship = self._create_relationship(sheet_name, primary_key)
                if relationship:
                    schema_structure['relationships'].append(relationship)
        
        self.logger.info(f"Analisi completata: {len(schema_structure['schemas'])} schemi, {len(schema_structure['tables'])} tabelle")
        return schema_structure
    
    def _parse_sheet_name(self, sheet_name: str) -> Tuple[str, str]:
        """
        Estrae schema e nome tabella dal nome del foglio
        
        Args:
            sheet_name: Nome del foglio (formato schema.tabella)
            
        Returns:
            Tupla (schema, tabella)
        """
        parts = sheet_name.split('.', 1)
        return parts[0], parts[1]
    
    def _analyze_columns(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """
        Analizza le colonne di una tabella
        
        Args:
            df: DataFrame della tabella
            sheet_name: Nome del foglio
            
        Returns:
            Lista delle definizioni delle colonne
        """
        columns = []
        
        if df.empty:
            return columns
        
        column_names = df.columns.tolist()
        
        for col_name in column_names:
            if pd.isna(col_name) or str(col_name).strip() == '':
                continue
            
            col_name = str(col_name).strip()
            column_def = self._create_column_definition(col_name, df[col_name], sheet_name)
            columns.append(column_def)
        
        return columns
    
    def _create_column_definition(self, col_name: str, col_data: pd.Series, sheet_name: str) -> Dict:
        """
        Crea la definizione di una colonna
        
        Args:
            col_name: Nome della colonna
            col_data: Dati della colonna
            sheet_name: Nome del foglio
            
        Returns:
            Definizione della colonna
        """
        # Determina il tipo di dato
        data_type = self._determine_data_type(col_name, col_data)
        
        # Determina se nullable
        nullable = self._is_nullable(col_name, sheet_name)
        
        return {
            'name': col_name,
            'type': data_type,
            'nullable': nullable,
            'is_primary_key': False,  # Sarà impostato successivamente
            'is_foreign_key': False   # Sarà impostato successivamente
        }
    
    def _determine_data_type(self, col_name: str, col_data: pd.Series) -> str:
        """
        Determina il tipo di dato SQL per una colonna
        
        Args:
            col_name: Nome della colonna
            col_data: Dati della colonna
            
        Returns:
            Tipo di dato SQL
        """
        col_name_lower = col_name.lower()
        
        # Colonna date
        if col_name_lower == 'date':
            return 'VARCHAR(7)'  # MM/YYYY format
        
        # Colonne monetarie (tutte le altre sono valori in €)
        return 'DECIMAL(15,2)'
    
    def _is_nullable(self, col_name: str, sheet_name: str) -> bool:
        """
        Determina se una colonna può essere NULL
        
        Args:
            col_name: Nome della colonna
            sheet_name: Nome del foglio
            
        Returns:
            True se la colonna può essere NULL
        """
        col_name_lower = col_name.lower()
        
        # La colonna date non può mai essere NULL (è PK o FK)
        if col_name_lower == 'date':
            return False
        
        # Le altre colonne possono essere NULL
        return True
    
    def _determine_primary_key(self, columns: List[Dict], sheet_name: str) -> str:
        """
        Determina la primary key per una tabella
        
        Args:
            columns: Lista delle colonne
            sheet_name: Nome del foglio
            
        Returns:
            Nome della colonna primary key
        """
        # Per dates.dates, la colonna date è PK
        if sheet_name == "dates.dates":
            for col in columns:
                if col['name'].lower() == 'date':
                    col['is_primary_key'] = True
                    return col['name']
        else:
            # Per tutte le altre tabelle, la colonna date è PK (che referenzia dates.dates)
            for col in columns:
                if col['name'].lower() == 'date':
                    col['is_primary_key'] = True
                    col['is_foreign_key'] = True
                    return col['name']
        
        return None
    
    def _create_relationship(self, sheet_name: str, foreign_key_column: str) -> Dict:
        """
        Crea una relazione foreign key
        
        Args:
            sheet_name: Nome del foglio (tabella child)
            foreign_key_column: Nome della colonna FK
            
        Returns:
            Definizione della relazione
        """
        if not foreign_key_column:
            return None
        
        return {
            'child_table': sheet_name,
            'child_column': foreign_key_column,
            'parent_table': 'dates.dates',
            'parent_column': 'date'
        }