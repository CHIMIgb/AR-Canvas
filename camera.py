import cv2
from threading import Thread

class WebcamVideoStream:
    """
    Gestiona la lectura asíncrona de la cámara web utilizando un hilo en segundo plano (Threading).
    Esto evita que el bucle principal se bloquee esperando I/O (operaciones de entrada/salida),
    mejorando significativamente los FPS (Cuadros por Segundo) de la aplicación.
    """
    def __init__(self, src=0, width=1280, height=720, fps=60):
        # Inicializa la camara
        self.stream = cv2.VideoCapture(src)
        
        # Peticion al driver de video para maximizar rendimiento
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.stream.set(cv2.CAP_PROP_FPS, fps)
        
        # Lee el primer frame
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        # Inicia un hilo Daemon (se cierra cuando se cierra la app)
        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        # Bucle ininterrumpido que solo lee la camara
        while True:
            if self.stopped:
                self.stream.release()
                return
            
            # Almacena el ultimo frame en la memoria
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # Devuelve el ultimo frame listo inmediatamente (Sin esperar a la camara fisica)
        return self.grabbed, self.frame

    def stop(self):
        # Señal de detencion para el hilo
        self.stopped = True
