# db_structure_generator/tests/test_infer.py
def test_basic_infer():
    from db_structure_generator.schema_infer import infer_column_properties
    headers = ["date","amount","note"]
    columns = {
        "date": ["01/2023","02/2023"],
        "amount": ["100,00 €", "200.50"],
        "note": ["x", None]
    }
    meta = infer_column_properties("Sheet1", headers, columns)
    assert meta["date"]["sql_type"] == "DATE"
    assert "NUMERIC" in meta["amount"]["sql_type"]
    assert meta["note"]["sql_type"].startswith("VARCHAR")
