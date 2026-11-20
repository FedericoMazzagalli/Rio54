# RIO54 — Archivo de lo inexplicado

Videojuego narrativo de investigación independiente, inspirado en el archivo y las preguntas del blog [RIO54 OVNI](https://rio54ovni.blogspot.com/).

## Estado del proyecto

- **Edición HTML5 1.4.2:** publicada en GitHub Pages.
- **Sitio:** https://federicomazzagalli.github.io/Rio54/
- Campaña: 4 expedientes y 16 indicios.
- Idiomas: español, inglés, portugués brasileño, francés, alemán, italiano, japonés y chino simplificado.
- Mecánicas: lectura de fuentes, archivo de indicios, tablero de relaciones y elaboración de conclusiones.
- PWA: manifiesto, iconos y service worker para instalación y caché offline después de la primera visita.
- **Unity WebGL:** paquete fuente v1.4 (`rio54_unity_webgl_proyecto_v1_4.zip`); la versión interna declarada del proyecto es 1.3.1. La estructura y los datos están validados por CI, pero la compilación del reproductor (.wasm) todavía no está generada.

## Publicación web y control de calidad

La publicación más reciente de GitHub Pages terminó correctamente en Configure Pages, Build, Upload artifact y Deploy. El paquete publicado incluye HTML, traducciones, renderizador, manifiesto, iconos y service worker.

El flujo ahora ejecuta un control adicional con `Tools/verify_pages.py`: comprueba identificadores HTML críticos y duplicados, referencias a recursos locales, manifiesto e iconos PNG, archivos precargados por el service worker, sintaxis JavaScript y estructura de las traducciones (7 idiomas adicionales × 4 expedientes × 4 pistas, con tablero y conclusión).

También ejecuta `Tools/test_browser.py` con Chromium y Playwright: prueba el diseño táctil móvil en cinco perfiles de pantalla (320, 360, 390, 430 px y horizontal), mide los botones principales, los ocho selectores de idioma, los cuatro expedientes y sus dieciséis pistas, tablero y conclusiones, guardado de campaña y carga offline mediante el service worker. La prueba se ejecuta en cada publicación de Pages y conserva un trace/screenshot cuando falla.

La prueba automatizada de navegador se ejecuta ahora dentro de GitHub Actions sobre `localhost`, que Chromium trata como contexto seguro para service workers: verifica el recorrido completo en Chromium, el WebGL disponible en el runner y la caché offline del service worker. Las pruebas en teléfonos físicos y en otros navegadores siguen pendientes de confirmación manual.

Para probar la edición web, abrí el [sitio publicado](https://federicomazzagalli.github.io/Rio54/). Para inspeccionar el flujo de publicación, consultá [GitHub Actions](https://github.com/FedericoMazzagalli/Rio54/actions).


### Última prueba E2E aprobada — 20/11/2026

La ejecución [GitHub Actions #44733800308](https://github.com/FedericoMazzagalli/Rio54/actions/runs/44733800308) completó los **4 expedientes y 16 pistas**, registró cuatro resultados A en el archivo, recuperó el progreso tras recargar y volvió a cargar desde la caché PWA sin conexión. Chromium 159 obtuvo un contexto WebGL y el test terminó con cero errores de consola y cero excepciones JavaScript. Se usó emulación móvil 390 × 844 px y WebGL por software; no es una prueba física Android ni de GPU móvil. El informe detallado está en [QA_BROWSER_E2E_2026-11-20.md](QA_BROWSER_E2E_2026-11-20.md).

## Pruebas en Android

La guía de aceptación para Chrome Android y PWA está en [ANDROID_TESTS_ES.md](ANDROID_TESTS_ES.md). La edición HTML5 se prueba en navegador; no es una APK nativa.

## Compilación Unity WebGL

El proyecto Unity fuente se encuentra en `unity/rio54_unity_webgl_proyecto_v1_4.zip`. Usa Unity 6.3 LTS, versión 6000.3.0f1.

El workflow separado es [RIO54 Unity WebGL](https://github.com/FedericoMazzagalli/Rio54/actions/workflows/unity-webgl.yml). Su validación de estructura y datos multilingües pasó correctamente. Un intento de compilación llegó a la verificación de credenciales y se detuvo porque aún no están configurados estos secretos privados de GitHub Actions:

- `UNITY_LICENSE`: contenido del archivo `Unity_lic.ulf` de Unity Hub.
- `UNITY_EMAIL`: correo de la cuenta Unity.
- `UNITY_PASSWORD`: contraseña de esa cuenta.

Con una licencia Personal, GameCI requiere los tres secretos. La documentación oficial describe cómo obtener el archivo `.ulf` desde Unity Hub y guardarlo como secreto: [GameCI — Activación](https://game.ci/docs/github/activation/).

Después de configurarlos en Settings → Secrets and variables → Actions, ejecutá el workflow **RIO54 Unity WebGL** con la opción `build_unity` activada. El resultado esperado será el artefacto `RIO54-Unity-WebGL`; hasta que exista ese artefacto validado no debe considerarse generada la versión `.wasm`.

No compartas el archivo `.ulf`, la contraseña ni el contenido de los secretos en chats, issues o archivos versionados.

## Criterio de investigación

El juego distingue entre observaciones, testimonios, documentos, hipótesis y conclusiones. Los expedientes no presentan como demostrados hechos o causalidades que las fuentes no acreditan. Los personajes y diálogos de juego son recreaciones narrativas, no testimonios históricos.

## Fuentes y créditos

- Archivo de referencia: https://rio54ovni.blogspot.com/
- Proyecto independiente, sin afiliación oficial con el autor del blog ni con organismos mencionados.
- Las traducciones se ofrecen para accesibilidad; para el análisis documental prevalecen las fuentes originales.
