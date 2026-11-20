# Pruebas Android instrumentadas de RIO54

Este conjunto se ejecuta dentro de un emulador Android 16 (API 36) con la aplicación instalada. El flujo de CI desactiva Wi-Fi y datos móviles antes de ejecutar las pruebas.

## Cobertura

1. Carga de la aplicación desde el origen HTTPS local appassets.androidplatform.net.
2. Presencia de los ocho idiomas del juego y del canvas WebGL.
3. Ausencia del permiso android.permission.INTERNET en la aplicación principal.
4. Inicio de una partida, apertura del primer expediente, despliegue de una pista y registro en el guardado local.
5. Persistencia del progreso al recrear la actividad Android.
6. Registro y activación del service worker del paquete local, con HTML, traducciones y renderizador presentes en la caché.

## Ejecución

El workflow .github/workflows/android-apk.yml descomprime el proyecto Android Studio fijado, incorpora estas pruebas y ejecuta :app:connectedDebugAndroidTest en un emulador API 36. Los informes quedan publicados como artefacto de GitHub Actions.

Estas pruebas no sustituyen la instalación en teléfonos físicos: quedan pendientes las comprobaciones en dispositivos reales, especialmente versiones Android 8–15, fabricantes distintos, rotación, ahorro de batería y rendimiento gráfico.
