"""Modelo de la tabla de películas."""

from sqlalchemy import Boolean, Column, Integer, String

from database import Base


class PeliculaModel(Base):
    __tablename__ = "peliculas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    director = Column(String(200), nullable=False)
    anio = Column(Integer, nullable=False)
    disponible = Column(Boolean, nullable=False)
