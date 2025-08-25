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

---

## 🧩 Código Base de Ejemplo  

Se incluye un prototipo de **aspiradora inteligente** que simula la limpieza de dos habitaciones.  
El agente:  
1. Evalúa el estado de la habitación actual (limpia o sucia).  
2. Aspira si encuentra suciedad.  
3. Cambia de posición si la habitación ya está limpia.  
4. Registra el estado en cada ciclo de simulación.  

```python
import random  

random.seed(42)  # Semilla para reproducibilidad

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
