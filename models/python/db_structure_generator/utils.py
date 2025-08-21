# models/python/db_structure_generator/utils.py
import logging
import os
from pathlib import Path
from typing import Optional

def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """
    Configura il sistema di logging
    
    Args:
        log_level: Livello di logging (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger configurato
    """
    # Configura il formato del log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configura il logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Output su console
        ]
    )
    
    return logging.getLogger('db_structure_generator')

def ensure_output_directory(output_dir: Path) -> None:
    """
    Assicura che la directory di output esista
    
    Args:
        output_dir: Percorso della directory di output
    """
    output_dir.mkdir(parents=True, exist_ok=True)

def validate_excel_file(file_path: Path) -> bool:
    """
    Valida che il file Excel esista e sia accessibile
    
    Args:
        file_path: Percorso del file Excel
        
    Returns:
        True se il file è valido
    """
    if not file_path.exists():
        return False
    
    if not file_path.is_file():
        return False
    
    if file_path.suffix.lower() not in ['.xlsx', '.xls']:
        return False
    
    return True

def clean_identifier(identifier: str) -> str:
    """
    Pulisce un identificatore per renderlo valido per SQL
    
    Args:
        identifier: Identificatore da pulire
        
    Returns:
        Identificatore pulito
    """
    # Rimuovi spazi iniziali e finali
    identifier = identifier.strip()
    
    # Sostituisci spazi con underscore
    identifier = identifier.replace(' ', '_')
    
    # Rimuovi caratteri non validi (mantieni solo lettere, numeri, underscore)
    import re
    identifier = re.sub(r'[^a-zA-Z0-9_]', '', identifier)
    
    # Assicurati che inizi con una lettera o underscore
    if identifier and not identifier[0].isalpha() and identifier[0] != '_':
        identifier = f"_{identifier}"
    
    return identifier

def format_file_size(size_bytes: int) -> str:
    """
    Formatta la dimensione di un file in formato leggibile
    
    Args:
        size_bytes: Dimensione in bytes
        
    Returns:
        Dimensione formattata
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_project_root() -> Path:
    """
    Ottiene il percorso root del progetto
    
    Returns:
        Percorso root del progetto
    """
    # Dalla posizione corrente (models/python/db_structure_generator)
    # torna indietro di 3 livelli per raggiungere la root
    current_file = Path(__file__)
    return current_file.parent.parent.parent.parent