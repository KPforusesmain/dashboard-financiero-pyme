from __future__ import annotations

import random
from pathlib import Path
from datetime import date, timedelta

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def _daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def main(seed: int = 42, year: int = 2025) -> None:
    random.seed(seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Master data ----
    clientes = [
        "Alfa Comercial", "Beta Services", "Café Central", "Delta Logistics", "Eco Market",
        "Faro Tech", "Grupo Horizonte", "Hotel Brisa", "Innova Studio", "Jade Imports",
        "Krypton Gym", "Luna Boutique", "Mar Azul", "Norte Constructora", "Órbita Media",
        "Pura Vida Tours", "Quantum Repair", "Río Verde", "Soluciones Tica", "TropiFood"
    ]

    proveedores = [
        "ICE Telecom", "AWS/Cloud", "Google Workspace", "Microsoft 365", "Proveedor Renta",
        "Proveedor Electricidad", "Proveedor Agua", "Papelería Centro", "Ferretería San José",
        "Agencia Marketing", "Contador Externo", "Servicios Limpieza", "Seguros PYME",
        "Proveedor Combustible", "Proveedor Transporte", "Proveedor Hosting", "Banco Comisiones"
    ]

    productos = [
        ("Servicio Mensual", 280, 650),
        ("Soporte Técnico", 120, 420),
        ("Implementación", 600, 1800),
        ("Capacitación", 180, 750),
        ("Proyecto", 900, 4200),
    ]

    cat_gasto = [
        "Alquiler", "Servicios", "Software", "Marketing", "Transporte",
        "Papelería", "Mantenimiento", "Honorarios", "Seguros", "Comisiones Bancarias"
    ]

    metodos_pago = ["Transferencia", "Tarjeta", "SINPE", "Efectivo"]
    moneda = "CRC"

    # ---- Calendar ----
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    # ---- Ventas (realista: estacionalidad + recurrencia) ----
    ventas_rows = []
    invoice_id = 1000

    # Clientes recurrentes (suscripción mensual)
    recurrentes = random.sample(clientes, 8)

    for mes in range(1, 13):
        # estacionalidad: sube en Q2-Q4
        season_multiplier = 1.0 + (0.08 if mes in [4,5,6] else 0.0) + (0.12 if mes in [9,10,11] else 0.0)

        # facturas recurrentes
        for c in recurrentes:
            dia = random.randint(1, 10)
            fecha = date(year, mes, dia)
            prod, lo, hi = random.choice(productos[:2])  # servicio mensual / soporte
            subtotal = round(random.uniform(lo, hi) * season_multiplier, 2)
            impuesto = round(subtotal * 0.13, 2)  # 13% IVA (puedes ajustar)
            total = round(subtotal + impuesto, 2)

            ventas_rows.append({
                "invoice_id": f"F-{invoice_id}",
                "fecha": fecha.isoformat(),
                "cliente": c,
                "producto": prod,
                "categoria": "Ingresos",
                "moneda": moneda,
                "subtotal": subtotal,
                "impuesto": impuesto,
                "monto": total,
                "metodo_pago": random.choice(metodos_pago),
                "estado": "Pagada" if random.random() > 0.12 else "Pendiente"
            })
            invoice_id += 1

        # ventas no recurrentes (proyectos)
        n_proyectos = random.randint(3, 7)
        for _ in range(n_proyectos):
            c = random.choice(clientes)
            dia = random.randint(8, 26)
            fecha = date(year, mes, min(dia, 28))
            prod, lo, hi = random.choice(productos[2:])  # implementacion/capacitacion/proyecto
            subtotal = round(random.uniform(lo, hi) * season_multiplier, 2)
            impuesto = round(subtotal * 0.13, 2)
            total = round(subtotal + impuesto, 2)
            estado = "Pagada" if random.random() > 0.25 else "Pendiente"  # más pendientes en proyectos

            ventas_rows.append({
                "invoice_id": f"F-{invoice_id}",
                "fecha": fecha.isoformat(),
                "cliente": c,
                "producto": prod,
                "categoria": "Ingresos",
                "moneda": moneda,
                "subtotal": subtotal,
                "impuesto": impuesto,
                "monto": total,
                "metodo_pago": random.choice(metodos_pago),
                "estado": estado
            })
            invoice_id += 1

    ventas = pd.DataFrame(ventas_rows).sort_values("fecha")
    ventas.to_csv(RAW_DIR / "ventas.csv", index=False)

    # ---- Gastos (mensuales + variables) ----
    gastos_rows = []
    expense_id = 5000

    gastos_fijos = [
        ("Proveedor Renta", "Alquiler", (420, 780)),
        ("ICE Telecom", "Servicios", (45, 120)),
        ("Proveedor Electricidad", "Servicios", (50, 180)),
        ("Google Workspace", "Software", (20, 60)),
        ("Microsoft 365", "Software", (20, 70)),
        ("Seguros PYME", "Seguros", (35, 120)),
        ("Contador Externo", "Honorarios", (120, 380)),
    ]

    for mes in range(1, 13):
        # fijos
        for prov, cat, (lo, hi) in gastos_fijos:
            dia = random.randint(1, 8)
            fecha = date(year, mes, dia)
            monto = round(random.uniform(lo, hi), 2)
            gastos_rows.append({
                "expense_id": f"G-{expense_id}",
                "fecha": fecha.isoformat(),
                "proveedor": prov,
                "concepto": f"Pago {cat}",
                "categoria": cat,
                "moneda": moneda,
                "monto": monto,
                "metodo_pago": random.choice(["Transferencia", "Tarjeta"]),
            })
            expense_id += 1

        # variables
        n_var = random.randint(10, 22)
        for _ in range(n_var):
            prov = random.choice(proveedores)
            cat = random.choice(cat_gasto)
            dia = random.randint(5, 28)
            fecha = date(year, mes, min(dia, 28))
            base = random.uniform(12, 250)

            # picos por marketing en Q2/Q4
            if cat == "Marketing" and mes in [4,5,6,10,11]:
                base *= random.uniform(1.5, 2.8)

            # comisiones bancarias más frecuentes
            if cat == "Comisiones Bancarias":
                base = random.uniform(3, 35)

            monto = round(base, 2)
            gastos_rows.append({
                "expense_id": f"G-{expense_id}",
                "fecha": fecha.isoformat(),
                "proveedor": prov,
                "concepto": f"Gasto {cat}",
                "categoria": cat,
                "moneda": moneda,
                "monto": monto,
                "metodo_pago": random.choice(metodos_pago),
            })
            expense_id += 1

    gastos = pd.DataFrame(gastos_rows).sort_values("fecha")
    gastos.to_csv(RAW_DIR / "gastos.csv", index=False)

    # ---- Banco (movimientos: refleja pagos y cobros; incluye comisiones) ----
    banco_rows = []
    move_id = 9000

    # Cobros: tomar ventas pagadas y generar depósitos (con fecha +/- 0-5 días)
    ventas_pagadas = ventas[ventas["estado"] == "Pagada"].copy()
    for _, r in ventas_pagadas.iterrows():
        f = pd.to_datetime(r["fecha"]).date()
        f2 = f + timedelta(days=random.randint(0, 5))
        banco_rows.append({
            "move_id": f"B-{move_id}",
            "fecha": f2.isoformat(),
            "descripcion": f"Depósito {r['cliente']} ({r['invoice_id']})",
            "tipo": "Ingreso",
            "moneda": r["moneda"],
            "monto": float(r["monto"]),
        })
        move_id += 1

        # comisión por tarjeta ocasional
        if r["metodo_pago"] == "Tarjeta" and random.random() > 0.35:
            fee = round(float(r["monto"]) * random.uniform(0.012, 0.028), 2)
            banco_rows.append({
                "move_id": f"B-{move_id}",
                "fecha": f2.isoformat(),
                "descripcion": f"Comisión tarjeta {r['invoice_id']}",
                "tipo": "Gasto",
                "moneda": r["moneda"],
                "monto": -fee,
            })
            move_id += 1

    # Pagos: reflejar gastos con fecha +/- 0-4 días
    for _, r in gastos.iterrows():
        f = pd.to_datetime(r["fecha"]).date()
        f2 = f + timedelta(days=random.randint(0, 4))
        banco_rows.append({
            "move_id": f"B-{move_id}",
            "fecha": f2.isoformat(),
            "descripcion": f"Pago {r['proveedor']} ({r['expense_id']})",
            "tipo": "Gasto",
            "moneda": r["moneda"],
            "monto": -float(r["monto"]),
        })
        move_id += 1

    # Comisiones bancarias mensuales extra
    for mes in range(1, 13):
        f = date(year, mes, random.randint(25, 28))
        fee = round(random.uniform(6, 28), 2)
        banco_rows.append({
            "move_id": f"B-{move_id}",
            "fecha": f.isoformat(),
            "descripcion": "Comisión bancaria mensual",
            "tipo": "Gasto",
            "moneda": moneda,
            "monto": -fee,
        })
        move_id += 1

    banco = pd.DataFrame(banco_rows)
    banco["fecha"] = pd.to_datetime(banco["fecha"])
    banco = banco.sort_values("fecha")
    banco["fecha"] = banco["fecha"].dt.strftime("%Y-%m-%d")
    banco.to_csv(RAW_DIR / "banco.csv", index=False)

    print("Dataset generado en data/raw/")
    print(" - ventas.csv:", len(ventas))
    print(" - gastos.csv:", len(gastos))
    print(" - banco.csv:", len(banco))


if __name__ == "__main__":
    main()