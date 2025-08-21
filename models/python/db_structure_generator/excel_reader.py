# models/python/db_structure_generator/excel_reader.py
import pandas as pd
from typing import Dict, List, Optional
import logging

class ExcelReader:
    """
    Classe per leggere il file Excel e estrarre i dati dai fogli
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
    
    def read_all_sheets(self) -> Dict[str, pd.DataFrame]:
        """
        Legge tutti i fogli dal file Excel
        
        Returns:
            Dict con nome foglio come chiave e DataFrame come valore
        """
        try:
            # Leggi tutti i fogli
            all_sheets = pd.read_excel(self.file_path, sheet_name=None)
            
            # Filtra i fogli validi (formato schema.tabella)
            valid_sheets = {}
            for sheet_name, df in all_sheets.items():
                if self._is_valid_sheet(sheet_name):
                    # Pulisci il DataFrame
                    cleaned_df = self._clean_dataframe(df)
                    if not cleaned_df.empty:
                        valid_sheets[sheet_name] = cleaned_df
                        self.logger.info(f"Foglio '{sheet_name}' caricato con {len(cleaned_df)} righe")
                else:
                    self.logger.info(f"Foglio '{sheet_name}' ignorato (non valido o escluso)")
            
            return valid_sheets
            
        except Exception as e:
            self.logger.error(f"Errore nella lettura del file Excel: {str(e)}")
            raise
    
    def _is_valid_sheet(self, sheet_name: str) -> bool:
        """
        Verifica se un foglio è valido secondo i criteri specificati
        
        Args:
            sheet_name: Nome del foglio
            
        Returns:
            True se il foglio è valido
        """
        # Escludi public.overview
        if sheet_name == "public.overview":
            return False
        
        # Controlla formato schema.tabella
        if '.' in sheet_name:
            parts = sheet_name.split('.')
            if len(parts) == 2 and all(part.strip() for part in parts):
                return True
        
        return False
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pulisce il DataFrame rimuovendo righe e colonne vuote
        
        Args:
            df: DataFrame da pulire
            
        Returns:
            DataFrame pulito
        """
        if df.empty:
            return df
        
        # Rimuovi colonne completamente vuote
        df = df.dropna(axis=1, how='all')
        
        # Rimuovi righe completamente vuote
        df = df.dropna(axis=0, how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def get_column_names(self, df: pd.DataFrame) -> List[str]:
        """
        Estrae i nomi delle colonne dalla prima riga del DataFrame
        
        Args:
            df: DataFrame di cui estrarre le colonne
            
        Returns:
            Lista dei nomi delle colonne
        """
        if df.empty:
            return []
        
        # I nomi delle colonne sono nella prima riga del DataFrame
        column_names = df.columns.tolist()
        
        # Pulisci i nomi delle colonne
        cleaned_names = []
        for col in column_names:
            if pd.isna(col) or str(col).strip() == '':
                continue
            cleaned_names.append(str(col).strip())
        
        return cleaned_names