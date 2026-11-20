# RIO54 — Prueba de aceptación en Android

Esta guía prueba la edición HTML5 publicada en GitHub Pages. No requiere instalar Unity ni descargar una APK.

## Antes de empezar

- Usá un teléfono Android con Chrome actualizado.
- Conectá el teléfono a Internet.
- Abrí https://federicomazzagalli.github.io/Rio54/
- Anotá modelo del dispositivo, versión de Android, navegador y fecha de prueba.

## Prueba rápida en navegador

- [ ] La página carga sin pantalla en blanco ni error visible.
- [ ] El título RIO54 aparece completo y no queda cortado horizontalmente.
- [ ] El selector de idioma se puede abrir y usar con el dedo.
- [ ] Cambiar a English, Português (Brasil), Français, Deutsch, Italiano, 日本語 y 简体中文 cambia los textos principales.
- [ ] La pantalla de inicio se adapta al ancho del teléfono, sin desplazamiento horizontal.
- [ ] Se puede iniciar una investigación y abrir las cuatro pistas del primer expediente.
- [ ] El cuadro de cada pista cabe en la pantalla; el texto se puede desplazar y el botón de cierre queda accesible.
- [ ] El tablero permite seleccionar una respuesta y confirmar.
- [ ] La conclusión permite seleccionar una respuesta y finalizar el expediente.
- [ ] Al volver a cargar la página, el progreso guardado sigue presente.

## Prueba de instalación PWA

1. Abrí el sitio en Chrome mientras el teléfono está conectado.
2. Abrí el menú de Chrome y elegí **Instalar aplicación** o **Agregar a pantalla principal** (el texto puede variar según versión).
3. Confirmá la instalación.
4. Cerrá Chrome y abrí RIO54 desde el icono de la pantalla de inicio.
5. Comprobá que inicia en una ventana propia y no en una pestaña común.

- [ ] Chrome ofrece la instalación.
- [ ] El icono de RIO54 aparece en la pantalla de inicio o en el listado de aplicaciones.
- [ ] La aplicación instalada abre correctamente.

## Prueba sin conexión

Esta prueba debe hacerse después de abrir el juego al menos una vez con Internet y esperar a que termine la carga inicial.

1. Cerrá RIO54.
2. Activá el modo avión.
3. Abrí RIO54 desde el icono instalado.
4. Probá la pantalla inicial, el selector de idioma y la apertura de una pista.
5. Desactivá el modo avión y comprobá que vuelve a funcionar normalmente.

- [ ] La interfaz inicial abre sin conexión.
- [ ] Los textos y recursos principales siguen disponibles.
- [ ] No aparece una pantalla de error por falta de red.
- [ ] Al recuperar Internet, el juego vuelve a funcionar.

Nota: el caché offline depende de que el service worker haya terminado la primera instalación y de las políticas de caché del navegador. Una prueba offline negativa debe repetirse después de una primera visita completa con conexión.

## Prueba de pantalla y accesibilidad

- [ ] En vertical, ningún texto ni botón queda fuera de pantalla.
- [ ] Al girar el teléfono a horizontal, el diseño sigue siendo utilizable.
- [ ] El texto de las pistas se lee sin zoom obligatorio.
- [ ] Los botones y opciones pueden tocarse sin pulsaciones repetidas.
- [ ] El teclado virtual no tapa de forma permanente el botón de confirmar.
- [ ] No hay elementos superpuestos en 360 px, 390 px y 430 px de ancho, si se dispone de dispositivos o emulación.

## Resultado

**Aprobado** si se completan todas las pruebas de navegador y las pruebas PWA requeridas sin errores bloqueantes.

**Aprobado con observaciones** si el juego se completa pero existe un problema visual menor.

**Rechazado** si no se puede iniciar, abrir pistas, terminar un expediente, cambiar idioma o recuperar la PWA instalada.

Registrar los fallos con una captura de pantalla, el paso exacto, el modelo del dispositivo y la versión de Chrome. No enviar contraseñas, tokens ni datos privados.

## Alcance

La edición HTML5 usa JavaScript y un renderizador WebGL de navegador. Esta guía no certifica la futura compilación Unity WebGL (.wasm), ni sustituye pruebas en otros navegadores o modelos Android. La compilación Unity sigue pendiente de configurar los secretos privados requeridos por GameCI.
