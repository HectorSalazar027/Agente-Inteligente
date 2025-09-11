import random
import time
import threading
import tkinter as tk
from tkinter import ttk

# ------------------ Config ------------------
PAUSA_TICK = 1.0        # pausa base entre "ticks" de ensuciamiento
PAUSA_CARGA = 2.0       # pausa para simular carga de batería
CLEAN_SEC_PER_PERCENT = 0.05 # segundos por % de suciedad (100% -> 5.0s aprox)
PAUSA_DECISION = 0.06   # pausa entre decisiones del controlador (rápida para buena respuesta)
ROOMS = ("A", "B", "C", "D")
# random.seed(42)       # activar si se quiere reproducibilidad

# ------------------ Backend de simulación ------------------
class VacuumSim:
    def __init__(self):
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.charging_event = threading.Event()  # si está cargando, todas se ensucian
        # Permiso de ensuciamiento por habitación (para pausar durante limpieza)
        self.allow_dirt = {r: threading.Event() for r in ROOMS}
        for r in ROOMS:
            self.allow_dirt[r].set()

        # Estado por habitación (0-99%)
        self.habitaciones = {r: random.randint(0, 99) for r in ROOMS}
        # Tasas fijas 1..4 por habitación
        self.rates = {r: random.randint(1, 4) for r in ROOMS}
        self.base_carga = "A"
        self.posicion = random.choice(ROOMS)
        self.bateria = 100

        # Estado de limpieza (para la barra de tiempo)
        self.cleaning_event = threading.Event()
        self.clean_total = 0.0
        self.clean_start = 0.0

        # Hilos de ensuciamiento por habitación
        self.threads = []
        for r in ROOMS:
            t = threading.Thread(target=self._hilo_ensuciar, args=(r,), daemon=True)
            self.threads.append(t)
            t.start()

    @staticmethod
    def _clamp99(x: int) -> int:
        return 99 if x > 99 else (0 if x < 0 else x)

    def _hilo_ensuciar(self, room: str):
        """Aumenta el % de suciedad de 'room' periódicamente."""
        while not self.stop_event.is_set():
            time.sleep(PAUSA_TICK)
            if self.charging_event.is_set() or self.allow_dirt[room].is_set():
                with self.lock:
                    if self.habitaciones[room] < 99:
                        self.habitaciones[room] = self._clamp99(self.habitaciones[room] + self.rates[room])

    # --- API pública ---
    def get_state(self):
        with self.lock:
            # calcular tiempo restante de limpieza
            cleaning = self.cleaning_event.is_set()
            if cleaning and self.clean_total > 0:
                elapsed = max(0.0, time.time() - self.clean_start)
                remaining = max(0.0, self.clean_total - elapsed)
            else:
                remaining = 0.0
            return {
                "habitaciones": dict(self.habitaciones),
                "posicion": self.posicion,
                "bateria": self.bateria,
                "rates": dict(self.rates),
                "cargando": self.charging_event.is_set(),
                "cleaning": cleaning,
                "clean_total": self.clean_total,
                "clean_remaining": remaining,
            }

    def is_cleaning(self) -> bool:
        return self.cleaning_event.is_set()

    def verificar_bateria_y_cargar_si_hace_falta(self):
        """Si batería <=15, ir a base A (si no estás) y cargar a 100%."""
        if self.bateria <= 15 and not self.is_cleaning():
            if self.posicion != self.base_carga:
                self.posicion = self.base_carga
                self.bateria = max(0, self.bateria - 10)
            self.charging_event.set()
            time.sleep(PAUSA_CARGA)
            self.bateria = 100
            self.charging_event.clear()
            return True
        return False

    def mover_a(self, destino: str):
        if destino not in ROOMS or self.is_cleaning():
            return
        self.verificar_bateria_y_cargar_si_hace_falta()
        if self.posicion != destino:
            self.posicion = destino
            self.bateria = max(0, self.bateria - 10)

    def limpiar_actual(self):
        if self.is_cleaning():
            return
        room = self.posicion
        with self.lock:
            pct = int(self.habitaciones[room])
        if pct <= 0:
            return

    # --- Preparar limpieza en pasadas de 25 puntos porcentuales ---
    # NUEVA FUNCIONALIDAD REPEAT N VECES: dividir limpieza en chunks de 25 de suciedad
        remaining = pct
        chunks = []
        while remaining > 0:
            chunk = min(25, remaining)                  # cada pasada quita 25 "puntos" de suciedad
            chunk_time = max(0.5, chunk * CLEAN_SEC_PER_PERCENT)
            chunks.append(chunk_time)
            remaining -= chunk
        total_time = sum(chunks)

        # Iniciar limpieza (mismo comportamiento que antes)
        self.clean_total = total_time
        self.clean_start = time.time()
        self.cleaning_event.set()

        # Consumir batería una vez al inicio (todo lo demás se queda igual)
        self.bateria = max(0, self.bateria - 15)

        # Bloquear ensuciamiento SOLO de la habitación actual durante toda la sesión
        self.allow_dirt[room].clear()

        # --- Ejecutar pasadas secuenciales ---
        for chunk_time in chunks:
            # Simular limpieza de esta pasada con steps pequeños para que la GUI muestre progreso continuo
            step = 0.05
            end_t = time.time() + chunk_time
            while time.time() < end_t and not self.stop_event.is_set():
                time.sleep(step)

            # Al terminar cada pasada, reducir 25 puntos de suciedad y reflejarlo en el estado
            with self.lock:
                self.habitaciones[room] = max(0, int(self.habitaciones[room]) - 25)

            # (opcional) si ya quedó en 0 por condiciones externas, salimos
            with self.lock:
                if self.habitaciones[room] <= 0:
                    break

        # Finalizar limpieza
        with self.lock:
            self.habitaciones[room] = 0
        self.allow_dirt[room].set()
        self.cleaning_event.clear()
        self.clean_total = 0.0
        self.clean_start = 0.0


# ------------------ Controlador Automático ------------------
class AutoController:
    """
    - Elegir siempre la(s) habitación(es) más sucia(s).
    - Empates: quedarse si la posición actual está entre las más sucias; si no, elegir la primera por orden A,B,C,D.
    - Antes de actuar, verificar/cargar batería.
    - Respetar cuando está limpiando (no interrumpir).
    """
    def __init__(self, sim: VacuumSim):
        self.sim = sim
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.stop_event = threading.Event()

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=1.0)

    def _loop(self):
        while not self.stop_event.is_set():
            # Si está limpiando, no tomar decisiones nuevas
            if self.sim.is_cleaning():
                time.sleep(0.05)
                continue

            # 1) Batería
            self.sim.verificar_bateria_y_cargar_si_hace_falta()

            # 2) Medir suciedad
            st = self.sim.get_state()
            dirty = st["habitaciones"]
            max_val = max(dirty.values())
            candidates = [r for r, v in dirty.items() if v == max_val]

            # 3) Decidir destino
            if st["posicion"] in candidates:
                objetivo = st["posicion"]
            else:
                objetivo = sorted(candidates, key=lambda r: ROOMS.index(r))[0]

            # 4) Mover si es necesario
            if st["posicion"] != objetivo:
                self.sim.mover_a(objetivo)

            # 5) Limpiar si hay suciedad
            st2 = self.sim.get_state()
            if st2["habitaciones"][st2["posicion"]] > 0 and not self.sim.is_cleaning():
                self.sim.limpiar_actual()

            time.sleep(PAUSA_DECISION)

# ------------------ GUI (Tkinter) ------------------
class VacuumGUI:
    def __init__(self, sim: VacuumSim, controller: AutoController):
        self.sim = sim
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("Aspiradora Inteligente - Automática (4 habitaciones)")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.W, self.H = 820, 560
        self.PAD, self.GAP = 24, 24

        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, bg="#f6f6f6", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Panel superior con métricas
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=(6, 10))
        self.lbl_info = ttk.Label(top, text="", font=("Helvetica", 11, "bold"))
        self.lbl_info.pack(side="left")

        # Definir rectángulos 2x2
        room_width = (self.W - 2 * self.PAD - self.GAP) // 2
        room_height = (self.H - 2 * self.PAD - self.GAP) // 2

        self.rooms = {}
        # A (arriba izq), B (arriba der), C (abajo izq), D (abajo der)
        self.rooms["A"] = (self.PAD, self.PAD, self.PAD + room_width, self.PAD + room_height)
        self.rooms["B"] = (self.PAD + room_width + self.GAP, self.PAD,
                           self.PAD + room_width * 2 + self.GAP, self.PAD + room_height)
        self.rooms["C"] = (self.PAD, self.PAD + room_height + self.GAP,
                           self.PAD + room_width, self.PAD + room_height * 2 + self.GAP)
        self.rooms["D"] = (self.PAD + room_width + self.GAP, self.PAD + room_height + self.GAP,
                           self.PAD + room_width * 2 + self.GAP, self.PAD + room_height * 2 + self.GAP)

        # Dibujar habitaciones
        self.fill_rect = {}
        self.fill_label = {}
        for r in ROOMS:
            x1, y1, x2, y2 = self.rooms[r]
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#ffffff", outline="#444", width=2)
            self.canvas.create_text(x1 + 8, y1 + 8, anchor="nw", text=f"Habitación {r}", font=("Helvetica", 11, "bold"))
            rid = self.canvas.create_rectangle(x1, y2, x2, y2, fill="#4caf50", outline="")
            self.fill_rect[r] = rid
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            lid = self.canvas.create_text(cx, cy, text="0%", font=("Helvetica", 16, "bold"))
            self.fill_label[r] = lid

        # Dibujar aspiradora
        self.vacuum_radius = 16
        self.vacuum_items = []
        self._make_vacuum_and_bars()

        # Iniciar controlador
        self.controller.start()

        # Refresco
        self._tick()

    # ------ Vacuum + Bars drawing ------
    def _make_vacuum_and_bars(self):
        room = self.sim.posicion
        x1, y1, x2, y2 = self.rooms[room]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        r = self.vacuum_radius
        # Vacuum
        body = self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#607d8b", outline="#263238", width=2)
        wnd = self.canvas.create_oval(cx - r/2, cy - r/2, cx - r/6, cy - r/6, fill="#cfd8dc", outline="")
        antenna = self.canvas.create_line(cx, cy - r, cx, cy - r - 12, width=3)
        self.vacuum_items = [body, wnd, antenna]

        # Bars layout under the vacuum
        bar_w = 140
        bar_h = 10
        bar_gap = 6
        top_y = cy + r + 10
        left_x = cx - bar_w/2

        # Battery bar (background + fill + label)
        self.batt_bg = self.canvas.create_rectangle(left_x, top_y, left_x + bar_w, top_y + bar_h, outline="#263238", width=1)
        self.batt_fg = self.canvas.create_rectangle(left_x, top_y, left_x, top_y + bar_h, fill="#4caf50", outline="")
        self.batt_text = self.canvas.create_text(cx, top_y + bar_h/2, text="Batería 100%", font=("Helvetica", 9))

        # Cleaning time bar (background + fill + label)
        top2 = top_y + bar_h + bar_gap
        self.clean_bg = self.canvas.create_rectangle(left_x, top2, left_x + bar_w, top2 + bar_h, outline="#263238", width=1)
        self.clean_fg = self.canvas.create_rectangle(left_x, top2, left_x, top2 + bar_h, fill="#03a9f4", outline="")
        self.clean_text = self.canvas.create_text(cx, top2 + bar_h/2, text="Limpieza 0.0s", font=("Helvetica", 9))

    def _move_bars_with_vacuum(self, dx, dy):
        # Move both bars and their labels
        for item in (self.batt_bg, self.batt_fg, self.batt_text, self.clean_bg, self.clean_fg, self.clean_text):
            self.canvas.move(item, dx, dy)

    def move_vacuum_to_room_center(self, room: str):
        x1, y1, x2, y2 = self.rooms[room]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

        # current center of oval
        curr_coords = self.canvas.coords(self.vacuum_items[0])  # oval
        x0 = (curr_coords[0] + curr_coords[2]) / 2
        y0 = (curr_coords[1] + curr_coords[3]) / 2
        dx, dy = cx - x0, cy - y0

        # move vacuum
        for item in self.vacuum_items:
            self.canvas.move(item, dx, dy)
        # move bars
        self._move_bars_with_vacuum(dx, dy)

    # ------ GUI Tick ------
    def _tick(self):
        st = self.sim.get_state()
        # Actualizar % y barras por habitación
        for r in ROOMS:
            x1, y1, x2, y2 = self.rooms[r]
            pct = int(st["habitaciones"][r])
            height = (y2 - y1) * (pct / 100.0)
            new_y = y2 - height
            self.canvas.coords(self.fill_rect[r], x1, new_y, x2, y2)
            self.canvas.itemconfigure(self.fill_label[r], text=f"{pct}%")

        # Indicador de carga (borde parpadeante en base A)
        if st["cargando"]:
            x1, y1, x2, y2 = self.rooms[self.sim.base_carga]
            if not hasattr(self, "_charge_indicator"):
                self._charge_indicator = self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, outline="#ff9800", width=3)
            else:
                state = self.canvas.itemcget(self._charge_indicator, "state")
                self.canvas.itemconfigure(self._charge_indicator, state=("hidden" if state == "normal" else "normal"))
        else:
            if hasattr(self, "_charge_indicator"):
                self.canvas.delete(self._charge_indicator)
                delattr(self, "_charge_indicator")

        # Texto superior con rates
        rates_txt = "  ".join([f"{r}=+{st['rates'][r]}/tick" for r in ROOMS])
        self.lbl_info.config(
            text=f"Posición: {st['posicion']}   •   Batería: {st['bateria']}%   •   Rates: {rates_txt}"
        )

        # Ajustar posición visual si cambió por decisiones
        self.move_vacuum_to_room_center(st["posicion"])

        # --- Actualizar barra de batería ---
        # usar width proporcional al % de batería
        batt_pct = max(0, min(100, int(st["bateria"])))
        # get current bg coords to compute width and position
        x1, y1, x2, y2 = self.canvas.coords(self.batt_bg)
        total_w = x2 - x1
        fill_w = total_w * (batt_pct / 100.0)
        self.canvas.coords(self.batt_fg, x1, y1, x1 + fill_w, y2)
        self.canvas.itemconfigure(self.batt_text, text=f"Batería {batt_pct}%")

        # --- Actualizar barra de limpieza ---
        if st["cleaning"] and st["clean_total"] > 0:
            rem = st["clean_remaining"]
            tot = st["clean_total"]
            progress = (tot - rem) / tot if tot > 0 else 0.0
            # clamp
            progress = 0.0 if progress < 0 else (1.0 if progress > 1.0 else progress)
            x1c, y1c, x2c, y2c = self.canvas.coords(self.clean_bg)
            total_wc = x2c - x1c
            self.canvas.coords(self.clean_fg, x1c, y1c, x1c + total_wc * progress, y2c)
            self.canvas.itemconfigure(self.clean_text, text=f"Limpieza {rem:.1f}s")
        else:
            # reset cleaning bar to 0
            x1c, y1c, x2c, y2c = self.canvas.coords(self.clean_bg)
            self.canvas.coords(self.clean_fg, x1c, y1c, x1c, y2c)
            self.canvas.itemconfigure(self.clean_text, text="Limpieza 0.0s")

        self.root.after(100, self._tick)

    def on_close(self):
        self.controller.stop()
        self.sim.stop_event.set()
        for t in self.sim.threads:
            t.join(timeout=1.0)
        self.root.destroy()

def main():
    sim = VacuumSim()
    controller = AutoController(sim)
    app = VacuumGUI(sim, controller)
    app.root.mainloop()

if __name__ == "__main__":
    main()