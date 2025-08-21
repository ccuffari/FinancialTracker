# db_structure_generator/cli.py
import typer
from pathlib import Path
from .core import generate_sql_from_excel

app = typer.Typer(help="DB structure generator from excel sheets")

@app.command()
def main(
    excel_file: Path = typer.Option(..., help="Path to input Excel file (.xlsx)"),
    out_dir: Path = typer.Option(Path("sql/ddl"), help="Output directory for generated SQL"),
    config: Path = typer.Option(Path("models/python/db_structure_generator/configs/generator.yml"), help="Optional config file"),
):
    excel_file = excel_file.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = generate_sql_from_excel(str(excel_file), str(config), str(out_dir))
    typer.echo(f"Generated {len(generated)} SQL files in {out_dir}")

if __name__ == "__main__":
    app()
