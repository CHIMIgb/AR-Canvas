# 🎨 AR Canvas — Pintura en el Aire con Gestos

> Proyecto de portfolio usando OpenCV + MediaPipe que permite dibujar en tiempo real con los dedos frente a la cámara, cambiar colores y herramientas mediante gestos, y exportar la obra final.

---

## Opinión técnica

**Veredicto: Hazlo. Pero hazlo bien.**

La versión básica (solo trazar con el dedo) la hacen muchos. La diferencia entre un proyecto mediocre y uno que te consigue entrevistas está en los detalles: suavizado de trazo, UI coherente integrada en AR, README con GIF demo, y código limpio con comentarios.

### Por qué es el proyecto ideal para portfolio

- **Demo instantánea** — cualquier reclutador lo entiende en 3 segundos sin explicación técnica
- **Scope controlable** — realizable en 1-2 semanas solo, sin necesidad de dataset ni GPU
- **Stack limpio** — OpenCV + MediaPipe + NumPy, sin over-engineering
- **Extensible** — puedes ir agregando features progresivamente
- **Visualmente impactante** — un GIF de 5 segundos en el README ya genera engagement

### Retos reales a considerar

- **Temblor de mano** — el mayor enemigo. Los trazos se ven "nerviosos" sin suavizado. Requiere filtro Kalman o interpolación. No es difícil, pero hay que implementarlo.
- **Detección de gestos ambigua** — distinguir entre "estoy pintando" y "estoy cambiando herramienta" sin activaciones falsas requiere manejo cuidadoso de estados.

### Métricas del proyecto

| Criterio            | Puntuación  |
|---------------------|-------------|
| Dificultad real     | 4 / 10      |
| Impacto visual      | 8 / 10      |
| Empleabilidad       | 7 / 10      |
| Originalidad base   | 5 / 10      |
| Con los extras      | 8 / 10      |

---

## Stack tecnológico

| Librería         | Rol                                                                 |
|------------------|---------------------------------------------------------------------|
| **MediaPipe Hands** | Detección de landmarks (21 puntos por mano). Robusto ante distintas iluminaciones y tonos de piel. |
| **OpenCV**          | Canvas, rendering en tiempo real, exportar imagen final.           |
| **NumPy**           | Suavizado e interpolación de puntos del trazo.                     |
| **Python 3.10+**    | Lenguaje base del proyecto.                                        |

> **¿Por qué MediaPipe y no solo OpenCV?**
> OpenCV puro para detectar dedos es frágil con distintas iluminaciones y colores de piel. MediaPipe tiene un modelo entrenado robusto y te da 21 puntos exactos de la mano. No reinventes la rueda.

---

## Features planeados

| Feature | Por qué importa en el portfolio |
|---|---|
| Suavizado de trazo con interpolación | Demuestra que piensas en UX |
| UI flotante en AR para paleta de colores | Demuestra integración visual |
| Diferentes pinceles (spray, acuarela, neón) | Demuestra creatividad técnica |
| Exportar como PNG / GIF del proceso | Feature completo y útil |
| Modo "levantar mano = pausar trazo" | Demuestra manejo fino de estados |

---

## Fases de implementación

### Fase 1 — Fundamentos (Días 1-2)
**Objetivo:** Ver la cámara funcionando con detección de mano básica.

- Configurar entorno virtual con `mediapipe`, `opencv-python`, `numpy`
- Capturar video desde la cámara con OpenCV
- Integrar MediaPipe Hands y visualizar los 21 landmarks en pantalla
- Aislar el landmark del dedo índice (punto 8)
- Dibujar un círculo sobre la punta del índice en tiempo real

**Entregable:** Video en vivo con un punto siguiendo la punta del dedo.

---

### Fase 2 — Canvas y trazado básico (Días 3-4)
**Objetivo:** Que el dedo deje un trazo persistente en pantalla.

- Crear un canvas transparente (NumPy array) separado del frame de la cámara
- Guardar la posición anterior del dedo para conectar puntos con `cv2.line`
- Fusionar el canvas sobre el frame en tiempo real (`cv2.addWeighted`)
- Implementar lógica de "pincel levantado": si el dedo desaparece o se aleja demasiado, no conectar el trazo

**Entregable:** Trazos persistentes que siguen el dedo índice sobre el video en vivo.

---

### Fase 3 — Suavizado del trazo (Día 5)
**Objetivo:** Eliminar el temblor y hacer los trazos fluidos.

- Implementar buffer circular de las últimas N posiciones del dedo
- Aplicar media móvil o interpolación de Catmull-Rom sobre los puntos
- Comparar visualmente trazo crudo vs suavizado y ajustar el tamaño del buffer
- (Opcional avanzado) Implementar filtro de Kalman para mayor precisión

**Entregable:** Trazos suaves y naturales, sin nerviosismo visual.

---

### Fase 4 — Gestos y cambio de herramienta (Días 6-7)
**Objetivo:** Controlar colores y herramientas con la mano sin tocar el teclado.

- Implementar detector de dedos levantados usando landmarks de MediaPipe
- Definir gestos:
  - ☝️ Solo índice → modo pintar
  - ✌️ Índice + medio → modo mover / cursor (no pinta)
  - ✋ Mano abierta → borrador
  - 👊 Puño → limpiar canvas completo (con confirmación visual)
- Añadir zona de UI en la parte superior del frame para selección de color
- Detectar cuando el dedo índice entra en la zona de UI para cambiar color

**Entregable:** Cambio de color y herramientas completamente sin teclado ni mouse.

---

### Fase 5 — Pinceles y efectos (Días 8-9)
**Objetivo:** Variedad de herramientas que demuestren creatividad técnica.

- **Pincel normal** — línea sólida con grosor configurable
- **Pincel spray** — puntos aleatorios en un radio alrededor del dedo (`np.random`)
- **Efecto neón** — trazo con glow usando `cv2.GaussianBlur` + blend
- **Acuarela** — trazo semitransparente con bordes difusos
- Añadir selector de grosor de pincel (gesto de pellizco: distancia entre índice y pulgar)

**Entregable:** Al menos 3 tipos de pincel funcionales y seleccionables.

---

### Fase 6 — UI en AR y exportación (Día 10)
**Objetivo:** Pulir la experiencia y hacerla presentable.

- Diseñar barra de herramientas flotante integrada en el video (paleta de colores, pinceles, borrador)
- Añadir indicador visual del color y herramienta activa
- Implementar exportación:
  - `S` → guardar PNG del canvas actual con timestamp
  - `G` → guardar GIF del proceso (buffer de frames)
- Añadir overlay de instrucciones en pantalla para nuevos usuarios

**Entregable:** Aplicación completa, usable y exportable.

---

### Fase 7 — Pulido y portfolio (Días 11-14)
**Objetivo:** Convertir el proyecto en algo que consiga entrevistas.

- Refactorizar el código en módulos: `canvas.py`, `gestures.py`, `brushes.py`, `ui.py`
- Añadir docstrings y comentarios claros
- Grabar GIF demo de 5-10 segundos para el README
- Escribir README completo con: descripción, GIF, requisitos, instalación, controles, arquitectura
- Subir a GitHub con commits semánticos y estructura de carpetas limpia
- (Bonus) Publicar demo en LinkedIn con el GIF

**Entregable:** Repositorio público listo para mostrar a reclutadores.

---

## Estructura de carpetas sugerida

```
ar-canvas/
├── main.py               # Entry point
├── canvas.py             # Lógica del canvas y fusión con el frame
├── gestures.py           # Detección de gestos con MediaPipe
├── brushes.py            # Tipos de pinceles y efectos
├── ui.py                 # Barra de herramientas AR
├── utils.py              # Suavizado, helpers
├── assets/
│   └── demo.gif          # Para el README
├── outputs/              # Imágenes y GIFs exportados
├── requirements.txt
└── README.md
```

---

## Checklist final antes de publicar

- [ ] El proyecto corre con `python main.py` sin errores desde cero
- [ ] README tiene GIF demo en la primera pantalla
- [ ] Al menos 3 tipos de pincel funcionando
- [ ] Exportación de PNG funcional
- [ ] Código dividido en módulos (no todo en un archivo)
- [ ] Sin credenciales ni rutas absolutas en el código
- [ ] Commits con mensajes descriptivos
