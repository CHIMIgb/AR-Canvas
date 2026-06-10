import cv2
import mediapipe as mp

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

    print("Iniciando AR Canvas - Fase 1")
    print("Presiona 'q' para salir.")

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
                
                # Dibujar un círculo sobre la punta del índice en tiempo real
                cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # Mostrar el frame
        cv2.imshow("AR Canvas - Fase 1", frame)

        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
