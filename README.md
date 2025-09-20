<div align="center">

# ☀️ Seguidor Solar con **OpenCV** + **ESP32** (Servo + Motor a Pasos)

**Rastrea la zona más luminosa con una webcam y mueve un servo (elevación) + un motor a pasos (azimut) controlados por ESP32.**  
Hecho para clases, demos y proyectos maker, con un *pipeline* simple, reproducible y bien documentado.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)](#)
[![Arduino-ESP32](https://img.shields.io/badge/Arduino-ESP32-00979D?logo=arduino&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Made with 💛 for FIME](https://img.shields.io/badge/Made%20with-%F0%9F%92%9B%20for%20FIME-blue)](#)

</div>

---

## 🧭 Tabla de contenido
- [Demo](#-demo)
- [Por qué funciona tan bien](#-por-qué-funciona-tan-bien)
- [Ventajas frente a un seguidor con LDR](#-ventajas-frente-a-un-seguidor-con-ldr)
- [Cómo funciona (pipeline)](#-cómo-funciona-pipeline)
- [Hardware y conexiones](#-hardware-y-conexiones)
- [Instalación (PC) y ejecución](#-instalación-pc-y-ejecución)
- [Carga de firmware (ESP32)](#-carga-de-firmware-esp32)
- [Parámetros clave](#-parámetros-clave)
- [Solución de problemas](#-solución-de-problemas)
- [Roadmap](#-roadmap)
- [Créditos y licencia](#-créditos-y-licencia)

---

## 🎥 Demo
> Inserta aquí tu video o GIF en `host/assets/demo.gif` y referéncialo:  
> `![demo](host/assets/demo.gif)`

---

## 🚀 ¿Por qué **funciona tan bien**?
Este proyecto usa **visión por computadora** para detectar el **punto más brillante** en la imagen. Eso lo vuelve **robusto** frente a **sombras, nubes, reflejos parciales, o luces laterales**. A diferencia de un arreglo de LDRs, la *cámara observa toda la escena* y decide con más contexto. Además:
- **Cierre de lazo real**: la cámara verifica en cada cuadro si el sol/la fuente luminosa está centrada y corrige en consecuencia.
- **Umbral adaptable**: ajustar `THRESH_VAL` permite discriminar condiciones de luz ambiental sin rehacer hardware.
- **Geometría explícita**: trabajamos con **centroides** y **distancias pixel** → control claro y ajustable con `TOLERANCIA`.
- **Reproducible y didáctico**: ideal para clase; el pipeline es visible (grises → binario → contorno → centro).
- **Extensible**: fácil añadir ROI, exposición fija, filtros o incluso un controlador PID o RL más adelante.

---

## 🆚 Ventajas frente a un seguidor con **LDR**
| Criterio | Vision-based (este proyecto) | Solo LDRs |
|---|---|---|
| Contexto de la escena | Alto (toda la imagen) | Bajo (solo intensidad local) |
| Sombra/reflejos | Mejor tolerancia (usa contornos y centroides) | Puede confundir fuentes/umbrales |
| Calibración HW | Nula/baja (ajuste por software) | Media/alta (resistencias, simetría, matching) |
| Multi‑fuente | Selecciona la más grande/brillante | Puede oscilar entre sensores |
| Afinamiento | Inmediato (parámetros en código) | Requiere cambiar HW o potenciómetros |
| Extensibilidad | Alta (ROI, filtros, PID, RL) | Limitada |
| Costo | + webcam | – webcam |

> **Conclusión**: Con cámara obtienes **más información** y **mejor control** con pequeños ajustes de software. Un arreglo de LDRs es barato y simple, pero **menos robusto** y **menos flexible**.

---

## ⚙️ Cómo funciona
```mermaid
flowchart LR
    A["Webcam"] --> B["Escala de grises"]
    B --> C["Umbral binario (THRESH_VAL)"]
    C --> D["Contornos"]
    D --> E["Mayor área"]
    E --> F["Centroide (cx, cy)"]
    F --> G{{"Comparación con centro de imagen (TOLERANCIA)"}}
    G -->|dx<0| H["MOTOR IZQUIERDA"]
    G -->|dx>0| I["MOTOR DERECHA"]
    G -->|dy<0| J["SERVO ARRIBA"]
    G -->|dy>0| K["SERVO ABAJO"]
    G -->|abs(dx), abs(dy) dentro| L["SOL CENTRO"]
    H & I & J & K & L --> M["Serial 115200 a ESP32"]
    M --> N["A4988 + Stepper / Servo"]
```
---
```bash
pip install -r requirements.txt
python host/app.py
```
---
1) Selecciona **puerto serie** (COMx / /dev/ttyUSBx).  
2) Elige **índice de cámara** (0/1/2).  
3) Pulsa **“Encender Cámara + Detección”**. La app enviará comandos según la posición del brillo respecto al centro.

---

## 🔌 Carga de firmware (ESP32)
1. Abre `firmware/esp32/firmware.ino` en **Arduino IDE**.  
2. Placa: **ESP32 Dev Module**, **115200 baud**.  
3. Sube el sketch y prueba.

---

## 🎚️ Parámetros clave
- **PC (`host/app.py`)**
  - `TOLERANCIA` → radio de “zona muerta” (px).  
  - `THRESH_VAL` → umbral de brillo (0–255).  
  - Resolución de captura `RES_W`, `RES_H`.

- **ESP32 (`firmware.ino`)**
  - `STEPS_PER_TICK` → pasos por orden izquierda/derecha.  
  - `STEP_DELAY_US` → velocidad del stepper.  
  - `SERVO_DELTA` → grados por orden arriba/abajo.

---

## 🛠️ Solución de problemas
- **Webcam no abre** → prueba otro índice (0/1) o permisos.  
- **Puertos serie** → verifica COMx/`/dev/ttyUSBx` y que no esté ocupado por otro programa.  
- **Stepper vibra/calienta** → baja corriente (Vref) y revisa cableado A/B y microstepping.  
- **Servo tiembla** → usa fuente 5V dedicada y GND común.  
- **Señal intermitente** → prueba un **umbral** (`THRESH_VAL`) más alto y/o fija exposición de la cámara.

---

## 🧭 Roadmap
- Control **PID** suave y centrado.  
- Pre‑apuntamiento con **posición solar** (biblioteca Astral).  
- **Aprendizaje por refuerzo** para minimizar movimiento total y consumo.  
- Registro de telemetría y métricas de seguimiento.

---

## 👥 Créditos y licencia
- Autor: René Guzmán Pérez (FIME UANL)
- Documento de proyecto en `docs/`.  
- Licencia: **MIT** (ver `LICENSE`).

---

> Si este repo te sirvió, ¡dale ⭐ en GitHub! Y comparte un GIF de tu montaje en *Issues/Discussions* 😄

