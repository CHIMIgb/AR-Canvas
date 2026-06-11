# AR Canvas

**AR Canvas** es una aplicación de Realidad Aumentada (AR) basada en Python que permite dibujar en el aire utilizando las manos, sin necesidad de ratón ni teclado. Desarrollada con Computer Vision avanzado, es capaz de detectar gestos complejos en tiempo real para cambiar pinceles, colores, grosor y borrar contenido de forma orgánica e intuitiva.

Este proyecto fue diseñado como una demostración de arquitectura de software, UX y visión artificial aplicada.

---

## 🚀 Tecnologías Utilizadas

El proyecto está construido principalmente sobre las siguientes librerías y herramientas:
- **Python 3.10 / 3.11**
- **OpenCV (`opencv-python`)**: Procesamiento de video en tiempo real, manipulación de matrices de píxeles, máscaras y modos de fusión aditiva y sólida.
- **MediaPipe (`mediapipe`)**: Modelo de Machine Learning provisto por Google para detectar y rastrear la topología de la mano (21 landmarks) a gran velocidad.
- **NumPy (`numpy`)**: Base matemática fundamental para la gestión de píxeles, generación de paletas de color y distribución de coordenadas (Gaussian distribution para pinceles de spray).
- **ImageIO (`imageio`)**: Para la exportación de buffers de memoria hacia archivos GIF animados.

---

## 🛠️ Instalación y Ejecución

1. **Clona el repositorio:**
```bash
git clone https://github.com/tu-usuario/ar-canvas.git
cd ar-canvas
```

2. **Crea y activa un entorno virtual (Recomendado):**
```bash
python -m venv venv

# En Windows:
.\venv\Scripts\activate

# En Mac/Linux:
source venv/bin/activate
```

3. **Instala las dependencias necesarias:**
```bash
pip install -r requirements.txt
```
> **Nota:** Se aconseja utilizar Python 3.10 o 3.11 debido a la compatibilidad nativa óptima de los bindings precompilados de `mediapipe`.

4. **Ejecuta la aplicación:**
```bash
python main.py
```

---

## 🎮 Controles Auxiliares

Toda la aplicación gráfica se maneja mediante el seguimiento de las manos a través de tu webcam, pero cuenta con unos útiles atajos de teclado para exportación:

| Tecla | Acción |
| :---: | :--- |
| `S` | Guarda una captura instantánea en formato PNG dentro de la carpeta `outputs/`. |
| `G` | Renderiza y exporta los últimos 5 segundos de tu dibujo continuo a un archivo animado GIF. |
| `Q` | Cierra la aplicación y libera la cámara de forma segura. |

---

## 🏗️ Arquitectura de Software

El código fuente ha sido estructurado bajo principios de código limpio, aplicando el principio de responsabilidad única (SRP) a través de la programación orientada a objetos. El proyecto se subdivide en 5 módulos centrales:

- `main.py`: Punto de entrada del programa. Inicializa la cámara, instancia las clases especializadas y ejecuta el ciclo iterativo principal. Está diseñado para ser descriptivo y muy legible (menos de 150 líneas).
- `gestures.py`: Contiene la clase `HandTracker`, que abstrae toda la complejidad de MediaPipe. Determina qué dedos están levantados, calcula la distancia euclidiana entre el pulgar e índice (pellizco) y aplica un buffer de medias móviles para evitar vibraciones excesivas del puntero de la mano.
- `ui.py`: Contiene la clase `UIManager`, encargada de renderizar la interfaz gráfica flotante por encima de la cámara, incluyendo la generación procedural de una paleta de 60 colores en espacio HSV y la lógica de detección de colisiones del puntero contra botones invisibles.
- `canvas.py`: Contiene la clase `CanvasManager`. Opera de forma transparente dos matrices `numpy` diferentes (`solid_canvas` y `add_canvas`) en paralelo para permitir el renderizado condicionado de fusiones aditivas directas (ideal para los brillos estilo neón) versus máscaras de recorte opacas (para trazos normales).
- `brushes.py`: Clase con métodos estáticos enfocada exclusivamente en la matemática de dibujado de primitivas de OpenCV adaptadas para simular lápices reales (Normal, Acuarela, Spray y Neón).
