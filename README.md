# Ingesaurios – Agente Inteligente  

Este proyecto fue desarrollado por el equipo **Ingesaurios** con el propósito de aplicar conceptos de **percepción, reglas, optimización y toma de decisiones** en diferentes entornos simulados.  

---

## 🎯 Objetivo  
El sistema busca mostrar cómo los estudiantes pueden **diseñar y programar un agente inteligente** capaz de responder a distintos escenarios, desde asistentes virtuales hasta simulaciones autónomas y chatbots basados en reglas.  

---

## ⚙️ Funcionalidades  

### 1. Asistente Virtual  
- Responde la hora actual cuando el usuario la solicita.  
- Puede dar respuestas aleatorias a preguntas sencillas como “¿Cómo estás?”.  

### 2. Auto Autónomo  
- Se detiene al detectar un obstáculo.  
- Obedece señales de tráfico (alto en semáforo rojo, avance en verde).  
- Avanza cuando el camino está libre.  

### 3. Chatbot Basado en Reglas  
- Responde saludos y despedidas con frases predefinidas.  
- Ejemplo:  
  - “Hola” → “¡Hola! ¿Cómo puedo ayudarte?”  
  - “Adiós” → “¡Hasta luego!”  

### 4. Aspiradora Inteligente (Agente Basado en Metas)  
- Simula la limpieza de **dos habitaciones (A y B)**.  
- Acciones disponibles:  
  - **Suck** → aspira si hay suciedad.  
  - **Move Left / Move Right** → se mueve entre habitaciones.  
  - **Brake** → frena si hay un obstáculo o pared.  
  - **Stop** → se detiene al cumplir la meta (ambas limpias).  
- Considera **obstáculos temporales** y **paredes**.  
- Controla **batería**, con recarga automática en base.  
- El agente **no se mueve innecesariamente**: si ambas habitaciones están limpias, se detiene.  

---

## 📊 Métricas del Agente  

Al finalizar la simulación, se imprimen métricas que permiten evaluar el desempeño:  

- **Pasos ejecutados** → total de ciclos realizados.  
- **Acciones realizadas** → cuántos `Suck`, `Move`, `Brake`, `Stop`, `None`.  
- **Energía consumida** → batería usada en movimientos y aspiraciones.  
- **Sucks útiles / innecesarios** → aspiraciones que limpiaron suciedad vs. las que no.  
- **Moves útiles / innecesarios** → movimientos hacia habitaciones realmente sucias vs. innecesarias.  
- **Frenadas** → número de veces que se encontró con un obstáculo o pared.  
- **Tiempo total** → duración completa de la simulación.  
- **Tiempo cargando** → cuánto estuvo recargando batería.  

Estas métricas permiten comparar eficiencia entre diferentes configuraciones (ej. distintas probabilidades de obstáculos o ensuciamiento).  

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
