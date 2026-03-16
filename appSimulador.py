# app.py — Master Engineering Hub · Simulador de Manufactura
# Desarrollado por Master Engineer Erik Armenta
#
# =============================================================================
# DOCUMENTACIÓN ARQUITECTÓNICA — ANÁLISIS PROFUNDO
# =============================================================================
#
# DESCRIPCIÓN GENERAL:
# -------------------
# Aplicación web de simulación de manufactura construida con Streamlit que
# integra un motor de simulación de eventos discretos (SimPy) con visualizaciones
# interactivas (Plotly/Altair) para análisis de líneas de producción.
#
# ARQUITECTURA DEL SISTEMA:
# -------------------------
# ┌─────────────────────────────────────────────────────────────────────────┐
# │                        FRONTEND (Streamlit)                             │
# │  ┌─────────────┬─────────────┬─────────────┬─────────────┬───────────┐  │
# │  │ Módulo 1    │ Módulo 2    │ Módulo 3    │ Módulo 4    │ Módulo 5  │  │
# │  │ Configuración│ Balanceo   │ Ejecución   │ Dashboard   │ Confiab.  │  │
# │  │ (Setup)     │ (Line Bal.) │ (SimPy)     │ (KPIs)      │ (MTBF)    │  │
# │  └──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴─────┬─────┘  │
# │         │             │             │             │            │        │
# │  ┌──────▼─────────────▼─────────────▼─────────────▼────────────▼─────┐  │
# │  │                    st.session_state (Persistencia)                │  │
# │  │   config: {piezas, takt, kanban, mtbf, mttr, estaciones}         │  │
# │  │   results: {kpis, df_prod, df_fail, df_wip, bottleneck_df}       │  │
# │  └───────────────────────────────────────────────────────────────────┘  │
# └─────────────────────────────────────────────────────────────────────────┘
#                                     │
#                                     ▼
# ┌─────────────────────────────────────────────────────────────────────────┐
# │                        BACKEND (Motor SimPy)                            │
# │  ┌─────────────────────────────────────────────────────────────────┐   │
# │  │  simulator.py: run_simulation(config)                           │   │
# │  │    - Clase Workstation: ciclo, variabilidad, MTBF/MTTR         │   │
# │  │    - Control Kanban via simpy.Resource                          │   │
# │  │    - Generación de eventos: producción, fallas, reparaciones    │   │
# │  └─────────────────────────────────────────────────────────────────┘   │
# │  ┌─────────────────────────────────────────────────────────────────┐   │
# │  │  line_balancer.py: Algoritmos de balanceo                       │   │
# │  │    - LCR (Largest Candidate Rule)                               │   │
# │  │    - RPW (Ranked Positional Weight)                             │   │
# │  │    - Optimización de operadores                                 │   │
# │  └─────────────────────────────────────────────────────────────────┘   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ESTRUCTURA DE MÓDULOS (856 líneas):
# -----------------------------------
# Líneas 001-016: Imports (streamlit, pandas, numpy, plotly, altair, simpy)
# Líneas 018-024: Configuración de página Streamlit (layout wide, sidebar)
# Líneas 026-083: CSS profesional (variables CSS, KPI cards, tema oscuro)
# Líneas 085-098: Session state (config, results para persistencia)
# Líneas 099-122: Helpers (PALETTE colores, PT template Plotly, kpi(), sec())
# Líneas 123-176: Sidebar (logo, menú módulos, resumen última corrida)
#
# MÓDULO 1 — CONFIGURACIÓN DE PLANTA (líneas 178-249):
#   - Parámetros generales: piezas, takt time, capacidad kanban
#   - Confiabilidad: MTBF (tiempo entre fallas), MTTR (tiempo reparación)
#   - Estaciones de trabajo: ciclo, variabilidad σ, ratio ciclo/takt
#   - CRUD de estaciones (agregar/eliminar dinámicamente)
#
# MÓDULO 2 — EJECUCIÓN Y ANÁLISIS (líneas 251-387):
#   - Invoca run_simulation(config) del motor SimPy
#   - KPI cards: unidades, throughput, OEE, disponibilidad, ciclo, fallas
#   - Gráficas: cuellos de botella, utilización, histograma esperas
#   - Diagrama Gantt de producción (primeras 50 piezas)
#   - Trazabilidad producción vs paros
#
# MÓDULO 3 — DASHBOARD KPIs (líneas 389-494):
#   - Gauge OEE con breakdown: Disponibilidad × Rendimiento × Calidad
#   - Box plot distribución ciclos vs takt time
#   - WIP acumulado por estación (línea temporal)
#   - Throughput instantáneo y producción acumulada
#
# MÓDULO 4 — CONFIABILIDAD (líneas 497-549):
#   - Análisis de eventos de paro (fallas)
#   - Downtime total por estación
#   - Distribución duración de fallas (histograma)
#   - Timeline eventos de paro
#
# MÓDULO 5 — REPORTE (líneas 552-585):
#   - Resumen ejecutivo de la simulación
#   - Estadísticas por estación
#   - Identificación de cuellos de botella
#   - Export CSV (datos completos, KPIs)
#
# MÓDULO 6 — BALANCEO DE LÍNEAS (líneas 588-856):
#   - Definición de tareas con precedencias
#   - Algoritmos: LCR (Largest Candidate Rule), RPW (Ranked Positional Weight)
#   - Métricas: eficiencia η, índice suavidad, % idle
#   - Optimización de operadores (headcount)
#   - Diagrama de precedencias interactivo
#   - Aplicar balanceo a simulación
#
# FLUJO DE DATOS:
# ---------------
# 1. Usuario configura parámetros en Módulo 1 → st.session_state.config
# 2. Usuario ejecuta simulación en Módulo 2 → run_simulation(config)
# 3. Resultados se almacenan en st.session_state.results
# 4. Módulos 3-5 leen results para visualizaciones
# 5. Módulo 6 puede recalcular estaciones y aplicar a config
#
# PATRONES DE DISEÑO:
# -------------------
# - State Management: session_state para persistencia entre reruns
# - Component Pattern: funciones helper kpi(), sec() para UI consistente
# - Template Pattern: PT dict para estilos Plotly uniformes
# - Module Pattern: separación clara de responsabilidades por módulo
#
# DEPENDENCIAS:
# -------------
# - streamlit: Framework web para interfaces de datos
# - pandas/numpy: Manipulación de datos y cálculos
# - plotly: Visualizaciones interactivas (barras, gauges, scatter, timeline)
# - altair: Visualizaciones declarativas (histogramas)
# - simpy: Motor de simulación de eventos discretos (via simulator.py)
#
# KPIs CALCULADOS:
# ----------------
# - OEE = Disponibilidad × Rendimiento × Calidad
# - Disponibilidad = MTBF / (MTBF + MTTR)
# - Throughput = Unidades / Tiempo (unidades/hora)
# - Utilización = Tiempo activo / Tiempo total por estación
# - Eficiencia balanceo η = Σ tiempos tarea / (N estaciones × Takt)
#
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import os
import json
from datetime import datetime
from TestSimuladorFOXIA import run_simulation
from line_balancer import (
    largest_candidate_rule, ranked_positional_weight,
    balance_metrics, stations_to_config, build_precedence_positions,
    compute_positional_weights, assign_operators, operator_balance_chart_data,
)

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MEH · Simulador de Manufactura",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-card:    #111827;
    --border:     #1e3a5f;
    --accent:     #00d4ff;
    --accent2:    #ff6b35;
    --accent3:    #00ff9f;
    --warn:       #ffb800;
    --danger:     #ff3b5c;
    --text:       #e8edf5;
    --muted:      #6b7fa3;
}

.stApp { background: var(--bg-primary); }
section[data-testid="stSidebar"] { background: #080c17 !important; border-right: 1px solid var(--border); }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--text); }
h1,h2,h3 { font-family: 'Rajdhani', sans-serif; letter-spacing: .03em; }

/* KPI CARDS */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 12px; margin-bottom: 24px; }
.kpi-card {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
    padding: 16px 18px; position: relative; overflow: hidden; transition: transform .2s, box-shadow .2s;
}
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background: var(--kpi-color, var(--accent)); }
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 28px #00d4ff15; }
.kpi-label { font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin-bottom:6px; font-weight:600; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:30px; font-weight:700; line-height:1; }
.kpi-sub   { font-size:11px; color:var(--muted); margin-top:5px; }

/* PARAM CARDS */
.param-card { background:var(--bg-card); border:1px solid var(--border); border-radius:14px; padding:20px 22px; margin-bottom:16px; }
.param-title { font-family:'Rajdhani',sans-serif; font-size:13px; font-weight:700; letter-spacing:.1em;
               text-transform:uppercase; color:var(--accent); margin-bottom:14px; }

/* SECTION HEADER */
.sec-hdr { font-family:'Rajdhani',sans-serif; font-size:20px; font-weight:700; letter-spacing:.05em;
           border-bottom:1px solid var(--border); padding-bottom:8px; margin-bottom:18px; display:flex; align-items:center; gap:8px; }
.sec-tag { font-size:10px; background:#00d4ff18; color:var(--accent); padding:2px 9px;
           border-radius:20px; border:1px solid #00d4ff33; }

/* DEV FOOTER */
.dev-footer { text-align:center; padding:16px; margin-top:32px; border-top:1px solid var(--border);
              font-size:11px; color:var(--muted); letter-spacing:.08em; }
.dev-footer strong { color:var(--accent); font-family:'Rajdhani',sans-serif; font-size:13px; }

/* Streamlit overrides */
div[data-testid="stNumberInput"] label,
div[data-testid="stSlider"] label { font-size:12px !important; color:var(--muted) !important; }
div[data-testid="metric-container"] { display:none; }
div[data-testid="stButton"] > button { font-family:'Rajdhani',sans-serif !important; font-weight:700 !important; letter-spacing:.08em !important; border-radius:8px !important; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if 'config' not in st.session_state:
    st.session_state.config = {
        'piezas': 50, 'takt': 50, 'kanban': 5,
        'mtbf': 800,  'mttr': 100, 'idle_factor': 5, 'defect_rate': 2,
        'estaciones': {
            'Ensamble':   {'ciclo': 40, 'var': 2},
            'Soldadura':  {'ciclo': 60, 'var': 5},
            'Inspección': {'ciclo': 30, 'var': 1},
        }
    }
if 'results' not in st.session_state:
    st.session_state.results = None
if 'previous_results' not in st.session_state:
    st.session_state.previous_results = None

# ─── HELPERS ─────────────────────────────────────────────────────────────────
PALETTE = ['#00d4ff','#ff6b35','#00ff9f','#ffb800','#9b59b6','#e74c3c','#1abc9c']

PT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.6)',
    font=dict(family='Inter', color='#6b7fa3', size=11),
    xaxis=dict(gridcolor='#1e3a5f', linecolor='#1e3a5f', tickfont=dict(color='#6b7fa3')),
    yaxis=dict(gridcolor='#1e3a5f', linecolor='#1e3a5f', tickfont=dict(color='#6b7fa3')),
    title_font=dict(family='Rajdhani', color='#e8edf5', size=15),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#6b7fa3')),
    margin=dict(l=40, r=20, t=48, b=36),
)

def kpi(label, value, sub="", color="#00d4ff"):
    return (f'<div class="kpi-card" style="--kpi-color:{color}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="color:{color}">{value}</div>'
            + (f'<div class="kpi-sub">{sub}</div>' if sub else '') +
            '</div>')

def sec(icon, title, tag=""):
    t = f'<span class="sec-tag">{tag}</span>' if tag else ''
    return f'<div class="sec-hdr">{icon} {title} {t}</div>'

def calc_delta(current, previous, higher_is_better=True):
    """Calcula delta porcentual entre valores actual y anterior."""
    if previous == 0:
        return None, None
    delta = ((current - previous) / previous) * 100
    is_positive = (delta > 0 and higher_is_better) or (delta < 0 and not higher_is_better)
    return round(delta, 1), is_positive

def comparison_row(label, current, previous, unit="", higher_is_better=True):
    """Genera HTML para una fila de comparación de KPIs."""
    delta, is_positive = calc_delta(current, previous, higher_is_better)
    if delta is None:
        delta_html = '<span style="color:#6b7fa3">N/A</span>'
    else:
        color = "#00ff9f" if is_positive else "#ff3b5c"
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        delta_html = f'<span style="color:{color}">{arrow} {abs(delta)}%</span>'
    return f'''
    <tr>
        <td style="padding:8px 12px;color:#e8edf5;font-weight:500">{label}</td>
        <td style="padding:8px 12px;text-align:center;color:#6b7fa3">{previous}{unit}</td>
        <td style="padding:8px 12px;text-align:center;color:#00d4ff;font-weight:600">{current}{unit}</td>
        <td style="padding:8px 12px;text-align:center">{delta_html}</td>
    </tr>'''

# ─── CONFIG VALIDATION ───────────────────────────────────────────────────────
def validate_config(config: dict) -> dict:
    """
    Valida la configuración de simulación y retorna warnings/errores.

    Returns:
        dict con claves:
            - 'valid': bool - True si la configuración es ejecutable
            - 'errors': list[str] - Errores críticos que impiden ejecución
            - 'warnings': list[str] - Advertencias sobre valores subóptimos
            - 'info': list[str] - Información adicional sobre la configuración
    """
    errors = []
    warnings = []
    info = []

    # ─── RANGOS VÁLIDOS (hard limits) ────────────────────────────────────────
    RANGES = {
        'piezas':      (1, 10000, "Piezas a simular"),
        'takt':        (1, 1000, "Takt Time (s)"),
        'kanban':      (1, 200, "Capacidad Kanban"),
        'mtbf':        (50, 10000, "MTBF (s)"),
        'mttr':        (5, 2000, "MTTR (s)"),
        'idle_factor': (0, 50, "Factor de Tiempo Muerto (%)"),
        'defect_rate': (0, 50, "Tasa de Defectos (%)"),
    }

    # ─── RANGOS ÓPTIMOS (soft limits para warnings) ──────────────────────────
    OPTIMAL = {
        'piezas':      (10, 2000, "Valores muy bajos no son estadísticamente significativos; muy altos pueden ser lentos"),
        'takt':        (20, 300, "Takt muy bajo puede ser irreal; muy alto reduce productividad"),
        'kanban':      (2, 50, "Kanban=1 causa bloqueos; valores muy altos ocultan problemas de flujo"),
        'mtbf':        (200, 3000, "MTBF muy bajo indica equipo en mal estado; muy alto puede ser optimista"),
        'mttr':        (15, 500, "MTTR muy bajo puede ser irreal; muy alto indica problemas de mantenimiento"),
        'idle_factor': (0, 15, "Idle >15% indica problemas serios de organización"),
        'defect_rate': (0, 10, "Scrap >10% indica problemas graves de calidad"),
    }

    # ─── VALIDAR EXISTENCIA DE CAMPOS REQUERIDOS ─────────────────────────────
    required_fields = ['piezas', 'takt', 'kanban', 'mtbf', 'mttr', 'estaciones']
    for field in required_fields:
        if field not in config:
            errors.append(f"Campo requerido '{field}' no encontrado en configuración")

    if errors:
        return {'valid': False, 'errors': errors, 'warnings': warnings, 'info': info}

    # ─── VALIDAR RANGOS DUROS ────────────────────────────────────────────────
    for param, (min_val, max_val, label) in RANGES.items():
        if param in config:
            val = config.get(param, 0)
            if not isinstance(val, (int, float)):
                errors.append(f"{label}: valor '{val}' no es numérico")
            elif val < min_val:
                errors.append(f"{label}: {val} está por debajo del mínimo permitido ({min_val})")
            elif val > max_val:
                errors.append(f"{label}: {val} excede el máximo permitido ({max_val})")

    # ─── VALIDAR ESTACIONES ──────────────────────────────────────────────────
    estaciones = config.get('estaciones', {})
    if not estaciones:
        errors.append("Se requiere al menos una estación de trabajo")
    else:
        for name, params in estaciones.items():
            if not isinstance(params, dict):
                errors.append(f"Estación '{name}': configuración inválida")
                continue

            ciclo = params.get('ciclo', 0)
            var = params.get('var', 0)

            if not isinstance(ciclo, (int, float)) or ciclo < 1:
                errors.append(f"Estación '{name}': ciclo debe ser >= 1 segundo")
            elif ciclo > 600:
                errors.append(f"Estación '{name}': ciclo {ciclo}s excede máximo (600s)")

            if not isinstance(var, (int, float)) or var < 0:
                errors.append(f"Estación '{name}': variabilidad no puede ser negativa")
            elif var > ciclo * 0.5:
                warnings.append(f"Estación '{name}': variabilidad ({var}s) es >50% del ciclo, puede causar inestabilidad")

    # Si hay errores críticos, no continuar con validaciones de optimización
    if errors:
        return {'valid': False, 'errors': errors, 'warnings': warnings, 'info': info}

    # ─── VALIDAR RANGOS ÓPTIMOS (warnings) ───────────────────────────────────
    for param, (opt_min, opt_max, reason) in OPTIMAL.items():
        if param in config:
            val = config.get(param, 0)
            if val < opt_min:
                warnings.append(f"{param}={val} por debajo del óptimo ({opt_min}): {reason}")
            elif val > opt_max:
                warnings.append(f"{param}={val} por encima del óptimo ({opt_max}): {reason}")

    # ─── VALIDACIONES DE RELACIÓN ENTRE PARÁMETROS ───────────────────────────
    takt = config['takt']
    mtbf = config['mtbf']
    mttr = config['mttr']

    # Disponibilidad teórica
    disponibilidad = (mtbf / (mtbf + mttr)) * 100
    if disponibilidad < 70:
        warnings.append(f"Disponibilidad teórica {disponibilidad:.1f}% < 70% (MTBF/MTTR ratio bajo)")
    elif disponibilidad < 85:
        info.append(f"Disponibilidad teórica {disponibilidad:.1f}% - considere mejorar MTBF o reducir MTTR")

    # Ratio MTBF/MTTR
    ratio = mtbf / max(1, mttr)
    if ratio < 4:
        warnings.append(f"Ratio MTBF/MTTR = {ratio:.1f} es crítico (recomendado > 8)")
    elif ratio < 8:
        info.append(f"Ratio MTBF/MTTR = {ratio:.1f} es aceptable pero mejorable")

    # Ciclos vs Takt (cuellos de botella)
    for name, params in estaciones.items():
        ciclo = params.get('ciclo', 0)
        if ciclo > takt * 1.2:
            warnings.append(f"Estación '{name}': ciclo ({ciclo}s) > 120% del Takt ({takt}s) - cuello de botella")
        elif ciclo > takt:
            info.append(f"Estación '{name}': ciclo ({ciclo}s) ligeramente > Takt ({takt}s)")

    # Factor de pérdida combinado
    idle_factor = config.get('idle_factor', 0)
    defect_rate = config.get('defect_rate', 0)
    perdida_total = idle_factor + defect_rate
    if perdida_total > 20:
        warnings.append(f"Pérdida combinada (idle + scrap) = {perdida_total}% - revisar procesos")

    # OEE teórico estimado
    rendimiento_est = min(100, (takt / max(1, max(p['ciclo'] for p in estaciones.values()))) * 100)
    calidad_est = 100 - defect_rate
    oee_teorico = (disponibilidad / 100) * (rendimiento_est / 100) * (calidad_est / 100) * 100
    if oee_teorico < 50:
        warnings.append(f"OEE teórico estimado {oee_teorico:.1f}% < 50% - revisar configuración")
    elif oee_teorico < 65:
        info.append(f"OEE teórico estimado {oee_teorico:.1f}% - hay oportunidad de mejora")

    # Tiempo de simulación estimado
    tiempo_sim_est = config['piezas'] * max(p['ciclo'] for p in estaciones.values())
    if tiempo_sim_est > 50000:
        info.append(f"Simulación larga estimada (~{tiempo_sim_est/60:.0f} min simulados)")

    return {
        'valid': True,
        'errors': errors,
        'warnings': warnings,
        'info': info,
        'metrics': {
            'disponibilidad_teorica': round(disponibilidad, 1),
            'oee_teorico': round(oee_teorico, 1),
            'ratio_mtbf_mttr': round(ratio, 2),
        }
    }

def show_validation_results(validation: dict):
    """Muestra los resultados de validación en la UI de Streamlit."""
    if validation['errors']:
        for err in validation['errors']:
            st.error(f"❌ {err}")

    if validation['warnings']:
        for warn in validation['warnings']:
            st.warning(f"⚠️ {warn}")

    if validation.get('info'):
        with st.expander("ℹ️ Información adicional", expanded=False):
            for inf in validation['info']:
                st.info(inf)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = "EA_2.png"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:18px 0 8px">
            <div style="font-family:'Rajdhani',sans-serif;font-size:38px;font-weight:700;color:#00d4ff">EA</div>
            <div style="font-size:9px;letter-spacing:.2em;color:#6b7fa3;margin-top:2px">MASTER ENGINEER</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:18px">
        <div style="font-family:'Rajdhani',sans-serif;font-size:16px;font-weight:700;color:#e8edf5;letter-spacing:.08em">MANUFACTURING HUB</div>
        <div style="font-size:10px;color:#6b7fa3;letter-spacing:.14em">SIMULATION SUITE v2.0</div>
    </div>
    <hr style="border-color:#1e3a5f;margin-bottom:18px">
    """, unsafe_allow_html=True)

    menu = st.selectbox("MÓDULO", [
        "⚙️  Configuración de Planta",
        "⚖️  Balanceo de Líneas",
        "▶️  Ejecución y Análisis",
        "📈  Dashboard de KPIs",
        "🔧  Análisis de Confiabilidad",
        "📋  Reporte de Producción",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color:#1e3a5f;margin:18px 0'>", unsafe_allow_html=True)

    if st.session_state.results:
        k = st.session_state.results['kpis']
        oc = "#00ff9f" if k['oee'] >= 75 else ("#ffb800" if k['oee'] >= 50 else "#ff3b5c")
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e3a5f;border-radius:10px;padding:13px">
            <div style="font-size:9px;letter-spacing:.12em;color:#6b7fa3;margin-bottom:8px">ÚLTIMA CORRIDA</div>
            <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                <span style="font-size:11px;color:#6b7fa3">Unidades</span>
                <span style="font-family:'Rajdhani',sans-serif;font-size:14px;color:#00d4ff;font-weight:700">{k['unidades']}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                <span style="font-size:11px;color:#6b7fa3">OEE</span>
                <span style="font-family:'Rajdhani',sans-serif;font-size:14px;color:{oc};font-weight:700">{k['oee']}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                <span style="font-size:11px;color:#6b7fa3">Throughput</span>
                <span style="font-family:'Rajdhani',sans-serif;font-size:14px;color:#00ff9f;font-weight:700">{k['throughput']} u/h</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                <span style="font-size:11px;color:#6b7fa3">Tiempo Muerto</span>
                <span style="font-family:'Rajdhani',sans-serif;font-size:14px;color:{'#00ff9f' if k.get('idle_time_pct', 0) <= 5 else ('#ffb800' if k.get('idle_time_pct', 0) <= 10 else '#ff3b5c')};font-weight:700">{k.get('idle_time_pct', 0)}%</span>
            </div>
            <div style="display:flex;justify-content:space-between">
                <span style="font-size:11px;color:#6b7fa3">Tasa de Scrap</span>
                <span style="font-family:'Rajdhani',sans-serif;font-size:14px;color:{'#00ff9f' if k.get('scrap_rate', 0) <= 2 else ('#ffb800' if k.get('scrap_rate', 0) <= 5 else '#ff3b5c')};font-weight:700">{k.get('scrap_rate', 0)}% ({k.get('scrap_count', 0)} pzas)</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="dev-footer">Desarrollado por<br><strong>Master Engineer Erik Armenta</strong></div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 · CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════
if "Configuración" in menu:
    st.markdown(sec("⚙️", "CONFIGURACIÓN DE PLANTA", "Setup"), unsafe_allow_html=True)

    # Bloque general
    st.markdown('<div class="param-card"><div class="param-title">🏭 Parámetros Generales</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.config['piezas'] = st.number_input("Piezas a simular", 1, 5000, st.session_state.config['piezas'], 10)
    with c2:
        st.session_state.config['takt']   = st.number_input("Takt Time objetivo (s)", 1, 500, st.session_state.config['takt'], 5)
    with c3:
        st.session_state.config['kanban'] = st.slider("Capacidad Kanban", 1, 100, st.session_state.config['kanban'])
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloque confiabilidad
    st.markdown('<div class="param-card"><div class="param-title">🔧 Confiabilidad — MTBF / MTTR / Idle / Scrap</div>', unsafe_allow_html=True)
    cf1, cf2, cf3 = st.columns([2, 2, 1])
    with cf1:
        st.session_state.config['mtbf'] = st.slider("MTBF · Tiempo entre fallas (s)", 100, 5000, st.session_state.config['mtbf'], 50)
    with cf2:
        st.session_state.config['mttr'] = st.slider("MTTR · Tiempo de reparación (s)", 10, 1000, st.session_state.config['mttr'], 10)
    with cf3:
        d = round((st.session_state.config['mtbf'] /
                   (st.session_state.config['mtbf'] + st.session_state.config['mttr'])) * 100, 1)
        dc = "#00ff9f" if d >= 90 else ("#ffb800" if d >= 75 else "#ff3b5c")
        st.markdown(f"""<div style="background:#0a0e1a;border:1px solid #1e3a5f;border-radius:10px;
                        padding:14px;text-align:center;margin-top:22px">
                        <div style="font-size:9px;color:#6b7fa3;letter-spacing:.1em;margin-bottom:4px">DISPONIBILIDAD TEÓRICA</div>
                        <div style="font-family:'Rajdhani',sans-serif;font-size:28px;font-weight:700;color:{dc}">{d}%</div>
                        </div>""", unsafe_allow_html=True)
    # Idle factor - tiempos muertos
    idle_col1, idle_col2 = st.columns([3, 2])
    with idle_col1:
        st.session_state.config['idle_factor'] = st.slider(
            "⏸️ Idle Factor · Tiempo muerto (%)",
            min_value=0, max_value=15,
            value=st.session_state.config.get('idle_factor', 5),
            help="Porcentaje de tiempo perdido por microparos, cambios de herramienta, esperas de material y otras ineficiencias operativas."
        )
    with idle_col2:
        idle_val = st.session_state.config['idle_factor']
        idle_color = "#00ff9f" if idle_val <= 5 else ("#ffb800" if idle_val <= 10 else "#ff3b5c")
        st.markdown(f"""<div style="background:#0a0e1a;border:1px solid #1e3a5f;border-radius:10px;
                        padding:14px;text-align:center;margin-top:22px">
                        <div style="font-size:9px;color:#6b7fa3;letter-spacing:.1em;margin-bottom:4px">IMPACTO TIEMPO MUERTO</div>
                        <div style="font-family:'Rajdhani',sans-serif;font-size:28px;font-weight:700;color:{idle_color}">{idle_val}%</div>
                        </div>""", unsafe_allow_html=True)
    # Defect rate - tasa de scrap/rechazo
    scrap_col1, scrap_col2 = st.columns([3, 2])
    with scrap_col1:
        st.session_state.config['defect_rate'] = st.slider(
            "🗑️ Defect Rate · Tasa de Scrap (%)",
            min_value=0, max_value=10,
            value=st.session_state.config.get('defect_rate', 2),
            help="Porcentaje de piezas defectuosas/rechazadas durante el proceso. Incluye defectos de calidad, retrabajos y scrap."
        )
    with scrap_col2:
        defect_val = st.session_state.config['defect_rate']
        defect_color = "#00ff9f" if defect_val <= 2 else ("#ffb800" if defect_val <= 5 else "#ff3b5c")
        st.markdown(f"""<div style="background:#0a0e1a;border:1px solid #1e3a5f;border-radius:10px;
                        padding:14px;text-align:center;margin-top:22px">
                        <div style="font-size:9px;color:#6b7fa3;letter-spacing:.1em;margin-bottom:4px">IMPACTO CALIDAD</div>
                        <div style="font-family:'Rajdhani',sans-serif;font-size:28px;font-weight:700;color:{defect_color}">{defect_val}%</div>
                        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Estaciones
    st.markdown('<div class="param-card"><div class="param-title">🏗️ Estaciones de Trabajo</div>', unsafe_allow_html=True)
    est_items = list(st.session_state.config['estaciones'].items())
    cols = st.columns(max(1, len(est_items)))
    icons = ["🔩","⚡","🔍","🔨","🖨️","🔬","🛠️"]
    for idx, (name, p) in enumerate(est_items):
        color = PALETTE[idx % len(PALETTE)]
        with cols[idx]:
            st.markdown(f"""<div style="background:#0a0e1a;border:1px solid {color}44;
                            border-top:3px solid {color};border-radius:10px;padding:14px;margin-bottom:8px">
                            <div style="font-family:'Rajdhani',sans-serif;font-size:14px;font-weight:700;
                            color:{color};letter-spacing:.07em;margin-bottom:10px">
                            {icons[idx%len(icons)]} {name.upper()}</div>""", unsafe_allow_html=True)
            st.session_state.config['estaciones'][name]['ciclo'] = st.slider(f"Ciclo (s)", 5, 200, p['ciclo'], key=f"c_{name}")
            st.session_state.config['estaciones'][name]['var']   = st.slider(f"Variabilidad σ", 0, 30, p['var'], key=f"v_{name}")
            ratio = p['ciclo'] / max(1, st.session_state.config['takt'])
            rc = "#00ff9f" if ratio <= 1 else "#ff3b5c"
            st.markdown(f"<div style='font-size:11px;color:#6b7fa3;margin-top:3px'>Ciclo/Takt: <b style='color:{rc}'>{ratio:.2f}</b></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    a1, a2, a3 = st.columns([2, 1, 1])
    new_name = a1.text_input("Nueva estación", placeholder="Ej: Pintura")
    a2.markdown("<br>", unsafe_allow_html=True)
    if a2.button("➕ Agregar"):
        if new_name and new_name not in st.session_state.config['estaciones']:
            st.session_state.config['estaciones'][new_name] = {'ciclo': 45, 'var': 3}
            st.rerun()
    del_opt = a3.selectbox("Eliminar", ["—"] + list(st.session_state.config['estaciones'].keys()))
    if del_opt != "—" and a3.button("🗑️ Eliminar"):
        del st.session_state.config['estaciones'][del_opt]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💾  GUARDAR CONFIGURACIÓN", use_container_width=True):
        st.success("✅ Configuración guardada.")

    # ─── EXPORT / IMPORT DE CONFIGURACIÓN ────────────────────────────────────
    st.markdown("<hr style='border-color:#1e3a5f;margin:20px 0'>", unsafe_allow_html=True)
    st.markdown(sec("📦", "EXPORTAR / IMPORTAR ESCENARIOS", "Config I/O"), unsafe_allow_html=True)

    exp_col, imp_col = st.columns(2)

    with exp_col:
        st.markdown("""<div style="background:#0a0e1a;border:1px solid #1e3a5f;border-radius:10px;padding:14px">
            <div style="font-size:11px;color:#6b7fa3;margin-bottom:8px">📤 EXPORTAR CONFIGURACIÓN</div>
            <div style="font-size:10px;color:#4a5568;margin-bottom:12px">Descarga la configuración actual como JSON para guardarla o compartirla.</div>
        """, unsafe_allow_html=True)

        # Preparar JSON de configuración
        config_export = {
            "metadata": {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "app": "MEH Simulador de Manufactura"
            },
            "config": {
                "piezas": st.session_state.config['piezas'],
                "takt": st.session_state.config['takt'],
                "kanban": st.session_state.config['kanban'],
                "mtbf": st.session_state.config['mtbf'],
                "mttr": st.session_state.config['mttr'],
                "idle_factor": st.session_state.config.get('idle_factor', 5),
                "defect_rate": st.session_state.config.get('defect_rate', 2),
                "seed": st.session_state.config.get('seed'),
                "estaciones": st.session_state.config['estaciones']
            }
        }
        config_json = json.dumps(config_export, indent=2, ensure_ascii=False)

        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meh_config_{timestamp}.json"

        st.download_button(
            label="📥 Descargar Configuración (.json)",
            data=config_json,
            file_name=filename,
            mime="application/json",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with imp_col:
        st.markdown("""<div style="background:#0a0e1a;border:1px solid #1e3a5f;border-radius:10px;padding:14px">
            <div style="font-size:11px;color:#6b7fa3;margin-bottom:8px">📥 IMPORTAR CONFIGURACIÓN</div>
            <div style="font-size:10px;color:#4a5568;margin-bottom:12px">Carga un archivo JSON con configuración guardada previamente.</div>
        """, unsafe_allow_html=True)

        uploaded_config = st.file_uploader(
            "Selecciona archivo JSON",
            type=['json'],
            key="config_uploader",
            label_visibility="collapsed"
        )

        if uploaded_config is not None:
            try:
                imported_data = json.load(uploaded_config)

                # Validar estructura del JSON
                if 'config' in imported_data:
                    imported_config = imported_data['config']

                    # Actualizar configuración
                    if 'piezas' in imported_config:
                        st.session_state.config['piezas'] = imported_config['piezas']
                    if 'takt' in imported_config:
                        st.session_state.config['takt'] = imported_config['takt']
                    if 'kanban' in imported_config:
                        st.session_state.config['kanban'] = imported_config['kanban']
                    if 'mtbf' in imported_config:
                        st.session_state.config['mtbf'] = imported_config['mtbf']
                    if 'mttr' in imported_config:
                        st.session_state.config['mttr'] = imported_config['mttr']
                    if 'idle_factor' in imported_config:
                        st.session_state.config['idle_factor'] = imported_config['idle_factor']
                    if 'defect_rate' in imported_config:
                        st.session_state.config['defect_rate'] = imported_config['defect_rate']
                    if 'seed' in imported_config:
                        st.session_state.config['seed'] = imported_config['seed']
                    if 'estaciones' in imported_config:
                        st.session_state.config['estaciones'] = imported_config['estaciones']

                    # Mostrar info de metadata si existe
                    if 'metadata' in imported_data:
                        meta = imported_data['metadata']
                        export_date = meta.get('exported_at', 'N/A')
                        if export_date != 'N/A':
                            export_date = export_date[:19].replace('T', ' ')
                        st.success(f"✅ Configuración importada (exportada: {export_date})")
                    else:
                        st.success("✅ Configuración importada correctamente")

                    st.rerun()
                else:
                    st.error("❌ Formato JSON inválido: falta sección 'config'")

            except json.JSONDecodeError:
                st.error("❌ Error: El archivo no es un JSON válido")
            except Exception as e:
                st.error(f"❌ Error al importar: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ─── VALIDACIÓN EN TIEMPO REAL ───────────────────────────────────────────
    st.markdown("<hr style='border-color:#1e3a5f;margin:20px 0'>", unsafe_allow_html=True)
    st.markdown(sec("🔍", "VALIDACIÓN DE CONFIGURACIÓN", "Live Check"), unsafe_allow_html=True)

    validation = validate_config(st.session_state.config)

    if validation['valid']:
        metrics = validation.get('metrics', {})
        m1, m2, m3 = st.columns(3)
        m1.metric("Disponibilidad Teórica", f"{metrics.get('disponibilidad_teorica', 0)}%",
                  delta="OK" if metrics.get('disponibilidad_teorica', 0) >= 85 else "Mejorable",
                  delta_color="normal" if metrics.get('disponibilidad_teorica', 0) >= 85 else "off")
        m2.metric("OEE Teórico Estimado", f"{metrics.get('oee_teorico', 0)}%",
                  delta="Bueno" if metrics.get('oee_teorico', 0) >= 65 else "Bajo",
                  delta_color="normal" if metrics.get('oee_teorico', 0) >= 65 else "off")
        m3.metric("Ratio MTBF/MTTR", f"{metrics.get('ratio_mtbf_mttr', 0)}",
                  delta="Óptimo" if metrics.get('ratio_mtbf_mttr', 0) >= 8 else "Revisar",
                  delta_color="normal" if metrics.get('ratio_mtbf_mttr', 0) >= 8 else "off")

        if validation['warnings'] or validation.get('info'):
            with st.expander(f"⚠️ {len(validation['warnings'])} advertencias · {len(validation.get('info', []))} notas", expanded=False):
                show_validation_results(validation)
        else:
            st.success("✅ Configuración válida y optimizada - lista para simular")
    else:
        st.error("❌ Configuración con errores críticos")
        show_validation_results(validation)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 · EJECUCIÓN
# ══════════════════════════════════════════════════════════════════════════════
elif "Ejecución" in menu:
    st.markdown(sec("▶️", "EJECUCIÓN Y ANÁLISIS", "Simulation"), unsafe_allow_html=True)
    conf = st.session_state.config

    with st.expander("📋 Configuración activa", expanded=False):
        x1, x2, x3 = st.columns(3)
        x1.markdown(f"**Piezas:** {conf['piezas']}  \n**Takt:** {conf['takt']}s  \n**Kanban:** {conf['kanban']}")
        x2.markdown(f"**MTBF:** {conf['mtbf']}s  \n**MTTR:** {conf['mttr']}s")
        x3.markdown("\n".join([f"**{n}:** {p['ciclo']}s ±{p['var']}" for n, p in conf['estaciones'].items()]))

    if st.button("🚀  INICIAR CORRIDA DE PRODUCCIÓN", use_container_width=True, type="primary"):
        # Validar configuración antes de ejecutar
        validation = validate_config(conf)

        if not validation['valid']:
            st.error("❌ Configuración inválida - no se puede ejecutar simulación")
            show_validation_results(validation)
        else:
            # Mostrar warnings si existen, pero permitir ejecución
            if validation['warnings']:
                with st.expander("⚠️ Advertencias de configuración", expanded=True):
                    show_validation_results(validation)

            with st.spinner("⚙️  Simulando..."):
                r = run_simulation(conf)
            if r:
                # Guardar resultado anterior para comparación de escenarios
                if st.session_state.results is not None:
                    st.session_state.previous_results = st.session_state.results
                st.session_state.results = r
                st.success(f"✅ Simulación completada — {r['kpis']['unidades']} unidades producidas")
            else:
                st.error("❌ La simulación no produjo resultados. Revisa los parámetros.")

    R = st.session_state.results
    if not R:
        st.markdown("""
        <div style="text-align:center;padding:50px;background:#111827;border:1px dashed #1e3a5f;
                    border-radius:14px;margin-top:20px">
            <div style="font-size:42px;margin-bottom:12px">⚙️</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:20px;color:#e8edf5;margin-bottom:6px">LISTO PARA SIMULAR</div>
            <div style="font-size:13px;color:#6b7fa3">Presiona <b style="color:#00d4ff">INICIAR CORRIDA</b> para ejecutar</div>
        </div>""", unsafe_allow_html=True)
        st.stop()

    k = R['kpis']
    df_prod  = R['df_prod']
    df_fail  = R['df_fail']
    df_total = R['df_total']

    # KPI CARDS
    oc = "#00ff9f" if k['oee'] >= 75 else ("#ffb800" if k['oee'] >= 50 else "#ff3b5c")
    dc = "#00ff9f" if k['disponibilidad'] >= 90 else ("#ffb800" if k['disponibilidad'] >= 75 else "#ff3b5c")
    st.markdown('<div class="kpi-grid">'
        + kpi("UNIDADES PRODUCIDAS", k['unidades'],   "piezas completadas",    "#00d4ff")
        + kpi("THROUGHPUT",          f"{k['throughput']}", "piezas / hora",    "#00ff9f")
        + kpi("OEE",                 f"{k['oee']}%",  "Efectividad global",    oc)
        + kpi("DISPONIBILIDAD",      f"{k['disponibilidad']}%", "A = MTBF/(MTBF+MTTR)", dc)
        + kpi("TIEMPO DE CICLO",     f"{k['ciclo_promedio']}s", "lead time promedio",    "#ffb800")
        + kpi("TIEMPO SIMULADO",     f"{k['t_final']}s", f"≈ {round(k['t_final']/3600,2)} h", "#9b59b6")
        + kpi("FALLAS TOTALES",      k['total_fallas'], "eventos de paro",      "#ff3b5c")
        + kpi("RENDIMIENTO",         f"{k['rendimiento']}%", "Performance OEE", "#ff6b35")
        + '</div>', unsafe_allow_html=True)

    # ── COMPARADOR DE ESCENARIOS ────────────────────────────────────────────
    prev = st.session_state.previous_results
    if prev:
        pk = prev['kpis']
        with st.expander("📊 Comparar con escenario anterior", expanded=False):
            st.markdown('''
            <div style="background:#111827;border-radius:12px;padding:16px;border:1px solid #1e3a5f">
                <table style="width:100%;border-collapse:collapse;font-size:13px">
                    <thead>
                        <tr style="border-bottom:1px solid #1e3a5f">
                            <th style="padding:8px 12px;text-align:left;color:#6b7fa3;font-weight:600">KPI</th>
                            <th style="padding:8px 12px;text-align:center;color:#6b7fa3;font-weight:600">Anterior</th>
                            <th style="padding:8px 12px;text-align:center;color:#6b7fa3;font-weight:600">Actual</th>
                            <th style="padding:8px 12px;text-align:center;color:#6b7fa3;font-weight:600">Delta</th>
                        </tr>
                    </thead>
                    <tbody>'''
                + comparison_row("Unidades Producidas", k['unidades'], pk['unidades'])
                + comparison_row("Throughput (pzas/h)", k['throughput'], pk['throughput'])
                + comparison_row("OEE", k['oee'], pk['oee'], "%")
                + comparison_row("Disponibilidad", k['disponibilidad'], pk['disponibilidad'], "%")
                + comparison_row("Tiempo de Ciclo", k['ciclo_promedio'], pk['ciclo_promedio'], "s", higher_is_better=False)
                + comparison_row("Fallas Totales", k['total_fallas'], pk['total_fallas'], "", higher_is_better=False)
                + comparison_row("Rendimiento", k['rendimiento'], pk['rendimiento'], "%")
                + comparison_row("Tasa de Scrap", k.get('scrap_rate', 0), pk.get('scrap_rate', 0), "%", higher_is_better=False)
                + '''
                    </tbody>
                </table>
            </div>''', unsafe_allow_html=True)

    # ROW 1
    g1, g2 = st.columns(2)
    with g1:
        bk = R['bottleneck_df'].copy()
        takt_v = conf['takt']
        colors_b = ["#ff3b5c" if v > takt_v * 0.5 else "#00d4ff" for v in bk['Espera_Prom']]
        fig_bk = go.Figure(go.Bar(
            x=bk['Estacion'], y=bk['Espera_Prom'],
            marker_color=colors_b,
            text=bk['Espera_Prom'].apply(lambda x: f"{x:.1f}s"),
            textposition='outside', textfont=dict(color='#e8edf5', size=12),
            hovertemplate="<b>%{x}</b><br>Espera prom: %{y:.2f}s<extra></extra>"
        ))
        fig_bk.add_hline(y=takt_v*0.5, line_dash="dash", line_color="#ffb800",
                         annotation_text=f"Límite ({takt_v*0.5:.0f}s)", annotation_font_color="#ffb800")
        fig_bk.update_layout(title="CUELLOS DE BOTELLA — Espera Promedio", **PT)
        st.plotly_chart(fig_bk, use_container_width=True)

    with g2:
        util = k['util_data']
        fig_util = go.Figure()
        for i, (nm, val) in enumerate(util.items()):
            c = "#00ff9f" if val < 80 else ("#ffb800" if val < 95 else "#ff3b5c")
            fig_util.add_trace(go.Bar(name=nm, x=[nm], y=[val], marker_color=c,
                text=[f"{val}%"], textposition='inside',
                textfont=dict(color='white', size=13, family='Rajdhani'),
                hovertemplate=f"<b>{nm}</b><br>Utilización: {val}%<extra></extra>"))
        fig_util.add_hline(y=85, line_dash="dot", line_color="#ffb800",
                           annotation_text="85% ref.", annotation_font_color="#ffb800")
        fig_util.update_layout(title="UTILIZACIÓN DE MÁQUINAS (%)", showlegend=False, **PT)
        fig_util.update_yaxes(range=[0, 115])
        st.plotly_chart(fig_util, use_container_width=True)

    # ROW 2
    g3, g4 = st.columns(2)
    with g3:
        if not df_prod.empty and df_prod['Espera'].sum() > 0:
            enames = df_prod['Estacion'].unique().tolist()
            cmap   = {n: PALETTE[i % len(PALETTE)] for i, n in enumerate(enames)}
            chart = alt.Chart(df_prod).mark_bar(opacity=0.82, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                alt.X('Espera:Q', bin=alt.Bin(maxbins=25), title='Tiempo de Espera (s)',
                      axis=alt.Axis(labelColor='#6b7fa3', titleColor='#6b7fa3', gridColor='#1e3a5f')),
                alt.Y('count():Q', title='Frecuencia',
                      axis=alt.Axis(labelColor='#6b7fa3', titleColor='#6b7fa3', gridColor='#1e3a5f')),
                alt.Color('Estacion:N', scale=alt.Scale(domain=list(cmap.keys()), range=list(cmap.values())),
                          legend=alt.Legend(labelColor='#6b7fa3', titleColor='#6b7fa3')),
                tooltip=['Estacion:N', alt.Tooltip('Espera:Q', format='.1f', title='Espera (s)'), 'count():Q']
            ).properties(
                title=alt.TitleParams('HISTOGRAMA — Tiempos de Espera', color='#e8edf5', font='Rajdhani', fontSize=15),
                background='rgba(17,24,39,0.6)'
            ).configure_view(strokeOpacity=0).configure_axis(domainColor='#1e3a5f')
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Sin tiempos de espera significativos con esta configuración.")

    with g4:
        fig_tr = px.scatter(df_total, x="Salida", y="Estacion", color="Tipo",
                            color_discrete_map={"Producción":"#00ff9f","Downtime":"#ff3b5c"},
                            hover_data={"ID":True,"Proceso":":.1f","Espera":":.1f"},
                            title="TRAZABILIDAD — Producción vs Paros")
        fig_tr.update_traces(marker=dict(size=7, opacity=0.8))
        fig_tr.update_layout(**PT)
        st.plotly_chart(fig_tr, use_container_width=True)

    # GANTT
    st.markdown(sec("📊", "DIAGRAMA DE GANTT", "Primeras 50 piezas"), unsafe_allow_html=True)
    if not df_prod.empty:
        dg = df_prod[df_prod['ID'] != 'PARO'].head(50).copy()
        dg['Inicio_dt'] = pd.to_datetime(dg['Inicio'], unit='s', origin='unix')
        dg['Salida_dt'] = pd.to_datetime(dg['Salida'],  unit='s', origin='unix')
        fig_g = px.timeline(dg, x_start="Inicio_dt", x_end="Salida_dt",
                            y="Estacion", color="Estacion", hover_name="ID",
                            hover_data={"Proceso":":.1f","Espera":":.1f"},
                            color_discrete_sequence=PALETTE,
                            title="GANTT — Flujo de Producción por Estación")
        fig_g.update_yaxes(autorange="reversed")
        fig_g.update_layout(**PT, height=260)
        st.plotly_chart(fig_g, use_container_width=True)

    with st.expander("📋 Datos completos"):
        st.dataframe(df_total.sort_values("Salida"), use_container_width=True, height=300)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 · DASHBOARD KPIs
# ══════════════════════════════════════════════════════════════════════════════
elif "Dashboard" in menu:
    st.markdown(sec("📈", "DASHBOARD DE KPIs", "Live"), unsafe_allow_html=True)
    if not st.session_state.results:
        st.warning("⚠️ Ejecuta una corrida primero.")
        st.stop()

    R    = st.session_state.results
    k    = R['kpis']
    conf = st.session_state.config

    d1, d2 = st.columns([1, 2])
    with d1:
        fig_oee = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=k['oee'],
            delta={'reference': 75, 'increasing':{'color':'#00ff9f'}, 'decreasing':{'color':'#ff3b5c'}},
            title={'text': "OEE GLOBAL", 'font': {'family':'Rajdhani','size':16,'color':'#e8edf5'}},
            number={'suffix':'%', 'font':{'family':'Rajdhani','size':38,'color':'#00d4ff'}},
            gauge={
                'axis': {'range':[0,100], 'tickcolor':'#6b7fa3'},
                'bar':  {'color':'#00d4ff'},
                'steps': [{'range':[0,50],  'color':'rgba(255,59,92,0.13)'},
                           {'range':[50,75], 'color':'rgba(255,184,0,0.13)'},
                           {'range':[75,100],'color':'rgba(0,255,159,0.13)'}],
                'threshold': {'line':{'color':'#ffb800','width':3}, 'value':75},
                'bgcolor': 'rgba(0,0,0,0)', 'bordercolor':'#1e3a5f',
            }
        ))
        fig_oee.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#6b7fa3',
                              height=290, margin=dict(l=20,r=20,t=48,b=10))
        st.plotly_chart(fig_oee, use_container_width=True)
        st.markdown(f"""
        <div style="background:#0a0e1a;border:1px solid #1e3a5f;border-radius:10px;padding:14px">
            <div style="font-size:9px;letter-spacing:.12em;color:#6b7fa3;margin-bottom:10px">OEE BREAKDOWN</div>
            <div style="display:flex;justify-content:space-between;margin-bottom:7px">
                <span style="font-size:12px;color:#6b7fa3">Disponibilidad (A)</span>
                <span style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#00d4ff;font-weight:700">{k['disponibilidad']}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:7px">
                <span style="font-size:12px;color:#6b7fa3">Rendimiento (P)</span>
                <span style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#ff6b35;font-weight:700">{k['rendimiento']}%</span>
            </div>
            <div style="display:flex;justify-content:space-between">
                <span style="font-size:12px;color:#6b7fa3">Calidad (Q)</span>
                <span style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#00ff9f;font-weight:700">{k['calidad']}%</span>
            </div>
        </div>""", unsafe_allow_html=True)

    with d2:
        if not R['df_prod'].empty:
            def _rgba(hx, a=0.2):
                h=hx.lstrip('#'); r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
                return f'rgba({r},{g},{b},{a})'
            fig_box = go.Figure()
            for i, en in enumerate(R['estaciones_names']):
                dat = R['df_prod'][R['df_prod']['Estacion']==en]['Proceso']
                c   = PALETTE[i % len(PALETTE)]
                fig_box.add_trace(go.Box(y=dat, name=en, marker_color=c,
                    line_color=c, fillcolor=_rgba(c),
                    hovertemplate=f"<b>{en}</b><br>Ciclo: %{{y:.1f}}s<extra></extra>"))
            fig_box.add_hline(y=conf['takt'], line_dash="dash", line_color="#ffb800",
                              annotation_text=f"Takt: {conf['takt']}s",
                              annotation_font_color="#ffb800")
            fig_box.update_layout(title="DISTRIBUCIÓN CICLOS vs TAKT TIME",
                                  showlegend=False, **PT, height=340)
            st.plotly_chart(fig_box, use_container_width=True)

    # WIP
    df_wip = R['df_wip']
    if not df_wip.empty:
        frames = []
        for en in R['estaciones_names']:
            de = df_wip[df_wip['estacion']==en].copy().sort_values('time')
            de['wip_cum'] = de['delta'].cumsum().clip(lower=0)
            frames.append(de)
        df_wp = pd.concat(frames)
        fig_wip = px.line(df_wp, x='time', y='wip_cum', color='estacion',
                          title="WIP ACUMULADO POR ESTACIÓN",
                          color_discrete_sequence=PALETTE,
                          labels={'time':'Tiempo (s)','wip_cum':'WIP','estacion':'Estación'})
        fig_wip.update_traces(line=dict(width=2))
        fig_wip.update_layout(**PT)
        st.plotly_chart(fig_wip, use_container_width=True)

    # Throughput acumulado
    last_est = R['estaciones_names'][-1]
    df_tp = R['df_prod'][R['df_prod']['Estacion']==last_est].sort_values('Salida').copy()
    if not df_tp.empty:
        df_tp['acumulado'] = range(1, len(df_tp)+1)
        df_tp['tp_inst']   = df_tp['acumulado'] / (df_tp['Salida'] / 3600)
        fig_tp = go.Figure()
        fig_tp.add_trace(go.Scatter(x=df_tp['Salida'], y=df_tp['acumulado'],
            name='Producción acumulada', line=dict(color='#00ff9f', width=2),
            fill='tozeroy', fillcolor='rgba(0,255,159,0.07)',
            hovertemplate="T: %{x:.0f}s<br>Piezas: %{y}<extra></extra>"))
        fig_tp.add_trace(go.Scatter(x=df_tp['Salida'], y=df_tp['tp_inst'],
            name='Throughput inst. (u/h)', yaxis='y2',
            line=dict(color='#00d4ff', width=1.5, dash='dot'),
            hovertemplate="TH: %{y:.1f} u/h<extra></extra>"))
        fig_tp.update_layout(title="PRODUCCIÓN ACUMULADA & THROUGHPUT INSTANTÁNEO",
            yaxis2=dict(overlaying='y', side='right', showgrid=False,
                        tickfont=dict(color='#00d4ff'), title='u/h'), **PT)
        st.plotly_chart(fig_tp, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4 · CONFIABILIDAD
# ══════════════════════════════════════════════════════════════════════════════
elif "Confiabilidad" in menu:
    st.markdown(sec("🔧", "ANÁLISIS DE CONFIABILIDAD", "Reliability"), unsafe_allow_html=True)
    if not st.session_state.results:
        st.warning("⚠️ Ejecuta una corrida primero.")
        st.stop()

    R    = st.session_state.results
    k    = R['kpis']
    conf = st.session_state.config

    st.markdown('<div class="kpi-grid">'
        + kpi("DISPONIBILIDAD",  f"{k['disponibilidad']}%", "A simulada",       "#00d4ff")
        + kpi("EVENTOS DE PARO", str(k['total_fallas']),    "fallas totales",   "#ff3b5c")
        + kpi("MTBF CONFIG",     f"{conf['mtbf']}s",        "entre fallas",     "#ffb800")
        + kpi("MTTR CONFIG",     f"{conf['mttr']}s",        "reparación media", "#ff6b35")
        + '</div>', unsafe_allow_html=True)

    if R['df_fail'].empty:
        st.info("Sin fallas registradas. Reduce el MTBF para generar eventos de paro.")
        st.stop()

    df_fail = R['df_fail']
    r1, r2 = st.columns(2)
    with r1:
        dt_est = df_fail.groupby('Estacion')['Proceso'].agg(['sum','count','mean']).reset_index()
        dt_est.columns = ['Estacion','Downtime Total (s)','Eventos','MTTR Real (s)']
        dt_est = dt_est.round(1)
        fig_dt = px.bar(dt_est, x='Estacion', y='Downtime Total (s)',
                        color='Estacion', text='Eventos',
                        color_discrete_sequence=PALETTE,
                        title="DOWNTIME TOTAL POR ESTACIÓN",
                        hover_data={'MTTR Real (s)':True})
        fig_dt.update_layout(**PT)
        st.plotly_chart(fig_dt, use_container_width=True)

    with r2:
        fig_fh = go.Figure(go.Histogram(x=df_fail['Proceso'], nbinsx=20,
                                        marker_color='#ff3b5c', opacity=0.75,
                                        hovertemplate="Duración: %{x:.0f}s<br>Frec: %{y}<extra></extra>"))
        fig_fh.update_layout(title="DISTRIBUCIÓN DURACIÓN DE FALLAS",
                             xaxis_title="Duración (s)", yaxis_title="Frecuencia", **PT)
        st.plotly_chart(fig_fh, use_container_width=True)

    fig_ft = px.scatter(df_fail, x='Inicio', y='Estacion', size='Proceso', color='Estacion',
                        color_discrete_sequence=PALETTE, title="LÍNEA DE TIEMPO — EVENTOS DE PARO",
                        hover_data={'Proceso':':.1f','ID':True},
                        labels={'Inicio':'Tiempo (s)','Proceso':'Duración (s)'})
    fig_ft.update_layout(**PT)
    st.plotly_chart(fig_ft, use_container_width=True)
    st.dataframe(df_fail[['ID','Estacion','Inicio','Proceso','Salida']].round(1), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 5 · REPORTE
# ══════════════════════════════════════════════════════════════════════════════
elif "Reporte" in menu:
    st.markdown(sec("📋", "REPORTE DE PRODUCCIÓN", "Export"), unsafe_allow_html=True)
    if not st.session_state.results:
        st.warning("⚠️ Ejecuta una corrida primero.")
        st.stop()

    R    = st.session_state.results
    k    = R['kpis']
    conf = st.session_state.config

    st.markdown('<div class="param-card"><div class="param-title">📊 Resumen Ejecutivo</div>', unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)
    rc1.markdown(f"**Piezas objetivo:** `{conf['piezas']}`  \n**Piezas producidas:** `{k['unidades']}`  \n**Tiempo simulado:** `{k['t_final']}s` ({round(k['t_final']/3600,2)} h)  \n**Takt Time:** `{conf['takt']}s`")
    rc2.markdown(f"**OEE:** `{k['oee']}%`  \n**Disponibilidad:** `{k['disponibilidad']}%`  \n**Throughput:** `{k['throughput']} u/h`  \n**Ciclo promedio:** `{k['ciclo_promedio']}s`")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### 📌 Estadísticas por Estación")
    st.dataframe(R['ciclo_est_df'], use_container_width=True)
    st.markdown("#### 🔴 Cuellos de Botella")
    st.dataframe(R['bottleneck_df'], use_container_width=True)

    st.markdown("#### ⬇️ Exportar")
    st.download_button("📥 Datos completos (.csv)",
        R['df_total'].to_csv(index=False).encode('utf-8'),
        "simulacion_manufactura.csv", "text/csv", use_container_width=True)
    st.download_button("📥 Resumen KPIs (.csv)",
        pd.DataFrame([k]).to_csv(index=False).encode('utf-8'),
        "kpis_manufactura.csv", "text/csv", use_container_width=True)

    st.markdown('<div class="dev-footer" style="margin-top:48px;font-size:13px"><strong>MASTER ENGINEERING HUB · v2.0</strong><br><span style="color:#6b7fa3">Desarrollado por Master Engineer Erik Armenta</span></div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 6 · BALANCEO DE LÍNEAS + OPERADORES
# ══════════════════════════════════════════════════════════════════════════════
elif "Balanceo" in menu:
    import math as _math
    st.markdown(sec("⚖️", "BALANCEO DE LÍNEAS", "Line Balancing · Operator Optimization"), unsafe_allow_html=True)

    # ── A: Definición de Tareas ───────────────────────────────────────────────
    st.markdown('<div class="param-card"><div class="param-title">📋 Definición de Tareas de Operación</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#6b7fa3;margin-bottom:10px">'
                'Define cada operación con su nombre, tiempo (s) y predecesoras separadas por coma '
                '(ej: T1,T2). Deja vacío si no tiene predecesoras.</div>', unsafe_allow_html=True)

    if 'bl_tasks_df' not in st.session_state:
        st.session_state.bl_tasks_df = pd.DataFrame([
            {"Tarea": "T1", "Tiempo (s)": 25, "Predecesoras": ""},
            {"Tarea": "T2", "Tiempo (s)": 30, "Predecesoras": "T1"},
            {"Tarea": "T3", "Tiempo (s)": 20, "Predecesoras": "T1"},
            {"Tarea": "T4", "Tiempo (s)": 35, "Predecesoras": "T2"},
            {"Tarea": "T5", "Tiempo (s)": 15, "Predecesoras": "T2,T3"},
            {"Tarea": "T6", "Tiempo (s)": 40, "Predecesoras": "T3"},
            {"Tarea": "T7", "Tiempo (s)": 25, "Predecesoras": "T4,T5,T6"},
        ])

    # Evitar bug de pérdida de foco al escribir:
    # Solo pisamos bl_tasks_df cuando regresamos de otra pestaña (bl_editor no existe en state)
    if "bl_editor" not in st.session_state and "bl_tasks_backup" in st.session_state:
        st.session_state.bl_tasks_df = st.session_state.bl_tasks_backup.copy()

    edited_df = st.data_editor(
        st.session_state.bl_tasks_df, num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Tarea":        st.column_config.TextColumn("Tarea", width="small"),
            "Tiempo (s)":  st.column_config.NumberColumn("Tiempo (s)", min_value=1, max_value=600, step=1),
            "Predecesoras": st.column_config.TextColumn("Predecesoras (separadas por coma)", width="large"),
        }, key="bl_editor"
    )
    # Guardamos los cambios en un backup sin reiniciar la tabla que se está graficando en este momento
    st.session_state.bl_tasks_backup = edited_df
    st.markdown('</div>', unsafe_allow_html=True)

    # ── B: Parámetros ─────────────────────────────────────────────────────────
    st.markdown('<div class="param-card"><div class="param-title">⚙️ Parámetros de Balanceo y Operadores</div>', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        bl_algo = st.selectbox("Algoritmo", ["LCR — Largest Candidate Rule", "RPW — Ranked Positional Weight"])
    with b2:
        bl_takt = st.number_input("Takt Time (s)", min_value=5, max_value=600,
                                  value=st.session_state.config['takt'], step=5,
                                  help="Tiempo disponible ÷ Demanda del cliente.")
    with b3:
        bl_current_ops = st.number_input("Operadores actuales", min_value=0, max_value=200, value=0, step=1,
                                         help="Escribe cuántos operadores tienes hoy en la línea. "
                                              "0 = solo calcular mínimo sin comparar.")
    with b4:
        t_disp = st.number_input("Tiempo disponible (min/turno)", min_value=60, max_value=1440, value=480, step=30,
                                 help="Minutos por turno. Usado para calcular la demanda implícita.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚖️  CALCULAR BALANCEO", use_container_width=True, type="primary"):
        df_t = edited_df.dropna(subset=["Tarea", "Tiempo (s)"])
        df_t = df_t[df_t["Tarea"].astype(str).str.strip() != ""]
        if df_t.empty:
            st.error("❌ Agrega al menos una tarea con nombre y tiempo válido.")
            st.stop()

        tasks_dict = {str(r["Tarea"]).strip(): float(r["Tiempo (s)"]) for _, r in df_t.iterrows()}
        prec_list  = []
        for _, r in df_t.iterrows():
            raw = str(r.get("Predecesoras", "") or "").strip()
            for p in raw.split(","):
                p = p.strip()
                if p and p in tasks_dict:
                    prec_list.append((p, str(r["Tarea"]).strip()))

        if "LCR" in bl_algo:
            stations   = largest_candidate_rule(tasks_dict, prec_list, bl_takt)
            algo_label = "LCR"
        else:
            stations   = ranked_positional_weight(tasks_dict, prec_list, bl_takt)
            algo_label = "RPW"

        metrics  = balance_metrics(stations, tasks_dict, bl_takt)
        ops_data = assign_operators(stations, tasks_dict, bl_takt, int(bl_current_ops))

        st.session_state['bl_result'] = {
            'stations': stations, 'metrics': metrics, 'ops': ops_data,
            'tasks': tasks_dict, 'prec': prec_list,
            'takt': bl_takt, 'algo': algo_label, 'current_ops': int(bl_current_ops),
        }

    # ── C: Resultados ─────────────────────────────────────────────────────────
    if 'bl_result' in st.session_state and st.session_state['bl_result']:
        BL     = st.session_state['bl_result']
        m      = BL['metrics']
        ops    = BL['ops']
        sd     = m['station_data']
        takt_v = BL['takt']

        st.markdown(sec("📊", "RESULTADOS DEL BALANCEO", BL['algo']), unsafe_allow_html=True)

        # ── KPI cards — balanceo ──────────────────────────────────────────────
        eff_c  = "#00ff9f" if m['efficiency'] >= 85 else ("#ffb800" if m['efficiency'] >= 70 else "#ff3b5c")
        opt_c  = "#00ff9f" if m['n_stations'] == m['n_min'] else ("#ffb800" if m['n_stations'] <= m['n_min']+1 else "#ff3b5c")
        idle_c = "#00ff9f" if m['idle_pct'] <= 15 else ("#ffb800" if m['idle_pct'] <= 30 else "#ff3b5c")
        st.markdown('<div class="kpi-grid">'
            + kpi("EFICIENCIA η",       f"{m['efficiency']}%",        "Σti / (N × Takt)",  eff_c)
            + kpi("N° ESTACIONES",      str(m['n_stations']),          "estaciones usadas", opt_c)
            + kpi("N° TEÓRICO (N*)",    str(m['n_min']),               "Σti / Takt",        "#00d4ff")
            + kpi("ÍNDICE SUAVIDAD SI", str(m['smoothness']),          "√Σ(Takt−Cargaᵢ)²", "#ff6b35")
            + kpi("% IDLE TOTAL",       f"{m['idle_pct']}%",          "tiempo ocioso",     idle_c)
            + kpi("SUMA OPERACIONES",   f"{m['total_task_time']}s",    "tiempo total",      "#9b59b6")
            + '</div>', unsafe_allow_html=True)

        # ── KPI cards — operadores ────────────────────────────────────────────
        st.markdown(sec("👷", "OPTIMIZACIÓN DE OPERADORES", "Headcount"), unsafe_allow_html=True)
        op_min  = ops.get('total_min_ops', 0)
        cur_ops = ops.get('current_ops', 0)
        saving  = ops.get('saving')
        sav_pct = ops.get('saving_pct')

        ops_cards = (
              kpi("OPERADORES MÍNIMOS", str(op_min), "calculado por balanceo", "#00d4ff")
            + (kpi("OPERADORES ACTUALES", str(cur_ops), "en línea hoy", "#ffb800") if cur_ops > 0 else "")
        )
        if saving is not None and cur_ops > 0:
            sav_c = "#00ff9f" if saving > 0 else "#6b7fa3"
            ops_cards += kpi("AHORRO POTENCIAL", f"−{saving} ops", f"{sav_pct}% reducción", sav_c)
        st.markdown('<div class="kpi-grid">' + ops_cards + '</div>', unsafe_allow_html=True)

        if saving and saving > 0:
            st.markdown(f"""
            <div style="background:rgba(0,255,159,0.07);border:1px solid #00ff9f44;border-radius:12px;
                        padding:16px;margin-bottom:18px;display:flex;align-items:center;gap:14px">
                <div style="font-size:36px">🚀</div>
                <div>
                    <div style="font-family:'Rajdhani',sans-serif;font-size:16px;font-weight:700;color:#00ff9f">
                        Potencial de ahorro: {saving} operador{'es' if saving!=1 else ''} ({sav_pct}% reducción)
                    </div>
                    <div style="font-size:12px;color:#6b7fa3;margin-top:3px">
                        Pasarías de {cur_ops} a {op_min} operadores manteniendo el ritmo del Takt Time de {takt_v}s.
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Gráficas ──────────────────────────────────────────────────────────
        g1, g2 = st.columns(2)

        with g1:
            # Carga por estación vs Takt
            names_s  = [s['Estación']  for s in sd]
            loads_s  = [s['Carga (s)'] for s in sd]
            idles_s  = [s['Idle (s)']  for s in sd]
            clr_load = ["#ff3b5c" if l > takt_v else "#00d4ff" for l in loads_s]

            fig_load = go.Figure()
            fig_load.add_trace(go.Bar(
                name="Carga", x=names_s, y=loads_s, marker_color=clr_load,
                text=[f"{v}s" for v in loads_s], textposition='inside',
                textfont=dict(color='white', size=12),
                hovertemplate="<b>%{x}</b><br>Carga: %{y}s<extra></extra>"
            ))
            fig_load.add_trace(go.Bar(
                name="Idle", x=names_s, y=idles_s,
                marker_color='rgba(107,127,163,0.2)',
                hovertemplate="<b>%{x}</b><br>Idle: %{y}s<extra></extra>"
            ))
            fig_load.add_hline(y=takt_v, line_dash="dash", line_color="#ffb800",
                               annotation_text=f"Takt {takt_v}s", annotation_font_color="#ffb800")
            fig_load.update_layout(title=f"CARGA POR ESTACIÓN vs TAKT ({BL['algo']})",
                                   barmode='stack', showlegend=True, height=320, **PT)
            fig_load.update_yaxes(range=[0, takt_v * 1.3])
            st.plotly_chart(fig_load, use_container_width=True)

        with g2:
            # Diagrama de precedencias
            positions = build_precedence_positions(BL['tasks'], BL['prec'])
            weights_rpw = compute_positional_weights(BL['tasks'], BL['prec'])
            task_to_st  = {}
            for idx2, st_tasks2 in enumerate(BL['stations']):
                for t2 in st_tasks2:
                    task_to_st[t2] = idx2

            fig_prec = go.Figure()
            for (pred, suc) in BL['prec']:
                if pred in positions and suc in positions:
                    x0, y0 = positions[pred]; x1, y1 = positions[suc]
                    fig_prec.add_trace(go.Scatter(
                        x=[x0, x1, None], y=[y0, y1, None], mode='lines',
                        line=dict(color='#2a4a6f', width=2),
                        showlegend=False, hoverinfo='skip'))
            for task, (x, y) in positions.items():
                s_idx = task_to_st.get(task, 0)
                col   = PALETTE[s_idx % len(PALETTE)]
                t_t   = BL['tasks'].get(task, 0)
                ops_n = ops.get('station_ops', [{}])[s_idx].get('Operadores', 1) if ops.get('station_ops') and s_idx < len(ops.get('station_ops', [])) else 1
                fig_prec.add_trace(go.Scatter(
                    x=[x], y=[y], mode='markers+text',
                    marker=dict(size=40, color=col, opacity=0.88, line=dict(color='white', width=1.5)),
                    text=[task], textposition='middle center',
                    textfont=dict(family='Rajdhani', color='white', size=11),
                    showlegend=False,
                    hovertemplate=f"<b>{task}</b><br>Tiempo: {t_t}s<br>Estación: E{s_idx+1}<br>Operadores: {ops_n}<br>RPW: {weights_rpw.get(task,0):.1f}<extra></extra>"
                ))
            fig_prec.update_layout(title="DIAGRAMA DE PRECEDENCIAS", height=320, **PT)
            fig_prec.update_xaxes(visible=False)
            fig_prec.update_yaxes(visible=False)
            st.plotly_chart(fig_prec, use_container_width=True)

        # ── Gráfica de operadores por estación ────────────────────────────────
        if ops.get('station_ops'):
            chart_data = operator_balance_chart_data(ops['station_ops'], takt_v)
            fig_ops = go.Figure()
            fig_ops.add_trace(go.Bar(
                name="Carga real", x=chart_data['names'], y=chart_data['loads'],
                marker_color='#00d4ff',
                text=[f"{l}s" for l in chart_data['loads']], textposition='inside',
                textfont=dict(color='white', size=11),
                hovertemplate="<b>%{x}</b><br>Carga: %{y}s<extra></extra>"
            ))
            fig_ops.add_trace(go.Bar(
                name="Capacidad libre", x=chart_data['names'], y=chart_data['slack'],
                marker_color='rgba(0,255,159,0.18)',
                hovertemplate="<b>%{x}</b><br>Capacidad libre: %{y:.1f}s<extra></extra>"
            ))
            for i, (nm, n_ops) in enumerate(zip(chart_data['names'], chart_data['ops'])):
                fig_ops.add_annotation(x=nm, y=chart_data['capacity'][i],
                    text=f"👷×{n_ops}", showarrow=False,
                    font=dict(color='#ffb800', size=13, family='Rajdhani'),
                    yshift=10)
            fig_ops.update_layout(
                title="OPERADORES POR ESTACIÓN (carga vs capacidad = ops × Takt)",
                barmode='stack', showlegend=True, height=300, **PT)
            fig_ops.update_yaxes(range=[0, max(chart_data['capacity']) * 1.25])
            st.plotly_chart(fig_ops, use_container_width=True)

        # ── Tablas ────────────────────────────────────────────────────────────
        ta1, ta2 = st.columns(2)
        with ta1:
            st.markdown(sec("📋", "ASIGNACIÓN DE TAREAS", "Por Estación"), unsafe_allow_html=True)
            df_assign = pd.DataFrame(sd)
            st.dataframe(df_assign, use_container_width=True, hide_index=True)
        with ta2:
            st.markdown(sec("👷", "OPERADORES POR ESTACIÓN", "Headcount"), unsafe_allow_html=True)
            if ops.get('station_ops'):
                df_ops = pd.DataFrame(ops['station_ops'])
                st.dataframe(df_ops, use_container_width=True, hide_index=True)

        # ── D: Aplicar a Simulación ───────────────────────────────────────────
        st.markdown('<div class="param-card"><div class="param-title">🚀 Aplicar Balanceo a la Simulación</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;color:#6b7fa3;margin-bottom:12px">'
                    'Carga las estaciones balanceadas al simulador (ciclo = suma de tareas). '
                    'Ve a ▶️ Ejecución para correr y comparar el OEE antes y después.</div>', unsafe_allow_html=True)
        av1, av2 = st.columns([2, 1])
        with av1:
            default_var = st.slider("Variabilidad σ (s) por estación", 0, 20, 3,
                                    help="Desviación estándar aplicada a todas las estaciones en la simulación.")
        with av2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄  APLICAR A SIMULACIÓN", use_container_width=True, type="primary"):
                new_est = stations_to_config(BL['stations'], BL['tasks'], default_var)
                st.session_state.config['estaciones'] = new_est
                st.session_state.config['takt'] = int(BL['takt'])
                st.session_state.results = None
                st.success(f"✅ {len(new_est)} estaciones cargadas · Takt={BL['takt']}s · Ve a ▶️ Ejecución.")
        st.markdown('</div>', unsafe_allow_html=True)
