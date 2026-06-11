import cv2
import numpy as np

class BrushRenderer:
    """
    Clase encargada de renderizar los trazos visuales sobre los lienzos de dibujo,
    manejando los diferentes efectos matemáticos para cada estilo de pincel.
    """
    @staticmethod
    def draw(active_brush, solid_canvas, add_canvas, p1, p2, color, thickness):
        """
        Dibuja un trazo conectando el punto previo (p1) con el actual (p2)
        usando el estilo de pincel activo.
        """
        w, h = solid_canvas.shape[1], solid_canvas.shape[0]
        
        if active_brush == "Normal":
            # Trazo solido y regular
            cv2.line(solid_canvas, p1, p2, color, thickness)
            
        elif active_brush == "Spray":
            # Distribuye puntos aleatoriamente usando distribucion normal (campana de Gauss)
            for _ in range(thickness * 3):
                offset_x = int(np.random.normal(0, thickness // 2))
                offset_y = int(np.random.normal(0, thickness // 2))
                rx, ry = p2[0] + offset_x, p2[1] + offset_y
                if 0 <= rx < w and 0 <= ry < h:
                    cv2.circle(add_canvas, (rx, ry), 1, color, -1)
                    
        elif active_brush == "Neon":
            # Trazo doble: borde oscuro grueso y nucleo blanco delgado brillante
            cv2.line(add_canvas, p1, p2, color, thickness * 2)
            cv2.line(add_canvas, p1, p2, (255, 255, 255), max(1, thickness // 2))
            
        elif active_brush == "Acuarela":
            # Trazo grueso semitransparente usando Alpha Blend (10% opacidad)
            overlay = add_canvas.copy()
            cv2.line(overlay, p1, p2, color, thickness * 3)
            cv2.addWeighted(overlay, 0.1, add_canvas, 0.9, 0, add_canvas)
            
    @staticmethod
    def erase(solid_canvas, add_canvas, p1, p2, thickness=100):
        """Aplica el borrador dibujando color negro sobre todos los lienzos."""
        cv2.line(solid_canvas, p1, p2, (0, 0, 0), thickness)
        cv2.line(add_canvas, p1, p2, (0, 0, 0), thickness)
