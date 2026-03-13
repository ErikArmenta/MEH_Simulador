# simulator.py — Motor SimPy corregido
# Desarrollado por Master Engineer Erik Armenta

import simpy
import random
import pandas as pd
import numpy as np


class Workstation:
    def __init__(self, env, name, ciclo, sigma, mtbf, mttr, kanban_cap):
        self.env      = env
        self.name     = name
        self.ciclo    = ciclo
        self.sigma    = sigma
        self.mtbf     = mtbf
        self.mttr     = mttr
        # Resource con capacity=kanban_cap limita piezas simultáneas en esta estación
        self.machine  = simpy.Resource(env, capacity=kanban_cap)
        self.stats    = []
        self.busy_time  = 0.0
        self.down_time  = 0.0
        self.broken   = False

        if mtbf > 0:
            env.process(self._break_machine())

    def _break_machine(self):
        while True:
            yield self.env.timeout(random.expovariate(1.0 / self.mtbf))
            if self.broken:
                continue
            self.broken = True
            repair = max(1.0, random.normalvariate(self.mttr, self.mttr * 0.15))
            self.down_time += repair
            self.stats.append({
                "ID": "PARO", "Estacion": self.name,
                "Espera": 0.0, "Inicio": round(self.env.now, 2),
                "Proceso": round(repair, 2),
                "Salida": round(self.env.now + repair, 2),
                "Tipo": "Downtime"
            })
            yield self.env.timeout(repair)
            self.broken = False

    def process(self, part_id, arrival_time):
        """Procesa una pieza. Usa request()/release() correctamente."""
        with self.machine.request() as req:
            yield req  # espera a que haya capacidad (Kanban)

            # Si la máquina está en paro, esperar en incrementos pequeños
            while self.broken:
                yield self.env.timeout(0.5)

            wait = round(self.env.now - arrival_time, 2)
            t    = max(0.1, random.normalvariate(self.ciclo, self.sigma))
            t0   = self.env.now
            yield self.env.timeout(t)
            self.busy_time += t

            self.stats.append({
                "ID":       f"P-{part_id:04d}",
                "Estacion": self.name,
                "Espera":   wait,
                "Inicio":   round(t0, 2),
                "Proceso":  round(t, 2),
                "Salida":   round(self.env.now, 2),
                "Tipo":     "Producción"
            })
        # Al salir del with, request se libera automáticamente → Kanban libera un slot


def _part_flow(env, part_id, workstations, results, lead_times):
    """Una pieza recorre todas las estaciones en secuencia."""
    t0 = env.now
    for ws in workstations:
        arrival = env.now
        yield env.process(ws.process(part_id, arrival))
    lead_times.append(round(env.now - t0, 2))
    results.append(part_id)


def _arrivals(env, n, workstations, takt, results, lead_times):
    """Lanza piezas al sistema con intervalos aleatorios."""
    interval = max(1.0, takt * 0.85)
    for i in range(n):
        env.process(_part_flow(env, i, workstations, results, lead_times))
        yield env.timeout(random.expovariate(1.0 / interval))


def run_simulation(config):
    """
    Ejecuta la simulación completa y retorna resultados.
    Sin deadlock: usa simpy.Resource con request()/release() — API correcta de SimPy.
    """
    random.seed(None)
    env = simpy.Environment()

    kanban_cap = max(1, config['kanban'])

    workstations = []
    for name, p in config['estaciones'].items():
        ws = Workstation(
            env, name,
            ciclo=p['ciclo'], sigma=p['var'],
            mtbf=config['mtbf'], mttr=config['mttr'],
            kanban_cap=kanban_cap
        )
        workstations.append(ws)

    results, lead_times = [], []
    env.process(_arrivals(env, config['piezas'], workstations,
                          config['takt'], results, lead_times))

    # Timeout de seguridad: la simulación SIEMPRE termina
    limite = config['piezas'] * (
        sum(p['ciclo'] for p in config['estaciones'].values()) + config['mttr']
    ) * 5
    env.run(until=limite)

    # ── Ensamblar datos ──────────────────────────────────────────────────────
    all_stats = []
    for ws in workstations:
        all_stats.extend(ws.stats)

    if not all_stats:
        return None

    df_total = pd.DataFrame(all_stats)
    df_prod  = df_total[df_total['Tipo'] == 'Producción'].copy()
    df_fail  = df_total[df_total['Tipo'] == 'Downtime'].copy()

    t_final  = df_total['Salida'].max()
    unidades = len(results)

    if t_final <= 0 or unidades == 0:
        return None

    # ── KPIs ────────────────────────────────────────────────────────────────
    throughput     = round((unidades / t_final) * 3600, 1)
    ciclo_prom     = round(float(np.mean(lead_times)), 2) if lead_times else 0
    total_down     = float(df_fail['Proceso'].sum()) if not df_fail.empty else 0
    disponibilidad = round(((t_final - total_down) / t_final) * 100, 1)
    util_data      = {ws.name: round((ws.busy_time / t_final) * 100, 1) for ws in workstations}
    rendimiento    = round(min(100.0, (ciclo_prom / max(1, config['takt'])) * 100), 1)
    calidad        = 98.5
    oee            = round((disponibilidad/100) * (rendimiento/100) * (calidad/100) * 100, 1)

    bottleneck_df = (df_prod.groupby("Estacion")["Espera"]
                     .mean().reset_index()
                     .rename(columns={"Espera": "Espera_Prom"})
                     .round(2))

    ciclo_est_df = (df_prod.groupby("Estacion")["Proceso"]
                   .agg(['mean', 'std', 'min', 'max']).reset_index()
                   .rename(columns={"mean":"Promedio","std":"Std","min":"Min","max":"Max"})
                   .round(2))

    # WIP log
    wip_rows = []
    for ws in workstations:
        for s in ws.stats:
            if s['Tipo'] == 'Producción':
                wip_rows += [
                    {"time": s['Inicio'], "delta":  1, "estacion": ws.name},
                    {"time": s['Salida'], "delta": -1, "estacion": ws.name},
                ]
    df_wip = pd.DataFrame(wip_rows) if wip_rows else pd.DataFrame()

    return {
        "df_total":       df_total,
        "df_prod":        df_prod,
        "df_fail":        df_fail,
        "df_wip":         df_wip,
        "bottleneck_df":  bottleneck_df,
        "ciclo_est_df":   ciclo_est_df,
        "lead_times":     lead_times,
        "kpis": {
            "unidades":       unidades,
            "throughput":     throughput,
            "ciclo_promedio": ciclo_prom,
            "disponibilidad": disponibilidad,
            "util_data":      util_data,
            "oee":            oee,
            "rendimiento":    rendimiento,
            "calidad":        calidad,
            "t_final":        round(t_final, 1),
            "total_fallas":   len(df_fail),
        },
        "estaciones_names": [ws.name for ws in workstations],
    }