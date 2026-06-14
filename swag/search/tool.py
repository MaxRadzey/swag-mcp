from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from swag.app.gateway import SpecGateway
from swag.exceptions import SwagError
from swag.search.models import SearchQuery, SearchResponse


def register_search_spec_tool(mcp: FastMCP, spec_search: SpecGateway) -> None:
    @mcp.tool()
    def search_spec(
        service_id: str,
        query: str,
        method: str | None = None,
        path: str | None = None,
        path_prefix: str | None = None,
        tag: str | None = None,
        limit: int = 5,
    ) -> SearchResponse:
        """Search API operations in a selected service specification.

        Returns compact ranked hits (method, path, summary). Call get_operation
        on a chosen hit for its full contract.
        """
        search_query = SearchQuery(
            query=query,
            method=method,
            path=path,
            path_prefix=path_prefix,
            tag=tag,
            limit=limit,
        )
        try:
            return spec_search.search(service_id, search_query)
        except SwagError as exc:
            raise ToolError(str(exc)) from exc
