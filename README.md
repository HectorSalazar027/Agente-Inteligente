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

## 📊 Métricas del Agente  

Al finalizar la simulación, se imprimen métricas para evaluar el desempeño:  

- **Pasos ejecutados** → total de ciclos realizados.  
- **Acciones realizadas** → cuántos `Suck`, `Clean`, `Charge`, `Move`, `Dump`, `Stop`, `None`.  
- **Energía consumida** → batería usada en movimientos y aspiraciones.  
- **Sucks útiles / innecesarios** → aspiraciones que limpiaron suciedad vs. intentos de limpieza en habitaciones ya limpias.  
- **Moves útiles / innecesarios** → movimientos hacia habitacion mas sucia sucias vs. innecesarias.
- **Recargas** → número total de veces que la batería bajó de 15% y fue necesario cargar.
- **Tiempo total** → duración completa de la simulación.  
- **Tiempo cargando** → cuánto estuvo recargando batería.
- **Tiempo vaciando** → tiempo acumulado vaciando la bolsa en la habitación D.
- **Bolsa de basura** → Máximo nivel alcanzado en la bolsa así como  el número de veces que se llenó y obligó a vaciarse.

Estas métricas permiten comparar eficiencia entre diferentes configuraciones (ej. distintas probabilidades de escoger un cuarto o tasas de ensuciamiento).  

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
