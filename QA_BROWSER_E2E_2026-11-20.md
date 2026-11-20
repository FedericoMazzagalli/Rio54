# RIO54 1.4.1 — Informe de prueba funcional de navegador

**Fecha:** 20 de noviembre de 2026  
**Resultado:** APROBADO — campaña completa  
**Ejecución verificable:** [GitHub Actions #44733342606](https://github.com/FedericoMazzagalli/Rio54/actions/runs/44733342606)  
**Commit probado:** `37ab16c7ccbef72dd40bda9d479b789b50860d43`

## Entorno

- Chromium `159.0.8154.6` en un runner Ubuntu de GitHub Actions.
- Emulación de pantalla móvil: **390 × 844 px**, escala 1, con eventos táctiles.
- Servidor local `localhost` para permitir el registro y control del service worker.
- WebGL habilitado en Chromium mediante renderizado software (SwiftShader). Esto verifica el contexto WebGL del navegador, no una GPU física de Android.

## Resultado general

| Área | Resultado |
|---|---|
| Carga inicial del sitio | Aprobada |
| Diseño móvil sin desbordamiento horizontal | Aprobado |
| Ocho idiomas de interfaz | Aprobados |
| Cuatro expedientes jugados de principio a fin | Aprobado |
| Dieciséis pistas abiertas y registradas | Aprobado |
| Cuatro tableros y cuatro informes finales | Aprobados |
| Archivo con cuatro expedientes resueltos | Aprobado |
| Guardado y restauración tras recargar | Aprobado |
| Service worker activo y página controlada | Aprobado |
| Recarga con conexión desactivada | Aprobada |
| Canvas y contexto WebGL 1 | Aprobados |
| Errores de JavaScript no capturados | **0** |
| Errores de consola | **0** |

## Idiomas comprobados

Español, inglés, portugués brasileño, francés, alemán, italiano, japonés y chino simplificado. El test comprobó el valor seleccionado, el atributo `lang` del documento y un encabezado principal no vacío y traducido en cada idioma.

## Campaña completa

Se completaron los cuatro expedientes, abriendo sus cuatro pistas, eligiendo la respuesta correcta en el tablero y presentando el informe final. Cada partida automatizada obtuvo calificación **A**.

| Expediente | Pistas registradas | Resultado |
|---|---:|---|
| La luz de septiembre | 4 | A |
| La comisión bajo la lupa | 4 | A |
| La noche de Monte Grande | 4 | A |
| Ecos desde el continente blanco | 4 | A |
| **Total** | **16** | **4/4 resueltos** |

El archivo mostró los cuatro expedientes y el progreso completo siguió presente después de recargar la página.

## PWA offline

El service worker se registró, alcanzó estado `activated` y controló la página después de una recarga. Con la conexión desactivada desde el contexto de prueba, RIO54 volvió a cargar desde la caché y mostró su título y la interfaz principal.

Esta prueba valida la caché offline en Chromium sobre `localhost`; no sustituye la prueba de instalación y modo avión en un teléfono Android físico.

## WebGL

El canvas de la escena inicial obtuvo un contexto WebGL y el documento informó el renderer `webgl`. Dimensiones detectadas: 368 × 210 px. El test se ejecutó con renderizado software del navegador, por lo que queda pendiente validar rendimiento y compatibilidad con la GPU de distintos teléfonos.

## Límites pendientes

- Prueba de instalación desde Chrome en un teléfono Android real.
- Prueba real en modo avión y con rotación de pantalla en dispositivos físicos.
- Pruebas en otros navegadores y GPUs.
- Compilación Unity WebGL (`.wasm`), pendiente de activar la licencia de Unity en GitHub Actions con los secretos privados requeridos por GameCI.

**Conclusión:** la edición web 1.4.1 pasó la prueba automatizada de la campaña completa, guardado, ocho idiomas, PWA offline y contexto WebGL en Chromium. No se declara todavía terminada la compilación Unity ni la validación física Android.
