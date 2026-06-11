import cv2
import mediapipe as mp
import numpy as np
from collections import deque

class HandTracker:
    """
    Clase encargada de rastrear hasta 2 manos, detectar gestos, suavizar el movimiento
    y calcular la interacción bimanual (Iron Man Mode).
    """
    def __init__(self, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [8, 12, 16, 20] # Índice, Medio, Anular, Meñique
        self.points_buffer = deque(maxlen=5)
        
    def _get_fingers(self, hand_landmarks):
        fingers = []
        for id in self.tip_ids:
            if hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def process_frame(self, frame):
        """
        Procesa el frame actual y devuelve el estado separado de ambas manos.
        Nota: La imagen debe pasarse SIN espejar a MediaPipe para que la clasificacion sea correcta,
        o manejar la inversion manualmente.
        """
        h, w, c = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        state = {
            "right": {
                "detected": False,
                "fingers": [],
                "cx": 0, "cy": 0,
                "smooth_cx": 0, "smooth_cy": 0,
                "pinch_dist": 0,
                "jump_detected": False
            },
            "left": {
                "detected": False,
                "landmarks": None,
                "fingers": []
            }
        }
        
        right_detected = False

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Extraer etiqueta de mano (Left o Right)
                # Al estar la imagen espejada ANTES de pasarse, la mano fisica derecha
                # del usuario sera leida por MediaPipe como "Left" o "Right" dependiendo del flip.
                # Como hacemos cv2.flip() a toda la imagen, la mano fisica DERECHA 
                # sera clasificada como "Right" porque ahora parece una mano derecha frente a la camara.
                label = results.multi_handedness[idx].classification[0].label
                
                if label == "Right":
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    right_detected = True
                    r_state = state["right"]
                    r_state["detected"] = True
                    r_state["fingers"] = self._get_fingers(hand_landmarks)

                    index_tip = hand_landmarks.landmark[8]
                    thumb_tip = hand_landmarks.landmark[4]
                    
                    cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                    tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    
                    r_state["cx"], r_state["cy"] = cx, cy
                    r_state["pinch_dist"] = np.hypot(cx - tx, cy - ty)
                    
                    if len(self.points_buffer) > 0:
                        last_cx, last_cy = self.points_buffer[-1]
                        if np.hypot(cx - last_cx, cy - last_cy) > 300:
                            self.points_buffer.clear()
                            r_state["jump_detected"] = True

                    self.points_buffer.append((cx, cy))
                    r_state["smooth_cx"] = int(np.mean([p[0] for p in self.points_buffer]))
                    r_state["smooth_cy"] = int(np.mean([p[1] for p in self.points_buffer]))

                elif label == "Left":
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS, 
                                                self.mp_draw.DrawingSpec(color=(0,255,255), thickness=2, circle_radius=4),
                                                self.mp_draw.DrawingSpec(color=(255,0,0), thickness=2))
                    l_state = state["left"]
                    l_state["detected"] = True
                    l_state["landmarks"] = hand_landmarks
                    l_state["fingers"] = self._get_fingers(hand_landmarks)

        if not right_detected:
            self.points_buffer.clear()
            
        return state
