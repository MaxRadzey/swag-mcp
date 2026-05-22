SERVER_INSTRUCTIONS = """\
Swag is a corporate MCP server that exposes registered API documentation.

Workflow:
1. Call list_services first to see available services (id, name, description).
2. Pick the service id that best matches the user's task using name and description.
3. The list_services response does not include OpenAPI documents or spec URLs.

To fetch full OpenAPI for a chosen service, use get_service_spec(service_id) when that tool is available. \
It is not registered on this server yet — do not invent or call it until it appears in the tool list.
"""
