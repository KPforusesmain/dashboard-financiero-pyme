from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUT_DIR = PROJECT_ROOT / "data" / "processed"


def _read_csv(name: str) -> pd.DataFrame:
    path = RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    return pd.read_csv(path)


def _to_date(df: pd.DataFrame, col: str = "fecha") -> pd.DataFrame:
    df[col] = pd.to_datetime(df[col], errors="coerce")
    bad = df[df[col].isna()]
    if not bad.empty:
        raise ValueError(f"Invalid dates found in column '{col}':\n{bad.head(10)}")
    return df


def build_dim_fecha(min_date: pd.Timestamp, max_date: pd.Timestamp) -> pd.DataFrame:
    d = pd.date_range(min_date, max_date, freq="D")
    dim = pd.DataFrame({"fecha": d})
    dim["anio"] = dim["fecha"].dt.year
    dim["mes_num"] = dim["fecha"].dt.month
    dim["mes"] = dim["fecha"].dt.strftime("%b")  # Jan, Feb...
    dim["trimestre"] = dim["fecha"].dt.quarter
    dim["dia"] = dim["fecha"].dt.day
    dim["dia_semana"] = dim["fecha"].dt.strftime("%a")
    dim["anio_mes"] = dim["fecha"].dt.strftime("%Y-%m")
    return dim


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ventas = _to_date(_read_csv("ventas.csv"))
    gastos = _to_date(_read_csv("gastos.csv"))
    banco = _to_date(_read_csv("banco.csv"))

    # Normalizar montos (ventas y gastos como positivos)
    ventas["monto"] = pd.to_numeric(ventas["monto"], errors="coerce")
    gastos["monto"] = pd.to_numeric(gastos["monto"], errors="coerce")
    banco["monto"] = pd.to_numeric(banco["monto"], errors="coerce")

    if ventas["monto"].isna().any() or gastos["monto"].isna().any() or banco["monto"].isna().any():
        raise ValueError("Found non-numeric 'monto' values in inputs.")

    # Hechos: movimientos unificados
    # ventas -> tipo=Ingreso
    fact_ventas = pd.DataFrame({
        "fecha": ventas["fecha"],
        "tipo": "Ingreso",
        "origen": "Ventas",
        "entidad": ventas["cliente"].astype(str),
        "categoria": ventas["categoria"].astype(str),
        "detalle": ventas["producto"].astype(str),
        "monto": ventas["monto"].abs()
    })

    # gastos -> tipo=Gasto
    fact_gastos = pd.DataFrame({
        "fecha": gastos["fecha"],
        "tipo": "Gasto",
        "origen": "Gastos",
        "entidad": gastos["proveedor"].astype(str),
        "categoria": gastos["categoria"].astype(str),
        "detalle": gastos["concepto"].astype(str),
        "monto": gastos["monto"].abs()
    })

    fact_mov = pd.concat([fact_ventas, fact_gastos], ignore_index=True)

    # Normalización ligera (trim)
    for c in ["entidad", "categoria", "detalle"]:
        fact_mov[c] = fact_mov[c].str.strip()

    # Dimensiones
    min_date = min(fact_mov["fecha"].min(), banco["fecha"].min())
    max_date = max(fact_mov["fecha"].max(), banco["fecha"].max())

    dim_fecha = build_dim_fecha(min_date, max_date)

    dim_categoria = (
        fact_mov[["tipo", "categoria"]]
        .drop_duplicates()
        .sort_values(["tipo", "categoria"])
        .reset_index(drop=True)
    )
    dim_categoria["categoria_id"] = range(1, len(dim_categoria) + 1)

    dim_entidad = (
        fact_mov[["entidad"]]
        .drop_duplicates()
        .sort_values("entidad")
        .reset_index(drop=True)
    )
    dim_entidad["entidad_id"] = range(1, len(dim_entidad) + 1)

    # Agregar IDs a hechos (para modelo en estrella en Power BI)
    fact_mov = fact_mov.merge(dim_categoria, on=["tipo", "categoria"], how="left")
    fact_mov = fact_mov.merge(dim_entidad, on=["entidad"], how="left")

    # Banco: dejarlo aparte para conciliación / flujo real
    banco_out = banco.copy()
    banco_out["descripcion"] = banco_out["descripcion"].astype(str).str.strip()
    banco_out["tipo"] = banco_out["tipo"].astype(str).str.strip()

    # Exportar para Power BI
    fact_mov.to_csv(OUT_DIR / "fact_movimientos.csv", index=False)
    dim_fecha.to_csv(OUT_DIR / "dim_fecha.csv", index=False)
    dim_categoria.to_csv(OUT_DIR / "dim_categoria.csv", index=False)
    dim_entidad.to_csv(OUT_DIR / "dim_entidad.csv", index=False)
    banco_out.to_csv(OUT_DIR / "banco_movimientos.csv", index=False)

    # Resumen mensual (útil para validar y para dashboard)
    resumen = (
        fact_mov.assign(anio_mes=fact_mov["fecha"].dt.strftime("%Y-%m"))
        .groupby(["anio_mes", "tipo"], as_index=False)["monto"].sum()
        .pivot(index="anio_mes", columns="tipo", values="monto")
        .fillna(0.0)
        .reset_index()
    )
    resumen["utilidad"] = resumen.get("Ingreso", 0.0) - resumen.get("Gasto", 0.0)
    resumen.to_csv(OUT_DIR / "resumen_mensual.csv", index=False)

    print("✅ ETL complete. Files written to:", OUT_DIR)
    for f in ["fact_movimientos.csv", "dim_fecha.csv", "dim_categoria.csv", "dim_entidad.csv", "banco_movimientos.csv", "resumen_mensual.csv"]:
        print(" -", f)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print("❌ ETL failed:", e, file=sys.stderr)
        raise