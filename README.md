# RIO54 — Archivo de lo inexplicado

Videojuego narrativo de investigación inspirado en el archivo y las preguntas del blog [RIO54 OVNI](https://rio54ovni.blogspot.com/).

## Estado del proyecto

- Edición jugable HTML5: paquete local **RIO54 1.4.0**.
- Campaña: 4 expedientes y 16 indicios.
- Idiomas integrados: español, inglés, portugués brasileño, francés, alemán, italiano, japonés y chino simplificado.
- Mecánicas: lectura de fuentes, archivo de indicios, tablero de relaciones y elaboración de conclusiones.
- PWA: manifiesto y service worker para instalación y caché offline tras la primera visita.
- Proyecto Unity WebGL: se mantiene como línea de compilación separada; requiere Unity Editor y licencia válida.

## Cómo probar la edición HTML5

1. Descargá y descomprimí el paquete `rio54_version_1_4_0.zip`.
2. Abrí `rio54_game/index.html` en un navegador moderno.
3. Para probar instalación PWA y caché offline, serví la carpeta por HTTPS o localhost (no abras el archivo con `file://`).

En Linux, si el paquete incluye el lanzador `JUGAR_EN_LINUX.sh`, ejecutalo desde la carpeta extraída.

## Criterio de investigación

El juego distingue entre observaciones, testimonios, documentos, hipótesis y conclusiones. Los expedientes no presentan como demostrados hechos o causalidades que las fuentes no acreditan. Los personajes y diálogos de juego son recreaciones narrativas, no testimonios históricos.

## Fuentes y créditos

- Archivo de referencia: https://rio54ovni.blogspot.com/
- Proyecto independiente, sin afiliación oficial con el autor del blog ni con organismos mencionados.
- Las traducciones se ofrecen para accesibilidad; para el análisis documental prevalecen las fuentes originales.

## Próximos hitos de publicación

- [ ] Incorporar el paquete HTML5 completo al repositorio.
- [ ] Activar GitHub Pages y comprobar el sitio público por HTTPS.
- [ ] Probar WebGL real en un dispositivo con aceleración gráfica.
- [ ] Verificar instalación y funcionamiento offline de la PWA.
- [ ] Compilar y validar la versión Unity WebGL (.wasm) con Unity Editor y licencia.
