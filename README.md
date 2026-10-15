# PIN Identification Program

Simulación gráfica local de la pantalla que aparece en `easymoney.mp4`.
No se conecta a dispositivos ni obtiene PIN reales.

## Ejecutar (Windows, Linux o macOS)

```sh
python -m pip install -r requirements.txt
python pin_simulator.py
```

Pulsa una tecla (excepto Enter/Esc) para iniciar y `R` para volver al principio.
`Enter` (tambi?n el num?rico) o `Esc` cierran el programa en cualquier momento.
Cada inicio genera un PIN aleatorio de cuatro cifras, incluidos ceros iniciales.
La ventana se puede redimensionar y conserva la proporción 16:9.
Opciones: `--fullscreen`, `--mute` y `--autoplay`.

## Referencia visual

El clip dura 10,63 segundos y alterna la pantalla con planos del teclado y
el actor. La aplicación reproduce la secuencia de la pantalla de forma continua:

- Cabecera ASCII `PIN IDENTIFICATION PROGRAM` y `Strike a key when ready ...`.
- Matriz monocroma de diez filas: llenado y actualización durante dos segundos.
- Reducción horizontal durante tres segundos hasta el PIN aleatorio de esta ejecuci?n.
- Cuatro filas con el PIN generado, `PIN IDENTIFICATION NUMBER: XXXX` y cursor parpadeante.

El marco, la iluminación y el grano se dibujan mediante código. No se reproduce
el vídeo dentro de la aplicación. La textura, la tipografía y los pitidos son
aproximaciones; no son los recursos originales de la película. Los tiempos de
la animación continua interpretan los cortes del montaje.

## Capturas reproducibles

```sh
python pin_simulator.py --snapshot inicio.png --ready
python pin_simulator.py --snapshot matriz.png --at 1
python pin_simulator.py --snapshot reduccion.png --at 3.5
python pin_simulator.py --snapshot resultado.png --at 5
python -m unittest discover -s tests -v
```

Las capturas funcionan sin pantalla ni dispositivo de audio.

## Docker (Linux con X11)

```sh
docker build -t pin-simulator .
docker run --rm -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro pin-simulator
```

Requiere que el servidor X11 permita la conexión del contenedor. Para usar
sonido en Linux puede ser necesario exponer el dispositivo de audio; se puede
usar `--mute` pasando `python pin_simulator.py --mute` al final del comando.
En Windows y macOS se recomienda ejecutar Python directamente.
