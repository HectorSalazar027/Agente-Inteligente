import random  # Importamos la librería random

random.seed(42)  # Opcional: Hace que los resultados sean reproducibles

# Definimos el entorno: Dos habitaciones A y B
habitaciones = {"A": random.choice(["sucio", "limpio"]),"B": 
    random.choice(["sucio", "limpio"])}

# Posición inicial de la aspiradora (A o B)
posicion_aspiradora = random.choice(["A", "B"])

def aspiradora_simulacion():
    global posicion_aspiradora
    print(f"Estado inicial: {habitaciones}")
    
    # La aspiradora ejecuta su tarea
    for _ in range(3):  # Simulamos 3 ciclos de limpieza
        print(f"\nLa aspiradora está en la habitación {posicion_aspiradora}")
        
        if habitaciones[posicion_aspiradora] == "sucio":
            print("🔹 Aspirando la habitación...")
            habitaciones[posicion_aspiradora] = "limpio"
        else:
            print("✅ La habitación ya está limpia. Moviéndome...")
            
            posicion_aspiradora = "A" if posicion_aspiradora == "B" else "B"  # Se mueve a la otra habitación
        
        print(f"Estado actual: {habitaciones}")

# Ejecutar la simulación
aspiradora_simulacion()

