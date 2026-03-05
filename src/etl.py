from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUT_DIR = PROJECT_ROOT / "data" / "processed"


def _read_csv(name: str) -> pd.DataFrame:
    p = RAW_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Missing input file: {p}")
    return pd.read_csv(p)


def _to_date(df: pd.DataFrame, col: str = "fecha", drop_bad: bool = False) -> pd.DataFrame:
    if col not in df.columns:
        raise KeyError(f"Missing required date column: {col}")

    # limpiar strings
    df[col] = df[col].astype(str).str.strip()

    # convertir
    parsed = pd.to_datetime(df[col], errors="coerce")
    bad_mask = parsed.isna()

    if bad_mask.any():
        bad = df.loc[bad_mask, [c for c in df.columns if c in ["invoice_id", "fecha_emision", col, "cliente"]]].head(15)
        msg = f"Invalid dates found in column '{col}'. Examples:\n{bad}"

        if drop_bad:
            df = df.loc[~bad_mask].copy()
            df[col] = pd.to_datetime(df[col], errors="coerce")
            return df
        raise ValueError(msg)

    df[col] = parsed
    return df

def build_dim_fecha(min_date: pd.Timestamp, max_date: pd.Timestamp) -> pd.DataFrame:
    d = pd.date_range(min_date, max_date, freq="D")
    dim = pd.DataFrame({"fecha": d})
    dim["anio"] = dim["fecha"].dt.year
    dim["mes_num"] = dim["fecha"].dt.month
    dim["mes"] = dim["fecha"].dt.strftime("%b")
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
    cxc = _to_date(_read_csv("cxc.csv"), col="fecha_emision")
    cxc = _to_date(cxc, col="fecha_vencimiento", drop_bad=True)

    # Numeric conversions
    for col in ["monto_factura", "pagado", "saldo"]:
        cxc[col] = pd.to_numeric(cxc[col], errors="coerce")

    if cxc[["monto_factura", "pagado", "saldo"]].isna().any().any():
        raise ValueError("Found non-numeric values in cxc monto_factura/pagado/saldo.")

    
    if ventas[["monto"]].isna().any().any() or gastos["monto"].isna().any() or banco["monto"].isna().any():
        raise ValueError("Found non-numeric values in monto/subtotal/impuesto.")

    # FACT: movimientos (modelo en estrella)
    fact_ventas = pd.DataFrame({
        "fecha": ventas["fecha"],
        "tipo": "Ingreso",
        "origen": "Ventas",
        "documento": ventas.get("invoice_id", "").astype(str),
        "entidad": ventas.get("cliente", "").astype(str),
        "categoria": ventas.get("categoria", "Ingresos").astype(str),
        "detalle": ventas.get("producto", "").astype(str),
        "estado": ventas.get("estado", "Pagada").astype(str),
        "moneda": ventas.get("moneda", "CRC").astype(str),
        "subtotal": ventas.get("subtotal", ventas["monto"]).astype(float),
        "impuesto": ventas.get("impuesto", 0.0).astype(float),
        "monto": ventas["monto"].abs().astype(float),
        "metodo_pago": ventas.get("metodo_pago", "").astype(str),
    })

    fact_gastos = pd.DataFrame({
        "fecha": gastos["fecha"],
        "tipo": "Gasto",
        "origen": "Gastos",
        "documento": gastos.get("expense_id", "").astype(str),
        "entidad": gastos.get("proveedor", "").astype(str),
        "categoria": gastos.get("categoria", "Gastos").astype(str),
        "detalle": gastos.get("concepto", "").astype(str),
        "estado": "Pagado",
        "moneda": gastos.get("moneda", "CRC").astype(str),
        "subtotal": gastos["monto"].abs().astype(float),
        "impuesto": 0.0,
        "monto": gastos["monto"].abs().astype(float),
        "metodo_pago": gastos.get("metodo_pago", "").astype(str),
    })

    fact_mov = pd.concat([fact_ventas, fact_gastos], ignore_index=True)

    # Clean strings
    for c in ["documento", "entidad", "categoria", "detalle", "estado", "moneda", "metodo_pago"]:
        fact_mov[c] = fact_mov[c].astype(str).str.strip()

    # Dimensions
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

    # ---- Aging buckets (as_of = última fecha disponible) ----
    as_of = max(
        fact_mov["fecha"].max(),
        banco["fecha"].max(),
        cxc["fecha_emision"].max(),
        cxc["fecha_vencimiento"].max(),
    )
    as_of = pd.to_datetime(as_of)

    cxc2 = cxc.copy()
    cxc2["as_of"] = as_of

    cxc2["dias_vencidos"] = (cxc2["as_of"] - cxc2["fecha_vencimiento"]).dt.days
    cxc2["dias_vencidos"] = cxc2["dias_vencidos"].fillna(0).astype(int)

    def bucket(d: int) -> str:
        if d <= 0:
            return "No vencido"
        if 1 <= d <= 30:
            return "1-30"
        if 31 <= d <= 60:
            return "31-60"
        if 61 <= d <= 90:
            return "61-90"
        return "90+"

    cxc2["bucket"] = cxc2["dias_vencidos"].apply(bucket)

    cxc2["entidad"] = cxc2["cliente"].astype(str).str.strip()
    cxc2 = cxc2.merge(dim_entidad[["entidad", "entidad_id"]], on="entidad", how="left")

    cxc_out = cxc2[[
        "invoice_id",
        "fecha_emision",
        "fecha_vencimiento",
        "cliente",
        "moneda",
        "monto_factura",
        "pagado",
        "saldo",
        "estado",
        "as_of",
        "dias_vencidos",
        "bucket",
        "entidad_id",
    ]].copy()
    
    # Add IDs to fact
    fact_mov = fact_mov.merge(dim_categoria, on=["tipo", "categoria"], how="left")
    fact_mov = fact_mov.merge(dim_entidad, on=["entidad"], how="left")

    # Banco output (separado para flujo real vs contable)
    banco_out = banco.copy()
    banco_out["descripcion"] = banco_out["descripcion"].astype(str).str.strip()
    banco_out["tipo"] = banco_out["tipo"].astype(str).str.strip()
    banco_out["moneda"] = banco_out.get("moneda", "CRC").astype(str).str.strip()

    # Monthly summary (validación + KPI rápido)
    resumen = (
        fact_mov.assign(anio_mes=fact_mov["fecha"].dt.strftime("%Y-%m"))
        .groupby(["anio_mes", "tipo"], as_index=False)["monto"].sum()
        .pivot(index="anio_mes", columns="tipo", values="monto")
        .fillna(0.0)
        .reset_index()
    )
    resumen["utilidad"] = resumen.get("Ingreso", 0.0) - resumen.get("Gasto", 0.0)

    # Write outputs
    fact_mov.to_csv(OUT_DIR / "fact_movimientos.csv", index=False)
    dim_fecha.to_csv(OUT_DIR / "dim_fecha.csv", index=False)
    dim_categoria.to_csv(OUT_DIR / "dim_categoria.csv", index=False)
    dim_entidad.to_csv(OUT_DIR / "dim_entidad.csv", index=False)
    banco_out.to_csv(OUT_DIR / "banco_movimientos.csv", index=False)
    resumen.to_csv(OUT_DIR / "resumen_mensual.csv", index=False)
    cxc_out.to_csv(OUT_DIR / "cxc_aging.csv", index=False)

    print("ETL complete. Files written to:", OUT_DIR)
    for f in [
        "fact_movimientos.csv",
        "dim_fecha.csv",
        "dim_categoria.csv",
        "dim_entidad.csv",
        "banco_movimientos.csv",
        "resumen_mensual.csv",
        "cxc_aging.csv",
    ]:
        print(" -", f)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print("ETL failed:", e, file=sys.stderr)
        raise