# RIO54 — Archivo de lo inexplicado

Videojuego narrativo de investigación independiente, inspirado en el archivo y las preguntas del blog [RIO54 OVNI](https://rio54ovni.blogspot.com/).

## Estado del proyecto

- **Edición HTML5 1.4.1:** publicada en GitHub Pages.
- **Sitio:** https://federicomazzagalli.github.io/Rio54/
- Campaña: 4 expedientes y 16 indicios.
- Idiomas: español, inglés, portugués brasileño, francés, alemán, italiano, japonés y chino simplificado.
- Mecánicas: lectura de fuentes, archivo de indicios, tablero de relaciones y elaboración de conclusiones.
- PWA: manifiesto, iconos y service worker para instalación y caché offline después de la primera visita.
- **Unity WebGL:** proyecto fuente 1.4.1 integrado y validado por CI. La compilación del reproductor (.wasm) todavía no está generada.

## Publicación web y control de calidad

La publicación más reciente de GitHub Pages terminó correctamente en Configure Pages, Build, Upload artifact y Deploy. El paquete publicado incluye HTML, traducciones, renderizador, manifiesto, iconos y service worker.

El flujo ahora ejecuta un control adicional con `Tools/verify_pages.py`: comprueba identificadores HTML críticos y duplicados, referencias a recursos locales, manifiesto e iconos PNG, archivos precargados por el service worker, sintaxis JavaScript y estructura de las traducciones (7 idiomas adicionales × 4 expedientes × 4 pistas, con tablero y conclusión).

La prueba funcional previa del núcleo de juego comprobó la secuencia completa de pistas, tablero, conclusión y cierre de expediente en Chromium. En esta sesión, el entorno de ejecución bloqueó la navegación automatizada local y el acceso web al dominio público; por eso la apertura real en distintos navegadores, WebGL GPU y el ciclo PWA offline en HTTPS siguen pendientes de confirmación manual.

Para probar la edición web, abrí el [sitio publicado](https://federicomazzagalli.github.io/Rio54/). Para inspeccionar el flujo de publicación, consultá [GitHub Actions](https://github.com/FedericoMazzagalli/Rio54/actions).

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
