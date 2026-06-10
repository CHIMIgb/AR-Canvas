import cv2
import mediapipe as mp
import numpy as np

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

    # Variables de Fase 2: Canvas y seguimiento
    canvas = None
    px, py = 0, 0

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
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Visualizar los 21 landmarks en pantalla
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Aislar el landmark del dedo índice (punto 8)
                index_finger_tip = hand_landmarks.landmark[8]
                
                # Obtener las dimensiones del frame
                h, w, c = frame.shape
                
                # Convertir coordenadas normalizadas a píxeles
                cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                
                # Fase 2: Lógica de trazado
                if canvas is None:
                    canvas = np.zeros_like(frame)

                if px == 0 and py == 0:
                    px, py = cx, cy

                # Pincel levantado (ignorar si el salto es muy grande, e.g. falso positivo o movimiento brusco)
                # Al estar en HD (1280x720), 100 píxeles era muy poco. Subimos el umbral a 300.
                if np.hypot(cx - px, cy - py) > 300:
                    px, py = cx, cy

                # Trazar línea en el canvas
                cv2.line(canvas, (px, py), (cx, cy), (255, 0, 255), 10)
                px, py = cx, cy

                # Dibujar un círculo sobre la punta del índice (cursor)
                cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        else:
            # Si se pierde la mano, reiniciar la posición previa
            px, py = 0, 0

        # Fusionar el canvas con el frame en tiempo real
        if canvas is not None:
            frame = cv2.addWeighted(frame, 1, canvas, 1, 0)

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
