import cv2
import numpy as np

class CanvasManager:
    """
    Clase para gestionar los diferentes lienzos (sólido y aditivo) y su fusión con el frame de la cámara.
    """
    def __init__(self, shape):
        self.solid_canvas = np.zeros(shape, dtype=np.uint8)
        self.add_canvas = np.zeros(shape, dtype=np.uint8)
        
    def clear(self):
        """Limpia ambos lienzos, borrando todo lo dibujado."""
        self.solid_canvas.fill(0)
        self.add_canvas.fill(0)
        
    def blend_with_frame(self, frame):
        """
        Fusiona de manera inteligente los lienzos con el frame de fondo.
        - add_canvas usa fusión aditiva para mantener brillos y transparencias.
        - solid_canvas usa enmascarado sólido para tapar completamente el fondo.
        """
        # 1. Fusión Aditiva (Neon, Spray, Acuarela)
        frame_blended = cv2.addWeighted(frame, 1, self.add_canvas, 1, 0)
        
        # 2. Fusión Sólida (Normal)
        canvas_gray = cv2.cvtColor(self.solid_canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(canvas_gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        frame_bg = cv2.bitwise_and(frame_blended, frame_blended, mask=mask_inv)
        final_frame = cv2.add(frame_bg, self.solid_canvas)
        
        return final_frame
