"""Servidor HTTP/WebSocket con errores de petición sin la clave data."""

from strawberry.asgi import GraphQL
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult
from starlette.requests import Request

from schema import schema


class CineclubGraphQL(GraphQL):
    async def process_result(
        self, request: Request, result: ExecutionResult
    ) -> GraphQLHTTPResponse:
        response = await super().process_result(request, result)
        # Los errores de análisis/validación no tienen ruta de ejecución.
        # Un fallo de resolver sí tiene path: debe conservar data, incluso null.
        if result.errors and result.data is None and all(
            error.path is None for error in result.errors
        ):
            response.pop("data", None)
        return response


app = CineclubGraphQL(schema)
