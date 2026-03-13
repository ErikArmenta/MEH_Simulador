# line_balancer.py — Motor de Balanceo de Líneas
# Desarrollado por Master Engineer Erik Armenta
#
# Algoritmos implementados:
#   · LCR — Largest Candidate Rule (Regla del Candidato Mayor)
#   · RPW — Ranked Positional Weight (Peso Posicional Ponderado)
#
# Métricas calculadas:
#   · N* — Número teórico mínimo de estaciones
#   · η  — Eficiencia de línea (%)
#   · SI — Índice de Suavidad (Smoothness Index)
#   · %Idle por estación

from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple


# ─── TIPOS ───────────────────────────────────────────────────────────────────
# tasks: dict  {nombre: tiempo_seg}
# precedences: list de tuplas [(pred, suc), ...]
# stations: list de listas, cada lista = tareas asignadas a esa estación
#           Ej: [["T1","T2"], ["T3"], ["T4","T5"]]


# ─── UTILIDADES DE PRECEDENCIA ────────────────────────────────────────────────

def _successors(task: str, precedences: List[Tuple[str, str]]) -> List[str]:
    """Devuelve todos los sucesores directos e indirectos de una tarea."""
    direct = {suc for pred, suc in precedences if pred == task}
    all_suc: set[str] = set()
    queue = list(direct)
    while queue:
        t = queue.pop()
        if t not in all_suc:
            all_suc.add(t)
            queue.extend(suc for pred, suc in precedences if pred == t)
    return list(all_suc)


def _predecessors_satisfied(
    task: str,
    assigned: set[str],
    precedences: List[Tuple[str, str]],
) -> bool:
    """Verifica que todos los predecesores directos de una tarea ya estén asignados."""
    required = {pred for pred, suc in precedences if suc == task}
    return required.issubset(assigned)


# ─── ALGORITMO 1: LARGEST CANDIDATE RULE (LCR) ───────────────────────────────

def largest_candidate_rule(
    tasks: Dict[str, float],
    precedences: List[Tuple[str, str]],
    takt: float,
) -> List[List[str]]:
    """
    LCR — Asigna tareas a estaciones en orden descendente de tiempo de tarea,
    respetando el Takt Time y las precedencias.

    Retorna lista de estaciones, cada una con sus tareas asignadas.
    """
    if takt <= 0:
        return []

    # Ordenar tareas de mayor a menor tiempo
    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1], reverse=True)

    stations: List[List[str]] = []
    assigned: set[str] = set()
    unassigned = [t for t, _ in sorted_tasks]

    while unassigned:
        station: List[str] = []
        station_time = 0.0
        progress = True

        while progress:
            progress = False
            for task in unassigned:
                if task in station:
                    continue
                t_time = tasks[task]
                if (
                    station_time + t_time <= takt
                    and _predecessors_satisfied(task, assigned | set(station), precedences)
                ):
                    station.append(task)
                    station_time += t_time
                    progress = True
                    break  # reiniciar búsqueda desde el principio

        if not station:
            # Forzar asignación de la primera tarea factible (aunque supere takt)
            for task in unassigned:
                if _predecessors_satisfied(task, assigned, precedences):
                    station.append(task)
                    break
            if not station:
                # Sin candidatos viables: tomar la primera sin importar precedencias
                station.append(unassigned[0])

        for t in station:
            assigned.add(t)
            unassigned.remove(t)

        stations.append(station)

    return stations


# ─── ALGORITMO 2: RANKED POSITIONAL WEIGHT (RPW) ─────────────────────────────

def compute_positional_weights(
    tasks: Dict[str, float],
    precedences: List[Tuple[str, str]],
) -> Dict[str, float]:
    """
    Calcula el Peso Posicional de cada tarea:
    RPW(task) = tiempo(task) + Σ tiempos de todos sus sucesores.
    """
    weights: Dict[str, float] = {}
    for task, t_time in tasks.items():
        suc = _successors(task, precedences)
        weights[task] = t_time + sum(tasks.get(s, 0.0) for s in suc)
    return weights


def ranked_positional_weight(
    tasks: Dict[str, float],
    precedences: List[Tuple[str, str]],
    takt: float,
) -> List[List[str]]:
    """
    RPW — Ordena tareas por peso posicional descendente y las asigna a
    estaciones respetando Takt Time y precedencias.

    Retorna lista de estaciones, cada una con sus tareas asignadas.
    """
    if takt <= 0:
        return []

    weights = compute_positional_weights(tasks, precedences)
    sorted_tasks = sorted(tasks.keys(), key=lambda t: weights[t], reverse=True)

    stations: List[List[str]] = []
    assigned: set[str] = set()
    unassigned = list(sorted_tasks)

    while unassigned:
        station: List[str] = []
        station_time = 0.0
        progress = True

        while progress:
            progress = False
            for task in unassigned:
                if task in station:
                    continue
                t_time = tasks[task]
                if (
                    station_time + t_time <= takt
                    and _predecessors_satisfied(task, assigned | set(station), precedences)
                ):
                    station.append(task)
                    station_time += t_time
                    progress = True
                    break

        if not station:
            for task in unassigned:
                if _predecessors_satisfied(task, assigned, precedences):
                    station.append(task)
                    break
            if not station:
                station.append(unassigned[0])

        for t in station:
            assigned.add(t)
            unassigned.remove(t)

        stations.append(station)

    return stations


# ─── MÉTRICAS DE BALANCEO ─────────────────────────────────────────────────────

def balance_metrics(
    stations: List[List[str]],
    tasks: Dict[str, float],
    takt: float,
) -> Dict:
    """
    Calcula métricas clave del balanceo de línea.

    Retorna:
        n_stations   — Número de estaciones usadas
        n_min        — Número teórico mínimo  N* = Σti / Takt
        efficiency   — η = Σti / (N * Takt)  en %
        smoothness   — SI = sqrt(Σ(Takt - ti_station)^2)
        idle_pct     — % de tiempo ocioso total
        station_data — lista de dicts por estación con nombre, tareas, carga, idle
    """
    if not stations or takt <= 0:
        return {}

    total_task_time = sum(tasks.values())
    n_stations = len(stations)
    n_min = math.ceil(total_task_time / takt)

    station_data = []
    for idx, station_tasks in enumerate(stations):
        load = sum(tasks.get(t, 0.0) for t in station_tasks)
        idle = max(0.0, takt - load)
        station_data.append({
            "Estación": f"E{idx + 1}",
            "Tareas": ", ".join(station_tasks),
            "Carga (s)": round(load, 2),
            "Idle (s)": round(idle, 2),
            "% Utilización": round((load / takt) * 100, 1),
        })

    total_cycle = n_stations * takt
    efficiency = round((total_task_time / total_cycle) * 100, 1)
    smoothness = round(
        math.sqrt(sum((takt - s["Carga (s)"]) ** 2 for s in station_data)), 2
    )
    idle_pct = round(((total_cycle - total_task_time) / total_cycle) * 100, 1)

    return {
        "n_stations": n_stations,
        "n_min": n_min,
        "efficiency": efficiency,
        "smoothness": smoothness,
        "idle_pct": idle_pct,
        "total_task_time": round(total_task_time, 2),
        "station_data": station_data,
    }


# ─── EXPORTAR COMO CONFIG DE ESTACIONES ──────────────────────────────────────

def stations_to_config(
    stations: List[List[str]],
    tasks: Dict[str, float],
    default_var: int = 3,
) -> Dict[str, Dict]:
    """
    Convierte el resultado del balanceo al formato de estaciones del simulador.
    Cada estación recibe el tiempo de ciclo = suma de sus tareas.

    Retorna dict compatible con config['estaciones'].
    """
    config_est = {}
    for idx, station_tasks in enumerate(stations):
        name = f"Estación {idx + 1}"
        ciclo = round(sum(tasks.get(t, 0.0) for t in station_tasks))
        config_est[name] = {"ciclo": max(5, ciclo), "var": default_var}
    return config_est


# ─── DATOS PARA DIAGRAMA DE PRECEDENCIAS ─────────────────────────────────────

def build_precedence_positions(
    tasks: Dict[str, float],
    precedences: List[Tuple[str, str]],
) -> Dict[str, Tuple[float, float]]:
    """
    Asigna coordenadas (x, y) a cada tarea para graficar el diagrama de
    precedencias. Usa topological sort para calcular niveles (columnas).

    Retorna dict {tarea: (x, y)}.
    """
    # Calcular nivel (profundidad desde el inicio) de cada tarea
    levels: Dict[str, int] = {t: 0 for t in tasks}
    changed = True
    while changed:
        changed = False
        for pred, suc in precedences:
            if levels[suc] <= levels[pred]:
                levels[suc] = levels[pred] + 1
                changed = True

    # Agrupar tareas por nivel
    from collections import defaultdict
    level_groups: Dict[int, List[str]] = defaultdict(list)
    for task, lvl in levels.items():
        level_groups[lvl].append(task)

    # Asignar coordenadas
    positions: Dict[str, Tuple[float, float]] = {}
    for lvl, group in level_groups.items():
        n = len(group)
        for i, task in enumerate(sorted(group)):
            y = (i - (n - 1) / 2) * 1.5
            positions[task] = (float(lvl) * 2.0, y)

    return positions


# ─── OPERADORES POR ESTACIÓN ──────────────────────────────────────────────────

def assign_operators(
    stations: List[List[str]],
    tasks: Dict[str, float],
    takt: float,
    current_operators: int = 0,
) -> Dict:
    """
    Calcula los operadores óptimos por estación y el total mínimo.

    Lógica:
      · Operadores por estación = ceil(carga_estación / takt)
        (si una estación carga 45s y takt=30s → necesita 2 operadores)
      · Operador mínimo total = Σ operadores por estación
      · Si current_operators > 0, calcula el ahorro potencial

    Retorna dict con:
      station_ops   — lista de dicts por estación con ops asignados
      total_min_ops — total mínimo de operadores
      saving        — operadores que se pueden eliminar vs actual
      saving_pct    — % de reducción
    """
    if not stations or takt <= 0:
        return {}

    station_ops = []
    total_min = 0

    for idx, st_tasks in enumerate(stations):
        load = sum(tasks.get(t, 0.0) for t in st_tasks)
        ops  = math.ceil(load / takt) if load > 0 else 1
        total_min += ops
        util_per_op = round((load / (ops * takt)) * 100, 1)
        station_ops.append({
            "Estación":       f"E{idx + 1}",
            "Tareas":         ", ".join(st_tasks),
            "Carga (s)":      round(load, 2),
            "Operadores":     ops,
            "% Util./Op.":    util_per_op,
        })

    saving      = max(0, current_operators - total_min) if current_operators > 0 else None
    saving_pct  = round((saving / current_operators) * 100, 1) if saving and current_operators > 0 else None

    return {
        "station_ops":    station_ops,
        "total_min_ops":  total_min,
        "current_ops":    current_operators,
        "saving":         saving,
        "saving_pct":     saving_pct,
    }


def operator_balance_chart_data(
    station_ops: List[Dict],
    takt: float,
) -> Dict:
    """
    Devuelve datos listos para graficar carga vs capacidad de operadores.
    Capacidad de operadores = operadores × takt.
    """
    names     = [s["Estación"] for s in station_ops]
    loads     = [s["Carga (s)"] for s in station_ops]
    ops       = [s["Operadores"] for s in station_ops]
    capacity  = [o * takt for o in ops]
    slack     = [max(0.0, c - l) for c, l in zip(capacity, loads)]
    return {"names": names, "loads": loads, "capacity": capacity,
            "slack": slack, "ops": ops}

