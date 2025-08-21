# models/python/db_structure_generator/sql_generator.py
from typing import Dict, List, Set
import logging
from datetime import datetime

class SQLGenerator:
    """
    Classe per generare il codice SQL DDL
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_ddl(self, schema_structure: Dict) -> str:
        """
        Genera il codice DDL completo
        
        Args:
            schema_structure: Struttura degli schemi e tabelle
            
        Returns:
            Codice SQL DDL
        """
        sql_parts = []
        
        # Header del file
        sql_parts.append(self._generate_header())
        
        # Inizio transazione (tutto o niente)
        sql_parts.append("BEGIN;")
        sql_parts.append("")
        
        # Creazione schemi
        sql_parts.append("-- =====================================")
        sql_parts.append("-- CREAZIONE SCHEMI")
        sql_parts.append("-- =====================================")
        sql_parts.append("")
        
        for schema in sorted(schema_structure['schemas']):
            sql_parts.append(f"CREATE SCHEMA IF NOT EXISTS {schema};")
        
        sql_parts.append("")
        
        # Creazione tabelle (dates.dates per prima)
        sql_parts.append("-- =====================================")
        sql_parts.append("-- CREAZIONE TABELLE")
        sql_parts.append("-- =====================================")
        sql_parts.append("")
        
        # Prima crea dates.dates
        if 'dates.dates' in schema_structure['tables']:
            table_sql = self._generate_table_sql(
                'dates.dates', 
                schema_structure['tables']['dates.dates']
            )
            sql_parts.append(table_sql)
            sql_parts.append("")
        
        # Poi crea le altre tabelle
        for table_name in sorted(schema_structure['tables'].keys()):
            if table_name != 'dates.dates':
                table_sql = self._generate_table_sql(
                    table_name, 
                    schema_structure['tables'][table_name]
                )
                sql_parts.append(table_sql)
                sql_parts.append("")
        
        # Foreign Key Constraints
        if schema_structure['relationships']:
            sql_parts.append("-- =====================================")
            sql_parts.append("-- FOREIGN KEY CONSTRAINTS")
            sql_parts.append("-- =====================================")
            sql_parts.append("")
            
            for relationship in schema_structure['relationships']:
                fk_sql = self._generate_foreign_key_sql(relationship)
                sql_parts.append(fk_sql)
                sql_parts.append("")
        
        # Commit transazione
        sql_parts.append("-- =====================================")
        sql_parts.append("-- COMMIT TRANSAZIONE")
        sql_parts.append("-- =====================================")
        sql_parts.append("COMMIT;")
        
        return "\n".join(sql_parts)
    
    def _generate_header(self) -> str:
        """
        Genera l'header del file SQL
        
        Returns:
            Header del file
        """
        return f"""-- =====================================
-- FINANCIAL TRACKER DATABASE DDL
-- =====================================
-- Generato automaticamente il {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- 
-- Questo script crea la struttura completa del database
-- per il Financial Tracker. La transazione è atomica:
-- o vengono create tutte le strutture o nessuna.
-- =====================================

"""
    
    def _generate_table_sql(self, table_full_name: str, table_info: Dict) -> str:
        """
        Genera l'SQL per creare una tabella
        
        Args:
            table_full_name: Nome completo della tabella (schema.tabella)
            table_info: Informazioni sulla tabella
            
        Returns:
            SQL per creare la tabella
        """
        schema = table_info['schema']
        table = table_info['table']
        columns = table_info['columns']
        primary_key = table_info['primary_key']
        
        sql_parts = []
        sql_parts.append(f"-- Tabella: {table_full_name}")
        sql_parts.append(f"CREATE TABLE {schema}.{table} (")
        
        # Definizioni colonne
        column_definitions = []
        for col in columns:
            col_def = self._generate_column_definition(col)
            column_definitions.append(f"    {col_def}")
        
        sql_parts.append(",\n".join(column_definitions))
        
        # Primary Key
        if primary_key:
            sql_parts.append(f",\n    CONSTRAINT pk_{schema}_{table} PRIMARY KEY ({primary_key})")
        
        sql_parts.append(");")
        
        return "\n".join(sql_parts)
    
    def _generate_column_definition(self, column: Dict) -> str:
        """
        Genera la definizione SQL di una colonna
        
        Args:
            column: Informazioni sulla colonna
            
        Returns:
            Definizione SQL della colonna
        """
        parts = [column['name'], column['type']]
        
        if not column['nullable']:
            parts.append('NOT NULL')
        
        return ' '.join(parts)
    
    def _generate_foreign_key_sql(self, relationship: Dict) -> str:
        """
        Genera l'SQL per un constraint foreign key
        
        Args:
            relationship: Informazioni sulla relazione
            
        Returns:
            SQL per il constraint foreign key
        """
        child_schema, child_table = relationship['child_table'].split('.')
        parent_schema, parent_table = relationship['parent_table'].split('.')
        
        constraint_name = f"fk_{child_schema}_{child_table}_{relationship['child_column']}"
        
        return f"""-- Foreign Key: {relationship['child_table']}.{relationship['child_column']} -> {relationship['parent_table']}.{relationship['parent_column']}
ALTER TABLE {child_schema}.{child_table}
    ADD CONSTRAINT {constraint_name}
    FOREIGN KEY ({relationship['child_column']})
    REFERENCES {parent_schema}.{parent_table} ({relationship['parent_column']})
    ON DELETE RESTRICT
    ON UPDATE CASCADE;"""