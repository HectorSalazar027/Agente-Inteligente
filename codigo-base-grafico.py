"""
Aspiradora gráfica simple con Tkinter
Muestra 4 habitaciones (2x2). Cada habitación se va llenando de manera progresiva
conforme pasa el tiempo (12%, 34%, 48%, 60%, 78%, 100%).
Cuando la aspiradora pasa por una habitación, su porcentaje se reinicia a 0%.

Cómo usar:
    python3 aspiradora_grafica.py
Controles:
    Flechas - mover la aspiradora
    Espacio - centrar aspiradora en la habitación 1
    q o Esc - salir

"""

import tkinter as tk

WIDTH, HEIGHT = 800, 600
PADDING = 40
ROOM_GAP = 20
FILL_STEPS = [0.12, 0.34, 0.48, 0.60, 0.78, 1.0]  # porcentajes
FILL_INTERVAL = 1500  # milisegundos entre actualizaciones

class AspiradoraGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Aspiradora Inteligente - Visor Gráfico")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#f0f0f0")
        self.canvas.pack()

        # Calcular tamaño de cada habitación (2x2)
        room_width = (WIDTH - 2 * PADDING - ROOM_GAP) // 2
        room_height = (HEIGHT - 2 * PADDING - ROOM_GAP) // 2
        self.rooms = []  # lista de rects: (x1,y1,x2,y2)

        for row in range(2):
            for col in range(2):
                x1 = PADDING + col * (room_width + ROOM_GAP)
                y1 = PADDING + row * (room_height + ROOM_GAP)
                x2 = x1 + room_width
                y2 = y1 + room_height
                self.rooms.append((x1, y1, x2, y2))

        # Inicializar estado de llenado
        self.fill_index = [0 for _ in self.rooms]  # índice de paso por habitación
        self.fill_rects = []
        self.fill_labels = []

        # Dibujar habitaciones vacías
        self.draw_rooms()

        # Aspiradora: posición inicial centro de la habitación 1
        self.vacuum_radius = 18
        r = self.rooms[0]
        cx = (r[0] + r[2]) / 2
        cy = (r[1] + r[3]) / 2
        self.vacuum = {'x': cx, 'y': cy, 'id': None}
        self.draw_vacuum()

        # Eventos teclado
        root.bind('<Left>', lambda e: self.move_vacuum(-20, 0))
        root.bind('<Right>', lambda e: self.move_vacuum(20, 0))
        root.bind('<Up>', lambda e: self.move_vacuum(0, -20))
        root.bind('<Down>', lambda e: self.move_vacuum(0, 20))
        root.bind('<space>', lambda e: self.reset_to_room(0))
        root.bind('q', lambda e: root.destroy())
        root.bind('<Escape>', lambda e: root.destroy())

        # Indicador de habitación actual
        self.info_text = self.canvas.create_text(WIDTH - 10, 10, anchor='ne', text='', font=('Helvetica', 12, 'bold'))
        self.update_info()

        # Iniciar llenado automático
        self.update_fill()

    def draw_rooms(self):
        colors = ['#ffffff', '#fff8e1', '#f1f8e9', '#e3f2fd']

        for i, rect in enumerate(self.rooms):
            x1, y1, x2, y2 = rect
            # contorno de habitación
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[i % len(colors)], outline='#444', width=2)
            # etiqueta
            self.canvas.create_text(x1 + 8, y1 + 8, anchor='nw', text=f'Habitación {i+1}', font=('Helvetica', 10, 'bold'))
            # rectángulo de llenado (vacío al inicio)
            fill_id = self.canvas.create_rectangle(x1, y2, x2, y2, fill='#4caf50', outline='')
            self.fill_rects.append(fill_id)
            # texto del porcentaje
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            label_id = self.canvas.create_text(cx, cy, text="0%", font=('Helvetica', 14, 'bold'))
            self.fill_labels.append(label_id)

    def draw_vacuum(self):
        if self.vacuum['id']:
            self.canvas.delete(self.vacuum['id'])
        x = self.vacuum['x']
        y = self.vacuum['y']
        r = self.vacuum_radius
        body = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill='#607d8b', outline='#263238', width=2)
        wnd = self.canvas.create_oval(x - r/2, y - r/2, x - r/6, y - r/6, fill='#cfd8dc', outline='')
        antenna = self.canvas.create_line(x, y - r, x, y - r - 14, width=3)
        tag = 'vacuum'
        for item in (body, wnd, antenna):
            self.canvas.addtag_withtag(tag, item)
        self.vacuum['id'] = tag

    def move_vacuum(self, dx, dy):
        new_x = self.vacuum['x'] + dx
        new_y = self.vacuum['y'] + dy
        min_x = PADDING
        min_y = PADDING
        max_x = WIDTH - PADDING
        max_y = HEIGHT - PADDING
        r = self.vacuum_radius
        new_x = max(min_x + r, min(max_x - r, new_x))
        new_y = max(min_y + r, min(max_y - r, new_y))
        dx = new_x - self.vacuum['x']
        dy = new_y - self.vacuum['y']
        self.vacuum['x'] = new_x
        self.vacuum['y'] = new_y
        self.canvas.move('vacuum', dx, dy)
        self.update_info()
        self.check_reset_fill()

    def reset_to_room(self, idx):
        if idx < 0 or idx >= len(self.rooms):
            return
        x1, y1, x2, y2 = self.rooms[idx]
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        dx = cx - self.vacuum['x']
        dy = cy - self.vacuum['y']
        self.move_vacuum(dx, dy)

    def current_room_index(self):
        x = self.vacuum['x']
        y = self.vacuum['y']
        for i, (x1, y1, x2, y2) in enumerate(self.rooms):
            if x1 <= x <= x2 and y1 <= y <= y2:
                return i
        return None

    def update_info(self):
        idx = self.current_room_index()
        if idx is None:
            text = 'Aspiradora: en pasillo'
        else:
            text = f'Aspiradora: Habitación {idx+1}'
        self.canvas.itemconfigure(self.info_text, text=text)

    def update_fill(self):
        for i, rect in enumerate(self.rooms):
            if self.fill_index[i] < len(FILL_STEPS):
                x1, y1, x2, y2 = rect
                percent = FILL_STEPS[self.fill_index[i]]
                fill_height = (y2 - y1) * percent
                new_y = y2 - fill_height
                self.canvas.coords(self.fill_rects[i], x1, new_y, x2, y2)
                self.canvas.itemconfigure(self.fill_labels[i], text=f"{int(percent*100)}%")
                self.fill_index[i] += 1
        if any(idx < len(FILL_STEPS) for idx in self.fill_index):
            self.root.after(FILL_INTERVAL, self.update_fill)

    def check_reset_fill(self):
        idx = self.current_room_index()
        if idx is not None:
            # reiniciar la habitación donde entra la aspiradora
            self.fill_index[idx] = 0
            x1, y1, x2, y2 = self.rooms[idx]
            self.canvas.coords(self.fill_rects[idx], x1, y2, x2, y2)
            self.canvas.itemconfigure(self.fill_labels[idx], text="0%")

if __name__ == '__main__':
    root = tk.Tk()
    app = AspiradoraGrafica(root)
    root.mainloop()
