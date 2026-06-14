from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from swag.app.gateway import SpecGateway
from swag.exceptions import SwagError
from swag.operation.models import OperationDetail


def register_get_operation_tool(mcp: FastMCP, spec_search: SpecGateway) -> None:
    @mcp.tool()
    def get_operation(service_id: str, method: str, path: str) -> OperationDetail:
        """Get one operation's full contract: parameters, request body, and responses.

        Use after search_spec to fetch the details of a chosen method+path. Local
        $ref schemas are resolved inline so the result is self-contained.
        """
        try:
            return spec_search.get_operation(service_id, method, path)
        except SwagError as exc:
            raise ToolError(str(exc)) from exc
