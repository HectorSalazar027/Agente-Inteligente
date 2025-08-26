import os
import random
import time
import threading
from collections import defaultdict

# ------------------ Config ------------------
PAUSA = 1.0            # pausa general entre pasos/acciones (ligeramente menor para pruebas)
PAUSA_CARGA = 1.5      # pausa para simular carga de batería
LIMPIAR_CADA_CICLO = True
PROB_OBSTACULO = 0.25  # probabilidad de obstáculo temporal al intentar moverse
MAX_STEPS = 200        # límite de seguridad del bucle del agente
EXPORTAR_CSV = False   # True para guardar log en CSV (requiere permisos de escritura)
# random.seed(42)       # Activar para reproducibilidad
# ------------------------------------------------

# Utilidades de salida
def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

# ====== Estado global compartido ======
habitaciones = {"A": random.randint(0, 99),
                "B": random.randint(0, 99)}
posicion_aspiradora = random.choice(["A", "B"])
base_carga = "A"
bateria = 100
memoria = {"A": None, "B": None}  # no se usa para recordar (compatibilidad)

# Historial (no imprescindible para metas, pero útil si luego quieres análisis)
historial_suciedad = {
    "A": {"Día": [], "Tarde": [], "Noche": []},
    "B": {"Día": [], "Tarde": [], "Noche": []}
}

# Rapidez de ensuciamiento (aleatoria por habitación, fija en la ejecución)
rates = {"A": random.randint(1, 4), "B": random.randint(1, 4)}
FAST_ROOM = "A" if rates["A"] >= rates["B"] else "B"
SLOW_ROOM = "B" if FAST_ROOM == "A" else "A"

print(f"Rates de ensuciamiento: A=+{rates['A']} por tick, B=+{rates['B']} por tick")
print(f"Habitación más rápida (informativo): {FAST_ROOM}")

# Sincronización
lock = threading.Lock()
stop_event = threading.Event()
charging_event = threading.Event()          # si está cargando, ambas se ensucian
allow_dirt = {"A": threading.Event(), "B": threading.Event()}  # si puede ensuciarse
allow_dirt["A"].set()
allow_dirt["B"].set()

def clamp99(x):
    return 99 if x > 99 else x

def hilo_ensuciar(hab):
    """Hilo por habitación: ensucia de forma periódica respetando flags."""
    while not stop_event.is_set():
        time.sleep(PAUSA)  # "tick" de ensuciamiento
        if charging_event.is_set() or allow_dirt[hab].is_set():
            with lock:
                if habitaciones[hab] < 99:
                    habitaciones[hab] = clamp99(habitaciones[hab] + rates[hab])

# Lanzar hilos de ensuciamiento
threads = [
    threading.Thread(target=hilo_ensuciar, args=("A",), daemon=True),
    threading.Thread(target=hilo_ensuciar, args=("B",), daemon=True),
]
for t in threads:
    t.start()

# ----------------- Utilidades de entorno -----------------
def estado_entorno():
    with lock:
        return {"A": habitaciones["A"], "B": habitaciones["B"]}

def todo_limpio():
    s = estado_entorno()
    return s["A"] == 0 and s["B"] == 0

def hay_suciedad(hab):
    with lock:
        return habitaciones[hab] > 0

def sentido_hacia(otro):
    """Devuelve 'left' si ir a A, 'right' si ir a B."""
    return "right" if otro == "B" else "left"

def hay_pared_si_muevo(direction):
    """Con dos habitaciones: desde A no puedes mover 'left'; desde B no puedes mover 'right'."""
    if posicion_aspiradora == "A" and direction == "left":
        return True
    if posicion_aspiradora == "B" and direction == "right":
        return True
    return False

def hay_obstaculo_temporal():
    return random.random() < PROB_OBSTACULO

# ----------------- Batería -----------------
def verificar_bateria(metrics):
    """Si la batería <=15, vuelve a base y recarga. Cuenta tiempos y acciones."""
    global bateria, posicion_aspiradora, base_carga
    if bateria <= 15:
        print("⚠ Batería baja. Moviéndose a la base de carga...")
        time.sleep(PAUSA)
        if posicion_aspiradora != base_carga:
            print("🔄 Desplazándose a la base de carga…")
            posicion_aspiradora = base_carga
            bateria = max(0, bateria - 10)  # coste por moverse
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

# ----------------- Métricas -----------------
def nueva_estructura_metricas():
    m = {
        "pasos": 0,
        "acciones": defaultdict(int),  # Suck, Move, Brake, Stop, None
        "energia_gastada": 0,          # suma de costos (mover 10, aspirar 15)
        "sucks_utiles": 0,             # aspirados que removieron suciedad real
        "sucks_innecesarios": 0,       # intentos de aspirar cuando ya estaba limpia
        "moves_utiles": 0,             # movimiento cuando la otra tenía suciedad
        "moves_innecesarios": 0,       # movimiento cuando la otra no tenía suciedad
        "frenadas": 0,                 # brakes (pared u obstáculo)
        "tiempo_total_s": 0.0,
        "tiempo_cargando_s": 0.0,
        "log": []                      # filas dict con snapshot por paso
    }
    return m

def imprimir_resumen_metricas(m):
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

# ----------------- Acciones primitivas (con métricas) -----------------
def aspirar_actual(metrics):
    """Suck solo si hay suciedad (meta: no actuar innecesariamente)."""
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

def mover(direction, metrics, motivo_util=True):
    """Move Left/Right con detección de obstáculo (pared u obstáculo temporal)."""
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
    # mover
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

def imprimir_estado():
    s = estado_entorno()
    print(f"Estado: A={s['A']}%  B={s['B']}%  | Pos={posicion_aspiradora} | 🔋{bateria}%")

# ----------------- Agente Basado en Metas -----------------
def run_goal_agent():
    """
    Meta: mantener el entorno limpio minimizando acciones innecesarias.
    Política (sin memoria histórica; sólo perceptos actuales):
      1) Si todo limpio -> Stop.
      2) Si actual sucia -> Suck.
      3) Si la otra está sucia -> mover hacia la otra (respetando obstáculos).
      4) Si ninguna sucia -> no moverse.
    """
    global bateria

    metrics = nueva_estructura_metricas()
    t_start = time.perf_counter()

    if LIMPIAR_CADA_CICLO: limpiar_pantalla()
    print("=== Agente Basado en Metas (dos habitaciones) ===")
    imprimir_estado()
    print("=================================================\n")

    while metrics["pasos"] < MAX_STEPS:
        metrics["pasos"] += 1
        print(f"-- Paso {metrics['pasos']} --")
        s0 = estado_entorno()
        pos0 = posicion_aspiradora

        imprimir_estado()

        # 0) Gestión de energía
        verificar_bateria(metrics)

        # 1) ¿ya está todo limpio?
        if todo_limpio():
            print("Action: Stop | Meta alcanzada (A y B limpias).")
            metrics["acciones"]["Stop"] += 1
            break

        # 2) Suck si la actual está sucia
        hizo_suck = aspirar_actual(metrics)
        if todo_limpio():
            print("Action: Stop | Meta alcanzada tras aspirar.")
            metrics["acciones"]["Stop"] += 1
            break

        # 3) ¿debo moverme a la otra?
        otra = "B" if posicion_aspiradora == "A" else "A"
        otra_sucia_antes = hay_suciedad(otra)  # criterio de utilidad del movimiento

        if otra_sucia_antes:
            dir_to_other = sentido_hacia(otra)
            moved = mover(dir_to_other, metrics, motivo_util=True)
            if not moved:
                # “girar”: intentar la otra dirección (usualmente pared -> Brake, queda registrado)
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

# ----------------- Entrada principal -----------------
if __name__ == "__main__":
    m = run_goal_agent()
    imprimir_resumen_metricas(m)

    # (Opcional) Exportar CSV
    if EXPORTAR_CSV:
        try:
            import csv
            with open("log_agente.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["paso","pos_inicio","A_ini","B_ini","pos_fin","A_fin","B_fin","bateria"])
                writer.writeheader()
                writer.writerows(m["log"])
            print('CSV guardado como "log_agente.csv" en el directorio actual.')
        except Exception as e:
            print(f"No se pudo guardar CSV: {e}")

    # Parar hilos limpiamente
    stop_event.set()
    for t in threads:
        t.join(timeout=1.0)
