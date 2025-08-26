# -*- coding: utf-8 -*-
"""
Simulación de un agente aspiradora de dos habitaciones con batería,
hilos de ensuciamiento estocástico y una política basada en metas.

Este módulo es una **versión documentada** del código original. La lógica
se mantiene igual, pero se agregan:
- Docstrings explicativos en el módulo y funciones
- Comentarios paso a paso
- Tipos (type hints) para mayor claridad
- Estructura y encabezados que facilitan el mantenimiento

Resumen de la simulación
------------------------
- Hay dos habitaciones: "A" y "B". Cada una tiene un porcentaje de suciedad (0-99).
- Dos hilos independientes incrementan la suciedad con cierta tasa por "tick".
- La aspiradora ocupa una de las dos habitaciones y tiene una batería (0-100%).
- Cuando la batería baja al 15% o menos, el agente va a la base de carga y recarga.
- El agente es **basado en metas**: intenta mantener todo limpio minimizando
  acciones innecesarias (mover/suck cuando no aporta).
- Se registran métricas como: pasos, energía, acciones, eficiencias y tiempos.

Ejecución
---------
Ejecuta directamente este archivo para ver la simulación en la terminal.
Si EXPORTAR_CSV=True, se guardará un log de pasos en "log_agente.csv".

Autoría
-------
Código base del usuario; esta versión añade documentación extensa y mejoras
de claridad sin alterar la lógica.
"""

from __future__ import annotations

import os
import random
import time
import threading
from collections import defaultdict
from typing import Dict, Any, List

# ============================================================================
#                                  CONFIG
# ============================================================================
# Pausas para simular el tiempo entre pasos y la carga
PAUSA: float = 1.0            # Pausa general entre pasos/acciones
PAUSA_CARGA: float = 1.5      # Pausa adicional para simular tiempo de carga
LIMPIAR_CADA_CICLO: bool = True
PROB_OBSTACULO: float = 0.25  # Probabilidad de encontrar obstáculo temporal
MAX_STEPS: int = 200          # Cortafuego para detener la simulación
EXPORTAR_CSV: bool = False    # True para exportar CSV con el log de pasos
# random.seed(42)             # Descomenta para ejecuciones reproducibles

# ============================================================================
#                           UTILIDADES DE SALIDA
# ============================================================================
def limpiar_pantalla() -> None:
    """Limpia la pantalla de la terminal (Windows/Linux/Unix)."""
    os.system("cls" if os.name == "nt" else "clear")


# ============================================================================
#                      ESTADO GLOBAL COMPARTIDO (SIMULADOR)
# ============================================================================
# Porcentaje de suciedad por habitación (0-99)
habitaciones: Dict[str, int] = {
    "A": random.randint(0, 99),
    "B": random.randint(0, 99),
}

# Posición inicial de la aspiradora y base de carga
posicion_aspiradora: str = random.choice(["A", "B"])
base_carga: str = "A"

# Carga de la batería (0-100)
bateria: int = 100

# "Memoria" no utilizada (compatibilidad con versiones anteriores)
memoria: Dict[str, Any] = {"A": None, "B": None}

# Histórico (útil si luego se quiere análisis por franja horaria)
historial_suciedad = {
    "A": {"Día": [], "Tarde": [], "Noche": []},
    "B": {"Día": [], "Tarde": [], "Noche": []}
}

# Tasa de ensuciamiento por "tick" (constante durante la ejecución)
rates: Dict[str, int] = {"A": random.randint(1, 4), "B": random.randint(1, 4)}
FAST_ROOM: str = "A" if rates["A"] >= rates["B"] else "B"
SLOW_ROOM: str = "B" if FAST_ROOM == "A" else "A"

print(f"Rates de ensuciamiento: A=+{rates['A']} por tick, B=+{rates['B']} por tick")
print(f"Habitación más rápida (informativo): {FAST_ROOM}")

# ============================================================================
#                               SINCRONIZACIÓN
# ============================================================================
# Bloqueo para proteger lectura/escritura del estado
lock = threading.Lock()

# Eventos de control
stop_event = threading.Event()       # Señal para detener hilos de ensuciamiento
charging_event = threading.Event()   # Si está cargando, ambas se ensucian
allow_dirt = {                       # Si una habitación puede seguir ensuciándose
    "A": threading.Event(),
    "B": threading.Event(),
}
allow_dirt["A"].set()
allow_dirt["B"].set()


# ============================================================================
#                            FUNCIONES DE ENTORNO
# ============================================================================
def clamp99(x: int) -> int:
    """Devuelve 99 si x > 99, de lo contrario x (acota a 0-99)."""
    return 99 if x > 99 else x


def hilo_ensuciar(hab: str) -> None:
    """
    Hilo por habitación que incrementa periódicamente la suciedad.

    Reglas:
    - Cada 'PAUSA' segundos, intenta ensuciar.
    - Si se está cargando (charging_event) o allow_dirt[hab] está activo,
      aumenta la suciedad de esa habitación hasta un máximo de 99.
    """
    while not stop_event.is_set():
        time.sleep(PAUSA)  # tick de ensuciamiento
        if charging_event.is_set() or allow_dirt[hab].is_set():
            with lock:
                if habitaciones[hab] < 99:
                    habitaciones[hab] = clamp99(habitaciones[hab] + rates[hab])


# Lanzar hilos de ensuciamiento como demonios (terminan con el proceso)
threads = [
    threading.Thread(target=hilo_ensuciar, args=("A",), daemon=True),
    threading.Thread(target=hilo_ensuciar, args=("B",), daemon=True),
]
for t in threads:
    t.start()


def estado_entorno() -> Dict[str, int]:
    """Devuelve una copia del estado de suciedad de las habitaciones."""
    with lock:
        return {"A": habitaciones["A"], "B": habitaciones["B"]}


def todo_limpio() -> bool:
    """True si ambas habitaciones están en 0% de suciedad."""
    s = estado_entorno()
    return s["A"] == 0 and s["B"] == 0


def hay_suciedad(hab: str) -> bool:
    """True si la habitación indicada tiene suciedad > 0%."""
    with lock:
        return habitaciones[hab] > 0


def sentido_hacia(otro: str) -> str:
    """
    Devuelve 'left' si el objetivo es ir a A, 'right' si es B.
    (Ayuda a mapear la habitación destino a una dirección abstracta).
    """
    return "right" if otro == "B" else "left"


def hay_pared_si_muevo(direction: str) -> bool:
    """
    Regla de mundo con dos habitaciones:
    - Desde A no puedes mover 'left' (hay pared a la izquierda).
    - Desde B no puedes mover 'right' (hay pared a la derecha).
    """
    if posicion_aspiradora == "A" and direction == "left":
        return True
    if posicion_aspiradora == "B" and direction == "right":
        return True
    return False


def hay_obstaculo_temporal() -> bool:
    """True con probabilidad PROB_OBSTACULO (p.ej., un objeto que bloquea el paso)."""
    return random.random() < PROB_OBSTACULO


# ============================================================================
#                           GESTIÓN DE BATERÍA
# ============================================================================
def verificar_bateria(metrics: Dict[str, Any]) -> bool:
    """
    Si la batería <= 15%:
      - Se mueve a la base (si está en otra habitación), pagando coste de movimiento.
      - Inicia carga (charging_event): ambas habitaciones siguen ensuciándose.
      - Recupera batería a 100% y actualiza tiempos/energía en métricas.

    Returns
    -------
    bool
        True si se realizó un ciclo de carga, False si no fue necesario.
    """
    global bateria, posicion_aspiradora, base_carga
    if bateria <= 15:
        print("⚠ Batería baja. Moviéndose a la base de carga...")
        time.sleep(PAUSA)
        if posicion_aspiradora != base_carga:
            print("🔄 Desplazándose a la base de carga…")
            posicion_aspiradora = base_carga
            bateria = max(0, bateria - 10)  # coste de moverse
            metrics["energia_gastada"] += 10
            metrics["acciones"]["Move"] += 1
            time.sleep(PAUSA)

        print("⚡ Cargando batería…")
        t0 = time.perf_counter()
        charging_event.set()  # durante la carga, ambas habitaciones se ensucian
        time.sleep(PAUSA_CARGA)
        bateria = 100
        charging_event.clear()
        metrics["tiempo_cargando_s"] += (time.perf_counter() - t0)
        print(f"Batería recargada: {bateria}%")
        time.sleep(PAUSA)
        return True
    return False


# ============================================================================
#                                  MÉTRICAS
# ============================================================================
def nueva_estructura_metricas() -> Dict[str, Any]:
    """
    Estructura de métricas que consolida energía/acciones/tiempos y el log de pasos.

    Claves destacadas:
    - pasos: contador de iteraciones del bucle principal
    - acciones: conteo de Suck/Move/Brake/Stop/None
    - energia_gastada: suma de costos (mover=10, aspirar=15)
    - sucks_utiles vs sucks_innecesarios: para eficiencia del "Suck"
    - moves_utiles vs moves_innecesarios: para eficiencia del movimiento
    - frenadas: paredes u obstáculos encontrados
    - log: historial por paso con snapshot de estado
    """
    m: Dict[str, Any] = {
        "pasos": 0,
        "acciones": defaultdict(int),  # Suck, Move, Brake, Stop, None
        "energia_gastada": 0,          # coste acumulado
        "sucks_utiles": 0,
        "sucks_innecesarios": 0,
        "moves_utiles": 0,
        "moves_innecesarios": 0,
        "frenadas": 0,
        "tiempo_total_s": 0.0,
        "tiempo_cargando_s": 0.0,
        "log": []  # cada fila: dict con snapshot por paso
    }
    return m


def imprimir_resumen_metricas(m: Dict[str, Any]) -> None:
    """Imprime métricas finales, incluidas eficiencias y tiempo total/carga."""
    print("\n===== MÉTRICAS =====")
    print(f"Pasos ejecutados: {m['pasos']}")
    print(f"Acciones: {dict(m['acciones'])}")
    print(f"Energía consumida total: {m['energia_gastada']}")
    print(f"Suck útiles: {m['sucks_utiles']} | Suck innecesarios: {m['sucks_innecesarios']}")
    print(f"Moves útiles: {m['moves_utiles']} | Moves innecesarios: {m['moves_innecesarios']}")
    total_sucks = m['sucks_utiles'] + m['sucks_innecesarios']
    total_moves = m['moves_utiles'] + m['moves_innecesarios']
    eff_suck = (m['sucks_utiles'] / total_sucks * 100) if total_sucks else 0.0
    eff_move = (m['moves_utiles'] / total_moves * 100) if total_moves else 0.0
    total_brakes = m['frenadas']
    brake_rate = (total_brakes / max(m['pasos'], 1) * 100)
    print(f"Eficiencia Suck: {eff_suck:.1f}% | Eficiencia Move: {eff_move:.1f}%")
    print(f"Frenadas: {total_brakes} ({brake_rate:.1f}% de pasos)")
    print(f"Tiempo total: {m['tiempo_total_s']:.2f}s | Tiempo cargando: {m['tiempo_cargando_s']:.2f}s")


# ============================================================================
#                   ACCIONES PRIMITIVAS (CON MÉTRICAS)
# ============================================================================
def aspirar_actual(metrics: Dict[str, Any]) -> bool:
    """
    Aspira únicamente si la habitación actual tiene suciedad (>0).

    - Congela temporalmente el ensuciamiento de la habitación actual
      (allow_dirt.clear), limpia y lo vuelve a permitir.
    - Descuenta el coste de energía y actualiza métricas de utilidad.

    Returns
    -------
    bool
        True si se aspiró (había suciedad), False si no (ya estaba limpia).
    """
    global bateria
    with lock:
        pct = habitaciones[posicion_aspiradora]

    if pct > 0:
        print(f"Action: Suck | Habitación {posicion_aspiradora} (antes: {pct}%)")
        allow_dirt[posicion_aspiradora].clear()
        with lock:
            habitaciones[posicion_aspiradora] = 0
        bateria = max(0, bateria - 15)  # coste limpiar
        metrics["energia_gastada"] += 15
        metrics["acciones"]["Suck"] += 1
        metrics["sucks_utiles"] += 1
        time.sleep(PAUSA)
        allow_dirt[posicion_aspiradora].set()
        return True
    else:
        print("Action: None | Ya está limpia, no aspiro.")
        metrics["acciones"]["None"] += 1
        metrics["sucks_innecesarios"] += 1
        return False


def mover(direction: str, metrics: Dict[str, Any], motivo_util: bool = True) -> bool:
    """
    Intenta mover la aspiradora en 'left' o 'right', con chequeo de paredes
    y obstáculo temporal. Actualiza métricas y coste energético.

    Parameters
    ----------
    direction : {'left', 'right'}
        Dirección abstracta: 'left' implica ir a 'A', 'right' a 'B'.
    motivo_util : bool
        True si el movimiento tenía sentido (la otra habitación estaba sucia);
        False si fue innecesario (la otra estaba limpia).

    Returns
    -------
    bool
        True si el movimiento se realizó; False si hubo pared u obstáculo.
    """
    global posicion_aspiradora, bateria
    # pared
    if hay_pared_si_muevo(direction):
        print("Action: Brake | Pared detectada, no me muevo.")
        metrics["acciones"]["Brake"] += 1
        metrics["frenadas"] += 1
        time.sleep(PAUSA)
        return False

    # obstáculo temporal
    if hay_obstaculo_temporal():
        print("Action: Brake | Obstáculo temporal, no me muevo (giro).")
        metrics["acciones"]["Brake"] += 1
        metrics["frenadas"] += 1
        time.sleep(PAUSA)
        return False

    # mover (aplicar cambio de posición y coste)
    if direction == "left":
        posicion_aspiradora = "A"
        print("Action: Move Left  | ahora en A")
    else:
        posicion_aspiradora = "B"
        print("Action: Move Right | ahora en B")

    bateria = max(0, bateria - 10)  # coste mover
    metrics["energia_gastada"] += 10
    metrics["acciones"]["Move"] += 1

    if motivo_util:
        metrics["moves_utiles"] += 1
    else:
        metrics["moves_innecesarios"] += 1

    time.sleep(PAUSA)
    return True


def imprimir_estado() -> None:
    """Imprime suciedad por habitación, posición actual y nivel de batería."""
    s = estado_entorno()
    print(f"Estado: A={s['A']}%  B={s['B']}%  | Pos={posicion_aspiradora} | 🔋{bateria}%")


# ============================================================================
#                        AGENTE BASADO EN METAS
# ============================================================================
def run_goal_agent() -> Dict[str, Any]:
    """
    Ejecuta el bucle del agente basado en metas.

    Política (sin memoria histórica; sólo perceptos actuales):
      1) Si todo limpio -> Stop.
      2) Si la actual está sucia -> Suck.
      3) Si la otra está sucia -> Mover hacia la otra (respetando obstáculos).
      4) Si ninguna está sucia -> No moverse (None).

    Métricas: se actualizan paso a paso (energía, tiempos, utilidades, etc.).
    """
    global bateria

    metrics = nueva_estructura_metricas()
    t_start = time.perf_counter()

    if LIMPIAR_CADA_CICLO:
        limpiar_pantalla()
    print("=== Agente Basado en Metas (dos habitaciones) ===")
    imprimir_estado()
    print("=================================================\n")

    while metrics["pasos"] < MAX_STEPS:
        metrics["pasos"] += 1
        print(f"-- Paso {metrics['pasos']} --")
        s0 = estado_entorno()
        pos0 = posicion_aspiradora

        imprimir_estado()

        # 0) Gestión de energía (puede mover a base y cargar)
        verificar_bateria(metrics)

        # 1) ¿ya está todo limpio?
        if todo_limpio():
            print("Action: Stop | Meta alcanzada (A y B limpias).")
            metrics["acciones"]["Stop"] += 1
            break

        # 2) Aspirar si la actual está sucia
        _ = aspirar_actual(metrics)

        if todo_limpio():
            print("Action: Stop | Meta alcanzada tras aspirar.")
            metrics["acciones"]["Stop"] += 1
            break

        # 3) Decidir si moverse a la otra habitación
        otra = "B" if posicion_aspiradora == "A" else "A"
        otra_sucia_antes = hay_suciedad(otra)  # criterio de utilidad del movimiento

        if otra_sucia_antes:
            dir_to_other = sentido_hacia(otra)
            moved = mover(dir_to_other, metrics, motivo_util=True)
            if not moved:
                # “Giro” alternativo: intentar la otra dirección
                alt = "left" if dir_to_other == "right" else "right"
                mover(alt, metrics, motivo_util=False)
        else:
            print("Action: None | La otra también está limpia. Me quedo.")
            metrics["acciones"]["None"] += 1
            time.sleep(PAUSA)

        # Log del paso
        s1 = estado_entorno()
        metrics["log"].append({
            "paso": metrics["pasos"],
            "pos_inicio": pos0,
            "A_ini": s0["A"], "B_ini": s0["B"],
            "pos_fin": posicion_aspiradora,
            "A_fin": s1["A"], "B_fin": s1["B"],
            "bateria": bateria
        })
        print()

    metrics["tiempo_total_s"] = time.perf_counter() - t_start
    return metrics


# ============================================================================
#                           ENTRADA PRINCIPAL
# ============================================================================
if __name__ == "__main__":
    m = run_goal_agent()
    imprimir_resumen_metricas(m)

    # (Opcional) Exportar CSV con el log del paso a paso
    if EXPORTAR_CSV:
        try:
            import csv
            with open("log_agente.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["paso","pos_inicio","A_ini","B_ini","pos_fin","A_fin","B_fin","bateria"]
                )
                writer.writeheader()
                writer.writerows(m["log"])
            print('CSV guardado como "log_agente.csv" en el directorio actual.')
        except Exception as e:
            print(f"No se pudo guardar CSV: {e}")

    # Parar hilos limpiamente (cada hilo es daemon, pero esto es más explícito)
    stop_event.set()
    for t in threads:
        t.join(timeout=1.0)
