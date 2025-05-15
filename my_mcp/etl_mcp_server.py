from fastmcp import FastMCP
import pandas as pd
from typing import List, Dict

# Create FastMCP server instance
mcp = FastMCP("etl-server")


@mcp.tool(name="read_csv_file")
def read_csv_file_tool(path: str, encoding: str = "utf-8") -> dict:
    """
    Reads a CSV file from the given path and returns its contents as a list of dicts.
    Args:
        path (str): Path to the CSV file.
        encoding (str, optional): File encoding (default "utf-8").
    Returns:
        dict: {"data": [...], "columns": [...]}
    """
    df = pd.read_csv(path, encoding=encoding)
    return {"data": df.to_dict(orient="records"), "columns": list(df.columns)}


@mcp.tool(name="check_data_types")
def check_data_types_tool(data: List[dict], type_mapping: Dict[str, str]) -> dict:
    """
    Ensures each column in data has the correct type according to the provided type mapping.
    Args:
        data (List[dict]): The data to check.
        type_mapping (Dict[str, str]): Mapping, e.g., {"column1": "int", "column2": "str"}.
    Returns:
        dict: {"data": [...]}
    Note:
        Agent must ask user for type_mapping if not provided in the request.
    """
    df = pd.DataFrame(data)
    for col, dtype in type_mapping.items():
        try:
            df[col] = df[col].astype(dtype)
        except Exception as e:
            raise ValueError(f"Column '{col}' cannot be converted to {dtype}: {e}")
    return {"data": df.to_dict(orient="records")}


@mcp.tool(name="detect_and_report_anomalies")
def detect_and_report_anomalies_tool(
    data: List[dict], anomaly_rules: Dict[str, dict]
) -> dict:
    """
    Checks for anomalies in the data based on provided rules (e.g., min/max for columns).
    Args:
        data (List[dict]): Data to analyze.
        anomaly_rules (Dict[str, dict]): Rules per column, e.g., {"age": {"min": 0, "max": 120}}.
    Returns:
        dict: {"anomalies": [...]}
    Note:
        Agent must ask user for anomaly_rules if not specified.
    """
    df = pd.DataFrame(data)
    anomalies = []
    for col, rule in anomaly_rules.items():
        if "min" in rule:
            out = df[df[col] < rule["min"]]
            if not out.empty:
                anomalies.extend(out.to_dict(orient="records"))
        if "max" in rule:
            out = df[df[col] > rule["max"]]
            if not out.empty:
                anomalies.extend(out.to_dict(orient="records"))
    return {"anomalies": anomalies}


@mcp.tool(name="remove_duplicates")
def remove_duplicates_tool(data: List[dict], subset_cols: List[str] = None) -> dict:
    """
    Removes duplicate rows in the data.
    Args:
        data (List[dict]): The data to deduplicate.
        subset_cols (List[str], optional): Columns to check for duplicates (default: all columns).
    Returns:
        dict: {"data": [...]}
    Note:
        If subset_cols is not given, remove duplicates across all columns.
    """
    df = pd.DataFrame(data)
    original_len = len(df)
    df = df.drop_duplicates(subset=subset_cols)
    new_len = len(df)
    if new_len == original_len:
        return {
            "message": "No duplicates found. No changes needed.",
            "data": df.to_dict(orient="records"),
        }
    return {"data": df.to_dict(orient="records")}


@mcp.tool(name="handle_missing_values")
def handle_missing_values_tool(data: List[dict], strategy: Dict[str, str]) -> dict:
    """
    Handles missing values according to provided strategy.
    Args:
        data (List[dict]): The data to process.
        strategy (Dict[str, str]): Per-column strategy, e.g., {"age": "drop", "salary": 0, "city": "ffill"}.
    Returns:
        dict: {"data": [...]}
    Note:
        Agent must ask user for strategy if not specified.
    """
    df = pd.DataFrame(data)
    for col, action in strategy.items():
        if action == "drop":
            df = df[df[col].notnull()]
        elif isinstance(action, (int, float, str)):
            df[col] = df[col].fillna(action)
        elif action == "ffill":
            df[col] = df[col].fillna(method="ffill")
        elif action == "bfill":
            df[col] = df[col].fillna(method="bfill")
    return {"data": df.to_dict(orient="records")}


@mcp.tool(name="standardize_values")
def standardize_values_tool(data: List[dict], rules: Dict[str, dict]) -> dict:
    """
    Applies string standardization rules per column (e.g., lowercase, strip).
    Args:
        data (List[dict]): Data to standardize.
        rules (Dict[str, dict]): Per-column rules, e.g., {"name": {"lower": True, "strip": True}}.
    Returns:
        dict: {"data": [...]}
    Note:
        Agent must ask user for rules if not specified.
    """
    df = pd.DataFrame(data)
    for col, rule in rules.items():
        if rule.get("lower"):
            df[col] = df[col].str.lower()
        if rule.get("strip"):
            df[col] = df[col].str.strip()
        if "date_format" in rule:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime(
                rule["date_format"]
            )
    return {"data": df.to_dict(orient="records")}


@mcp.tool(name="enforce_constraints")
def enforce_constraints_tool(data: List[dict], constraints: Dict[str, dict]) -> dict:
    """
    Enforces constraints such as not-null and unique on columns.
    Args:
        data (List[dict]): Data to check.
        constraints (Dict[str, dict]): e.g., {"id": {"unique": True}, "age": {"not_null": True}}.
    Returns:
        dict: {"data": [...]}
    Note:
        Agent must ask user for constraints if not specified.
    """
    df = pd.DataFrame(data)
    for col, rule in constraints.items():
        if rule.get("not_null") and df[col].isnull().any():
            raise ValueError(f"Null values found in '{col}'")
        if rule.get("unique") and df[col].duplicated().any():
            raise ValueError(f"Duplicate values found in unique column '{col}'")
    return {"data": df.to_dict(orient="records")}


@mcp.tool(name="transform_data")
def transform_data_tool(
    data: List[dict], transformation_rules: Dict[str, dict]
) -> dict:
    """
    Applies transformations to the data (e.g., rename columns, add new columns).
    Args:
        data (List[dict]): Data to transform.
        transformation_rules (Dict[str, dict]): {"rename_columns": {...}, "new_columns": {...}}.
    Returns:
        dict: {"data": [...]}
    Note:
        Agent must ask user for transformation_rules if not specified.
    """
    df = pd.DataFrame(data)
    if "rename_columns" in transformation_rules:
        df = df.rename(columns=transformation_rules["rename_columns"])
    if "new_columns" in transformation_rules:
        for col, expr in transformation_rules["new_columns"].items():
            # WARNING: eval can be unsafe if the string comes from user input!
            df[col] = df.eval(expr)
    return {"data": df.to_dict(orient="records")}


if __name__ == "__main__":
    print("Running MCP server on default host/port...", flush=True)
    mcp.run()
