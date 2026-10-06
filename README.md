# Cineclub: GraphQL y MySQL

Unidad II, actividades 1 y 2 · Leonardo Balmes.

El catálogo de películas usa Strawberry y SQLAlchemy con MySQL. La actividad 2 añade suscripciones, validación, campos calculados, respuestas parciales e introspección.

## Organización de la entrega

- `schema.py`, `database.py`, `models.py` y `app.py`: versión completa en la carpeta original.
- `actividad_2/cineclub/`: copia de entrega de la segunda actividad, con el mismo código.
- `evidencias/actividad_2/`: **capturas exclusivas de la actividad 2**, explicaciones y respuestas JSON reales.
- Las evidencias anteriores permanecen directamente en `evidencias/`.
- `tests/test_actividad2.py`: cinco pruebas automáticas aisladas; no modifican MySQL.

El material de clase utiliza libros. Este proyecto conserva el dominio de cineclub de la actividad 1: `Book` → `Pelicula`, `Author` → `Director`, `books` → `peliculas`, `addBook` → `agregarPelicula` y `bookAdded` → `peliculaAgregada`. `siglo` y `etiqueta` conservan sus nombres. Es una adaptación al proyecto: no expone los nombres de libros del ejemplo.

## Ejecución

Requiere Python 3.10+ y MySQL. Crear la base si todavía no existe:

```sql
CREATE DATABASE IF NOT EXISTS cineclub;
```

Desde la raíz del proyecto:

```bash
python3 -m venv virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='mysql+pymysql://USUARIO:CONTRASENA@127.0.0.1:3306/cineclub'
python -m uvicorn app:app --host 127.0.0.1 --port 8004
```

Sustituir las credenciales por las de tu MySQL. Abrir dos pestañas en <http://localhost:8004/graphql>. Para ejecutar la copia, cambiar a `actividad_2/cineclub` después de activar el entorno y usar el mismo comando de Uvicorn. Ejecutar un solo proceso: las colas no se comparten entre servidores.

Se utiliza `app.py` porque Strawberry 0.328.0 incluye `data: null` en los errores de validación por defecto. Esta vista omite `data` únicamente en errores previos a la ejecución (sin `path`) y conserva `data` y `errors` cuando falla un resolver. `strawberry dev schema` no aplica este ajuste HTTP.

## 1. Suscripción y mutación

Ejecutar primero en una pestaña y dejarla abierta:

```graphql
subscription NuevaPelicula {
  peliculaAgregada {
    titulo
    anio
    director { nombre }
  }
}
```

Después, en otra pestaña, ejecutar una sola vez:

```graphql
mutation AltaPelicula {
  agregarPelicula(pelicula: {
    titulo: "The Little Prince"
    director: "Mark Osborne"
    anio: 2015
    disponible: true
  }) {
    titulo
    anio
    director { nombre }
  }
}
```

La primera pestaña recibe el evento sin volver a consultar. La mutación ejecuta `commit` y `refresh` antes de publicar el objeto `Pelicula`. Cada conexión tiene una cola propia; `await cola.get()` espera y `yield` produce la respuesta. `finally` retira la cola al desconectarse. No se reenvía el catálogo previo. Repetir una mutación inserta otra fila: el título no es único.

## 2. Validación

Ejecutar por separado:

```graphql
{ peliculas { isbn } }
```

```graphql
{ peliculas { director } }
```

```graphql
{ peliculas { titulo { nombre } } }
```

Las tres operaciones devuelven `errors` sin `data`. Respectivamente: el campo no existe, un objeto necesita subcampos y un escalar no acepta subcampos. La validación ocurre antes de abrir una sesión de base de datos.

## 3. Ejecución: campo calculado

```graphql
query Siglos {
  peliculas {
    titulo
    anio
    siglo
  }
}
```

`siglo` calcula `(anio + 99) // 100` en el resolver: Cinema Paradiso (1988) pertenece al siglo 20 y Spirited Away (2001) al 21. No se agregaron columnas a MySQL.

## 4. Respuesta parcial

Insertar una película anterior a 1900, una sola vez:

```graphql
mutation PeliculaAntigua {
  agregarPelicula(pelicula: {
    titulo: "La Sortie de l'usine Lumiere a Lyon"
    director: "Louis Lumiere"
    anio: 1895
    disponible: true
  }) { titulo anio }
}
```

```graphql
{ peliculas { titulo anio etiqueta } }
```

La película de 1895 conserva título y año, pero `etiqueta` es `null`; `errors` incluye el mensaje y la ruta del campo. Las demás películas conservan `"en catálogo"`. El tipo opcional `str | None` evita que el error anule toda la película. Las respuestas completas están en `evidencias/actividad_2/resultados.json`. La captura compara dos películas por título para mostrar claramente ambas respuestas, sin las filas duplicadas que ya existían en el catálogo.

## 5. Introspección

```graphql
query Introspeccion {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
  }
  pelicula: __type(name: "Pelicula") { fields { name } }
  suscripcion: __type(name: "Subscription") { fields { name } }
}
```

El resultado muestra Query, Mutation, Subscription, los campos `siglo` y `etiqueta`, y `peliculaAgregada`. La introspección consulta el esquema y no el catálogo MySQL.

## Verificación

```bash
python -m unittest discover -s tests -v
```

Las cinco pruebas usan SQLite temporal para aislarse de los datos personales: validación sin sesiones SQL, siglos y datos parciales, dos suscriptores/publicación posterior al commit/limpieza, commit fallido sin publicación, e introspección. Además, las capturas y los JSON se obtuvieron de GraphiQL contra MySQL, usando HTTP y WebSocket reales.

## Alcance

La cola de eventos vive en memoria: reiniciar el servidor desconecta a los suscriptores, sin borrar películas. Para varios procesos sería necesario un pub/sub compartido. La base mantiene únicamente `id`, `titulo`, `director`, `anio` y `disponible`.
