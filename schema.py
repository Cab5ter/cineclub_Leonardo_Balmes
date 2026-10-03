"""Esquema GraphQL del cineclub respaldado por MySQL."""

import strawberry

from database import Base, SessionLocal, engine
from models import PeliculaModel


@strawberry.type
class Director:
    nombre: str


@strawberry.type
class Pelicula:
    titulo: str
    director: Director
    anio: int
    disponible: bool


def fila_a_pelicula(fila: PeliculaModel) -> Pelicula:
    return Pelicula(
        titulo=fila.titulo,
        director=Director(nombre=fila.director),
        anio=fila.anio,
        disponible=fila.disponible,
    )


def preparar_datos() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(PeliculaModel).count() == 0:
            db.add_all(
                [
                    PeliculaModel(
                        titulo="Cinema Paradiso",
                        director="Giuseppe Tornatore",
                        anio=1988,
                        disponible=True,
                    ),
                    PeliculaModel(
                        titulo="Spirited Away",
                        director="Hayao Miyazaki",
                        anio=2001,
                        disponible=True,
                    ),
                    PeliculaModel(
                        titulo="The Godfather",
                        director="Francis Ford Coppola",
                        anio=1972,
                        disponible=False,
                    ),
                ]
            )
            db.commit()


preparar_datos()


@strawberry.type
class Query:
    @strawberry.field
    def peliculas(self) -> list[Pelicula]:
        with SessionLocal() as db:
            filas = db.query(PeliculaModel).order_by(PeliculaModel.id).all()
            return [fila_a_pelicula(fila) for fila in filas]

    @strawberry.field
    def pelicula(self, titulo: str) -> Pelicula | None:
        with SessionLocal() as db:
            fila = db.query(PeliculaModel).filter(PeliculaModel.titulo == titulo).first()
            return fila_a_pelicula(fila) if fila is not None else None

    @strawberry.field
    def peliculas_disponibles(self) -> list[Pelicula]:
        with SessionLocal() as db:
            filas = (
                db.query(PeliculaModel)
                .filter(PeliculaModel.disponible.is_(True))
                .order_by(PeliculaModel.id)
                .all()
            )
            return [fila_a_pelicula(fila) for fila in filas]


@strawberry.input
class AgregarPeliculaInput:
    titulo: str
    director: str
    anio: int
    disponible: bool


@strawberry.type
class Mutation:
    @strawberry.mutation
    def agregar_pelicula(self, pelicula: AgregarPeliculaInput) -> Pelicula:
        with SessionLocal() as db:
            fila = PeliculaModel(
                titulo=pelicula.titulo,
                director=pelicula.director,
                anio=pelicula.anio,
                disponible=pelicula.disponible,
            )
            db.add(fila)
            db.commit()
            db.refresh(fila)
            return fila_a_pelicula(fila)


schema = strawberry.Schema(query=Query, mutation=Mutation)
