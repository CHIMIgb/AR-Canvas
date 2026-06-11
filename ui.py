import cv2
import numpy as np

class UIManager:
    """
    Clase para gestionar la interfaz holográfica bimanual: 
    dibuja la paleta flotando sobre la mano izquierda.
    """
    def __init__(self):
        self.brush_types = ["Normal", "Spray", "Neon", "Acuarela"]
        
        # Parámetros de Paleta HSV
        self.palette_cols = 12
        self.palette_rows = 5
        self.block_w = 30 # Mas pequeños para que floten bien
        self.block_h = 20
        self.palette_img, self.colors_grid = self._generate_palette()
        
        # Coordenadas actuales en pantalla (variables)
        self.current_px = 0
        self.current_py = 0
        self.current_brush_rects = []
        
    def _generate_palette(self):
        palette = np.zeros((self.palette_rows * self.block_h, self.palette_cols * self.block_w, 3), dtype=np.uint8)
        colors = []
        for r in range(self.palette_rows):
            row_colors = []
            for c in range(self.palette_cols):
                if c == self.palette_cols - 1:
                    val = 255 - (r * 255 // (self.palette_rows - 1))
                    color = (val, val, val)
                else:
                    hue = int(c * 179 / (self.palette_cols - 2))
                    if r == 0: sat, val = 100, 255
                    elif r == 1: sat, val = 255, 255
                    elif r == 2: sat, val = 255, 200
                    elif r == 3: sat, val = 255, 120
                    else: sat, val = 255, 60
                    
                    hsv = np.uint8([[[hue, sat, val]]])
                    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
                    color = (int(bgr[0]), int(bgr[1]), int(bgr[2]))
                
                row_colors.append(color)
                cv2.rectangle(palette, (c*self.block_w, r*self.block_h), ((c+1)*self.block_w, (r+1)*self.block_h), color, cv2.FILLED)
            colors.append(row_colors)
        return palette, colors

    def draw_floating_ui(self, frame, left_landmarks, color_rect, brush_idx):
        """
        Dibuja la paleta de colores y herramientas ancladas a la muñeca de la mano izquierda.
        """
        h, w, _ = frame.shape
        wrist = left_landmarks.landmark[0]
        wx, wy = int(wrist.x * w), int(wrist.y * h)
        
        pw = self.palette_cols * self.block_w
        ph = self.palette_rows * self.block_h
        
        # Posicionar arriba de la mano izquierda
        px = np.clip(wx - pw // 2, 0, w - pw)
        py = np.clip(wy - 250, 0, h - ph)
        
        self.current_px = px
        self.current_py = py
        
        # 1. Dibujar Paleta de Colores
        cv2.rectangle(frame, (px - 5, py - 5), (px + pw + 5, py + ph + 5), (40, 40, 40), cv2.FILLED)
        frame[py:py + ph, px:px + pw] = self.palette_img
        
        if color_rect:
            cx_rect, cy_rect, cw, ch = color_rect
            # Ajustar posiciones relativas al arrastrar la UI
            cv2.rectangle(frame, (px + cx_rect, py + cy_rect), (px + cx_rect + cw, py + cy_rect + ch), (255, 255, 255), 3)

        # 2. Dibujar Pinceles (Botones redondos/cuadrados debajo de la paleta)
        self.current_brush_rects = []
        for i, b in enumerate(self.brush_types):
            bx = px + i * 90
            by = py + ph + 10
            bw, bh = 85, 30
            cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (60, 60, 60), cv2.FILLED)
            cv2.putText(frame, b, (bx + 5, by + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            if i == brush_idx:
                cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (255, 255, 255), 2)
            self.current_brush_rects.append((bx, by, bw, bh))

        # 3. Rayo Laser holografico de conexion (Iron Man estético)
        cv2.line(frame, (wx, wy), (px + pw//2, py + ph + 45), (0, 255, 255), 2)
        cv2.circle(frame, (wx, wy), 8, (0, 255, 255), cv2.FILLED)

    def draw_static_ui(self, frame, brush_thickness):
        """Dibuja info estática como grosor y atajos."""
        h, w, _ = frame.shape
        cv2.putText(frame, f"Grosor: {brush_thickness}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        instructions = [
            "AR CANVAS",
            "Mano Izquierda: Activa Paleta",
            "1 Dedo Derecho: Pintar/Seleccionar",
            "3 Dedos Der: Grosor",
            "Mano Der Abierta: Borrador"
        ]
        cv2.rectangle(frame, (w - 320, 10), (w, 20 + len(instructions) * 30), (30, 30, 30), cv2.FILLED)
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (w - 310, 40 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 255, 255) if i==0 else (200, 200, 200), 2 if i==0 else 1)

    def check_spatial_clicks(self, smooth_cx, smooth_cy, draw_color, color_rect, active_brush, brush_idx):
        """Detecta colisiones entre el cursor derecho y la UI flotante de la mano izquierda."""
        # Check Paleta
        px, py = self.current_px, self.current_py
        pw = self.palette_cols * self.block_w
        ph = self.palette_rows * self.block_h
        
        if px <= smooth_cx < px + pw and py <= smooth_cy < py + ph:
            c = (smooth_cx - px) // self.block_w
            r = (smooth_cy - py) // self.block_h
            if 0 <= c < self.palette_cols and 0 <= r < self.palette_rows:
                draw_color = self.colors_grid[r][c]
                # Guardar el color rect de forma RELATIVA a la paleta para que se mueva con la mano
                color_rect = (c*self.block_w, r*self.block_h, self.block_w, self.block_h)
                    
        # Check Pinceles
        for i, (bx, by, bw, bh) in enumerate(self.current_brush_rects):
            if bx <= smooth_cx <= bx + bw and by <= smooth_cy <= by + bh:
                brush_idx = i
                active_brush = self.brush_types[brush_idx]
                    
        return draw_color, color_rect, active_brush, brush_idx
