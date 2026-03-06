# Dashboard Financiero PYME

Dashboard financiero para PYMEs con KPIs ejecutivos (ingresos, gastos, utilidad, flujo de caja y variaciones).

## Problema
Las PYMEs suelen tener información financiera dispersa y poco accionable.

## Solución
Un flujo reproducible:
1) Dataset ficticio (ventas, gastos, bancos)
2) Limpieza y transformación (Python/pandas)
3) Modelo de datos
4) Dashboard (Power BI o Streamlit) + KPIs

## Tecnologías
- Python (pandas)
- (Power BI / Streamlit)
- Git + GitHub

## Estructura
- `data/raw`: datos originales
- `data/processed`: datos listos para dashboard
- `src`: scripts de transformación
- `docs`: documentación (modelo y decisiones)
- `assets`: capturas y demo

## Cómo ejecutar (si usas Streamlit)
1) Crear entorno e instalar dependencias:
   - `python -m venv .venv`
   - activar entorno
   - `pip install -r requirements.txt`
2) Ejecutar:
   - `streamlit run src/app.py`

## KPIs
- Margen %
- Flujo Neto (banco)
- Saldo CxC, % CxC vencido, % CxC 30+ / 90+
- Concentración Top 3
- Riesgo Score (0–100) + alerta ejecutiva

## Roadmap
- [ ] Dataset ficticio
- [ ] ETL + modelo de datos
- [ ] Dashboard base
- [ ] Reporte ejecutivo (1 página)
- [ ] Demo (GIF)

## Lecciones aprendidas

-Control de tipos y locales (fechas/decimales) en Power Query
-Diseño de KPIs de riesgo con narrativa ejecutiva
-Modelo en estrella para escalabilidad y performance

## Licencia
MIT

