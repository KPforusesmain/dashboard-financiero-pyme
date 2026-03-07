# Dashboard Financiero PYME

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/pandas-2.0%2B-green)](https://pandas.pydata.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Ready-yellow)](https://powerbi.microsoft.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Optional-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

**Dashboard ejecutivo para PYMEs que transforma datos financieros dispersos en KPIs accionables: ingresos, gastos, utilidad, flujo de caja y alertas de riesgo.**

---

## Tabla de Contenidos
- [El Desafío PYME](#el-desafío-pyme)
- [Nuestra Solución](#nuestra-solución)
- [Tecnologías](#tecnologías)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [KPIs Estratégicos](#kpis-estratégicos)
- [Instalación y Ejecución](#instalación-y-ejecución)
- [Roadmap](#roadmap)
- [Lecciones Aprendidas](#lecciones-aprendidas)
- [Demo](#demo)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

---

## El Desafío PYME

Las pequeñas y medianas empresas enfrentan una realidad común:

| Problema | Impacto |
|----------|---------|
| **Información dispersa** | Datos en Excel, sistema contable, banco y papel |
| **Reportes manuales** | Horas perdidas consolidando información |
| **Datos poco accionables** | Números sin contexto ni alertas tempranas |
| **Riesgos no detectados** | Problemas de liquidez que se ven demasiado tarde |

**Resultado:** Decisiones basadas en intuición, no en datos.

---

## Mi Solución

Un flujo de trabajo completamente reproducible que:

1. **Genera** un dataset ficticio pero realista (ventas, gastos, movimientos bancarios).
2. **Limpia y transforma** los datos con Python y pandas.
3. **Construye un modelo de datos** óptimo para análisis.
4. **Visualiza** en un dashboard interactivo (Power BI o Streamlit) con KPIs ejecutivos.


---

## Tecnologías

| Capa | Tecnología | Propósito |
|------|------------|-----------|
| **Extracción/Transformación** | ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) + ![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-green) | Generación y limpieza de datos |
| **Modelado** | ![Power Query](https://img.shields.io/badge/Power%20Query-M%20Language-purple) | Modelo en estrella y relaciones |
| **Visualización** | ![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow) / ![Streamlit](https://img.shields.io/badge/Streamlit-App-red) | Dashboard interactivo |
| **Control de Versiones** | ![Git](https://img.shields.io/badge/Git-Flow-orange) + ![GitHub](https://img.shields.io/badge/GitHub-Repo-black) | Colaboración y trazabilidad |

---


---

## KPIs Estratégicos

El dashboard está diseñado para responder preguntas clave de negocio:

### Rentabilidad
| KPI | Fórmula | Qué revela |
|-----|---------|------------|
| **Margen Neto %** | `(Ingresos - Gastos) / Ingresos` | Rentabilidad real del negocio |
| **Variación vs Mes Anterior** | `((Mes Actual / Mes Anterior) - 1) * 100` | Tendencia de crecimiento |

### Liquidez
| KPI | Fórmula | Qué revela |
|-----|---------|------------|
| **Flujo Neto de Caja** | `Ingresos Banco - Egresos Banco` | Salud de caja en el período |
| **Saldo CxC (Cuentas por Cobrar)** | `Suma facturas impagas` | Capital inmovilizado |

### Riesgo Crediticio
| KPI | Fórmula | Qué revela |
|-----|---------|------------|
| **% CxC Vencido** | `(Vencido / Total CxC) * 100` | Calidad de la cartera |
| **% CxC 30+ / 90+ días** | `(30+ / Total CxC) * 100` | Severidad del vencimiento |
| **Concentración Top 3 Clientes** | `(Top 3 / Total CxC) * 100` | Dependencia de clientes clave |

### Alerta Ejecutiva
| Métrica | Descripción |
|---------|-------------|
| **Riesgo Score (0-100)** | Score compuesto basado en liquidez, vencimiento y concentración |
| **Alerta Semáforo** | Bajo riesgo / Riesgo moderado /  Riesgo crítico |

---

## Instalación y Ejecución

### Opción 1: Dashboard en Streamlit

```bash
# 1. Clonar repositorio
git clone https://github.com/tuusuario/dashboard-financiero-pyme.git
cd dashboard-financiero-pyme

# 2. Crear y activar entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Generar datos (opcional, ya vienen incluidos)
python src/generador_dataset.py

# 5. Ejecutar ETL
python src/etl_pipeline.py

# 6. Lanzar dashboard
streamlit run src/app.py

```
### Mejoras aplicadas:

1. **Estructura profesional:** Tabla de contenidos, secciones bien definidas
2. **Visual atractivo:** Emojis, badges, tablas comparativas
3. **Contenido enriquecido:** Tablas de KPIs con explicación de negocio
4. **Arquitectura clara:** Estructura de carpetas detallada
5. **Instrucciones precisas:** Comandos listos para copiar/pegar
6. **Lecciones aprendidas:** Valor agregado más allá del código
7. **Doble opción:** Streamlit y Power BI
8. **Formato ejecutivo:** Diseñado para comunicar tanto a técnicos como a dueños de negocio

