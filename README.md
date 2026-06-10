# 🎨 AR Canvas — Pintura en el Aire con Gestos

> **Nota:** Se agregará un GIF demostrativo aquí una vez que el proyecto esté más avanzado.
> *![Demo del Proyecto](assets/demo.gif)*

AR Canvas es un proyecto interactivo de Visión por Computadora y Realidad Aumentada (AR) que permite dibujar en tiempo real utilizando la cámara web. Mediante la inteligencia artificial y el seguimiento de las manos, puedes utilizar tu dedo índice como un pincel virtual para trazar sobre el entorno en vivo, cambiar herramientas mediante gestos y exportar tus creaciones.

---

## ✨ Características

*   **Seguimiento en tiempo real:** Detección robusta de la mano y rastreo preciso de la punta del dedo índice a pesar de las variaciones de iluminación.
*   **Reconocimiento de Gestos (Próximamente):** Controles *touchless* (sin contacto físico) para cambiar de pincel, elegir colores o aplicar el borrador, activados únicamente con formas de la mano.
*   **Filtros y Pinceles (Próximamente):** Variedad de herramientas creativas, incluyendo pincel normal, spray, efecto neón y acuarelas.
*   **Exportación de Obras (Próximamente):** Posibilidad de guardar el canvas como imagen (`.png`) o el proceso completo como una animación (`.gif`).
*   **Interfaz AR (Próximamente):** Barra de herramientas integrada gráficamente sobre el video.

---

## 🛠️ Stack Tecnológico

El proyecto está construido sin necesidad de GPU ni entrenar datasets complejos:

*   **[Python 3.10+](https://www.python.org/)** - Lenguaje principal.
*   **[MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)** - Proporciona los 21 *landmarks* de la mano en tiempo real con alta exactitud.
*   **[OpenCV](https://opencv.org/)** - Maneja el motor gráfico: captura el video de la cámara web, renderiza los trazos y superpone imágenes.
*   **[NumPy](https://numpy.org/)** - Usado para la manipulación de matrices, control del *canvas* transparente y futuras interpolaciones para suavizar el temblor de la mano.

---

## 🚀 Instalación y Uso

1.  **Clona este repositorio** y accede a la carpeta:
    ```bash
    git clone https://github.com/TU_USUARIO/AR-Canvas.git
    cd AR-Canvas
    ```

2.  **Crea y activa un entorno virtual** (recomendado para aislar dependencias):
    ```powershell
    # En Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instala los requerimientos:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta la aplicación:**
    ```bash
    python main.py
    ```

---

## 🎮 Controles de la Aplicación

Actualmente el proyecto se encuentra en la **Fase 1**. Estas son las interacciones planeadas y disponibles:

| Acción | Activación (Gesto o Teclado) | Estado Actual |
| :--- | :--- | :--- |
| **Dibujar / Trazar** | ☝️ Solo índice levantado | En desarrollo |
| **Mover Cursor (Sin pintar)** | ✌️ Índice y medio levantados | En desarrollo |
| **Borrador** | ✋ Mano abierta | En desarrollo |
| **Limpiar todo el Canvas** | 👊 Cerrar puño | En desarrollo |
| **Salir de la App** | Presionar tecla `q` | ✅ Implementado |

---

## 🏗️ Arquitectura y Estructura

El proyecto se dividirá en módulos para mantener el código limpio y legible (actualmente todo funciona de forma monolítica en la Fase 1 como prueba de concepto).

```text
ar-canvas/
├── main.py               # Entry point actual
├── requirements.txt      # Listado de dependencias
└── README.md             # Documentación principal
```

*Nota: Durante las próximas fases se implementarán `canvas.py`, `gestures.py`, `brushes.py` y `ui.py`.*
