# Ingesaurios – Agente Aspiradora Basado en Metas  

Este proyecto fue desarrollado por el equipo **Ingesaurios** con el propósito de aplicar conceptos de **percepción, reglas, optimización y toma de decisiones** en un entorno simulado sencillo, agregando las nuevas funciones que son importantes para la mejora de la primera entrega. 

---

## 🎯 Objetivo  
El sistema busca mostrar cómo se puede **diseñar y programar un agente inteligente** capaz de limpiar habitaciones de manera autónoma, tomando decisiones basadas en el estado actual del entorno y optimizando el uso de su batería.  

---

## ⚙️ Funcionalidades  

### Aspiradora Inteligente (Agente Basado en Metas)  
- Simula la limpieza de **dos habitaciones (A y B)** con suciedad variable entre 0 y 99%.  
- Acciones disponibles:  
  - **Suck** → aspira si hay suciedad.  
  - **Move Left / Move Right** → se mueve entre habitaciones.  
  - **Brake** → frena si hay un obstáculo o pared.  
  - **Stop** → se detiene al cumplir la meta (ambas limpias).  
  - **None** → no realiza acción si no es necesario.  
- Considera **obstáculos temporales** y **paredes**.  
- Controla **batería**, con recarga automática en la base cuando baja del 15%.  
- El agente **minimiza movimientos innecesarios**: si ambas habitaciones están limpias, no se mueve.  

## Sensores y Actuadores 
Sensor
- Detector de suciedad
- Sensor de posición
- Detector de batería 
Actuador
- Motor de movimiento

---

## 📊 Métricas del Agente  

Al finalizar la simulación, se imprimen métricas para evaluar el desempeño:  

- **Pasos ejecutados** → total de ciclos realizados.  
- **Acciones realizadas** → cuántos `Suck`, `Move`, `Brake`, `Stop`, `None`.  
- **Energía consumida** → batería usada en movimientos y aspiraciones.  
- **Sucks útiles / innecesarios** → aspiraciones que limpiaron suciedad vs. las que no.  
- **Moves útiles / innecesarios** → movimientos hacia habitaciones realmente sucias vs. innecesarias.  
- **Frenadas** → veces que se encontró con un obstáculo o pared.  
- **Tiempo total** → duración completa de la simulación.  
- **Tiempo cargando** → cuánto estuvo recargando batería.  

Estas métricas permiten comparar eficiencia entre diferentes configuraciones (ej. distintas probabilidades de obstáculos o tasas de ensuciamiento).  

---

## 🧠 Clasificación del Agente según las Propiedades del Entorno de Tareas  

De acuerdo con la teoría de **entornos de tareas en IA**, nuestro agente aspiradora se clasifica así:  

- **Observable → Parcialmente observable**  
  El agente solo conoce la suciedad en la habitación donde está, y no tiene una visión completa del entorno al mismo tiempo.  

- **Agentes → Único**  
  Solo hay un agente actuando (la aspiradora).  

- **Determinístico / Estocástico → Estocástico**  
  El entorno es incierto porque aparecen obstáculos aleatorios y la suciedad aumenta de manera probabilística.  

- **Episódico / Secuencial → Secuencial**  
  Las acciones tienen impacto en estados futuros: si la aspiradora no limpia ahora, la suciedad se acumula más adelante.  

- **Estático / Dinámico → Dinámico**  
  Aunque la aspiradora no actúe, el entorno cambia (la suciedad aumenta con el tiempo).  

- **Discreto / Continuo → Discreto**  
  Las acciones posibles están en un conjunto finito (aspirar, mover, detenerse), aunque la suciedad tenga valores numéricos.  

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
