# RIO54 — Preparar una APK Android firmada

Esta guía permite generar una APK de distribución con una clave de firma que queda bajo control del propietario del proyecto. **No subas la clave privada ni sus contraseñas al repositorio ni las compartas por chat.**

## 1. Crear la clave de firma (Linux Mint)

Instalá un JDK 17 o superior y ejecutá en una terminal, dentro de una carpeta privada de tu equipo:

```bash
keytool -genkeypair -v \
  -keystore rio54-release.jks \
  -storetype JKS \
  -keyalg RSA -keysize 4096 \
  -validity 10000 \
  -alias rio54
```

Keytool solicitará una contraseña para el almacén, otra para la clave (podés usar la misma si así lo decidís) y datos del certificado. Guardá el archivo `rio54-release.jks` y las contraseñas en dos lugares seguros y fuera del repositorio. Hacé una copia de respaldo cifrada. Si perdés esta clave, no podrás actualizar una aplicación publicada con esa misma identidad de firma.

## 2. Crear los secretos en GitHub

En el repositorio, abrí **Settings → Secrets and variables → Actions → New repository secret** y creá estos cuatro secretos:

| Nombre del secreto | Contenido |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | El archivo JKS convertido a Base64, en una sola línea |
| `ANDROID_KEYSTORE_PASSWORD` | Contraseña del almacén |
| `ANDROID_KEY_ALIAS` | `rio54` |
| `ANDROID_KEY_PASSWORD` | Contraseña de la clave |

En Linux Mint podés obtener el texto Base64 con:

```bash
base64 -w 0 rio54-release.jks > rio54-keystore-base64.txt
```

Abrí ese archivo localmente y copiá su contenido al secreto `ANDROID_KEYSTORE_BASE64`. No lo agregues a Git, no lo adjuntes a un issue y eliminá la copia temporal cuando termines.

## 3. Generar la APK firmada

Una vez configurados los cuatro secretos:

1. Abrí **Actions → RIO54 Android signed release**.
2. Elegí **Run workflow** sobre la rama `main`.
3. Esperá a que terminen la compilación `assembleRelease`, la firma y la verificación con `apksigner`.
4. Descargá el artefacto **RIO54-Android-signed-release**.

El flujo falla explícitamente si falta algún secreto. La APK sólo se publica como artefacto cuando la firma se pudo verificar. El archivo SHA-256 acompaña a la APK.

## 4. Prueba física antes de distribuir

La automatización en emulador Android 16 pasó 3/3 pruebas, pero no reemplaza la prueba en un teléfono real. Antes de distribuir, instalá la APK firmada en un dispositivo de prueba y verificá:

- Inicio, cambio entre los ocho idiomas y navegación de los cuatro expedientes.
- Apertura y cierre de pistas, tablero de relaciones y conclusión.
- Cierre y reapertura de la app, persistencia del progreso y funcionamiento sin conexión.
- Orientación vertical/horizontal, teclado, áreas táctiles y rendimiento.
- Actualización de la APK firmada sobre una instalación anterior firmada con la misma clave.

No distribuyas la APK debug como versión final. La APK Android actual es un contenedor WebView de la edición HTML5, no una compilación Unity nativa.

## Estado

- Android 16 emulador: 3/3 pruebas instrumentadas aprobadas.
- APK debug: compilada.
- APK release firmada: pendiente de crear y configurar la clave privada del propietario.
- Teléfono físico: prueba manual pendiente.
- Publicación en Google Play: no realizada.
