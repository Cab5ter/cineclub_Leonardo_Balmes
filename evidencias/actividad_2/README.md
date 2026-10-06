# Evidencias · Unidad II · Actividad 2

Capturas reales de GraphiQL ejecutando el cineclub contra MySQL. Las evidencias de la actividad 1 están en la carpeta superior.

## 1. Suscripción

La conexión WebSocket recibe The Little Prince después del commit, sin volver a consultar y sin reenviar las películas anteriores.

![Suscripción recibiendo la película](01_suscripcion.png)

## 2. Validación

La petición se detiene en validación: `isbn` no existe en Pelicula; la respuesta contiene `errors` y no contiene `data`.

![Campo inexistente](02_validacion_1.png)

Un objeto como `director` requiere seleccionar sus subcampos; la validación rechaza la consulta antes de ejecutar resolvers.

![Objeto sin subcampos](02_validacion_2.png)

Un escalar como `titulo` no admite una selección interna; el servidor devuelve un error de petición.

![Escalar con subcampos](02_validacion_3.png)

## 3. Ejecución

El resolver `siglo` calcula el siglo con el año de cada película durante la ejecución, sin una columna adicional en MySQL.

![Campo calculado siglo](03_siglo.png)

## 4. Respuesta parcial

Durante la ejecución, `etiqueta` falla para la película de 1895: queda null, pero título, año y los datos de la película de 2015 permanecen en `data`; `errors` identifica el campo que falló.

![Datos parciales](04_respuesta_parcial.png)

La primera captura usa dos búsquedas por título para facilitar la comparación. La siguiente muestra la lista completa, que también se conserva en `lista_parcial` de [resultados.json](resultados.json).

![Respuesta parcial del catálogo completo](04_respuesta_parcial_lista.png)

## 5. Introspección

La consulta del esquema confirma las raíces Query, Mutation y Subscription, los campos calculados y la suscripción `peliculaAgregada`.

![Introspección del esquema](05_introspeccion.png)

[Respuestas JSON reales de todas las comprobaciones](resultados.json).
