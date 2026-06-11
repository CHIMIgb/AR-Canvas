import cv2
import os
import datetime
import imageio
from collections import deque
import numpy as np

from gestures import HandTracker
from canvas import CanvasManager
from ui import UIManager
from brushes import BrushRenderer

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("Iniciando AR Canvas - Fase 8 (Modo Iron Man)")
    
    tracker = HandTracker()
    ui = UIManager()
    canvas_manager = None
    
    px, py = 0, 0
    draw_color = ui.colors_grid[1][0]
    # Posición relativa inicial del resaltador
    color_rect = (0 * ui.block_w, 1 * ui.block_h, ui.block_w, ui.block_h)
    active_brush = ui.brush_types[0]
    brush_idx = 0
    brush_thickness = 10
    clear_counter = 0

    gif_buffer = deque(maxlen=150)
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        if canvas_manager is None:
            canvas_manager = CanvasManager(frame.shape)

        # 1. Rastrear Manos
        state = tracker.process_frame(frame)
        r_state = state["right"]
        l_state = state["left"]
        
        # Logica Mano Derecha (Pincel)
        if r_state["detected"]:
            fingers = r_state["fingers"]
            scx, scy = r_state["smooth_cx"], r_state["smooth_cy"]
            
            if r_state["jump_detected"]:
                px, py = 0, 0

            if fingers != [0, 0, 0, 0]:
                clear_counter = 0

            # Si la UI esta activa y hay 1 o 2 dedos, actuamos como selector espacial
            # Si la UI no esta activa, 1 dedo pinta.
            
            if l_state["detected"] and (fingers == [1, 0, 0, 0] or fingers == [1, 1, 0, 0]):
                # MODO SELECCION HOLOGRAFICA
                cv2.circle(frame, (scx, scy), 15, draw_color, 2)
                cv2.circle(frame, (scx, scy), 5, (255, 255, 255), cv2.FILLED)
                px, py = 0, 0
                draw_color, color_rect, active_brush, brush_idx = ui.check_spatial_clicks(
                    scx, scy, draw_color, color_rect, active_brush, brush_idx
                )

            elif fingers == [1, 1, 1, 0]:
                # MODO GROSOR
                brush_thickness = int(np.clip(r_state["pinch_dist"] / 3, 5, 60))
                cv2.circle(frame, (scx, scy), brush_thickness, draw_color, 2)
                cv2.putText(frame, "Grosor", (scx - 40, scy - brush_thickness - 20), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)
                px, py = 0, 0

            elif fingers == [1, 0, 0, 0]:
                # MODO PINTAR
                cv2.circle(frame, (scx, scy), brush_thickness, draw_color, cv2.FILLED)
                if px != 0 and py != 0:
                    BrushRenderer.draw(active_brush, canvas_manager.solid_canvas, canvas_manager.add_canvas, 
                                       (px, py), (scx, scy), draw_color, brush_thickness)
                px, py = scx, scy

            elif fingers == [1, 1, 1, 1]:
                # MODO BORRADOR
                cv2.circle(frame, (scx, scy), 50, (0, 0, 0), cv2.FILLED)
                cv2.circle(frame, (scx, scy), 50, (255, 255, 255), 2)
                if px != 0 and py != 0:
                    BrushRenderer.erase(canvas_manager.solid_canvas, canvas_manager.add_canvas, (px, py), (scx, scy))
                px, py = scx, scy

            elif fingers == [0, 0, 0, 0]:
                # MODO LIMPIAR
                clear_counter += 1
                progreso = min(clear_counter, 30)
                ancho_barra = int((progreso / 30.0) * 450)
                cv2.rectangle(frame, (w//2 - 250, h//2), (w//2 - 250 + ancho_barra, h//2 + 30), (0, 0, 255), cv2.FILLED)
                cv2.rectangle(frame, (w//2 - 250, h//2), (w//2 - 250 + 450, h//2 + 30), (255, 255, 255), 3)

                if clear_counter > 30:
                    canvas_manager.clear()
                    cv2.putText(frame, "CANVAS LIMPIO", (w//2 - 200, h//2 + 100), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 5)
                px, py = 0, 0
                
            else:
                px, py = 0, 0
        else:
            px, py = 0, 0

        # 2. Render de UI Flotante si la mano izquierda está visible
        if l_state["detected"]:
            ui.draw_floating_ui(frame, l_state["landmarks"], color_rect, brush_idx)

        # 3. Fusionar Canvas
        if canvas_manager is not None:
            frame = canvas_manager.blend_with_frame(frame)

        # 4. Dibujar UI estática superpuesta
        ui.draw_static_ui(frame, brush_thickness)

        # 5. Guardar Buffer
        small_frame = cv2.resize(frame, (640, 360))
        gif_buffer.append(cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB))
        cv2.imshow("AR Canvas", frame)

        # 6. Teclado
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        elif key == ord('s'):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/canvas_{ts}.png"
            cv2.imwrite(filename, frame)
            print(f"Imagen guardada: {filename}")
        elif key == ord('g'):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/proceso_{ts}.gif"
            print("Guardando GIF...")
            imageio.mimsave(filename, list(gif_buffer), fps=30)
            print(f"GIF guardado: {filename}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
