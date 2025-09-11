# Ingesaurios — Aspiradora Inteligente (Agente Basado en Metas)

> **Proyecto académico de Inteligencia Artificial — Facultad de Ingeniería, UNAM (Grupo 05)**  
> **Profesor:** Miguel Pérez Gaspar · **Fecha de entrega:** 11 de septiembre de 2025  
> Este README está alineado con el contenido del **Reporte_Aspiradora.pdf** y documenta alcance, diseño,
> ejecución y limitaciones del sistema.

---

## 📁 Estructura del proyecto
> La imagen adjunta en el repositorio muestra esta estructura mínima.

```
.
├── README.md                ← Este documento
├── codigo-base-grafico.py   ← Demo/visor base (teclado)
└── codigoFinal.py           ← Versión completa (agente automático + GUI)
```

> Puedes insertar tu imagen con:  
> `![Estructura del proyecto](ruta/a/tu/imagen.png)`

---

## 🧭 Introducción
El proyecto implementa una **aspiradora inteligente** que opera como **agente autónomo** en un entorno
de **cuatro habitaciones (A–D)**. El agente **percibe** suciedad, batería y capacidad de la bolsa, y **actúa** 
limpiando, moviéndose, cargando en **A** y vaciando la bolsa en **D**. La **interfaz gráfica (Tkinter)** muestra
en tiempo real **porcentaje de suciedad**, **posición del robot**, **batería**, **barra de limpieza** y **estado de bolsa**.

El objetivo didáctico es ir **más allá del agente de reflejo simple**, construyendo un **agente basado en metas** que
**planea y gestiona recursos** (energía y depósito) con **políticas de decisión** y **nuevas instrucciones de control**
(IF/ELSE, REPEAT n).

---

## 🧩 Planteamiento del problema
- Simular una aspiradora real con **propiedades de un agente inteligente** (sensores, actuadores y función de agente).
- Manejar **retrasos/condiciones** de la tarea: **bolsa llena** (ir a D, vaciar y volver), **batería baja** (ir a A y cargar)
  y **ensuciamiento continuo** de habitaciones.
- Buscar **mayor eficiencia**: minimizar movimientos innecesarios y evitar trabajo redundante.

---

## 🎯 Objetivos
- Diseñar/programar un agente aspiradora (A–D) que **decida** entre **limpiar** o **moverse** según el estado local,
  optimizando **batería** y **capacidad de bolsa**.
- **Corregir errores** del primer diseño y mostrar **evidencia de ejecución**.
- **Incorporar** las instrucciones: `IF SUCIO THEN {…} ELSE {…}` y `REPEAT n {…}` en el controlador.
- Superar el enfoque de reflejo simple: operar como **agente basado en metas/desempeño**.
- Reportar en tiempo real: **suciedad por cuarto, batería, estado de carga, nivel/capacidad de bolsa, tiempo de limpieza
  y posición actual**.

---

## ⚙️ Funcionalidades
- **Escenario 2×2 (A, B, C, D)** con **suciedad inicial 0–99%** y **ensuciamiento progresivo** a **tasa fija por cuarto**
  (1–4 puntos por **tick** de ~1 s). Durante la **limpieza**, se **pausa** el ensuciamiento **solo** del cuarto actual.
- **Acciones del agente**:
  - `Clean/Suck` → limpia la habitación **en pasadas** de **hasta 25 puntos**; **consume 15** unidades de batería.
  - `Move` → desplazamiento a la habitación objetivo (más sucia); **consume 10** unidades de batería.
  - `Charge` → **carga en A** cuando la batería cae a **≤ 15%** (luego retoma la tarea).
  - `Dump` → **bolsa con capacidad 200**; al llenarse, **va a D**, **vacía** y **regresa** a continuar.
  - `Idle` → si no hay nada que limpiar ni gestionar, **permanece en reposo**.
- **Política de selección/movimiento**:
  - Elegir **siempre** la(s) **habitación(es) más sucia(s)**.
  - En empate: **quedarse** si ya está en una de ellas; si no, elegir por orden **A→B→C→D**.
  - Si **todas están en 0%**, **no se mueve**.
- **Interfaz gráfica** (Tkinter):
  - Barras por habitación (suciedad), **posición del robot**, **batería**, **barra de tiempo de limpieza**, indicadores
    de **carga (A)** y **vaciado (D)**, y **nivel/capacidad de bolsa** + **tasas** de ensuciamiento.

---

## 🛠️ Desarrollo 
- **Sensores**: suciedad por cuarto, posición, batería, estado de carga, **tasas por cuarto**, **nivel/capacidad de bolsa**.
- **Actuadores**: `Move`, `Clean/Suck`, `Charge`, `Dump`.
- **Función del agente** (bucle de decisión):
  1) Si **batería ≤ 15%** → ir a **A** y **cargar**;  
  2) Si **bolsa llena** → ir a **D** y **vaciar**;  
  3) Seleccionar **habitación objetivo** siguiendo la política;  
  4) **Limpiar en pasadas** hasta **0%** y volver al paso 1.
- **Ambiente**: **dinámico** (ensuciamiento continuo por hilos), **completamente observable** y **espacio de estados finito**.

---

## 🧮 Clasificación del agente según el **entorno de tareas** 
- **Observable** → **Completamente observable** (acceso simultáneo a A–D, batería, posición, tasas y bolsa).
- **Agentes** → **Único** (una sola aspiradora).
- **Determinístico / Estocástico** → **Determinístico** tras la aleatorización inicial (suciedad/tasas).
- **Episódico / Secuencial** → **Secuencial** (decisiones influyen estados futuros).
- **Estático / Dinámico** → **Dinámico** (suciedad progresa aun si el agente no actúa).
- **Discreto / Continuo** → **Discreto** (ticks/porcentajes/decisiones).

---

## 🧱 Problemas y limitaciones
- **Reproducibilidad**: semilla aleatoria **desactivada** (escenarios cambian por corrida).
- **Movimiento idealizado**: traslados **instantáneos** (sin ruta/tiempo/colisiones); costo energético **fijo**.
- **Sin criterio de paro global**: con todo en 0% el ciclo **continúa** (no hay meta *Stop*).
- **Empates sesgados**: orden A→D en igualdad puede **sesgar atención**.
- **Concurrencia**: algunas lecturas/actualizaciones **sin bloqueo total** (UI puede mostrar estados intermedios).
- **Modelo de limpieza simplificado**: **chunks=25**, tiempo **lineal** por %; **bolsa rígida**.
- **Progreso parcial**: la **barra de limpieza** no incluye traslados ni vaciado; `clean_total` puede no ajustarse tras interrupciones.
- **Energía idealizada**: consumos `-15` (limpiar) y `-10` (moverse); sin envejecimiento/pérdidas/carga dependiente del nivel.

---

## 🧠 Instrucciones de control implementadas 
### 1) `IF SUCIO THEN { limpiar_actual() } ELSE { … }`
- Condición: **suciedad > 0** en la **habitación actual** y **no** hay limpieza en curso.  
- Efecto: **inicia** limpieza; en caso **contrario** (ELSE), el agente **no aspira** en ese instante y continúa
  el **ciclo de decisión** (ej. moverse u esperar).

### 2) `REPEAT n { … }` 
- Si la habitación tiene `pct` de suciedad, se calcula `n = ceil(pct/25)` y se **repite** la secuencia de limpieza
  **n veces** con **chunks de ≤25 puntos**; cada pasada **suma** al **nivel de bolsa**.
- Durante cada pasada se **pausa el ensuciamiento** del cuarto actual.

---

## 🧪 Casos de prueba 
- **IF SUCIO — ejemplo 1/2**: el robot **inicia** limpieza cuando la habitación actual tiene `%>0` y no hay limpieza en curso
  (se ve la **barra “Limpieza”** activa).
- **REPEAT n — ejemplo**: se observa el avance por **pasadas** (~25 puntos) y el **aumento de la bolsa** cada pasada.
- **Caso negativo (batería)**: con **batería 0%**, **no** se inicia limpieza aunque haya suciedad (control negativo).

---

## 🖥️ Requisitos para ejecutar
- **Python 3.9+** (probado en 3.10/3.11).
- **Tkinter** (incluido en Windows y Python oficial para macOS).  
  - **Linux/WSL**: `sudo apt-get install python3-tk`.

_No hay dependencias adicionales de `pip`._

---

## ▶️ Cómo ejecutar
Desde la carpeta del proyecto:

```bash
# Versión automática completa
python codigoFinal.py

# Visor base (demo con teclado)
python codigo-base-grafico.py
```

La **ventana Tkinter** mostrará el entorno 2×2. Cierra la ventana para terminar la simulación.

> *Tip:* si necesitas **reproducibilidad**, agrega una **semilla** (`random.seed(...)`) al inicio del código.

---

## 🔧 Parámetros y configuración sugerida
Estos valores aparecen en el código final y/o se desprenden del reporte:
- **Tick de ensuciamiento**: ~**1 s** por actualización de tasas (1–4 puntos por cuarto).
- **Pasadas de limpieza**: **25 puntos** máximo por pasada.
- **Consumo energético**: **-15** al limpiar; **-10** al moverse.
- **Batería**: umbral de **≤15%** para **cargar en A**.
- **Bolsa**: capacidad **200**; **vaciar en D** al llenarse.

Puedes exponerlos como **constantes** para facilitar experimentación (p. ej., `CLEAN_SEC_PER_PERCENT`, `BAG_CAPACITY`, `MOVE_COST`).

---

## 📌 Métricas en la UI
- **Suciedad** por A, B, C, D (%)
- **Posición** actual del robot
- **Batería** y **estado de carga**
- **Barra “Limpieza”** (tiempo restante)
- **Nivel/Capacidad de bolsa** (y **vaciado** en D)
- **Tasas** de ensuciamiento por cuarto

---

## 🗺️ Roadmap (extensiones posibles)
- **Criterio de paro** configurable (p. ej., “todas ≤X% por Y s”).
- **Movimiento con ruta/tiempo** (distancias, obstáculos, colisiones) y **costos realistas**.
- **Planificador** por utilidad/costo-tiempo (no solo “más sucia”).
- **Ruido/estocasticidad** en sensores/actuadores y **fallos**.
- **Telemetría** (CSV/JSON) y **tests automáticos**.
- **Semilla** configurable por **CLI**.

---

## 👥 Créditos
Trabajo del equipo **Ingesaurios** para la materia de **Inteligencia Artificial** (Grupo 05).  
Este repositorio es de **uso académico** y refleja los resultados y hallazgos del **Reporte_Aspiradora.pdf**.
