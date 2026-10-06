"""Pruebas aisladas: SQLite temporal, sin tocar el catálogo MySQL del usuario."""
import asyncio
import os
import tempfile
import unittest
from unittest.mock import patch

_tmp = tempfile.TemporaryDirectory()
os.environ['DATABASE_URL'] = 'sqlite:///' + _tmp.name + '/pruebas.db'

import schema as modulo
from app import app


class Actividad2(unittest.IsolatedAsyncioTestCase):
    async def test_validacion_no_abre_base(self):
        for query in ('{ peliculas { isbn } }', '{ peliculas { director } }',
                      '{ peliculas { titulo { nombre } } }'):
            with patch.object(modulo, 'SessionLocal') as session:
                result = await modulo.schema.execute(query)
                session.assert_not_called()
            response = await app.process_result(None, result)
            self.assertIn('errors', response)
            self.assertNotIn('data', response)

    async def test_calculo_y_error_parcial(self):
        for year, century in ((1895, 19), (1900, 19), (1901, 20), (2000, 20), (2001, 21)):
            film = modulo.Pelicula(titulo='Prueba', director=modulo.Director(nombre='Prueba'),
                                   anio=year, disponible=True)
            self.assertEqual(film.siglo(), century)
        await modulo.schema.execute('''mutation { agregarPelicula(pelicula: {
          titulo: "Antigua de prueba", director: "Prueba", anio: 1895, disponible: true
        }) { titulo } }''')
        result = await modulo.schema.execute('''{ peliculas { titulo anio etiqueta } }''')
        self.assertTrue(result.errors)
        old = next(x for x in result.data['peliculas'] if x['titulo']=='Antigua de prueba')
        self.assertEqual(old, {'titulo':'Antigua de prueba', 'anio':1895, 'etiqueta':None})
        response = await app.process_result(None, result)
        self.assertIn('data', response)
        self.assertIn('errors', response)
        self.assertTrue(all(error.path for error in result.errors))

    async def test_suscriptores_commit_y_desconexion(self):
        streams = [await modulo.schema.subscribe('subscription { peliculaAgregada { titulo } }')
                   for _ in range(2)]
        tasks = [asyncio.create_task(anext(stream)) for stream in streams]
        await asyncio.sleep(0.05)
        self.assertEqual(len(modulo._suscriptores), 2)
        self.assertTrue(all(not task.done() for task in tasks))  # No reenvía historial.
        original = modulo.publicar_pelicula
        def comprobar_commit(film):
            with modulo.SessionLocal() as db:
                self.assertIsNotNone(db.query(modulo.PeliculaModel).filter_by(titulo=film.titulo).first())
            original(film)
        with patch.object(modulo, 'publicar_pelicula', side_effect=comprobar_commit):
            result = await modulo.schema.execute('''mutation { agregarPelicula(pelicula: {
              titulo: "Evento de prueba", director: "Prueba", anio: 2015, disponible: true
            }) { titulo } }''')
        self.assertFalse(result.errors)
        for task in tasks:
            event = await asyncio.wait_for(task, 1)
            self.assertEqual(event.data['peliculaAgregada']['titulo'], 'Evento de prueba')
        for stream in streams:
            await stream.aclose()
        self.assertEqual(len(modulo._suscriptores), 0)

    async def test_commit_fallido_no_publica(self):
        with patch.object(modulo, 'SessionLocal') as session, patch.object(modulo, 'publicar_pelicula') as publish:
            session.return_value.__enter__.return_value.commit.side_effect = RuntimeError('commit fallido')
            result = await modulo.schema.execute('''mutation { agregarPelicula(pelicula: {
              titulo: "No guardada", director: "Prueba", anio: 2015, disponible: true
            }) { titulo } }''')
            self.assertTrue(result.errors)
            publish.assert_not_called()
        response = await app.process_result(None, result)
        self.assertIn('data', response)  # Fallo de ejecución en un campo obligatorio.
        self.assertIsNone(response['data'])

    async def test_introspeccion(self):
        result = await modulo.schema.execute('''{
          __schema { queryType { name } mutationType { name } subscriptionType { name } }
          __type(name: "Subscription") { fields { name } }
        }''')
        self.assertFalse(result.errors)
        self.assertEqual(result.data['__schema']['subscriptionType']['name'], 'Subscription')
        self.assertEqual(result.data['__type']['fields'], [{'name': 'peliculaAgregada'}])


if __name__ == '__main__':
    unittest.main()
