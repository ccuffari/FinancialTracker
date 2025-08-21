# db_structure_generator/cli.py
import typer
from pathlib import Path
from typing import Optional
from .core import generate_sql_from_excel

app = typer.Typer(help="DB structure generator from excel sheets")

def _default_excel_path() -> Path:
    """
    Restituisce il path di default:
    <repo-root>/data/financialTracker.xlsx

    Nota: questo file presuppone la struttura:
    project-root/
    ├─ data/financialTracker.xlsx
    └─ models/python/db_structure_generator/cli.py  <-- qui

    Per calcolare project-root si risale di 3 directory da questo file:
    db_structure_generator -> python -> models -> project-root
    """
    # parents[3] porta alla radice del repo (project-root)
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "data" / "financialTracker.xlsx"

@app.command()
def main(
    excel_file: Optional[Path] = typer.Option(
        None,
        help="Path to input Excel file (.xlsx). If omitted, uses data/financialTracker.xlsx at repo root."
    ),
    out_dir: Path = typer.Option(Path("sql/ddl"), help="Output directory for generated SQL"),
    config: Path = typer.Option(Path("models/python/db_structure_generator/configs/generator.yml"), help="Optional config file"),
):
    # se non passato, usa il file di default alla radice del repo
    if excel_file is None:
        excel_file = _default_excel_path()

    excel_file = excel_file.resolve()
    if not excel_file.exists():
        typer.echo(f"[ERROR] Excel file not found: {excel_file}", err=True)
        raise typer.Exit(code=2)

    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    generated = generate_sql_from_excel(str(excel_file), str(config), str(out_dir))
    typer.echo(f"Generated {len(generated)} SQL files in {out_dir}")

if __name__ == "__main__":
    app()
