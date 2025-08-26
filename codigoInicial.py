import os
import random
import time
import threading

# ------------------ Config ------------------
PAUSA = 1.4           # única pausa general entre pasos/acciones
PAUSA_CARGA = 2       # pausa específica para simular carga de batería
LIMPIAR_CADA_CICLO = True
# random.seed(42)  # Activar si quieres reproducibilidad
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
memoria = {"A": None, "B": None}

# Historial por habitación y periodo con porcentajes
historial_suciedad = {
    "A": {"Día": [], "Tarde": [], "Noche": []},
    "B": {"Día": [], "Tarde": [], "Noche": []}
}

# Rapidez de ensuciamiento (aleatoria por habitación, fija en la ejecución)
rates = {"A": random.randint(1, 4), "B": random.randint(1, 4)}
FAST_ROOM = "A" if rates["A"] >= rates["B"] else "B"      # la más rápida para el día 4
SLOW_ROOM = "B" if FAST_ROOM == "A" else "A"

print(f"Rates de ensuciamiento: A=+{rates['A']} por tick, B=+{rates['B']} por tick")
print(f"Habitación más rápida (día 4 primero): {FAST_ROOM}")

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

# ----------------- Lógica principal -----------------

def periodo_dia(numero):
    if numero == 0:
        return "Día"
    elif numero == 1:
        return "Tarde"
    else:
        return "Noche"

def verificar_bateria():
    global bateria, posicion_aspiradora, base_carga
    if bateria <= 15:
        print("⚠ Batería baja. Moviéndose a la base de carga...")
        time.sleep(PAUSA)
        if posicion_aspiradora != base_carga:
            print("🔄 Desplazándose a la base de carga…")
            posicion_aspiradora = base_carga
            bateria = max(0, bateria - 10)
            time.sleep(PAUSA)
        print("⚡ Cargando batería…")
        charging_event.set()  # durante la carga, ambas habitaciones se ensucian
        time.sleep(PAUSA_CARGA)
        bateria = 100
        charging_event.clear()
        print(f"Batería recargada: {bateria}%")
        time.sleep(PAUSA)
        return True
    return False

# --- Fase de observación: SIEMPRE elegir la más sucia ---
def ciclo_limpieza(periodo, bateria_inicial):
    global habitaciones, memoria, posicion_aspiradora, bateria, historial_suciedad

    if LIMPIAR_CADA_CICLO: limpiar_pantalla()
    with lock:
        estado_inicial = dict(habitaciones)
    print(f"=== {periodo} | Fase de observación ===")
    print(f"Estado inicial: {estado_inicial}")
    print(f"Batería inicial: {bateria_inicial}%")
    print(f"Posición inicial: Habitación {posicion_aspiradora}")
    bateria = bateria_inicial
    time.sleep(PAUSA)

    for ciclo in range(3):  # 3 ciclos por periodo
        if LIMPIAR_CADA_CICLO:
            limpiar_pantalla()
            with lock:
                estado = dict(habitaciones)
            print(f"=== {periodo} | Ciclo {ciclo+1}/3 ===")
            print(f"Habitaciones: {estado} | Memoria: {memoria}")
            print(f"Posición: {posicion_aspiradora} | Batería: {bateria}%")
            time.sleep(PAUSA)

        verificar_bateria()

        # Elegir SIEMPRE la más sucia (si empatan, permanece donde está si es una de las más sucias)
        with lock:
            a, b = habitaciones["A"], habitaciones["B"]
        if a > b:
            objetivo = "A"
        elif b > a:
            objetivo = "B"
        else:
            objetivo = posicion_aspiradora if posicion_aspiradora in ("A", "B") else "A"

        # Mover si hace falta
        if posicion_aspiradora != objetivo:
            posicion_aspiradora = objetivo
            bateria = max(0, bateria - 10)
            print(f"➡️  Moviéndose a habitación {posicion_aspiradora}…")
            time.sleep(PAUSA)

        print(f"📍 La aspiradora está en la habitación {posicion_aspiradora}")
        print(f"🔋 Batería actual: {bateria}%")

        # Actualizar memoria antes de limpiar
        with lock:
            if memoria[posicion_aspiradora] is None:
                memoria[posicion_aspiradora] = habitaciones[posicion_aspiradora]

            pct_actual = habitaciones[posicion_aspiradora]
        historial_suciedad[posicion_aspiradora][periodo].append(pct_actual)

        # Limpiar: bloquear ensuciamiento de esta habitación
        if pct_actual > 0:
            print(f"🔹 Aspirando la habitación… (antes: {pct_actual}%)")
            allow_dirt[posicion_aspiradora].clear()
            with lock:
                habitaciones[posicion_aspiradora] = 0
            bateria = max(0, bateria - 15)
            time.sleep(PAUSA)
            allow_dirt[posicion_aspiradora].set()
        else:
            print("✅ La habitación ya está en 0% (limpia).")
            time.sleep(PAUSA)

        # (Los hilos siguen ensuciando en paralelo la otra habitación)
        with lock:
            estado = dict(habitaciones)
        print(f"Estado actual: {estado}")
        print(f"Memoria de la aspiradora: {memoria}")
        time.sleep(PAUSA)

    return bateria

# =======================
# Recolección por 3 días
# =======================
NUM_DIAS_OBSERVACION = 3
ORDEN_PERIODOS = [0, 2, 1]  # Día → Noche → Tarde

for dia in range(NUM_DIAS_OBSERVACION):
    for i in ORDEN_PERIODOS:
        memoria = {"A": None, "B": None}
        with lock:
            habitaciones = {"A": random.randint(0, 99),
                            "B": random.randint(0, 99)}
        posicion_aspiradora = random.choice(["A", "B"])
        bateria = ciclo_limpieza(periodo_dia(i), bateria)

# Crear tabla de prioridad basada en porcentajes (promedio por periodo) — informativa
tabla_prioridad = {"A": {"Día": 0, "Tarde": 0, "Noche": 0},
                   "B": {"Día": 0, "Tarde": 0, "Noche": 0}}
for hab, periodos in historial_suciedad.items():
    for per, valores in periodos.items():
        tabla_prioridad[hab][per] = (sum(valores) / len(valores)) if valores else 0.0

print("\n📊 Tabla de prioridad (promedio de suciedad observada en 3 días):")
print(tabla_prioridad)
time.sleep(PAUSA)

# --- Fase de limpieza priorizada (día 4): usar FAST_ROOM determinado por rates ---
def ciclo_prioridad(periodo):
    global memoria, habitaciones, posicion_aspiradora, bateria

    if LIMPIAR_CADA_CICLO: limpiar_pantalla()
    with lock:
        estado = dict(habitaciones)
    print(f"=== {periodo} | Fase de limpieza priorizada ===")
    print(f"Estado inicial: {estado}")
    print(f"Batería inicial: {bateria}%")
    print(f"Posición inicial: Habitación {posicion_aspiradora}")
    print(f"🔀 Orden de prioridad fijo por rapidez: {FAST_ROOM} → {SLOW_ROOM}")
    time.sleep(PAUSA)

    for hab in [FAST_ROOM, SLOW_ROOM]:
        verificar_bateria()
        if posicion_aspiradora != hab:
            posicion_aspiradora = hab
            bateria = max(0, bateria - 10)
            print(f"➡️  Moviéndose a habitación {posicion_aspiradora}…")
            time.sleep(PAUSA)

        print(f"\n📍 La aspiradora está en la habitación {posicion_aspiradora}")
        print(f"🔋 Batería actual: {bateria}%")

        with lock:
            if memoria[hab] is None:
                memoria[hab] = habitaciones[hab]
            pct = habitaciones[hab]

        if pct > 0:
            print(f"🔹 Aspirando la habitación… (antes: {pct}%)")
            allow_dirt[hab].clear()
            with lock:
                habitaciones[hab] = 0
            bateria = max(0, bateria - 15)
            time.sleep(PAUSA)
            allow_dirt[hab].set()
        else:
            print("✅ La habitación ya está en 0%.")

        time.sleep(PAUSA)  # los hilos siguen ensuciando la otra

    with lock:
        estado = dict(habitaciones)
    if all(estado_hab == 0 for estado_hab in estado.values()):
        print("🛑 Ambas habitaciones en 0%. Aspiradora apagada")

    print(f"Estado actual: {estado}")
    print(f"Memoria de la aspiradora: {memoria}")
    time.sleep(PAUSA)

# =========================
# Día 4: limpieza priorizada
# =========================
for i in ORDEN_PERIODOS:  # Día → Noche → Tarde
    memoria = {"A": None, "B": None}
    with lock:
        habitaciones = {"A": random.randint(0, 99),
                        "B": random.randint(0, 99)}
    posicion_aspiradora = random.choice(["A", "B"])
    ciclo_prioridad(periodo_dia(i))

print("\n✅ Ejecución completa.")

# Parar hilos limpiamente
stop_event.set()
for t in threads:
    t.join(timeout=1.0)
