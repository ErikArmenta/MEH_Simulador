# simulator.py — Motor SimPy corregido
# Desarrollado por Master Engineer Erik Armenta
# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENTACIÓN ARQUITECTÓNICA - ANÁLISIS PROFUNDO
# ══════════════════════════════════════════════════════════════════════════════
#
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │                    MOTOR DE SIMULACIÓN DISCRETA SimPy                       │
# │                   Simulador de Línea de Manufactura MEH                     │
# └─────────────────────────────────────────────────────────────────────────────┘
#
# PROPÓSITO:
#   Este módulo implementa el núcleo de simulación de eventos discretos para
#   una línea de manufactura utilizando SimPy. Modela el flujo de piezas a
#   través de múltiples estaciones de trabajo con variabilidad estocástica,
#   fallas de máquina (MTBF/MTTR), y control de inventario Kanban.
#
# ══════════════════════════════════════════════════════════════════════════════
# ARQUITECTURA DEL MOTOR DE SIMULACIÓN
# ══════════════════════════════════════════════════════════════════════════════
#
#   ┌─────────────────────────────────────────────────────────────────────────┐
#   │                         FLUJO DE SIMULACIÓN                             │
#   ├─────────────────────────────────────────────────────────────────────────┤
#   │                                                                         │
#   │   run_simulation(config)                                                │
#   │          │                                                              │
#   │          ▼                                                              │
#   │   ┌─────────────────┐                                                   │
#   │   │ simpy.Environment │  ◄── Kernel de eventos discretos               │
#   │   └────────┬────────┘                                                   │
#   │            │                                                            │
#   │            ▼                                                            │
#   │   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐  │
#   │   │   Workstation   │────▶│   Workstation   │────▶│   Workstation   │  │
#   │   │   (Estación 1)  │     │   (Estación 2)  │     │   (Estación N)  │  │
#   │   │                 │     │                 │     │                 │  │
#   │   │ ┌─────────────┐ │     │ ┌─────────────┐ │     │ ┌─────────────┐ │  │
#   │   │ │simpy.Resource│ │     │ │simpy.Resource│ │     │ │simpy.Resource│ │  │
#   │   │ │(Kanban Cap) │ │     │ │(Kanban Cap) │ │     │ │(Kanban Cap) │ │  │
#   │   │ └─────────────┘ │     │ └─────────────┘ │     │ └─────────────┘ │  │
#   │   └─────────────────┘     └─────────────────┘     └─────────────────┘  │
#   │            │                      │                      │             │
#   │            └──────────────────────┼──────────────────────┘             │
#   │                                   ▼                                     │
#   │                        ┌─────────────────┐                              │
#   │                        │   _part_flow()  │  ◄── Proceso por pieza      │
#   │                        └─────────────────┘                              │
#   │                                   │                                     │
#   │                                   ▼                                     │
#   │                        ┌─────────────────┐                              │
#   │                        │   _arrivals()   │  ◄── Generador de llegadas  │
#   │                        └─────────────────┘                              │
#   │                                                                         │
#   └─────────────────────────────────────────────────────────────────────────┘
#
# ══════════════════════════════════════════════════════════════════════════════
# COMPONENTES PRINCIPALES
# ══════════════════════════════════════════════════════════════════════════════
#
# 1. CLASE WORKSTATION:
#    ├── Representa una estación de trabajo física en la línea
#    ├── Encapsula: ciclo de proceso, variabilidad (sigma), MTBF, MTTR
#    ├── simpy.Resource: Control de capacidad Kanban (WIP limitado)
#    ├── _break_machine(): Proceso paralelo de fallas aleatorias
#    └── process(): Procesa piezas con tiempos estocásticos
#
# 2. CONTROL KANBAN (simpy.Resource):
#    ├── Limita piezas simultáneas por estación (kanban_cap)
#    ├── request(): Pieza solicita "tarjeta Kanban" para entrar
#    ├── release(): Al salir, libera slot para siguiente pieza
#    └── Previene acumulación excesiva de WIP
#
# 3. MODELO DE FALLAS (MTBF/MTTR):
#    ├── MTBF (Mean Time Between Failures): Tiempo promedio entre fallas
#    │   └── Distribución exponencial: random.expovariate(1/MTBF)
#    ├── MTTR (Mean Time To Repair): Tiempo promedio de reparación
#    │   └── Distribución normal: normalvariate(MTTR, MTTR*0.15)
#    └── Flag 'broken': Bloquea proceso mientras máquina está en paro
#
# 4. VARIABILIDAD DE PROCESO:
#    ├── Tiempo de ciclo: normalvariate(ciclo, sigma)
#    ├── Llegadas: expovariate(1/interval) - Proceso de Poisson
#    └── Mínimos garantizados para evitar tiempos negativos
#
# ══════════════════════════════════════════════════════════════════════════════
# CÁLCULO DE KPIs (KEY PERFORMANCE INDICATORS)
# ══════════════════════════════════════════════════════════════════════════════
#
# ┌────────────────────┬────────────────────────────────────────────────────────┐
# │ KPI                │ FÓRMULA                                                │
# ├────────────────────┼────────────────────────────────────────────────────────┤
# │ Throughput         │ (unidades_completadas / tiempo_final) × 3600 piezas/h │
# │ Ciclo Promedio     │ mean(lead_times) - Tiempo total por pieza             │
# │ Disponibilidad     │ ((t_final - downtime) / t_final) × 100%               │
# │ Utilización        │ (busy_time / t_final) × 100% por estación             │
# │ Rendimiento        │ (ciclo_promedio / takt) × 100%                        │
# │ Calidad            │ (piezas_buenas / piezas_totales) × 100% (real)        │
# │ Scrap Rate         │ (piezas_scrap / piezas_totales) × 100%                │
# │ OEE                │ Disponibilidad × Rendimiento × Calidad                │
# └────────────────────┴────────────────────────────────────────────────────────┘
#
# ══════════════════════════════════════════════════════════════════════════════
# ESTRUCTURAS DE DATOS DE SALIDA
# ══════════════════════════════════════════════════════════════════════════════
#
# El diccionario de retorno incluye:
#   - df_total:      DataFrame con TODOS los eventos (producción + downtime)
#   - df_prod:       DataFrame filtrado solo eventos de producción
#   - df_fail:       DataFrame filtrado solo eventos de downtime
#   - df_wip:        DataFrame para gráfico de WIP en tiempo
#   - bottleneck_df: Tiempo de espera promedio por estación (cuellos de botella)
#   - ciclo_est_df:  Estadísticas de ciclo por estación (mean, std, min, max)
#   - lead_times:    Lista de tiempos totales por pieza
#   - kpis:          Diccionario con todos los indicadores calculados
#
# ══════════════════════════════════════════════════════════════════════════════
# CONSIDERACIONES DE DISEÑO
# ══════════════════════════════════════════════════════════════════════════════
#
# 1. PREVENCIÓN DE DEADLOCK:
#    - Uso correcto de context manager (with request)
#    - Timeout de seguridad: límite = piezas × (suma_ciclos + mttr) × 5
#    - Verificación de broken flag con polling (yield timeout 0.5)
#
# 2. REPRODUCIBILIDAD:
#    - random.seed(None) por defecto para variabilidad real
#    - Parámetro 'seed' configurable: si es número, resultados reproducibles
#    - Útil para debugging, comparación de escenarios, y pruebas automatizadas
#
# 3. ROBUSTEZ:
#    - Manejo de casos edge: df vacío, t_final=0, unidades=0
#    - Mínimos garantizados: max(0.1, tiempo), max(1.0, intervalo)
#
# ══════════════════════════════════════════════════════════════════════════════

import simpy
import random
import pandas as pd
import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
# CLASE WORKSTATION - Estación de Trabajo
# ══════════════════════════════════════════════════════════════════════════════
# Modela una estación física de la línea de producción con:
# - Tiempo de ciclo con variabilidad normal (ciclo ± sigma)
# - Control de capacidad Kanban via simpy.Resource
# - Proceso de fallas paralelo (MTBF/MTTR)
# - Registro de estadísticas para análisis posterior
# ══════════════════════════════════════════════════════════════════════════════

class Workstation:
    def __init__(self, env, name, ciclo, sigma, mtbf, mttr, kanban_cap, idle_factor=0.0, defect_rate=0.0):
        self.env      = env
        self.name     = name
        self.ciclo    = ciclo
        self.sigma    = sigma
        self.mtbf     = mtbf
        self.mttr     = mttr
        self.idle_factor = idle_factor  # Factor de tiempo muerto (0.0 - 0.15 = 0% - 15%)
        self.defect_rate = defect_rate  # Tasa de defectos/scrap (0.0 - 0.10 = 0% - 10%)
        # Resource con capacity=kanban_cap limita piezas simultáneas en esta estación
        self.machine  = simpy.Resource(env, capacity=kanban_cap)
        self.stats    = []
        self.busy_time  = 0.0
        self.down_time  = 0.0
        self.idle_time  = 0.0  # Tiempo muerto acumulado (cambios herramienta, microparos)
        self.scrap_count = 0   # Contador de piezas defectuosas/scrap
        self.good_count  = 0   # Contador de piezas buenas
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

    def _idle_events(self):
        """
        Genera tiempo muerto aleatorio usando distribución exponencial.

        Simula eventos de tiempo muerto comunes en manufactura:
        - Cambios de herramienta (tool changeovers)
        - Esperas de material (material waiting)
        - Microparos (micro-stops < 5 min)
        - Ajustes menores (minor adjustments)
        - Limpieza rápida (quick cleaning)

        Returns:
            float: Tiempo de idle en segundos (0 si idle_factor <= 0)

        Distribución:
            Exponencial con media = ciclo * idle_factor
            Esto genera tiempos mayoritariamente cortos con ocasionales más largos,
            reflejando el patrón real de microparos en planta.
        """
        if self.idle_factor <= 0:
            return 0.0

        # Media del tiempo muerto basada en el ciclo de la estación
        # idle_factor de 0.10 = 10% del ciclo en promedio como tiempo muerto
        mean_idle = self.ciclo * self.idle_factor

        # Distribución exponencial: mayoría cortos, algunos largos
        # Probabilidad de 63% de estar bajo la media, 37% sobre ella
        idle_time = random.expovariate(1.0 / mean_idle) if mean_idle > 0 else 0.0

        # Cap máximo: no más del 50% del ciclo para evitar valores extremos
        max_idle = self.ciclo * 0.5
        idle_time = min(idle_time, max_idle)

        return max(0.0, idle_time)

    def process(self, part_id, arrival_time):
        """
        Procesa una pieza con tiempo muerto aleatorio.
        Usa request()/release() correctamente para control Kanban.

        El proceso incluye:
        1. Espera por capacidad Kanban (request)
        2. Espera si máquina en paro (broken)
        3. Tiempo de proceso con variabilidad normal
        4. Tiempo muerto aleatorio (idle_events)

        Args:
            part_id: Identificador único de la pieza
            arrival_time: Momento de llegada a la estación
        """
        with self.machine.request() as req:
            yield req  # espera a que haya capacidad (Kanban)

            # Si la máquina está en paro, esperar en incrementos pequeños
            while self.broken:
                yield self.env.timeout(0.5)

            wait = round(self.env.now - arrival_time, 2)
            t0   = self.env.now

            # ── Tiempo de proceso con variabilidad ──────────────────────────
            t_proceso = max(0.1, random.normalvariate(self.ciclo, self.sigma))
            yield self.env.timeout(t_proceso)
            self.busy_time += t_proceso

            # ── Tiempo muerto aleatorio (idle) ──────────────────────────────
            # Simula: cambios de herramienta, esperas de material, microparos
            t_idle = self._idle_events()
            if t_idle > 0:
                yield self.env.timeout(t_idle)
                self.idle_time += t_idle
                # Registrar evento de idle si es significativo (> 0.5 seg)
                if t_idle > 0.5:
                    self.stats.append({
                        "ID":       f"P-{part_id:04d}",
                        "Estacion": self.name,
                        "Espera":   0.0,
                        "Inicio":   round(self.env.now - t_idle, 2),
                        "Proceso":  round(t_idle, 2),
                        "Salida":   round(self.env.now, 2),
                        "Tipo":     "Idle"
                    })

            # Tiempo total = proceso + idle
            t_total = t_proceso + t_idle

            # ── Verificación de Scrap/Defectos ────────────────────────────────
            # Simula inspección de calidad: si random < defect_rate, pieza es scrap
            # Causas típicas en manufactura:
            # - Defectos dimensionales (fuera de tolerancia)
            # - Defectos superficiales (rayaduras, golpes)
            # - Defectos de material (porosidad, inclusiones)
            # - Errores de ensamble (componentes mal colocados)
            is_scrap = random.random() < self.defect_rate

            if is_scrap:
                self.scrap_count += 1
                self.stats.append({
                    "ID":       f"P-{part_id:04d}",
                    "Estacion": self.name,
                    "Espera":   wait,
                    "Inicio":   round(t0, 2),
                    "Proceso":  round(t_proceso, 2),
                    "Salida":   round(self.env.now, 2),
                    "Tipo":     "Scrap",
                    "Idle":     round(t_idle, 2),
                    "Defecto":  True
                })
            else:
                self.good_count += 1
                self.stats.append({
                    "ID":       f"P-{part_id:04d}",
                    "Estacion": self.name,
                    "Espera":   wait,
                    "Inicio":   round(t0, 2),
                    "Proceso":  round(t_proceso, 2),
                    "Salida":   round(self.env.now, 2),
                    "Tipo":     "Producción",
                    "Idle":     round(t_idle, 2),
                    "Defecto":  False
                })
        # Al salir del with, request se libera automáticamente → Kanban libera un slot


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN _part_flow - Flujo de Pieza Individual
# ══════════════════════════════════════════════════════════════════════════════
# Proceso SimPy que modela el recorrido de una pieza a través de TODAS las
# estaciones de trabajo en secuencia. Registra lead time total.
#
# Flujo: Pieza → Estación1 → Estación2 → ... → EstaciónN → Completada
# ══════════════════════════════════════════════════════════════════════════════

def _part_flow(env, part_id, workstations, results, lead_times):
    """
    Una pieza recorre todas las estaciones en secuencia.

    Args:
        env: Ambiente SimPy
        part_id: Identificador único de la pieza
        workstations: Lista ordenada de estaciones de trabajo
        results: Lista donde se agregan piezas completadas
        lead_times: Lista donde se registran tiempos totales

    Yields:
        Procesos de cada estación en secuencia
    """
    t0 = env.now
    for ws in workstations:
        arrival = env.now
        yield env.process(ws.process(part_id, arrival))
    lead_times.append(round(env.now - t0, 2))
    results.append(part_id)


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN _arrivals - Generador de Llegadas
# ══════════════════════════════════════════════════════════════════════════════
# Implementa un proceso de Poisson para la llegada de piezas al sistema.
# El intervalo entre llegadas sigue distribución exponencial basada en takt time.
#
# Distribución: Exponencial con λ = 1 / (takt × 0.85)
# Esto simula variabilidad real en llegada de material/órdenes
# ══════════════════════════════════════════════════════════════════════════════

def _arrivals(env, n, workstations, takt, results, lead_times):
    """
    Lanza piezas al sistema con intervalos aleatorios (proceso de Poisson).

    Args:
        env: Ambiente SimPy
        n: Número total de piezas a simular
        workstations: Lista de estaciones de trabajo
        takt: Takt time objetivo (segundos)
        results: Lista para piezas completadas
        lead_times: Lista para tiempos de ciclo

    Yields:
        Timeouts entre llegadas de piezas
    """
    interval = max(1.0, takt * 0.85)
    for i in range(n):
        env.process(_part_flow(env, i, workstations, results, lead_times))
        yield env.timeout(random.expovariate(1.0 / interval))


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN run_simulation - PUNTO DE ENTRADA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
# Orquesta la simulación completa de la línea de manufactura:
#
# 1. INICIALIZACIÓN:
#    - Crea ambiente SimPy (kernel de eventos discretos)
#    - Instancia todas las estaciones de trabajo
#    - Configura capacidad Kanban por estación
#
# 2. EJECUCIÓN:
#    - Lanza proceso de llegadas (_arrivals)
#    - Ejecuta hasta timeout de seguridad
#    - Cada estación procesa piezas con fallas aleatorias
#
# 3. POST-PROCESAMIENTO:
#    - Ensambla estadísticas de todas las estaciones
#    - Calcula KPIs (OEE, throughput, disponibilidad, etc.)
#    - Genera DataFrames para visualización
#
# PARÁMETROS DE CONFIG ESPERADOS:
#   config = {
#       'piezas': int,           # Número de piezas a simular
#       'takt': float,           # Takt time objetivo (segundos)
#       'kanban': int,           # Capacidad Kanban por estación
#       'mtbf': float,           # Mean Time Between Failures (segundos)
#       'mttr': float,           # Mean Time To Repair (segundos)
#       'idle_factor': float,    # Factor de tiempo muerto (0.0-0.15) [opcional]
#       'defect_rate': float,    # Tasa de defectos/scrap (0.0-0.10) [opcional]
#       'seed': int|None,        # Semilla para reproducibilidad [opcional]
#       'estaciones': {          # Diccionario de estaciones
#           'nombre': {
#               'ciclo': float,  # Tiempo de ciclo (segundos)
#               'var': float,    # Desviación estándar (sigma)
#           },
#           ...
#       }
#   }
# ══════════════════════════════════════════════════════════════════════════════

def run_simulation(config):
    """
    Ejecuta la simulación completa y retorna resultados.
    Sin deadlock: usa simpy.Resource con request()/release() — API correcta de SimPy.

    Args:
        config: Diccionario con parámetros de simulación
            - seed (int|None): Semilla para reproducibilidad. Si es None, cada
              corrida produce resultados diferentes. Si es un número entero,
              la misma semilla produce resultados idénticos (útil para debugging,
              comparación de escenarios, y pruebas automatizadas).

    Returns:
        dict: Resultados completos incluyendo DataFrames y KPIs
        None: Si la simulación no produce resultados válidos
    """
    # ── SEMILLA PARA REPRODUCIBILIDAD ────────────────────────────────────────
    # seed=None: Variabilidad real en cada corrida (comportamiento por defecto)
    # seed=<int>: Resultados reproducibles (misma semilla = mismos resultados)
    # Útil para: debugging, comparación de escenarios A/B, pruebas unitarias
    seed = config.get('seed', None)
    random.seed(seed)

    env = simpy.Environment()

    # ── CONFIGURACIÓN KANBAN ────────────────────────────────────────────────
    # Mínimo de 1 para evitar bloqueo total del sistema
    kanban_cap = max(1, config['kanban'])

    # ── CONFIGURACIÓN IDLE FACTOR ──────────────────────────────────────────
    # Factor de tiempo muerto (0.0 - 0.15 = 0% - 15%)
    # Simula microparos, cambios de herramienta, esperas de material
    idle_factor = config.get('idle_factor', 0.0)

    # ── CONFIGURACIÓN DEFECT RATE ──────────────────────────────────────────
    # Tasa de defectos/scrap (0.0 - 0.10 = 0% - 10%)
    # Simula piezas defectuosas que no pasan inspección de calidad
    defect_rate = config.get('defect_rate', 0.0)

    # ── CREACIÓN DE ESTACIONES ────────────────────────────────────────────────
    # Cada estación es un proceso independiente con su propia cola Kanban
    workstations = []
    for name, p in config['estaciones'].items():
        ws = Workstation(
            env, name,
            ciclo=p['ciclo'], sigma=p['var'],
            mtbf=config['mtbf'], mttr=config['mttr'],
            kanban_cap=kanban_cap,
            idle_factor=idle_factor,
            defect_rate=defect_rate
        )
        workstations.append(ws)

    # ── LANZAMIENTO DE SIMULACIÓN ───────────────────────────────────────────
    # Inicializa listas para resultados y arranca el proceso de llegadas
    results, lead_times = [], []
    env.process(_arrivals(env, config['piezas'], workstations,
                          config['takt'], results, lead_times))

    # ── TIMEOUT DE SEGURIDAD ──────────────────────────────────────────────────
    # Fórmula: piezas × (suma_ciclos + mttr) × 5
    # Factor de 5x garantiza que incluso con fallas extremas, la simulación termina
    # Previene deadlocks infinitos sin afectar operación normal
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
    df_scrap = df_total[df_total['Tipo'] == 'Scrap'].copy()  # Eventos de scrap

    t_final  = df_total['Salida'].max()
    unidades = len(results)

    if t_final <= 0 or unidades == 0:
        return None

    # ── CÁLCULO DE KPIs ─────────────────────────────────────────────────────
    # Throughput: Piezas por hora = (unidades/tiempo_seg) × 3600
    throughput     = round((unidades / t_final) * 3600, 1)

    # Ciclo Promedio: Media de lead times (tiempo total por pieza)
    ciclo_prom     = round(float(np.mean(lead_times)), 2) if lead_times else 0

    # ── Tiempo Idle Total ───────────────────────────────────────────────────
    # Suma de todos los tiempos muertos de todas las estaciones
    total_idle     = sum(ws.idle_time for ws in workstations)
    idle_pct       = round((total_idle / t_final) * 100, 2) if t_final > 0 else 0

    # ── Conteo de Scrap y Calidad Real ──────────────────────────────────────
    # Suma de todas las piezas scrap y buenas de todas las estaciones
    total_scrap    = sum(ws.scrap_count for ws in workstations)
    total_good     = sum(ws.good_count for ws in workstations)
    total_produced = total_scrap + total_good

    # Calidad Real: % de piezas conformes basado en producción real
    # Fórmula: (piezas_buenas / piezas_totales) × 100
    # Si no hay producción, usar 100% (sin defectos)
    if total_produced > 0:
        calidad = round((total_good / total_produced) * 100, 1)
    else:
        calidad = 100.0

    # Tasa de scrap: % de piezas defectuosas
    scrap_rate = round((total_scrap / total_produced) * 100, 2) if total_produced > 0 else 0.0

    # Disponibilidad: % de tiempo que la línea estuvo operativa
    # Fórmula: ((tiempo_total - tiempo_paros - tiempo_idle) / tiempo_total) × 100
    # NOTA: El idle afecta disponibilidad efectiva pero se reporta separado
    total_down     = float(df_fail['Proceso'].sum()) if not df_fail.empty else 0
    disponibilidad = round(((t_final - total_down) / t_final) * 100, 1)

    # Utilización por Estación: % de tiempo que cada estación estuvo procesando
    util_data      = {ws.name: round((ws.busy_time / t_final) * 100, 1) for ws in workstations}

    # Rendimiento: Relación ciclo real vs takt objetivo (capped a 100%)
    rendimiento    = round(min(100.0, (ciclo_prom / max(1, config['takt'])) * 100), 1)

    # OEE (Overall Equipment Effectiveness): Métrica compuesta de manufactura
    # OEE = Disponibilidad × Rendimiento × Calidad
    # World-class: >85%, Típico: 60%, Bajo: <40%
    oee            = round((disponibilidad/100) * (rendimiento/100) * (calidad/100) * 100, 1)

    # ── ANÁLISIS DE CUELLOS DE BOTELLA ──────────────────────────────────────
    # Estación con mayor tiempo de espera promedio = cuello de botella
    # La espera indica acumulación de WIP antes de esa estación
    bottleneck_df = (df_prod.groupby("Estacion")["Espera"]
                     .mean().reset_index()
                     .rename(columns={"Espera": "Espera_Prom"})
                     .round(2))

    # ── ESTADÍSTICAS DE CICLO POR ESTACIÓN ────────────────────────────────────
    # Útil para identificar variabilidad excesiva (std alto) o outliers
    ciclo_est_df = (df_prod.groupby("Estacion")["Proceso"]
                   .agg(['mean', 'std', 'min', 'max']).reset_index()
                   .rename(columns={"mean":"Promedio","std":"Std","min":"Min","max":"Max"})
                   .round(2))

    # ── REGISTRO DE WIP (Work In Progress) ────────────────────────────────────
    # Construye serie temporal de WIP para gráficos de evolución
    # delta +1 cuando pieza ENTRA a estación, -1 cuando SALE
    # Permite visualizar acumulación de inventario en tiempo
    wip_rows = []
    for ws in workstations:
        for s in ws.stats:
            if s['Tipo'] == 'Producción':
                wip_rows += [
                    {"time": s['Inicio'], "delta":  1, "estacion": ws.name},
                    {"time": s['Salida'], "delta": -1, "estacion": ws.name},
                ]
    df_wip = pd.DataFrame(wip_rows) if wip_rows else pd.DataFrame()

    # ── ESTRUCTURA DE RETORNO ───────────────────────────────────────────────
    # Diccionario completo con todos los resultados de la simulación
    # Diseñado para consumo directo por appSimulador.py (Streamlit frontend)
    return {
        # DataFrames de eventos
        "df_total":       df_total,       # Todos los eventos (producción + downtime + scrap)
        "df_prod":        df_prod,        # Solo eventos de producción (piezas buenas)
        "df_fail":        df_fail,        # Solo eventos de downtime/fallas
        "df_scrap":       df_scrap,       # Solo eventos de scrap (piezas defectuosas)
        "df_wip":         df_wip,         # Serie temporal de WIP

        # DataFrames de análisis
        "bottleneck_df":  bottleneck_df,  # Tiempos de espera por estación
        "ciclo_est_df":   ciclo_est_df,   # Estadísticas de ciclo por estación

        # Datos crudos
        "lead_times":     lead_times,     # Lista de lead times individuales

        # KPIs calculados
        "kpis": {
            "unidades":       unidades,       # Piezas completadas
            "throughput":     throughput,     # Piezas por hora
            "ciclo_promedio": ciclo_prom,     # Lead time promedio
            "disponibilidad": disponibilidad, # % tiempo operativo
            "util_data":      util_data,      # Utilización por estación
            "oee":            oee,            # Overall Equipment Effectiveness
            "rendimiento":    rendimiento,    # % rendimiento vs takt
            "calidad":        calidad,        # % piezas conformes (calculado real)
            "t_final":        round(t_final, 1),  # Tiempo total simulación
            "total_fallas":   len(df_fail),   # Número de eventos de falla
            # ── KPIs de Tiempo Muerto ───────────────────────────────────────
            "idle_time_total": round(total_idle, 2),  # Tiempo idle total (segundos)
            "idle_pct":        idle_pct,              # % de tiempo en idle
            "idle_by_station": {ws.name: round(ws.idle_time, 2) for ws in workstations},
            # ── KPIs de Scrap/Calidad ────────────────────────────────────────
            "scrap_count":     total_scrap,    # Total de piezas scrap
            "good_count":      total_good,     # Total de piezas buenas
            "scrap_rate":      scrap_rate,     # % tasa de scrap
            "scrap_by_station": {ws.name: ws.scrap_count for ws in workstations},
            "good_by_station":  {ws.name: ws.good_count for ws in workstations},
        },

        # Metadata
        "estaciones_names": [ws.name for ws in workstations],  # Nombres ordenados
        "seed_used": seed,  # Semilla usada (None si fue aleatoria)
    }