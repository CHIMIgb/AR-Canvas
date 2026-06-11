import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import os
import datetime
import imageio

def main():
    # Inicializar MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    mp_draw = mp.solutions.drawing_utils

    # Capturar video desde la cámara web
    cap = cv2.VideoCapture(0)
    
    # Configurar resolución a 1280x720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("Iniciando AR Canvas - Fase 5")
    print("Presiona 'q' para salir.")

    # Variables de Seguimiento y Canvas
    solid_canvas = None
    add_canvas = None
    px, py = 0, 0
    points_buffer = deque(maxlen=5)

    # Variables de Fase 4 y 5: Gestos, UI y Pinceles
    tip_ids = [8, 12, 16, 20]
    
    # Generar Paleta de Colores Avanzada
    palette_cols = 12
    palette_rows = 5
    block_w = 40
    block_h = 20
    palette_x = 400
    palette_y = 0
    palette_img = np.zeros((palette_rows * block_h, palette_cols * block_w, 3), dtype=np.uint8)
    colors_grid = []

    for r in range(palette_rows):
        row_colors = []
        for c in range(palette_cols):
            if c == palette_cols - 1: # Última columna: grises
                val = 255 - (r * 255 // (palette_rows - 1))
                color = (val, val, val)
            else:
                hue = int(c * 179 / (palette_cols - 2))
                if r == 0: sat, val = 100, 255
                elif r == 1: sat, val = 255, 255
                elif r == 2: sat, val = 255, 200
                elif r == 3: sat, val = 255, 120
                else: sat, val = 255, 60
                
                hsv = np.uint8([[[hue, sat, val]]])
                bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
                color = (int(bgr[0]), int(bgr[1]), int(bgr[2]))
            
            row_colors.append(color)
            cv2.rectangle(palette_img, (c*block_w, r*block_h), ((c+1)*block_w, (r+1)*block_h), color, cv2.FILLED)
        colors_grid.append(row_colors)

    draw_color = colors_grid[1][0] # Rojo brillante por defecto
    color_rect = (palette_x + 0*block_w, palette_y + 1*block_h, block_w, block_h)
    
    brush_types = ["Normal", "Spray", "Neon", "Acuarela"]
    brush_idx = 0
    active_brush = brush_types[brush_idx]
    
    brush_thickness = 10
    clear_counter = 0

    gif_buffer = deque(maxlen=150) # Buffer para 5 segundos a 30fps
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("No se pudo capturar el frame de la cámara.")
            break

        # Voltear el frame horizontalmente
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        if solid_canvas is None:
            solid_canvas = np.zeros_like(frame)
            add_canvas = np.zeros_like(frame)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Detectar dedos levantados (ignorando pulgar para el estado principal)
                fingers = []
                for id in tip_ids:
                    if hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # Obtener posiciones de índice y pulgar
                index_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
                
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                
                # Distancia entre índice y pulgar (Pellizco)
                pinch_dist = np.hypot(cx - tx, cy - ty)
                
                # Suavizado
                if len(points_buffer) > 0:
                    last_cx, last_cy = points_buffer[-1]
                    if np.hypot(cx - last_cx, cy - last_cy) > 300:
                        points_buffer.clear()
                        px, py = 0, 0

                points_buffer.append((cx, cy))
                smooth_cx = int(np.mean([p[0] for p in points_buffer]))
                smooth_cy = int(np.mean([p[1] for p in points_buffer]))

                if fingers != [0, 0, 0, 0]:
                    clear_counter = 0

                # Lógica de Gestos
                if fingers == [1, 1, 1, 0]:
                    # MODO AJUSTAR GROSOR (Tres dedos: Índice, Medio, Anular)
                    brush_thickness = int(np.clip(pinch_dist / 3, 5, 60))
                    cv2.circle(frame, (smooth_cx, smooth_cy), brush_thickness, draw_color, 2)
                    cv2.putText(frame, "Grosor", (smooth_cx - 40, smooth_cy - brush_thickness - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    px, py = 0, 0

                elif fingers == [1, 1, 0, 0]:
                    # MODO MOVER / SELECCIÓN
                    cv2.circle(frame, (smooth_cx, smooth_cy), 15, draw_color, 2)
                    px, py = 0, 0
                    
                    # Seleccionar Color (UI Paleta Avanzada)
                    if palette_x <= smooth_cx < palette_x + palette_cols * block_w and palette_y <= smooth_cy < palette_y + palette_rows * block_h:
                        c = (smooth_cx - palette_x) // block_w
                        r = (smooth_cy - palette_y) // block_h
                        if 0 <= c < palette_cols and 0 <= r < palette_rows:
                            draw_color = colors_grid[r][c]
                            color_rect = (palette_x + c*block_w, palette_y + r*block_h, block_w, block_h)
                                
                    # Seleccionar Pincel (UI Izquierda)
                    elif smooth_cx < 200 and 150 < smooth_cy < 150 + 4 * 80:
                        for i in range(len(brush_types)):
                            if 150 + i * 80 < smooth_cy < 150 + (i + 1) * 80:
                                brush_idx = i
                                active_brush = brush_types[brush_idx]

                elif fingers == [1, 0, 0, 0]:
                    # MODO PINTAR
                    cv2.circle(frame, (smooth_cx, smooth_cy), brush_thickness, draw_color, cv2.FILLED)
                    if px != 0 and py != 0:
                        # Seleccionar tipo de pincel
                        if active_brush == "Normal":
                            cv2.line(solid_canvas, (px, py), (smooth_cx, smooth_cy), draw_color, brush_thickness)
                        
                        elif active_brush == "Spray":
                            for _ in range(brush_thickness * 3):
                                offset_x = int(np.random.normal(0, brush_thickness // 2))
                                offset_y = int(np.random.normal(0, brush_thickness // 2))
                                rx, ry = smooth_cx + offset_x, smooth_cy + offset_y
                                if 0 <= rx < w and 0 <= ry < h:
                                    cv2.circle(add_canvas, (rx, ry), 1, draw_color, -1)
                        
                        elif active_brush == "Neon":
                            # Efecto Neon
                            cv2.line(add_canvas, (px, py), (smooth_cx, smooth_cy), draw_color, brush_thickness * 2)
                            cv2.line(add_canvas, (px, py), (smooth_cx, smooth_cy), (255, 255, 255), max(1, brush_thickness // 2))
                        
                        elif active_brush == "Acuarela":
                            # Acuarela
                            overlay = add_canvas.copy()
                            cv2.line(overlay, (px, py), (smooth_cx, smooth_cy), draw_color, brush_thickness * 3)
                            cv2.addWeighted(overlay, 0.1, add_canvas, 0.9, 0, add_canvas)
                            
                    px, py = smooth_cx, smooth_cy

                elif fingers == [1, 1, 1, 1]:
                    # MODO BORRADOR
                    cv2.circle(frame, (smooth_cx, smooth_cy), 50, (0, 0, 0), cv2.FILLED)
                    cv2.circle(frame, (smooth_cx, smooth_cy), 50, (255, 255, 255), 2)
                    if px != 0 and py != 0:
                        cv2.line(solid_canvas, (px, py), (smooth_cx, smooth_cy), (0, 0, 0), 100)
                        cv2.line(add_canvas, (px, py), (smooth_cx, smooth_cy), (0, 0, 0), 100)
                    px, py = smooth_cx, smooth_cy

                elif fingers == [0, 0, 0, 0]:
                    # MODO LIMPIAR CANVAS
                    clear_counter += 1
                    cv2.putText(frame, "Mantenga el puno para borrar", (w//2 - 250, h//2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    progreso = min(clear_counter, 60)
                    ancho_barra = int((progreso / 60.0) * 450)
                    cv2.rectangle(frame, (w//2 - 250, h//2), (w//2 - 250 + ancho_barra, h//2 + 30), (0, 0, 255), cv2.FILLED)
                    cv2.rectangle(frame, (w//2 - 250, h//2), (w//2 - 250 + 450, h//2 + 30), (255, 255, 255), 3)

                    if clear_counter > 60:
                        solid_canvas = np.zeros_like(frame)
                        add_canvas = np.zeros_like(frame)
                        cv2.putText(frame, "CANVAS LIMPIO", (w//2 - 200, h//2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
                    px, py = 0, 0
                else:
                    px, py = 0, 0
        else:
            px, py = 0, 0
            points_buffer.clear()

        # Fusionar los canvas con el frame
        if solid_canvas is not None and add_canvas is not None:
            # 1. Fusión Aditiva (Neon, Spray, Acuarela)
            frame = cv2.addWeighted(frame, 1, add_canvas, 1, 0)
            
            # 2. Fusión Sólida (Normal)
            canvas_gray = cv2.cvtColor(solid_canvas, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(canvas_gray, 1, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            
            frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
            frame = cv2.add(frame_bg, solid_canvas)

        # UI Colores (Paleta Avanzada)
        # Dibujar fondo oscuro detrás de la paleta para que destaque
        cv2.rectangle(frame, (palette_x - 10, palette_y), (palette_x + palette_cols * block_w + 10, palette_y + palette_rows * block_h + 10), (40, 40, 40), cv2.FILLED)
        # Copiar imagen de paleta al frame
        frame[palette_y:palette_y + palette_rows * block_h, palette_x:palette_x + palette_cols * block_w] = palette_img
        
        # Resaltar color seleccionado
        if color_rect:
            cx_rect, cy_rect, cw, ch = color_rect
            cv2.rectangle(frame, (cx_rect, cy_rect), (cx_rect + cw, cy_rect + ch), (255, 255, 255), 3)

        # UI Pinceles (Izquierda)
        cv2.rectangle(frame, (0, 150), (200, 150 + len(brush_types) * 80), (40, 40, 40), cv2.FILLED)
        for i, b in enumerate(brush_types):
            y1 = 150 + i * 80
            y2 = y1 + 80
            cv2.putText(frame, b, (20, y1 + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            if i == brush_idx:
                cv2.rectangle(frame, (0, y1), (200, y2), (255, 255, 255), 3)

        # UI de Grosor Actual
        cv2.putText(frame, f"Grosor: {brush_thickness}", (w - 250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # UI Instrucciones (Derecha)
        instructions = [
            "1 Dedo: Pintar",
            "2 Dedos: Seleccionar",
            "3 Dedos + Pellizcar: Grosor",
            "Mano Abierta: Borrador",
            "Puno (2s): Limpiar",
            "S: Guardar PNG",
            "G: Guardar GIF (5s)"
        ]
        cv2.rectangle(frame, (w - 320, 100), (w, 110 + len(instructions) * 30), (30, 30, 30), cv2.FILLED)
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (w - 310, 135 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Buffer para exportación a GIF
        small_frame = cv2.resize(frame, (640, 360))
        gif_buffer.append(cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB))

        cv2.imshow("AR Canvas", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/canvas_{ts}.png"
            cv2.imwrite(filename, frame)
            print(f"Imagen guardada: {filename}")
        elif key == ord('g'):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/proceso_{ts}.gif"
            print("Guardando GIF... (esto congelara la camara un momento)")
            imageio.mimsave(filename, list(gif_buffer), fps=30)
            print(f"GIF guardado: {filename}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
