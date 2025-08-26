import random  # Importamos la librería random
from datetime import datetime

random.seed  # Opcional: Hace que los resultados sean reproducibles

# Definimos el entorno: Dos habitaciones A y B
habitaciones = {"A": random.choice(["sucio", "limpio"]),"B": 
    random.choice(["sucio", "limpio"])}

# Posición inicial de la aspiradora (A o B)
posicion_aspiradora = random.choice(["A", "B"])

# Base de carga
base_carga = "A"

# Batería
bateria= 100
limpieza= 15  # Consumo por limpiar
consumo= 10  # Consumo por moverse

def periodo_dia():
    hora_actual = datetime.now().hour
    if 6 <= hora_actual < 12:
        return "mañana"
    elif 12 <= hora_actual < 18:
        return "tarde"
    else:
        return "noche"

def verificar_bateria():
    global bateria, posicion_aspiradora
    
    if bateria <= 15:
        print("⚠ Batería baja. Regresando a la base de carga...")
        
        # Mover a la base de carga
        if posicion_aspiradora != base_carga:
            print("🔄 Moviéndose a la base de carga...")
            posicion_aspiradora = base_carga
            bateria -= consumo
        print("⚡ Cargando batería...")
        bateria = 100  # Recargar completamente
        return False
    
    return True


def aspiradora_simulacion():
    global posicion_aspiradora, bateria
    print(f"Estado inicial: {habitaciones}")
    print(f"Bateria inicial: {bateria}%")
    print(f"Posición inicial: Habitación {posicion_aspiradora}")
    
    
    # La aspiradora ejecuta su tarea
    for ciclo in range(3):  # Simulamos 3 ciclos de limpieza

        #verfiicando el estado de la bateria
        #si la aspiradora estaba cargando, salta al siguiente ciclo
        if not verificar_bateria():
            continue 
        
        
        print(f"\nLa aspiradora está en la habitación {posicion_aspiradora}")
        print(f"Batería actual: {bateria}%")
        
        if habitaciones[posicion_aspiradora] == "sucio":
            print("🔹 Aspirando la habitación...")
            habitaciones[posicion_aspiradora] = "limpio"
            bateria -= limpieza
        else:
            print("✅ La habitación ya está limpia. Moviéndome...")
            
            if "sucio" in habitaciones.values():
                print("Cambiando de habitacion")
                posicion_aspiradora = "A" if posicion_aspiradora == "B" else "B"  # Se mueve a la otra habitación
                bateria -= consumo
            else: 
                print("Ambas habitaciones estan limpias ... Apiradora apagada ")
        
        print(f"Estado actual: {habitaciones}")

# Ejecutar la simulación
aspiradora_simulacion()

