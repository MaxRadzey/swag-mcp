SERVER_INSTRUCTIONS = """\
Swag is a corporate MCP server that exposes registered API documentation.

Workflow:
1. Call list_services first to see available services (id, name, description).
2. Pick the service id that best matches the user's task using name and description.
3. Use search_spec(service_id, query, method, path, path_prefix, tag, limit) to find matching API operations.
4. Pass any clear intent from the user as search arguments: natural-language action/entity in query,
   HTTP method when explicit, and path/tag only when they are obvious.
5. Call get_operation(service_id, method, path) on the chosen hit to get its full contract:
   parameters, request body, and responses (local $ref schemas are resolved inline).
6. The list_services response does not include OpenAPI documents or spec URLs.

search_spec returns compact ranked operation hits (method, path, summary), not the full document.
Pick the best hit, then use get_operation to retrieve the details the user needs to build a request.
Use the result to answer the user or ask a clarifying question when results are ambiguous.
"""
