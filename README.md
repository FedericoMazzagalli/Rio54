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

También ejecuta `Tools/test_browser.py` con Chromium y Playwright, y smoke tests de `Tools/test_cross_browser.py` con Firefox y WebKit: prueba el diseño táctil móvil en cinco perfiles de pantalla (320, 360, 390, 430 px y horizontal), mide los botones principales, los ocho selectores de idioma, los cuatro expedientes y sus dieciséis pistas, tablero y conclusiones, guardado de campaña y carga offline mediante el service worker. La prueba se ejecuta en cada publicación de Pages y conserva un trace/screenshot cuando falla.

La prueba automatizada completa se ejecuta en Chromium sobre `localhost`, que Chromium trata como contexto seguro para service workers: verifica los cuatro expedientes, la escena WebGL y la caché offline. Firefox y WebKit prueban la carga, cambio de idioma, inicio de expediente, apertura/cierre de pista y tres perfiles de pantalla. Las pruebas en teléfonos físicos y en otros navegadores siguen pendientes de confirmación manual.

Para probar la edición web, abrí el [sitio publicado](https://federicomazzagalli.github.io/Rio54/). Para inspeccionar el flujo de publicación, consultá [GitHub Actions](https://github.com/FedericoMazzagalli/Rio54/actions).


### Última prueba E2E aprobada — 20/11/2026

La ejecución [GitHub Actions #44737237957](https://github.com/FedericoMazzagalli/Rio54/actions/runs/44737237957) aprobó la campaña completa **4/4 expedientes y 16/16 pistas**, cuatro calificaciones A, guardado tras recargar, PWA offline y contexto WebGL sin errores. También pasó el smoke test en **Firefox 159.0 y WebKit 27.2**, con tres perfiles de pantalla por motor. Chromium comprobó cinco perfiles (320×700, 360×800, 390×844, 430×932 y 844×390), con el botón principal visible y controles de 44 px. El informe está en [QA_BROWSER_E2E_2026-11-20_1_4_2.md](QA_BROWSER_E2E_2026-11-20_1_4_2.md). Son pruebas automatizadas en runner, no una certificación de un teléfono físico ni de GPU móvil.

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


## APK Android de depuración — compilación aprobada

La primera APK Android ya fue compilada correctamente por GitHub Actions el **20/11/2026**. La ejecución [#44739024932](https://github.com/FedericoMazzagalli/Rio54/actions/runs/44739024932) terminó con éxito: JDK 17, Android SDK 36, Gradle 9.6.0, validación de los recursos y `assembleDebug` aprobados. El artefacto descargable es [RIO54-Android-debug-APK](https://github.com/FedericoMazzagalli/Rio54/actions/runs/44739024932/artifacts/14629443143).

La APK es una compilación **debug** para pruebas manuales; no está firmada con una clave release de distribución. Falta instalarla y comprobarla en un teléfono Android físico.

## Aplicación Android instalable

El paquete Android nativo v0.1.0 está disponible en [android/RIO54_Android_Offline_App_v0_1.zip](android/RIO54_Android_Offline_App_v0_1.zip). Es un contenedor Android WebView que lleva la edición HTML5 1.4.2 dentro del APK, con caché local y soporte de service worker mediante un origen HTTPS local. No es la compilación Unity ni una APK ya verificada en un teléfono físico.

El workflow [RIO54 Android APK](https://github.com/FedericoMazzagalli/Rio54/actions/workflows/android-apk.yml) compila una APK debug con Android 16/API 36. Cuando el workflow termine, su artefacto se llamará `RIO54-Android-debug-APK`. La distribución en Play Store requerirá firma release y pruebas físicas adicionales.

## QA automatizada en emulador Android

El workflow Android ahora añade pruebas instrumentadas en un emulador Android 16/API 36 con conectividad desactivada. Comprueba el origen HTTPS local del WebView, los ocho idiomas, el canvas WebGL, que la APK no solicite permiso de Internet, el inicio de un expediente, el registro de una pista, la persistencia después de recrear la actividad y la activación del service worker con el HTML, las traducciones y el renderizador en caché. Los informes se publican como artefacto de GitHub Actions.

Estas pruebas automatizadas no equivalen a una certificación en un teléfono físico. Siguen pendientes la instalación real, los fabricantes y tamaños de pantalla distintos, Android 8–15, rotación, consumo y rendimiento gráfico móvil.


## Preparar una APK Android firmada

Se agregó el workflow manual [RIO54 Android signed release](.github/workflows/android-release.yml), que compila la variante release, firma con la clave privada del propietario y verifica el certificado antes de publicar el artefacto. Antes de ejecutarlo, seguí [ANDROID_RELEASE_ES.md](ANDROID_RELEASE_ES.md) para crear la clave y configurar los cuatro secretos de GitHub Actions. La clave privada nunca debe subirse al repositorio ni compartirse por chat. La prueba en un teléfono físico sigue siendo necesaria.
