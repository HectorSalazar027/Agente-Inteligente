# Ingesaurios – Agente Aspiradora Basado en Metas  

Este proyecto fue desarrollado por el equipo **Ingesaurios** con el propósito de aplicar conceptos de **percepción, reglas, optimización y toma de decisiones** en un entorno simulado sencillo, agregando las nuevas funciones que son importantes para la mejora de la primera entrega. 

---

## 🎯 Objetivo  
El sistema busca mostrar cómo se puede **diseñar y programar un agente inteligente** capaz de limpiar habitaciones de manera autónoma, tomando decisiones basadas en el estado actual del entorno y optimizando el uso de su batería.  

---

## ⚙️ Funcionalidades  

### Aspiradora Inteligente (Agente Basado en Metas)  
- Simula la limpieza de **cuatro habitaciones (A, B, C y D)**.
- Cada habitación cuenta con un nivel de suciedad entre 0 y 99%.
- La suciedad aumenta automáticamente con el tiempo, a distinta velocidad en cada cuarto.  
- Acciones disponibles:  
  - **Suck** → si la habitación actual tiene suciedad, inicia limpieza en bloques de hasta 25%.  
  - **Move** → se desplaza de la habitación actual a otra más sucia, consumiendo batería.
  - **Dump** → cuando la bolsa interna se llena, se traslada a la habitación D, vacía la suciedad (parpadeo) y regresa.
  - **Stop** → se detiene al cumplir la meta.  
  - **None** → si no hay suciedad y no hay necesidad de recargar o vaciar, permanece quieta.  
- Considera **obstáculos temporales** y **paredes**.  
- Controla **batería**, si la batería baja de 15%, se traslada a la base (habitación A), se detiene y recarga hasta el 100%. 
- El agente **minimiza movimientos innecesarios**: El controlador automático siempre elige la(s) habitación(es) con mayor suciedad, si está en una de las habitaciones más sucias, se queda y limpia ahí. Si todas las habitaciones están limpias, no se mueve.
- Se consdiera la **bolsa de suciedad**: Tiene capacidad limitada y cada vez que limpia, acumula suciedad en la bolsa.


## Sensores y Actuadores 
Sensor
- Detector de suciedad
- Sensor de posición
- Detector de batería
- Estado de carga
- Estado de la bolsa de suciedad
  
Actuador
- Motor de movimiento
- Vaciado de basura o suciedad


---

## 🧠 Clasificación del Agente según las Propiedades del Entorno de Tareas  

De acuerdo con la teoría de **entornos de tareas en IA**, nuestro agente aspiradora mejorado se clasifica así:  

- **Observable → Parcialmente observable**  
  El agente solo conoce la suciedad en la habitación donde está así como la batería y la bolsa, y no tiene una visión completa del entorno al mismo tiempo.  

- **Agentes → Único**  
  Solo hay un agente actuando en todo el sistema (la aspiradora).  

- **Determinístico / Estocástico → Estocástico**  
  El entorno es incierto por la generación de suciedad y la variabilidad en los tiempos de limpieza. 

- **Episódico / Secuencial → Secuencial**  
  Las acciones tienen impacto en estados futuros: la suciedad acumulada afecta decisiones posteriores de limpieza y recarga.

- **Estático / Dinámico → Dinámico**  
  Aunque la aspiradora no actúe, el entorno cambia (la suciedad aumenta continuamente con el tiempo).  

- **Discreto / Continuo → Discreto**  
  Las acciones posibles están en un conjunto finito (aspirar, mover, detenerse), aunque la suciedad tenga valores numéricos.  

---

## 🧩 Implementación de las Nuevas Instrucciones

## IF SUCIO THEN {...} ELSE {...}
Basándonos en el código principal, esta instrucción se implementa de forma explícita en tiempo real dentro del método del controlador automático _loop() y en limpiar_actual().

```python
# Dentro de AutoController._loop()
st2 = self.sim.get_state()
if st2["habitaciones"][st2["posicion"]] > 0 and not self.sim.is_cleaning():
    self.sim.limpiar_actual()
``` 
Se puede visualizar que 
- if st2["habitaciones"][st2["posicion"]] > 0 → equivale a **IF SUCIO**
- self.sim.limpiar_actual() → acción **“Suck”**
- else implícito → no hace nada, sigue evaluando en el siguiente tick (time.sleep(PAUSA_DECISION))
En otras palabras, el agente decide en tiempo real si limpiar la habitación actual o moverse a otra, basándose en la suciedad.


## REPEAT n {...}
Esto aparece en la simulación de limpieza en chunks dentro de VacuumSim.limpiar_actual()

```python
# Dentro de VacuumSim.limpiar_actual()
remaining = pct
chunks = []
while remaining > 0:
    chunk_points = min(25, remaining)
    chunk_time = max(0.5, chunk_points * CLEAN_SEC_PER_PERCENT)
    chunks.append((chunk_points, chunk_time))
    remaining -= chunk_points

# --- Ejecutar pasadas secuenciales ---
for chunk_points, chunk_time in chunks:
    step = 0.05
    end_t = time.time() + chunk_time
    while time.time() < end_t and not self.stop_event.is_set():
        time.sleep(step)

    with self.lock:
        self.habitaciones[room] = max(0, int(self.habitaciones[room]) - chunk_points)
        self.bag_level += chunk_points
``` 
- El agente divide la limpieza en “chunks” de 25 puntos de suciedad y ejecuta cada pasada secuencialmente.
- Cada pasada se repite hasta que la suciedad de la habitación llega a 0 o la bolsa se llena.
Podmeos decir que el **REPEAT n { ... }:** implementa la repetición de la acción de aspirar un chunk n veces según la suciedad total.


---
## 🧩 Ejemplo de Código Simplificado  

```python
import random  

habitaciones = {"A": random.choice(["sucio", "limpio"]), 
                "B": random.choice(["sucio", "limpio"])}

posicion_aspiradora = random.choice(["A", "B"])

def aspiradora_simulacion():
    global posicion_aspiradora
    print(f"Estado inicial: {habitaciones}")
    
    for _ in range(3):  # Tres ciclos de limpieza
        print(f"\nLa aspiradora está en la habitación {posicion_aspiradora}")
        
        if habitaciones[posicion_aspiradora] == "sucio":
            print("🔹 Aspirando...")
            habitaciones[posicion_aspiradora] = "limpio"
        else:
            print("✅ Ya está limpia. Cambiando de habitación...")
            posicion_aspiradora = "A" if posicion_aspiradora == "B" else "B"
        
        print(f"Estado actual: {habitaciones}")

aspiradora_simulacion()
```  

---

