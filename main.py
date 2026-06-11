import cv2
import mediapipe as mp
import numpy as np
from collections import deque

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

    print("Iniciando AR Canvas - Fase 2")
    print("Presiona 'q' para salir.")

    # Variables de Seguimiento y Canvas
    canvas = None
    px, py = 0, 0
    points_buffer = deque(maxlen=5)

    # Variables de Fase 4: Gestos y UI
    tip_ids = [8, 12, 16, 20] # Índices de las puntas de los dedos (Índice, Medio, Anular, Meñique)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)] # BGR: Azul, Verde, Rojo, Amarillo
    color_idx = 0
    draw_color = colors[color_idx]
    clear_counter = 0 # Contador para confirmación de borrado

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("No se pudo capturar el frame de la cámara.")
            break

        # Voltear el frame horizontalmente para que actúe como un espejo
        frame = cv2.flip(frame, 1)
        
        # Convertir a RGB (MediaPipe usa RGB)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar el frame para detectar manos
        results = hands.process(img_rgb)
        
        h, w, c = frame.shape
        if canvas is None:
            canvas = np.zeros_like(frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Fase 4: Detectar dedos levantados
                fingers = []
                for id in tip_ids:
                    # Comparamos la punta (id) con la articulación media (id - 2)
                    if hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # Obtener posición del dedo índice (punto 8)
                index_finger_tip = hand_landmarks.landmark[8]
                cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                
                # Suavizado
                if len(points_buffer) > 0:
                    last_cx, last_cy = points_buffer[-1]
                    if np.hypot(cx - last_cx, cy - last_cy) > 300:
                        points_buffer.clear()
                        px, py = 0, 0

                points_buffer.append((cx, cy))
                smooth_cx = int(np.mean([p[0] for p in points_buffer]))
                smooth_cy = int(np.mean([p[1] for p in points_buffer]))

                # Resetear contador si no es puño
                if fingers != [0, 0, 0, 0]:
                    clear_counter = 0

                # Lógica de Gestos (Fase 4)
                if fingers == [1, 1, 0, 0]:
                    # MODO MOVER / SELECCIÓN
                    cv2.circle(frame, (smooth_cx, smooth_cy), 15, draw_color, 2)
                    px, py = 0, 0 # Romper el trazo
                    
                    # Chequear si está seleccionando un color en la UI
                    if smooth_cy < 100:
                        for i, color in enumerate(colors):
                            if 200 + i*150 < smooth_cx < 300 + i*150:
                                color_idx = i
                                draw_color = colors[color_idx]

                elif fingers == [1, 0, 0, 0]:
                    # MODO PINTAR
                    cv2.circle(frame, (smooth_cx, smooth_cy), 15, draw_color, cv2.FILLED)
                    if px != 0 and py != 0:
                        cv2.line(canvas, (px, py), (smooth_cx, smooth_cy), draw_color, 10)
                    px, py = smooth_cx, smooth_cy

                elif fingers == [1, 1, 1, 1]:
                    # MODO BORRADOR
                    cv2.circle(frame, (smooth_cx, smooth_cy), 40, (0, 0, 0), cv2.FILLED)
                    cv2.circle(frame, (smooth_cx, smooth_cy), 40, (255, 255, 255), 2)
                    if px != 0 and py != 0:
                        cv2.line(canvas, (px, py), (smooth_cx, smooth_cy), (0, 0, 0), 80)
                    px, py = smooth_cx, smooth_cy

                elif fingers == [0, 0, 0, 0]:
                    # MODO LIMPIAR CANVAS (con confirmación de tiempo)
                    clear_counter += 1
                    
                    # Dibujar barra de progreso del borrado
                    cv2.putText(frame, "Mantenga el puno para borrar", (w//2 - 250, h//2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    # Progreso dinámico hasta 60 frames (aprox 2 segundos a 30fps)
                    progreso = min(clear_counter, 60)
                    ancho_barra = int((progreso / 60.0) * 450)
                    cv2.rectangle(frame, (w//2 - 250, h//2), (w//2 - 250 + ancho_barra, h//2 + 30), (0, 0, 255), cv2.FILLED)
                    cv2.rectangle(frame, (w//2 - 250, h//2), (w//2 - 250 + 450, h//2 + 30), (255, 255, 255), 3)

                    if clear_counter > 60: # Aprox 2 segundos a 30fps
                        canvas = np.zeros_like(frame)
                        cv2.putText(frame, "CANVAS LIMPIO", (w//2 - 200, h//2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
                        
                    px, py = 0, 0
                
                else:
                    # Gesto no definido (pausa)
                    px, py = 0, 0
        else:
            # Si se pierde la mano
            px, py = 0, 0
            points_buffer.clear()

        # Fusionar el canvas con el frame
        frame = cv2.addWeighted(frame, 1, canvas, 1, 0)

        # Dibujar UI sobre el frame final
        cv2.rectangle(frame, (0, 0), (w, 100), (40, 40, 40), cv2.FILLED)
        for i, color in enumerate(colors):
            cv2.rectangle(frame, (200 + i*150, 10), (300 + i*150, 90), color, cv2.FILLED)
            if i == color_idx:
                cv2.rectangle(frame, (190 + i*150, 0), (310 + i*150, 100), (255, 255, 255), 3)

        # Mostrar el frame
        cv2.imshow("AR Canvas", frame)

        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
