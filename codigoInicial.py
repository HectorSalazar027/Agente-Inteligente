import random

# random.seed(42)  # Activar si quieres reproducibilidad

# Inicialización
habitaciones = {"A": random.choice(["sucio", "limpio"]),
                "B": random.choice(["sucio", "limpio"])}
posicion_aspiradora = random.choice(["A", "B"])
base_carga = "A"
bateria = 100
memoria = {"A": None, "B": None}
historial_suciedad = {"A": [], "B": []}

# Función para definir periodo del día
def periodo_dia(numero):
    if numero == 0:
        return "Día"
    elif numero == 1:
        return "Tarde"
    else:
        return "Noche"

# Función para verificar y recargar batería
def verificar_bateria():
    global bateria, posicion_aspiradora, base_carga
    if bateria <= 15:
        print("⚠ Batería baja. Moviéndose a la base de carga...")
        if posicion_aspiradora != base_carga:
            print("🔄 Moviéndose a la base de carga...")
            posicion_aspiradora = base_carga
            bateria -= 10
        print("⚡ Cargando batería...")
        bateria = 100
        print(f"Batería recargada: {bateria}%")
        return True
    return False

# --- Fase de observación ---
def ciclo_limpieza(periodo, bateria_inicial):
    global habitaciones, memoria, posicion_aspiradora, bateria, historial_suciedad
    print(f"\n{periodo}")
    print(f"Estado inicial: {habitaciones}")
    print(f"Batería inicial: {bateria_inicial}%")
    print(f"Posición inicial: Habitación {posicion_aspiradora}")
    bateria = bateria_inicial

    for ciclo in range(6):
        verificar_bateria()
        print(f"\nLa aspiradora está en la habitación {posicion_aspiradora}")
        print(f"Batería actual: {bateria}%")

        # Actualizar memoria y registrar historial
        if memoria[posicion_aspiradora] is None:
            memoria[posicion_aspiradora] = habitaciones[posicion_aspiradora]
        if habitaciones[posicion_aspiradora] == "sucio":
            historial_suciedad[posicion_aspiradora].append(periodo)
            print("🔹 Aspirando la habitación...")
            habitaciones[posicion_aspiradora] = "limpio"
            bateria -= 15
        else:
            print("✅ La habitación ya está limpia.")

        # Decisión de movimiento
        if "sucio" in habitaciones.values() or None in memoria.values():
            posicion_aspiradora = "A" if posicion_aspiradora == "B" else "B"
            bateria -= 10
            print("Cambiando de habitacion")
        else:
            print("Ambas habitaciones revisadas y limpias. Aspiradora apagada")
            break

        print(f"Estado actual: {habitaciones}")
        print(f"Memoria de la aspiradora: {memoria}")

    return bateria

# Ejecutar fase de observación para Día, Tarde y Noche
for i in range(3):
    memoria = {"A": None, "B": None}
    habitaciones = {"A": random.choice(["sucio", "limpio"]),
                    "B": random.choice(["sucio", "limpio"])}
    posicion_aspiradora = random.choice(["A", "B"])
    bateria = ciclo_limpieza(periodo_dia(i), bateria)

# Crear tabla de prioridad
tabla_prioridad = {}
for hab, periodos in historial_suciedad.items():
    tabla_prioridad[hab] = {"Día": 0, "Tarde": 0, "Noche": 0}
    for p in periodos:
        tabla_prioridad[hab][p] += 1

print("\nTabla de prioridad según suciedad registrada:")
print(tabla_prioridad)

# --- Fase de limpieza priorizada ---
def ciclo_prioridad(periodo, tabla_prioridad):
    global memoria, habitaciones, posicion_aspiradora, bateria
    print(f"\n{periodo} (fase de limpieza priorizada)")
    print(f"Estado inicial: {habitaciones}")
    print(f"Batería inicial: {bateria}%")
    print(f"Posición inicial: Habitación {posicion_aspiradora}")

    # Determinar habitación prioritaria según tabla
    if tabla_prioridad["A"][periodo] >= tabla_prioridad["B"][periodo]:
        primero, segundo = "A", "B"
    else:
        primero, segundo = "B", "A"

    # Limpiar habitación prioritaria y luego la otra
    for hab in [primero, segundo]:
        verificar_bateria()
        posicion_aspiradora = hab
        print(f"\nLa aspiradora está en la habitación {posicion_aspiradora}")
        print(f"Batería actual: {bateria}%")

        if memoria[hab] is None:
            memoria[hab] = habitaciones[hab]

        if habitaciones[hab] == "sucio":
            print("🔹 Aspirando la habitación...")
            habitaciones[hab] = "limpio"
            bateria -= 15
        else:
            print("✅ La habitación ya está limpia.")

    if all(estado == "limpio" for estado in habitaciones.values()):
        print("Ambas habitaciones revisadas y limpias. Aspiradora apagada")

    print(f"Estado actual: {habitaciones}")
    print(f"Memoria de la aspiradora: {memoria}")

# Ejecutar limpieza priorizada para Día, Tarde y Noche
for i in range(3):
    memoria = {"A": None, "B": None}
    habitaciones = {"A": random.choice(["sucio", "limpio"]),
                    "B": random.choice(["sucio", "limpio"])}
    posicion_aspiradora = random.choice(["A", "B"])
    ciclo_prioridad(periodo_dia(i), tabla_prioridad)
