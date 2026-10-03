# Cineclub: GraphQL y MySQL

Proyecto de la Unidad II, Actividad 1. Strawberry expone la cartelera y SQLAlchemy guarda las películas en MySQL.

## Preparación

Requiere Python 3.10 o superior y un servidor MySQL activo. Crea una base vacía llamada `cineclub`:

```sql
CREATE DATABASE IF NOT EXISTS cineclub;
```

Desde esta carpeta:

```sh
python3 -m venv virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='mysql+pymysql://USUARIO:CONTRASENA@127.0.0.1:3306/cineclub'
strawberry dev schema
```

Sustituye `USUARIO` y `CONTRASENA` por tus credenciales y ajusta el host y el puerto. La conexión se configura mediante `DATABASE_URL`; las credenciales no se guardan en el código. En PowerShell usa `$env:DATABASE_URL = "mysql+pymysql://USUARIO:CONTRASENA@127.0.0.1:3306/cineclub"`. Abre `http://localhost:8000/graphql` para usar GraphiQL.

## Operaciones de comprobación

```graphql
{
  peliculas {
    titulo
    anio
    disponible
    director { nombre }
  }
}
```

```graphql
{
  pelicula(titulo: "The Godfather") { titulo director { nombre } }
  inexistente: pelicula(titulo: "Amelie") { titulo }
  peliculasDisponibles { titulo }
}
```

```graphql
mutation {
  agregarPelicula(pelicula: {
    titulo: "Amelie"
    director: "Jean-Pierre Jeunet"
    anio: 2001
    disponible: true
  }) {
    titulo
    anio
    director { nombre }
  }
}
```

Ejecuta la mutación una sola vez. Después repite la primera consulta, reinicia el servidor y vuelve a consultarla. Verifica las cuatro filas directamente en MySQL con:

```sql
SELECT titulo, director, anio, disponible FROM cineclub.peliculas;
```

Las capturas de la consulta en GraphiQL, de la consulta después del reinicio y de las filas devueltas por el cliente MySQL están en `evidencias/`. La salida de MySQL también está guardada como texto en esa carpeta.
